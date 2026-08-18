from __future__ import annotations

from typing import Any

from .intake_workflow import (
    INTAKE_MODE_DRAFT,
    INTAKE_MODE_SCRATCH,
    INTAKE_MODE_TEMPLATE,
    INTAKE_MODES,
    question_budget,
    resolve_intake_mode,
)


SUPPORTED_LANGUAGES = {"zh", "en", "de", "ms"}


COPY = {
    "en": {
        "conversation_title": "Start with the business decision",
        "conversation_description": (
            "Describe the action this product should improve. AI PM will turn it into "
            "a focused interview and a build-ready requirement."
        ),
        "conversation_question": "What business action should the first release improve?",
        "template_description": (
            "This template is active. Its content guides the interview but remains unconfirmed "
            "until you answer."
        ),
        "template_question": "Which real scenario should this template support first?",
        "draft_description": (
            "The draft is the starting evidence. AI PM will preserve its confirmed facts and ask only about blocking gaps or conflicts."
        ),
        "draft_question": "Upload the draft, then confirm which extracted point is incorrect or still disputed?",
        "department_description": (
            "The expert interview is ready. Start with the first-version decision, owner, "
            "data source, writeback boundary, and acceptance evidence."
        ),
        "fallback_question": "What should the first release help its primary user decide or do?",
        "suggestions": {
            "production": (
                "Production: improve the first-version production action for its owner; "
                "source SQL Server or SAP, with Excel/CSV upload only when manual input is needed."
            ),
            "quality": (
                "Quality: improve the first-version quality action for its owner; "
                "source SQL Server or SAP, with Excel/CSV upload only when manual input is needed."
            ),
            "tdi": (
                "TDI: define the first-version case action, owner, source of truth, "
                "writeback boundary, and closure evidence."
            ),
            "general": (
                "General: define the department, business action, owner, SQL Server/SAP source "
                "or Excel/CSV upload, and acceptance evidence."
            ),
        },
        "generic_suggestions": (
            ("Business outcome", "The first release should improve [business action] for [primary user], measured by [success evidence]."),
            ("Current workflow", "Today [role] completes this through [current steps]; the main delay or risk is [problem]."),
            ("Data source", "The source of truth is [SQL Server or SAP]; [Excel/CSV] is only needed for manual upload."),
        ),
    },
    "zh": {
        "conversation_title": "先说清要改善的业务动作",
        "conversation_description": "描述首版要改善的动作，AI PM 会把它拆成聚焦采访，并逐步形成可交付需求。",
        "conversation_question": "首版首先要改善什么业务动作？",
        "template_description": "模板已启用；它只负责引导采访，在你确认之前不会被当成真实需求。",
        "template_question": "这个模板首先要支持哪个真实场景？",
        "draft_description": "草稿是起始证据；AI PM 会保留其中已明确的事实，只追问阻断交付的缺口或冲突。",
        "draft_question": "请上传草稿，然后确认抽取结果中哪一点不正确或仍有争议？",
        "department_description": "专家采访已就绪，请先确认首版业务动作、负责人、数据源、回写边界和验收证据。",
        "fallback_question": "首版需要帮助主要用户做出什么判断或完成什么动作？",
        "suggestions": {
            "production": "Production：改善首版生产动作及负责人；数据来自 SQL Server 或 SAP，只有需要人工补录时才上传 Excel/CSV。",
            "quality": "Quality：改善首版质量动作及负责人；数据来自 SQL Server 或 SAP，只有需要人工补录时才上传 Excel/CSV。",
            "tdi": "TDI：确认首版 case 动作、负责人、source of truth、回写边界和关闭证据。",
            "general": "General：确认部门、业务动作、负责人、SQL Server/SAP 数据源或 Excel/CSV 上传，以及验收证据。",
        },
        "generic_suggestions": (
            ("业务结果", "首版要为[主要用户]改善[业务动作]，并用[成功证据]衡量。"),
            ("当前流程", "目前由[角色]通过[现有步骤]完成，最大的延迟或风险是[问题]。"),
            ("数据来源", "source of truth 是[SQL Server 或 SAP]；只有人工补录时才使用[Excel/CSV]上传。"),
        ),
    },
    "de": {
        "conversation_title": "Mit der Geschaeftsentscheidung beginnen",
        "conversation_description": (
            "Beschreibe die Aktion, die das Produkt verbessern soll. AI PM macht daraus "
            "ein fokussiertes Interview und eine umsetzbare Anforderung."
        ),
        "conversation_question": "Welche Geschaeftsaktion soll das erste Release verbessern?",
        "template_description": (
            "Diese Vorlage ist aktiv. Sie fuehrt das Interview, gilt aber erst nach deiner Bestaetigung als Anforderung."
        ),
        "template_question": "Welches reale Szenario soll diese Vorlage zuerst abdecken?",
        "draft_description": (
            "Der Draft ist die Ausgangsbasis. AI PM behaelt bestaetigte Fakten und fragt nur nach blockierenden Luecken oder Konflikten."
        ),
        "draft_question": "Lade den Draft hoch: Welcher extrahierte Punkt ist falsch oder noch strittig?",
        "department_description": (
            "Das Experteninterview ist bereit. Starte mit Entscheidung, Owner, Datenquelle, Rueckschreibgrenze und Abnahmenachweis."
        ),
        "fallback_question": "Welche Entscheidung oder Aktion soll das erste Release fuer den Hauptnutzer verbessern?",
        "suggestions": {
            "production": "Production: Aktion und Owner klaeren; Quelle SQL Server oder SAP, Excel/CSV nur fuer manuelle Eingaben.",
            "quality": "Quality: Aktion und Owner klaeren; Quelle SQL Server oder SAP, Excel/CSV nur fuer manuelle Eingaben.",
            "tdi": "TDI: Case-Aktion, Owner, Source of Truth, Rueckschreibgrenze und Abschlussnachweis klaeren.",
            "general": "General: Bereich, Aktion, Owner, SQL Server/SAP oder Excel/CSV Upload und Abnahmenachweis klaeren.",
        },
        "generic_suggestions": (
            ("Geschaeftsergebnis", "Das erste Release verbessert [Aktion] fuer [Hauptnutzer], gemessen durch [Nachweis]."),
            ("Aktueller Ablauf", "Heute erledigt [Rolle] dies ueber [Schritte]; das groesste Risiko ist [Problem]."),
            ("Datenquelle", "Source of Truth ist [SQL Server oder SAP]; [Excel/CSV] nur fuer manuellen Upload."),
        ),
    },
    "ms": {
        "conversation_title": "Mulakan dengan keputusan perniagaan",
        "conversation_description": (
            "Terangkan tindakan yang perlu diperbaiki. AI PM akan menukarnya kepada temu bual fokus dan requirement sedia bina."
        ),
        "conversation_question": "Tindakan perniagaan apa perlu diperbaiki oleh release pertama?",
        "template_description": (
            "Templat ini aktif. Ia membimbing temu bual tetapi belum menjadi requirement sehingga anda mengesahkannya."
        ),
        "template_question": "Senario sebenar mana perlu disokong dahulu?",
        "draft_description": (
            "Draft ialah bukti permulaan. AI PM mengekalkan fakta yang disahkan dan hanya bertanya gap atau konflik yang menghalang delivery."
        ),
        "draft_question": "Muat naik draft: perkara yang diekstrak mana tidak tepat atau masih dipertikaikan?",
        "department_description": (
            "Temu bual pakar sedia. Mulakan dengan tindakan versi pertama, owner, sumber data, sempadan writeback dan bukti penerimaan."
        ),
        "fallback_question": "Apakah keputusan atau tindakan yang perlu dibantu oleh release pertama?",
        "suggestions": {
            "production": "Production: sahkan tindakan dan owner; sumber SQL Server atau SAP, Excel/CSV hanya untuk input manual.",
            "quality": "Quality: sahkan tindakan dan owner; sumber SQL Server atau SAP, Excel/CSV hanya untuk input manual.",
            "tdi": "TDI: sahkan tindakan case, owner, source of truth, sempadan writeback dan bukti penutupan.",
            "general": "General: sahkan jabatan, tindakan, owner, SQL Server/SAP atau muat naik Excel/CSV, dan bukti penerimaan.",
        },
        "generic_suggestions": (
            ("Hasil perniagaan", "Release pertama perlu memperbaiki [tindakan] untuk [pengguna], diukur dengan [bukti]."),
            ("Aliran semasa", "Hari ini [peranan] melakukannya melalui [langkah]; risiko utama ialah [masalah]."),
            ("Sumber data", "Source of truth ialah [SQL Server atau SAP]; [Excel/CSV] hanya untuk muat naik manual."),
        ),
    },
}


