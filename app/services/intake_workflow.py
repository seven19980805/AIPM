from __future__ import annotations

import re
from typing import Any


INTAKE_MODE_SCRATCH = "scratch"
INTAKE_MODE_DRAFT = "draft"
INTAKE_MODE_TEMPLATE = "template"
INTAKE_MODES = {
    INTAKE_MODE_SCRATCH,
    INTAKE_MODE_DRAFT,
    INTAKE_MODE_TEMPLATE,
}

BUSINESS_ROUTE_PRODUCTION = "production"
BUSINESS_ROUTE_QUALITY = "quality"
BUSINESS_ROUTE_TDI = "tdi"
BUSINESS_ROUTES = {
    BUSINESS_ROUTE_PRODUCTION,
    BUSINESS_ROUTE_QUALITY,
    BUSINESS_ROUTE_TDI,
}

QUESTION_BUDGET_TARGET = 5
QUESTION_BUDGET_MAXIMUM = 7
INTERVIEW_RESPONSE_MAX_CHARS = 1200

_ROUTE_ALIASES = {
    "production": BUSINESS_ROUTE_PRODUCTION,
    "prod": BUSINESS_ROUTE_PRODUCTION,
    "quality": BUSINESS_ROUTE_QUALITY,
    "qdm": BUSINESS_ROUTE_QUALITY,
    "tdi": BUSINESS_ROUTE_TDI,
}


def normalize_business_route(value: Any, *, required: bool = False) -> str:
    normalized = str(value or "").strip().lower()
    route = _ROUTE_ALIASES.get(normalized, "")
    if route:
        return route
    if required or normalized:
        raise ValueError("business_route must be production, quality, or tdi.")
    return ""


def resolve_intake_mode(
    *,
    requested_mode: Any = "",
    template_id: Any = "",
    start_function: Any = "",
) -> str:
    requested = str(requested_mode or "").strip().lower()
    if requested and requested not in INTAKE_MODES:
        raise ValueError("intake_mode must be scratch, draft, or template.")

    has_template = bool(str(template_id or "").strip())
    draft_start = str(start_function or "").strip().lower() == "improve_draft"
    derived = (
        INTAKE_MODE_TEMPLATE
        if has_template
        else INTAKE_MODE_DRAFT
        if draft_start
        else INTAKE_MODE_SCRATCH
    )
    if not requested:
        return derived
    if requested == INTAKE_MODE_TEMPLATE and not has_template:
        raise ValueError("template intake requires template_id.")
    if requested != INTAKE_MODE_TEMPLATE and has_template:
        raise ValueError("template_id can only be used with template intake.")
    if requested == INTAKE_MODE_DRAFT and not draft_start:
        return INTAKE_MODE_DRAFT
    if requested == INTAKE_MODE_SCRATCH and draft_start:
        raise ValueError("scratch intake cannot use improve_draft.")
    return requested


def business_route_from_model(model: dict[str, Any] | None) -> str:
    payload = model if isinstance(model, dict) else {}
    product_context = payload.get("product_context")
    if not isinstance(product_context, dict):
        return ""
    department = str(product_context.get("requesting_department", "")).strip().lower()
    for alias, route in _ROUTE_ALIASES.items():
        if alias in department:
            return route
    return ""


def business_route_from_template(template: dict[str, Any] | None) -> str:
    payload = template if isinstance(template, dict) else {}
    explicit = str(payload.get("business_route", "")).strip().lower()
    if explicit in BUSINESS_ROUTES:
        return explicit

    values: list[Any] = [
        payload.get("template_id"),
        payload.get("template_key"),
        payload.get("template_name"),
        payload.get("template_category"),
        payload.get("business_domain"),
        payload.get("description"),
    ]
    for key in ("tags", "applicable_scenarios"):
        items = payload.get(key)
        if isinstance(items, list):
            values.extend(items)
    text = " ".join(str(value or "").strip().lower() for value in values)

    if any(
        token in text
        for token in (
            "quality",
            "qdm",
            "inspection",
            "defect",
            "yield",
            "cpk",
            "spc",
            "iqc",
        )
    ):
        return BUSINESS_ROUTE_QUALITY
    if re.search(r"\btdi\b", text):
        return BUSINESS_ROUTE_TDI
    if any(
        token in text
        for token in (
            "production",
            "planning",
            "scheduling",
            "wip",
            "lot flow",
            "shop floor",
        )
    ):
        return BUSINESS_ROUTE_PRODUCTION
    return ""


