from __future__ import annotations

import re
from typing import Any, Callable

from .data_source_policy import (
    CADENCE_PATTERN,
    KEY_FIELD_PATTERN,
    OBSERVABLE_EVIDENCE_PATTERN,
    SOURCE_ARTIFACT_PATTERN,
    classify_data_paths,
    data_boundary_is_confirmed,
    writeback_is_authorized,
)


FAST_DECISION_IDS = (
    "outcome",
    "actor_action",
    "v1_flow",
    "data_boundary",
    "acceptance",
)

STRICT_REVIEW_KEYS = (
    "objective",
    "scope",
    "users",
    "scenarios",
    "features",
    "rules",
    "integrations",
    "acceptance",
    "ownership",
)

_DOCUMENT_STATUSES = {"missing", "current", "stale"}

_LANGUAGE_ALIASES = {
    "en": "en",
    "en-us": "en",
    "english": "en",
    "de": "de",
    "de-de": "de",
    "deutsch": "de",
    "german": "de",
    "zh": "zh",
    "zh-cn": "zh",
    "zh-hans": "zh",
    "中文": "zh",
    "chinese": "zh",
    "ms": "ms",
    "ms-my": "ms",
    "bahasa melayu": "ms",
    "malay": "ms",
}

_QUESTION_COPY: dict[str, dict[str, tuple[str, str, str]]] = {
    "en": {
        "outcome": (
            "Measurable business outcome",
            "What measurable business result should the first release improve?",
            "For example: reduce false-fail e-test escapes by 15% next quarter.",
        ),
        "actor_action": (
            "User and business action",
            "Who will use it, and what decision will they make with it?",
            "For example: a shift supervisor schedules retests from yield trends by product code.",
        ),
        "v1_flow": (
            "First-release scenario and scope",
            "Which core scenario must the first release support, and what is in or out of scope?",
            "For example: filter yield trends and select lots for retest; automated disposition is out of scope.",
        ),
        "data_boundary": (
            "Data source and read/write boundary",
            "Where does the data come from, and is the first release read-only or allowed to write back?",
            "For example: read e-test results from SQL Server with no production writeback.",
        ),
        "writeback": (
            "Writeback authorization",
            "Which system will the first release write into, what does it write, who authorizes it, and what proves it worked?",
            "Name all four, or keep the first release read-only.",
        ),
        "acceptance": (
            "Observable acceptance evidence",
            "What observable result will prove that the first release passes acceptance?",
            "For example: the supervisor can identify the top loss code for a selected product.",
        ),
        "rules": (
            "Business rules",
            "Which formulas, thresholds, or workflow rules must the solution follow?",
            "For example: yield must use the Quality-approved finished-lot formula.",
        ),
        "ownership": (
            "Business and acceptance ownership",
            "Who owns the business result, and who signs off acceptance?",
            "Name both roles; they may be the same person.",
        ),
    },
    "de": {
        "outcome": (
            "Messbares Geschäftsergebnis",
            "Welches messbare Geschäftsergebnis soll die erste Version verbessern?",
            "Zum Beispiel: die Zahl falsch-negativer E-Test-Ausreißer im nächsten Quartal um 15 % senken.",
        ),
        "actor_action": (
            "Nutzer und Geschäftsentscheidung",
            "Wer nutzt die Lösung und welche Entscheidung trifft diese Person damit?",
            "Zum Beispiel: Die Schichtleitung plant Nachtests anhand der Ausbeute je Produktcode.",
        ),
        "v1_flow": (
            "Kernszenario und Umfang der ersten Version",
            "Welches Kernszenario muss die erste Version unterstützen und was gehört dazu oder nicht dazu?",
            "Zum Beispiel: Ausbeutetrends filtern und Lose für Nachtests auswählen; automatische Disposition ist ausgeschlossen.",
        ),
        "data_boundary": (
            "Datenquelle und Schreibgrenze",
            "Woher kommen die Daten und ist die erste Version nur lesend oder darf sie zurückschreiben?",
            "Zum Beispiel: E-Test-Ergebnisse nur lesend aus SQL Server, ohne Produktionsrückschreiben.",
        ),
        "writeback": (
            "Freigabe für Rückschreiben",
            "In welches System schreibt die erste Version, was schreibt sie, wer gibt es frei und woran ist der Erfolg erkennbar?",
            "Alle vier nennen oder die erste Version nur lesend halten.",
        ),
        "acceptance": (
            "Beobachtbarer Abnahmenachweis",
            "Welches beobachtbare Ergebnis belegt die erfolgreiche Abnahme der ersten Version?",
            "Zum Beispiel: Die Schichtleitung erkennt den häufigsten Verlustcode je Produkt.",
        ),
        "rules": (
            "Geschäftsregeln",
            "Welche Formeln, Grenzwerte oder Prozessregeln muss die Lösung einhalten?",
            "Zum Beispiel: Die Ausbeute nutzt die von Quality freigegebene Formel.",
        ),
        "ownership": (
            "Geschäfts- und Abnahmeverantwortung",
            "Wer verantwortet das Geschäftsergebnis und wer nimmt die Lösung ab?",
            "Beide Rollen benennen; dieselbe Person kann beide übernehmen.",
        ),
    },
    "zh": {
        "outcome": (
            "可衡量的业务结果",
            "首版要改善什么可衡量的业务结果？",
            "例如：下季度将电测误判漏出率降低 15%。",
        ),
        "actor_action": (
            "用户与业务动作",
            "谁会使用它，并据此做什么决定？",
            "例如：值班主管根据产品代码良率趋势安排复测。",
        ),
        "v1_flow": (
            "首版场景与范围",
            "首版必须支持哪个核心场景，包含和不包含什么？",
            "例如：筛选良率趋势并选择复测批次；不包含自动处置。",
        ),
        "data_boundary": (
            "数据来源与读写边界",
            "数据来自哪里，首版是只读还是允许回写？",
            "例如：只读获取 SQL Server 电测结果，不向生产系统回写。",
        ),
        "writeback": (
            "写回授权",
            "首版要写入哪个系统、写入什么、谁授权，以及看到什么可以验证成功？",
            "请一次说明这四项，或保持首版只读。",
        ),
        "acceptance": (
            "可观察的验收证据",
            "看到什么结果可以判定首版验收通过？",
            "例如：值班主管能找到所选产品代码的首要损失原因。",
        ),
        "rules": (
            "业务规则",
            "方案必须遵守哪些公式、阈值或流程规则？",
            "例如：良率必须使用质量部门批准的成品批次公式。",
        ),
        "ownership": (
            "业务与验收负责人",
            "谁对业务结果负责，谁负责验收签字？",
            "请分别明确两个角色；可以由同一人承担。",
        ),
    },
    "ms": {
        "outcome": (
            "Hasil perniagaan yang boleh diukur",
            "Apakah hasil perniagaan yang boleh diukur yang perlu ditambah baik oleh keluaran pertama?",
            "Contoh: kurangkan pelepasan e-test gagal palsu sebanyak 15% pada suku tahun hadapan.",
        ),
        "actor_action": (
            "Pengguna dan tindakan perniagaan",
            "Siapakah yang akan menggunakannya, dan apakah keputusan yang akan dibuat?",
            "Contoh: penyelia syif menjadualkan ujian semula berdasarkan trend hasil mengikut kod produk.",
        ),
        "v1_flow": (
            "Senario dan skop keluaran pertama",
            "Apakah senario teras yang mesti disokong, dan apakah yang termasuk atau tidak termasuk dalam skop?",
            "Contoh: tapis trend hasil dan pilih lot untuk ujian semula; pelupusan automatik tidak termasuk.",
        ),
        "data_boundary": (
            "Sumber data dan sempadan baca/tulis",
            "Dari manakah data diperoleh, dan adakah keluaran pertama baca sahaja atau boleh menulis semula?",
            "Contoh: baca keputusan e-test daripada SQL Server tanpa tulis balik ke sistem pengeluaran.",
        ),
        "writeback": (
            "Kebenaran tulis balik",
            "Sistem mana yang akan ditulis oleh keluaran pertama, apa yang ditulis, siapa yang membenarkan, dan apa buktinya berjaya?",
            "Nyatakan keempat-empatnya, atau kekalkan keluaran pertama baca sahaja.",
        ),
        "acceptance": (
            "Bukti penerimaan yang boleh diperhatikan",
            "Apakah hasil yang boleh diperhatikan yang membuktikan keluaran pertama lulus penerimaan?",
            "Contoh: penyelia boleh mengenal pasti kod kehilangan utama bagi produk yang dipilih.",
        ),
        "rules": (
            "Peraturan perniagaan",
            "Apakah formula, ambang, atau peraturan aliran kerja yang mesti dipatuhi?",
            "Contoh: hasil mesti menggunakan formula lot siap yang diluluskan oleh Quality.",
        ),
        "ownership": (
            "Pemilikan perniagaan dan penerimaan",
            "Siapakah pemilik hasil perniagaan, dan siapakah yang meluluskan penerimaan?",
            "Nyatakan kedua-dua peranan; orang yang sama boleh memegang kedua-duanya.",
        ),
    },
}

