"""Document QA: a single structured source of truth for generated-document review.

Historically the QA findings were rendered straight to a Markdown appendix and the
frontend re-parsed that Markdown with regexes to render the QA card. That round-trip
was fragile: any wording drift in the appendix silently broke the parser.

This module computes the QA findings ONCE as a structured dict
(:func:`build_document_qa_state`) and renders the human-readable Markdown appendix
FROM that same dict (:func:`render_document_qa_appendix`). The structured dict is also
returned by the API alongside ``pm_methodology_state`` so the frontend can consume it
directly instead of reparsing the document.

The functions here are pure (no service/session state) so they are independently
testable. The few generic list helpers are duplicated locally to keep the module
self-contained rather than coupling it to the large requirement collector class.
"""

from __future__ import annotations

from typing import Any

# --- generic helpers (local, pure copies to keep this module self-contained) -------

_LABEL_KEYS = (
    "name",
    "title",
    "label",
    "role",
    "actor",
    "feature",
    "page",
    "metric",
    "field",
    "source",
    "rule",
    "description",
    "flow",
    "acceptance",
    "content",
)


def _flatten_strings(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        cleaned = value.strip()
        return [cleaned] if cleaned else []
    if isinstance(value, (int, float, bool)):
        return [str(value)]
    if isinstance(value, list):
        values: list[str] = []
        for item in value:
            values.extend(_flatten_strings(item))
        return _unique_strings(values)
    if isinstance(value, dict):
        parts = [str(value.get(key, "")).strip() for key in _LABEL_KEYS if str(value.get(key, "")).strip()]
        if parts:
            return [" - ".join(parts)]
        values = []
        for item in value.values():
            values.extend(_flatten_strings(item))
        return _unique_strings(values)
    return []


def _string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return _unique_strings(_flatten_strings(value))
    if isinstance(value, str):
        cleaned = value.strip()
        return [cleaned] if cleaned else []
    if value is None:
        return []
    return _flatten_strings(value)


def _unique_strings(values: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        normalized = " ".join(str(value).split())
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        unique.append(normalized)
    return unique


def _markdown_bullets(values: list[str]) -> list[str]:
    cleaned = _unique_strings([str(value).strip() for value in values if str(value).strip()])
    if not cleaned:
        return ["- None"]
    return [f"- {value}" for value in cleaned]


# --- classification + findings (pure) ----------------------------------------------

_PRODUCTION_KEYWORDS = (
    "mes",
    "api",
    "database",
    "db view",
    "data access",
    "integration",
    "source system",
    "shift definition",
    "duration",
    "start time",
    "end time",
    "calendar",
    "refresh",
    "frequency",
    "cadence",
    "real-time",
    "poll",
    "authentication",
    "auth",
    "sso",
    "vpn",
    "access",
    "security",
    "tolerance",
    "sla",
    "数据源",
    "接口",
    "数据库",
    "班次",
    "刷新",
    "认证",
    "权限",
)
_DEMO_KEYWORDS = (
    "visual",
    "branding",
    "color",
    "layout",
    "sorting",
    "filter",
    "copy",
    "entry point",
    "menu",
    "颜色",
    "布局",
    "排序",
    "筛选",
    "入口",
)
_IMPLEMENTATION_KEYWORDS = (
    "technology",
    "stack",
    "c#",
    "sqlite",
    "mock",
    "demo",
    "hosting",
    "deployment",
    "技术栈",
    "部署",
    "演示",
)


def classify_open_question(question: str) -> str:
    lowered = question.lower()
    if any(keyword in lowered for keyword in _PRODUCTION_KEYWORDS):
        return "blocking_for_production"
    if any(keyword in lowered for keyword in _IMPLEMENTATION_KEYWORDS):
        return "implementation_assumptions"
    if any(keyword in lowered for keyword in _DEMO_KEYWORDS):
        return "ok_for_demo"
    return "needs_review"


def business_rule_findings(model: dict[str, Any]) -> list[str]:
    evidence = " ".join(
        [
            *_string_list(model.get("business_rules")),
            *_string_list(model.get("risks_and_notes")),
            *_flatten_strings(model.get("functional_requirements")),
            *_flatten_strings(model.get("acceptance_criteria")),
        ]
    ).lower()
    findings: list[str] = []
    simple_plan_actual_rule = (
        "actual < plan" in evidence
        or "actual pieces < planned" in evidence
        or "actual below plan" in evidence
        or "actual output is below plan" in evidence
    )
    time_phased_terms = (
        "elapsed",
        "time-phased",
        "current-time",
        "current time",
        "pace",
        "expected output",
        "proportional",
        "by current time",
        "累计计划",
        "当前时间",
        "节拍",
    )
    if simple_plan_actual_rule and not any(term in evidence for term in time_phased_terms):
        findings.append(
            "Behind-schedule rule may be wrong for mid-shift use: comparing current actual against full-shift plan can mark most lines behind until shift end. Prefer time-phased expected output or MES current-time target."
        )
    return findings


def implementation_findings(doc_markdown: str, is_design: bool) -> list[str]:
    lowered = doc_markdown.lower()
    findings: list[str] = []
    if is_design and (
        "default technology stack" in lowered
        or "personal project/demo policy" in lowered
        or "c#" in lowered
        or "sqlite" in lowered
        or "vanilla js" in lowered
    ):
        findings.append(
            "Technology stack appears to be a system default or demo assumption; verify it before IT delivery."
        )
    if "mock" in lowered or "demo data" in lowered or "fallback demo" in lowered:
        findings.append(
            "Mock/demo data is acceptable for prototype validation only; production requires a confirmed source integration."
        )
    if "real-time" in lowered and (
        "manual refresh" in lowered
        or "refresh frequency | tbd" in lowered
        or ("refresh frequency" in lowered and "tbd" in lowered)
    ):
        findings.append(
            "Real-time wording conflicts with manual/TBD refresh behavior; confirm the refresh cadence."
        )
    return _unique_strings(findings)


# --- structured state (single source of truth) -------------------------------------


def build_document_qa_state(
    doc_markdown: str,
    model: dict[str, Any],
    progress: dict[str, Any],
    is_design: bool,
    source_kind: str,
) -> dict[str, Any]:
    """Compute the structured Document QA state from a generated document + model.

    ``model`` is expected to already be normalized. ``progress`` is the structured
    requirement progress dict. The returned dict is API-serializable and also carries
    the lists/percentages the Markdown renderer needs.
    """

    open_questions = _string_list(model.get("open_questions"))
    classified_questions: dict[str, list[str]] = {
        "blocking_for_production": [],
        "ok_for_demo": [],
        "implementation_assumptions": [],
        "needs_review": [],
    }
    for question in open_questions:
        classified_questions[classify_open_question(question)].append(question)

    rule_findings = business_rule_findings(model)
    impl_findings = implementation_findings(doc_markdown, is_design)
    production_blockers = [
        *classified_questions["blocking_for_production"],
        *rule_findings,
    ]
    if any("real-time" in finding.lower() for finding in impl_findings):
        production_blockers.append(
            "Real-time positioning conflicts with manual/TBD refresh behavior unless the business accepts that trade-off."
        )
    if is_design and any("mock" in finding.lower() for finding in impl_findings):
        production_blockers.append(
            "Real MES integration is not yet specified; mock/demo data is only enough for prototype delivery."
        )

    if production_blockers:
        production_readiness = "Blocked"
    elif classified_questions["needs_review"] or impl_findings:
        production_readiness = "Needs review"
    else:
        production_readiness = "Ready"
    demo_readiness = "Ready with assumptions" if impl_findings or open_questions else "Ready"

    return {
        "source_kind": source_kind,
        "document_type": "Design" if is_design else "PRD",
        "demo_readiness": demo_readiness,
        "production_readiness": production_readiness,
        "open_question_count": len(open_questions),
        "production_blockers": _unique_strings(production_blockers),
        "business_rule_findings": rule_findings,
        "implementation_findings": impl_findings,
        "classification_counts": {
            "blocking_for_production": len(classified_questions["blocking_for_production"]),
            "ok_for_demo": len(classified_questions["ok_for_demo"]),
            "implementation_assumptions": len(classified_questions["implementation_assumptions"]),
            "needs_review": len(classified_questions["needs_review"]),
        },
        # Extra fields used by the Markdown renderer (frontend ignores them).
        "classified_questions": classified_questions,
        "readiness_percentage": int(progress.get("readiness_percentage", 0) or 0),
        "collection_coverage_percentage": int(progress.get("collection_coverage_percentage", 0) or 0),
        "confirmation_percentage": int(progress.get("confirmation_percentage", 0) or 0),
    }


_API_STATE_KEYS = (
    "source_kind",
    "document_type",
    "demo_readiness",
    "production_readiness",
    "open_question_count",
    "production_blockers",
    "business_rule_findings",
    "implementation_findings",
    "classification_counts",
)


def to_api_state(state: dict[str, Any] | None) -> dict[str, Any] | None:
    """Project the full QA state down to the API-serializable subset.

    :func:`build_document_qa_state` also carries renderer-only fields
    (``classified_questions`` and the readiness percentages) that the frontend
    never reads. Strip them so the API payload is exactly the set of fields the
    client consumes.
    """
    if not state:
        return None
    return {key: state[key] for key in _API_STATE_KEYS if key in state}


# --- Markdown appendix (rendered FROM the structured state) -------------------------


def render_document_qa_appendix(state: dict[str, Any], language: str) -> str:
    classified = state.get("classified_questions", {}) or {}
    if language == "zh":
        return _render_appendix_zh(state, classified)
    return _render_appendix_en(state, classified)


def _render_appendix_en(state: dict[str, Any], classified: dict[str, list[str]]) -> str:
    doc_label = state.get("document_type", "PRD")
    return "\n".join(
        [
            "## Document QA",
            "",
            f"- **Document type**: {doc_label}",
            f"- **Structured readiness**: {state.get('readiness_percentage', 0)}% final readiness; "
            f"{state.get('collection_coverage_percentage', 0)}% collection coverage; "
            f"{state.get('confirmation_percentage', 0)}% confirmation.",
            f"- **System-counted open questions**: {state.get('open_question_count', 0)}",
            f"- **Demo readiness**: {state.get('demo_readiness', 'Ready')}",
            f"- **Production readiness**: {state.get('production_readiness', 'Ready')}",
            "",
            "### Production Blockers",
            *_markdown_bullets(state.get("production_blockers", [])),
            "",
            "### Open Question Classification",
            f"- **Blocking for production**: {len(classified.get('blocking_for_production', []))}",
            *_markdown_bullets(classified.get("blocking_for_production", [])),
            f"- **OK for demo / polish later**: {len(classified.get('ok_for_demo', []))}",
            *_markdown_bullets(classified.get("ok_for_demo", [])),
            f"- **Implementation assumptions**: {len(classified.get('implementation_assumptions', []))}",
            *_markdown_bullets(classified.get("implementation_assumptions", [])),
            f"- **Needs review**: {len(classified.get('needs_review', []))}",
            *_markdown_bullets(classified.get("needs_review", [])),
            "",
            "### Business Rule Sanity Checks",
            *_markdown_bullets(state.get("business_rule_findings", [])),
            "",
            "### Implementation Assumption Checks",
            *_markdown_bullets(state.get("implementation_findings", [])),
        ]
    )


def _render_appendix_zh(state: dict[str, Any], classified: dict[str, list[str]]) -> str:
    doc_label = "设计文档" if state.get("document_type") == "Design" else "需求文档"
    return "\n".join(
        [
            "## 文档质量检查 / Document QA",
            "",
            f"- **文档类型**：{doc_label}",
            f"- **结构化就绪度**：最终就绪度 {state.get('readiness_percentage', 0)}%；"
            f"收集覆盖率 {state.get('collection_coverage_percentage', 0)}%；"
            f"确认完成度 {state.get('confirmation_percentage', 0)}%。",
            f"- **系统计数的 open questions**：{state.get('open_question_count', 0)}",
            f"- **Demo readiness**：{state.get('demo_readiness', 'Ready')}",
            f"- **Production readiness**：{state.get('production_readiness', 'Ready')}",
            "",
            "### 生产版阻塞项",
            *_markdown_bullets(state.get("production_blockers", [])),
            "",
            "### Open Question 分类",
            f"- **生产版阻塞**：{len(classified.get('blocking_for_production', []))}",
            *_markdown_bullets(classified.get("blocking_for_production", [])),
            f"- **Demo 可接受 / 后续润色**：{len(classified.get('ok_for_demo', []))}",
            *_markdown_bullets(classified.get("ok_for_demo", [])),
            f"- **实现假设**：{len(classified.get('implementation_assumptions', []))}",
            *_markdown_bullets(classified.get("implementation_assumptions", [])),
            f"- **仍需人工复核**：{len(classified.get('needs_review', []))}",
            *_markdown_bullets(classified.get("needs_review", [])),
            "",
            "### 业务规则 sanity check",
            *_markdown_bullets(state.get("business_rule_findings", [])),
            "",
            "### 实现假设检查",
            *_markdown_bullets(state.get("implementation_findings", [])),
        ]
    )
