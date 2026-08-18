from __future__ import annotations

import re
from typing import Any

from .data_source_policy import normalize_writeback_authorization


STRUCTURED_REQUIREMENT_MODEL_SYSTEM_PROMPT = """You extract a compact, evidence-backed Build Brief model from an AI PM conversation.

Evidence and status contract:
1) Output strict JSON only. Do not add markdown, commentary, or keys outside the schema.
2) A direct, unambiguous declarative statement from the user is explicit confirmation. Do not require a later yes/confirm turn. Confirm only the fact actually stated.
3) An A/B/C reply confirms only the exact option text immediately offered by the assistant. Never add detail that was absent from that option.
4) If an accepted option is explicitly labeled as an assumption, preserve it with the prefix "ASSUMPTION:". It is confirmed only to the exact extent stated.
5) Template baselines, AI suggestions, and attachment inferences remain unconfirmed until the user explicitly adopts them. Uploaded drafts, assistant summaries, and generated documents follow the same rule.
6) Evidence priority is: latest explicit user statement, exact accepted option, then unconfirmed draft/template candidate. A later user correction wins; incompatible evidence is a conflict.
7) Never invent scope, users, owners, formulas, thresholds, fields, tables, endpoints, states, approvals, permissions, SLAs, writeback, pages, or acceptance criteria.
8) Use empty strings/arrays for unknown content. Put only delivery-relevant unresolved decisions in open_questions.
9) Business owner and acceptance owner are separate. Existing names are captured only. Confirm ownership after both are independently confirmed.

Status values:
- confirmed: the user explicitly settled this specific implementation-relevant fact.
- captured: reliable context exists but is not yet a settled delivery decision.
- pending_confirmation: a candidate, ambiguity, or concrete decision still needs user confirmation.
- conflict: user evidence is inconsistent.
- missing: there is no reliable evidence.
- Keep these English enum tokens unchanged. Each non-confirmed item may contain at most one focused pending question.
- A missing adjacent detail must not downgrade a separate fact that the user already confirmed.

Production boundaries:
- Approved data paths are SQL Server, SAP, MES, QIS/QMS, or manual Excel/CSV upload. Other databases stay pending until the user names an approved system.
- Never fabricate source objects, fields, joins, tables, APIs, or writeback. Keep an unspecified physical path pending.
- A KPI is implementation-ready only when its formula, time window, and material exclusions are explicit or exactly accepted. For Cpk, capture either the approved source value or the approved formula and specification limits.
- Pages are advisory. Include concrete touchpoints only when supported by evidence; do not ask for decorative layout detail.

Compact output limits:
- scope.in_scope: at most 5; scope.out_of_scope: at most 4.
- target_users: at most 3; core_scenarios: at most 4.
- feature_details: at most 6. Merge overlap and keep the smallest coherent first release.
- pages: at most 5; business_rules: at most 8.
- data_and_dependencies: at most 6; acceptance_criteria: at most 6.
- open_questions: at most 6. Do not generate code or implementation prose.
- writeback_authorization: leave empty unless the user explicitly authorized writing into a source system; never mark it authorized yourself.

Output JSON schema:
{
  "document_info": {
    "project_name": "string",
    "requirement_name": "string"
  },
  "product_context": {
    "requesting_department": "string",
    "business_owner": "string",
    "software_type": "string",
    "primary_user": "string",
    "decision_or_action": "string",
    "acceptance_owner": "string"
  },
  "background": {
    "summary": "string",
    "objective": "string"
  },
  "scope": {
    "in_scope": ["string"],
    "out_of_scope": ["string"]
  },
  "users_and_scenarios": {
    "target_users": ["string"],
    "core_scenarios": ["string"]
  },
  "functional_requirements": {
    "overview": "string",
    "feature_details": [{
      "feature_name": "string",
      "description": "string",
      "trigger": "string",
      "processing_logic": "string",
      "inputs": ["string"],
      "outputs": ["string"],
      "exception_cases": ["string"]
    }]
  },
  "business_rules": ["string"],
  "page_and_interaction": {
    "pages": [{
      "page_name": "string",
      "entry_point": "string",
      "page_elements": ["string"],
      "button_actions": ["string"]
    }],
    "interaction_flow": ["string"]
  },
  "copywriting": ["string"],
  "data_and_dependencies": ["string"],
  "writeback_authorization": {"target_system": "string", "action": "string", "authorization_owner": "string", "acceptance_evidence": "string"},
  "risks_and_notes": ["string"],
  "acceptance_criteria": ["string"],
  "open_questions": ["string"],
  "collection_status": {
    "<each key: objective, scope, users, ownership, scenarios, features, pages, rules, integrations, acceptance>":
      {"status": "missing|captured|pending_confirmation|confirmed|conflict", "reason": "string", "pending_questions": ["string"]}
  }
}
"""

