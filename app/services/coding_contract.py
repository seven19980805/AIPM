from __future__ import annotations

from typing import Any, Iterable

from .data_source_policy import (
    classify_data_paths,
    normalize_writeback_authorization,
    referenced_source_types,
    sanitize_data_dependencies,
    writeback_is_authorized,
)
from .structured_requirement_model import normalize_structured_requirement_model


WORKFLOW_MODES = {"scratch", "draft", "template"}

_PHASE_DEFINITIONS = {
    "scratch": (
        ("discover", ("objective", "users", "scenarios")),
        ("define_solution", ("scope", "features", "rules")),
        ("connect_data", ("integrations",)),
        ("verify", ("acceptance",)),
    ),
    "draft": (
        ("extract_draft", ("objective", "scope", "users", "scenarios")),
        ("close_draft_gaps", ("features", "rules", "integrations")),
        ("verify_draft", ("acceptance",)),
    ),
    "template": (
        ("validate_baseline", ("objective", "scope", "users")),
        (
            "close_template_gaps",
            ("scenarios", "features", "rules", "integrations"),
        ),
        ("verify_template_delta", ("acceptance",)),
    ),
}

_PHASE_LABELS = {
    "en": {
        "discover": "Discover the outcome",
        "define_solution": "Define the solution",
        "shape_experience": "Shape UX and data",
        "connect_data": "Confirm the data boundary",
        "verify": "Lock acceptance",
        "extract_draft": "Extract confirmed draft facts",
        "close_draft_gaps": "Close draft gaps and conflicts",
        "verify_draft": "Verify acceptance",
        "validate_baseline": "Validate template baseline",
        "close_template_gaps": "Close template gaps",
        "verify_template_delta": "Verify changes and acceptance",
        "package": "Generate Build Brief",
        "handoff": "Ready for Go Coding",
    },
    "zh": {
        "discover": "发现目标与场景",
        "define_solution": "定义首版方案",
        "shape_experience": "明确页面与数据",
        "connect_data": "确认数据边界",
        "verify": "锁定验收",
        "extract_draft": "提取草稿已确认事实",
        "close_draft_gaps": "补齐草稿缺口与冲突",
        "verify_draft": "确认验收",
        "validate_baseline": "校验模板基线",
        "close_template_gaps": "补齐模板差异",
        "verify_template_delta": "确认变更与验收",
        "package": "生成开发简报",
        "handoff": "可交接 Go Coding",
    },
    "de": {
        "discover": "Ziel und Szenarien klaeren",
        "define_solution": "Loesung definieren",
        "shape_experience": "UX und Daten klaeren",
        "connect_data": "Datengrenze bestaetigen",
        "verify": "Abnahme festlegen",
        "extract_draft": "Bestaetigte Draft-Fakten extrahieren",
        "close_draft_gaps": "Draft-Luecken schliessen",
        "verify_draft": "Abnahme pruefen",
        "validate_baseline": "Template-Basis pruefen",
        "close_template_gaps": "Template-Luecken schliessen",
        "verify_template_delta": "Aenderungen und Abnahme pruefen",
        "package": "Build Brief erzeugen",
        "handoff": "Bereit fuer Go Coding",
    },
    "ms": {
        "discover": "Kenal pasti hasil dan senario",
        "define_solution": "Tentukan penyelesaian",
        "shape_experience": "Tetapkan UX dan data",
        "connect_data": "Sahkan sempadan data",
        "verify": "Kunci penerimaan",
        "extract_draft": "Ekstrak fakta draft",
        "close_draft_gaps": "Lengkapkan jurang draft",
        "verify_draft": "Sahkan penerimaan",
        "validate_baseline": "Sahkan garis dasar templat",
        "close_template_gaps": "Lengkapkan jurang templat",
        "verify_template_delta": "Sahkan perubahan dan penerimaan",
        "package": "Jana Build Brief",
        "handoff": "Sedia untuk Go Coding",
    },
}

_REQUIREMENT_LABELS = {
    "en": {
        "objective": "Business objective",
        "scope": "Scope boundary",
        "users": "Target users",
        "scenarios": "Core scenarios",
        "features": "Functional requirements",
        "pages": "Pages and interactions",
        "rules": "Business rules",
        "integrations": "Data and integrations",
        "acceptance": "Acceptance criteria",
    },
    "zh": {
        "objective": "业务目标",
        "scope": "范围边界",
        "users": "目标用户",
        "scenarios": "核心场景",
        "features": "功能需求",
        "pages": "页面与交互",
        "rules": "业务规则",
        "integrations": "数据与集成",
        "acceptance": "验收标准",
    },
}


