from __future__ import annotations

from copy import deepcopy
import re
import uuid
from typing import Any

from .structured_requirement_model import normalize_structured_requirement_model


class ProposalValidationError(ValueError):
    """Raised when a reply does not identify one current, single-decision proposal."""


_YES_TOKENS = {
    "yes",
    "y",
    "ok",
    "okay",
    "confirm",
    "confirmed",
    "accept",
    "是",
    "好的",
    "好",
    "确认",
    "可以",
    "采用",
    "ja",
    "bestätigen",
    "bestaetigen",
    "ya",
    "sahkan",
}

_DECISION_FIELD_WHITELISTS: dict[str, frozenset[str]] = {
    "outcome": frozenset(
        {
            "background.objective",
            "collection_status.objective.status",
            "collection_status.objective.reason",
            "collection_status.objective.pending_questions",
        }
    ),
    "actor_action": frozenset(
        {
            "product_context.primary_user",
            "product_context.decision_or_action",
            "users_and_scenarios.target_users",
            "collection_status.users.status",
            "collection_status.users.reason",
            "collection_status.users.pending_questions",
        }
    ),
    "v1_flow": frozenset(
        {
            "scope.in_scope",
            "scope.out_of_scope",
            "users_and_scenarios.core_scenarios",
            "functional_requirements.overview",
            "collection_status.scope.status",
            "collection_status.scope.reason",
            "collection_status.scope.pending_questions",
            "collection_status.scenarios.status",
            "collection_status.scenarios.reason",
            "collection_status.scenarios.pending_questions",
            "collection_status.features.status",
            "collection_status.features.reason",
            "collection_status.features.pending_questions",
        }
    ),
    "data_boundary": frozenset(
        {
            "data_and_dependencies",
            "collection_status.integrations.status",
            "collection_status.integrations.reason",
            "collection_status.integrations.pending_questions",
        }
    ),
    "acceptance": frozenset(
        {
            "acceptance_criteria",
            "collection_status.acceptance.status",
            "collection_status.acceptance.reason",
            "collection_status.acceptance.pending_questions",
        }
    ),
    "ownership": frozenset(
        {
            "product_context.business_owner",
            "product_context.acceptance_owner",
            "collection_status.ownership.status",
            "collection_status.ownership.reason",
            "collection_status.ownership.pending_questions",
        }
    ),
    "rules": frozenset(
        {
            "business_rules",
            "collection_status.rules.status",
            "collection_status.rules.reason",
            "collection_status.rules.pending_questions",
        }
    ),
}
_DECISION_FIELD_WHITELISTS.update(
    {
        "objective": _DECISION_FIELD_WHITELISTS["outcome"],
        "users": _DECISION_FIELD_WHITELISTS["actor_action"],
        "integrations": _DECISION_FIELD_WHITELISTS["data_boundary"],
        "scope": frozenset(
            {
                "scope.in_scope",
                "scope.out_of_scope",
                "collection_status.scope.status",
                "collection_status.scope.reason",
                "collection_status.scope.pending_questions",
            }
        ),
        "scenarios": frozenset(
            {
                "users_and_scenarios.core_scenarios",
                "collection_status.scenarios.status",
                "collection_status.scenarios.reason",
                "collection_status.scenarios.pending_questions",
            }
        ),
        "features": frozenset(
            {
                "functional_requirements.overview",
                "collection_status.features.status",
                "collection_status.features.reason",
                "collection_status.features.pending_questions",
            }
        ),
    }
)

