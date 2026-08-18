from __future__ import annotations

import base64
from dataclasses import dataclass
import json
import logging
from pathlib import Path
import time
from typing import Any, Iterator

import requests


class LLMError(RuntimeError):
    """Raised when LLM request fails."""


@dataclass(frozen=True)
class LLMConfig:
    provider: str = "openai_compatible"
    base_url: str = ""
    api_key: str = ""
    model: str = ""
    timeout_seconds: int = 500
    proxy_url: str = ""
    max_retries: int = 2
    debug_stream: bool = False
    google_project_id: str = ""
    google_location: str = "global"
    google_credentials_path: str = ""

    def validate_for_startup(self) -> None:
        provider = (self.provider or "").strip().lower()
        if not self.model:
            raise LLMError("LLM_MODEL is required.")
        if provider == "openai_compatible":
            missing = []
            if not self.base_url:
                missing.append("LLM_BASE_URL")
            if not self.api_key:
                missing.append("LLM_API_KEY")
            if missing:
                raise LLMError(
                    f"openai_compatible provider requires: {', '.join(missing)}."
                )
        elif provider == "vertex_gemini":
            if not self.google_project_id:
                raise LLMError("vertex_gemini provider requires LLM_GCP_PROJECT_ID.")
            credentials_path = self.google_credentials_path
            if credentials_path and not Path(credentials_path).is_file():
                raise LLMError(
                    f"vertex_gemini credentials path not found: {credentials_path}."
                )
        else:
            raise LLMError(
                f"Unsupported LLM_PROVIDER: {self.provider!r}. "
                "Use 'openai_compatible' or 'vertex_gemini'."
            )


logger = logging.getLogger(__name__)


