from __future__ import annotations

import re
import logging
import threading
import zipfile
from io import BytesIO
import json
import mimetypes
from http import HTTPStatus
from pathlib import Path
from xml.etree import ElementTree

from flask import Blueprint, Response, current_app, jsonify, request, send_file, stream_with_context

from .services.llm_client import LLMError
from .services.requirement_collector import RequirementCollectorService
from .services.asr_client import ASRError

api = Blueprint("api", __name__, url_prefix="/api")
logger = logging.getLogger(__name__)
_structured_requirement_refresh_lock = threading.Lock()
_structured_requirement_refresh_jobs: set[tuple[str, str]] = set()
MAX_ATTACHMENT_BYTES = 8 * 1024 * 1024
MAX_EXTRACTED_ATTACHMENT_CHARS = 12000
MAX_MULTIMODAL_INLINE_BYTES = 7 * 1024 * 1024
MAX_MULTIMODAL_PARTS = 8
DOCX_MIME_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
SUPPORTED_ATTACHMENT_EXTENSIONS = {
    ".pptx",
    ".docx",
    ".xlsx",
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".gif",
    ".txt",
    ".md",
    ".csv",
    ".json",
    ".log",
}


def _send_generated_document_file(
    service: RequirementCollectorService,
    result: tuple[Path, str],
):
    file_path, download_name = result
    download_format = request.args.get("format", "").strip().lower()
    if download_format in {"docx", "word", "docs"}:
        docx_buffer, docx_name = service.build_docx_download(file_path, download_name)
        return send_file(
            docx_buffer,
            mimetype=DOCX_MIME_TYPE,
            as_attachment=True,
            download_name=docx_name,
            max_age=0,
        )

    return send_file(
        file_path,
        mimetype="text/markdown; charset=utf-8",
        as_attachment=True,
        download_name=download_name,
        max_age=0,
    )
MULTIMODAL_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def _get_service() -> RequirementCollectorService:
    service = current_app.extensions.get("requirement_collector")
    if service is None:
        raise RuntimeError("Requirement collector service not initialized.")
    return service


def _get_asr_client():
    """获取ASR客户端"""
    asr_client = current_app.extensions.get("asr_client")
    if asr_client is None:
        raise RuntimeError("ASR client not initialized.")
    return asr_client


def _is_truthy_request_arg(name: str) -> bool:
    return str(request.args.get(name, "")).strip().lower() in {"1", "true", "yes", "on"}


def _start_structured_requirement_refresh(
    service: RequirementCollectorService,
    session_id: str,
    language: str,
) -> None:
    job_key = (session_id, language.strip().lower() or "zh")
    with _structured_requirement_refresh_lock:
        if job_key in _structured_requirement_refresh_jobs:
            return
        _structured_requirement_refresh_jobs.add(job_key)

    def refresh() -> None:
        try:
            service.build_structured_requirement_model(session_id, language, force_refresh=True)
        except Exception:
            logger.exception("Background structured requirement refresh failed for session %s", session_id)
        finally:
            with _structured_requirement_refresh_lock:
                _structured_requirement_refresh_jobs.discard(job_key)

    threading.Thread(
        target=refresh,
        name=f"structured-requirement-refresh-{session_id[:8]}",
        daemon=True,
    ).start()


def _request_language(default: str = "zh") -> str:
    payload = request.get_json(silent=True) or {}
    language = str(payload.get("language", request.args.get("language", default))).strip().lower()
    return language or default


def _truncate_attachment_text(text: str) -> tuple[str, bool]:
    normalized = re.sub(r"\n{3,}", "\n\n", text).strip()
    if len(normalized) <= MAX_EXTRACTED_ATTACHMENT_CHARS:
        return normalized, False
    return normalized[:MAX_EXTRACTED_ATTACHMENT_CHARS].rstrip(), True


def _xml_text(xml_bytes: bytes) -> str:
    try:
        root = ElementTree.fromstring(xml_bytes)
    except ElementTree.ParseError:
        return ""
    chunks = []
    for item in root.iter():
        if item.text and item.text.strip():
            chunks.append(item.text.strip())
    return "\n".join(chunks)


def _zip_member_sort_key(name: str) -> tuple[str, int, str]:
    match = re.search(r"(\d+)(?=\.xml$)", name)
    return (str(Path(name).parent), int(match.group(1)) if match else 0, name)