def build_session_launch_context(
    *,
    language: str,
    session_title: str,
    applied_template_id: str,
    applied_template_name: str,
    start_function: str,
    has_messages: bool,
    template: dict[str, Any] | None,
    structured_requirement_model: dict[str, Any] | None,
    conversation_chain_state: dict[str, Any] | None,
    intake_mode: str = "",
    business_route: str = "",
    user_turn_count: int = 0,
) -> dict[str, Any]:
    normalized_language = _normalize_language(language)
    copy = COPY[normalized_language]
    template_payload = template if isinstance(template, dict) else {}
    chain = conversation_chain_state if isinstance(conversation_chain_state, dict) else {}
    model = structured_requirement_model if isinstance(structured_requirement_model, dict) else {}

    mode = (
        intake_mode
        if intake_mode in INTAKE_MODES
        else resolve_intake_mode(
            template_id=applied_template_id,
            start_function=start_function,
        )
    )
    chain_active = bool(chain.get("enabled"))

    status = str(chain.get("status", "")).strip()
    if not status:
        status = "in_progress" if has_messages else "not_started"

    title = _launch_title(
        mode=mode,
        session_title=session_title,
        applied_template_name=applied_template_name,
        template=template_payload,
        model=model,
        copy=copy,
    )
    description = _launch_description(mode, template_payload, copy)
    if user_turn_count <= 0:
        question = _initial_question(mode, copy)
    else:
        question = _next_model_question(model)
        if not question and chain_active:
            question = str(chain.get("current_node_label", "")).strip()
        if not question:
            question = str(copy["fallback_question"])
    question = _single_question(question)

    return {
        "version": 2,
        "mode": mode,
        "business_route": business_route,
        "status": status,
        "title": title,
        "description": description,
        "question": question,
        "stages": _launch_stages(model, normalized_language),
        "suggestions": _launch_suggestions(mode, business_route, copy),
        "question_budget": question_budget(user_turn_count),
        "source": _launch_source(
            mode=mode,
            language=normalized_language,
            applied_template_id=applied_template_id,
            applied_template_name=applied_template_name,
            start_function=start_function,
            template=template_payload,
            business_route=business_route,
        ),
    }