_STRICT_COPY_KEY = {
    "objective": "outcome",
    "scope": "v1_flow",
    "users": "actor_action",
    "scenarios": "v1_flow",
    "features": "v1_flow",
    "rules": "rules",
    "integrations": "data_boundary",
    "acceptance": "acceptance",
    "ownership": "ownership",
}

_GENERAL_ANSWER_OPTIONS: dict[str, dict[str, tuple[str, str, str]]] = {
    "en": {
        "outcome": (
            "Reduce exception-handling time by 30% within the next quarter.",
            "Reduce the relevant defect or error rate by 15% within the next quarter.",
            "Increase on-time completion of the target work to at least 95%.",
        ),
        "actor_action": (
            "The team lead uses the latest status and exceptions to decide the next action.",
            "The process owner uses trends and priorities to allocate people and follow-up work.",
            "The frontline specialist uses a worklist to decide which item to handle first.",
        ),
        "v1_flow": (
            "Show the current status, allow filtering, and open item details; automated execution is out of scope.",
            "Provide an exception worklist, assignment, and closure tracking; upstream process changes are out of scope.",
            "Provide trend analysis and export; forecasting and automated decisions are out of scope.",
        ),
        "data_boundary": (
            "Read from SQL Server and keep the first release read-only with no source-system writeback.",
            "Read approved data from SAP and keep the first release read-only.",
            "Start with user-uploaded Excel or CSV files and do not write back to production systems.",
            "Read lot and defect records from MES or QIS/QMS and keep the first release read-only.",
        ),
        "writeback": (
            "Write back to MES: post the QA disposition to the lot record, authorized by the Quality manager; MES shows the posted disposition within 5 minutes.",
            "Write back to SAP: update the inspection status on the order, authorized by the Quality manager; SAP shows the updated status within 10 minutes.",
            "Keep the first release read-only; no writeback to any source system.",
        ),
        "acceptance": (
            "The primary user can find the highest-priority exception and its evidence within five minutes.",
            "The primary user can filter, inspect, and export the required result without manual data merging.",
            "The primary user can complete the target decision from one page using current data.",
        ),
        "rules": (
            "Use the currently approved business formula and threshold; do not introduce a new calculation.",
            "Flag exceptions when the approved threshold is breached and retain the evidence used.",
            "Keep manual approval for final decisions; the first release only recommends or highlights.",
        ),
        "ownership": (
            "The department manager owns the business result; the process owner signs off acceptance.",
            "The process owner owns both the business result and acceptance.",
            "The department head owns the result; the key-user representative signs off acceptance.",
        ),
    },
    "zh": {
        "outcome": (
            "下季度将异常处理时长缩短 30%。",
            "下季度将相关缺陷率或错误率降低 15%。",
            "将目标工作的按时完成率提升到 95% 以上。",
        ),
        "actor_action": (
            "团队负责人根据最新状态和异常决定下一步处理动作。",
            "流程负责人根据趋势和优先级安排人员及跟进任务。",
            "一线专员根据待办清单决定优先处理哪一项。",
        ),
        "v1_flow": (
            "首版展示当前状态、支持筛选并查看详情；不包含自动执行。",
            "首版提供异常清单、任务分派和关闭追踪；不改造上游流程。",
            "首版提供趋势分析和导出；不包含预测和自动决策。",
        ),
        "data_boundary": (
            "从 SQL Server 读取数据，首版只读，不向源系统回写。",
            "读取 SAP 中已批准的数据，首版保持只读。",
            "先由用户上传 Excel 或 CSV，首版不向生产系统回写。",
            "从 MES 或 QIS/QMS 读取批次与缺陷记录，首版保持只读。",
        ),
        "writeback": (
            "回写 MES：把 QA 判定登记到批次记录，由质量经理授权；MES 中 5 分钟内可以看到已写入的判定。",
            "回写 SAP：更新工单的检验状态，由质量经理授权；SAP 中 10 分钟内可以看到更新后的状态。",
            "保持首版只读，不向任何源系统回写。",
        ),
        "acceptance": (
            "主要用户能在 5 分钟内找到最高优先级异常及其证据。",
            "主要用户无需手工合并数据即可完成筛选、查看和导出。",
            "主要用户能在一个页面内基于最新数据完成目标决策。",
        ),
        "rules": (
            "沿用当前已批准的业务公式和阈值，不新增计算口径。",
            "超过已批准阈值时标记异常，并保留所用证据。",
            "最终决定保留人工审批；首版只做推荐或高亮提示。",
        ),
        "ownership": (
            "部门经理对业务结果负责，流程负责人负责验收签字。",
            "流程负责人同时对业务结果和验收负责。",
            "部门负责人对结果负责，关键用户代表负责验收签字。",
        ),
    },
    "de": {
        "outcome": (
            "Die Bearbeitungszeit für Ausnahmen im nächsten Quartal um 30 % senken.",
            "Die relevante Fehlerquote im nächsten Quartal um 15 % senken.",
            "Die termingerechte Erledigung der Zielarbeit auf mindestens 95 % erhöhen.",
        ),
        "actor_action": (
            "Die Teamleitung entscheidet anhand von Status und Ausnahmen über die nächste Aktion.",
            "Der Prozesseigner plant anhand von Trends und Prioritäten Personal und Folgearbeit.",
            "Der Fachexperte entscheidet anhand einer Arbeitsliste, was zuerst bearbeitet wird.",
        ),
        "v1_flow": (
            "Status, Filter und Details anzeigen; automatische Ausführung ist nicht im Umfang.",
            "Ausnahmeliste, Zuweisung und Abschlussverfolgung; keine Änderung des Quellprozesses.",
            "Trendanalyse und Export; keine Prognose oder automatische Entscheidung.",
        ),
        "data_boundary": (
            "Daten nur lesend aus SQL Server, ohne Rückschreiben ins Quellsystem.",
            "Freigegebene Daten nur lesend aus SAP.",
            "Start mit Excel- oder CSV-Upload, ohne Rückschreiben in Produktionssysteme.",
            "Los- und Fehlerdaten nur lesend aus MES oder QIS/QMS.",
        ),
        "writeback": (
            "Rückschreiben nach MES: die QA-Entscheidung im Los-Datensatz buchen, freigegeben von der Quality-Leitung; MES zeigt die gebuchte Entscheidung innerhalb von 5 Minuten.",
            "Rückschreiben nach SAP: den Prüfstatus im Auftrag aktualisieren, freigegeben von der Quality-Leitung; SAP zeigt den Status innerhalb von 10 Minuten.",
            "Die erste Version nur lesend halten; kein Rückschreiben in Quellsysteme.",
        ),
        "acceptance": (
            "Der Hauptnutzer findet die wichtigste Ausnahme samt Nachweis innerhalb von fünf Minuten.",
            "Der Hauptnutzer kann filtern, prüfen und exportieren, ohne Daten manuell zusammenzuführen.",
            "Der Hauptnutzer kann die Zielentscheidung auf einer Seite mit aktuellen Daten treffen.",
        ),
        "rules": (
            "Die aktuell freigegebene Formel und Schwelle verwenden; keine neue Berechnung einführen.",
            "Ausnahmen bei Überschreitung der freigegebenen Schwelle markieren und Nachweise speichern.",
            "Die endgültige Entscheidung bleibt manuell; die erste Version empfiehlt oder markiert nur.",
        ),
        "ownership": (
            "Die Abteilungsleitung verantwortet das Ergebnis; der Prozesseigner nimmt ab.",
            "Der Prozesseigner verantwortet Ergebnis und Abnahme.",
            "Die Bereichsleitung verantwortet das Ergebnis; der Key User nimmt ab.",
        ),
    },
    "ms": {
        "outcome": (
            "Kurangkan masa pengendalian pengecualian sebanyak 30% pada suku tahun hadapan.",
            "Kurangkan kadar kecacatan atau ralat berkaitan sebanyak 15% pada suku tahun hadapan.",
            "Tingkatkan penyelesaian kerja tepat masa kepada sekurang-kurangnya 95%.",
        ),
        "actor_action": (
            "Ketua pasukan menggunakan status dan pengecualian terkini untuk menentukan tindakan seterusnya.",
            "Pemilik proses menggunakan trend dan keutamaan untuk mengagihkan orang dan kerja susulan.",
            "Pakar barisan hadapan menggunakan senarai kerja untuk menentukan item yang perlu didahulukan.",
        ),
        "v1_flow": (
            "Paparkan status, penapis dan butiran; pelaksanaan automatik di luar skop.",
            "Sediakan senarai pengecualian, tugasan dan penjejakan penutupan; tiada perubahan proses sumber.",
            "Sediakan analisis trend dan eksport; ramalan dan keputusan automatik di luar skop.",
        ),
        "data_boundary": (
            "Baca daripada SQL Server sahaja tanpa tulis balik ke sistem sumber.",
            "Baca data yang diluluskan daripada SAP sahaja.",
            "Mulakan dengan muat naik Excel atau CSV tanpa tulis balik ke sistem pengeluaran.",
            "Baca rekod lot dan kecacatan daripada MES atau QIS/QMS sahaja.",
        ),
        "writeback": (
            "Tulis balik ke MES: pos keputusan QA ke rekod lot, diluluskan oleh Quality manager; MES memaparkan keputusan dalam masa 5 minit.",
            "Tulis balik ke SAP: kemas kini status pemeriksaan pada pesanan, diluluskan oleh Quality manager; SAP memaparkan status dalam masa 10 minit.",
            "Kekalkan keluaran pertama baca sahaja; tiada tulis balik ke sistem sumber.",
        ),
        "acceptance": (
            "Pengguna utama boleh mencari pengecualian keutamaan tertinggi dan buktinya dalam lima minit.",
            "Pengguna utama boleh menapis, menyemak dan mengeksport tanpa menggabungkan data secara manual.",
            "Pengguna utama boleh membuat keputusan sasaran pada satu halaman menggunakan data terkini.",
        ),
        "rules": (
            "Gunakan formula dan ambang perniagaan yang diluluskan tanpa pengiraan baharu.",
            "Tandakan pengecualian apabila ambang dilanggar dan simpan bukti yang digunakan.",
            "Kekalkan kelulusan manual untuk keputusan akhir; keluaran pertama hanya mencadangkan atau menonjolkan.",
        ),
        "ownership": (
            "Pengurus jabatan memiliki hasil perniagaan; pemilik proses meluluskan penerimaan.",
            "Pemilik proses memiliki hasil perniagaan dan penerimaan.",
            "Ketua jabatan memiliki hasil; wakil pengguna utama meluluskan penerimaan.",
        ),
    },
}