def _extract_zip_xml_text(file_bytes: bytes, prefixes: tuple[str, ...]) -> str:
    chunks = []
    with zipfile.ZipFile(BytesIO(file_bytes)) as archive:
        member_names = sorted(
            (
                name
                for name in archive.namelist()
                if name.endswith(".xml") and any(name.startswith(prefix) for prefix in prefixes)
            ),
            key=_zip_member_sort_key,
        )
        for name in member_names:
            text = _xml_text(archive.read(name))
            if text:
                chunks.append(text)
    return "\n\n".join(chunks)


def _guess_mime_type(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix == ".pptx":
        return "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    if suffix == ".docx":
        return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    if suffix == ".xlsx":
        return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    if suffix == ".pdf":
        return "application/pdf"
    return mimetypes.guess_type(filename)[0] or "application/octet-stream"


def _extract_pptx_inline_media(file_bytes: bytes) -> list[dict[str, object]]:
    media_parts: list[dict[str, object]] = []
    with zipfile.ZipFile(BytesIO(file_bytes)) as archive:
        media_names = sorted(
            (
                name
                for name in archive.namelist()
                if name.startswith("ppt/media/")
                and Path(name).suffix.lower() in MULTIMODAL_IMAGE_EXTENSIONS
            ),
            key=_zip_member_sort_key,
        )
        for name in media_names:
            data = archive.read(name)
            if not data or len(data) > MAX_MULTIMODAL_INLINE_BYTES:
                continue
            media_parts.append(
                {
                    "filename": Path(name).name,
                    "mime_type": _guess_mime_type(name),
                    "data": data,
                }
            )
            if len(media_parts) >= MAX_MULTIMODAL_PARTS:
                break
    return media_parts


def _attachment_inline_data(filename: str, file_bytes: bytes) -> list[dict[str, object]]:
    suffix = Path(filename).suffix.lower()
    if suffix in MULTIMODAL_IMAGE_EXTENSIONS or suffix == ".pdf":
        if len(file_bytes) <= MAX_MULTIMODAL_INLINE_BYTES:
            return [
                {
                    "filename": filename,
                    "mime_type": _guess_mime_type(filename),
                    "data": file_bytes,
                }
            ]
        return []
    if suffix == ".pptx":
        return _extract_pptx_inline_media(file_bytes)
    return []


def _attachment_analysis_prompt(
    filename: str,
    extracted_text: str,
    inline_data: list[dict[str, object]],
    language: str = "zh",
    visual_unavailable_note: str = "",
) -> str:
    media_names = [str(item.get("filename", "")) for item in inline_data if item.get("filename")]
    media_note = "\n".join(f"- {name}" for name in media_names) or "- None"
    output_language = {
        "zh": "Chinese",
        "de": "German",
        "ms": "Bahasa Melayu",
        "en": "English",
    }.get(language, "Chinese")
    unavailable_section = (
        f"\nVisual analysis fallback note: {visual_unavailable_note}\n"
        if visual_unavailable_note
        else ""
    )
    return (
        "You are an expert AI product manager helping users turn business attachments into software requirements.\n"
        "Analyze the attachment content and any images/charts provided. Focus on PRD completion gaps and what a PM should ask next.\n\n"
        f"File name: {filename}\n"
        f"Visual parts provided to the model:\n{media_note}\n\n"
        f"{unavailable_section}"
        "Extracted text and chart XML text, if any:\n"
        f"{extracted_text or '(No readable text extracted.)'}\n\n"
        f"Return a concise {output_language} summary with these sections:\n"
        "1. Already clear facts for the PRD\n"
        "2. Inferred but pending-confirmation assumptions\n"
        "3. Missing or conflicting PRD gaps\n"
        "4. The single most important next AI PM question\n"
        "Do not invent exact numbers or internal system names if they are not visible."
    )


def extract_attachment_text(filename: str, file_bytes: bytes) -> dict[str, object]:
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_ATTACHMENT_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_ATTACHMENT_EXTENSIONS))
        raise ValueError(f"Unsupported file type. Supported: {supported}")
    if len(file_bytes) > MAX_ATTACHMENT_BYTES:
        raise ValueError("Attachment is too large. Please keep it under 8 MB.")

    if suffix in {".txt", ".md", ".csv", ".json", ".log"}:
        raw_text = file_bytes.decode("utf-8", errors="replace")
        kind = "text"
    elif suffix == ".pptx":
        raw_text = _extract_zip_xml_text(file_bytes, ("ppt/slides/", "ppt/notesSlides/", "ppt/charts/"))
        kind = "presentation"
    elif suffix == ".pdf":
        raw_text = ""
        kind = "pdf"
    elif suffix in MULTIMODAL_IMAGE_EXTENSIONS:
        raw_text = ""
        kind = "image"
    elif suffix == ".docx":
        raw_text = _extract_zip_xml_text(file_bytes, ("word/document.xml", "word/header", "word/footer"))
        kind = "document"
    else:
        raw_text = _extract_zip_xml_text(file_bytes, ("xl/sharedStrings.xml", "xl/worksheets/"))
        kind = "spreadsheet"

    text, truncated = _truncate_attachment_text(raw_text)
    if not text and kind not in {"pdf", "image", "presentation"}:
        raise ValueError("No readable text was found in this attachment.")
    return {
        "filename": filename,
        "size": len(file_bytes),
        "kind": kind,
        "text": text,
        "truncated": truncated,
    }


