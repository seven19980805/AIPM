from __future__ import annotations

import re
from typing import Any

from .structured_requirement_model import normalize_structured_requirement_model


PM_METHODOLOGY_VERSION = "2026-06-15"

PM_METHODOLOGY_CHECKS = (
    {
        "key": "opportunity_solution_tree",
        "method": "Opportunity Solution Tree",
        "label": "Outcome, opportunity, solution",
        "source_methods": ["Opportunity Solution Tree", "Outcome Roadmap", "JTBD"],
        "missing": [
            "Measurable business outcome",
            "Target user opportunity or pain point",
            "Candidate solution or feature set",
        ],
        "next_question": (
            "What business outcome should this improve, for which user, and which solution path "
            "is currently being considered?"
        ),
    },
    {
        "key": "success_metric",
        "method": "North Star / KPI design",
        "label": "Success metric",
        "source_methods": ["North Star Metric", "Metrics Dashboard", "OKR"],
        "missing": ["Primary success metric", "Target value or pass/fail threshold"],
        "next_question": "What metric and target will prove this requirement worked?",
    },
    {
        "key": "assumption_risk",
        "method": "Assumption mapping",
        "label": "Assumptions and risks",
        "source_methods": ["Assumption Mapping", "Pre-mortem", "Strategy Red Team"],
        "missing": ["Risky assumptions", "Known risks or open questions"],
        "next_question": "What assumption, risk, or unknown could most easily make this requirement fail?",
    },
    {
        "key": "prioritization",
        "method": "Prioritization framework",
        "label": "Priority and scope trade-offs",
        "source_methods": ["MoSCoW", "Kano", "RICE", "Prioritization Frameworks"],
        "missing": ["P0/P1 or must/should distinction", "Explicit out-of-scope trade-off"],
        "next_question": "Which part is P0 for the first release, and what is explicitly out of scope?",
    },
    {
        "key": "validation_plan",
        "method": "Experiment / validation plan",
        "label": "Validation plan",
        "source_methods": ["Lean Experiment", "A/B Test Analysis", "Test Scenarios"],
        "missing": ["Validation approach", "Acceptance metric or UAT evidence"],
        "next_question": "How will the team validate this with users or data before calling it accepted?",
    },
    {
        "key": "story_acceptance",
        "method": "User stories and acceptance criteria",
        "label": "User story and acceptance",
        "source_methods": ["User Stories", "Job Stories", "Test Scenarios"],
        "missing": ["Actor", "Scenario", "Feature behavior", "Testable acceptance criteria"],
        "next_question": "What user scenario should become the first story and what outcome proves it passes?",
    },
    {
        "key": "roadmap_release",
        "method": "Outcome roadmap / release plan",
        "label": "Release plan",
        "source_methods": ["Outcome Roadmap", "Sprint Plan", "Release Notes"],
        "missing": ["First-release boundary", "Rollout or phase plan"],
        "next_question": "What is the first releasable slice and what can wait for a later phase?",
    },
)

STATUS_POINTS = {
    "ready": 1.0,
    "partial": 0.4,
    "missing": 0.0,
    "conflict": 0.0,
}


def build_pm_methodology_state(
    structured_requirement_model: dict[str, Any] | None,
    language: str | None = None,
) -> dict[str, Any]:
    model = normalize_structured_requirement_model(structured_requirement_model)
    context = _model_context(model)
    checks = [
        _build_check_state(definition, context, language)
        for definition in PM_METHODOLOGY_CHECKS
    ]
    score = round(
        sum(STATUS_POINTS.get(str(check.get("status")), 0.0) for check in checks)
        / max(len(checks), 1)
        * 100
    )
    missing_evidence = [
        str(check["key"])
        for check in checks
        if check.get("status") != "ready"
    ]
    recommended_next_method = missing_evidence[0] if missing_evidence else ""

    return {
        "version": PM_METHODOLOGY_VERSION,
        "score": score,
        "ready_for_pm_review": score >= 85 and not missing_evidence,
        "recommended_next_method": recommended_next_method,
        "missing_evidence": missing_evidence,
        "checks": checks,
        "prompt_guidance": _prompt_guidance(checks),
    }