def question_budget(user_turn_count: int) -> dict[str, int]:
    asked = max(0, int(user_turn_count or 0))
    return {
        "target": QUESTION_BUDGET_TARGET,
        "maximum": QUESTION_BUDGET_MAXIMUM,
        "asked": asked,
        "remaining": max(0, QUESTION_BUDGET_MAXIMUM - asked),
    }


def enforce_interview_response_contract(value: str) -> str:
    lines = _limit_summary_bullets(
        _limit_choice_lines(str(value or "").strip().splitlines())
    )
    guarded_lines: list[str] = []
    question_seen = False

    for line in lines:
        question_positions = [
            index for index, character in enumerate(line) if character in {"?", "？"}
        ]
        if not question_positions:
            guarded_lines.append(line.rstrip())
            continue
        if question_seen:
            continue

        first_question = question_positions[0]
        tail = (
            line[first_question + 1 :]
            .replace("?", ".")
            .replace("？", "。")
        )
        guarded_lines.append(f"{line[: first_question + 1]}{tail}".rstrip())
        question_seen = True

    if not question_seen:
        for index, line in enumerate(guarded_lines):
            if not _looks_like_unpunctuated_question(line):
                continue
            guarded_lines[index] = f"{line.rstrip(':：.;。 ')}?"
            break

    guarded = "\n".join(guarded_lines).strip()
    if len(guarded) <= INTERVIEW_RESPONSE_MAX_CHARS:
        return guarded

    clipped = guarded[:INTERVIEW_RESPONSE_MAX_CHARS].rstrip()
    boundary = max(clipped.rfind("\n"), clipped.rfind(" "))
    return clipped[:boundary].rstrip() if boundary > 0 else clipped


def _limit_choice_lines(lines: list[str], maximum: int = 3) -> list[str]:
    result: list[str] = []
    choice_count = 0
    for line in lines:
        if _CHOICE_LINE_PATTERN.match(line):
            choice_count += 1
            if choice_count > maximum:
                continue
        result.append(line)
    return result


def _limit_summary_bullets(lines: list[str], maximum: int = 3) -> list[str]:
    result: list[str] = []
    bullet_count = 0
    for line in lines:
        if _CHOICE_LINE_PATTERN.match(line):
            result.append(line)
            continue
        if _SUMMARY_BULLET_PATTERN.match(line):
            bullet_count += 1
            if bullet_count > maximum:
                continue
        result.append(line)
    return result


def _looks_like_unpunctuated_question(value: str) -> bool:
    text = str(value or "").strip().strip("*_#- ").lower()
    interrogative_prefixes = (
        "what ",
        "which ",
        "who ",
        "when ",
        "where ",
        "why ",
        "how ",
        "should ",
        "would ",
        "could ",
        "can ",
        "do ",
        "does ",
        "did ",
        "is ",
        "are ",
        "will ",
        "please choose ",
        "首版",
        "请选择",
        "哪个",
        "什么",
        "是否",
        "welche ",
        "welcher ",
        "was ",
        "soll ",
        "apakah ",
        "perlu ",
    )
    if text.startswith(interrogative_prefixes):
        return True
    return any(
        marker in text
        for marker in (
            ", should ",
            ", would ",
            ", could ",
            ", can ",
            ", does ",
            ", is ",
            ", are ",
            ", will ",
            "，首版",
            "，是否",
        )
    )


