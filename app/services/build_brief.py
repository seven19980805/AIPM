from __future__ import annotations

import re
import unicodedata
from typing import Any, Iterable

from .data_source_policy import (
    sanitize_data_dependencies,
    writeback_is_authorized,
)
from .structured_requirement_model import (
    _field_for_open_question,
    normalize_structured_requirement_model,
)


BUILD_BRIEF_MAX_CHARS = 6000
_ITEM_MAX_CHARS = 180


def render_build_brief(
    structured_requirement_model: dict[str, Any] | None,
    *,
    title: str = "",
    intake_mode: str = "scratch",
    business_route: str = "",
    language: str = "en",
    deferred_items: Iterable[dict[str, Any]] | None = None,
) -> str:
    model = normalize_structured_requirement_model(structured_requirement_model)
    normalized_language = _normalize_language(language)
    copy = _COPY[normalized_language]
    project_title = (
        model["document_info"]["requirement_name"]
        or model["document_info"]["project_name"]
        or title
        or copy["untitled"]
    )
    route_label = business_route.title() if business_route else copy["unknown"]
    mode_label = copy["modes"].get(intake_mode, intake_mode or copy["unknown"])

    product = model["product_context"]
    background = model["background"]
    scope = model["scope"]
    users = model["users_and_scenarios"]
    functional = model["functional_requirements"]
    interaction = model["page_and_interaction"]
    primary_user_key = product["primary_user"].casefold()
    target_users = [
        user
        for user in users["target_users"]
        if not primary_user_key or user.casefold() != primary_user_key
    ]

    lines = [
        f"# {copy['title']}: {_clip(project_title, 100)}",
        "",
        f"{copy['route']}: **{route_label}** | {copy['intake']}: **{mode_label}**",
        "",
    ]
    _add_section(
        lines,
        copy["outcome"],
        [
            _labeled(copy["objective"], background["objective"]),
            _labeled(copy["decision"], product["decision_or_action"]),
            _labeled(copy["context"], background["summary"]),
        ],
        copy["not_confirmed"],
        maximum=3,
    )
    _add_section(
        lines,
        copy["users"],
        [
            _labeled(copy["primary_user"], product["primary_user"]),
            _labeled(copy["business_owner"], product["business_owner"]),
            _labeled(copy["acceptance_owner"], product["acceptance_owner"]),
            *target_users,
        ],
        copy["not_confirmed"],
        maximum=4,
    )
    _add_section(
        lines,
        copy["scope"],
        [
            *(_prefixed(copy["in_scope"], scope["in_scope"])),
            *(_prefixed(copy["out_scope"], scope["out_of_scope"])),
        ],
        copy["not_confirmed"],
        maximum=4,
    )

    workflow_items: list[str] = []
    workflow_items.extend(_prefixed(copy["scenario"], users["core_scenarios"]))
    workflow_items.extend(_prefixed(copy["flow"], interaction["interaction_flow"]))
    workflow_items.extend(
        _format_feature(feature, copy)
        for feature in functional["feature_details"]
        if isinstance(feature, dict)
    )
    workflow_items.extend(
        _format_page(page, copy)
        for page in interaction["pages"]
        if isinstance(page, dict)
    )
    _add_section(
        lines,
        copy["workflow"],
        workflow_items,
        copy["not_confirmed"],
        maximum=6,
    )

    approved_dependencies = sanitize_data_dependencies(
        model["data_and_dependencies"],
        language=normalized_language,
        writeback_authorization=model["writeback_authorization"],
    )
    rules_and_data = [
        *(_prefixed(copy["rule"], model["business_rules"])),
        *(_prefixed(copy["data"], approved_dependencies)),
        copy["data_policy"],
    ]
    _add_section(
        lines,
        copy["rules_data"],
        rules_and_data,
        copy["not_confirmed"],
        maximum=7,
    )
    _add_section(
        lines,
        copy["acceptance"],
        model["acceptance_criteria"],
        copy["not_confirmed"],
        maximum=4,
    )
    open_items = [
        *(
            _format_deferred_item(item, copy)
            for item in deferred_items or ()
            if isinstance(item, dict)
        ),
        *(_prefixed(copy["open"], _unresolved_open_questions(model))),
        *(_prefixed(copy["risk"], model["risks_and_notes"])),
    ]
    _add_section(
        lines,
        copy["open_items"],
        open_items,
        copy["none"],
        maximum=10,
    )

    markdown = "\n".join(lines).strip()
    if len(markdown) <= BUILD_BRIEF_MAX_CHARS:
        return markdown
    return _truncate_markdown(markdown, BUILD_BRIEF_MAX_CHARS, copy["truncated"])


def _unresolved_open_questions(model: dict[str, Any]) -> list[str]:
    status_by_field = model["collection_status"]
    unresolved: list[str] = []
    for question in model["open_questions"]:
        field = _launch_question_field(question) or _field_for_open_question(question)
        status = status_by_field.get(field, {}).get("status") if field else ""
        if status == "confirmed":
            continue
        unresolved.append(question)
    return unresolved