def _build_check_state(
    definition: dict[str, Any],
    context: dict[str, Any],
    language: str | None,
) -> dict[str, Any]:
    key = str(definition["key"])
    status, evidence = _evaluate_check(key, context)
    missing = [] if status == "ready" else list(definition["missing"])

    return {
        "key": key,
        "method": definition["method"],
        "label": _localized_label(definition, language),
        "source_methods": list(definition["source_methods"]),
        "status": status,
        "ready": status == "ready",
        "evidence": evidence,
        "missing": missing,
        "next_question": _localized_next_question(definition, language),
    }


def _evaluate_check(key: str, context: dict[str, Any]) -> tuple[str, list[str]]:
    if key == "opportunity_solution_tree":
        ready = context["has_objective"] and context["has_user_opportunity"] and context["has_solution"]
        partial = context["has_objective"] or context["has_user_opportunity"] or context["has_solution"]
        return _status(ready, partial, context["has_conflict"]), _evidence(
            context,
            ["objective", "decision_or_action", "users", "scenarios", "features"],
        )

    if key == "success_metric":
        ready = context["has_success_metric"]
        partial = context["has_objective"] or context["has_acceptance"]
        return _status(ready, partial, context["status_conflicts"].get("acceptance", False)), _evidence(
            context,
            ["objective", "acceptance", "business_rules"],
        )

    if key == "assumption_risk":
        ready = context["has_risk_or_assumption"]
        partial = context["has_open_questions"] or context["has_pending_status"]
        return _status(ready, partial, context["has_conflict"]), _evidence(
            context,
            ["risks", "open_questions", "pending_status"],
        )

    if key == "prioritization":
        ready = context["has_priority"] and context["has_scope_boundary"]
        partial = context["has_priority"] or context["has_scope_boundary"] or context["has_features"]
        return _status(ready, partial, context["status_conflicts"].get("scope", False)), _evidence(
            context,
            ["scope", "features", "business_rules"],
        )

    if key == "validation_plan":
        ready = context["has_acceptance"] and (context["has_success_metric"] or context["has_data_dependencies"])
        partial = context["has_acceptance"] or context["has_success_metric"]
        return _status(ready, partial, context["status_conflicts"].get("acceptance", False)), _evidence(
            context,
            ["acceptance", "data_dependencies", "objective"],
        )

    if key == "story_acceptance":
        ready = (
            context["has_users"]
            and context["has_scenarios"]
            and context["has_features"]
            and context["has_acceptance"]
        )
        partial = context["has_users"] or context["has_scenarios"] or context["has_features"] or context["has_acceptance"]
        return _status(ready, partial, context["has_conflict"]), _evidence(
            context,
            ["users", "scenarios", "features", "acceptance"],
        )

    if key == "roadmap_release":
        ready = context["has_release_plan"]
        partial = context["has_scope_boundary"] or context["has_priority"]
        return _status(ready, partial, context["status_conflicts"].get("scope", False)), _evidence(
            context,
            ["scope", "risks", "business_rules"],
        )

    return "missing", []