STRUCTURED_REQUIREMENT_LANGUAGE_HINTS = {
    "en": "Output all field values in English.",
    "de": "Output all field values in German.",
    "zh": "Output all field values in Simplified Chinese.",
    "ms": "Output all field values in Bahasa Melayu.",
}

REQUIREMENT_ITEM_KEYS = (
    "objective",
    "scope",
    "users",
    "ownership",
    "scenarios",
    "features",
    "pages",
    "rules",
    "integrations",
    "acceptance",
)

REQUIREMENT_ITEM_STATUS_VALUES = {
    "missing",
    "captured",
    "pending_confirmation",
    "confirmed",
    "conflict",
}


def build_structured_requirement_model_prompt(language: str) -> str:
    normalized = str(language or "").strip().lower()
    language_hint = STRUCTURED_REQUIREMENT_LANGUAGE_HINTS.get(
        normalized,
        STRUCTURED_REQUIREMENT_LANGUAGE_HINTS["en"],
    )
    return f"{STRUCTURED_REQUIREMENT_MODEL_SYSTEM_PROMPT}\n\nLanguage requirement:\n- {language_hint}"


def empty_structured_requirement_model() -> dict[str, Any]:
    return {
        "document_info": {
            "project_name": "",
            "requirement_name": "",
        },
        "product_context": {
            "requesting_department": "",
            "business_owner": "",
            "software_type": "",
            "primary_user": "",
            "decision_or_action": "",
            "acceptance_owner": "",
        },
        "background": {
            "summary": "",
            "objective": "",
        },
        "scope": {
            "in_scope": [],
            "out_of_scope": [],
        },
        "users_and_scenarios": {
            "target_users": [],
            "core_scenarios": [],
        },
        "functional_requirements": {
            "overview": "",
            "feature_details": [],
        },
        "business_rules": [],
        "page_and_interaction": {
            "pages": [],
            "interaction_flow": [],
        },
        "copywriting": [],
        "data_and_dependencies": [],
        "writeback_authorization": normalize_writeback_authorization(None),
        "risks_and_notes": [],
        "acceptance_criteria": [],
        "open_questions": [],
        "collection_status": {
            key: _empty_requirement_status()
            for key in REQUIREMENT_ITEM_KEYS
        },
    }