def _attachment_visual_fallback_text(filename: str, language: str, reason: str) -> str:
    if language == "zh":
        return (
            f"附件 {filename} 包含图片、PDF 或图表内容，但当前模型未能完成视觉分析。"
            "我会先基于可抽取文字继续梳理；图片里的字段、数值、流程或图表含义需要你下一步确认。"
            f"\n\n降级原因：{reason}"
        )
    if language == "de":
        return (
            f"Der Anhang {filename} enthaelt Bilder, PDF- oder Chart-Inhalte, aber das aktuelle Modell konnte sie nicht visuell analysieren. "
            "Ich nutze zuerst den extrahierbaren Text; Felder, Zahlen, Prozesse oder Chart-Bedeutungen aus Bildern muessen bestaetigt werden."
            f"\n\nFallback-Grund: {reason}"
        )
    if language == "ms":
        return (
            f"Lampiran {filename} mengandungi imej, PDF atau carta, tetapi model semasa tidak dapat menganalisis visual tersebut. "
            "Saya akan gunakan teks yang boleh diekstrak dahulu; field, nombor, proses atau maksud carta dalam imej perlu disahkan."
            f"\n\nSebab fallback: {reason}"
        )
    return (
        f"The attachment {filename} contains image, PDF, or chart content, but the current model could not analyze the visual parts. "
        "I will continue from extracted text first; fields, numbers, process steps, or chart meaning in images need user confirmation."
        f"\n\nFallback reason: {reason}"
    )


def _attachment_text_with_visual_note(
    filename: str,
    extraction: dict[str, object],
    language: str,
    reason: str,
) -> str:
    fallback_text = _attachment_visual_fallback_text(filename, language, reason)
    extracted_text = str(extraction.get("text", "")).strip()
    if not extracted_text:
        return fallback_text
    if language == "zh":
        return f"{fallback_text}\n\n已保留可抽取文字：\n{extracted_text}"
    if language == "de":
        return f"{fallback_text}\n\nExtrahierbarer Text wurde beibehalten:\n{extracted_text}"
    if language == "ms":
        return f"{fallback_text}\n\nTeks yang boleh diekstrak dikekalkan:\n{extracted_text}"
    return f"{fallback_text}\n\nExtracted text preserved:\n{extracted_text}"


def _analyze_attachment_text_only(
    filename: str,
    extraction: dict[str, object],
    language: str,
    visual_unavailable_note: str = "",
) -> str:
    extracted_text = str(extraction.get("text", "")).strip()
    if not extracted_text:
        return _attachment_visual_fallback_text(filename, language, visual_unavailable_note or "No readable text was extracted.")

    service = _get_service()
    prompt = _attachment_analysis_prompt(
        filename,
        extracted_text,
        [],
        language=language,
        visual_unavailable_note=visual_unavailable_note,
    )
    return service.llm_client.chat([{"role": "user", "content": prompt}], temperature=0.2)