def normalize_workflow_mode(value: str | None) -> str:
    normalized = str(value or "").strip().lower()
    return normalized if normalized in WORKFLOW_MODES else "scratch"


def workflow_mode_for_template(template_id: str | None) -> str:
    return "template" if str(template_id or "").strip() else "scratch"


def build_delivery_workflow(
    structured_requirement_model: dict[str, Any] | None,
    *,
    workflow_mode: str,
    language: str = "en",
    has_prd_document: bool = False,
) -> dict[str, Any]:
    model = normalize_structured_requirement_model(structured_requirement_model)
    mode = normalize_workflow_mode(workflow_mode)
    normalized_language = _normalize_language(language)
    phase_labels = _PHASE_LABELS[normalized_language]
    collection_status = model["collection_status"]

    phases: list[dict[str, Any]] = []
    ordered_fields: list[str] = []
    requirements_complete = True

    for phase_key, field_keys in _PHASE_DEFINITIONS[mode]:
        ordered_fields.extend(field_keys)
        statuses = [collection_status[key]["status"] for key in field_keys]
        phase_complete = all(status == "confirmed" for status in statuses)
        requirements_complete = requirements_complete and phase_complete
        phases.append(
            {
                "key": phase_key,
                "label": phase_labels[phase_key],
                "field_keys": list(field_keys),
                "status": "complete" if phase_complete else "pending",
                "completion": _phase_completion(statuses),
            }
        )

    first_incomplete = next(
        (index for index, phase in enumerate(phases) if phase["status"] != "complete"),
        None,
    )
    if first_incomplete is not None:
        phases[first_incomplete]["status"] = "current"

    package_status = "complete" if has_prd_document and requirements_complete else "pending"
    if requirements_complete and not has_prd_document:
        package_status = "current"
    phases.append(
        {
            "key": "package",
            "label": phase_labels["package"],
            "field_keys": [],
            "status": package_status,
            "completion": 100 if has_prd_document else 0,
        }
    )
    phases.append(
        {
            "key": "handoff",
            "label": phase_labels["handoff"],
            "field_keys": [],
            "status": "current" if requirements_complete and has_prd_document else "pending",
            "completion": 100 if requirements_complete and has_prd_document else 0,
        }
    )

    blocking_fields = _blocking_fields(
        collection_status,
        ordered_fields,
        normalized_language,
    )
    ready_for_documents = requirements_complete and not blocking_fields
    ready_for_handoff = ready_for_documents and has_prd_document
    if ready_for_handoff:
        current_phase = "handoff"
    elif ready_for_documents:
        current_phase = "package"
    else:
        current_phase = next(
            phase["key"] for phase in phases if phase["status"] == "current"
        )

    required_fields = list(dict.fromkeys(ordered_fields))
    confirmed_count = sum(
        1
        for key in required_fields
        if collection_status[key]["status"] == "confirmed"
    )
    readiness_percentage = round(
        ((confirmed_count + (1 if has_prd_document and ready_for_documents else 0))
        / (len(required_fields) + 1))
        * 100
    )

    return {
        "schema_version": "1.0",
        "workflow_mode": mode,
        "current_phase": current_phase,
        "phases": phases,
        "blocking_fields": blocking_fields,
        "confirmed_fields": confirmed_count,
        "total_fields": len(required_fields),
        "readiness_percentage": readiness_percentage,
        "ready_for_documents": ready_for_documents,
        "ready_for_handoff": ready_for_handoff,
        "next_action": _next_action(
            mode,
            current_phase,
            blocking_fields,
            normalized_language,
        ),
    }