_PROPOSAL_COPY: dict[str, dict[str, dict[str, Any]]] = {
    "outcome": {
        "zh": {
            "text": "在下一季度把误判导致的电测逃逸率降低 15%。",
            "patch": {"background.objective": "在下一季度把误判导致的电测逃逸率降低 15%。"},
        },
        "en": {
            "text": "Reduce false-fail e-test escapes by 15% within the next quarter.",
            "patch": {
                "background.objective": (
                    "Reduce false-fail e-test escapes by 15% within the next quarter."
                )
            },
        },
        "de": {
            "text": "Die False-Fail-E-Test-Escapes im nächsten Quartal um 15 % senken.",
            "patch": {
                "background.objective": (
                    "Die False-Fail-E-Test-Escapes im nächsten Quartal um 15 % senken."
                )
            },
        },
        "ms": {
            "text": "Kurangkan pelepasan e-test false-fail sebanyak 15% dalam suku berikutnya.",
            "patch": {
                "background.objective": (
                    "Kurangkan pelepasan e-test false-fail sebanyak 15% dalam suku berikutnya."
                )
            },
        },
    },
    "actor_action": {
        "zh": {
            "text": "值班主管根据产品代码的实时良率趋势安排复测。",
            "patch": {
                "product_context.primary_user": "值班主管",
                "product_context.decision_or_action": "根据产品代码的实时良率趋势安排复测",
                "users_and_scenarios.target_users": ["值班主管"],
            },
        },
        "en": {
            "text": "The shift supervisor uses real-time yield by product code to schedule retests.",
            "patch": {
                "product_context.primary_user": "Shift supervisor",
                "product_context.decision_or_action": (
                    "Use real-time yield by product code to schedule retests"
                ),
                "users_and_scenarios.target_users": ["Shift supervisor"],
            },
        },
        "de": {
            "text": "Die Schichtleitung plant Nachtests anhand der Echtzeit-Ausbeute je Produktcode.",
            "patch": {
                "product_context.primary_user": "Schichtleitung",
                "product_context.decision_or_action": (
                    "Nachtests anhand der Echtzeit-Ausbeute je Produktcode planen"
                ),
                "users_and_scenarios.target_users": ["Schichtleitung"],
            },
        },
        "ms": {
            "text": "Penyelia syif menjadualkan ujian semula berdasarkan trend yield masa nyata mengikut kod produk.",
            "patch": {
                "product_context.primary_user": "Penyelia syif",
                "product_context.decision_or_action": (
                    "Jadualkan ujian semula berdasarkan trend yield masa nyata mengikut kod produk"
                ),
                "users_and_scenarios.target_users": ["Penyelia syif"],
            },
        },
    },
    "v1_flow": {
        "zh": {
            "text": "首版提供按产品代码筛选的良率趋势看板、异常批次下钻和复测清单；不包含自动处置。",
            "patch": {
                "scope.in_scope": ["良率趋势看板", "异常批次下钻", "复测清单"],
                "scope.out_of_scope": ["自动处置"],
                "users_and_scenarios.core_scenarios": [
                    "筛选产品代码并下钻异常批次后生成复测清单"
                ],
                "functional_requirements.overview": (
                    "按产品代码展示良率趋势，支持异常批次下钻和复测清单。"
                ),
            },
        },
        "en": {
            "text": "V1 provides yield trends by product code, abnormal-lot drill-down, and a retest list; automated disposition is out of scope.",
            "patch": {
                "scope.in_scope": [
                    "Yield trends by product code",
                    "Abnormal-lot drill-down",
                    "Retest list",
                ],
                "scope.out_of_scope": ["Automated disposition"],
                "users_and_scenarios.core_scenarios": [
                    "Filter a product code, inspect an abnormal lot, and create a retest list"
                ],
                "functional_requirements.overview": (
                    "Show yield trends by product code with abnormal-lot drill-down and retest lists."
                ),
            },
        },
        "de": {
            "text": "V1 bietet Ausbeutetrends je Produktcode, Drill-down für auffällige Lose und eine Nachtestliste; automatische Disposition ist nicht enthalten.",
            "patch": {
                "scope.in_scope": [
                    "Ausbeutetrends je Produktcode",
                    "Drill-down für auffällige Lose",
                    "Nachtestliste",
                ],
                "scope.out_of_scope": ["Automatische Disposition"],
                "users_and_scenarios.core_scenarios": [
                    "Produktcode filtern, auffälliges Los prüfen und Nachtestliste erstellen"
                ],
                "functional_requirements.overview": (
                    "Ausbeutetrends je Produktcode mit Los-Drill-down und Nachtestliste anzeigen."
                ),
            },
        },
        "ms": {
            "text": "V1 menyediakan trend yield mengikut kod produk, drill-down lot abnormal dan senarai ujian semula; pelupusan automatik di luar skop.",
            "patch": {
                "scope.in_scope": [
                    "Trend yield mengikut kod produk",
                    "Drill-down lot abnormal",
                    "Senarai ujian semula",
                ],
                "scope.out_of_scope": ["Pelupusan automatik"],
                "users_and_scenarios.core_scenarios": [
                    "Tapis kod produk, semak lot abnormal dan bina senarai ujian semula"
                ],
                "functional_requirements.overview": (
                    "Paparkan trend yield, drill-down lot abnormal dan senarai ujian semula."
                ),
            },
        },
    },
    "data_boundary": {
        "zh": {
            "text": "首版只读 SQL Server 中的电测结果和 SAP 产品主数据，不向源系统回写。",
            "patch": {
                "data_and_dependencies": [
                    "只读 SQL Server 电测结果",
                    "只读 SAP 产品主数据",
                    "首版不向任何源系统回写",
                ]
            },
        },
        "en": {
            "text": "V1 reads e-test results from SQL Server and product master data from SAP; it writes nothing back to source systems.",
            "patch": {
                "data_and_dependencies": [
                    "Read-only SQL Server e-test results",
                    "Read-only SAP product master data",
                    "No source-system writeback in V1",
                ]
            },
        },
        "de": {
            "text": "V1 liest E-Test-Ergebnisse aus SQL Server und Produktstammdaten aus SAP; es gibt keinen Rückschreibzugriff.",
            "patch": {
                "data_and_dependencies": [
                    "SQL-Server-E-Test-Ergebnisse nur lesen",
                    "SAP-Produktstammdaten nur lesen",
                    "Kein Rückschreiben in V1",
                ]
            },
        },
        "ms": {
            "text": "V1 membaca keputusan e-test daripada SQL Server dan data induk produk daripada SAP tanpa menulis balik ke sistem sumber.",
            "patch": {
                "data_and_dependencies": [
                    "Baca sahaja keputusan e-test SQL Server",
                    "Baca sahaja data induk produk SAP",
                    "Tiada writeback ke sistem sumber dalam V1",
                ]
            },
        },
    },
    "acceptance": {
        "zh": {
            "text": "用户可在 5 分钟内看到最近一批数据，按产品代码下钻异常批次并导出复测清单。",
            "patch": {
                "acceptance_criteria": [
                    "最近一批数据在 5 分钟内可见",
                    "可按产品代码下钻异常批次",
                    "可导出复测清单",
                ]
            },
        },
        "en": {
            "text": "Users see the latest lot within five minutes, drill into abnormal lots by product code, and export a retest list.",
            "patch": {
                "acceptance_criteria": [
                    "Latest lot visible within five minutes",
                    "Abnormal lots can be drilled into by product code",
                    "Retest list can be exported",
                ]
            },
        },
        "de": {
            "text": "Nutzer sehen das neueste Los innerhalb von fünf Minuten, öffnen auffällige Lose je Produktcode und exportieren eine Nachtestliste.",
            "patch": {
                "acceptance_criteria": [
                    "Neuestes Los innerhalb von fünf Minuten sichtbar",
                    "Drill-down auffälliger Lose je Produktcode",
                    "Nachtestliste exportierbar",
                ]
            },
        },
        "ms": {
            "text": "Pengguna melihat lot terkini dalam lima minit, drill-down lot abnormal mengikut kod produk dan eksport senarai ujian semula.",
            "patch": {
                "acceptance_criteria": [
                    "Lot terkini kelihatan dalam lima minit",
                    "Lot abnormal boleh di-drill-down mengikut kod produk",
                    "Senarai ujian semula boleh dieksport",
                ]
            },
        },
    },
}