def normalize_structured_requirement_model(payload: Any) -> dict[str, Any]:
    root = payload if isinstance(payload, dict) else {}
    model = empty_structured_requirement_model()

    document_info = root.get("document_info") if isinstance(root.get("document_info"), dict) else {}
    model["document_info"] = {
        "project_name": _string_value(document_info.get("project_name")),
        "requirement_name": _string_value(document_info.get("requirement_name")),
    }

    product_context = root.get("product_context") if isinstance(root.get("product_context"), dict) else {}
    model["product_context"] = {
        "requesting_department": _string_value(product_context.get("requesting_department")),
        "business_owner": _string_value(product_context.get("business_owner")),
        "software_type": _string_value(product_context.get("software_type")),
        "primary_user": _string_value(product_context.get("primary_user")),
        "decision_or_action": _string_value(product_context.get("decision_or_action")),
        "acceptance_owner": _string_value(product_context.get("acceptance_owner")),
    }

    background = root.get("background") if isinstance(root.get("background"), dict) else {}
    model["background"] = {
        "summary": _string_value(background.get("summary")),
        "objective": _string_value(background.get("objective")),
    }

    scope = root.get("scope") if isinstance(root.get("scope"), dict) else {}
    model["scope"] = {
        "in_scope": _string_list(scope.get("in_scope")),
        "out_of_scope": _string_list(scope.get("out_of_scope")),
    }

    users_and_scenarios = (
        root.get("users_and_scenarios")
        if isinstance(root.get("users_and_scenarios"), dict)
        else {}
    )
    model["users_and_scenarios"] = {
        "target_users": _string_list(users_and_scenarios.get("target_users")),
        "core_scenarios": _string_list(users_and_scenarios.get("core_scenarios")),
    }

    functional_requirements = (
        root.get("functional_requirements")
        if isinstance(root.get("functional_requirements"), dict)
        else {}
    )
    model["functional_requirements"] = {
        "overview": _string_value(functional_requirements.get("overview")),
        "feature_details": _feature_details(functional_requirements.get("feature_details")),
    }

    model["business_rules"] = _string_list(root.get("business_rules"))

    page_and_interaction = (
        root.get("page_and_interaction")
        if isinstance(root.get("page_and_interaction"), dict)
        else {}
    )
    model["page_and_interaction"] = {
        "pages": _pages(page_and_interaction.get("pages")),
        "interaction_flow": _string_list(page_and_interaction.get("interaction_flow")),
    }

    model["copywriting"] = _string_list(root.get("copywriting"))
    model["data_and_dependencies"] = _string_list(root.get("data_and_dependencies"))
    model["writeback_authorization"] = normalize_writeback_authorization(
        root.get("writeback_authorization")
    )
    model["risks_and_notes"] = _string_list(root.get("risks_and_notes"))
    model["acceptance_criteria"] = _string_list(root.get("acceptance_criteria"))
    model["open_questions"] = _string_list(root.get("open_questions"))
    collection_status = (
        root.get("collection_status") if isinstance(root.get("collection_status"), dict) else {}
    )
    model["collection_status"] = {
        key: _requirement_status_item(collection_status.get(key))
        for key in REQUIREMENT_ITEM_KEYS
    }
    return model


def apply_delivery_evidence_gates(
    payload: Any,
    *,
    language: str = "en",
) -> dict[str, Any]:
    model = normalize_structured_requirement_model(payload)
    _apply_field_open_question_gates(model)
    if not _has_metric_requirement_context(model):
        return model

    rules_status = model["collection_status"]["rules"]
    if (
        rules_status["status"] == "confirmed"
        and not _has_concrete_metric_rule(model["business_rules"])
    ):
        question = _METRIC_RULE_QUESTION.get(
            _normalize_gate_language(language),
            _METRIC_RULE_QUESTION["en"],
        )
        rules_status.update(
            {
                "status": "pending_confirmation",
                "reason": "The metric or SPC rule is not implementation-ready.",
                "pending_questions": [question],
            }
        )
        return model
    if (
        rules_status["status"] == "confirmed"
        and _has_cpk_requirement_context(model)
        and not _has_cpk_value_definition(model)
    ):
        question = _CPK_DEFINITION_QUESTION.get(
            _normalize_gate_language(language),
            _CPK_DEFINITION_QUESTION["en"],
        )
        rules_status.update(
            {
                "status": "pending_confirmation",
                "reason": "The Cpk value source or approved formula is not confirmed.",
                "pending_questions": [question],
            }
        )
    return model


def _apply_field_open_question_gates(model: dict[str, Any]) -> None:
    collection_status = model["collection_status"]
    for question in model["open_questions"]:
        field_key = _field_for_open_question(question)
        if not field_key:
            continue
        item = collection_status[field_key]
        if item["status"] == "conflict":
            continue
        item.update(
            {
                "status": "pending_confirmation",
                "reason": "A delivery-relevant decision is still open.",
                "pending_questions": [question],
            }
        )


def _field_for_open_question(question: str) -> str:
    text = str(question or "").strip().lower()
    for field_key, keywords in _OPEN_QUESTION_FIELD_KEYWORDS:
        if any(keyword in text for keyword in keywords):
            return field_key
    return ""


def _has_metric_requirement_context(model: dict[str, Any]) -> bool:
    text = " ".join(_iter_text(model)).lower()
    if any(keyword in text for keyword in _METRIC_CONTEXT_KEYWORDS):
        return True

    implementation_text = " ".join(
        _iter_text(
            {
                "functional_requirements": model.get("functional_requirements"),
                "business_rules": model.get("business_rules"),
                "data_and_dependencies": model.get("data_and_dependencies"),
            }
        )
    ).lower()
    return (
        any(keyword in implementation_text for keyword in _GENERIC_METRIC_KEYWORDS)
        and any(keyword in implementation_text for keyword in _METRIC_IMPLEMENTATION_KEYWORDS)
    )