def _model_context(model: dict[str, Any]) -> dict[str, Any]:
    product_context = _record(model.get("product_context"))
    background = _record(model.get("background"))
    scope = _record(model.get("scope"))
    users_and_scenarios = _record(model.get("users_and_scenarios"))
    functional_requirements = _record(model.get("functional_requirements"))
    collection_status = _record(model.get("collection_status"))

    in_scope = _string_list(scope.get("in_scope"))
    out_of_scope = _string_list(scope.get("out_of_scope"))
    users = _string_list(users_and_scenarios.get("target_users"))
    scenarios = _string_list(users_and_scenarios.get("core_scenarios"))
    features = _feature_texts(functional_requirements)
    business_rules = _string_list(model.get("business_rules"))
    data_dependencies = _string_list(model.get("data_and_dependencies"))
    risks = _string_list(model.get("risks_and_notes"))
    acceptance = _string_list(model.get("acceptance_criteria"))
    open_questions = _string_list(model.get("open_questions"))
    objective = str(background.get("objective") or "").strip()
    summary = str(background.get("summary") or "").strip()
    decision_or_action = str(product_context.get("decision_or_action") or "").strip()

    all_statuses = {
        key: str(_record(item).get("status") or "missing").strip().lower()
        for key, item in collection_status.items()
    }
    status_conflicts = {
        key: status == "conflict"
        for key, status in all_statuses.items()
    }
    has_pending_status = any(
        status in {"captured", "pending_confirmation"}
        for status in all_statuses.values()
    )
    has_conflict = any(status_conflicts.values())

    metric_texts = [objective, summary, *business_rules, *acceptance]
    priority_texts = [*in_scope, *out_of_scope, *business_rules, *features]
    release_texts = [*out_of_scope, *business_rules, *risks, summary]

    return {
        "objective": objective or summary,
        "decision_or_action": decision_or_action,
        "users": users,
        "scenarios": scenarios,
        "features": features,
        "scope": [*in_scope, *out_of_scope],
        "business_rules": business_rules,
        "data_dependencies": data_dependencies,
        "risks": risks,
        "acceptance": acceptance,
        "open_questions": open_questions,
        "pending_status": _pending_status_evidence(collection_status),
        "status_conflicts": status_conflicts,
        "has_conflict": has_conflict,
        "has_pending_status": has_pending_status,
        "has_objective": bool(objective or summary),
        "has_user_opportunity": bool(users or scenarios or decision_or_action),
        "has_solution": bool(features or functional_requirements.get("overview")),
        "has_users": bool(users),
        "has_scenarios": bool(scenarios),
        "has_features": bool(features or functional_requirements.get("overview")),
        "has_scope_boundary": bool(in_scope and out_of_scope),
        "has_acceptance": bool(acceptance),
        "has_data_dependencies": bool(data_dependencies),
        "has_open_questions": bool(open_questions),
        "has_risk_or_assumption": bool(risks or open_questions),
        "has_success_metric": _contains_metric_signal(metric_texts),
        "has_priority": _contains_priority_signal(priority_texts),
        "has_release_plan": _contains_release_signal(release_texts),
    }


def _status(ready: bool, partial: bool, conflict: bool) -> str:
    if conflict:
        return "conflict"
    if ready:
        return "ready"
    if partial:
        return "partial"
    return "missing"


def _evidence(context: dict[str, Any], fields: list[str], limit: int = 3) -> list[str]:
    evidence: list[str] = []
    for field in fields:
        value = context.get(field)
        if isinstance(value, list):
            evidence.extend(_clip(item) for item in value if str(item).strip())
        elif isinstance(value, str) and value.strip():
            evidence.append(_clip(value))
        if len(evidence) >= limit:
            break
    return evidence[:limit]


def _prompt_guidance(checks: list[dict[str, Any]]) -> list[str]:
    guidance: list[str] = []
    for check in checks:
        if check.get("status") == "ready":
            continue
        question = str(check.get("next_question") or "").strip()
        if question:
            guidance.append(
                f"{check.get('method')}: ask next only if this is the highest-value gap. {question}"
            )
    return guidance[:3]


def _localized_label(definition: dict[str, Any], language: str | None) -> str:
    labels = {
        "zh": {
            "opportunity_solution_tree": "业务结果 / 机会 / 方案",
            "success_metric": "成功指标",
            "assumption_risk": "假设与风险",
            "prioritization": "优先级与范围取舍",
            "validation_plan": "验证计划",
            "story_acceptance": "用户故事与验收",
            "roadmap_release": "发布边界",
        }
    }
    normalized = str(language or "").strip().lower()
    if normalized.startswith("zh"):
        return labels["zh"].get(str(definition["key"]), str(definition["label"]))
    return str(definition["label"])