def _normalize_language(language: str) -> str:
    normalized = str(language or "").strip().lower()
    return normalized if normalized in {"zh", "en", "de", "ms"} else "en"


def is_confirmation_text(text: str) -> bool:
    normalized = re.sub(r"[.!！。?？]+$", "", str(text or "").strip().lower())
    return normalized in _YES_TOKENS


def build_decision_proposal(
    decision_id: str,
    structured_requirement_model: dict[str, Any] | None,
    language: str,
) -> dict[str, Any]:
    decision_key = str(decision_id or "").strip()
    language_key = _normalize_language(language)
    normalized_model = normalize_structured_requirement_model(
        structured_requirement_model,
    )
    localized = _contextual_proposal_copy(
        decision_key,
        normalized_model,
        language_key,
    ) or _proposal_copy_for_decision(decision_key, language_key)
    patch = deepcopy(localized["patch"])
    patch.update(_confirmation_status_patch(decision_key, language_key))
    allowed_fields = sorted(patch)
    _validate_proposal_fields(decision_key, allowed_fields, patch)
    return {
        "proposal_id": f"proposal-{uuid.uuid4().hex}",
        "decision_id": decision_key,
        "text": str(localized["text"]),
        "allowed_fields": allowed_fields,
        "patch": patch,
    }