def _has_concrete_metric_rule(rules: list[str]) -> bool:
    text = " ".join(rules).lower()
    if not text:
        return False
    if "assumption:" in text:
        return True
    if re.search(r"(?:<=|>=|<|>|≤|≥)\s*-?\d+(?:\.\d+)?", text):
        return True
    if re.search(
        r"\b(?:below|above|under|over|less than|greater than)\s+-?\d+(?:\.\d+)?",
        text,
    ):
        return True
    if re.search(r"\b\d+(?:\.\d+)?\s*(?:sigma|σ)\b", text):
        return True
    if any(name in text for name in ("western electric", "nelson rules")):
        return True
    if "numerator" in text and "denominator" in text:
        return True
    if "分子" in text and "分母" in text:
        return True
    return bool(
        "=" in text
        and any(token in text for token in ("/", "%", "usl", "lsl", "average", "sum"))
    )


def _has_cpk_requirement_context(model: dict[str, Any]) -> bool:
    text = " ".join(_iter_text(model)).lower()
    return any(alias in text for alias in _CPK_ALIASES)


def _has_cpk_value_definition(model: dict[str, Any]) -> bool:
    statements = [
        *model["business_rules"],
        *model["data_and_dependencies"],
    ]
    for statement in statements:
        text = str(statement or "").lower()
        if not any(alias in text for alias in _CPK_ALIASES):
            continue
        if any(signal in text for signal in _CPK_DEFINITION_SIGNALS):
            return True
    return False


def _iter_text(value: Any):
    if isinstance(value, str):
        if value.strip():
            yield value.strip()
        return
    if isinstance(value, dict):
        for item in value.values():
            yield from _iter_text(item)
        return
    if isinstance(value, list):
        for item in value:
            yield from _iter_text(item)


def _normalize_gate_language(language: str) -> str:
    normalized = str(language or "").strip().lower().replace("_", "-")
    if normalized.startswith("zh"):
        return "zh"
    return normalized if normalized in _METRIC_RULE_QUESTION else "en"


_METRIC_CONTEXT_KEYWORDS = (
    "spc",
    "cpk",
    "process capability",
    "control chart",
    "yield",
    "oee",
    "良率",
    "控制图",
    "过程能力",
)

_GENERIC_METRIC_KEYWORDS = ("kpi", "metric", "指标")

_METRIC_IMPLEMENTATION_KEYWORDS = (
    "dashboard",
    "chart",
    "formula",
    "calculation",
    "calculate",
    "aggregation",
    "看板",
    "图表",
    "公式",
    "计算",
    "聚合",
    "口径",
)

_CPK_ALIASES = (
    "cpk",
    "process capability index",
    "过程能力指数",
)

_CPK_DEFINITION_SIGNALS = (
    "source field",
    "provided by",
    "supplied by",
    "read from",
    "stored in",
    "calculated",
    "computed",
    "approved formula",
    "usl",
    "lsl",
    "来源字段",
    "源字段",
    "提供",
    "读取",
    "计算",
    "公式",
    "quellfeld",
    "bereitgestellt",
    "dikira",
    "medan sumber",
)