def _normalize_language(language: str) -> str:
    normalized = str(language or "").strip().lower().replace("_", "-")
    if normalized.startswith("zh"):
        return "zh"
    return normalized if normalized in SUPPORTED_LANGUAGES else "en"


def _launch_title(
    *,
    mode: str,
    session_title: str,
    applied_template_name: str,
    template: dict[str, Any],
    model: dict[str, Any],
    copy: dict[str, Any],
) -> str:
    if mode == "template":
        return (
            str(template.get("template_name", "")).strip()
            or str(applied_template_name).strip()
            or str(session_title).strip()
            or str(copy["conversation_title"])
        )
    if mode in {INTAKE_MODE_SCRATCH, INTAKE_MODE_DRAFT}:
        product_context = model.get("product_context")
        if isinstance(product_context, dict):
            department = str(product_context.get("requesting_department", "")).strip()
            if department:
                return f"{department} requirement interview"
    return str(session_title).strip() or str(copy["conversation_title"])


def _launch_description(mode: str, template: dict[str, Any], copy: dict[str, Any]) -> str:
    if mode == INTAKE_MODE_TEMPLATE:
        return str(template.get("description", "")).strip() or str(copy["template_description"])
    if mode == INTAKE_MODE_DRAFT:
        return str(copy["draft_description"])
    return str(copy["conversation_description"])


def _launch_stages(model: dict[str, Any], language: str) -> list[dict[str, str]]:
    collection_status = model.get("collection_status")
    if not isinstance(collection_status, dict):
        collection_status = {}
    definitions = (
        ("outcome", ("objective", "users")),
        ("scope_workflow", ("scope", "scenarios", "features")),
        ("rules_data", ("rules", "integrations")),
        ("acceptance", ("acceptance",)),
        ("package", ()),
    )
    labels = _STAGE_LABELS.get(language, _STAGE_LABELS["en"])
    stages: list[dict[str, str]] = []
    first_pending_found = False
    all_requirement_fields_confirmed = all(
        str(collection_status.get(key, {}).get("status", "")).lower() == "confirmed"
        for _, keys in definitions[:-1]
        for key in keys
    )
    for key, fields in definitions:
        complete = (
            all_requirement_fields_confirmed
            if key == "package"
            else bool(fields)
            and all(
                str(collection_status.get(field, {}).get("status", "")).lower() == "confirmed"
                for field in fields
            )
        )
        status = "complete" if complete else "pending"
        if not complete and not first_pending_found:
            status = "current"
            first_pending_found = True
        stages.append(
            {
                "key": key,
                "track": key,
                "label": labels[key],
                "status": status,
            }
        )
    return stages