_STRICT_REVIEW_ANSWER_OPTIONS: dict[
    str,
    dict[str, tuple[str, str, str]],
] = {
    "en": {
        "scope": (
            "Allow quick ranges for the last 7, 30, or 90 days plus a custom date range.",
            "Fix the first release to the latest 30 days and make the range configurable later.",
            "Use the source system's current time range and add no new date filter in the first release.",
        ),
        "rules": (
            "All users are read-only; only managers may export, and the first release never writes back.",
            "Use role-based access for frontline users and managers, with every export recorded.",
            "Keep the source system's existing permissions and add no new approval workflow.",
        ),
        "integrations": (
            "Use a read-only SQL Server view keyed by lot ID and refresh it every five minutes.",
            "Use an approved SAP table or API with named key fields and a daily refresh.",
            "Use a controlled Excel or CSV template, validate required fields, and reject invalid rows.",
        ),
        "ownership": (
            "The department manager owns the business result; the process owner signs off acceptance.",
            "The process owner owns both the business result and acceptance.",
            "The department head owns the result; a key-user representative signs off acceptance.",
        ),
    },
    "zh": {
        "scope": (
            "首版支持最近 7、30、90 天快捷切换，并允许自定义日期范围。",
            "首版固定展示最近 30 天，后续再开放时间范围配置。",
            "首版沿用源系统现有时间范围，不新增日期筛选。",
        ),
        "rules": (
            "所有用户只读；仅经理可导出；首版不向源系统回写。",
            "一线用户与经理按角色控制查看和导出权限，并记录导出日志。",
            "沿用源系统现有权限，首版不新增审批流程。",
        ),
        "integrations": (
            "使用 SQL Server 只读视图，以批次号为主键，每 5 分钟刷新。",
            "使用已批准的 SAP 表或 API，明确关键字段，每天刷新。",
            "使用受控 Excel/CSV 模板，校验必填字段并拒绝无效行。",
        ),
        "ownership": (
            "部门经理负责业务结果，流程负责人负责验收签字。",
            "流程负责人同时负责业务结果和验收。",
            "部门负责人负责业务结果，关键用户代表负责验收签字。",
        ),
    },
    "de": {
        "scope": (
            "Schnellfilter für 7, 30 oder 90 Tage plus einen benutzerdefinierten Zeitraum anbieten.",
            "Die erste Version fest auf die letzten 30 Tage begrenzen und später konfigurierbar machen.",
            "Den Zeitraum des Quellsystems übernehmen und keinen neuen Datumsfilter ergänzen.",
        ),
        "rules": (
            "Alle Nutzer haben Lesezugriff; nur Führungskräfte dürfen exportieren; kein Rückschreiben.",
            "Rollenbasierte Sicht- und Exportrechte mit Protokollierung jedes Exports verwenden.",
            "Bestehende Berechtigungen des Quellsystems übernehmen und keinen neuen Freigabeprozess ergänzen.",
        ),
        "integrations": (
            "Eine schreibgeschützte SQL-Server-Ansicht mit Los-ID und Aktualisierung alle fünf Minuten verwenden.",
            "Eine freigegebene SAP-Tabelle oder API mit benannten Schlüsselfeldern täglich aktualisieren.",
            "Eine kontrollierte Excel/CSV-Vorlage verwenden und ungültige Zeilen ablehnen.",
        ),
        "ownership": (
            "Die Abteilungsleitung verantwortet das Ergebnis; der Prozesseigner nimmt ab.",
            "Der Prozesseigner verantwortet Ergebnis und Abnahme.",
            "Die Bereichsleitung verantwortet das Ergebnis; ein Key User nimmt ab.",
        ),
    },
    "ms": {
        "scope": (
            "Sediakan julat pantas 7, 30 atau 90 hari serta julat tarikh tersuai.",
            "Tetapkan keluaran pertama kepada 30 hari terkini dan jadikan ia boleh dikonfigurasi kemudian.",
            "Gunakan julat masa sistem sumber tanpa penapis tarikh baharu dalam keluaran pertama.",
        ),
        "rules": (
            "Semua pengguna baca sahaja; hanya pengurus boleh mengeksport; tiada tulis balik.",
            "Gunakan akses berasaskan peranan dan rekod setiap eksport.",
            "Kekalkan kebenaran sistem sumber tanpa aliran kelulusan baharu.",
        ),
        "integrations": (
            "Gunakan paparan SQL Server baca sahaja berkunci ID lot dan segar semula setiap lima minit.",
            "Gunakan jadual atau API SAP yang diluluskan dengan medan kunci dan segar semula harian.",
            "Gunakan templat Excel/CSV terkawal, sahkan medan wajib dan tolak baris tidak sah.",
        ),
        "ownership": (
            "Pengurus jabatan memiliki hasil; pemilik proses meluluskan penerimaan.",
            "Pemilik proses memiliki hasil dan penerimaan.",
            "Ketua jabatan memiliki hasil; wakil pengguna utama meluluskan penerimaan.",
        ),
    },
}