def _localized_next_question(definition: dict[str, Any], language: str | None) -> str:
    questions = {
        "zh": {
            "opportunity_solution_tree": "这个需求要改善哪个业务结果、服务哪个用户机会，目前考虑的方案路径是什么？",
            "success_metric": "用哪个指标和目标值证明这个需求做成了？",
            "assumption_risk": "哪个假设、风险或未知点最可能让这个需求失败？",
            "prioritization": "第一版必须做的 P0 是什么，哪些明确不在本次范围？",
            "validation_plan": "团队会如何通过用户或数据验证它，再判断可以验收？",
            "story_acceptance": "第一个用户故事应该覆盖哪个场景，什么结果证明它通过？",
            "roadmap_release": "第一版可发布的最小边界是什么，哪些可以放到后续阶段？",
        }
    }
    normalized = str(language or "").strip().lower()
    if normalized.startswith("zh"):
        return questions["zh"].get(str(definition["key"]), str(definition["next_question"]))
    return str(definition["next_question"])


def _contains_metric_signal(values: list[str]) -> bool:
    text = "\n".join(values).lower()
    if re.search(r"\d+\s*(%|percent|pct|minutes?|mins?|hours?|days?|x\b)", text):
        return True
    metric_keywords = (
        "metric",
        "kpi",
        "okr",
        "north star",
        "target",
        "threshold",
        "success criteria",
        "pass/fail",
        "目标值",
        "指标",
        "成功",
        "验收阈值",
        "通过标准",
    )
    return any(keyword in text for keyword in metric_keywords)


def _contains_priority_signal(values: list[str]) -> bool:
    text = "\n".join(values).lower()
    priority_keywords = (
        "p0",
        "p1",
        "must",
        "should",
        "could",
        "won't",
        "wont",
        "moscow",
        "kano",
        "rice",
        "high priority",
        "medium priority",
        "low priority",
        "first release",
        "first version",
        "version one",
        "version-one",
        "v1",
        "优先级",
        "必须",
        "应该",
        "高优",
        "中优",
        "低优",
        "第一版",
    )
    return any(keyword in text for keyword in priority_keywords)


def _contains_release_signal(values: list[str]) -> bool:
    text = "\n".join(values).lower()
    release_keywords = (
        "mvp",
        "release",
        "phase",
        "rollout",
        "first version",
        "first release",
        "later phase",
        "v1",
        "version 1",
        "路线图",
        "发布",
        "阶段",
        "第一版",
        "后续",
    )
    return any(keyword in text for keyword in release_keywords)


def _feature_texts(functional_requirements: dict[str, Any]) -> list[str]:
    texts: list[str] = []
    overview = str(functional_requirements.get("overview") or "").strip()
    if overview:
        texts.append(overview)
    raw_features = functional_requirements.get("feature_details")
    if not isinstance(raw_features, list):
        return texts
    for item in raw_features:
        record = _record(item)
        pieces = [
            str(record.get("feature_name") or "").strip(),
            str(record.get("description") or "").strip(),
            str(record.get("trigger") or "").strip(),
            str(record.get("processing_logic") or "").strip(),
        ]
        text = " ".join(piece for piece in pieces if piece)
        if text:
            texts.append(text)
    return texts


def _pending_status_evidence(collection_status: dict[str, Any]) -> list[str]:
    evidence: list[str] = []
    for key, item in collection_status.items():
        record = _record(item)
        status = str(record.get("status") or "").strip()
        reason = str(record.get("reason") or "").strip()
        if status in {"captured", "pending_confirmation", "conflict"}:
            evidence.append(f"{key}: {status}{f' - {reason}' if reason else ''}")
    return evidence


def _record(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _clip(value: str, limit: int = 140) -> str:
    normalized = " ".join(str(value).split())
    if len(normalized) <= limit:
        return normalized
    return f"{normalized[:limit].rstrip()}..."
