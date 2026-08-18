from __future__ import annotations

import re
from typing import Any, Iterable


# Approved IC Substrate data paths. MES and QIS/QMS are legitimate production
# sources alongside SQL Server, SAP, and manual Excel/CSV upload. Acronyms use
# word boundaries so "mes" never matches inside "names" or "sometimes".
_APPROVED_SOURCE_PATTERN = re.compile(
    # The system must be named. A bare "SQL"/"database" is ambiguous (it is just
    # as likely to be MySQL) and must not pass as a confirmed data path.
    r"\bsql\s*server\b|\bsqlserver\b"
    r"|\bsap\b"
    r"|\bmes\b|\bqis\b|\bqms\b"
    r"|\bexcel\b|\bxlsx?\b|\bcsv\b|\bupload\b"
    r"|\bmuat\s+naik\b|\bhochladen\b"
    r"|上传|导入",
    re.IGNORECASE,
)

_UNAPPROVED_SOURCE_PATTERN = re.compile(
    r"\b(?:erp|postgres(?:ql)?|mysql|oracle|mongodb)\b",
    re.IGNORECASE,
)

# Keeps an explicit read/write boundary even when the named source is not an
# approved path. Mirrors interview_state._BOUNDARY_MARKERS so the interview gate
# and the delivery documents agree in all four supported languages.
_BOUNDARY_PATTERN = re.compile(
    r"\b(?:no|without|does not|do not)\b.*\bwrite(?:back|[- ]back)\b"
    r"|\bread[- ]only\b"
    r"|\bwrite(?:back|[- ]back)\b.*\b(?:out of scope|prohibited|disabled)\b"
    r"|只读"
    r"|(?:不|禁止|无|勿)[^。；;，,]{0,16}?回写"
    r"|\bnur lesend\b"
    r"|\bschreibgesch(?:ü|ue)tzt\b"
    r"|\b(?:ohne|kein(?:e[rmns]?)?|nicht)\b[^.;]{0,40}?\w*r(?:ü|ue)ckschreib\w*"
    r"|\bbaca\s+(?:sahaja|saja)\b"
    r"|\b(?:tanpa|tiada|tidak)\b[^.;]{0,40}?\btulis\s+balik\b",
    re.IGNORECASE,
)

# A request to write into a source system. Only meaningful when the same line
# does not already assert a read-only boundary.
_WRITEBACK_PATTERN = re.compile(
    r"\bwriteback\b|\bwrite\s*-?\s*back\b|\bwrite\b[^.;]{0,40}?\bback\b"
    r"|回写|写回"
    r"|\w*r(?:ü|ue)ckschreib\w*"
    r"|\btulis\s+balik\b",
    re.IGNORECASE,
)

# The business action performed by the writeback. "Writeback is allowed" names
# no action and therefore stays pending.
_WRITEBACK_ACTION_PATTERN = re.compile(
    r"\b(?:post|posting|posted|update|updating|insert|upsert|create|creating|"
    r"release|releasing|approve|approval|reject|close|closing|cancel|sync|"
    r"synchronize|flag|set|record|recording|log|logging|save|saving|store|"
    r"storing|submit|submitting|mark|marking|write|writing|publish|transfer|"
    r"attach|append|assign)\b"
    r"|过账|更新|写入|写回|回填|创建|放行|审批|关闭|取消|同步|登记|标记|提交|"
    r"记录|保存|上报|存入|录入|归档|指派"
    r"|\b(?:buchen|aktualisieren|freigeben|anlegen|schlie(?:ß|ss)en|"
    r"synchronisieren|markieren|eintragen|speichern|erfassen|uebertragen|"
    r"übertragen|hinterlegen|zuweisen)\b"
    r"|\b(?:pos|kemas\s+kini|luluskan|cipta|tutup|segerak|tanda|rekod|simpan|"
    r"hantar|catat|kemaskini|tugaskan)\b",
    re.IGNORECASE,
)