def _launch_question_field(question: str) -> str:
    normalized = str(question or "").strip().casefold()
    objective_signals = (
        ("single business action", "release improve"),
        ("首版", "业务动作", "改善"),
        ("eine geschaeftsaktion", "release verbessern"),
        ("satu tindakan bisnes", "release pertama"),
    )
    if any(all(signal in normalized for signal in signals) for signals in objective_signals):
        return "objective"
    return ""


def _add_section(
    lines: list[str],
    heading: str,
    items: Iterable[Any],
    empty_text: str,
    *,
    maximum: int,
) -> None:
    lines.extend([f"## {heading}", ""])
    cleaned = _unique(_clip(item) for item in items if str(item or "").strip())
    selected = cleaned[:maximum]
    if not selected:
        selected = [empty_text]
    lines.extend(f"- {item}" for item in selected)
    lines.append("")


def _format_feature(feature: dict[str, Any], copy: dict[str, Any]) -> str:
    name = str(feature.get("feature_name", "")).strip()
    description = str(feature.get("description", "")).strip()
    trigger = str(feature.get("trigger", "")).strip()
    output = ", ".join(_strings(feature.get("outputs")))[:80]
    parts = [part for part in (description, _labeled(copy["trigger"], trigger), _labeled(copy["output"], output)) if part]
    return f"{copy['feature']} {name}: {'; '.join(parts)}".strip(": ")


def _format_page(page: dict[str, Any], copy: dict[str, Any]) -> str:
    name = str(page.get("page_name", "")).strip()
    actions = ", ".join(_strings(page.get("button_actions")))[:90]
    elements = ", ".join(_strings(page.get("page_elements")))[:90]
    details = "; ".join(
        part
        for part in (
            _labeled(copy["elements"], elements),
            _labeled(copy["actions"], actions),
        )
        if part
    )
    return f"{copy['screen']} {name}: {details}".strip(": ")


def _format_deferred_item(item: dict[str, Any], copy: dict[str, Any]) -> str:
    label = str(item.get("label", "")).strip() or copy["unknown"]
    evidence = str(item.get("evidence", "")).strip() or copy["not_provided"]
    return f"{copy['tbd']}: {label} — {evidence}"


def _prefixed(prefix: str, values: Iterable[Any]) -> list[str]:
    return [
        f"{prefix}: {value}"
        for value in _strings(values)
        if str(value).strip()
    ]


def _labeled(label: str, value: Any) -> str:
    text = str(value or "").strip()
    return f"{label}: {text}" if text else ""