def _contextual_proposal_copy(
    decision_id: str,
    model: dict[str, Any],
    language: str,
) -> dict[str, Any] | None:
    alias = {
        "objective": "outcome",
        "users": "actor_action",
        "integrations": "data_boundary",
    }.get(decision_id, decision_id)
    if alias != "outcome":
        return None

    background = model.get("background")
    objective = (
        str(background.get("objective", "")).strip()
        if isinstance(background, dict)
        else ""
    )
    if not objective:
        return None
    base = objective.rstrip(" .。；;")
    text = {
        "zh": f"{base}，并以下季度约定核心指标改善 15% 作为首版目标。",
        "en": (
            f"{base}, measured by a 15% improvement in the agreed primary KPI "
            "within the next quarter."
        ),
        "de": (
            f"{base}; als Ziel gilt eine Verbesserung der vereinbarten "
            "Kernkennzahl um 15 % im nächsten Quartal."
        ),
        "ms": (
            f"{base}, diukur melalui peningkatan 15% pada KPI utama yang "
            "dipersetujui dalam suku berikutnya."
        ),
    }[language]
    return {
        "text": text,
        "patch": {"background.objective": text},
    }


def _proposal_copy_for_decision(decision_id: str, language: str) -> dict[str, Any]:
    alias = {
        "objective": "outcome",
        "users": "actor_action",
        "integrations": "data_boundary",
    }.get(decision_id, decision_id)
    decision_copy = _PROPOSAL_COPY.get(alias)
    if decision_copy is not None:
        return decision_copy.get(language) or decision_copy["en"]

    v1_copy = _PROPOSAL_COPY["v1_flow"].get(language) or _PROPOSAL_COPY["v1_flow"]["en"]
    if decision_id == "scope":
        return {
            "text": {
                "zh": "首版包含良率趋势看板、异常批次下钻和复测清单；不包含自动处置。",
                "en": "V1 includes yield trends, abnormal-lot drill-down, and a retest list; automated disposition is out of scope.",
                "de": "V1 umfasst Ausbeutetrends, Los-Drill-down und Nachtestliste; automatische Disposition ist ausgeschlossen.",
                "ms": "V1 merangkumi trend yield, drill-down lot abnormal dan senarai ujian semula; pelupusan automatik di luar skop.",
            }[language],
            "patch": {
                key: value
                for key, value in v1_copy["patch"].items()
                if key.startswith("scope.")
            },
        }
    if decision_id == "scenarios":
        return {
            "text": {
                "zh": "核心场景是筛选产品代码、下钻异常批次并生成复测清单。",
                "en": "The core scenario is to filter a product code, inspect an abnormal lot, and create a retest list.",
                "de": "Das Kernszenario filtert einen Produktcode, prüft ein auffälliges Los und erstellt eine Nachtestliste.",
                "ms": "Senario teras ialah menapis kod produk, menyemak lot abnormal dan membina senarai ujian semula.",
            }[language],
            "patch": {
                "users_and_scenarios.core_scenarios": v1_copy["patch"][
                    "users_and_scenarios.core_scenarios"
                ]
            },
        }
    if decision_id == "features":
        return {
            "text": {
                "zh": "核心能力是按产品代码展示良率趋势，并支持异常批次下钻和复测清单。",
                "en": "The core capability shows yield trends by product code with abnormal-lot drill-down and retest lists.",
                "de": "Die Kernfunktion zeigt Ausbeutetrends je Produktcode mit Los-Drill-down und Nachtestlisten.",
                "ms": "Keupayaan teras memaparkan trend yield mengikut kod produk dengan drill-down lot abnormal dan senarai ujian semula.",
            }[language],
            "patch": {
                "functional_requirements.overview": v1_copy["patch"][
                    "functional_requirements.overview"
                ]
            },
        }
    if decision_id == "rules":
        return {
            "text": {
                "zh": "良率使用质量部门批准的成品批次公式，阈值变更必须保留审计记录。",
                "en": "Yield uses the Quality-approved finished-lot formula, and threshold changes must be audited.",
                "de": "Die Ausbeute nutzt die von Quality freigegebene Fertiglos-Formel; Grenzwertänderungen werden auditiert.",
                "ms": "Yield menggunakan formula lot siap yang diluluskan Quality dan perubahan ambang mesti diaudit.",
            }[language],
            "patch": {
                "business_rules": [
                    {
                        "zh": "良率使用质量部门批准的成品批次公式。",
                        "en": "Yield uses the Quality-approved finished-lot formula.",
                        "de": "Die Ausbeute nutzt die von Quality freigegebene Fertiglos-Formel.",
                        "ms": "Yield menggunakan formula lot siap yang diluluskan Quality.",
                    }[language],
                    {
                        "zh": "阈值变更必须保留审计记录。",
                        "en": "Threshold changes must retain an audit trail.",
                        "de": "Grenzwertänderungen müssen auditierbar sein.",
                        "ms": "Perubahan ambang mesti menyimpan rekod audit.",
                    }[language],
                ]
            },
        }
    if decision_id == "ownership":
        return {
            "text": {
                "zh": "制造经理对业务结果负责，质量经理负责验收签字。",
                "en": "The Manufacturing Manager owns the business outcome, and the Quality Manager signs off acceptance.",
                "de": "Die Fertigungsleitung verantwortet das Geschäftsergebnis, die Qualitätsleitung die Abnahme.",
                "ms": "Pengurus Pembuatan memiliki hasil perniagaan dan Pengurus Kualiti meluluskan penerimaan.",
            }[language],
            "patch": {
                "product_context.business_owner": {
                    "zh": "制造经理",
                    "en": "Manufacturing Manager",
                    "de": "Fertigungsleitung",
                    "ms": "Pengurus Pembuatan",
                }[language],
                "product_context.acceptance_owner": {
                    "zh": "质量经理",
                    "en": "Quality Manager",
                    "de": "Qualitätsleitung",
                    "ms": "Pengurus Kualiti",
                }[language],
            },
        }
    raise ProposalValidationError(
        f"No single-decision example is available for {decision_id!r}."
    )