# Observable, checkable evidence. Shared with the interview acceptance gate so
# "the writeback works" never counts as acceptance evidence.
OBSERVABLE_EVIDENCE_PATTERN = re.compile(
    r"(?:\d+(?:[.,]\d+)?\s*(?:%|minutes?|hours?|days?|分钟|小时|天)?)"
    r"|(?:<=|>=|<|>|=)"
    r"|\b(?:can|must|shows?|displays?|appears?|exports?|identif(?:y|ies)|"
    r"records?|rejects?|prevents?|within|given|when|then|visible)\b"
    r"|(?:可以|能够|必须|显示|出现|导出|识别|记录|拒绝|阻止|以内|可见|当.+时)"
    r"|\b(?:kann|muss|zeigt|erscheint|exportiert|erkennt|zeichnet auf|"
    r"verhindert|innerhalb|sichtbar)\b"
    r"|\b(?:boleh|mesti|memaparkan|muncul|eksport|mengenal pasti|merekod|"
    r"menolak|menghalang|dalam masa|kelihatan)\b",
    re.IGNORECASE,
)

# Data-detail vocabulary. A dependency line that names no source still belongs in
# the delivery documents when it carries a real integration detail: an artifact,
# a key/field mapping, or a refresh cadence. Anything else is a stray note.
SOURCE_ARTIFACT_PATTERN = re.compile(
    r"\b(?:table|view|api|endpoint|file|dataset|object|topic|queue)\b"
    r"|(?:表|视图|接口|端点|文件|数据集|对象|主题|队列)"
    r"|\b(?:tabelle|ansicht|datei|datensatz|objekt|warteschlange)\b"
    r"|\b(?:jadual|paparan|fail|set data|objek|baris gilir)\b",
    re.IGNORECASE,
)
KEY_FIELD_PATTERN = re.compile(
    r"\b(?:key|keys|field|fields|column|columns|identifier|identifiers|join)\b"
    r"|(?:主键|业务键|字段|列|关联|连接键|标识)"
    r"|\b(?:schluessel|feld|felder|spalte|spalten|kennung|verknuepfung)\b"
    r"|\b(?:kunci|medan|lajur|pengecam|gabung)\b",
    re.IGNORECASE,
)
CADENCE_PATTERN = re.compile(
    r"\b(?:real[- ]?time|near[- ]?real[- ]?time|refresh|every\s+\d+|"
    r"hourly|daily|weekly|batch|schedule|frequency|cadence)\b"
    r"|(?:实时|准实时|刷新|每\s*\d+|每小时|每天|每周|批次|频率|周期)"
    r"|\b(?:echtzeit|aktualisierung|stuendlich|taeglich|woechentlich|"
    r"stapel|zeitplan|frequenz)\b"
    r"|\b(?:masa nyata|segar semula|setiap\s+\d+|setiap jam|harian|"
    r"mingguan|kelompok|jadual|kekerapan)\b",
    re.IGNORECASE,
)

# A measurable or system-anchored claim. Keeps "shows it" out of a production
# writeback authorization.
_EVIDENCE_ANCHOR_PATTERN = re.compile(
    r"\d+(?:[.,]\d+)?\s*(?:%|percent|seconds?|minutes?|mins?|hours?|days?|"
    r"分钟|小时|天|秒|sekunden|minuten|stunden|tage|saat|minit|jam|hari)",
    re.IGNORECASE,
)

_MINIMUM_EVIDENCE_TOKENS = 4


def _content_token_count(value: str) -> int:
    """Rough word count that works for latin scripts and CJK alike."""

    text = str(value or "")
    latin = len(re.findall(r"[A-Za-z0-9_]+", text))
    cjk = len(re.findall(r"[㐀-鿿]", text))
    return latin + cjk // 2


def _is_specific_writeback_action(value: str) -> bool:
    return bool(
        _WRITEBACK_ACTION_PATTERN.search(value)
        and _content_token_count(value) >= _MINIMUM_EVIDENCE_TOKENS
    )


def _is_observable_writeback_evidence(value: str) -> bool:
    anchored = bool(
        _EVIDENCE_ANCHOR_PATTERN.search(value)
        or _APPROVED_SOURCE_PATTERN.search(value)
        or SOURCE_ARTIFACT_PATTERN.search(value)
    )
    return bool(
        OBSERVABLE_EVIDENCE_PATTERN.search(value)
        and anchored
        and _content_token_count(value) >= _MINIMUM_EVIDENCE_TOKENS
    )


WRITEBACK_AUTHORIZATION_FIELDS = (
    "target_system",
    "action",
    "authorization_owner",
    "acceptance_evidence",
)

