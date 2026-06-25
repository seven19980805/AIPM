from __future__ import annotations

from typing import Any


STRUCTURED_REQUIREMENT_MODEL_SYSTEM_PROMPT = """You are a senior requirement analysis assistant.
Convert the requirement conversation into a structured requirement model based on a simple PRD template.

Important rules:
1) Output strict JSON only with no markdown fences and no extra text.
2) Capture only confirmed or explicitly stated information from the conversation.
3) If something is unclear or missing, use empty strings or empty arrays.
4) Do not invent facts. Put unresolved items into open_questions when they materially affect delivery.
5) Keep the JSON keys exactly as specified below.
6) Prefer concise, requirement-oriented statements; do not generate implementation code or pseudo-code.
7) feature_details should describe concrete features or requirement items, not vague themes.
8) pages should list concrete pages or touchpoints only when the conversation supports them.
9) copywriting should list concrete UI text, labels, or error messages only when they were mentioned.
10) acceptance_criteria should be testable outcomes when the conversation provides enough signal.
11) Do not backfill empty sections with generic product assumptions.
12) If the conversation does not explicitly mention pages, business rules, integrations, or acceptance criteria, leave them empty.
13) For each requirement item, assign a collection status that reflects whether it is really confirmed, not just mentioned.
14) Only use "confirmed" when the conversation already provides stable, implementation-ready information and there is no meaningful follow-up needed for that item.
15) Use "captured" when some useful signal exists but it is still too early or too shallow to call it confirmed.
16) Use "pending_confirmation" when the item has a candidate definition but still needs an explicit user confirmation or a focused follow-up.
17) Use "conflict" when the conversation contains inconsistent statements for the item.
18) Use "missing" when the conversation provides no reliable information for the item.
19) reason should briefly explain why the item is currently in that status.
20) pending_questions should contain short, concrete follow-up questions only when the item is not confirmed.
21) Keep collection_status.status values exactly as the English enum tokens in the schema. Do not translate those enum values.
22) product_context should capture the product-manager handoff facts when stated: requesting department, business owner, first-version software type, primary user, decision/action supported, and acceptance owner.
23) Assistant suggestions, assistant summaries, assistant-generated draft PRDs, and generated document text are not user confirmation. They may explain candidate assumptions, but they must not upgrade collection_status to "confirmed".
24) A/B/C user replies confirm only the specific option text immediately offered by the assistant, not later assistant elaborations or inferred document content.
25) If any item still has pending_questions, or if open_questions contains delivery-relevant gaps, that item is not fully ready for document generation / Go Coding.
26) When the user selects Option A (by replying "A", "A.", "选A", "我选A", "Confirm...", or "按建议口径确认...") to confirm a blocker label, this constitutes explicit user confirmation of that requirement item or methodology gap using version-one assumptions. You MUST:
  a) Identify which blocker label is being confirmed (e.g., "Priority and scope trade-offs" / "优先级与范围取舍" / "scope", "Success metric" / "成功指标" / "success_metric", "Validation plan" / "验证计划" / "validation_plan", "Integration systems" / "集成系统" / "integrations", etc.).
  b) Formulate a reasonable, concrete version-one assumption for that blocker/item based on the project context (for example, if the label is "Priority and scope trade-offs", populate "scope.in_scope" with the core features mentioned and "scope.out_of_scope" with standard exclusions; if the label is "Success metric" or "Validation plan", write a verifiable acceptance criterion).
  c) Write this formulated assumption into the corresponding JSON fields.
  d) Upgrade the status of the corresponding key(s) in "collection_status" to "confirmed" (e.g., "scope", "acceptance", "integrations", etc.), clear its "pending_questions", and write a brief reason like "Confirmed via Option A assumption."


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
    "feature_details": [
      {
        "feature_name": "string",
        "description": "string",
        "trigger": "string",
        "processing_logic": "string",
        "inputs": ["string"],
        "outputs": ["string"],
        "exception_cases": ["string"]
      }
    ]
  },
  "business_rules": ["string"],
  "page_and_interaction": {
    "pages": [
      {
        "page_name": "string",
        "entry_point": "string",
        "page_elements": ["string"],
        "button_actions": ["string"]
      }
    ],
    "interaction_flow": ["string"]
  },
  "copywriting": ["string"],
  "data_and_dependencies": ["string"],
  "risks_and_notes": ["string"],
  "acceptance_criteria": ["string"],
  "open_questions": ["string"],
  "collection_status": {
    "objective": {
      "status": "missing|captured|pending_confirmation|confirmed|conflict",
      "reason": "string",
      "pending_questions": ["string"]
    },
    "scope": {
      "status": "missing|captured|pending_confirmation|confirmed|conflict",
      "reason": "string",
      "pending_questions": ["string"]
    },
    "users": {
      "status": "missing|captured|pending_confirmation|confirmed|conflict",
      "reason": "string",
      "pending_questions": ["string"]
    },
    "scenarios": {
      "status": "missing|captured|pending_confirmation|confirmed|conflict",
      "reason": "string",
      "pending_questions": ["string"]
    },
    "features": {
      "status": "missing|captured|pending_confirmation|confirmed|conflict",
      "reason": "string",
      "pending_questions": ["string"]
    },
    "pages": {
      "status": "missing|captured|pending_confirmation|confirmed|conflict",
      "reason": "string",
      "pending_questions": ["string"]
    },
    "rules": {
      "status": "missing|captured|pending_confirmation|confirmed|conflict",
      "reason": "string",
      "pending_questions": ["string"]
    },
    "integrations": {
      "status": "missing|captured|pending_confirmation|confirmed|conflict",
      "reason": "string",
      "pending_questions": ["string"]
    },
    "acceptance": {
      "status": "missing|captured|pending_confirmation|confirmed|conflict",
      "reason": "string",
      "pending_questions": ["string"]
    }
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