_STRICT_REVIEW_HINT = {
    "en": "Choose the closest answer, or write the exact rule.",
    "zh": "请选择最接近的答案，或直接填写准确规则。",
    "de": "Die passendste Antwort wählen oder die genaue Regel eingeben.",
    "ms": "Pilih jawapan terdekat atau tulis peraturan yang tepat.",
}

_ROUTE_ANSWER_OVERRIDES: dict[str, dict[str, dict[str, tuple[str, str, str]]]] = {
    "en": {
        "production": {
            "outcome": (
                "Reduce production plan deviations by 15% within the next quarter.",
                "Cut material-shortage response time to under 30 minutes.",
                "Increase on-time lot completion to at least 95%.",
            ),
            "actor_action": (
                "The shift supervisor uses WIP and exception status to decide the next lot priority.",
                "The production planner uses demand and material readiness to adjust the daily plan.",
                "The process engineer uses yield and downtime trends to choose the next improvement action.",
            ),
            "v1_flow": (
                "Show plan versus actual, WIP, and shortages with drill-down; automatic rescheduling is out of scope.",
                "Provide a material-shortage worklist with owner and aging; purchasing execution is out of scope.",
                "Show lot-flow and downtime trends with filters and export; machine control is out of scope.",
            ),
            "acceptance": (
                "The production supervisor can identify the highest-risk delayed lot within five minutes.",
                "The planner can see every material shortage, owner, and expected recovery time on one page.",
                "The process engineer can identify the top yield or downtime loss for a selected line and shift.",
            ),
        },
        "quality": {
            "outcome": (
                "Reduce quality disposition lead time by 30% within the next quarter.",
                "Reduce repeat defects in the selected process by 15%.",
                "Increase on-time closure of quality actions to at least 95%.",
            ),
            "actor_action": (
                "The quality engineer uses defect trends to decide which product and lot to investigate first.",
                "The quality manager uses risk and aging to prioritize pending dispositions.",
                "The inspector uses the exception list to decide which item requires reinspection.",
            ),
            "v1_flow": (
                "Show defect trends and affected lots with drill-down; automated disposition is out of scope.",
                "Provide a disposition queue with owner, risk, and aging; ERP posting is out of scope.",
                "Track CAPA actions, due dates, and evidence; changing the approval workflow is out of scope.",
            ),
            "acceptance": (
                "The quality engineer can identify the top defect and affected lots within five minutes.",
                "The quality manager can see every overdue disposition and accountable owner on one page.",
                "The inspector can trace an exception to its evidence and current status without manual data merging.",
            ),
        },
        "tdi": {
            "outcome": (
                "Reduce TDI request lead time by 30% within the next quarter.",
                "Increase on-time completion of TDI requests to at least 95%.",
                "Reduce requests returned for missing information by 20%.",
            ),
            "actor_action": (
                "The TDI coordinator uses request status and blockers to decide which request to escalate.",
                "The request owner uses readiness and due dates to decide the next handoff action.",
                "The approver uses scope, evidence, and risk to decide whether the request can proceed.",
            ),
            "v1_flow": (
                "Provide request intake, assignment, status, and closure tracking; implementation execution is out of scope.",
                "Show request readiness, blockers, and due dates with reminders; automatic approval is out of scope.",
                "Track handoffs, verification evidence, and closure; changing external systems is out of scope.",
            ),
            "acceptance": (
                "The coordinator can identify every blocked or overdue request and its owner on one page.",
                "The request owner can see the next required action and due date without asking another team.",
                "The approver can trace each request to the evidence required for approval and closure.",
            ),
        },
    },
    "zh": {
        "production": {
            "outcome": (
                "下季度将生产计划偏差率降低 15%。",
                "将物料短缺响应时间缩短到 30 分钟以内。",
                "将批次按时完成率提升到 95% 以上。",
            ),
            "actor_action": (
                "值班主管根据 WIP 和异常状态决定下一批次的优先级。",
                "生产计划员根据需求和物料齐套情况调整日计划。",
                "工艺工程师根据良率和停机趋势决定下一项改善动作。",
            ),
            "v1_flow": (
                "首版展示计划与实际、WIP 和缺料并支持下钻；不包含自动排程。",
                "首版提供缺料清单、负责人和超期时长；不包含采购执行。",
                "首版展示批次流转和停机趋势并支持筛选导出；不控制设备。",
            ),
            "acceptance": (
                "生产主管能在 5 分钟内找出延期风险最高的批次。",
                "计划员能在一个页面看到全部缺料、负责人和预计恢复时间。",
                "工艺工程师能找出所选产线和班次的首要良率或停机损失。",
            ),
        },
        "quality": {
            "outcome": (
                "下季度将质量判定周期缩短 30%。",
                "将所选工序的重复缺陷率降低 15%。",
                "将质量行动按时关闭率提升到 95% 以上。",
            ),
            "actor_action": (
                "质量工程师根据缺陷趋势决定优先调查的产品和批次。",
                "质量经理根据风险和超期时长安排待判事项优先级。",
                "检验员根据异常清单决定哪些项目需要复检。",
            ),
            "v1_flow": (
                "首版展示缺陷趋势和受影响批次并支持下钻；不包含自动判定。",
                "首版提供待判队列、负责人、风险和超期时长；不包含 ERP 过账。",
                "首版追踪 CAPA 行动、到期日和证据；不改变审批流程。",
            ),
            "acceptance": (
                "质量工程师能在 5 分钟内找出首要缺陷及受影响批次。",
                "质量经理能在一个页面看到全部超期待判事项和负责人。",
                "检验员无需手工合并数据即可追溯异常证据和当前状态。",
            ),
        },
        "tdi": {
            "outcome": (
                "下季度将 TDI 需求处理周期缩短 30%。",
                "将 TDI 需求按时完成率提升到 95% 以上。",
                "将因信息缺失被退回的需求比例降低 20%。",
            ),
            "actor_action": (
                "TDI 协调员根据需求状态和阻塞项决定优先升级哪一条需求。",
                "需求负责人根据齐备度和到期日决定下一步交接动作。",
                "审批人根据范围、证据和风险决定需求是否可以继续。",
            ),
            "v1_flow": (
                "首版提供需求受理、分派、状态和关闭追踪；不包含实施执行。",
                "首版展示需求齐备度、阻塞项和到期日并提醒；不包含自动审批。",
                "首版追踪交接、验证证据和关闭；不改造外部系统。",
            ),
            "acceptance": (
                "协调员能在一个页面找出全部阻塞或超期需求及负责人。",
                "需求负责人无需询问其他团队即可看到下一步动作和到期日。",
                "审批人能追溯每条需求在审批和关闭时所需的证据。",
            ),
        },
    },
}

