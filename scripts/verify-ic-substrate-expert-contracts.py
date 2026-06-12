#!/usr/bin/env python3
"""Static regression checks for the IC Substrate expert PM contracts.

The checks intentionally avoid importing the Flask app so they can run in a
minimal Python environment during packaging or code review.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIREMENT_COLLECTOR = ROOT / "app" / "services" / "requirement_collector.py"
FRONTEND_APP = ROOT / "frontend" / "src" / "App.vue"
REQUIREMENT_PREVIEW = ROOT / "frontend" / "src" / "components" / "RequirementMarkdownPreview.vue"


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def method_body(source: str, name: str) -> str:
    match = re.search(rf"^    def {re.escape(name)}\(", source, re.MULTILINE)
    require(match is not None, f"missing method {name}")
    start = match.start()
    next_match = re.search(r"^    def \w+\(", source[match.end() :], re.MULTILINE)
    if next_match is None:
        return source[start:]
    return source[start : match.end() + next_match.start()]


def require_all(text: str, snippets: list[str], label: str) -> None:
    missing = [snippet for snippet in snippets if snippet not in text]
    require(not missing, f"{label} missing snippets: {missing}")


def main() -> None:
    collector = REQUIREMENT_COLLECTOR.read_text(encoding="utf-8")
    frontend = FRONTEND_APP.read_text(encoding="utf-8")
    preview = REQUIREMENT_PREVIEW.read_text(encoding="utf-8")

    active_departments = re.search(
        r"ACTIVE_IC_SUBSTRATE_DEPARTMENTS\s*=\s*\(([^)]*)\)",
        collector,
        re.MULTILINE,
    )
    require(active_departments is not None, "missing active department constant")
    normalized_departments = re.findall(r'"([^"]+)"', active_departments.group(1))
    require(
        normalized_departments == ["production", "quality", "tdi", "general"],
        f"unexpected active departments: {normalized_departments}",
    )

    conversation_prompt = method_body(collector, "_conversation_chain_state_for_prompt")
    send_user_message = method_body(collector, "send_user_message")
    stream_user_message = method_body(collector, "stream_user_message")
    structured_prompt = method_body(collector, "_structured_requirement_model_prompt")
    prd_prompt = method_body(collector, "_prd_doc_prompt")
    document_quality_gate = method_body(collector, "_document_quality_gate")
    quality_gate_block = method_body(collector, "_document_quality_gate_block_markdown")
    evidence_appendix = method_body(collector, "_append_ic_substrate_prd_evidence_appendix")
    evidence_appendix_heading = method_body(collector, "_ic_substrate_prd_evidence_appendix_heading")
    evidence_appendix_formatter = method_body(collector, "_format_ic_substrate_prd_evidence_appendix")
    stream_prd_document = method_body(collector, "stream_prd_document")
    build_prd_document = method_body(collector, "build_prd_document")
    readiness_gate = method_body(collector, "_ic_substrate_readiness_evidence_gate")
    browser_handoff = method_body(collector, "build_browser_handoff_payload")
    implementation_context = method_body(collector, "build_implementation_context")
    implementation_prompt = method_body(collector, "_build_implementation_prompt")
    language_router = method_body(collector, "_language_for_user_message")
    choice_formatter = method_body(collector, "_ensure_choice_question_format")
    fallback_choice_block = method_body(collector, "_fallback_choice_block")
    json_parser = method_body(collector, "_parse_json_from_model_output")
    json_trailing_comma_repair = method_body(collector, "_remove_json_trailing_commas")
    expert_gate = method_body(collector, "_ic_substrate_expert_prd_quality_gate_for_prompt")
    department_playbook = method_body(collector, "_ic_substrate_production_tdi_quality_playbook_guidance")
    extraction_contract = method_body(collector, "_ic_substrate_structured_extraction_contract")
    document_contract = method_body(collector, "_ic_substrate_prd_document_contract")

    require(
        "_ic_substrate_expert_prd_quality_gate_for_prompt" in conversation_prompt,
        "conversation prompt does not include expert PRD quality gate",
    )
    require(
        "_ic_substrate_structured_extraction_contract" in structured_prompt,
        "structured extraction prompt does not include IC Substrate contract",
    )
    require(
        "_ic_substrate_prd_document_contract" in prd_prompt,
        "PRD prompt does not include IC Substrate document contract",
    )
    require(
        "_ic_substrate_readiness_evidence_gate" in document_quality_gate
        and "ic_substrate_readiness_evidence" in document_quality_gate,
        "document quality gate does not expose IC Substrate readiness evidence",
    )
    require_all(
        build_prd_document,
        ["_append_ic_substrate_prd_evidence_appendix", "doc_markdown=doc_markdown"],
        "non-streaming PRD evidence appendix",
    )
    require_all(
        stream_prd_document,
        [
            "_append_ic_substrate_prd_evidence_appendix",
            "yield {\"event\": \"content\", \"delta\": appendix_delta}",
            "doc_markdown = appended_doc_markdown",
        ],
        "streaming PRD evidence appendix",
    )
    require_all(
        evidence_appendix,
        [
            "_ic_substrate_readiness_evidence_gate",
            "_format_ic_substrate_prd_evidence_appendix",
            "IC Substrate Expert Evidence Appendix",
        ],
        "PRD evidence appendix append guard",
    )
    require_all(
        evidence_appendix_formatter,
        [
            "ready_count",
            "missing_evidence",
            "mandatory_rules",
            "Evidence status",
        ],
        "PRD evidence appendix formatter",
    )
    require_all(
        evidence_appendix_heading,
        [
            "IC Substrate Expert Evidence Appendix",
            "IC Substrate 专家证据附录",
            "IC Substrate Experten-Evidence-Anhang",
            "Lampiran Evidence Pakar IC Substrate",
        ],
        "PRD evidence appendix four-language headings",
    )
    require_all(
        language_router,
        ["_ = user_message", "return self._normalize_language(language)"],
        "UI language lock for user message responses",
    )
    require_all(
        send_user_message,
        [
            "response_language = self._language_for_user_message(language, user_message)",
            "assistant_text = self._ensure_choice_question_format(assistant_text, response_language)",
        ],
        "non-streaming assistant choice fallback",
    )
    require_all(
        stream_user_message,
        [
            "response_language = self._language_for_user_message(language, user_message)",
            "formatted_assistant_text = self._ensure_choice_question_format(assistant_text, response_language)",
            "yield {\"event\": \"content\", \"delta\": assistant_delta}",
            "assistant_text = formatted_assistant_text",
        ],
        "streaming assistant choice fallback",
    )
    require_all(
        choice_formatter,
        ["_looks_like_clarification_question", "_has_choice_options", "_fallback_choice_block"],
        "assistant choice formatter",
    )
    require_all(
        fallback_choice_block,
        [
            "A. Use the suggested interpretation",
            "A. 同意按上面的建议口径",
            "A. Die oben genannte Empfehlung",
            "A. Terima cadangan",
        ],
        "four-language fallback choice blocks",
    )
    require_all(
        json_parser,
        ["_json_candidate_variants", "_try_load_first_json_object"],
        "structured requirement JSON parser repair path",
    )
    require_all(
        json_trailing_comma_repair,
        ['lstrip("\\ufeff")', "in_string", "lookahead", 'cleaned[lookahead] in \"}]\"'],
        "structured requirement JSON trailing comma repair",
    )

    expert_gate_terms = [
        "Production",
        "Quality",
        "TDI",
        "General",
        "lot/panel/unit",
        "acceptance",
    ]
    extraction_terms = expert_gate_terms + [
        "source of truth",
        "open question",
        "collection_status",
        "pending_confirmation",
    ]
    document_terms = [
        "Production",
        "Quality",
        "TDI",
        "General",
        "lot/panel/unit",
        "source of truth",
        "Open Questions",
        "Functional Requirements",
        "Acceptance Criteria",
    ]
    require_all(expert_gate, expert_gate_terms, "expert quality gate")
    require_all(
        department_playbook,
        [
            "专家追问梯子",
            "Expert question ladder",
            "专家必确认清单",
            "Expert must-confirm checklist",
            "source of truth",
            "Finished Lot",
            "numerator/denominator",
            "clock start/pause/stop",
            "defect taxonomy",
            "inspection coverage",
            "defect code hierarchy",
            "closure/reopen",
            "writeback target",
        ],
        "department expert playbook",
    )
    require_all(extraction_contract, extraction_terms, "structured extraction contract")
    require_all(document_contract, document_terms, "PRD document contract")
    require_all(
        readiness_gate,
        [
            "entry_owner",
            "business_action",
            "object_grain",
            "workflow_state_owner",
            "data_reconciliation",
            "acceptance_evidence",
            "uncertainty_handling",
            "source of truth",
            "Never invent formulas",
        ],
        "IC Substrate readiness evidence gate",
    )
    require_all(
        browser_handoff,
        ["ic_substrate_evidence", "STRUCTURED_REQUIREMENT_CANONICAL_CACHE_KEY"],
        "browser coding handoff evidence payload",
    )
    require_all(
        implementation_context,
        ["ic_substrate_evidence", "STRUCTURED_REQUIREMENT_CANONICAL_CACHE_KEY"],
        "implementation context evidence payload",
    )
    require_all(
        implementation_prompt,
        ["ic_substrate_evidence", "Read that evidence package", "Do not invent formulas"],
        "implementation prompt evidence instructions",
    )
    require_all(
        quality_gate_block,
        [
            "IC Substrate Expert Evidence Gaps",
            "ic_substrate_readiness_evidence",
            "if_missing",
        ],
        "quality gate blocked markdown",
    )

    language_markers = ['normalized_language == "zh"', 'normalized_language == "de"', 'normalized_language == "ms"']
    for label, body in {
        "expert quality gate": expert_gate,
        "structured extraction contract": extraction_contract,
        "PRD document contract": document_contract,
    }.items():
        require_all(body, language_markers, label)

    start_department_match = re.search(
        r"const icSubstrateStartDepartments\s*=\s*\[([^\]]*)\]",
        frontend,
        re.MULTILINE,
    )
    require(start_department_match is not None, "missing frontend start department picker")
    start_departments = re.findall(r"'([^']+)'", start_department_match.group(1))
    require(
        start_departments == ["Production", "Quality", "TDI"],
        f"frontend visible IC Substrate picker should expose only Production/Quality/TDI chips, got {start_departments}",
    )
    require(
        "General requirement" in frontend and "IC Substrate professional chain" in frontend,
        "frontend new-chat entry cards should keep General and IC Substrate paths",
    )
    require_all(
        preview,
        [
            "icSubstrateEvidence",
            "asIcSubstrateEvidenceSection",
            "Entry department and owner",
            "Object grain",
            "Data source and reconciliation",
            "Acceptance evidence",
        ],
        "frontend developer markdown IC Substrate evidence checklist",
    )

    print("IC Substrate expert PM contracts verified.")


if __name__ == "__main__":
    main()