_SOURCE_TYPE_PATTERNS = (
    ("sql_server", re.compile(r"\bsql\s*server\b|\bsqlserver\b", re.IGNORECASE)),
    ("sap", re.compile(r"\bsap\b", re.IGNORECASE)),
    ("mes", re.compile(r"\bmes\b", re.IGNORECASE)),
    ("qis", re.compile(r"\bqis\b", re.IGNORECASE)),
    ("qms", re.compile(r"\bqms\b", re.IGNORECASE)),
    (
        "file_upload",
        re.compile(
            r"\bexcel\b|\bxlsx?\b|\bcsv\b|\bupload\b|\bmuat\s+naik\b"
            r"|\bhochladen\b|上传|导入",
            re.IGNORECASE,
        ),
    ),
)

_UNCONFIRMED_SOURCE_COPY = {
    "en": "Unconfirmed data source; choose SQL Server, SAP, MES, QIS/QMS, or Excel/CSV upload before implementation.",
    "zh": "数据来源待确认；实施前须选择 SQL Server、SAP、MES、QIS/QMS 或手动上传 Excel/CSV。",
    "de": "Datenquelle unbestaetigt; vor der Implementierung SQL Server, SAP, MES, QIS/QMS oder Excel/CSV-Upload waehlen.",
    "ms": "Sumber data belum disahkan; pilih SQL Server, SAP, MES, QIS/QMS atau upload Excel/CSV sebelum pelaksanaan.",
}

_PENDING_WRITEBACK_COPY = {
    "en": "Writeback not authorized; confirm target system, writeback action, business owner, and acceptance evidence before implementing it.",
    "zh": "写回尚未授权；实施前须确认目标系统、写回动作、业务负责人和可验证验收证据。",
    "de": "Rueckschreiben nicht freigegeben; vor der Umsetzung Zielsystem, Schreibaktion, Business Owner und Abnahmenachweis bestaetigen.",
    "ms": "Tulis balik belum dibenarkan; sahkan sistem sasaran, tindakan tulis balik, business owner dan bukti penerimaan sebelum melaksanakannya.",
}


def normalize_writeback_authorization(value: Any) -> dict[str, Any]:
    """Normalize the writeback authorization block and derive its status.

    The status is always recomputed from the evidence fields, so neither the
    client nor the extraction model can declare a writeback authorized. A model
    without the block normalizes to pending, which fails closed.
    """

    record = value if isinstance(value, dict) else {}
    fields = {
        key: str(record.get(key) or "").strip()
        for key in WRITEBACK_AUTHORIZATION_FIELDS
    }
    target = fields["target_system"]
    authorized = bool(
        target
        and _APPROVED_SOURCE_PATTERN.search(target)
        and not _UNAPPROVED_SOURCE_PATTERN.search(target)
        and _is_specific_writeback_action(fields["action"])
        and fields["authorization_owner"]
        and _is_observable_writeback_evidence(fields["acceptance_evidence"])
    )
    return {**fields, "status": "authorized" if authorized else "pending"}


def writeback_is_authorized(model: Any) -> bool:
    """Effective authorization: a valid block that still matches the target."""

    record = model if isinstance(model, dict) else {}
    return classify_data_paths(
        record.get("data_and_dependencies") or (),
        writeback_authorization=record.get("writeback_authorization"),
    )["writeback_authorized"]