def build_coding_contract(
    structured_requirement_model: dict[str, Any] | None,
    *,
    session_id: str,
    title: str,
    workflow_mode: str,
    template_id: str = "",
    template_name: str = "",
    language: str = "en",
    has_prd_document: bool = False,
) -> dict[str, Any]:
    model = normalize_structured_requirement_model(structured_requirement_model)
    mode = normalize_workflow_mode(workflow_mode)
    readiness = build_delivery_workflow(
        model,
        workflow_mode=mode,
        language=language,
        has_prd_document=has_prd_document,
    )
    features = [
        {
            "id": _stable_id("F", index),
            **feature,
        }
        for index, feature in enumerate(
            model["functional_requirements"]["feature_details"],
            start=1,
        )
    ]
    screens = [
        {
            "id": _stable_id("UI", index),
            "name": page["page_name"],
            "entry_point": page["entry_point"],
            "elements": page["page_elements"],
            "actions": page["button_actions"],
        }
        for index, page in enumerate(
            model["page_and_interaction"]["pages"],
            start=1,
        )
    ]
    business_rules = [
        {"id": _stable_id("BR", index), "rule": value}
        for index, value in enumerate(model["business_rules"], start=1)
    ]
    acceptance_tests = [
        {"id": _stable_id("AC", index), "statement": value}
        for index, value in enumerate(model["acceptance_criteria"], start=1)
    ]
    sanitized_dependencies = sanitize_data_dependencies(
        model["data_and_dependencies"],
        language=_normalize_language(language),
        writeback_authorization=model["writeback_authorization"],
    )
    dependencies = [
        {"id": _stable_id("DD", index), "requirement": value}
        for index, value in enumerate(sanitized_dependencies, start=1)
    ]
    blockers = [
        {
            "key": item["key"],
            "status": item["status"],
            "reason": item["reason"],
            "questions": item["questions"],
        }
        for item in readiness["blocking_fields"]
    ]
    unresolved_items = _unique_strings(
        [
            *model["open_questions"],
            *(
                question
                for blocker in blockers
                for question in blocker["questions"]
            ),
        ]
    )

    return {
        "schema_version": "1.0",
        "contract_kind": "small_model_coding_contract",
        "session_id": session_id,
        "title": title,
        "language": _normalize_language(language),
        "workflow_mode": mode,
        "source": {
            "type": mode,
            "template_id": template_id if mode == "template" else "",
            "template_name": template_name if mode == "template" else "",
        },
        "execution_policy": {
            "primary_source": "coding_contract",
            "delivery_strategy": "vertical_slices_in_packet_order",
            "assumption_policy": "record_and_surface_do_not_silently_invent",
            "change_policy": "stay_within_confirmed_scope",
            "required_finish": ["runnable_project", "critical_path_tests", "runbook"],
        },
        "project": {
            "name": model["document_info"]["project_name"] or title,
            "requirement_name": model["document_info"]["requirement_name"],
            "objective": model["background"]["objective"],
            "background": model["background"]["summary"],
            **model["product_context"],
        },
        "scope": model["scope"],
        "users": model["users_and_scenarios"]["target_users"],
        "scenarios": model["users_and_scenarios"]["core_scenarios"],
        "features": features,
        "screens": screens,
        "interaction_flow": model["page_and_interaction"]["interaction_flow"],
        "business_rules": business_rules,
        "data_dependencies": dependencies,
        "data_policy": _company_data_policy(
            model["data_and_dependencies"],
            writeback_authorization=model["writeback_authorization"],
        ),
        "acceptance_tests": acceptance_tests,
        "risks": model["risks_and_notes"],
        "unresolved_items": unresolved_items,
        "blockers": blockers,
        "do_not_invent": [
            "Business formulas or KPI definitions",
            "Source-system fields, tables, endpoints, or credentials",
            "Workflow states, owners, approvals, or SLA values",
            "Production writeback or automation not explicitly confirmed",
            "Features outside the confirmed first-version scope",
        ],
        "implementation_packets": _implementation_packets(
            features,
            screens,
            business_rules,
            dependencies,
            acceptance_tests,
        ),
        "delivery_readiness": readiness,
    }