def _confirmation_status_patch(decision_id: str, language: str) -> dict[str, Any]:
    status_keys = {
        "outcome": ("objective",),
        "actor_action": ("users",),
        "v1_flow": ("scope", "scenarios", "features"),
        "data_boundary": ("integrations",),
        "acceptance": ("acceptance",),
        "ownership": ("ownership",),
        "rules": ("rules",),
        "objective": ("objective",),
        "users": ("users",),
        "scope": ("scope",),
        "scenarios": ("scenarios",),
        "features": ("features",),
        "integrations": ("integrations",),
    }.get(decision_id, ())
    reasons = {
        "zh": "用户采用了当前单一决策提案。",
        "en": "The user accepted the current single-decision proposal.",
        "de": "Der Nutzer hat den aktuellen Einzelentscheidungsvorschlag bestätigt.",
        "ms": "Pengguna menerima cadangan keputusan tunggal semasa.",
    }
    patch: dict[str, Any] = {}
    for key in status_keys:
        prefix = f"collection_status.{key}"
        patch[f"{prefix}.status"] = "confirmed"
        patch[f"{prefix}.reason"] = reasons[language]
        patch[f"{prefix}.pending_questions"] = []
    return patch


def _validate_proposal_fields(
    decision_id: str,
    allowed_fields: list[str],
    patch: dict[str, Any],
) -> None:
    whitelist = _DECISION_FIELD_WHITELISTS.get(decision_id)
    if whitelist is None:
        raise ProposalValidationError("Unknown proposal decision.")
    normalized_allowed = {str(item) for item in allowed_fields}
    patch_fields = {str(item) for item in patch}
    if not normalized_allowed or normalized_allowed != patch_fields:
        raise ProposalValidationError("Proposal fields are incomplete or inconsistent.")
    if not patch_fields.issubset(whitelist):
        raise ProposalValidationError("Proposal crosses the active decision boundary.")


def validate_proposal(proposal: Any) -> dict[str, Any]:
    if not isinstance(proposal, dict):
        raise ProposalValidationError("No valid proposal is available.")
    proposal_id = str(proposal.get("proposal_id", "")).strip()
    decision_id = str(proposal.get("decision_id", "")).strip()
    text = str(proposal.get("text", "")).strip()
    allowed_fields = proposal.get("allowed_fields")
    patch = proposal.get("patch")
    if (
        not proposal_id
        or not decision_id
        or not text
        or not isinstance(allowed_fields, list)
        or not isinstance(patch, dict)
    ):
        raise ProposalValidationError("The proposal metadata is incomplete.")
    _validate_proposal_fields(decision_id, allowed_fields, patch)
    return deepcopy(proposal)