_SOURCE_MARKERS = (
    "sql",
    "sap",
    "csv",
    "excel",
    "api",
    "mes",
    "database",
    "data source",
    "from ",
    "source",
    "数据库",
    "数据源",
    "来自",
    "quelle",
    "daten",
    "daripada",
    "sumber",
)

_BOUNDARY_MARKERS = (
    "read-only",
    "read only",
    "readonly",
    "writeback",
    "write back",
    "read/write",
    "no production writeback",
    "只读",
    "回写",
    "读写",
    "nur lesend",
    "schreibgeschützt",
    "rückschreiben",
    "baca sahaja",
    "baca saja",
    "tulis balik",
)

_MEASURABLE_OUTCOME_PATTERN = re.compile(
    r"(?:\d+(?:[.,]\d+)?\s*(?:%|percent|percentage|分钟|小时|天|周|月|季度)?)"
    r"|\b(?:rate|ratio|yield|time|cost|count|volume|accuracy|throughput|output|"
    r"downtime|cycle time|lead time|sla|defect|escape|aging|revenue|margin)\b"
    r"|(?:良率|比率|比例|时间|时长|成本|数量|准确率|产出|停机|周期|缺陷|漏检|老化|收入|利润)"
    r"|\b(?:quote|rate|zeit|kosten|anzahl|genauigkeit|durchsatz|ausgabe|"
    r"ausfallzeit|zykluszeit|fehler|umsatz|marge)\b"
    r"|\b(?:kadar|nisbah|masa|kos|bilangan|ketepatan|hasil|masa henti|"
    r"masa kitaran|kecacatan|sla)\b",
    re.IGNORECASE,
)