def analyze_attachment_with_model(filename: str, file_bytes: bytes, language: str = "zh") -> dict[str, object]:
    extraction = extract_attachment_text(filename, file_bytes)
    inline_data = _attachment_inline_data(filename, file_bytes)
    normalized_language = language if language in {"en", "de", "zh", "ms"} else "zh"
    if not inline_data:
        try:
            extraction["text"] = _analyze_attachment_text_only(filename, extraction, normalized_language)
            extraction["analysis_note"] = "Analyzed from extracted text only."
        except LLMError as exc:
            extraction["analysis_note"] = f"Text-only attachment analysis unavailable: {exc}"
        extraction["visual_count"] = 0
        extraction["multimodal"] = False
        return extraction

    service = _get_service()
    extraction["visual_count"] = len(inline_data)
    prompt = _attachment_analysis_prompt(
        filename,
        str(extraction.get("text", "")),
        inline_data,
        language=normalized_language,
    )
    try:
        analysis = service.llm_client.chat_multimodal(prompt, inline_data, temperature=0.2)
        extraction["text"] = analysis
        extraction["multimodal"] = True
    except LLMError as exc:
        fallback_note = str(exc)
        try:
            extraction["text"] = _analyze_attachment_text_only(
                filename,
                extraction,
                normalized_language,
                visual_unavailable_note=fallback_note,
            )
        except LLMError:
            extraction["text"] = _attachment_text_with_visual_note(filename, extraction, normalized_language, fallback_note)
        extraction["analysis_note"] = f"Visual analysis fell back to text-only mode: {fallback_note}"
        extraction["multimodal"] = False
    return extraction


def _structured_requirement_response(
    session_id: str,
    structured_requirement_model: dict[str, object],
    sync_status: str = "ready",
    conversation_chain_state: dict[str, object] | None = None,
    pm_methodology_state: dict[str, object] | None = None,
    ic_substrate_evidence_state: dict[str, object] | None = None,
):
    response = {
        "session_id": session_id,
        "summary": structured_requirement_model,
        "structured_requirement_model": structured_requirement_model,
        "structured_requirement_sync_status": sync_status,
    }
    if conversation_chain_state is not None:
        response["conversation_chain_state"] = conversation_chain_state
    if pm_methodology_state is not None:
        response["pm_methodology_state"] = pm_methodology_state
    if ic_substrate_evidence_state is not None:
        response["ic_substrate_evidence_state"] = ic_substrate_evidence_state
    return response


@api.post("/sessions")
def create_session():
    service = _get_service()
    payload = request.get_json(silent=True) or {}
    template_id = str(payload.get("template_id", "")).strip() or None
    template_start_mode = str(payload.get("template_start_mode", "guided")).strip().lower()
    starter_department = str(payload.get("starter_department", "")).strip()
    start_function = str(payload.get("start_function", "from_scratch")).strip().lower()
    language = _request_language()
    try:
        session = service.create_session(
            template_id=template_id,
            language=language,
            template_start_mode=template_start_mode,
            starter_department=starter_department,
            start_function=start_function,
        )
    except KeyError:
        return jsonify({"error": "Business template not found."}), HTTPStatus.NOT_FOUND
    except ValueError as exc:
        return jsonify({"error": str(exc)}), HTTPStatus.BAD_REQUEST
    structured_requirement_snapshot = service.get_structured_requirement_snapshot(session.id, language)
    return (
        jsonify(
            {
                "session_id": session.id,
                "title": session.title,
                "prompt_template": session.prompt_template,
                "applied_template_id": session.applied_template_id,
                "applied_template_name": session.applied_template_name,
                "start_function": session.start_function,
                "created_at": session.created_at,
                "updated_at": session.updated_at,
                "messages": session.messages,
                "summary": structured_requirement_snapshot["structured_requirement_model"],
                "structured_requirement_model": structured_requirement_snapshot["structured_requirement_model"],
                "structured_requirement_sync_status": structured_requirement_snapshot["structured_requirement_sync_status"],
                "conversation_chain_state": structured_requirement_snapshot["conversation_chain_state"],
                "pm_methodology_state": structured_requirement_snapshot["pm_methodology_state"],
                "ic_substrate_evidence_state": structured_requirement_snapshot["ic_substrate_evidence_state"],
            }
        ),
        HTTPStatus.CREATED,
    )


@api.get("/sessions")
def list_sessions():
    service = _get_service()
    return jsonify({"sessions": service.list_sessions()})


@api.get("/templates")
def list_templates():
    service = _get_service()
    return jsonify({"templates": service.list_business_templates()})


@api.get("/templates/<template_id>")
def get_template(template_id: str):
    service = _get_service()
    template = service.get_business_template(template_id)
    if template is None:
        return jsonify({"error": "Business template not found."}), HTTPStatus.NOT_FOUND
    return jsonify(template)


@api.post("/attachments/extract")
def extract_attachment():
    file = request.files.get("file")
    if file is None or not file.filename:
        return jsonify({"error": "Field `file` is required."}), HTTPStatus.BAD_REQUEST

    file_bytes = file.read()
    try:
        result = extract_attachment_text(file.filename, file_bytes)
    except (ValueError, zipfile.BadZipFile) as exc:
        return jsonify({"error": str(exc)}), HTTPStatus.BAD_REQUEST
    return jsonify(result)