_CHOICE_LINE_PATTERN = re.compile(
    r"^\s*(?:[-*]\s*)?(?:\*\*)?[A-Z][.)](?:\*\*)?\s+",
    re.IGNORECASE,
)
_SUMMARY_BULLET_PATTERN = re.compile(r"^\s*[-*]\s+\S")


def build_intake_prompt_contract(
    *,
    mode: str,
    business_route: str,
    user_turn_count: int,
    language: str,
) -> str:
    normalized_mode = str(mode or "").strip().lower()
    if normalized_mode not in INTAKE_MODES:
        raise ValueError("mode must be scratch, draft, or template.")
    route = normalize_business_route(business_route)
    budget = question_budget(user_turn_count)
    route_label = route.title() if route else "selected"

    if str(language or "").lower().startswith("zh"):
        mode_rule = {
            INTAKE_MODE_SCRATCH: (
                "空白访谈：从业务动作开始，不预设方案；按结果、用户/流程、规则/数据、验收顺序补齐。"
            ),
            INTAKE_MODE_DRAFT: (
                "草稿补全：先提取并复用草稿中的事实，只追问缺口、冲突和未确认假设；不得重复询问已有答案。"
            ),
            INTAKE_MODE_TEMPLATE: (
                "模板访谈：模板只是基线假设；优先确认适用场景、与基线的差异以及仍未知的关键项。"
            ),
        }[normalized_mode]
        return (
            "AI PM 生产访谈合同：\n"
            f"- 入口：{normalized_mode}；路线：{route_label}。\n"
            f"- {mode_rule}\n"
            "- 每轮只处理 InterviewStateV2 指定的一个交付决策；界面单独展示唯一下一问题。\n"
            "- 不为追求 100% 表格覆盖而追问低价值细节；页面结构可由已确认场景和功能推导。\n"
            "- 阻断项优先级：业务结果与主要用户 > 首版范围与主流程 > 业务规则与数据边界 > 可观察验收。\n"
            f"- 目标在 {budget['target']} 个问题内收敛，最多 {budget['maximum']} 个；"
            f"当前已问 {budget['asked']} 个。达到上限后停止扩展范围，把非阻断未知项写入 Open Items。\n"
            "- 公司数据路径只能是 SQL Server、SAP，或用户手动上传 Excel/CSV；不要虚构其他系统、表或接口。\n"
            "- 助手消息只总结本轮新确认事实，最多 2 条；不包含问题、选项、阶段或百分比。"
        )

    mode_rule = {
        INTAKE_MODE_SCRATCH: (
            "Scratch: begin with the business action and discover outcome, workflow, rules/data, and acceptance without assuming a solution."
        ),
        INTAKE_MODE_DRAFT: (
            "Draft: reuse extracted facts and ask only about gaps, conflicts, or unconfirmed assumptions; never re-ask an answered point."
        ),
        INTAKE_MODE_TEMPLATE: (
            "Template: treat the template as a baseline hypothesis and confirm applicability, deltas, and the remaining critical unknowns."
        ),
    }[normalized_mode]
    return (
        "Production AI PM interview contract:\n"
        f"- Intake: {normalized_mode}; route: {route_label}.\n"
        f"- {mode_rule}\n"
        "- Handle only the single delivery decision selected by InterviewStateV2; the UI renders the one active question separately.\n"
        "- Do not chase 100% form coverage. Screens may be derived from confirmed scenarios and features.\n"
        "- Blocker priority: outcome/user > first-release scope/workflow > rules/data boundary > observable acceptance.\n"
        f"- Target convergence within {budget['target']} questions, hard maximum {budget['maximum']}; "
        f"{budget['asked']} user turns have been used. At the limit, stop expanding scope and put non-blocking unknowns in Open Items.\n"
        "- Company data paths are SQL Server, SAP, or user-uploaded Excel/CSV only. Never invent other systems, tables, or endpoints.\n"
        "- Assistant messages summarize at most two newly confirmed facts and contain no question, choices, stage, score, or percentage."
    )