_OUTCOME_DIRECTION_PATTERN = re.compile(
    r"\b(?:reduce|decrease|lower|cut|shorten|increase|raise|improve|"
    r"achieve|maintain|prevent)\b"
    r"|(?:降低|减少|缩短|提升|提高|改善|达到|保持|避免)"
    r"|\b(?:senken|reduzieren|verringern|verkürzen|erhöhen|verbessern|"
    r"erreichen|halten|vermeiden)\b"
    r"|\b(?:kurangkan|rendahkan|pendekkan|tingkatkan|tambah baik|capai|"
    r"kekalkan|elakkan)\b",
    re.IGNORECASE,
)

_OBSERVABLE_ACCEPTANCE_PATTERN = OBSERVABLE_EVIDENCE_PATTERN

_STRICT_SOURCE_ARTIFACT_PATTERN = SOURCE_ARTIFACT_PATTERN
_STRICT_KEY_FIELD_PATTERN = KEY_FIELD_PATTERN
_STRICT_CADENCE_PATTERN = CADENCE_PATTERN


def decision_has_required_evidence_v2(
    structured_model: dict[str, Any] | None,
    decision_id: str,
) -> bool:
    """Return whether a decision has enough concrete evidence to be confirmed."""

    model = _record(structured_model)
    normalized_id = _string(decision_id).casefold()
    context = _record(model.get("product_context"))
    users_and_scenarios = _record(model.get("users_and_scenarios"))
    scope = _record(model.get("scope"))
    functional_requirements = _record(model.get("functional_requirements"))

    if normalized_id in {"outcome", "objective"}:
        objective = _string(_record(model.get("background")).get("objective"))
        return bool(
            objective
            and _MEASURABLE_OUTCOME_PATTERN.search(objective)
            and _OUTCOME_DIRECTION_PATTERN.search(objective)
        )
    if normalized_id == "actor_action":
        users = _string_list(users_and_scenarios.get("target_users"))
        scenarios = _string_list(users_and_scenarios.get("core_scenarios"))
        return bool(
            (users or _string(context.get("primary_user")))
            and (_string(context.get("decision_or_action")) or scenarios)
        )
    if normalized_id == "users":
        return bool(
            _string(context.get("primary_user"))
            or _string_list(users_and_scenarios.get("target_users"))
        )
    if normalized_id == "v1_flow":
        return bool(
            _string_list(scope.get("in_scope"))
            and _string_list(users_and_scenarios.get("core_scenarios"))
            and (
                _string(functional_requirements.get("overview"))
                or _nonempty_records(functional_requirements.get("feature_details"))
            )
        )
    if normalized_id == "scope":
        return bool(_string_list(scope.get("in_scope")))
    if normalized_id == "scenarios":
        return bool(_string_list(users_and_scenarios.get("core_scenarios")))
    if normalized_id == "features":
        return bool(
            _string(functional_requirements.get("overview"))
            or _nonempty_records(functional_requirements.get("feature_details"))
        )
    if normalized_id == "writeback":
        return writeback_is_authorized(model)
    if normalized_id in {"data_boundary", "integrations"}:
        return _data_boundary_evidence_complete(model)
    if normalized_id == "acceptance":
        return any(
            _OBSERVABLE_ACCEPTANCE_PATTERN.search(criterion)
            for criterion in _string_list(model.get("acceptance_criteria"))
        )
    if normalized_id == "rules":
        return bool(_string_list(model.get("business_rules")))
    if normalized_id == "ownership":
        return bool(
            _string(context.get("business_owner"))
            and _string(context.get("acceptance_owner"))
        )
    return False