@api.post("/attachments/analyze")
def analyze_attachment():
    file = request.files.get("file")
    if file is None or not file.filename:
        return jsonify({"error": "Field `file` is required."}), HTTPStatus.BAD_REQUEST

    file_bytes = file.read()
    language = str(request.form.get("language", request.args.get("language", "zh"))).strip().lower()
    try:
        result = analyze_attachment_with_model(file.filename, file_bytes, language)
    except (ValueError, zipfile.BadZipFile) as exc:
        return jsonify({"error": str(exc)}), HTTPStatus.BAD_REQUEST
    return jsonify(result)


@api.get("/sessions/<session_id>")
def get_session(session_id: str):
    service = _get_service()
    session = service.get_session(session_id)
    if session is None:
        return jsonify({"error": "Session not found."}), HTTPStatus.NOT_FOUND
    structured_requirement_snapshot = service.get_structured_requirement_snapshot(
        session_id,
        _request_language(),
    )

    return jsonify(
        {
            "session_id": session.id,
            "title": session.title,
            "prompt_template": session.prompt_template,
            "applied_template_id": session.applied_template_id,
            "applied_template_name": session.applied_template_name,
            "start_function": session.start_function,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "messages": session.messages,
            "summary": structured_requirement_snapshot["structured_requirement_model"],
            "structured_requirement_model": structured_requirement_snapshot["structured_requirement_model"],
            "structured_requirement_sync_status": structured_requirement_snapshot["structured_requirement_sync_status"],
            "conversation_chain_state": structured_requirement_snapshot["conversation_chain_state"],
            "pm_methodology_state": structured_requirement_snapshot["pm_methodology_state"],
            "ic_substrate_evidence_state": structured_requirement_snapshot["ic_substrate_evidence_state"],
        }
    )


@api.delete("/sessions/<session_id>")
def delete_session(session_id: str):
    service = _get_service()
    deleted = service.delete_session(session_id)
    if not deleted:
        return jsonify({"error": "Session not found."}), HTTPStatus.NOT_FOUND
    return ("", HTTPStatus.NO_CONTENT)


@api.post("/sessions/<session_id>/prompt-template")
def update_session_prompt_template(session_id: str):
    payload = request.get_json(silent=True) or {}
    prompt_template = str(payload.get("prompt_template", "")).strip()
    if not prompt_template:
        return jsonify({"error": "Field `prompt_template` is required."}), HTTPStatus.BAD_REQUEST

    service = _get_service()
    try:
        session = service.update_session_prompt_template(session_id, prompt_template)
    except KeyError:
        return jsonify({"error": "Session not found."}), HTTPStatus.NOT_FOUND
    except ValueError as exc:
        return jsonify({"error": str(exc)}), HTTPStatus.CONFLICT

    return jsonify(
        {
            "session_id": session.id,
            "title": session.title,
            "prompt_template": session.prompt_template,
            "applied_template_id": session.applied_template_id,
            "applied_template_name": session.applied_template_name,
            "start_function": session.start_function,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "messages": session.messages,
        }
    )


@api.post("/sessions/<session_id>/messages")
def send_message(session_id: str):
    payload = request.get_json(silent=True) or {}
    user_message = str(payload.get("message", "")).strip()
    display_message = str(payload.get("display_message", "")).strip()
    language = str(payload.get("language", "zh")).strip()
    if not user_message:
        return jsonify({"error": "Field `message` is required."}), HTTPStatus.BAD_REQUEST

    service = _get_service()
    try:
        result = service.send_user_message(session_id, user_message, language, display_message)
    except KeyError:
        return jsonify({"error": "Session not found."}), HTTPStatus.NOT_FOUND
    except LLMError as exc:
        return jsonify({"error": str(exc)}), HTTPStatus.BAD_GATEWAY

    return jsonify(result)


