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
    structured_prompt = method_body(collector, "_structured_requirement_model_prompt")
    prd_prompt = method_body(collector, "_prd_doc_prompt")
    document_quality_gate = method_body(collector, "_document_quality_gate")
    readiness_gate = method_body(collector, "_ic_substrate_readiness_evidence_gate")
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
            "source of truth",
            "Finished Lot",
            "defect taxonomy",
            "closure/reopen",
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

    print("IC Substrate expert PM contracts verified.")


if __name__ == "__main__":
    main()