def build_interview_state_v2(
    structured_model: dict[str, Any] | None,
    *,
    document_status: str = "missing",
    language: str = "en",
    active_proposal: dict[str, Any] | None = None,
    deferred_decision_ids: list[str] | tuple[str, ...] | set[str] | None = None,
    defer_available_decision_id: str = "",
    strict_review_turn_count: int = 0,
    strict_review_turn_limit: int = 2,
    business_route: str = "",
) -> dict[str, Any]:
    """Build the single authoritative state for the V2 interview flow."""

    model = _record(structured_model)
    normalized_document_status = _normalize_document_status(document_status)
    normalized_language = _normalize_language(language)

    fast_complete = {
        "outcome": _outcome_complete(model),
        "actor_action": _actor_action_complete(model),
        "v1_flow": _v1_flow_complete(model),
        "data_boundary": _data_boundary_complete(model),
        "acceptance": _acceptance_complete(model),
    }
    confirmed_decisions = sum(
        1 for decision_id in FAST_DECISION_IDS if fast_complete[decision_id]
    )
    deferred_decisions = {
        decision_id
        for raw_decision_id in deferred_decision_ids or ()
        if (decision_id := _string(raw_decision_id)) in FAST_DECISION_IDS
        and not fast_complete[decision_id]
    }
    assumption_count = len(deferred_decisions)
    brief_ready = (
        confirmed_decisions + assumption_count == len(FAST_DECISION_IDS)
    )

    strict_complete = {
        key: _strict_requirement_complete(model, key)
        for key in STRICT_REVIEW_KEYS
    }
    remaining_review_keys = [
        key for key in STRICT_REVIEW_KEYS if not strict_complete[key]
    ]
    review_ready = not remaining_review_keys
    normalized_strict_turn_count = max(0, int(strict_review_turn_count or 0))
    normalized_strict_turn_limit = max(1, int(strict_review_turn_limit or 2))
    strict_review_exhausted = (
        not review_ready
        and normalized_strict_turn_count >= normalized_strict_turn_limit
    )

    if not brief_ready:
        stage = "brief_discovery"
        active_decision_id = next(
            decision_id
            for decision_id in FAST_DECISION_IDS
            if not fast_complete[decision_id]
            and decision_id not in deferred_decisions
        )
        if active_decision_id == "data_boundary" and _writeback_needs_authorization(
            model
        ):
            # The user asked to write into a source system. Ask the writeback
            # question instead of repeating the data-boundary card, while the
            # decision still counts as the same one of the five.
            active_decision_id = "writeback"
        can_generate_brief = False
        can_handoff = False
    elif normalized_document_status == "missing":
        stage = "brief_ready"
        active_decision_id = None
        can_generate_brief = True
        can_handoff = False
    elif not review_ready:
        stage = "strict_review"
        active_decision_id = (
            None if strict_review_exhausted else remaining_review_keys[0]
        )
        can_generate_brief = False
        can_handoff = False
    elif normalized_document_status == "stale":
        stage = "refresh_brief"
        active_decision_id = None
        can_generate_brief = True
        can_handoff = False
    else:
        stage = "handoff_ready"
        active_decision_id = None
        can_generate_brief = False
        can_handoff = True

    next_decision = (
        _build_next_decision(
            active_decision_id,
            language=normalized_language,
            active_proposal=active_proposal,
            can_defer=(
                stage == "brief_discovery"
                # Writeback offers a read-only escape instead of a TBD, which
                # would park it as an assumption that never resolves.
                and active_decision_id != "writeback"
                and _string(defer_available_decision_id) == active_decision_id
            ),
            business_route=business_route,
            structured_model=model,
            strict_review=stage == "strict_review",
        )
        if active_decision_id
        else None
    )

    return {
        "schema_version": "2.0",
        "stage": stage,
        "brief": {
            "confirmed_decisions": confirmed_decisions,
            "total_decisions": len(FAST_DECISION_IDS),
            "assumption_count": assumption_count,
            "ready": brief_ready,
            "document_status": normalized_document_status,
        },
        "review": {
            "remaining_count": len(remaining_review_keys),
            "remaining_keys": remaining_review_keys,
            "ready": review_ready,
            "asked_count": normalized_strict_turn_count,
            "max_questions": normalized_strict_turn_limit,
            "input_mode": (
                "complete"
                if review_ready
                else "manual"
                if strict_review_exhausted
                else "question"
            ),
        },
        "next_decision": next_decision,
        "actions": {
            "can_generate_brief": can_generate_brief,
            "can_handoff": can_handoff,
        },
    }


def _build_next_decision(
    decision_id: str,
    *,
    language: str,
    active_proposal: dict[str, Any] | None,
    can_defer: bool,
    business_route: str,
    structured_model: dict[str, Any],
    strict_review: bool,
) -> dict[str, Any]:
    copy_key = _STRICT_COPY_KEY.get(decision_id, decision_id)
    label, question, hint = _QUESTION_COPY[language][copy_key]
    if strict_review:
        status = _record(
            _record(structured_model.get("collection_status")).get(decision_id)
        )
        pending_questions = _string_list(status.get("pending_questions"))
        if pending_questions:
            question = pending_questions[0]
        hint = _STRICT_REVIEW_HINT[language]
    proposal = _matching_proposal(active_proposal, decision_id)
    return {
        "decision_id": decision_id,
        "label": label,
        "question": question,
        "hint": hint,
        "mode": "confirm_proposal" if proposal else "free_text",
        "proposal": proposal,
        "can_defer": can_defer,
        "options": (
            []
            if proposal
            else (
                _strict_review_answer_options(
                    decision_id,
                    language=language,
                )
                if strict_review
                else _answer_options(
                    copy_key,
                    language=language,
                    business_route=business_route,
                )
            )
        ),
    }


def _strict_review_answer_options(
    decision_id: str,
    *,
    language: str,
) -> list[dict[str, str]]:
    option_texts = _STRICT_REVIEW_ANSWER_OPTIONS.get(language, {}).get(
        decision_id,
        (),
    )
    return [
        {
            "option_id": f"strict-{decision_id}-{index}",
            "text": text,
        }
        for index, text in enumerate(option_texts, start=1)
    ]


def _answer_options(
    decision_id: str,
    *,
    language: str,
    business_route: str,
) -> list[dict[str, str]]:
    normalized_route = _string(business_route).casefold()
    route_options = (
        _ROUTE_ANSWER_OVERRIDES
        .get(language, {})
        .get(normalized_route, {})
        .get(decision_id)
    )
    option_texts = (
        route_options
        or _GENERAL_ANSWER_OPTIONS[language].get(decision_id)
        or ()
    )
    return [
        {
            "option_id": f"{decision_id}-{normalized_route or 'general'}-{index}",
            "text": text,
            "label": _option_label(text),
        }
        for index, text in enumerate(option_texts, start=1)
    ]