def _launch_suggestions(
    mode: str,
    business_route: str,
    copy: dict[str, Any],
) -> list[dict[str, str]]:
    if mode != INTAKE_MODE_TEMPLATE and not business_route:
        labels = (
            ("production", "Production"),
            ("quality", "Quality"),
            ("tdi", "TDI"),
        )
        suggestion_copy = copy["suggestions"]
        return [
            {
                "id": key,
                "label": label,
                "text": str(suggestion_copy[key]),
            }
            for key, label in labels
        ]

    return [
        {
            "id": f"starter-{index + 1}",
            "label": str(label),
            "text": str(text),
        }
        for index, (label, text) in enumerate(copy["generic_suggestions"])
    ]


def _launch_source(
    *,
    mode: str,
    language: str,
    applied_template_id: str,
    applied_template_name: str,
    start_function: str,
    template: dict[str, Any],
    business_route: str,
) -> dict[str, str]:
    if mode == INTAKE_MODE_TEMPLATE:
        return {
            "type": "template",
            "id": str(template.get("template_id", "")).strip() or str(applied_template_id).strip(),
            "name": str(template.get("template_name", "")).strip() or str(applied_template_name).strip(),
            "version": str(template.get("version", "")).strip(),
            "language": str(template.get("language", "")).strip() or language,
            "start_function": str(start_function).strip(),
            "business_route": business_route,
        }
    return {
        "type": mode,
        "id": "",
        "name": "",
        "version": "",
        "language": language,
        "start_function": str(start_function).strip(),
        "business_route": business_route,
    }


def _initial_question(mode: str, copy: dict[str, Any]) -> str:
    if mode == INTAKE_MODE_DRAFT:
        return str(copy["draft_question"])
    if mode == INTAKE_MODE_TEMPLATE:
        return str(copy["template_question"])
    return str(copy["conversation_question"])


def _next_model_question(model: dict[str, Any]) -> str:
    collection_status = model.get("collection_status")
    if isinstance(collection_status, dict):
        for key in (
            "objective",
            "users",
            "scope",
            "scenarios",
            "features",
            "rules",
            "integrations",
            "acceptance",
            "pages",
        ):
            item = collection_status.get(key)
            if not isinstance(item, dict):
                continue
            questions = item.get("pending_questions")
            if isinstance(questions, list):
                for question in questions:
                    if str(question).strip():
                        return str(question).strip()
    questions = model.get("open_questions")
    if isinstance(questions, list):
        return next((str(item).strip() for item in questions if str(item).strip()), "")
    return ""


def _single_question(value: str) -> str:
    text = " ".join(str(value or "").split()).replace("？", "?")
    if not text:
        return "What should the first release help its primary user decide or do?"
    text = text.split("?", 1)[0].rstrip(".!;: ")
    return f"{text}?"


_STAGE_LABELS = {
    "en": {
        "outcome": "Outcome & user",
        "scope_workflow": "Scope & workflow",
        "rules_data": "Rules & data",
        "acceptance": "Acceptance",
        "package": "Build brief",
    },
    "zh": {
        "outcome": "结果与用户",
        "scope_workflow": "范围与流程",
        "rules_data": "规则与数据",
        "acceptance": "验收",
        "package": "开发简报",
    },
    "de": {
        "outcome": "Outcome & Nutzer",
        "scope_workflow": "Scope & Workflow",
        "rules_data": "Regeln & Daten",
        "acceptance": "Abnahme",
        "package": "Build Brief",
    },
    "ms": {
        "outcome": "Outcome & pengguna",
        "scope_workflow": "Skop & workflow",
        "rules_data": "Rules & data",
        "acceptance": "Acceptance",
        "package": "Build brief",
    },
}
