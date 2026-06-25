from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from .structured_requirement_model import normalize_structured_requirement_model


IC_SUBSTRATE_DOMAIN_PACK_PATH = Path(__file__).resolve().parents[2] / "data" / "ic_substrate" / "domain_pack.json"


@lru_cache(maxsize=1)
def load_ic_substrate_domain_pack() -> dict[str, Any]:
    if not IC_SUBSTRATE_DOMAIN_PACK_PATH.exists():
        return {}
    with IC_SUBSTRATE_DOMAIN_PACK_PATH.open("r", encoding="utf-8") as pack_file:
        payload = json.load(pack_file)
    return payload if isinstance(payload, dict) else {}


def build_ic_substrate_evidence_state(
    readiness_gate: dict[str, Any] | None,
    structured_requirement_model: dict[str, Any] | None,
    department: str = "",
    product_shape: str = "",
    language: str | None = None,
) -> dict[str, Any]:
    pack = load_ic_substrate_domain_pack()
    gate = readiness_gate if isinstance(readiness_gate, dict) else {}
    if not gate.get("enabled"):
        return {
            "enabled": False,
            "version": str(pack.get("version", "")),
            "department": "",
            "department_label": "",
            "product_shape": "",
            "product_shape_label": "",
            "readiness_score": 0,
            "ready_for_expert_review": False,
            "missing_evidence": [],
            "checks": [],
            "domain_context": {},
            "guardrails": _string_list(_record(pack.get("guardrails")).get("forbidden_assumptions")),
        }

    model = normalize_structured_requirement_model(structured_requirement_model)
    normalized_department = _normalize_department(department or str(gate.get("department_specific_evidence", "")), pack)
    normalized_shape = _normalize_product_shape(product_shape, pack)
    checks = [_normalize_gate_check(check) for check in _record_list(gate.get("checks"))]
    missing_evidence = [
        str(key)
        for key in gate.get("missing_evidence", [])
        if str(key).strip()
    ] or [check["key"] for check in checks if not check["ready"]]
    ready_count = sum(1 for check in checks if check["ready"])
    readiness_score = round(ready_count / max(len(checks), 1) * 100)
    department_pack = _record(_record(pack.get("departments")).get(normalized_department))
    shape_pack = _record(_record(pack.get("product_shapes")).get(normalized_shape))

    return {
        "enabled": True,
        "version": str(pack.get("version", "")),
        "department": _department_label(normalized_department),
        "department_key": normalized_department,
        "department_label": str(department_pack.get("label", "")) or _department_label(normalized_department),
        "product_shape": normalized_shape,
        "product_shape_label": str(shape_pack.get("label", "")) or normalized_shape,
        "readiness_score": readiness_score,
        "ready_for_expert_review": readiness_score >= 85 and not missing_evidence,
        "missing_evidence": missing_evidence,
        "checks": checks,
        "domain_context": _build_domain_context(model, pack, normalized_department, normalized_shape),
        "question_ladder": _string_list(department_pack.get("question_ladder")),
        "shape_required_dimensions": _string_list(shape_pack.get("required_dimensions")),
        "guardrails": _string_list(_record(pack.get("guardrails")).get("forbidden_assumptions")),
    }


def _normalize_gate_check(check: dict[str, Any]) -> dict[str, Any]:
    evidence = str(check.get("evidence", "")).strip()
    ready = bool(check.get("ready"))
    if ready:
        status = "ready"
    elif evidence:
        status = "partial"
    else:
        status = "missing"
    return {
        "key": str(check.get("key", "")).strip(),
        "label": str(check.get("label", "")).strip(),
        "status": status,
        "ready": ready,
        "evidence": [evidence] if evidence else [],
        "missing": [] if ready else [str(check.get("if_missing", "")).strip()],
        "next_question": "" if ready else str(check.get("if_missing", "")).strip(),
    }


def _build_domain_context(
    model: dict[str, Any],
    pack: dict[str, Any],
    department: str,
    product_shape: str,
) -> dict[str, Any]:
    all_texts = _collect_text(model)
    all_text = "\n".join(all_texts).lower()
    data_dependencies = _string_list(model.get("data_and_dependencies"))
    business_rules = _string_list(model.get("business_rules"))
    acceptance = _string_list(model.get("acceptance_criteria"))
    department_pack = _record(_record(pack.get("departments")).get(department))
    business_objects = _string_list(department_pack.get("business_objects"))
    glossary_terms = _string_list(pack.get("glossary_seed_terms"))
    source_contract = _string_list(_record(pack.get("guardrails")).get("source_of_truth_contract"))

    matched_objects = [term for term in business_objects if term.lower() in all_text]
    matched_terms = [term for term in glossary_terms if term.lower() in all_text]

    return {
        "business_objects": matched_objects,
        "object_grain": _first_matching_text(all_texts, ["lot", "panel", "unit", "case", "grain", "route", "station", "对象", "粒度"]),
        "source_of_truth": _first_matching_text(data_dependencies, ["source", "truth", "system", "interface", "refresh", "reconciliation", "数据源", "系统", "接口", "刷新", "对账"]),
        "workflow_states": _first_matching_text(business_rules + acceptance + all_texts, ["state", "status", "owner", "hold", "release", "closure", "approval", "状态", "责任", "放行", "关闭", "审批"]),
        "confirmed_terms": matched_terms,
        "product_shape": product_shape,
        "source_of_truth_contract": source_contract,
    }


def _normalize_department(value: str, pack: dict[str, Any]) -> str:
    normalized = value.strip().lower()
    aliases = {
        "production": "production",
        "prod": "production",
        "quality": "quality",
        "qdm": "quality",
        "tdi": "tdi",
        "general": "general",
    }
    normalized = aliases.get(normalized, normalized)
    departments = _record(pack.get("departments"))
    return normalized if normalized in departments else ""


def _department_label(department: str) -> str:
    labels = {
        "production": "Production",
        "quality": "Quality",
        "tdi": "TDI",
        "general": "General",
    }
    return labels.get(department, department)


def _normalize_product_shape(value: str, pack: dict[str, Any]) -> str:
    normalized = value.strip().lower()
    aliases = {
        "workflow": "workflow_tracker",
        "case_tracking": "workflow_tracker",
        "case tracker": "workflow_tracker",
        "planning": "planning_simulation",
        "simulation": "planning_simulation",
        "scheduling": "planning_simulation",
        "schedule": "planning_simulation",
        "forecast": "planning_simulation",
        "forecasting": "planning_simulation",
        "capacity loading": "planning_simulation",
        "report": "report_export",
        "export": "report_export",
        "query": "data_query",
        "search": "data_query",
        "alert": "alerting",
        "alarm": "alerting",
        "admin": "admin_tool",
        "console": "admin_tool",
    }
    normalized = aliases.get(normalized, normalized)
    shapes = _record(pack.get("product_shapes"))
    return normalized if normalized in shapes else ""


def _collect_text(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        texts: list[str] = []
        for item in value:
            texts.extend(_collect_text(item))
        return texts
    if isinstance(value, dict):
        texts = []
        for item in value.values():
            texts.extend(_collect_text(item))
        return texts
    return []


def _first_matching_text(values: list[str], keywords: list[str]) -> str:
    normalized_keywords = [keyword.lower() for keyword in keywords]
    for value in values:
        text = str(value).strip()
        if not text:
            continue
        lowered = text.lower()
        if any(keyword in lowered for keyword in normalized_keywords):
            return text[:220]
    return ""


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _record(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _record_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]