def _strings(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if value is None:
        return []
    text = str(value).strip()
    return [text] if text else []


def _clip(value: Any, maximum: int = _ITEM_MAX_CHARS) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= maximum:
        return text
    return f"{text[: maximum - 3].rstrip()}..."


def _unique(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        signature = _semantic_signature(value)
        if not value or not signature or signature in seen:
            continue
        seen.add(signature)
        result.append(value)
    return result


def _semantic_signature(value: str) -> str:
    text = unicodedata.normalize("NFKC", str(value or "")).casefold()
    text = re.sub(r"\b(?:show|shows|display|displays)\b", "", text)
    text = re.sub(r"(?:展示|显示)", "", text)
    return re.sub(r"[^\w\u3400-\u9fff]+", "", text)


def _truncate_markdown(markdown: str, maximum: int, notice: str) -> str:
    suffix = f"\n\n- {notice}"
    kept: list[str] = []
    length = 0
    for line in markdown.splitlines():
        addition = len(line) + (1 if kept else 0)
        if length + addition + len(suffix) > maximum:
            break
        kept.append(line)
        length += addition
    return "\n".join(kept).rstrip() + suffix


def _normalize_language(language: str) -> str:
    normalized = str(language or "").strip().lower().replace("_", "-")
    if normalized.startswith("zh"):
        return "zh"
    return normalized if normalized in _COPY else "en"


_COPY = {
    "en": {
        "title": "Build Brief",
        "untitled": "Untitled requirement",
        "unknown": "Unconfirmed",
        "route": "Business route",
        "intake": "Intake",
        "modes": {"scratch": "Scratch", "draft": "Draft", "template": "Template"},
        "outcome": "Outcome",
        "objective": "Objective",
        "decision": "Primary decision/action",
        "context": "Current context",
        "users": "Users & Ownership",
        "primary_user": "Primary user",
        "business_owner": "Business owner",
        "acceptance_owner": "Acceptance owner",
        "scope": "Scope",
        "in_scope": "In",
        "out_scope": "Out",
        "workflow": "Workflow & Screens",
        "scenario": "Scenario",
        "flow": "Flow",
        "feature": "Feature",
        "screen": "Screen",
        "trigger": "Trigger",
        "output": "Output",
        "elements": "Elements",
        "actions": "Actions",
        "rules_data": "Rules & Data",
        "rule": "Rule",
        "data": "Data",
        "data_policy": "Allowed data paths: SQL Server, SAP, MES, QIS/QMS, or manual Excel/CSV upload.",
        "acceptance": "Acceptance",
        "open_items": "Open Items",
        "open": "Open",
        "tbd": "TBD",
        "not_provided": "Not provided",
        "risk": "Risk",
        "none": "None.",
        "not_confirmed": "Not confirmed.",
        "truncated": "Additional detail remains in the structured requirement model.",
    },
    "zh": {
        "title": "开发简报",
        "untitled": "未命名需求",
        "unknown": "待确认",
        "route": "业务路线",
        "intake": "入口",
        "modes": {"scratch": "空白访谈", "draft": "草稿补全", "template": "模板访谈"},
        "outcome": "业务结果",
        "objective": "目标",
        "decision": "主要判断/动作",
        "context": "当前背景",
        "users": "用户与责任人",
        "primary_user": "主要用户",
        "business_owner": "业务负责人",
        "acceptance_owner": "验收负责人",
        "scope": "首版范围",
        "in_scope": "包含",
        "out_scope": "不包含",
        "workflow": "流程与页面",
        "scenario": "场景",
        "flow": "流程",
        "feature": "功能",
        "screen": "页面",
        "trigger": "触发",
        "output": "输出",
        "elements": "元素",
        "actions": "动作",
        "rules_data": "规则与数据",
        "rule": "规则",
        "data": "数据",
        "data_policy": "允许的数据路径：SQL Server、SAP、MES、QIS/QMS，或用户手动上传 Excel/CSV。",
        "acceptance": "验收标准",
        "open_items": "待确认项",
        "open": "待确认",
        "tbd": "待确认/TBD",
        "not_provided": "未提供",
        "risk": "风险",
        "none": "无。",
        "not_confirmed": "待确认。",
        "truncated": "更多细节保留在结构化需求模型中。",
    },
    "de": {
        "title": "Build Brief",
        "untitled": "Unbenannte Anforderung",
        "unknown": "Unbestaetigt",
        "route": "Business Route",
        "intake": "Intake",
        "modes": {"scratch": "Scratch", "draft": "Draft", "template": "Template"},
        "outcome": "Outcome",
        "objective": "Ziel",
        "decision": "Primaere Aktion",
        "context": "Kontext",
        "users": "Nutzer & Owner",
        "primary_user": "Hauptnutzer",
        "business_owner": "Business Owner",
        "acceptance_owner": "Abnahme-Owner",
        "scope": "Scope",
        "in_scope": "In",
        "out_scope": "Out",
        "workflow": "Workflow & Screens",
        "scenario": "Szenario",
        "flow": "Flow",
        "feature": "Feature",
        "screen": "Screen",
        "trigger": "Trigger",
        "output": "Output",
        "elements": "Elemente",
        "actions": "Aktionen",
        "rules_data": "Regeln & Daten",
        "rule": "Regel",
        "data": "Daten",
        "data_policy": "Erlaubte Datenpfade: SQL Server, SAP, MES, QIS/QMS oder manueller Excel/CSV-Upload.",
        "acceptance": "Abnahme",
        "open_items": "Offene Punkte",
        "open": "Offen",
        "tbd": "TBD",
        "not_provided": "Nicht angegeben",
        "risk": "Risiko",
        "none": "Keine.",
        "not_confirmed": "Nicht bestaetigt.",
        "truncated": "Weitere Details bleiben im strukturierten Anforderungsmodell.",
    },
    "ms": {
        "title": "Build Brief",
        "untitled": "Requirement tanpa nama",
        "unknown": "Belum disahkan",
        "route": "Laluan bisnes",
        "intake": "Intake",
        "modes": {"scratch": "Scratch", "draft": "Draft", "template": "Template"},
        "outcome": "Outcome",
        "objective": "Objektif",
        "decision": "Tindakan utama",
        "context": "Konteks",
        "users": "Pengguna & Owner",
        "primary_user": "Pengguna utama",
        "business_owner": "Business owner",
        "acceptance_owner": "Acceptance owner",
        "scope": "Skop",
        "in_scope": "Dalam",
        "out_scope": "Luar",
        "workflow": "Workflow & Screens",
        "scenario": "Senario",
        "flow": "Flow",
        "feature": "Feature",
        "screen": "Screen",
        "trigger": "Trigger",
        "output": "Output",
        "elements": "Elements",
        "actions": "Actions",
        "rules_data": "Rules & Data",
        "rule": "Rule",
        "data": "Data",
        "data_policy": "Laluan data dibenarkan: SQL Server, SAP, MES, QIS/QMS atau upload manual Excel/CSV.",
        "acceptance": "Acceptance",
        "open_items": "Open Items",
        "open": "Open",
        "tbd": "TBD",
        "not_provided": "Tidak diberikan",
        "risk": "Risk",
        "none": "Tiada.",
        "not_confirmed": "Belum disahkan.",
        "truncated": "Butiran tambahan kekal dalam structured requirement model.",
    },
}