def resolve_proposal_from_messages(
    messages: list[dict[str, Any]],
    reply_context: dict[str, Any] | None,
    *,
    free_text: str = "",
) -> dict[str, Any]:
    context = reply_context if isinstance(reply_context, dict) else {}
    action = str(context.get("action", "")).strip()
    if action and action != "accept_proposal":
        raise ProposalValidationError("The reply does not accept a proposal.")
    if not action and not is_confirmation_text(free_text):
        raise ProposalValidationError("The reply is not an explicit proposal acceptance.")

    if not messages:
        raise ProposalValidationError("There is no proposal to confirm.")
    latest = messages[-1]
    if not isinstance(latest, dict) or latest.get("role") != "assistant":
        raise ProposalValidationError("The latest assistant turn is not a proposal.")
    metadata = latest.get("metadata")
    interview_turn = metadata.get("interview_turn") if isinstance(metadata, dict) else None
    if not isinstance(interview_turn, dict):
        raise ProposalValidationError("The latest assistant turn has no proposal.")
    if interview_turn.get("proposals"):
        raise ProposalValidationError("Multiple proposals cannot be confirmed with a generic yes.")
    proposal = validate_proposal(interview_turn.get("proposal"))

    if action:
        expected_decision_id = str(context.get("decision_id", "")).strip()
        expected_proposal_id = str(context.get("proposal_id", "")).strip()
        if expected_decision_id != proposal["decision_id"]:
            raise ProposalValidationError("The proposal belongs to another decision.")
        if expected_proposal_id != proposal["proposal_id"]:
            raise ProposalValidationError("The proposal is stale or no longer active.")
    return proposal


def apply_proposal_to_model(
    structured_requirement_model: dict[str, Any] | None,
    proposal: dict[str, Any],
) -> dict[str, Any]:
    validated = validate_proposal(proposal)
    model = normalize_structured_requirement_model(structured_requirement_model)
    for path, value in validated["patch"].items():
        _set_path(model, path, deepcopy(value))
    return normalize_structured_requirement_model(model)


def _set_path(target: dict[str, Any], path: str, value: Any) -> None:
    parts = path.split(".")
    current = target
    for part in parts[:-1]:
        child = current.get(part)
        if not isinstance(child, dict):
            child = {}
            current[part] = child
        current = child
    current[parts[-1]] = value


_STOP_LINE_PATTERNS = (
    re.compile(r"^\s*(next question|one question|to keep moving|to proceed)\b", re.I),
    re.compile(r"^\s*(下一|接下来|为了继续|请从以下)\b"),
    re.compile(r"^\s*(nächste frage|um fortzufahren)\b", re.I),
    re.compile(r"^\s*(soalan seterusnya|untuk meneruskan)\b", re.I),
)
_CHOICE_LINE = re.compile(r"^\s*(?:[-*]\s*)?[ABC][.)：:]\s+", re.I)
_READINESS_CLAIM = re.compile(
    r"(?:"
    r"ready to (?:generate|handoff|go coding)|"
    r"ready to be generated|"
    r"enough detail to generate|click .*generate|"
    r"interview is (?:now )?(?:complete|finished)|"
    r"please generate .*build brief|"
    r"可以(?:生成|进入)|已(?:就绪|准备好)|点击.*生成|"
    r"访谈.*(?:完成|结束)|请.*生成.*(?:build brief|构建简报)|"
    r"bereit (?:zum|für)|genug details|"
    r"interview.*abgeschlossen|build brief.*erstellen|"
    r"sedia untuk|cukup maklumat|temu bual.*selesai|"
    r"jana.*build brief"
    r")",
    re.I,
)


def sanitize_assistant_summary(text: str, language: str = "en") -> str:
    lines = str(text or "").replace("\r\n", "\n").split("\n")
    kept: list[str] = []
    bullet_count = 0
    for raw_line in lines:
        line = raw_line.rstrip()
        line = " ".join(
            sentence
            for sentence in re.split(r"(?<=[.!?。！？])\s+", line)
            if sentence and not _READINESS_CLAIM.search(sentence)
        )
        stripped = line.strip()
        if any(pattern.search(stripped) for pattern in _STOP_LINE_PATTERNS):
            break
        if _CHOICE_LINE.search(stripped):
            continue
        if _READINESS_CLAIM.search(stripped):
            continue
        if "?" in stripped or "？" in stripped:
            continue
        if re.match(r"^\s*[-*]\s+", line):
            bullet_count += 1
            if bullet_count > 2:
                continue
        kept.append(line)

    sanitized = "\n".join(kept).strip()
    sanitized = re.sub(r"\n{3,}", "\n\n", sanitized)
    if sanitized:
        return sanitized
    fallbacks = {
        "zh": "已记录这条信息。",
        "de": "Diese Information wurde erfasst.",
        "ms": "Maklumat ini telah direkodkan.",
        "en": "That information has been recorded.",
    }
    return fallbacks[_normalize_language(language)]