def render_coding_contract_markdown(contract: dict[str, Any]) -> str:
    project = contract.get("project", {})
    readiness = contract.get("delivery_readiness", {})
    lines = [
        "# Coding Contract",
        "",
        f"- Schema: `{contract.get('schema_version', '')}`",
        f"- Workflow: `{contract.get('workflow_mode', '')}`",
        f"- Project: {project.get('name', '')}",
        f"- Ready for Build Brief: `{str(bool(readiness.get('ready_for_documents'))).lower()}`",
        f"- Ready for handoff: `{str(bool(readiness.get('ready_for_handoff'))).lower()}`",
        "",
        "## Execution Protocol",
        "",
        "1. Treat this Coding Contract as the primary source of truth.",
        "2. Execute implementation packets in ID order and finish each packet's done criteria.",
        "3. Use the Build Brief only as supporting context.",
        "4. Do not invent formulas, source fields, workflow states, owners, writeback, or extra scope.",
        "5. Put unresolved items in `ASSUMPTIONS.md` and keep affected behavior conservative.",
        "",
        "## Product Boundary",
        "",
        f"- Objective: {project.get('objective', '')}",
        f"- Primary user: {project.get('primary_user', '')}",
        f"- Decision/action: {project.get('decision_or_action', '')}",
        f"- In scope: {_join(contract.get('scope', {}).get('in_scope', []))}",
        f"- Out of scope: {_join(contract.get('scope', {}).get('out_of_scope', []))}",
        "",
        "## Features",
        "",
    ]
    lines.extend(
        f"- **{item['id']} {item.get('feature_name', '')}**: {item.get('description', '')}"
        for item in contract.get("features", [])
    )
    lines.extend(["", "## Screens", ""])
    lines.extend(
        f"- **{item['id']} {item.get('name', '')}**: {_join(item.get('elements', []))}"
        for item in contract.get("screens", [])
    )
    lines.extend(["", "## Business Rules", ""])
    lines.extend(
        f"- **{item['id']}**: {item.get('rule', '')}"
        for item in contract.get("business_rules", [])
    )
    lines.extend(["", "## Data Dependencies", ""])
    lines.extend(
        f"- **{item['id']}**: {item.get('requirement', '')}"
        for item in contract.get("data_dependencies", [])
    )
    data_policy = contract.get("data_policy", {})
    lines.append(
        f"- Writeback default: `{data_policy.get('writeback_default', 'forbidden')}`"
    )
    lines.extend(["", "## Acceptance Tests", ""])
    lines.extend(
        f"- **{item['id']}**: {item.get('statement', '')}"
        for item in contract.get("acceptance_tests", [])
    )
    lines.extend(["", "## Implementation Packets", ""])
    for packet in contract.get("implementation_packets", []):
        lines.extend(
            [
                f"### {packet['id']} {packet['title']}",
                "",
                f"- Depends on: {_join(packet.get('depends_on', [])) or 'None'}",
                f"- Inputs: {_join(packet.get('input_ids', [])) or 'Confirmed contract'}",
                f"- Deliverables: {_join(packet.get('deliverables', []))}",
                f"- Done when: {_join(packet.get('done_when', []))}",
                "",
            ]
        )
    if contract.get("blockers"):
        lines.extend(["## Blocking Items", ""])
        for blocker in contract["blockers"]:
            lines.append(
                f"- **{blocker['key']} / {blocker['status']}**: "
                f"{blocker.get('reason', '')} {_join(blocker.get('questions', []))}".strip()
            )
        lines.append("")
    if contract.get("unresolved_items"):
        lines.extend(["## Unresolved Items", ""])
        lines.extend(f"- {item}" for item in contract["unresolved_items"])
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def _phase_completion(statuses: Iterable[str]) -> int:
    points = {
        "missing": 0,
        "conflict": 0,
        "captured": 40,
        "pending_confirmation": 65,
        "confirmed": 100,
    }
    values = [points.get(status, 0) for status in statuses]
    return round(sum(values) / len(values)) if values else 0


def _blocking_fields(
    collection_status: dict[str, Any],
    ordered_fields: list[str],
    language: str,
) -> list[dict[str, Any]]:
    labels = _REQUIREMENT_LABELS.get(language, _REQUIREMENT_LABELS["en"])
    blockers = []
    for key in ordered_fields:
        item = collection_status[key]
        if item["status"] == "confirmed":
            continue
        blockers.append(
            {
                "key": key,
                "label": labels.get(key, key),
                "status": item["status"],
                "reason": item["reason"],
                "questions": item["pending_questions"],
            }
        )
    return blockers


def _next_action(
    mode: str,
    current_phase: str,
    blockers: list[dict[str, Any]],
    language: str,
) -> str:
    if current_phase == "handoff":
        return {
            "zh": "开发简报已就绪，可交接给 Go Coding。",
            "de": "Der Build Brief ist fuer Go Coding bereit.",
            "ms": "Build Brief sedia dihantar ke Go Coding.",
            "en": "The Build Brief is ready for Go Coding.",
        }[language]
    if current_phase == "package":
        return {
            "zh": "需求已确认，下一步生成面向小编程模型的开发简报。",
            "de": "Anforderungen sind bestaetigt. Als Naechstes den Build Brief erzeugen.",
            "ms": "Keperluan telah disahkan. Jana Build Brief seterusnya.",
            "en": "Requirements are confirmed. Generate the small-model Build Brief next.",
        }[language]
    blocker_label = blockers[0]["label"] if blockers else current_phase
    if language == "zh":
        verb = "校验模板中的" if mode == "template" else "明确"
        return f"下一步：{verb}{blocker_label}。"
    if language == "de":
        return f"Naechster Schritt: {blocker_label} klaeren."
    if language == "ms":
        return f"Langkah seterusnya: sahkan {blocker_label}."
    verb = "Validate the template's" if mode == "template" else "Clarify"
    return f"Next: {verb} {blocker_label}."