@api.post("/sessions/<session_id>/messages/stream")
def stream_message(session_id: str):
    payload = request.get_json(silent=True) or {}
    user_message = str(payload.get("message", "")).strip()
    display_message = str(payload.get("display_message", "")).strip()
    language = str(payload.get("language", "zh")).strip()
    if not user_message:
        return jsonify({"error": "Field `message` is required."}), HTTPStatus.BAD_REQUEST

    service = _get_service()

    def event_stream():
        try:
            for item in service.stream_user_message(session_id, user_message, language, display_message):
                event_name = item.get("event", "message")
                data = json.dumps(item, ensure_ascii=False)
                yield f"event: {event_name}\n"
                yield f"data: {data}\n\n"
        except KeyError:
            data = json.dumps({"event": "error", "error": "Session not found."}, ensure_ascii=False)
            yield "event: error\n"
            yield f"data: {data}\n\n"
        except LLMError as exc:
            data = json.dumps({"event": "error", "error": str(exc)}, ensure_ascii=False)
            yield "event: error\n"
            yield f"data: {data}\n\n"
        except Exception as exc:  # Defensive fallback for streaming parsing issues.
            data = json.dumps({"event": "error", "error": str(exc)}, ensure_ascii=False)
            yield "event: error\n"
            yield f"data: {data}\n\n"

    return Response(
        stream_with_context(event_stream()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@api.get("/sessions/<session_id>/summary")
def get_summary(session_id: str):
    language = _request_language()
    service = _get_service()
    try:
        structured_requirement_model = service.build_structured_requirement_model(session_id, language)
        session = service.get_session(session_id)
        if session is None:
            raise KeyError("Session not found.")
        conversation_chain_state = service.build_conversation_chain_state(
            session,
            structured_requirement_model,
            language,
        )
        pm_methodology_state = service.build_pm_methodology_state(
            structured_requirement_model,
            language,
        )
        ic_substrate_evidence_state = service.build_ic_substrate_evidence_state(
            session,
            structured_requirement_model,
            language,
        )
    except KeyError:
        return jsonify({"error": "Session not found."}), HTTPStatus.NOT_FOUND
    except LLMError as exc:
        return jsonify({"error": str(exc)}), HTTPStatus.BAD_GATEWAY
    return jsonify(
        _structured_requirement_response(
            session_id,
            structured_requirement_model,
            "ready",
            conversation_chain_state,
            pm_methodology_state,
            ic_substrate_evidence_state,
        )
    )


@api.get("/sessions/<session_id>/structured-requirement")
def get_structured_requirement(session_id: str):
    language = _request_language()
    background = _is_truthy_request_arg("background")
    service = _get_service()
    try:
        if background:
            snapshot = service.get_structured_requirement_snapshot(session_id, language)
            if snapshot["structured_requirement_sync_status"] in {"missing", "stale"}:
                _start_structured_requirement_refresh(service, session_id, language)
            return jsonify(
                _structured_requirement_response(
                    session_id,
                    snapshot["structured_requirement_model"],
                    snapshot["structured_requirement_sync_status"],
                    snapshot["conversation_chain_state"],
                    snapshot["pm_methodology_state"],
                    snapshot["ic_substrate_evidence_state"],
                )
            )

        structured_requirement_model = service.build_structured_requirement_model(session_id, language)
        session = service.get_session(session_id)
        if session is None:
            raise KeyError("Session not found.")
        conversation_chain_state = service.build_conversation_chain_state(
            session,
            structured_requirement_model,
            language,
        )
        pm_methodology_state = service.build_pm_methodology_state(
            structured_requirement_model,
            language,
        )
        ic_substrate_evidence_state = service.build_ic_substrate_evidence_state(
            session,
            structured_requirement_model,
            language,
        )
    except KeyError:
        return jsonify({"error": "Session not found."}), HTTPStatus.NOT_FOUND
    except LLMError as exc:
        return jsonify({"error": str(exc)}), HTTPStatus.BAD_GATEWAY
    return jsonify(
        _structured_requirement_response(
            session_id,
            structured_requirement_model,
            "ready",
            conversation_chain_state,
            pm_methodology_state,
            ic_substrate_evidence_state,
        )
    )


@api.get("/sessions/<session_id>/design-doc")
def get_design_doc(session_id: str):
    language = _request_language()
    service = _get_service()
    try:
        result = service.build_system_design_document(session_id, language, save_history=False)
    except KeyError:
        return jsonify({"error": "Session not found."}), HTTPStatus.NOT_FOUND
    except LLMError as exc:
        return jsonify({"error": str(exc)}), HTTPStatus.BAD_GATEWAY
    return jsonify(result)


@api.get("/sessions/<session_id>/prd-doc")
def get_prd_doc(session_id: str):
    language = _request_language()
    service = _get_service()
    try:
        result = service.build_prd_document(session_id, language, save_history=False)
    except KeyError:
        return jsonify({"error": "Session not found."}), HTTPStatus.NOT_FOUND
    except LLMError as exc:
        return jsonify({"error": str(exc)}), HTTPStatus.BAD_GATEWAY
    return jsonify(result)


@api.post("/sessions/<session_id>/prd-doc")
def post_prd_doc(session_id: str):
    language = _request_language()
    service = _get_service()
    try:
        result = service.build_prd_document(session_id, language, save_history=True)
    except KeyError:
        return jsonify({"error": "Session not found."}), HTTPStatus.NOT_FOUND
    except LLMError as exc:
        return jsonify({"error": str(exc)}), HTTPStatus.BAD_GATEWAY
    return jsonify(result)


@api.post("/sessions/<session_id>/prd-doc/stream")
def stream_prd_doc(session_id: str):
    language = _request_language()
    service = _get_service()

    def event_stream():
        try:
            for item in service.stream_prd_document(session_id, language, save_history=True):
                event_name = item.get("event", "message")
                data = json.dumps(item, ensure_ascii=False)
                yield f"event: {event_name}\n"
                yield f"data: {data}\n\n"
        except KeyError:
            data = json.dumps({"event": "error", "error": "Session not found."}, ensure_ascii=False)
            yield "event: error\n"
            yield f"data: {data}\n\n"
        except LLMError as exc:
            data = json.dumps({"event": "error", "error": str(exc)}, ensure_ascii=False)
            yield "event: error\n"
            yield f"data: {data}\n\n"
        except Exception as exc:
            data = json.dumps({"event": "error", "error": str(exc)}, ensure_ascii=False)
            yield "event: error\n"
            yield f"data: {data}\n\n"

    return Response(
        stream_with_context(event_stream()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@api.post("/sessions/<session_id>/design-doc")
def post_design_doc(session_id: str):
    language = _request_language()
    service = _get_service()
    try:
        result = service.build_system_design_document(session_id, language, save_history=True)
    except KeyError:
        return jsonify({"error": "Session not found."}), HTTPStatus.NOT_FOUND
    except LLMError as exc:
        return jsonify({"error": str(exc)}), HTTPStatus.BAD_GATEWAY
    return jsonify(result)


@api.post("/sessions/<session_id>/design-doc/stream")
def stream_design_doc(session_id: str):
    language = _request_language()
    service = _get_service()

    def event_stream():
        try:
            for item in service.stream_system_design_document(session_id, language, save_history=True):
                event_name = item.get("event", "message")
                data = json.dumps(item, ensure_ascii=False)
                yield f"event: {event_name}\n"
                yield f"data: {data}\n\n"
        except KeyError:
            data = json.dumps({"event": "error", "error": "Session not found."}, ensure_ascii=False)
            yield "event: error\n"
            yield f"data: {data}\n\n"
        except LLMError as exc:
            data = json.dumps({"event": "error", "error": str(exc)}, ensure_ascii=False)
            yield "event: error\n"
            yield f"data: {data}\n\n"
        except Exception as exc:
            data = json.dumps({"event": "error", "error": str(exc)}, ensure_ascii=False)
            yield "event: error\n"
            yield f"data: {data}\n\n"

    return Response(
        stream_with_context(event_stream()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@api.get("/sessions/<session_id>/design-doc/download")
def download_design_doc(session_id: str):
    service = _get_service()
    try:
        result = service.get_saved_design_document(session_id)
    except KeyError:
        return jsonify({"error": "Session not found."}), HTTPStatus.NOT_FOUND

    if result is None:
        return jsonify({"error": "Design document not found. Generate it first."}), HTTPStatus.NOT_FOUND

    return _send_generated_document_file(service, result)


@api.get("/sessions/<session_id>/messages/<int:message_id>/download")
def download_session_message_document(session_id: str, message_id: int):
    service = _get_service()
    try:
        result = service.get_saved_message_document(session_id, message_id)
    except KeyError:
        return jsonify({"error": "Session not found."}), HTTPStatus.NOT_FOUND

    if result is None:
        return jsonify({"error": "Document not found for this history item."}), HTTPStatus.NOT_FOUND

    return _send_generated_document_file(service, result)


@api.get("/sessions/<session_id>/prd-doc/download")
def download_prd_doc(session_id: str):
    service = _get_service()
    try:
        result = service.get_saved_prd_document(session_id)
    except KeyError:
        return jsonify({"error": "Session not found."}), HTTPStatus.NOT_FOUND

    if result is None:
        return jsonify({"error": "PRD document not found. Generate it first."}), HTTPStatus.NOT_FOUND

    return _send_generated_document_file(service, result)


@api.get("/sessions/<session_id>/implementation-context")
def get_implementation_context(session_id: str):
    language = _request_language()
    service = _get_service()
    try:
        result = service.build_implementation_context(session_id, language)
    except KeyError:
        return jsonify({"error": "Session not found."}), HTTPStatus.NOT_FOUND

    if not result.get("documents_ready"):
        missing_documents = result.get("missing_documents", [])
        missing_summary = ", ".join(str(item) for item in missing_documents) or "prd, design"
        return (
            jsonify(
                {
                    "error": f"Required generated documents are missing: {missing_summary}.",
                    **result,
                }
            ),
            HTTPStatus.NOT_FOUND,
        )

    return jsonify(result)


@api.post("/sessions/<session_id>/coding-handoff")
def create_coding_handoff(session_id: str):
    language = _request_language()
    service = _get_service()
    try:
        result = service.create_coding_handoff(session_id, language)
    except KeyError:
        return jsonify({"error": "Session not found."}), HTTPStatus.NOT_FOUND

    if not result.get("payload", {}).get("documents_ready", result.get("documents_ready", False)):
        payload = result.get("payload") if isinstance(result.get("payload"), dict) else result
        missing_documents = payload.get("missing_documents", []) if isinstance(payload, dict) else []
        missing_summary = ", ".join(str(item) for item in missing_documents) or "prd, design"
        return (
            jsonify(
                {
                    "error": f"Required generated documents are missing: {missing_summary}.",
                    **payload,
                }
            ),
            HTTPStatus.NOT_FOUND,
        )

    payload = result.get("payload") if isinstance(result.get("payload"), dict) else result
    if not payload.get("handoff_ready", True):
        methodology_gaps = payload.get("methodology_gaps", [])
        gap_summary = ", ".join(str(item) for item in methodology_gaps) or "PM methodology gaps"
        return (
            jsonify(
                {
                    "error": f"PM Methodology is not ready for Go Coding handoff: {gap_summary}.",
                    **payload,
                }
            ),
            HTTPStatus.CONFLICT,
        )

    open_url = request.args.get("open_url", "").strip()
    response_payload = {
        "handoff_token": result["handoff_token"],
        "expires_at": result["expires_at"],
        "documents_ready": payload.get("documents_ready", True),
        "handoff_ready": payload.get("handoff_ready", True),
        "methodology_ready": payload.get("methodology_ready", True),
        "implementation_prompt": payload.get("implementation_prompt", ""),
        "documents": payload.get("documents", []),
        "ic_substrate_evidence": payload.get("ic_substrate_evidence", {}),
    }
    if open_url:
        response_payload["open_url"] = open_url
    return jsonify(response_payload), HTTPStatus.CREATED


@api.get("/coding-handoffs/<token>")
def resolve_coding_handoff(token: str):
    service = _get_service()
    result = service.resolve_coding_handoff(token)
    if result is None:
        return jsonify({"error": "Coding handoff not found or expired."}), HTTPStatus.NOT_FOUND
    return jsonify(result)


@api.post("/asr/recognize")
def recognize_speech():
    """识别语音并返回文本"""
    if "audio" not in request.files:
        return jsonify({"error": "Field `audio` is required."}), HTTPStatus.BAD_REQUEST
    
    audio_file = request.files["audio"]
    audio_data = audio_file.read()
    
    # 保存录音文件
    import os
    import uuid
    from datetime import datetime
    
    # 创建录音保存目录
    recordings_dir = os.path.join(os.path.dirname(__file__), "..", "recordings")
    if not os.path.exists(recordings_dir):
        os.makedirs(recordings_dir)
    
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"recording_{timestamp}_{str(uuid.uuid4())[:8]}.wav"
    filepath = os.path.join(recordings_dir, filename)
    
    # 保存录音
    with open(filepath, "wb") as f:
        f.write(audio_data)
    
    asr_client = _get_asr_client()
    try:
        result = asr_client.recognize(audio_data)
    except ASRError as exc:
        return jsonify({"error": str(exc)}), HTTPStatus.BAD_GATEWAY
    except Exception as exc:
        return jsonify({"error": str(exc)}), HTTPStatus.INTERNAL_SERVER_ERROR
    
    return jsonify({"text": result, "recording_file": filename})