class MiniMaxChatClient:
    def __init__(self, config: LLMConfig) -> None:
        self.config = config
        self.provider = (self.config.provider or "openai_compatible").strip().lower()
        self.session = requests.Session()
        # Use only the proxy explicitly configured for this app.
        self.session.trust_env = False
        if self.config.proxy_url:
            self.session.proxies.update(
                {
                    "http": self.config.proxy_url,
                    "https": self.config.proxy_url,
                }
            )

        self._google_credentials = None
        self._google_auth_request = None
        self.google_project_id = self.config.google_project_id
        self.google_location = self.config.google_location or "global"
        self.google_credentials_path = self.config.google_credentials_path

        if self.provider == "vertex_gemini":
            self._init_vertex_state()

    def chat(self, messages: list[dict[str, Any]], temperature: float = 0.3) -> str:
        if self.provider == "vertex_gemini":
            return self._vertex_chat(messages=messages, temperature=temperature)

        response = self._request_openai_compatible(messages=messages, temperature=temperature, stream=False)

        if response.status_code >= 400:
            raise LLMError(f"LLM request failed ({response.status_code}): {response.text}")

        data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content")
        if not content:
            raise LLMError("LLM returned empty content.")
        return content

    def chat_multimodal(
        self,
        prompt: str,
        inline_data: list[dict[str, Any]],
        temperature: float = 0.2,
    ) -> str:
        if self.provider == "vertex_gemini":
            token = self._get_vertex_access_token()
            payload = self._build_vertex_multimodal_payload(
                prompt=prompt,
                inline_data=inline_data,
                temperature=temperature,
            )
            url = (
                "https://aiplatform.googleapis.com/v1/"
                f"projects/{self.google_project_id}/locations/{self.google_location}/publishers/google/models/{self.config.model}:generateContent"
            )
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
            response = self._post_with_retries(url=url, headers=headers, json_payload=payload, stream=False)
            if response.status_code >= 400:
                raise LLMError(f"Gemini multimodal request failed ({response.status_code}): {response.text}")

            data = response.json()
            content = self._extract_vertex_text(data).strip()
            if not content:
                prompt_feedback = data.get("promptFeedback")
                if prompt_feedback:
                    raise LLMError(f"Gemini returned no multimodal text. Prompt feedback: {prompt_feedback}")
                raise LLMError("Gemini returned empty multimodal content.")
            return content

        messages = self._build_openai_compatible_multimodal_messages(prompt, inline_data)
        response = self._request_openai_compatible(messages=messages, temperature=temperature, stream=False)
        if response.status_code >= 400:
            raise LLMError(f"OpenAI-compatible multimodal request failed ({response.status_code}): {response.text}")

        data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content")
        if isinstance(content, list):
            content = "".join(str(part.get("text", "")) for part in content if isinstance(part, dict))
        if not content:
            raise LLMError("OpenAI-compatible model returned empty multimodal content.")
        return str(content)

    def stream_chat(
        self, messages: list[dict[str, Any]], temperature: float = 0.3
    ) -> Iterator[dict[str, str]]:
        if self.provider == "vertex_gemini":
            yield from self._vertex_stream_chat(messages=messages, temperature=temperature)
            return

        response = self._request_openai_compatible(messages=messages, temperature=temperature, stream=True)
        if response.status_code >= 400:
            raise LLMError(f"LLM request failed ({response.status_code}): {response.text}")

        started = time.perf_counter()
        tag_state = {"in_think": False, "pending": ""}
        if self.config.debug_stream:
            logger.info("LLM stream started status=%s", response.status_code)

        # Use tiny chunk_size to reduce buffering and improve token-level streaming feel.
        for raw_line in response.iter_lines(chunk_size=1, decode_unicode=True):
            if not raw_line:
                continue
            line = raw_line.strip()
            data_text = line[5:].strip() if line.startswith("data:") else line
            if data_text == "[DONE]":
                if self.config.debug_stream:
                    elapsed = time.perf_counter() - started
                    logger.info("LLM stream done elapsed=%.3fs", elapsed)
                break

            try:
                data = json.loads(data_text)
            except json.JSONDecodeError:
                if self.config.debug_stream:
                    elapsed = time.perf_counter() - started
                    snippet = data_text[:100].replace("\n", " ")
                    logger.info("LLM stream non-json chunk t=%.3fs text=%s", elapsed, snippet)
                continue

            choice = (data.get("choices") or [{}])[0]
            delta = choice.get("delta", {}) or {}

            thinking = delta.get("reasoning_content") or delta.get("reasoning") or ""
            if isinstance(thinking, str) and thinking:
                if self.config.debug_stream:
                    elapsed = time.perf_counter() - started
                    snippet = thinking[:100].replace("\n", " ")
                    logger.info("LLM stream thinking t=%.3fs len=%s text=%s", elapsed, len(thinking), snippet)
                yield {"type": "thinking", "text": thinking}

            content = delta.get("content")
            if isinstance(content, str) and content:
                for item in self._extract_stream_parts(content, tag_state):
                    if self.config.debug_stream:
                        elapsed = time.perf_counter() - started
                        snippet = item["text"][:100].replace("\n", " ")
                        logger.info(
                            "LLM stream %s t=%.3fs len=%s text=%s",
                            item["type"],
                            elapsed,
                            len(item["text"]),
                            snippet,
                        )
                    yield item

            # Some providers may return full message content in stream chunks.
            message_content = (choice.get("message") or {}).get("content")
            if isinstance(message_content, str) and message_content:
                for item in self._extract_stream_parts(message_content, tag_state):
                    if self.config.debug_stream:
                        elapsed = time.perf_counter() - started
                        snippet = item["text"][:100].replace("\n", " ")
                        logger.info(
                            "LLM stream message-%s t=%.3fs len=%s text=%s",
                            item["type"],
                            elapsed,
                            len(item["text"]),
                            snippet,
                        )
                    yield item

        # Flush any residual buffered text after stream ends.
        if tag_state["pending"]:
            final_type = "thinking" if tag_state["in_think"] else "content"
            yield {"type": final_type, "text": tag_state["pending"]}
            tag_state["pending"] = ""

    def _request_openai_compatible(
        self, messages: list[dict[str, Any]], temperature: float, stream: bool
    ) -> requests.Response:
        url = f"{self.config.base_url.rstrip('/')}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            # Some OpenAI-compatible providers rely on this for SSE streaming.
            "Accept": "text/event-stream" if stream else "application/json",
        }
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        payload: dict[str, Any] = {
            "model": self.config.model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream,
        }

        return self._post_with_retries(url=url, headers=headers, json_payload=payload, stream=stream)

    def _build_openai_compatible_multimodal_messages(
        self,
        prompt: str,
        inline_data: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        content_parts: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
        for item in inline_data:
            filename = str(item.get("filename", "")).strip() or "attachment"
            mime_type = str(item.get("mime_type", "")).strip() or "application/octet-stream"
            data = item.get("data", b"")
            raw_data = data.encode("utf-8") if isinstance(data, str) else bytes(data)
            if not raw_data:
                continue

            encoded = base64.b64encode(raw_data).decode("ascii")
            data_url = f"data:{mime_type};base64,{encoded}"
            if mime_type.startswith("image/"):
                content_parts.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": data_url},
                    }
                )
            else:
                content_parts.append(
                    {
                        "type": "file",
                        "file": {
                            "filename": filename,
                            "file_data": data_url,
                        },
                    }
                )
        return [{"role": "user", "content": content_parts}]

    def _post_with_retries(
        self,
        *,
        url: str,
        headers: dict[str, str],
        json_payload: dict[str, Any],
        stream: bool,
    ) -> requests.Response:
        attempts = self.config.max_retries + 1
        last_error: requests.RequestException | None = None

        for attempt in range(1, attempts + 1):
            try:
                return self.session.post(
                    url,
                    headers=headers,
                    json=json_payload,
                    timeout=self.config.timeout_seconds,
                    stream=stream,
                )
            except requests.RequestException as exc:
                last_error = exc
                if attempt >= attempts:
                    break
                # Lightweight backoff for unstable proxy/network hops.
                time.sleep(1.2 * attempt)

        raise LLMError(f"LLM network error: {last_error}")

    def _init_vertex_state(self) -> None:
        credentials_path = self.google_credentials_path.strip()
        if not credentials_path:
            raise LLMError(
                "Vertex Gemini provider requires `LLM_GCP_CREDENTIALS_PATH` or `GOOGLE_APPLICATION_CREDENTIALS`."
            )

        credentials_file = Path(credentials_path)
        if not credentials_file.exists():
            raise LLMError(f"Vertex Gemini credentials file not found: {credentials_file}")

        try:
            from google.auth.transport.requests import Request as GoogleAuthRequest
            from google.oauth2 import service_account
        except ImportError as exc:
            raise LLMError(
                "Vertex Gemini support requires the `google-auth` package. Install it with `python -m pip install google-auth`."
            ) from exc

        scopes = ["https://www.googleapis.com/auth/cloud-platform"]
        self._google_credentials = service_account.Credentials.from_service_account_file(
            str(credentials_file),
            scopes=scopes,
        )
        self._google_auth_request = GoogleAuthRequest(session=self.session)
        if not self.google_project_id:
            self.google_project_id = getattr(self._google_credentials, "project_id", "") or self._read_project_id(
                credentials_file
            )

        if not self.google_project_id:
            raise LLMError(
                "Vertex Gemini requires a Google Cloud project id. Set `LLM_GCP_PROJECT_ID` or use a credential file that includes `project_id`."
            )

    def _read_project_id(self, credentials_file: Path) -> str:
        try:
            data = json.loads(credentials_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return ""
        return str(data.get("project_id", "")).strip()

    def _vertex_chat(self, messages: list[dict[str, str]], temperature: float) -> str:
        token = self._get_vertex_access_token()
        payload = self._build_vertex_payload(messages=messages, temperature=temperature)
        url = (
            "https://aiplatform.googleapis.com/v1/"
            f"projects/{self.google_project_id}/locations/{self.google_location}/publishers/google/models/{self.config.model}:generateContent"
        )
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        response = self._post_with_retries(url=url, headers=headers, json_payload=payload, stream=False)
        if response.status_code >= 400:
            raise LLMError(f"Gemini request failed ({response.status_code}): {response.text}")

        data = response.json()
        content = self._extract_vertex_text(data).strip()
        if not content:
            prompt_feedback = data.get("promptFeedback")
            if prompt_feedback:
                raise LLMError(f"Gemini returned no text. Prompt feedback: {prompt_feedback}")
            raise LLMError("Gemini returned empty content.")
        return content

    def _vertex_stream_chat(
        self, messages: list[dict[str, str]], temperature: float
    ) -> Iterator[dict[str, str]]:
        token = self._get_vertex_access_token()
        payload = self._build_vertex_payload(messages=messages, temperature=temperature)
        url = (
            "https://aiplatform.googleapis.com/v1/"
            f"projects/{self.google_project_id}/locations/{self.google_location}/publishers/google/models/{self.config.model}:streamGenerateContent"
        )
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        response = self._post_with_retries(url=url, headers=headers, json_payload=payload, stream=True)
        if response.status_code >= 400:
            raise LLMError(f"Gemini stream request failed ({response.status_code}): {response.text}")

        emitted_text = ""
        received_any_text = False
        prompt_feedback: dict[str, Any] | None = None

        for data in self._iter_vertex_stream_objects(response):
            if prompt_feedback is None and isinstance(data.get("promptFeedback"), dict):
                prompt_feedback = data["promptFeedback"]

            content = self._extract_vertex_text(data)
            if not content:
                continue

            delta, emitted_text = self._resolve_vertex_stream_delta(previous=emitted_text, current=content)

            if not delta:
                continue

            received_any_text = True
            yield {"type": "content", "text": delta}

        if not received_any_text:
            if prompt_feedback:
                raise LLMError(f"Gemini returned no text. Prompt feedback: {prompt_feedback}")
            raise LLMError("Gemini returned empty streamed content.")

    def _get_vertex_access_token(self) -> str:
        if self._google_credentials is None or self._google_auth_request is None:
            raise LLMError("Vertex Gemini credentials are not initialized.")

        if not self._google_credentials.valid:
            last_error: Exception | None = None
            attempts = self.config.max_retries + 1
            for attempt in range(1, attempts + 1):
                try:
                    self._google_credentials.refresh(self._google_auth_request)
                    last_error = None
                    break
                except Exception as exc:
                    last_error = exc
                    if attempt >= attempts:
                        break
                    time.sleep(1.2 * attempt)

            if last_error is not None:
                raise LLMError(f"Failed to refresh Google access token for Vertex Gemini: {last_error}") from last_error

        token = getattr(self._google_credentials, "token", "")
        if not token:
            raise LLMError("Failed to obtain Google access token for Vertex Gemini.")
        return token

    def _build_vertex_payload(self, messages: list[dict[str, str]], temperature: float) -> dict[str, Any]:
        system_parts: list[str] = []
        contents: list[dict[str, Any]] = []

        for message in messages:
            role = str(message.get("role", "")).strip()
            content = str(message.get("content", "")).strip()
            if not content:
                continue

            if role == "system":
                system_parts.append(content)
                continue

            vertex_role = "model" if role == "assistant" else "user"
            contents.append(
                {
                    "role": vertex_role,
                    "parts": [{"text": content}],
                }
            )

        payload: dict[str, Any] = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
            },
        }
        if system_parts:
            payload["systemInstruction"] = {
                "parts": [{"text": "\n\n".join(system_parts)}],
            }
        return payload

    def _build_vertex_multimodal_payload(
        self,
        prompt: str,
        inline_data: list[dict[str, Any]],
        temperature: float,
    ) -> dict[str, Any]:
        parts: list[dict[str, Any]] = [{"text": prompt}]
        for item in inline_data:
            mime_type = str(item.get("mime_type", "")).strip()
            data = item.get("data", b"")
            if isinstance(data, str):
                raw_data = data.encode("utf-8")
            else:
                raw_data = bytes(data)
            if not mime_type or not raw_data:
                continue
            parts.append(
                {
                    "inlineData": {
                        "mimeType": mime_type,
                        "data": base64.b64encode(raw_data).decode("ascii"),
                    }
                }
            )

        return {
            "contents": [
                {
                    "role": "user",
                    "parts": parts,
                }
            ],
            "generationConfig": {
                "temperature": temperature,
            },
        }

    def _extract_vertex_text(self, data: dict[str, Any]) -> str:
        candidates = data.get("candidates") or []
        if not candidates:
            return ""

        parts = ((candidates[0].get("content") or {}).get("parts") or [])
        text_parts = [str(part.get("text", "")) for part in parts if isinstance(part, dict) and part.get("text")]
        return "".join(text_parts)

    def _iter_vertex_stream_objects(self, response: requests.Response) -> Iterator[dict[str, Any]]:
        buffer = ""
        for raw_chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
            if not raw_chunk:
                continue

            chunk = raw_chunk.decode("utf-8", errors="ignore") if isinstance(raw_chunk, bytes) else raw_chunk
            buffer += chunk

            objects, buffer = self._extract_json_objects_from_buffer(buffer)
            for item in objects:
                yield item

        objects, buffer = self._extract_json_objects_from_buffer(buffer)
        for item in objects:
            yield item

        if self.config.debug_stream and buffer.strip(" \r\n\t[],"):
            logger.info("Gemini stream leftover buffer: %s", buffer[:200])

    def _extract_json_objects_from_buffer(self, buffer: str) -> tuple[list[dict[str, Any]], str]:
        objects: list[dict[str, Any]] = []
        start_index: int | None = None
        depth = 0
        in_string = False
        escaped = False
        last_consumed = 0

        for index, char in enumerate(buffer):
            if start_index is None:
                if char in " \r\n\t[],":
                    last_consumed = index + 1
                    continue
                if char != "{":
                    last_consumed = index + 1
                    continue
                start_index = index
                depth = 1
                in_string = False
                escaped = False
                continue

            if in_string:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    in_string = False
                continue

            if char == '"':
                in_string = True
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    snippet = buffer[start_index : index + 1]
                    try:
                        parsed = json.loads(snippet)
                    except json.JSONDecodeError:
                        if self.config.debug_stream:
                            logger.info("Gemini stream invalid json snippet: %s", snippet[:200])
                        return objects, buffer[start_index:]

                    if isinstance(parsed, dict):
                        objects.append(parsed)
                    last_consumed = index + 1
                    start_index = None

        if start_index is not None:
            return objects, buffer[start_index:]
        return objects, buffer[last_consumed:].lstrip(" \r\n\t[],")

    def _resolve_vertex_stream_delta(self, previous: str, current: str) -> tuple[str, str]:
        if not current:
            return "", previous

        if not previous:
            return current, current

        if current.startswith(previous):
            return current[len(previous) :], current

        if previous.startswith(current):
            return "", previous

        common_length = 0
        max_common = min(len(previous), len(current))
        while common_length < max_common and previous[common_length] == current[common_length]:
            common_length += 1

        if common_length > 0:
            return current[common_length:], current

        return current, previous + current

    def _extract_stream_parts(self, chunk: str, state: dict[str, Any]) -> list[dict[str, str]]:
        open_tag = "<think>"
        close_tag = "</think>"
        carry_len = max(len(open_tag), len(close_tag)) - 1
        out: list[dict[str, str]] = []

        state["pending"] += chunk
        pending = state["pending"]

        while True:
            if state["in_think"]:
                end = pending.find(close_tag)
                if end == -1:
                    if len(pending) > carry_len:
                        emit = pending[:-carry_len]
                        if emit:
                            out.append({"type": "thinking", "text": emit})
                        pending = pending[-carry_len:]
                    break
                emit = pending[:end]
                if emit:
                    out.append({"type": "thinking", "text": emit})
                pending = pending[end + len(close_tag) :]
                state["in_think"] = False
                continue

            start = pending.find(open_tag)
            if start == -1:
                if len(pending) > carry_len:
                    emit = pending[:-carry_len]
                    if emit:
                        out.append({"type": "content", "text": emit})
                    pending = pending[-carry_len:]
                break

            emit = pending[:start]
            if emit:
                out.append({"type": "content", "text": emit})
            pending = pending[start + len(open_tag) :]
            state["in_think"] = True

        state["pending"] = pending
        return out