_OPEN_QUESTION_FIELD_KEYWORDS = (
    (
        "ownership",
        (
            "business owner",
            "acceptance owner",
            "who owns",
            "who will accept",
            "owner for acceptance",
            "业务负责人",
            "验收负责人",
            "谁负责",
            "负责人",
            "geschäftsverantwort",
            "abnahmeverantwort",
            "pemilik perniagaan",
            "pemilik penerimaan",
        ),
    ),
    (
        "rules",
        (
            "approve",
            "approval",
            "approver",
            "transition",
            "status",
            "sla",
            "rule",
            "formula",
            "threshold",
            "permission",
            "审批",
            "批准",
            "状态",
            "规则",
            "公式",
            "阈值",
            "权限",
        ),
    ),
    (
        "integrations",
        (
            "data source",
            "source of truth",
            "sql server",
            "sap",
            "upload",
            "interface",
            "api",
            "table",
            "field",
            "数据源",
            "数据来源",
            "接口",
            "表",
            "字段",
            "上传",
        ),
    ),
    (
        "acceptance",
        (
            "acceptance",
            "success evidence",
            "proof",
            "pass/fail",
            "验收",
            "成功证据",
            "通过标准",
        ),
    ),
    (
        "scope",
        (
            "scope",
            "in scope",
            "out of scope",
            "first release",
            "v1",
            "范围",
            "首版",
        ),
    ),
    (
        "users",
        (
            "primary user",
            "target user",
            "主要用户",
            "目标用户",
        ),
    ),
    (
        "scenarios",
        (
            "workflow",
            "scenario",
            "current process",
            "流程",
            "场景",
        ),
    ),
    (
        "features",
        (
            "feature",
            "function",
            "capability",
            "功能",
            "能力",
        ),
    ),
    (
        "objective",
        (
            "objective",
            "business outcome",
            "goal",
            "业务目标",
            "业务结果",
        ),
    ),
)

_METRIC_RULE_QUESTION = {
    "en": "What exact formula, threshold, time window, or SPC rule should v1 use?",
    "zh": "首版应使用什么明确的公式、阈值、时间窗或 SPC 判异规则？",
    "de": "Welche genaue Formel, Schwelle, Zeitspanne oder SPC-Regel soll v1 verwenden?",
    "ms": "Formula, ambang, tetingkap masa atau peraturan SPC tepat yang mana perlu digunakan untuk v1?",
}

_CPK_DEFINITION_QUESTION = {
    "en": "Does v1 use a confirmed source field or an approved formula and window for Cpk?",
    "zh": "首版 Cpk 是读取已确认的来源字段，还是按已批准的公式和时间窗计算？",
    "de": "Liest v1 Cpk aus einem bestaetigten Quellfeld oder berechnet es mit einer freigegebenen Formel und Zeitspanne?",
    "ms": "Adakah v1 membaca Cpk daripada medan sumber yang disahkan atau mengiranya dengan formula dan tetingkap masa yang diluluskan?",
}


def _feature_details(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []

    items: list[dict[str, Any]] = []
    for raw_item in value:
        if not isinstance(raw_item, dict):
            continue

        item = {
            "feature_name": _string_value(raw_item.get("feature_name")),
            "description": _string_value(raw_item.get("description")),
            "trigger": _string_value(raw_item.get("trigger")),
            "processing_logic": _string_value(raw_item.get("processing_logic")),
            "inputs": _string_list(raw_item.get("inputs")),
            "outputs": _string_list(raw_item.get("outputs")),
            "exception_cases": _string_list(raw_item.get("exception_cases")),
        }
        if _has_object_content(item):
            items.append(item)
    return items


def _pages(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []

    items: list[dict[str, Any]] = []
    for raw_item in value:
        if not isinstance(raw_item, dict):
            continue

        item = {
            "page_name": _string_value(raw_item.get("page_name")),
            "entry_point": _string_value(raw_item.get("entry_point")),
            "page_elements": _string_list(raw_item.get("page_elements")),
            "button_actions": _string_list(raw_item.get("button_actions")),
        }
        if _has_object_content(item):
            items.append(item)
    return items


def _string_value(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [item for item in (_string_value(entry) for entry in value) if item]
    if isinstance(value, str):
        cleaned = value.strip()
        return [cleaned] if cleaned else []
    return []


def _has_object_content(value: dict[str, Any]) -> bool:
    for field_value in value.values():
        if isinstance(field_value, list) and field_value:
            return True
        if isinstance(field_value, str) and field_value:
            return True
    return False


def _empty_requirement_status() -> dict[str, Any]:
    return {
        "status": "missing",
        "reason": "",
        "pending_questions": [],
    }


def _requirement_status_item(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return _empty_requirement_status()

    status = _string_value(value.get("status")).lower()
    if status not in REQUIREMENT_ITEM_STATUS_VALUES:
        status = "missing"

    return {
        "status": status,
        "reason": _string_value(value.get("reason")),
        "pending_questions": _string_list(value.get("pending_questions")),
    }