_OPTION_LABEL_MAX_CHARS = 80


def _option_label(text: str, maximum: int = _OPTION_LABEL_MAX_CHARS) -> str:
    """A scannable label for the card; the full text is still what gets sent.

    A complete writeback authorization has to name four facts, so its answer is
    far longer than a normal option. The card shows the leading clause and sends
    the whole sentence, which keeps grounding intact.
    """

    normalized = _string(text)
    if len(normalized) <= maximum:
        return normalized
    head = re.split(r"[:：;；,，]", normalized, maxsplit=1)[0].strip()
    if head and len(head) <= maximum:
        return head
    return f"{normalized[: maximum - 1].rstrip()}…"


def _matching_proposal(
    value: dict[str, Any] | None,
    decision_id: str,
) -> dict[str, str] | None:
    proposal = _record(value)
    if _string(proposal.get("decision_id")) != decision_id:
        return None
    proposal_id = _string(proposal.get("proposal_id"))
    text = _string(proposal.get("text"))
    if not proposal_id or not text:
        return None
    return {"proposal_id": proposal_id, "text": text}


def _outcome_complete(model: dict[str, Any]) -> bool:
    return _is_fast_answered(
        model,
        "objective",
    ) and decision_has_required_evidence_v2(model, "outcome")


def _actor_action_complete(model: dict[str, Any]) -> bool:
    return _is_fast_answered(
        model,
        "users",
    ) and decision_has_required_evidence_v2(model, "actor_action")


def _v1_flow_complete(model: dict[str, Any]) -> bool:
    return (
        _is_fast_answered(model, "scope")
        and _is_fast_answered(model, "scenarios")
        and _is_fast_answered(model, "features")
        and decision_has_required_evidence_v2(model, "v1_flow")
    )


def _data_boundary_complete(model: dict[str, Any]) -> bool:
    return (
        _is_fast_answered(model, "integrations")
        and decision_has_required_evidence_v2(model, "data_boundary")
    )


def _acceptance_complete(model: dict[str, Any]) -> bool:
    return (
        _is_fast_answered(model, "acceptance")
        and decision_has_required_evidence_v2(model, "acceptance")
    )


def _strict_requirement_complete(model: dict[str, Any], key: str) -> bool:
    validators: dict[str, Callable[[dict[str, Any]], bool]] = {
        "objective": lambda value: _is_confirmed(value, "objective")
        and decision_has_required_evidence_v2(value, "outcome"),
        "scope": lambda value: _is_confirmed(value, "scope")
        and bool(_string_list(_record(value.get("scope")).get("in_scope"))),
        "users": lambda value: _is_confirmed(value, "users")
        and decision_has_required_evidence_v2(value, "actor_action"),
        "scenarios": lambda value: _is_confirmed(value, "scenarios")
        and bool(
            _string_list(
                _record(value.get("users_and_scenarios")).get("core_scenarios")
            )
        ),
        "features": lambda value: _is_confirmed(value, "features")
        and bool(
            _string(
                _record(value.get("functional_requirements")).get("overview")
            )
            or _nonempty_records(
                _record(value.get("functional_requirements")).get(
                    "feature_details"
                )
            )
        ),
        "rules": lambda value: _is_confirmed(value, "rules")
        and bool(_string_list(value.get("business_rules"))),
        "integrations": lambda value: _is_confirmed(value, "integrations")
        and _integration_detail_complete(value),
        "acceptance": lambda value: _is_confirmed(value, "acceptance")
        and decision_has_required_evidence_v2(value, "acceptance"),
        "ownership": _ownership_complete,
    }
    return validators[key](model)


def _writeback_needs_authorization(model: dict[str, Any]) -> bool:
    """The user asked to write into a source system but has not authorized it."""

    return classify_data_paths(
        _string_list(model.get("data_and_dependencies")),
        writeback_authorization=model.get("writeback_authorization"),
    )["pending_writeback"]


def _data_boundary_evidence_complete(model: dict[str, Any]) -> bool:
    return data_boundary_is_confirmed(
        _string_list(model.get("data_and_dependencies")),
        writeback_authorization=model.get("writeback_authorization"),
    )


def _integration_detail_complete(model: dict[str, Any]) -> bool:
    dependencies = _string_list(model.get("data_and_dependencies"))
    combined = "\n".join(dependencies)
    return (
        _data_boundary_evidence_complete(model)
        and bool(_STRICT_SOURCE_ARTIFACT_PATTERN.search(combined))
        and bool(_STRICT_KEY_FIELD_PATTERN.search(combined))
        and bool(_STRICT_CADENCE_PATTERN.search(combined))
    )


def _ownership_complete(model: dict[str, Any]) -> bool:
    context = _record(model.get("product_context"))
    return (
        _is_confirmed(model, "ownership")
        and bool(_string(context.get("business_owner")))
        and bool(_string(context.get("acceptance_owner")))
    )


def _is_confirmed(model: dict[str, Any], key: str) -> bool:
    collection_status = _record(model.get("collection_status"))
    status_item = _record(collection_status.get(key))
    return _string(status_item.get("status")).casefold() == "confirmed"


def _is_fast_answered(model: dict[str, Any], key: str) -> bool:
    collection_status = _record(model.get("collection_status"))
    status_item = _record(collection_status.get(key))
    return _string(status_item.get("status")).casefold() in {
        "confirmed",
        "pending_confirmation",
    }


def _normalize_language(value: str) -> str:
    return _LANGUAGE_ALIASES.get(_string(value).casefold(), "en")


def _normalize_document_status(value: str) -> str:
    normalized = _string(value).casefold()
    return normalized if normalized in _DOCUMENT_STATUSES else "missing"


def _record(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _string(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [text for item in value if (text := _string(item))]
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    return []


def _nonempty_records(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [
        item
        for item in value
        if isinstance(item, dict) and any(_string(field) for field in item.values())
    ]