def classify_data_paths(
    values: Iterable[Any],
    *,
    writeback_authorization: Any = None,
) -> dict[str, Any]:
    """Classify data dependencies against the approved data-path policy.

    Single source of truth: the interview gate and the delivery documents both
    read this result, so one answer can never be confirmed in one layer and
    rejected in the other.
    """

    authorization = normalize_writeback_authorization(writeback_authorization)
    writeback_target_types: set[str] = set()
    entries: list[tuple[str, str]] = []
    has_approved_source = False
    has_forbidden_source = False
    has_read_boundary = False
    writeback_requested = False

    for value in values:
        text = str(value or "").strip()
        if not text:
            continue
        if _UNAPPROVED_SOURCE_PATTERN.search(text):
            # Names a system outside the approved paths: never reaches delivery
            # documents and blocks confirmation.
            has_forbidden_source = True
            entries.append((text, "forbidden"))
            continue

        names_source = bool(_APPROVED_SOURCE_PATTERN.search(text))
        asserts_boundary = bool(_BOUNDARY_PATTERN.search(text))
        requests_writeback = bool(
            _WRITEBACK_PATTERN.search(text)
        ) and not asserts_boundary

        if not (names_source or asserts_boundary or requests_writeback):
            carries_detail = bool(
                SOURCE_ARTIFACT_PATTERN.search(text)
                or KEY_FIELD_PATTERN.search(text)
                or CADENCE_PATTERN.search(text)
            )
            # A real integration detail (artifact, key/field mapping, cadence)
            # rides along with a named source. A stray note never does.
            entries.append((text, "detail" if carries_detail else "stray"))
            continue

        has_approved_source = has_approved_source or names_source
        has_read_boundary = has_read_boundary or asserts_boundary
        if requests_writeback:
            writeback_requested = True
            writeback_target_types.update(referenced_source_types([text]))
        entries.append((text, "signal"))

    # Detail lines are carried into the delivery documents as soon as the set
    # names a legitimate source; on their own they leave the source unnamed.
    keep_details = has_approved_source
    approved: list[str] = []
    has_unnamed_source = False
    for text, kind in entries:
        if kind == "forbidden":
            continue
        if kind == "stray":
            continue
        if kind == "detail" and not keep_details:
            has_unnamed_source = True
            continue
        if text not in approved:
            approved.append(text)

    # The authorization only counts for the system it actually named, so an
    # authorization left over from an earlier target cannot unlock a new one.
    authorized_types = set(
        referenced_source_types([authorization["target_system"]])
    )
    writeback_authorized = bool(
        writeback_requested
        and authorization["status"] == "authorized"
        and authorized_types
        and authorized_types & writeback_target_types
    )
    return {
        "approved": approved,
        "has_approved_source": has_approved_source,
        "has_forbidden_source": has_forbidden_source,
        # Dependencies that never name an approved system stay unconfirmed, so
        # the documents flag them instead of reading as a clean brief.
        "has_unapproved_source": bool(
            has_forbidden_source
            or has_unnamed_source
            or (entries and not has_approved_source)
        ),
        "has_read_boundary": has_read_boundary,
        "writeback_requested": writeback_requested,
        "writeback_target_types": sorted(writeback_target_types),
        "writeback_authorization": authorization,
        "writeback_authorized": writeback_authorized,
        "pending_writeback": writeback_requested and not writeback_authorized,
    }


def sanitize_data_dependencies(
    values: Iterable[Any],
    *,
    language: str = "en",
    writeback_authorization: Any = None,
) -> list[str]:
    classification = classify_data_paths(
        values,
        writeback_authorization=writeback_authorization,
    )
    approved = list(classification["approved"])
    if classification["has_unapproved_source"]:
        approved.append(
            _UNCONFIRMED_SOURCE_COPY.get(language, _UNCONFIRMED_SOURCE_COPY["en"])
        )
    if classification["pending_writeback"]:
        approved.append(
            _PENDING_WRITEBACK_COPY.get(language, _PENDING_WRITEBACK_COPY["en"])
        )
    return approved


def data_boundary_is_confirmed(
    values: Iterable[Any],
    *,
    writeback_authorization: Any = None,
) -> bool:
    """Whether the data boundary may be treated as confirmed.

    The first release defaults to read-only: a writeback only counts once its
    own authorization block names the target system, the writeback action, an
    accountable owner, and observable acceptance evidence.
    """

    classification = classify_data_paths(
        values,
        writeback_authorization=writeback_authorization,
    )
    return bool(
        classification["has_approved_source"]
        and not classification["has_forbidden_source"]
        and not classification["pending_writeback"]
        and (
            classification["has_read_boundary"]
            or classification["writeback_authorized"]
        )
    )


def is_specific_writeback_action(value: Any) -> bool:
    return _is_specific_writeback_action(str(value or ""))


def is_observable_writeback_evidence(value: Any) -> bool:
    return _is_observable_writeback_evidence(str(value or ""))


def first_approved_source(value: Any) -> str:
    """The approved system named in the text, in its own words."""

    text = str(value or "")
    if _UNAPPROVED_SOURCE_PATTERN.search(text):
        return ""
    match = _APPROVED_SOURCE_PATTERN.search(text)
    return match.group(0).strip() if match else ""


def line_requests_writeback(value: Any) -> bool:
    """Whether one dependency line asks to write into a source system."""

    text = str(value or "")
    return bool(
        _WRITEBACK_PATTERN.search(text) and not _BOUNDARY_PATTERN.search(text)
    )


def asserts_read_boundary(value: Any) -> bool:
    return bool(_BOUNDARY_PATTERN.search(str(value or "")))


def referenced_source_types(values: Iterable[Any]) -> list[str]:
    combined = " ".join(str(value or "") for value in values)
    return [
        source_type
        for source_type, pattern in _SOURCE_TYPE_PATTERNS
        if pattern.search(combined)
    ]