def _company_data_policy(
    dependencies: list[str],
    *,
    writeback_authorization: Any = None,
) -> dict[str, Any]:
    classification = classify_data_paths(
        dependencies,
        writeback_authorization=writeback_authorization,
    )
    return {
        "allowed_sources": [
            {
                "type": "sql_server",
                "connection_mode": "read_only_by_default",
            },
            {
                "type": "sap",
                "connection_mode": "read_only_by_default",
            },
            {
                "type": "mes",
                "connection_mode": "read_only_by_default",
            },
            {
                "type": "qis",
                "connection_mode": "read_only_by_default",
            },
            {
                "type": "qms",
                "connection_mode": "read_only_by_default",
            },
            {
                "type": "file_upload",
                "connection_mode": "user_supplied",
                "formats": [".xlsx", ".xls", ".csv"],
                "optional": True,
            },
        ],
        "referenced_sources": referenced_source_types(dependencies),
        "writeback_authorization": classification["writeback_authorization"],
        "writeback_target_types": classification["writeback_target_types"],
        "writeback_default": "forbidden",
        "writeback_requested": classification["writeback_requested"],
        "writeback_authorized": classification["writeback_authorized"],
        "pending_writeback": classification["pending_writeback"],
        "writeback_rule": "Only implement writeback when system, owner, fields, validation, and approval are explicitly confirmed.",
    }


def _implementation_packets(
    features: list[dict[str, Any]],
    screens: list[dict[str, Any]],
    rules: list[dict[str, Any]],
    dependencies: list[dict[str, Any]],
    acceptance_tests: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [
        {
            "id": "P-01",
            "title": "Foundation and runnable skeleton",
            "depends_on": [],
            "input_ids": [],
            "deliverables": [
                "Project structure and dependency manifests",
                "Environment example without secrets",
                "Local startup and health-check path",
            ],
            "done_when": [
                "The project installs and starts locally",
                "README contains exact run and verification commands",
            ],
        },
        {
            "id": "P-02",
            "title": "Data boundary and persistence",
            "depends_on": ["P-01"],
            "input_ids": [item["id"] for item in dependencies],
            "deliverables": [
                "Typed data-source interfaces",
                "SQL Server, SAP, or upload adapters only when referenced",
                "Validation and empty/error states",
            ],
            "done_when": [
                "No unconfirmed source fields or writeback are invented",
                "Adapters can be replaced without changing business logic",
            ],
        },
        {
            "id": "P-03",
            "title": "Business capabilities and API",
            "depends_on": ["P-02"],
            "input_ids": [
                *[item["id"] for item in features],
                *[item["id"] for item in rules],
            ],
            "deliverables": [
                "Critical business flow implemented end to end",
                "Consistent validation, field names, and error responses",
            ],
            "done_when": [
                "Every referenced feature and business rule is traceable by ID",
                "Core API/service tests pass",
            ],
        },
        {
            "id": "P-04",
            "title": "User workflow and screens",
            "depends_on": ["P-03"],
            "input_ids": [item["id"] for item in screens],
            "deliverables": [
                "Specified screens and interactions",
                "Loading, empty, error, and disabled states",
                "Frontend integration with the implemented API",
            ],
            "done_when": [
                "The primary user journey works without placeholder actions",
                "Desktop and mobile layouts preserve the main workflow",
            ],
        },
        {
            "id": "P-05",
            "title": "Acceptance and delivery",
            "depends_on": ["P-04"],
            "input_ids": [item["id"] for item in acceptance_tests],
            "deliverables": [
                "Automated critical-path verification",
                "Seed or demo data when required",
                "Runbook and explicit assumptions",
            ],
            "done_when": [
                "Acceptance items are verified or reported with evidence",
                "Build, tests, and startup checks are recorded",
            ],
        },
    ]


def _stable_id(prefix: str, index: int) -> str:
    return f"{prefix}-{index:03d}"


def _normalize_language(value: str | None) -> str:
    normalized = str(value or "").strip().lower()
    return normalized if normalized in _PHASE_LABELS else "en"


def _unique_strings(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result = []
    for value in values:
        normalized = str(value or "").strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
    return result


def _join(values: Iterable[str]) -> str:
    return "; ".join(str(value).strip() for value in values if str(value).strip())
