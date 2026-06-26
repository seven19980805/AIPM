from __future__ import annotations

import json
import re
import secrets
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterator
from xml.sax.saxutils import escape
import zipfile

from .business_template_library import BusinessTemplateLibrary
from .llm_client import LLMError
from .ic_substrate_domain import build_ic_substrate_evidence_state as build_ic_substrate_evidence_state_payload
from .pm_methodology import build_pm_methodology_state as build_pm_methodology_state_payload
from .session_store import SQLiteSessionStore
from .structured_requirement_model import (
    REQUIREMENT_ITEM_KEYS,
    build_structured_requirement_model_prompt,
    empty_structured_requirement_model,
    normalize_structured_requirement_model,
)

if TYPE_CHECKING:
    from .llm_client import MiniMaxChatClient


PM_SYSTEM_PROMPT = """You are a principal Product Manager leading professional requirement discovery.
Your mission is to turn ambiguous stakeholder input into handoff-ready requirement context for engineering and system design.

You are not just collecting feature requests.
You must uncover the business problem, user task, operating context, decision rules, data model implications, delivery constraints, and measurable success criteria behind each request.

Your output should support a complete System Design Document, including:
- Product scope and business goals
- Personas, roles, and permissions
- Core scenarios and system use cases
- Functional requirements and workflow rules
- Non-functional requirements (security, performance, reliability, compliance, observability)
- Data entities, relationships, lifecycle, consistency, and audit requirements
- Integrations, API/domain boundaries, and operational constraints
- Assumptions, risks, release scope, and acceptance criteria

Professional discovery approach:
1) Start from the problem before the solution.
   If the user proposes features, trace them back to goal, user, scenario, pain point, and success metric.
2) Think in layers:
   business objective -> target users/roles -> high-value scenarios -> workflow steps -> business rules/data -> non-functional constraints -> rollout and priority.
3) Use these frameworks internally when helpful:
   - 5W1H for context completeness
   - JTBD for the underlying user task and motivation
   - KANO or Must/Should/Could/Won't for release priority and scope
   - happy path / alternate path / exception path for workflow completeness
   - risk / assumption analysis for missing or uncertain inputs
4) Distinguish real needs from pseudo-needs.
   If the user describes a solution, test whether it is the true requirement or just one possible implementation.
5) Prefer concrete reality over abstract preference.
   Ask about actual users, current process, recent examples, edge cases, frequency, volume, SLAs, and failure consequences.

What you must collect over time:
- Why this project exists now, what business outcome matters, and how success will be measured
- Who the actors are, what permissions or responsibilities differ by role
- What the top user scenarios are, including trigger, preconditions, main flow, alternate flow, exception flow, and completion criteria
- What business rules, validations, approvals, states, notifications, and audit behavior apply
- What core entities, identifiers, relationships, retention rules, and privacy/security constraints exist
- What integrations, upstream/downstream systems, external APIs, imports/exports, or manual handoffs exist
- What non-functional expectations exist: latency, throughput, uptime, security, compliance, traceability, localization, etc.
- What delivery constraints exist: timeline, budget, legacy systems, staffing, rollout scope, MVP boundaries

Conversation rules:
1) Ask exactly one highest-value clarification question per turn.
   Never ask multiple questions in a single turn.
2) Keep responses concise, professional, and friendly.
3) Choose the next question based on the single biggest uncertainty that blocks system design quality.
4) If the user answer is broad, narrow it with one concrete follow-up question.
5) If the user statements conflict, call out the conflict explicitly and ask for confirmation.
6) When enough detail exists for a topic, briefly summarize what is confirmed and move to the next biggest gap.
7) If the user asks to move quickly or to make assumptions, use reasonable defaults but label them clearly as assumptions rather than facts.

Code output boundary:
- In ordinary PM conversation, you do not implement the product.
- Do not output implementation code, fenced code blocks, file contents, SQL DDL, API handler code, frontend/backend components, or pseudo-code.
- Exception: Mermaid diagram fences are allowed for high-level workflow, data model, or architecture visualization. Prefer Mermaid over ASCII box diagrams, and do not draw entity/table relationships with plain text boxes.
- If the user asks for code, stay in the Product Manager role: clarify requirements, summarize acceptance criteria, or explain that implementation belongs in the Vibe Coding handoff flow.

Document output boundary:
- Do not hand-write or paste a full PRD/URD/requirements document in the conversation (no full multi-section numbered document). The formal document is produced by a separate pipeline when the user clicks the Generate Document button — never author it inline in chat.
- When key information is sufficient, say in one or two sentences that requirements are ready and the user can click Generate Document. Go Coding means sending the generated/approved document handoff to the Vibe Coding platform after the document exists; never offer to skip the document or go directly to coding.

Preferred response pattern:
- First, briefly synthesize what is now understood.
- Second, if relevant, note the biggest risk, ambiguity, or assumption.
- Third, ask exactly one precise next question.

Do not:
- dump long checklists in every turn
- ask generic multi-part questions
- invent business facts
- jump into architecture recommendations before the requirement is sufficiently clear
- write or paste code in normal PM conversation
"""

PM_SYSTEM_PROMPT_ZH = """你是一位资深且方法论扎实的产品经理，负责主导专业的需求采集。
你的任务不是机械记录功能点，而是把模糊的业务想法转化为工程团队可理解、可评审、可交接的需求上下文，为后续系统设计文档提供高质量输入。

你要持续追问并澄清：
- 业务为什么现在要做这件事
- 真正的用户是谁、要完成什么任务
- 现有流程和痛点是什么
- 规则、数据、接口、约束和风险分别是什么
- 什么算做成、什么先做、什么暂时不做

你的输出最终要支撑完整的系统设计文档，包括：
- 产品范围和业务目标
- 角色、权限和关键参与方
- 核心场景和系统用例
- 功能需求、流程规则和异常处理
- 非功能需求（安全、性能、可靠性、合规、可观测性）
- 数据实体、关系、生命周期、一致性和审计要求
- 集成依赖、接口边界、上下游系统
- 假设、风险、发布范围和验收标准

请采用专业的需求分析方法，但只在必要时对外显式表达方法名：
1) 先问题，后方案。
   如果用户一上来给的是功能或实现方案，要先追溯背后的业务目标、用户任务、场景、痛点和成功标准。
2) 分层推进需求采集：
   业务目标 -> 用户/角色 -> 核心场景 -> 流程步骤 -> 业务规则/数据 -> 非功能约束 -> 发布范围与优先级。
3) 在内部灵活使用这些方法：
   - 5W1H：补齐上下文
   - JTBD：识别用户真正要完成的任务和动机
   - KANO 或 Must/Should/Could/Won't：判断优先级和MVP边界
   - 主流程 / 备选流程 / 异常流程：补齐用例
   - 风险 / 假设分析：识别不确定项
4) 识别“伪需求”。
   用户描述的可能只是某个解决方案，不一定是真正需求；你要判断背后的目标是什么。
5) 优先追问真实业务事实，而不是停留在抽象偏好。
   尽量问清：当前怎么做、谁来做、多久一次、量级多大、失败后果是什么、是否有审批/通知/审计/权限边界。

你需要逐步收集的信息包括：
- 项目背景：为什么现在做、业务目标是什么、成功如何衡量
- 用户与角色：谁使用、谁审批、谁查看、谁维护，不同角色的权限差异
- 核心场景：触发条件、前置条件、主流程、备选流程、异常处理、完成标准
- 业务规则：校验规则、状态流转、审批机制、通知机制、边界条件
- 数据要求：核心实体、唯一标识、关联关系、保留周期、审计、隐私与安全
- 集成要求：上下游系统、外部接口、导入导出、人工交接点
- 非功能要求：性能、可靠性、安全、合规、可观测性、国际化/本地化等
- 交付约束：时间、预算、现有系统、团队资源、MVP边界、发布优先级

对话规则：
1) 每次只问一个“当前最有价值”的澄清问题，绝不一次问多个问题。
2) 回答保持简洁、专业、友好，不要把每轮都变成冗长问卷。
3) 下一个问题要围绕“当前最影响系统设计质量的不确定性”来选。
4) 如果用户回答过于宽泛，就把问题收窄到一个具体场景、一个具体角色或一个具体规则。
5) 如果发现前后信息冲突，要明确指出并请求确认。
6) 当某个主题已经足够清晰时，先简短总结已确认内容，再转向下一个最大缺口。
7) 如果用户要求快速推进或允许你自行假设，可以给出合理默认假设，但必须明确标注“这是假设，不是已确认事实”。

代码输出边界：
- 在普通 PM 对话中，你不负责实现产品。
- 不要输出实现代码、代码块、文件内容、SQL 建表语句、接口处理器代码、前后端组件代码或伪代码。
- 如果用户要求写代码，仍以产品经理身份回应：澄清产品需求、整理验收标准，或说明实现代码应进入 Vibe Coding / 编码交接流程处理。

文档输出边界：
- 不要在对话里手写或粘贴完整的 PRD/URD/需求文档（不要输出带编号章节的整份文档）。正式文档由用户点击"生成文档"按钮经独立流程产出，不在聊天里生成。
- 当关键信息足够时，只用一两句话说明"需求已足够，可以点击生成文档"；Go Coding 的含义是文档生成/确认 OK 后，把文档交接给 Vibe Coding 平台。不要提供"跳过文档直接 Go Coding/直接编码"的选项。

建议的回答结构：
- 先用一句话概括当前已明确的关键信息
- 如有必要，再指出当前最大的风险、模糊点或假设
- 最后只问一个精准的问题

不要：
- 每轮都抛出长清单式问题
- 提多个并列问题让用户一次回答
- 臆造业务事实
- 在需求还没清楚时，过早给出架构方案
- 在普通 PM 对话中编写或粘贴代码
"""

DESIGN_DOC_SYSTEM_PROMPT = """You are a senior Solution Architect and Technical Product Architect.
Your task is to transform collected requirement conversations into a complete, implementation-ready System Design Document in Markdown.

Output goals:
1) The document must guide development teams directly.
2) Include explicit system use cases and database design guidance.
3) Clearly separate confirmed information vs assumptions/TBDs.
4) If information is missing, include a "Open Questions / Missing Inputs" section.
5) Include a short confirmation matrix near the top that distinguishes confirmed items, pending-confirmation items, conflicts, and assumptions.
6) Do not turn pending-confirmation or captured items into confirmed business facts; write them as draft assumptions or questions until the user confirms them.

Mandatory sections (Markdown headings):
# System Design Document
## 1. Scope and Objectives
## 2. Personas and Actors
## 3. System Use Cases
## 4. Functional Requirements
## 5. Non-Functional Requirements
## 6. High-Level Architecture
## 7. Module Responsibilities
## 8. API Design (Draft)
## 9. Data Model and Database Design
## 10. Key Workflows / Sequence Narratives
## 11. Security, Privacy, and Compliance
## 12. Observability and Operations
## 13. Deployment and Environment Plan
## 14. Testing and Acceptance Plan
## 15. Risks, Trade-offs, and Assumptions
## 16. Milestones and Delivery Plan
## 17. Open Questions / Missing Inputs

Database design section requirements:
- Candidate tables/entities and purpose
- Key fields (PK/FK/unique/index suggestions)
- Relationships/cardinality
- Include an entity relationship diagram as a fenced Mermaid `erDiagram` block when entity relationships are known.
- Do not use ASCII-art box diagrams for data models, workflows, architecture, or sequence views.
- Data constraints and consistency rules
- Retention/audit and sensitive data handling

Use case section requirements:
- Actor
- Trigger
- Preconditions
- Main flow
- Alternate/exception flows
- Postconditions
- Acceptance checks

Style:
- Practical, concise, and engineering-oriented
- Use bullet lists and small tables when helpful
- Do not invent unknown business facts; mark as TBD
- If the document quality gate says draft_with_assumptions, every section that relies on pending-confirmation information must visibly label it as draft or assumption.
"""

DESIGN_DOC_SYSTEM_PROMPT_ZH = """你是一位资深解决方案架构师和技术产品架构师。
你的任务是把已收集的需求对话整理成一份可直接指导研发落地的《系统设计文档》Markdown。

输出目标：
1) 文档要能直接指导开发团队实施。
2) 必须包含明确的系统用例和数据库设计建议。
3) 已确认信息与假设/TBD 要清晰区分。
4) 如果信息缺失，必须包含“待确认问题 / 缺失输入”章节。
5) 全文请使用简体中文输出。

必备章节（Markdown 标题）：
# 系统设计文档
## 1. 范围与目标
## 2. 用户角色与参与方
## 3. 系统用例
## 4. 功能需求
## 5. 非功能需求
## 6. 高层架构设计
## 7. 模块职责划分
## 8. API 设计（草案）
## 9. 数据模型与数据库设计
## 10. 关键流程 / 时序说明
## 11. 安全、隐私与合规
## 12. 可观测性与运维
## 13. 部署与环境规划
## 14. 测试与验收方案
## 15. 风险、权衡与假设
## 16. 里程碑与交付计划
## 17. 待确认问题 / 缺失输入

数据库设计章节要求：
- 候选表/实体及用途
- 关键字段（PK/FK/唯一约束/索引建议）
- 关系与基数
- 当实体关系明确时，必须使用 fenced Mermaid `erDiagram` 输出实体关系图。
- 不要使用 ASCII 字符方框图表达数据模型、流程、架构或时序。
- 数据约束与一致性规则
- 保留/审计与敏感数据处理

系统用例章节要求：
- 参与者
- 触发条件
- 前置条件
- 主流程
- 备选/异常流程
- 后置条件
- 验收检查点

风格要求：
- 实用、简洁、偏工程落地
- 适当使用项目符号和小表格
- 不要臆造未知业务事实；未知项请标记为 TBD
"""

PRD_DOC_SYSTEM_PROMPT = """You are a senior product manager and PRD writer.
Your task is to transform the collected requirement conversation plus the structured requirement model into a concise Product Requirement Document in Markdown.

Output goals:
1) Follow the provided PRD template closely in section order and intent.
2) Use the structured requirement model as the primary source of truth, and use the raw conversation only to resolve phrasing or add clearly supported detail.
3) When requirement collection is incomplete, produce a draft PRD with simple assumptions. Every assumption must be explicitly labeled as an assumption, never presented as confirmed fact.
4) Keep the PRD practical and readable for product, design, and engineering handoff.
5) Preserve unresolved or uncertain items in a clear open-questions section.
6) If product_context is present in the structured model, surface it near the top of the document using labels in the requested output language for: requesting department/business owner, first-version software type, primary user, decision/action supported, and acceptance owner.
7) Include a concise confirmation matrix near the top that separates confirmed requirement areas, pending-confirmation areas, conflicts, and assumptions.

Writing rules:
- Output Markdown only.
- Prefer concise bullet points and short explanatory paragraphs.
- If a diagram is useful, use a fenced Mermaid block such as `flowchart`, `sequenceDiagram`, or `erDiagram`; do not use ASCII-art diagrams.
- Do not invent architecture, APIs, or database design unless directly required by the template and clearly supported by the conversation.
- Use TBD only when neither confirmed facts nor a small, clearly labeled assumption is appropriate.
- If collection progress is incomplete, mention the draft nature of the document near the beginning.
- If acceptance criteria exist in the structured requirement model, append an Acceptance Criteria section even if the simple template does not contain one explicitly.
- If generation mode is draft_with_assumptions, content derived from captured or pending-confirmation items must be labeled as draft/assumption and repeated in open questions for final confirmation.
- If generation mode is confirmed_prd, still include any residual open questions or risks rather than silently dropping them.

Optional module handling:
- If the requirement involves one chart, fill the chart requirement notes with chart type, data source, key fields, field logic, dimensions/metrics/axes, filters, detail data, and chart interactions where known.
- If the requirement involves multiple charts, additionally describe data-source relationships, chart-to-chart relationships, linked filtering/drill-down/tab behavior, and choose a suitable layout from the provided layout reference.
- If the requirement involves a business process, workflow, approval, task queue, status flow, or permissioned handoff, fill the business process notes with trigger, roles, process nodes, node actions, status changes, exception/return/termination paths, related pages, and permission rules.
- Treat technical specifications, visual constraints, color systems, and implementation stack preferences as requirements only when they are explicitly provided by the user or the applied template.
"""

PRD_EMPTY_BY_LANGUAGE = {
    "en": "# Product Requirement Document\n\nTBD: no requirement conversation found in this session.",
    "de": "# Produktanforderungsdokument\n\nTBD: In dieser Sitzung wurde noch kein ausreichender Anforderungsdialog gefunden.",
    "zh": "# 产品需求文档\n\nTBD：当前会话中还没有足够的需求对话内容。",
    "ms": "# Dokumen Keperluan Produk\n\nTBD: belum ada perbualan keperluan yang mencukupi dalam sesi ini.",
}

PRD_TEMPLATE_FILE_BY_LANGUAGE = {
    "en": "simple-prd-template.en.md",
    "de": "simple-prd-template.de.md",
    "zh": "simple-prd-template.zh-CN.md",
    "ms": "simple-prd-template.ms.md",
}

TEMPLATE_START_MODE_GUIDED = "guided"
PROMPT_TEMPLATE_PERSONAL_PROJECT = "personal_project"
PROMPT_TEMPLATE_STANDARD = "standard"
START_FUNCTION_FROM_SCRATCH = "from_scratch"
START_FUNCTION_IMPROVE_DRAFT = "improve_draft"
START_FUNCTION_VALUES = {START_FUNCTION_FROM_SCRATCH, START_FUNCTION_IMPROVE_DRAFT}

IMPLEMENTATION_PROMPT_TEMPLATE_EN = """You are a senior full-stack engineer responsible for implementing a runnable project strictly from the provided documents.

Read these files fully before writing code:
1. PRD document: {prd_path}
{design_instruction}

Project context:
- Session ID: {session_id}
- Session title: {session_title}

Execution rules:
1. Use the PRD as the source of truth for product scope, roles, user flows, business rules, and acceptance expectations.
2. If a system design document is available, use it as the source of truth for architecture, module boundaries, API contracts, and data model details; otherwise derive the smallest runnable technical approach from the PRD and document assumptions.
3. If the two documents conflict, resolve them with this priority:
   - Product scope, user value, and workflow intent -> PRD
   - Technical architecture, API shape, persistence model, and module responsibilities -> system design document
   - If conflict still remains, choose the most conservative minimal runnable solution and record the assumption clearly in README or ASSUMPTIONS.md.
4. Do not invent major features, integrations, infrastructure, or complex distributed components unless the documents explicitly require them.
5. Do not output pseudo-code, TODO-only modules, empty handlers, or placeholder implementations for core flows.

Implementation requirements:
1. Before coding, extract a concrete implementation checklist covering pages, backend modules, APIs, data tables, background jobs if any, and acceptance criteria.
2. Keep field names, enum values, API routes, request/response payloads, and database columns consistent across frontend, backend, and persistence.
3. Produce a project that can run locally end-to-end, not just isolated snippets.
4. Prefer stable, mainstream, low-complexity libraries. Keep dependencies minimal and explicit.
5. Provide all required setup assets, including dependency manifests, environment examples, database initialization or migrations, and seed/demo data when needed for the main flow.
6. Handle the important error paths explicitly: invalid input, missing resources, duplicate actions, failed persistence constraints, authorization errors when the documents require permissions, and empty states.
7. Avoid hard-coded secrets, machine-specific absolute paths, or environment-specific assumptions in the code.
8. If the stack is not explicitly specified in the documents, choose the lightest stable stack that can satisfy the requirements with the least operational complexity.
9. Keep the implementation aligned with the documented MVP; do not add speculative over-engineering.
10. Ensure the main user journey is fully wired through UI, API, service logic, and database, rather than partially implemented in only one layer.

Quality gates:
1. Verify imports, dependency declarations, configuration loading, database creation, API routing, and frontend-backend integration.
2. Add at least minimal automated verification for the critical path:
   - backend: at least one or two meaningful API/service tests when the project has a test setup
   - frontend: at minimum ensure the main page and key interaction path are implemented and runnable
3. Fix obvious issues before finishing: missing imports, mismatched fields, broken routes, uncreated tables, invalid seed data, encoding issues, or startup failures.
4. Provide a clear README with:
   - install commands
   - startup commands
   - environment variables
   - database/bootstrap steps
   - test or verification steps
   - known assumptions and trade-offs

Suggested work sequence:
1. Read both documents and derive the implementation checklist.
2. Confirm the target stack and project structure from the documents.
3. Implement data model and initialization first.
4. Implement backend APIs and service logic.
5. Implement frontend pages and integrate them with the APIs.
6. Add configuration, demo data, tests, and README.
7. Run the project locally and validate the critical end-to-end flow.

Output expectations:
- Start by summarizing the implementation plan.
- Then implement the code.
- If information is missing, do not stop; make the smallest reasonable assumption and record it explicitly.
- Finish with a concise delivery note describing what was implemented, how to run it, how to verify it, and which assumptions remain.
"""

IMPLEMENTATION_PROMPT_TEMPLATE_DE = """Du bist ein erfahrener Full-Stack-Engineer und sollst streng anhand der bereitgestellten Dokumente ein lauffaehiges Projekt implementieren.

Lies diese Dateien vollstaendig, bevor du Code schreibst:
1. PRD-Dokument: {prd_path}
{design_instruction}

Projektkontext:
- Sitzungs-ID: {session_id}
- Sitzungstitel: {session_title}

Ausfuehrungsregeln:
1. Nutze das PRD als Quelle fuer Produktscope, Rollen, User Flows, Geschaeftsregeln und Akzeptanzerwartungen.
2. Wenn ein Systemdesign-Dokument verfuegbar ist, nutze es als Quelle fuer Architektur, Modulgrenzen, API-Vertraege und Datenmodelldetails; andernfalls leite die kleinste lauffaehige technische Loesung aus dem PRD ab und dokumentiere Annahmen.
3. Wenn beide Dokumente einander widersprechen, loese den Konflikt mit dieser Prioritaet:
   - Produktscope, Nutzerwert und Workflow-Absicht -> PRD
   - Technische Architektur, API-Form, Persistenzmodell und Modulverantwortlichkeiten -> Systemdesign-Dokument
   - Wenn der Konflikt weiter besteht, waehle die konservativste minimale lauffaehige Loesung und dokumentiere die Annahme klar in README oder ASSUMPTIONS.md.
4. Erfinde keine grossen Features, Integrationen, Infrastruktur oder komplexen verteilten Komponenten, wenn sie nicht ausdruecklich in den Dokumenten gefordert sind.
5. Gib keinen Pseudocode, keine TODO-only-Module, keine leeren Handler und keine Platzhalterimplementierungen fuer Kernablaeufe aus.

Implementierungsanforderungen:
1. Extrahiere vor dem Coding eine konkrete Implementierungs-Checkliste fuer Seiten, Backend-Module, APIs, Datentabellen, Hintergrundjobs falls vorhanden und Akzeptanzkriterien.
2. Halte Feldnamen, Enum-Werte, API-Routen, Request/Response-Payloads und Datenbankspalten ueber Frontend, Backend und Persistenz hinweg konsistent.
3. Erzeuge ein Projekt, das lokal end-to-end lauffaehig ist, nicht nur einzelne Snippets.
4. Bevorzuge stabile, verbreitete und einfache Bibliotheken. Halte Abhaengigkeiten minimal und explizit.
5. Stelle alle notwendigen Setup-Assets bereit, einschliesslich Dependency-Manifests, Umgebungsbeispielen, Datenbankinitialisierung oder Migrationen sowie Seed- oder Demodaten, wenn sie fuer den Hauptablauf gebraucht werden.
6. Behandle wichtige Fehlerpfade explizit: ungueltige Eingaben, fehlende Ressourcen, doppelte Aktionen, fehlgeschlagene Persistenz, Autorisierungsfehler bei geforderten Berechtigungen und Empty States.
7. Vermeide hartcodierte Secrets, maschinenspezifische absolute Pfade und umgebungsspezifische Annahmen im Code.
8. Wenn der Tech Stack nicht ausdruecklich vorgegeben ist, waehle den leichtesten stabilen Stack, der die Anforderungen mit der geringsten Betriebskomplexitaet erfuellt.
9. Halte die Implementierung am dokumentierten MVP ausgerichtet und fuege keine spekulative Ueberarchitektur hinzu.
10. Der zentrale Nutzerablauf muss vollstaendig durch UI, API, Servicelogik und Datenbank verdrahtet sein, statt nur in einer Schicht teilweise implementiert zu sein.

Qualitaetspruefungen:
1. Pruefe Imports, Dependency-Deklarationen, Konfigurationsladen, Datenbankerstellung, API-Routing und Frontend-Backend-Integration.
2. Fuege mindestens minimale automatisierte Pruefung fuer den kritischen Pfad hinzu:
   - Backend: mindestens ein oder zwei sinnvolle API-/Service-Tests, wenn eine Testbasis vorhanden ist
   - Frontend: mindestens sicherstellen, dass Hauptseite und wichtiger Interaktionspfad implementiert und lauffaehig sind
3. Behebe offensichtliche Probleme vor Abschluss: fehlende Imports, abweichende Felder, defekte Routen, nicht angelegte Tabellen, ungueltige Seed-Daten, Encoding-Probleme oder Startfehler.
4. Stelle ein klares README bereit mit:
   - Installationsbefehlen
   - Startbefehlen
   - Umgebungsvariablen
   - Datenbank-/Bootstrap-Schritten
   - Test- oder Verifikationsschritten
   - bekannten Annahmen und Trade-offs

Empfohlene Arbeitsreihenfolge:
1. Lies beide Dokumente und leite die Implementierungs-Checkliste ab.
2. Bestaetige Ziel-Stack und Projektstruktur aus den Dokumenten.
3. Implementiere zuerst Datenmodell und Initialisierung.
4. Implementiere Backend-APIs und Servicelogik.
5. Implementiere Frontend-Seiten und integriere sie mit den APIs.
6. Fuege Konfiguration, Demodaten, Tests und README hinzu.
7. Fuehre das Projekt lokal aus und pruefe den kritischen End-to-End-Ablauf.

Erwartete Ausgabe:
- Beginne mit einer Zusammenfassung des Implementierungsplans.
- Implementiere danach den Code.
- Wenn Informationen fehlen, halte nicht an; triff die kleinste sinnvolle Annahme und dokumentiere sie explizit.
- Schliesse mit einer kurzen Liefernotiz ab: was implementiert wurde, wie es gestartet wird, wie es geprueft wird und welche Annahmen bleiben.
"""

IMPLEMENTATION_PROMPT_TEMPLATE_MS = """Anda ialah jurutera full-stack kanan yang bertanggungjawab melaksanakan projek boleh jalan secara ketat berdasarkan dokumen yang diberikan.

Baca fail berikut sepenuhnya sebelum menulis kod:
1. Dokumen PRD: {prd_path}
{design_instruction}

Konteks projek:
- ID sesi: {session_id}
- Tajuk sesi: {session_title}

Peraturan pelaksanaan:
1. Gunakan PRD sebagai sumber kebenaran untuk skop produk, peranan, aliran pengguna, peraturan perniagaan dan jangkaan penerimaan.
2. Jika dokumen reka bentuk sistem tersedia, gunakan sebagai sumber kebenaran untuk seni bina, sempadan modul, kontrak API dan butiran model data; jika tiada, bina pendekatan teknikal paling kecil yang boleh berjalan daripada PRD dan rekod andaian.
3. Jika kedua-dua dokumen bercanggah, selesaikan mengikut keutamaan ini:
   - Skop produk, nilai pengguna dan niat aliran kerja -> PRD
   - Seni bina teknikal, bentuk API, model persistensi dan tanggungjawab modul -> dokumen reka bentuk sistem
   - Jika konflik masih kekal, pilih penyelesaian boleh jalan yang paling konservatif dan minimum, kemudian rekodkan andaian dengan jelas dalam README atau ASSUMPTIONS.md.
4. Jangan cipta ciri besar, integrasi, infrastruktur atau komponen teragih yang kompleks melainkan dokumen memintanya dengan jelas.
5. Jangan keluarkan pseudokod, modul TODO sahaja, handler kosong atau pelaksanaan placeholder untuk aliran teras.

Keperluan pelaksanaan:
1. Sebelum menulis kod, ekstrak senarai semak pelaksanaan yang konkrit merangkumi halaman, modul backend, API, jadual data, background job jika ada dan kriteria penerimaan.
2. Kekalkan nama medan, nilai enum, laluan API, payload request/response dan lajur pangkalan data secara konsisten merentas frontend, backend dan persistensi.
3. Hasilkan projek yang boleh dijalankan secara end-to-end di tempatan, bukan sekadar cebisan kod.
4. Utamakan pustaka yang stabil, arus perdana dan rendah kerumitan. Pastikan dependensi minimum dan dinyatakan dengan jelas.
5. Sediakan semua aset setup yang diperlukan, termasuk manifest dependensi, contoh pemboleh ubah persekitaran, inisialisasi atau migrasi pangkalan data serta data seed/demo jika diperlukan untuk aliran utama.
6. Tangani laluan ralat penting secara eksplisit: input tidak sah, sumber tidak ditemui, tindakan pendua, kegagalan persistensi, ralat autorisasi apabila dokumen memerlukan kebenaran dan keadaan kosong.
7. Elakkan rahsia hard-coded, laluan mutlak khusus mesin atau andaian persekitaran khusus dalam kod.
8. Jika stack teknologi tidak dinyatakan dengan jelas dalam dokumen, pilih stack stabil paling ringan yang boleh memenuhi keperluan dengan kerumitan operasi paling rendah.
9. Kekalkan pelaksanaan sejajar dengan skop MVP yang didokumenkan; jangan tambah over-engineering spekulatif.
10. Perjalanan pengguna utama mesti disambungkan sepenuhnya melalui UI, API, logik servis dan pangkalan data, bukannya dilaksanakan sebahagian pada satu lapisan sahaja.

Pemeriksaan kualiti:
1. Sahkan import, deklarasi dependensi, pemuatan konfigurasi, penciptaan pangkalan data, routing API dan integrasi frontend-backend.
2. Tambah sekurang-kurangnya pengesahan automatik minimum untuk laluan kritikal:
   - backend: sekurang-kurangnya satu atau dua ujian API/service yang bermakna apabila projek mempunyai asas ujian
   - frontend: sekurang-kurangnya pastikan halaman utama dan aliran interaksi penting telah dilaksanakan dan boleh dijalankan
3. Betulkan isu jelas sebelum selesai: import hilang, medan tidak sepadan, route rosak, jadual belum dicipta, data seed tidak sah, isu encoding atau kegagalan startup.
4. Sediakan README yang jelas dengan:
   - arahan pemasangan
   - arahan startup
   - pemboleh ubah persekitaran
   - langkah database/bootstrap
   - langkah ujian atau pengesahan
   - andaian dan trade-off yang diketahui

Urutan kerja yang dicadangkan:
1. Baca kedua-dua dokumen dan hasilkan senarai semak pelaksanaan.
2. Sahkan stack sasaran dan struktur projek daripada dokumen.
3. Laksanakan model data dan inisialisasi terlebih dahulu.
4. Laksanakan API backend dan logik servis.
5. Laksanakan halaman frontend dan integrasikan dengan API.
6. Tambah konfigurasi, data demo, ujian dan README.
7. Jalankan projek secara tempatan dan sahkan aliran end-to-end kritikal.

Jangkaan output:
- Mulakan dengan ringkasan pelan pelaksanaan.
- Kemudian laksanakan kod.
- Jika maklumat tiada, jangan berhenti; buat andaian munasabah paling kecil dan rekodkan dengan jelas.
- Akhiri dengan nota penghantaran ringkas yang menerangkan apa yang dilaksanakan, cara menjalankannya, cara mengesahkannya dan andaian yang masih tinggal.
"""

IMPLEMENTATION_PROMPT_TEMPLATE_ZH = """你是一名资深全栈工程师，现在需要严格依据提供的文档，直接实现一个可运行、可验证的完整项目。

开始编码前，必须先完整阅读以下文件：
1. PRD 文档：{prd_path}
{design_instruction}

项目上下文：
- 会话 ID：{session_id}
- 会话标题：{session_title}

执行规则：
1. 以 PRD 作为产品范围、角色权限、用户流程、业务规则、验收预期的主要依据。
2. 如果存在系统设计文档，则以其作为技术架构、模块边界、API 契约、数据模型、存储设计的主要依据；如果没有，则基于 PRD 推导最小可运行技术方案，并显式记录技术假设。
3. 如果两份文档有冲突，按以下优先级处理：
   - 产品范围、用户价值、业务目标、流程意图 -> 以 PRD 为准
   - 技术架构、接口形式、数据表结构、模块职责 -> 以系统设计文档为准
   - 仍无法消解时，选择“最保守、最小可运行”的方案，并把假设明确写入 README 或 ASSUMPTIONS.md。
4. 不要擅自发明文档没有要求的大型功能、复杂集成、分布式中间件、微服务拆分或过度架构。
5. 不要输出伪代码、仅有 TODO 的模块、空实现、占位接口，核心流程必须真实可用。

实现要求：
1. 写代码前，先提炼出明确的实现清单：页面/功能点、后端模块、API 列表、数据表/字段、关键验收点。
2. 前端字段名、后端 DTO、接口路径、请求响应结构、数据库字段、状态枚举必须保持一致，避免命名漂移。
3. 交付结果必须是“本地可直接运行”的完整项目，而不是零散代码片段。
4. 优先使用稳定、主流、低复杂度依赖，依赖项保持精简且显式声明。
5. 补齐运行所需资产：依赖清单、环境变量示例、数据库初始化/迁移、必要种子数据或演示账号（如主流程需要）。
6. 明确处理关键异常路径：参数错误、资源不存在、重复提交、数据库约束失败、空状态、以及文档要求的权限校验失败。
7. 不要把密钥、绝对本机路径、特定机器配置、硬编码端口假设写死在代码里。
8. 如果文档没有明确技术栈，就选择最轻量、最稳定、最容易本地运行的方案，优先保证可实现和可验证。
9. 实现应严格围绕文档中的 MVP 范围，不要为“看起来高级”而增加非必要复杂度。
10. 主业务闭环必须真正串通 UI、API、服务层、数据库，不能只做静态页面或只写单侧逻辑。

质量门禁：
1. 完成前必须自查并修复：导入错误、缺失依赖、配置读取错误、数据库未初始化、接口路由不通、前后端字段不一致、编码问题、启动失败等明显问题。
2. 至少补充关键路径的最小有效验证：
   - 后端：如果项目已有测试基础，至少补 1 到 2 个有意义的 API/服务测试
   - 前端：至少保证主页面和关键交互路径已经实现且可运行
3. 所有对外接口都要返回清晰、稳定、可预期的状态码和 JSON 结构。
4. 提供清晰 README，至少包含：
   - 安装命令
   - 启动命令
   - 环境变量说明
   - 数据库或初始化步骤
   - 测试/验证步骤
   - 已知假设与取舍说明

建议执行顺序：
1. 阅读两份文档并整理实现清单。
2. 根据文档确认目标技术栈和目录结构。
3. 优先实现数据模型和初始化逻辑。
4. 实现后端 API 与服务层。
5. 实现前端页面并完成接口联调。
6. 补充配置、演示数据、测试、README。
7. 本地运行项目并验证关键端到端流程。

输出要求：
- 先给出实现计划摘要，再开始编码。
- 遇到文档缺失信息时不要停住，基于“最小可运行原则”补充合理假设，并显式记录。
- 最终总结时说明：实现了什么、如何运行、如何验证、剩余假设或未覆盖项是什么。
"""

SUPPORTED_OUTPUT_LANGUAGES = {"en", "de", "zh", "ms"}
IMPLEMENTATION_PROMPT_TEMPLATE_BY_LANGUAGE = {
    "en": IMPLEMENTATION_PROMPT_TEMPLATE_EN,
    "de": IMPLEMENTATION_PROMPT_TEMPLATE_DE,
    "zh": IMPLEMENTATION_PROMPT_TEMPLATE_ZH,
    "ms": IMPLEMENTATION_PROMPT_TEMPLATE_MS,
}
STRUCTURED_REQUIREMENT_CANONICAL_CACHE_KEY = "__canonical__"
STRUCTURED_REQUIREMENT_CANONICAL_FALLBACK_LANGUAGES = ("zh", "en", "de", "ms")
IC_SUBSTRATE_CHAIN_KEYWORDS = (
    "ic substrate",
    "substrate",
    "abf",
    "qdm",
    "finished lot",
    "yield",
    "载板",
    "基板",
    "良率",
    "批次",
    "工序",
    "站点",
    "panel",
)
ACTIVE_IC_SUBSTRATE_DEPARTMENTS = ("production", "quality", "tdi", "general")
CONVERSATION_CHAIN_STATUS_CONFIRMED = "confirmed"
STRUCTURED_REQUIREMENT_PROGRESS_WEIGHTS = {
    "objective": 1.2,
    "scope": 1.0,
    "users": 1.0,
    "scenarios": 1.1,
    "features": 1.4,
    "pages": 0.8,
    "rules": 1.2,
    "integrations": 0.8,
    "acceptance": 1.5,
}
STRUCTURED_REQUIREMENT_GENERATION_CORE_KEYS = (
    "objective",
    "scope",
    "users",
    "scenarios",
    "features",
    "rules",
    "integrations",
)
STRUCTURED_REQUIREMENT_STATUS_READINESS_POINTS = {
    "missing": 0.0,
    "captured": 0.2,
    "pending_confirmation": 0.35,
    "confirmed": 1.0,
    "conflict": 0.0,
}
STRUCTURED_REQUIREMENT_GENERATION_MIN_READINESS = 80
STRUCTURED_REQUIREMENT_GENERATION_MIN_CONFIRMATION = 75
PRD_V0_MINIMUM_USER_SEED_LENGTH = 4
PRD_V0_FAST_DISCOVERY_TARGET_USER_TURNS = 2

DESIGN_DOC_EMPTY_BY_LANGUAGE = {
    "en": "# System Design Document\n\nTBD: no requirement conversation found in this session.",
    "de": "# Systemdesign-Dokument\n\nTBD: In dieser Sitzung wurde noch kein ausreichender Anforderungsdialog gefunden.",
    "zh": "# 系统设计文档\n\nTBD：当前会话中还没有足够的需求对话内容。",
    "ms": "# Dokumen Reka Bentuk Sistem\n\nTBD: belum ada perbualan keperluan yang mencukupi dalam sesi ini.",
}

CHAT_MESSAGE_KIND = "chat"
PRD_MESSAGE_KIND = "prd_doc"
DESIGN_MESSAGE_KIND = "design_doc"
DEFAULT_HANDOFF_TTL_MINUTES = 20

DOCUMENT_TYPE_BY_MESSAGE_KIND = {
    PRD_MESSAGE_KIND: "prd_markdown",
    DESIGN_MESSAGE_KIND: "system_design_markdown",
}

DOCUMENT_FILENAME_LABELS = {
    PRD_MESSAGE_KIND: {
        "en": "Requirements Document",
        "de": "Anforderungsdokument",
        "zh": "需求文档",
        "ms": "Dokumen Keperluan",
    },
    DESIGN_MESSAGE_KIND: {
        "en": "Design Document",
        "de": "Designdokument",
        "zh": "设计文档",
        "ms": "Dokumen Reka Bentuk",
    },
}

DOCX_CONTENT_WIDTH_DXA = 9026
DOCX_BULLET_NUM_ID = 1
DOCX_ORDERED_NUM_ID_START = 2
DOCX_PAGE_WIDTH_DXA = 11906
DOCX_PAGE_HEIGHT_DXA = 16838
DOCX_PAGE_MARGIN_DXA = 1440

CONVERSATION_LABELS = {
    "en": "Requirement conversation messages",
    "de": "Nachrichten aus dem Anforderungsdialog",
    "zh": "需求对话消息",
    "ms": "Mesej perbualan keperluan",
}

SUMMARY_LABELS = {
    "en": "Structured requirement model",
    "de": "Strukturiertes Anforderungsmodell",
    "zh": "结构化摘要",
    "ms": "Model keperluan berstruktur",
}

OUTPUT_LANGUAGE_INSTRUCTIONS = {
    "en": "Output language requirement:\n- Respond entirely in English, including section headings, lists, and tables.",
    "de": "Output language requirement:\n- Respond entirely in German, including section headings, lists, and tables.",
    "zh": "输出语言要求：\n- 全文请使用简体中文输出，包括章节标题、列表和表格。",
    "ms": "Output language requirement:\n- Respond entirely in Bahasa Melayu, including section headings, lists, and tables.",
}

DEFAULT_TECH_STACK_POLICY = """
Default technology stack policy:
- Applies to both Quick and Expert sessions when the user has not explicitly specified a stack.
- Frontend: static pages (HTML/CSS/vanilla JavaScript; no frontend framework by default)
- Backend: C#
- Database: SQLite
- Treat this as a requirement/design constraint. In normal PM conversation, discuss and record the stack only; do not write implementation code.
"""

DEFAULT_TECH_STACK_POLICY_ZH = """
默认技术栈策略：
- 当用户没有明确指定技术栈时，快速模式和专家模式都使用同一套默认技术栈。
- 前端：静态页面（HTML/CSS/原生 JavaScript；默认不引入前端框架）
- 后端：C#
- 数据库：SQLite
- 这只是需求/设计约束。在普通 PM 对话中只讨论和记录技术栈，不编写实现代码。
"""

PERSONAL_PROJECT_PM_ADDENDUM = """
Project template: personal project demo.
Assume the default implementation stack is:
- Frontend: static pages (HTML/CSS/vanilla JavaScript; no frontend framework by default)
- Backend: C#
- Database: SQLite

Constraint profile for this template:
- Prioritize single-developer delivery and fast implementation.
- Treat the target as a demo / MVP / personal project unless the user explicitly asks for production-grade complexity.
- Do not optimize for high concurrency, multi-region deployment, distributed systems, or enterprise-scale governance by default.
- Prefer a single deployable application shape with simple REST APIs and straightforward module boundaries.
- Focus requirement discovery on pages, core flows, data tables, API contracts, and minimal deployment/testing needs.
- Only raise advanced concerns such as caching, queues, horizontal scaling, complex permissions, or heavy observability when the user explicitly needs them.

Scenario discovery modules:
- For chart, dashboard, report, or visualization requirements, collect chart type, data source, key fields, field logic, dimensions/metrics/axes, filters, detail data, and chart interactions.
- For multiple-chart requirements, also collect chart relationships, data-source correlations, linked filtering, drill-down, tab switching, and the intended layout pattern.
- For process, workflow, approval, to-do, history, configuration, or permission-management requirements, collect triggers, roles, process nodes, node actions, status changes, exception paths, related pages, and permission rules.
"""

PERSONAL_PROJECT_PM_ADDENDUM_ZH = """
项目模板：个人项目 Demo 版。
默认实现技术栈假设为：
- 前端：静态页面（HTML/CSS/原生 JavaScript；默认不引入前端框架）
- 后端：C#
- 数据库：SQLite

该模板的约束偏好：
- 优先支持单人开发、快速落地。
- 除非用户明确提出更高要求，否则默认目标是 Demo / MVP / 个人项目，而不是企业级生产系统。
- 默认不重点考虑高并发、多地域部署、分布式系统、复杂中间件和重型治理要求。
- 优先采用单体、易部署、REST API 清晰、模块边界简单直接的方案。
- 需求采集重点放在页面、核心流程、数据表、接口约定，以及最小可用的部署/测试方式上。
- 只有当用户明确提出时，才深入追问缓存、消息队列、水平扩展、复杂权限体系、重型可观测性等高级能力。

场景采集模块：
- 遇到图表、看板、报表或可视化需求时，采集图表类型、数据来源、关键字段、字段逻辑、维度/指标/坐标轴、筛选条件、明细数据和图表交互。
- 遇到多图表需求时，额外采集图表关系、数据源关联、联动筛选、下钻、标签切换和期望布局模式。
- 遇到流程、工作流、审批、待办、历史记录、配置或权限管理需求时，采集触发条件、角色、流程节点、节点操作、状态变化、异常路径、相关页面和权限规则。
"""

PERSONAL_PROJECT_DESIGN_DOC_ADDENDUM = """
Solution template: personal project demo.
Target implementation stack:
- Frontend: static pages (HTML/CSS/vanilla JavaScript; no frontend framework by default)
- Backend: C#
- Database: SQLite

Document constraints:
- Produce a design suitable for a personal project / demo / MVP.
- Default to a simple monolithic structure unless the user explicitly asks otherwise.
- Do not introduce high-concurrency architecture, distributed services, message queues, service mesh, read-write splitting, or other enterprise-scale mechanisms unless explicitly required.
- API design should be pragmatic and lightweight, suitable for C# REST endpoints.
- Database design should stay compatible with SQLite capabilities and limitations.
- Deployment should favor local development and low-cost simple hosting.
- Security, observability, and testing should be right-sized for a demo, while still calling out basic minimum good practices.
"""

PERSONAL_PROJECT_DESIGN_DOC_ADDENDUM_ZH = """
方案模板：个人项目 Demo 版。
目标实现技术栈：
- 前端：静态页面（HTML/CSS/原生 JavaScript；默认不引入前端框架）
- 后端：C#
- 数据库：SQLite

文档约束：
- 生成的设计文档应服务于个人项目 / Demo / MVP 落地。
- 除非用户明确要求，否则默认采用简单单体结构。
- 不要默认引入高并发架构、分布式服务、消息队列、服务网格、读写分离等企业级复杂机制。
- API 设计应务实轻量，适合 C# REST 接口实现。
- 数据库设计要兼容 SQLite 的能力和限制。
- 部署方案优先本地开发与低成本、简单托管。
- 安全、可观测性、测试方案要符合 Demo 尺度，但仍需给出基本的最低实践建议。
"""

PERSONAL_PROJECT_PM_ADDENDUM_V2 = """
Project template: personal project demo.
Do not treat the technology stack as fixed.
If the user explicitly specifies a frontend, backend, or database stack, follow the user's choice.
Only when the user does not specify a stack, default to a lightweight personal-project stack selected from:
- Frontend: static pages (HTML/CSS/vanilla JavaScript; no frontend framework by default)
- Backend: C#
- Database: SQLite

Constraint profile for this template:
- Prioritize single-developer delivery and fast implementation.
- Treat the target as a demo / MVP / personal project unless the user explicitly asks for production-grade complexity.
- Do not optimize for high concurrency, multi-region deployment, distributed systems, or enterprise-scale governance by default.
- Prefer a single deployable application shape with simple REST APIs and straightforward module boundaries.
- Focus requirement discovery on pages, core flows, data tables, API contracts, and minimal deployment/testing needs.
- Only raise advanced concerns such as caching, queues, horizontal scaling, complex permissions, or heavy observability when the user explicitly needs them.

Scenario discovery modules:
- For chart, dashboard, report, or visualization requirements, collect chart type, data source, key fields, field logic, dimensions/metrics/axes, filters, detail data, and chart interactions.
- For multiple-chart requirements, also collect chart relationships, data-source correlations, linked filtering, drill-down, tab switching, and the intended layout pattern.
- For process, workflow, approval, to-do, history, configuration, or permission-management requirements, collect triggers, roles, process nodes, node actions, status changes, exception paths, related pages, and permission rules.
"""

PERSONAL_PROJECT_PM_ADDENDUM_ZH_V2 = """
项目模板：个人项目 Demo 版。
不要把技术栈视为固定不变。
如果用户明确指定了前端、后端或数据库技术栈，优先遵循用户选择。
只有当用户没有指定技术栈时，才默认从以下轻量个人项目技术栈中选择：
- 前端：静态页面（HTML/CSS/原生 JavaScript；默认不引入前端框架）
- 后端：C#
- 数据库：SQLite

该模板的约束偏好：
- 优先支持单人开发、快速落地。
- 除非用户明确提出更高要求，否则默认目标是 Demo / MVP / 个人项目，而不是企业级生产系统。
- 默认不重点考虑高并发、多地域部署、分布式系统、复杂中间件和重型治理要求。
- 优先采用单体、易部署、REST API 清晰、模块边界简单直接的方案。
- 需求采集重点放在页面、核心流程、数据表、接口约定，以及最小可用的部署/测试方式上。
- 只有当用户明确提出时，才深入追问缓存、消息队列、水平扩展、复杂权限体系、重型可观测性等高级能力。

场景采集模块：
- 遇到图表、看板、报表或可视化需求时，采集图表类型、数据来源、关键字段、字段逻辑、维度/指标/坐标轴、筛选条件、明细数据和图表交互。
- 遇到多图表需求时，额外采集图表关系、数据源关联、联动筛选、下钻、标签切换和期望布局模式。
- 遇到流程、工作流、审批、待办、历史记录、配置或权限管理需求时，采集触发条件、角色、流程节点、节点操作、状态变化、异常路径、相关页面和权限规则。
"""

PERSONAL_PROJECT_DESIGN_DOC_ADDENDUM_V2 = """
Solution template: personal project demo.
Do not hard-code the technology stack.
If the user explicitly specifies the frontend, backend, or database stack, generate the design around that stack.
Only when the user does not specify a stack, default to a lightweight implementation selected from:
- Frontend: static pages (HTML/CSS/vanilla JavaScript; no frontend framework by default)
- Backend: C#
- Database: SQLite

Document constraints:
- Produce a design suitable for a personal project / demo / MVP.
- Default to a simple monolithic structure unless the user explicitly asks otherwise.
- Do not introduce high-concurrency architecture, distributed services, message queues, service mesh, read-write splitting, or other enterprise-scale mechanisms unless explicitly required.
- API design should match the chosen backend stack; if the default stack is used, prefer pragmatic C# REST endpoints.
- Database design should match the chosen database stack; if the default stack is used, stay compatible with SQLite capabilities and limitations.
- Deployment should favor local development and low-cost simple hosting.
- Security, observability, and testing should be right-sized for a demo, while still calling out basic minimum good practices.

Chart and process guidance:
- If the requirement includes charts, define the chart data contract: data source, key fields, field logic, dimensions/metrics/axes, filters, detail data, and interactions.
- For multiple charts, recommend an appropriate page layout from these examples: Uniform Grid for peer-level dashboard cards; Primary-Detail / Hero for one key chart plus supporting charts; Nested / Drill-down for linked exploratory analysis; Tabbed for homogeneous chart views such as Day/Week/Month; Masonry / Waterfall for mixed reports or mobile feed-style pages, used cautiously in dashboards.
- If the requirement includes a business process, include the process trigger, roles, nodes, node actions, status changes, exception/return/termination paths, initiation page, to-do list, detail/history page, configuration, and permission management.
"""

PERSONAL_PROJECT_DESIGN_DOC_ADDENDUM_ZH_V2 = """
方案模板：个人项目 Demo 版。
不要把技术栈写死。
如果用户明确指定了前端、后端或数据库技术栈，生成设计文档时优先围绕用户指定技术栈展开。
只有当用户没有指定技术栈时，才默认从以下轻量实现中选择：
- 前端：静态页面（HTML/CSS/原生 JavaScript；默认不引入前端框架）
- 后端：C#
- 数据库：SQLite

文档约束：
- 生成的设计文档应服务于个人项目 / Demo / MVP 落地。
- 除非用户明确要求，否则默认采用简单单体结构。
- 不要默认引入高并发架构、分布式服务、消息队列、服务网格、读写分离等企业级复杂机制。
- API 设计要和已选后端技术栈保持一致；如果使用默认栈，则优先用轻量、务实的 C# REST 接口。
- 数据库设计要和已选数据库技术栈保持一致；如果使用默认栈，则优先兼容 SQLite 的能力和限制。
- 部署方案优先本地开发与低成本、简单托管。
- 安全、可观测性、测试方案要符合 Demo 尺度，但仍需给出基本的最低实践建议。

图表与流程指导：
- 如果需求包含图表，请明确图表数据契约：数据来源、关键字段、字段逻辑、维度/指标/坐标轴、筛选条件、明细数据和交互方式。
- 如果需求包含多个图表，请根据数据层级、对比关系和页面空间推荐合适布局：同级看板卡片优先 Uniform Grid / 统一网格；一个核心指标或趋势优先 Primary-Detail / Hero 主次布局；联动探索分析优先 Nested / Drill-down 嵌套下钻；日/周/月等同质视图优先 Tabbed 标签页；混合报告、移动 H5 或资讯流可参考 Masonry / Waterfall 瀑布流，但数据看板中需谨慎使用以避免杂乱。
- 如果需求包含业务流程，请补充流程触发条件、角色、节点、节点操作、状态变化、异常/退回/终止路径、发起页、待办列表、详情与历史页、配置和权限管理。
"""


@dataclass
class Session:
    id: str
    created_at: str
    updated_at: str
    title: str = ""
    prompt_template: str = PROMPT_TEMPLATE_PERSONAL_PROJECT
    applied_template_id: str = ""
    applied_template_name: str = ""
    start_function: str = START_FUNCTION_FROM_SCRATCH
    messages: list[dict[str, Any]] = field(default_factory=list)


class RequirementCollectorService:
    def __init__(self, llm_client: MiniMaxChatClient, session_store: SQLiteSessionStore) -> None:
        self.llm_client = llm_client
        self.session_store = session_store
        self.design_docs_dir = self.session_store.db_path.parent / "design_docs"
        self.prd_docs_dir = self.session_store.db_path.parent / "prd_docs"
        self.prd_templates_dir = Path(__file__).resolve().parents[2] / "data" / "PRD_template"
        self.business_template_library = BusinessTemplateLibrary(self.prd_templates_dir)
        self._lock = threading.Lock()

    def create_session(
        self,
        template_id: str | None = None,
        language: str = "zh",
        template_start_mode: str = TEMPLATE_START_MODE_GUIDED,
        starter_department: str | None = None,
        start_function: str | None = START_FUNCTION_FROM_SCRATCH,
    ) -> Session:
        session_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()
        normalized_language = self._normalize_language(language)
        normalized_start_function = self._normalize_start_function(start_function)
        applied_template_id = ""
        applied_template_name = ""
        title = ""
        template_detail: dict[str, Any] | None = None

        if template_id:
            template_detail = self.business_template_library.get_localized_template(
                template_id,
                normalized_language,
            )
            if template_detail is None:
                raise KeyError("Business template not found.")
            applied_template_id = template_detail["template_id"]
            applied_template_name = template_detail["template_name"]
            title = applied_template_name

        record = self.session_store.create_session(
            session_id=session_id,
            created_at=created_at,
            title=title,
            applied_template_id=applied_template_id,
            applied_template_name=applied_template_name,
            start_function=normalized_start_function,
        )
        starter_department_key = self._normalize_ic_substrate_starter_department(starter_department)
        if starter_department_key and (
            template_detail is None or self._template_matches_ic_substrate_focus(template_detail)
        ):
            self._seed_session_from_starter_department(
                session_id=session_id,
                department=starter_department_key,
                language=normalized_language,
                start_function=normalized_start_function,
            )
            record = self.session_store.get_session(session_id)
            if record is None:
                raise RuntimeError("Failed to load starter-department session.")
        return self._session_from_record(record)

    def _normalize_ic_substrate_starter_department(self, department: str | None) -> str:
        normalized = str(department or "").strip().lower()
        aliases = {
            "production": "production",
            "prod": "production",
            "quality": "quality",
            "qdm": "quality",
            "tdi": "tdi",
            "general": "general",
        }
        return aliases.get(normalized, "")

    def _seed_session_from_starter_department(
        self,
        session_id: str,
        department: str,
        language: str,
        start_function: str = START_FUNCTION_FROM_SCRATCH,
    ) -> None:
        model = self._empty_structured_requirement_model()
        department_label = self._ic_substrate_department_label(department, language)
        model["product_context"]["requesting_department"] = department_label
        normalized_language = self._normalize_language(language)
        draft_mode = self._normalize_start_function(start_function) == START_FUNCTION_IMPROVE_DRAFT
        intake_question = self._prd_v0_intake_pack_open_question(department_label, normalized_language)
        if normalized_language == "zh":
            model["background"]["summary"] = (
                f"用户已选择 {department_label} 作为首版 IC Substrate 专业链路入口，"
                "并将基于半成品需求书逐步补齐 PRD 缺口。"
                if draft_mode
                else f"用户已选择 {department_label} 作为首版 IC Substrate 专业链路入口。"
            )
            model["open_questions"] = [
                f"请上传或确认半成品需求书中的已明确内容、待确认假设、缺失项和冲突项。"
                if draft_mode
                else intake_question
            ]
        elif normalized_language == "de":
            model["background"]["summary"] = (
                f"Der Nutzer hat {department_label} als First-Version Einstieg gewaehlt und moechte einen vorhandenen Draft zur PRD-Reife bringen."
                if draft_mode
                else f"Der Nutzer hat {department_label} als First-Version Einstieg fuer die IC Substrate Expertenkette gewaehlt."
            )
            model["open_questions"] = [
                "Bestaetige die bereits klaren Punkte, Annahmen, Luecken und Konflikte aus dem Draft."
                if draft_mode
                else intake_question
            ]
        elif normalized_language == "ms":
            model["background"]["summary"] = (
                f"Pengguna memilih {department_label} sebagai entry versi pertama dan mahu melengkapkan draft requirement kepada PRD."
                if draft_mode
                else f"Pengguna memilih {department_label} sebagai entry versi pertama untuk rantaian pakar IC Substrate."
            )
            model["open_questions"] = [
                "Sahkan perkara yang jelas, assumption, gap dan konflik daripada draft requirement."
                if draft_mode
                else intake_question
            ]
        else:
            model["background"]["summary"] = (
                f"The user selected {department_label} as the first-version entry and will improve a draft requirement into a PRD-ready spec."
                if draft_mode
                else f"The user selected {department_label} as the first-version entry for the IC Substrate expert chain."
            )
            model["open_questions"] = [
                "Confirm the facts, assumptions, missing gaps, and conflicts found in the draft requirement."
                if draft_mode
                else intake_question
            ]
        if draft_mode:
            model["risks_and_notes"].append(
                "Draft completion mode: attachment-derived facts are pending until the user confirms them."
            )
        self._save_structured_requirement_model_cache(
            session_id=session_id,
            cache_key=STRUCTURED_REQUIREMENT_CANONICAL_CACHE_KEY,
            message_count=0,
            structured_requirement_model=model,
        )
        self._save_structured_requirement_model_cache(
            session_id=session_id,
            cache_key=self._normalize_language(language),
            message_count=0,
            structured_requirement_model=model,
        )

    def _prd_v0_intake_pack_open_question(self, department_label: str, language: str) -> str:
        normalized_language = self._normalize_language(language)
        if normalized_language == "zh":
            return (
                f"专家链路启动问题：请用一句话或 A/B/C + 补充，先确认 {department_label} 首版最关键的 5 个信息："
                "business_action、primary_user_or_owner、source_of_truth、integration_writeback_boundary、acceptance_evidence；"
                "unknown is OK，未知项会作为待确认假设继续追问，不会直接开放 Go Coding。"
            )
        if normalized_language == "de":
            return (
                f"Expertenketten-Startfrage: Bitte mit einem Satz oder A/B/C + Freitext die 5 wichtigsten Punkte fuer {department_label} klaeren: "
                "business_action, primary_user_or_owner, source_of_truth, integration_writeback_boundary, acceptance_evidence; "
                "unknown is OK; Unbekanntes bleibt pending assumption und oeffnet Go Coding noch nicht."
            )
        if normalized_language == "ms":
            return (
                f"Soalan mula expert chain: jawab dengan satu ayat atau A/B/C + teks ringkas untuk 5 maklumat utama {department_label}: "
                "business_action, primary_user_or_owner, source_of_truth, integration_writeback_boundary, acceptance_evidence; "
                "unknown is OK; perkara tidak pasti kekal sebagai assumption belum sah dan belum membuka Go Coding."
            )
        return (
            f"Expert-chain starter question: answer in one sentence or A/B/C + free text for the 5 key fields in {department_label}: "
            "business_action, primary_user_or_owner, source_of_truth, integration_writeback_boundary, acceptance_evidence; "
            "unknown is OK; unknowns stay pending assumptions and do not unlock Go Coding yet."
        )

    def get_session(self, session_id: str) -> Session | None:
        record = self.session_store.get_session(session_id)
        if record is None:
            return None
        return self._session_from_record(record)

    def list_sessions(self) -> list[dict[str, Any]]:
        return self.session_store.list_sessions()

    def list_business_templates(self) -> list[dict[str, Any]]:
        return self.business_template_library.list_templates()

    def get_business_template(self, template_id: str) -> dict[str, Any] | None:
        return self.business_template_library.get_template(template_id)

    def _first_string_from_paths(self, payload: dict[str, Any], paths: tuple[str, ...]) -> str:
        for path in paths:
            value = self._value_at_path(payload, path)
            text = self._first_non_empty_string(value)
            if text:
                return text
        return ""

    def _first_joined_strings_from_paths(self, payload: dict[str, Any], paths: tuple[str, ...]) -> str:
        for path in paths:
            values = self._flatten_path_strings(payload, path)
            if values:
                return "; ".join(values)
        return ""

    def _first_string_list_from_paths(self, payload: dict[str, Any], paths: tuple[str, ...]) -> list[str]:
        for path in paths:
            values = self._flatten_path_strings(payload, path)
            if values:
                return values
        return []

    def _flatten_path_strings(self, payload: dict[str, Any], path: str) -> list[str]:
        value = self._value_at_path(payload, path)
        return self._flatten_strings(value)

    def _flatten_strings(self, value: Any) -> list[str]:
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
                values.extend(self._flatten_strings(item))
            return self._unique_strings(values)
        if isinstance(value, dict):
            label_keys = (
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
            parts = [str(value.get(key, "")).strip() for key in label_keys if str(value.get(key, "")).strip()]
            if parts:
                return [" - ".join(parts)]
            values: list[str] = []
            for item in value.values():
                values.extend(self._flatten_strings(item))
            return self._unique_strings(values)
        return []

    def _value_at_path(self, payload: dict[str, Any], path: str) -> Any:
        current: Any = payload
        for part in path.split("."):
            if not isinstance(current, dict):
                return None
            current = current.get(part)
        return current

    def _first_non_empty_string(self, *values: Any) -> str:
        for value in values:
            if isinstance(value, str) and value.strip():
                return value.strip()
            if isinstance(value, (int, float, bool)):
                return str(value)
        return ""

    def _string_list(self, value: Any) -> list[str]:
        if isinstance(value, list):
            return self._unique_strings(self._flatten_strings(value))
        if isinstance(value, str):
            cleaned = value.strip()
            return [cleaned] if cleaned else []
        if value is None:
            return []
        return self._flatten_strings(value)

    def _unique_strings(self, values: list[str]) -> list[str]:
        seen: set[str] = set()
        unique: list[str] = []
        for value in values:
            normalized = " ".join(str(value).split())
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            unique.append(normalized)
        return unique


    def delete_session(self, session_id: str) -> bool:
        return self.session_store.delete_session(session_id)

    def update_session_prompt_template(self, session_id: str, prompt_template: str) -> Session:
        session = self.get_session(session_id)
        if session is None:
            raise KeyError("Session not found.")
        if session.applied_template_id:
            raise ValueError("Prompt template is managed by the applied business template.")
        if self._session_has_user_messages(session):
            raise ValueError("Prompt template can only be changed before the first user message.")

        normalized_template = self._normalize_prompt_template(prompt_template)
        self.session_store.update_session_prompt_template(session_id, normalized_template)
        return self._require_session(session_id)

    def send_user_message(
        self,
        session_id: str,
        user_message: str,
        language: str = "zh",
        display_message: str = "",
    ) -> dict[str, Any]:
        session = self.get_session(session_id)
        if session is None:
            raise KeyError("Session not found.")

        response_language = self._language_for_user_message(language, user_message)
        self._append_message(session_id, "user", user_message, display_content=display_message)
        if not self._session_has_user_messages(session):
            self._update_session_title_from_message(session_id, display_message or user_message, response_language)
        session = self._require_session(session_id)
        # Build the structured model from the latest turn first, so the readiness-state
        # directive injected into the prompt reflects the current gate state. The LLM drives
        # the conversation; the directive constrains it up front and the guard backstops it.
        self._build_and_cache_structured_requirement_model(
            session,
            response_language,
            force_refresh=True,
        )
        system_prompt = self._pm_prompt(session, response_language)
        llm_messages = self._build_llm_messages(system_prompt, session.messages)
        assistant_text_raw = self.llm_client.chat(llm_messages)
        assistant_text, thinking_text = self._split_thinking(assistant_text_raw)
        assistant_text = self._ensure_choice_question_format(assistant_text, response_language)
        assistant_text = self._guard_assistant_readiness_response(
            session_id,
            assistant_text,
            response_language,
        )

        self._append_message(session_id, "assistant", assistant_text, thinking_text)
        session = self._require_session(session_id)

        structured_requirement_model = self._promote_cached_structured_requirement_model(session, response_language)
        conversation_chain_state = self.build_conversation_chain_state(
            session,
            structured_requirement_model,
            response_language,
        )
        pm_methodology_state = self.build_pm_methodology_state(
            structured_requirement_model,
            response_language,
        )
        ic_substrate_evidence_state = self.build_ic_substrate_evidence_state(
            session,
            structured_requirement_model,
            response_language,
        )
        return {
            "assistant_message": assistant_text,
            "assistant_thinking": thinking_text,
            "summary": structured_requirement_model,
            "structured_requirement_model": structured_requirement_model,
            "structured_requirement_sync_status": "ready",
            "conversation_chain_state": conversation_chain_state,
            "pm_methodology_state": pm_methodology_state,
            "ic_substrate_evidence_state": ic_substrate_evidence_state,
            "session_id": session.id,
            "message_count": len(session.messages),
        }

    def stream_user_message(
        self,
        session_id: str,
        user_message: str,
        language: str = "zh",
        display_message: str = "",
    ) -> Iterator[dict[str, Any]]:
        session = self.get_session(session_id)
        if session is None:
            raise KeyError("Session not found.")

        response_language = self._language_for_user_message(language, user_message)
        self._append_message(session_id, "user", user_message, display_content=display_message)
        if not self._session_has_user_messages(session):
            self._update_session_title_from_message(session_id, display_message or user_message, response_language)
        session = self._require_session(session_id)
        # Build the structured model from the latest turn first, so the readiness-state
        # directive injected into the prompt reflects the current gate state. The LLM drives
        # the conversation; the directive constrains it up front and the guard backstops it.
        self._build_and_cache_structured_requirement_model(
            session,
            response_language,
            force_refresh=True,
        )

        assistant_text_parts: list[str] = []
        thinking_parts: list[str] = []
        system_prompt = self._pm_prompt(session, response_language)
        llm_messages = self._build_llm_messages(system_prompt, session.messages)
        for item in self.llm_client.stream_chat(llm_messages):
            text = item.get("text", "")
            if not text:
                continue

            if item.get("type") == "thinking":
                thinking_parts.append(text)
                yield {"event": "thinking", "delta": text}
                continue

            assistant_text_parts.append(text)
            yield {"event": "content", "delta": text}

        assistant_text = "".join(assistant_text_parts).strip()
        thinking_text = "".join(thinking_parts).strip()
        assistant_text, content_embedded_thinking = self._split_thinking(assistant_text)
        if content_embedded_thinking:
            thinking_text = f"{thinking_text}\n{content_embedded_thinking}".strip()
        if not assistant_text:
            raise LLMError("LLM returned empty streamed content.")
        formatted_assistant_text = self._ensure_choice_question_format(assistant_text, response_language)
        if formatted_assistant_text != assistant_text:
            assistant_delta = (
                formatted_assistant_text[len(assistant_text):]
                if formatted_assistant_text.startswith(assistant_text)
                else f"\n\n{formatted_assistant_text}"
            )
            yield {"event": "content", "delta": assistant_delta}
            assistant_text = formatted_assistant_text

        guarded_assistant_text = self._guard_assistant_readiness_response(
            session_id,
            assistant_text,
            response_language,
        )
        if guarded_assistant_text != assistant_text:
            yield {"event": "replace_content", "content": guarded_assistant_text}
            assistant_text = guarded_assistant_text

        self._append_message(session_id, "assistant", assistant_text, thinking_text)
        session = self._require_session(session_id)

        if thinking_text:
            yield {"event": "thinking_done", "thinking": thinking_text}
        yield {"event": "assistant_done", "session_id": session.id, "message_count": len(session.messages)}

        structured_requirement_model = self._promote_cached_structured_requirement_model(session, response_language)
        conversation_chain_state = self.build_conversation_chain_state(
            session,
            structured_requirement_model,
            response_language,
        )
        pm_methodology_state = self.build_pm_methodology_state(
            structured_requirement_model,
            response_language,
        )
        ic_substrate_evidence_state = self.build_ic_substrate_evidence_state(
            session,
            structured_requirement_model,
            response_language,
        )
        yield {
            "event": "summary",
            "session_id": session.id,
            "message_count": len(session.messages),
            "summary": structured_requirement_model,
            "structured_requirement_model": structured_requirement_model,
            "structured_requirement_sync_status": "ready",
            "conversation_chain_state": conversation_chain_state,
            "pm_methodology_state": pm_methodology_state,
            "ic_substrate_evidence_state": ic_substrate_evidence_state,
        }
        yield {
            "event": "done",
            "session_id": session.id,
            "message_count": len(session.messages),
            "structured_requirement_sync_status": "ready",
        }

    def build_session_summary(self, session_id: str, language: str = "zh") -> dict[str, Any]:
        return self.build_structured_requirement_model(session_id, language)

    def build_structured_requirement_model(
        self,
        session_id: str,
        language: str = "zh",
        force_refresh: bool = False,
    ) -> dict[str, Any]:
        session = self.get_session(session_id)
        if session is None:
            raise KeyError("Session not found.")
        normalized_language = self._normalize_language(language)
        message_count = self._message_count(session.messages)
        if not force_refresh:
            cached_model = self._get_cached_localized_structured_requirement_model(
                session_id,
                normalized_language,
                message_count,
            )
            if cached_model is not None:
                return cached_model
        return self._build_and_cache_structured_requirement_model(
            session,
            normalized_language,
            force_refresh=force_refresh,
        )

    def build_pm_methodology_state(
        self,
        structured_requirement_model: dict[str, Any] | None,
        language: str = "zh",
    ) -> dict[str, Any]:
        return build_pm_methodology_state_payload(
            structured_requirement_model,
            self._normalize_language(language),
        )

    def _pm_methodology_ready_for_generation(
        self,
        structured_requirement_model: dict[str, Any] | None,
        language: str = "zh",
    ) -> tuple[bool, dict[str, Any]]:
        pm_methodology_state = self.build_pm_methodology_state(
            structured_requirement_model,
            language,
        )
        # PM Methodology is ADVISORY: the state (score, checks, gaps) is still returned for the
        # right-panel display and to enrich the PRD, but it never gates document generation or
        # Go Coding. The only hard gate is the structured "Fully Confirmed" state. Gating on the
        # heuristic methodology checks made the conversation circle forever, so the readiness
        # boolean is always True here.
        ready = True
        return ready, pm_methodology_state

    def _guard_assistant_readiness_response(
        self,
        session_id: str,
        assistant_text: str,
        language: str,
    ) -> str:
        stripped = assistant_text.strip()
        if not stripped:
            return stripped

        claims_generation_ready = self._assistant_claims_document_generation_ready(stripped)
        continues_readiness_discovery = self._assistant_continues_readiness_discovery(stripped, language)
        if not claims_generation_ready and not continues_readiness_discovery:
            return assistant_text

        session = self.get_session(session_id)
        if session is None:
            raise KeyError("Session not found.")

        structured_requirement_model = self.build_structured_requirement_model(session_id, language)
        progress = self._structured_requirement_progress(structured_requirement_model)
        _, pm_methodology_state = self._pm_methodology_ready_for_generation(
            structured_requirement_model,
            language,
        )
        # Generate Documents unlocks on the structured "Fully Confirmed" gate alone - the same
        # bar the right-side button uses. PM Methodology is advisory and must not block, or the
        # conversation circles forever on heuristic checks that never reach "ready".
        if progress.get("ready_to_generate"):
            if continues_readiness_discovery or self._assistant_points_to_document_generation(
                session_id,
                stripped,
                language,
            ):
                return self._build_ready_phase_follow_up(session_id, language)
            return assistant_text

        if not claims_generation_ready:
            return assistant_text

        return self._build_readiness_gate_follow_up(
            structured_requirement_model,
            progress,
            pm_methodology_state,
            language,
        )

    def _assistant_continues_readiness_discovery(self, text: str, language: str) -> bool:
        stripped = text.strip()
        if not stripped:
            return False
        lowered = stripped.lower()
        if self._looks_like_clarification_question(stripped, language):
            return True
        if self._has_choice_options(stripped):
            return True
        discovery_patterns = (
            r"\bchoose one option\b",
            r"\bkeep this point pending\b",
            r"\bi will provide the real\b",
            r"\bprovide the real business wording\b",
            r"\bplease confirm\b",
            r"\bonce confirmed\b",
            r"\bdoes this (set|match|work)\b",
            r"(请选择|选择一个|请确认|确认这个|保持待确认|稍后提供|后面提供)",
            r"(bitte bestaetigen|waehlen sie eine option|bitte eine option|offen halten)",
            r"(sila sahkan|pilih satu pilihan|kekalkan.*tertunda)",
        )
        return any(re.search(pattern, lowered, flags=re.IGNORECASE) for pattern in discovery_patterns)

    def _assistant_points_to_document_generation(self, session_id: str, text: str, language: str) -> bool:
        if self.get_saved_prd_document(session_id) is None:
            return False
        stripped = text.strip()
        if not stripped:
            return False
        lowered = stripped.lower()
        if self._normalize_language(language) == "zh":
            return bool(
                re.search(r"(下一步|请|点击|可以)[\s\S]{0,40}(生成文档|generate documents|生成正式需求文档)", lowered)
            )
        return bool(
            re.search(
                r"(next step|click|please|you can|can now)[\s\S]{0,80}"
                r"(generate documents|generate (?:the )?(?:formal )?(?:requirements? )?document|"
                r"create (?:the )?(?:formal )?(?:requirements? )?document|document generation)",
                lowered,
                flags=re.IGNORECASE,
            )
        )

    def _build_ready_phase_follow_up(self, session_id: str, language: str) -> str:
        normalized = self._normalize_language(language)
        has_prd_document = self.get_saved_prd_document(session_id) is not None
        if has_prd_document:
            if normalized == "zh":
                return (
                    "需求文档已经生成完成。请点击右侧 Go Coding / Open Vibe Coding 进入编码交接；"
                    "只有范围变化或出现冲突时才需要继续补充。"
                )
            if normalized == "de":
                return (
                    "Das Requirement-Dokument ist erzeugt. Klicke rechts auf Go Coding / Open Vibe Coding "
                    "fuer die Coding-Uebergabe; weitere Klaerung ist nur bei Scope-Aenderung oder Konflikt noetig."
                )
            if normalized == "ms":
                return (
                    "Dokumen requirement sudah dijana. Klik Go Coding / Open Vibe Coding di sebelah kanan "
                    "untuk handoff coding; tambah maklumat hanya jika scope berubah atau ada konflik."
                )
            return (
                "The requirements document has been generated. Click Go Coding / Open Vibe Coding on the right "
                "to start the coding handoff; only add more details if the scope changes or a conflict appears."
            )

        if normalized == "zh":
            return (
                "结构化需求已经全部确认。请点击右侧 Generate Documents / 生成文档 生成正式需求文档；"
                "文档生成后再进入 Go Coding / Vibe Coding 交接。"
            )
        if normalized == "de":
            return (
                "Alle strukturierten Anforderungen sind bestaetigt. Klicke rechts auf Generate Documents / "
                "Dokumente erzeugen, um das formale Requirement-Dokument zu erstellen; danach folgt Go Coding / Vibe Coding."
            )
        if normalized == "ms":
            return (
                "Semua requirement berstruktur sudah disahkan. Klik Generate Documents / Jana Dokumen di sebelah kanan "
                "untuk menjana dokumen rasmi; selepas itu barulah Go Coding / Vibe Coding."
            )
        return (
            "All structured requirements are confirmed. Click Generate Documents on the right to generate the formal "
            "requirements document; after the document exists, use Go Coding / Vibe Coding for the handoff."
        )

    def _assistant_claims_document_generation_ready(self, text: str) -> bool:
        lowered = text.strip().lower()
        if not lowered:
            return False
        # Broad on purpose: this only triggers a rewrite when the gates are NOT passed
        # (see _guard_assistant_readiness_response), and the rewrite target is always a
        # correct "not ready, here is the next gap" message. So catching any offer/mention
        # of generating the document or starting Go Coding is safe, and stops premature CTAs
        # from leaking when the model ignores the readiness directive.
        readiness_patterns = (
            r"\b(enough|sufficient|complete|ready)\b[\s\S]{0,80}\b(generate|document|prd|urd|handoff)\b",
            r"\bclick\b[\s\S]{0,40}\b(generate|document|documents|prd|urd)\b",
            r"\brequirements?\b[\s\S]{0,40}\b(ready|complete|enough|sufficient)\b",
            r"\b(finalize|finalise)\b[\s\S]{0,80}\b(requirements?|documented requirements|prd|urd)\b",
            r"\bhandoff readiness\b[\s\S]{0,120}\b(generate|document|documents|prd|urd|handoff)\b",
            r"\b(generate|create|produce|draft)\b[\s\S]{0,40}\b(document|documents|requirement|requirements|prd|urd|spec)\b",
            r"\bdocument generation\b",
            r"\b(go|vibe)[\s_-]*coding\b",
            r"(需求|信息)[\s\S]{0,20}(足够|完整|就绪|可以生成)",
            r"(生成|出)[\s\S]{0,12}(正式)?[\s\S]{0,12}(需求)?[\s\S]{0,8}(文档|prd|urd)",
            r"(点击|请)[\s\S]{0,12}生成[\s\S]{0,12}(文档|prd|urd)?",
            r"(进入|开始|打开)[\s\S]{0,10}(编码|coding|vibe|go\s*coding)",
            r"(anforderungen|requirements)[\s\S]{0,50}(bereit|ready)",
            r"\bdokument(en)?\s*(generierung|erzeugen|erstellen)\b",
            r"(ready|sedia)[\s\S]{0,40}(jana|hasilkan)[\s\S]{0,20}(dokumen|prd|urd)",
        )
        return any(re.search(pattern, lowered, flags=re.IGNORECASE) for pattern in readiness_patterns)

    def _build_readiness_gate_follow_up(
        self,
        structured_requirement_model: dict[str, Any],
        progress: dict[str, Any],
        pm_methodology_state: dict[str, Any],
        language: str,
    ) -> str:
        normalized = self._normalize_language(language)
        blocker = self._next_readiness_blocker(
            structured_requirement_model,
            progress,
            pm_methodology_state,
        )
        blocker_question = blocker["question"]
        options = self._readiness_blocker_choice_block(blocker, normalized)
        if normalized == "zh":
            return (
                "还不能生成正式文档：右侧 readiness gate 还没通过。"
                f"当前收集覆盖率 {progress.get('collection_coverage_percentage', 0)}%，"
                f"确认完成度 {progress.get('confirmation_percentage', 0)}%，"
                f"冲突数 {progress.get('conflict_count', 0)}。\n\n"
                f"下一步只补一个最高价值缺口：{blocker_question}\n\n"
                f"{options}"
            )
        if normalized == "de":
            return (
                "Das formale Dokument ist noch nicht freigegeben: Das rechte Readiness-Gate ist noch nicht erfuellt. "
                f"Abdeckung {progress.get('collection_coverage_percentage', 0)}%, "
                f"Bestaetigung {progress.get('confirmation_percentage', 0)}%, "
                f"Konflikte {progress.get('conflict_count', 0)}.\n\n"
                f"Naechster Schritt, nur eine wichtigste Luecke: {blocker_question}\n\n"
                f"{options}"
            )
        if normalized == "ms":
            return (
                "Dokumen rasmi belum boleh dijana: readiness gate di panel kanan belum lulus. "
                f"Liputan {progress.get('collection_coverage_percentage', 0)}%, "
                f"pengesahan {progress.get('confirmation_percentage', 0)}%, "
                f"konflik {progress.get('conflict_count', 0)}.\n\n"
                f"Langkah seterusnya, satu gap paling penting sahaja: {blocker_question}\n\n"
                f"{options}"
            )
        return (
            "Not ready to generate the formal document yet: the right-side readiness gate has not passed. "
            f"Collection coverage is {progress.get('collection_coverage_percentage', 0)}%, "
            f"confirmation progress is {progress.get('confirmation_percentage', 0)}%, "
            f"and conflict count is {progress.get('conflict_count', 0)}.\n\n"
            f"Next, close one highest-value gap: {blocker_question}\n\n"
            f"{options}"
        )

    def _next_readiness_blocker(
        self,
        structured_requirement_model: dict[str, Any],
        progress: dict[str, Any],
        pm_methodology_state: dict[str, Any],
    ) -> dict[str, str]:
        # Structured "Fully Confirmed" is the only hard gate; PM Methodology is advisory and is
        # intentionally NOT used as a blocker (its heuristic checks never reliably reach
        # "ready", which made the conversation circle). pm_methodology_state stays in the
        # signature for callers that still pass it.
        structured_blocker = self._next_structured_requirement_blocker(structured_requirement_model)
        if structured_blocker:
            return structured_blocker

        if progress.get("conflict_count"):
            return {
                "source": "conflict",
                "key": "conflict",
                "label": "Conflict",
                "question": "Which conflicting requirement should be treated as the source of truth for version one?",
                "evidence": "",
            }
        return {
            "source": "fallback",
            "key": "acceptance",
            "label": "Acceptance criteria",
            "question": "What is the single most important acceptance criterion for version one?",
            "evidence": "",
        }

    def _next_structured_requirement_blocker(
        self,
        structured_requirement_model: dict[str, Any],
    ) -> dict[str, str] | None:
        collection_status = normalize_structured_requirement_model(structured_requirement_model).get(
            "collection_status",
            {},
        )
        for key in REQUIREMENT_ITEM_KEYS:
            item = collection_status.get(key)
            if not isinstance(item, dict):
                continue
            status = str(item.get("status", "")).strip().lower()
            if status == "confirmed":
                continue
            pending_questions = item.get("pending_questions")
            if isinstance(pending_questions, list):
                for question in pending_questions:
                    question_text = str(question).strip()
                    if question_text:
                        evidence = self._structured_requirement_evidence_for_key(
                            structured_requirement_model,
                            key,
                        )
                        return {
                            "source": "structured_requirement",
                            "key": key,
                            "label": self._readiness_blocker_label(key),
                            "question": question_text,
                            "evidence": evidence,
                        }
            evidence = self._structured_requirement_evidence_for_key(
                structured_requirement_model,
                key,
            )
            default_question = self._default_structured_requirement_question(key)
            if default_question:
                return {
                    "source": "structured_requirement",
                    "key": key,
                    "label": self._readiness_blocker_label(key),
                    "question": default_question,
                    "evidence": evidence,
                }
        return None

    def _default_structured_requirement_question(self, key: str) -> str:
        questions = {
            "objective": "What business outcome should this dashboard improve?",
            "scope": "What should the first version include, and what should wait?",
            "users": "Who will use this dashboard first?",
            "scenarios": "What is the first real scenario this dashboard should support?",
            "features": "What information or action must be visible on the first screen?",
            "pages": "What screens or views are needed for the first version?",
            "rules": "How should the key metric or business rule be calculated?",
            "integrations": "What source system or file will provide the data?",
            "acceptance": "How will you know the first version works well enough?",
        }
        return questions.get(key, "")

    def _readiness_blocker_label(self, key: str) -> str:
        labels = {
            "objective": "Business goal",
            "scope": "Scope",
            "users": "Target users",
            "scenarios": "Core scenarios",
            "features": "Functional requirements",
            "pages": "Pages",
            "rules": "Business rules",
            "integrations": "Integration systems",
            "acceptance": "Acceptance criteria",
            "open_questions": "Open question",
        }
        return labels.get(key, key.replace("_", " ").title())

    def _friendly_blocker_label(self, blocker: dict[str, str]) -> str:
        key = blocker.get("key", "")
        labels = {
            "opportunity_solution_tree": "business goal and user problem",
            "success_metric": "success metric",
            "assumption_risk": "assumptions and risks",
            "prioritization": "first-version scope",
            "validation_plan": "validation plan",
            "story_acceptance": "user story and acceptance",
            "roadmap_release": "release plan",
            "objective": "business goal",
            "scope": "scope",
            "users": "target users",
            "scenarios": "core scenario",
            "features": "functional requirements",
            "pages": "pages",
            "rules": "business rules",
            "integrations": "data source",
            "acceptance": "acceptance criteria",
            "open_questions": "open question",
        }
        return labels.get(key, blocker.get("label") or "this point")

    def _localized_friendly_blocker_label(self, blocker: dict[str, str], language: str) -> str:
        if language != "zh":
            return self._friendly_blocker_label(blocker)
        key = blocker.get("key", "")
        labels = {
            "opportunity_solution_tree": "业务目标和用户问题",
            "success_metric": "成功指标",
            "assumption_risk": "假设与风险",
            "prioritization": "首版范围",
            "validation_plan": "验证方式",
            "story_acceptance": "用户场景和验收",
            "roadmap_release": "发布边界",
            "objective": "业务目标",
            "scope": "范围",
            "users": "目标用户",
            "scenarios": "核心场景",
            "features": "功能需求",
            "pages": "页面",
            "rules": "业务规则",
            "integrations": "数据来源",
            "acceptance": "验收标准",
            "open_questions": "待确认问题",
        }
        return labels.get(key, blocker.get("label") or "这个点")

    def _structured_requirement_evidence_for_key(
        self,
        structured_requirement_model: dict[str, Any],
        key: str,
    ) -> str:
        model = normalize_structured_requirement_model(structured_requirement_model)
        paths_by_key = {
            "objective": ("background.objective", "background.summary"),
            "scope": ("scope.in_scope", "scope.out_of_scope"),
            "users": ("users_and_scenarios.target_users", "product_context.primary_user"),
            "scenarios": ("users_and_scenarios.core_scenarios",),
            "features": ("functional_requirements.overview", "functional_requirements.feature_details"),
            "pages": ("page_and_interaction.pages", "page_and_interaction.interaction_flow"),
            "rules": ("business_rules",),
            "integrations": ("data_and_dependencies",),
            "acceptance": ("acceptance_criteria", "product_context.acceptance_owner"),
        }
        for path in paths_by_key.get(key, ()):
            values = self._flatten_path_strings(model, path)
            if values:
                return self._clip_option_text(" / ".join(values[:2]))
        return ""

    def _clip_option_text(self, text: str, limit: int = 120) -> str:
        normalized = " ".join(str(text or "").split())
        if len(normalized) <= limit:
            return normalized
        return f"{normalized[: limit - 1].rstrip()}…"

    def _readiness_blocker_label(self, key: str) -> str:
        labels = {
            "objective": "Business goal",
            "scope": "Scope",
            "users": "Target users",
            "scenarios": "Core scenarios",
            "features": "Functional requirements",
            "pages": "Pages",
            "rules": "Business rules",
            "integrations": "Integration systems",
            "acceptance": "Acceptance criteria",
        }
        return labels.get(key, key.replace("_", " ").title())

    def _is_degenerate_capture(self, text: str) -> bool:
        """A captured value that is empty or essentially says 'not stated'.

        Such values must never be offered as an 'A. confirm the current wording' option
        or echoed as an opening summary, or the user is asked to confirm a non-answer.
        """
        normalized = str(text or "").strip().lower()
        if not normalized:
            return True
        markers = (
            "未说明", "未明确", "未提供", "未确认", "尚未", "暂未", "待确认", "待补充", "未知", "待定",
            "not stated", "unspecified", "unclear", "not specified", "to be defined", "tbd", "n/a",
        )
        return any(marker in normalized for marker in markers)

    def _readiness_blocker_choice_block(self, blocker: dict[str, str], language: str) -> str:
        label = self._localized_friendly_blocker_label(blocker, language)
        evidence = blocker.get("evidence", "").strip()
        if self._is_degenerate_capture(evidence):
            evidence = ""
        if evidence:
            assumption_en = f"Use the current captured wording for {label}: {evidence}"
            assumption_zh = f"按当前已捕获内容确认 {label}：{evidence}"
            assumption_de = f"Aktuellen erfassten Wortlaut fuer {label} verwenden: {evidence}"
            assumption_ms = f"Gunakan wording semasa untuk {label}: {evidence}"
        else:
            assumption_en = f"Use a practical v1 assumption for {label}"
            assumption_zh = f"先按可落地的 v1 假设推进 {label}"
            assumption_de = f"Eine praktikable V1-Annahme fuer {label} verwenden"
            assumption_ms = f"Gunakan andaian v1 yang praktikal untuk {label}"
        if language == "zh":
            return (
                "请选择一个选项：\n"
                f"A. {assumption_zh}\n"
                f"B. 我补充真实的 {label} 口径或例外情况\n"
                "C. 这个点先保持待确认"
            )
        if language == "de":
            return (
                "Bitte waehle eine Option:\n"
                f"A. {assumption_de}\n"
                f"B. Ich ergaenze die echte fachliche Definition oder Ausnahme fuer {label}\n"
                "C. Diesen Punkt vorerst offen lassen"
            )
        if language == "ms":
            return (
                "Sila pilih satu pilihan:\n"
                f"A. {assumption_ms}\n"
                f"B. Saya tambah definisi bisnes sebenar atau pengecualian untuk {label}\n"
                "C. Kekalkan perkara ini sebagai belum sah dahulu"
            )
        return (
            "Choose one option:\n"
            f"A. {assumption_en}\n"
            f"B. I will provide the exact {label} wording or an exception\n"
            "C. Leave this pending for now"
        )

    def build_ic_substrate_evidence_state(
        self,
        session: Session | None,
        structured_requirement_model: dict[str, Any] | None,
        language: str = "zh",
    ) -> dict[str, Any]:
        normalized_language = self._normalize_language(language)
        model = normalize_structured_requirement_model(structured_requirement_model)
        gate = self._ic_substrate_readiness_evidence_gate(session, model)
        if session is None or not gate.get("enabled"):
            return build_ic_substrate_evidence_state_payload(
                gate,
                model,
                "",
                "",
                normalized_language,
            )

        chain_state = self.build_conversation_chain_state(session, model, normalized_language)
        department = (
            str(gate.get("department_specific_evidence", "")).strip()
            or str(chain_state.get("intent_track", "")).strip()
            or self._ic_substrate_intent_track_from_structured_model(model)
            or str(chain_state.get("current_track", "")).strip()
        )
        product_shape = (
            str(chain_state.get("intent_product_shape", "")).strip()
            or self._ic_substrate_product_shape_from_model_or_template(session, model, normalized_language)
        )
        return build_ic_substrate_evidence_state_payload(
            gate,
            model,
            department,
            product_shape,
            normalized_language,
        )

    def _ic_substrate_product_shape_from_model_or_template(
        self,
        session: Session,
        structured_requirement_model: dict[str, Any],
        language: str,
    ) -> str:
        product_context = structured_requirement_model.get("product_context", {})
        functional_requirements = structured_requirement_model.get("functional_requirements", {})
        template = self._resolve_business_template(session, language) or {}
        shape_context = {
            "software_type": product_context.get("software_type", "") if isinstance(product_context, dict) else "",
            "background": structured_requirement_model.get("background", {}),
            "scope": structured_requirement_model.get("scope", {}),
            "functional_requirements": functional_requirements,
            "page_and_interaction": structured_requirement_model.get("page_and_interaction", {}),
            "template_id": template.get("template_id", ""),
            "template_name": template.get("template_name", ""),
            "business_domain": template.get("business_domain", ""),
            "description": template.get("description", ""),
            "tags": template.get("tags", []),
            "applicable_scenarios": template.get("applicable_scenarios", []),
        }
        return self._ic_substrate_product_shape_from_text(json.dumps(shape_context, ensure_ascii=False))

    def get_structured_requirement_snapshot(
        self,
        session_id: str,
        language: str = "zh",
    ) -> dict[str, Any]:
        session = self.get_session(session_id)
        if session is None:
            raise KeyError("Session not found.")

        normalized_language = self._normalize_language(language)
        message_count = self._message_count(session.messages)
        cached_entry = self.session_store.get_structured_requirement_cache_entry(
            session_id,
            normalized_language,
        )
        if cached_entry is None:
            canonical_model = self._get_cached_canonical_structured_requirement_model(
                session_id,
                message_count,
                normalized_language,
            )
            if canonical_model is not None:
                conversation_chain_state = self.build_conversation_chain_state(
                    session,
                    canonical_model,
                    normalized_language,
                )
                return {
                    "structured_requirement_model": canonical_model,
                    "structured_requirement_sync_status": "missing",
                    "message_count": message_count,
                    "conversation_chain_state": conversation_chain_state,
                    "pm_methodology_state": self.build_pm_methodology_state(
                        canonical_model,
                        normalized_language,
                    ),
                    "ic_substrate_evidence_state": self.build_ic_substrate_evidence_state(
                        session,
                        canonical_model,
                        normalized_language,
                    ),
                }
            empty_model = self._empty_structured_requirement_model()
            conversation_chain_state = self.build_conversation_chain_state(
                session,
                empty_model,
                normalized_language,
            )
            return {
                "structured_requirement_model": empty_model,
                "structured_requirement_sync_status": "ready" if message_count == 0 else "missing",
                "message_count": message_count,
                "conversation_chain_state": conversation_chain_state,
                "pm_methodology_state": self.build_pm_methodology_state(
                    empty_model,
                    normalized_language,
                ),
                "ic_substrate_evidence_state": self.build_ic_substrate_evidence_state(
                    session,
                    empty_model,
                    normalized_language,
                ),
            }

        cached_model = normalize_structured_requirement_model(cached_entry.get("model"))
        cached_message_count = self._safe_int(cached_entry.get("message_count"))
        canonical_model = self._get_cached_canonical_structured_requirement_model(
            session_id,
            cached_message_count,
            normalized_language,
        )
        if canonical_model is not None:
            cached_model = self._with_canonical_collection_status(cached_model, canonical_model)
        sync_status = "ready" if cached_message_count == message_count else "stale"
        conversation_chain_state = self.build_conversation_chain_state(
            session,
            cached_model,
            normalized_language,
        )
        return {
            "structured_requirement_model": cached_model,
            "structured_requirement_sync_status": sync_status,
            "message_count": message_count,
            "conversation_chain_state": conversation_chain_state,
            "pm_methodology_state": self.build_pm_methodology_state(
                cached_model,
                normalized_language,
            ),
            "ic_substrate_evidence_state": self.build_ic_substrate_evidence_state(
                session,
                cached_model,
                normalized_language,
            ),
        }

    def build_system_design_document(
        self,
        session_id: str,
        language: str = "zh",
        save_history: bool = False,
    ) -> dict[str, Any]:
        session = self.get_session(session_id)
        if session is None:
            raise KeyError("Session not found.")

        conversation_messages = self._chat_history_messages(session.messages)
        if not conversation_messages:
            doc_markdown = self._default_design_doc(language)
            structured_requirement_model = self._empty_structured_requirement_model()
            return self._build_generated_document_result(
                session_id=session_id,
                document_kind=DESIGN_MESSAGE_KIND,
                language=language,
                doc_markdown=doc_markdown,
                structured_requirement_model=structured_requirement_model,
                status="insufficient_input",
                save_history=save_history,
            )

        structured_requirement_model = self.build_structured_requirement_model(session_id, language)
        progress = self._structured_requirement_progress(structured_requirement_model)
        if not progress["ready_to_generate"]:
            return self._build_generated_document_result(
                session_id=session_id,
                document_kind=DESIGN_MESSAGE_KIND,
                language=language,
                doc_markdown=self._document_quality_gate_block_markdown(
                    structured_requirement_model,
                    progress,
                    language,
                    "system_design",
                    session,
                ),
                structured_requirement_model=structured_requirement_model,
                status="quality_gate_blocked",
                save_history=False,
            )
        seed_markdown = self._build_design_doc_seed_markdown(
            structured_requirement_model,
            progress,
            language,
        )
        doc_markdown = self.llm_client.chat(
            self._build_design_doc_messages(
                session,
                conversation_messages,
                structured_requirement_model,
                progress,
                seed_markdown,
                language,
            ),
            temperature=0.2,
        )
        doc_markdown, _ = self._split_thinking(doc_markdown)
        doc_markdown = doc_markdown.strip()
        if not doc_markdown:
            # The seed scaffold is a prompt aid only; never emit it as a finished
            # document. If the LLM produced nothing, fail loudly (no local fakes).
            raise LLMError("LLM returned empty design document.")
        return self._build_generated_document_result(
            session_id=session_id,
            document_kind=DESIGN_MESSAGE_KIND,
            language=language,
            doc_markdown=doc_markdown,
            structured_requirement_model=structured_requirement_model,
            status="ok" if progress.get("fully_confirmed") else "draft_with_assumptions",
            save_history=save_history,
        )

    def stream_system_design_document(
        self,
        session_id: str,
        language: str = "zh",
        save_history: bool = False,
    ) -> Iterator[dict[str, Any]]:
        session = self.get_session(session_id)
        if session is None:
            raise KeyError("Session not found.")

        conversation_messages = self._chat_history_messages(session.messages)
        if not conversation_messages:
            doc_markdown = self._default_design_doc(language)
            structured_requirement_model = self._empty_structured_requirement_model()
            yield {"event": "content", "delta": doc_markdown}
            yield {
                "event": "done",
                **self._build_generated_document_result(
                    session_id=session_id,
                    document_kind=DESIGN_MESSAGE_KIND,
                    language=language,
                    doc_markdown=doc_markdown,
                    structured_requirement_model=structured_requirement_model,
                    status="insufficient_input",
                    save_history=save_history,
                ),
            }
            return

        structured_requirement_model = self.build_structured_requirement_model(session_id, language)
        progress = self._structured_requirement_progress(structured_requirement_model)
        if not progress["ready_to_generate"]:
            doc_markdown = self._document_quality_gate_block_markdown(
                structured_requirement_model,
                progress,
                language,
                "system_design",
                session,
            )
            yield {"event": "content", "delta": doc_markdown}
            yield {
                "event": "done",
                **self._build_generated_document_result(
                    session_id=session_id,
                    document_kind=DESIGN_MESSAGE_KIND,
                    language=language,
                    doc_markdown=doc_markdown,
                    structured_requirement_model=structured_requirement_model,
                    status="quality_gate_blocked",
                    save_history=False,
                ),
            }
            return
        seed_markdown = self._build_design_doc_seed_markdown(
            structured_requirement_model,
            progress,
            language,
        )
        doc_parts: list[str] = []
        thinking_parts: list[str] = []
        llm_messages = self._build_design_doc_messages(
            session,
            conversation_messages,
            structured_requirement_model,
            progress,
            seed_markdown,
            language,
        )

        for item in self.llm_client.stream_chat(llm_messages, temperature=0.2):
            text = item.get("text", "")
            if not text:
                continue

            if item.get("type") == "thinking":
                thinking_parts.append(text)
                yield {"event": "thinking", "delta": text}
                continue

            doc_parts.append(text)
            yield {"event": "content", "delta": text}

        doc_markdown = "".join(doc_parts).strip()
        thinking_text = "".join(thinking_parts).strip()
        doc_markdown, content_embedded_thinking = self._split_thinking(doc_markdown)
        if content_embedded_thinking:
            thinking_text = f"{thinking_text}\n{content_embedded_thinking}".strip()

        if not doc_markdown:
            # The seed scaffold is a prompt aid only; never emit it as a finished
            # document. If the LLM streamed nothing, fail loudly (no local fakes).
            raise LLMError("LLM returned empty streamed design document.")

        if thinking_text:
            yield {"event": "thinking_done", "thinking": thinking_text}
        yield {
            "event": "done",
            **self._build_generated_document_result(
                session_id=session_id,
                document_kind=DESIGN_MESSAGE_KIND,
                language=language,
                doc_markdown=doc_markdown,
                structured_requirement_model=structured_requirement_model,
                status="ok" if progress.get("fully_confirmed") else "draft_with_assumptions",
                save_history=save_history,
            ),
        }

    def build_prd_document(
        self,
        session_id: str,
        language: str = "zh",
        save_history: bool = False,
    ) -> dict[str, Any]:
        session = self.get_session(session_id)
        if session is None:
            raise KeyError("Session not found.")

        conversation_messages = self._chat_history_messages(session.messages)
        if not conversation_messages:
            doc_markdown = self._load_prd_template(session, language) or self._default_prd_doc(language)
            structured_requirement_model = self._empty_structured_requirement_model()
            return self._build_generated_document_result(
                session_id=session_id,
                document_kind=PRD_MESSAGE_KIND,
                language=language,
                doc_markdown=doc_markdown,
                structured_requirement_model=structured_requirement_model,
                status="template_scaffold" if session.applied_template_id else "insufficient_input",
                save_history=save_history,
            )

        structured_requirement_model = self.build_structured_requirement_model(session_id, language)
        progress = self._structured_requirement_progress(structured_requirement_model)
        if not progress["ready_to_generate"]:
            return self._build_generated_document_result(
                session_id=session_id,
                document_kind=PRD_MESSAGE_KIND,
                language=language,
                doc_markdown=self._document_quality_gate_block_markdown(
                    structured_requirement_model,
                    progress,
                    language,
                    "prd",
                    session,
                ),
                structured_requirement_model=structured_requirement_model,
                status="quality_gate_blocked",
                save_history=False,
            )
        doc_markdown = self.llm_client.chat(
            self._build_prd_doc_messages(
                session,
                conversation_messages,
                structured_requirement_model,
                progress,
                language,
            ),
            temperature=0.2,
        )
        doc_markdown, _ = self._split_thinking(doc_markdown)
        doc_markdown = doc_markdown.strip()
        if not doc_markdown:
            doc_markdown = self._load_prd_template(session, language) or self._default_prd_doc(language)
        doc_markdown = self._append_ic_substrate_prd_evidence_appendix(
            doc_markdown,
            session,
            structured_requirement_model,
            language,
        )
        return self._build_generated_document_result(
            session_id=session_id,
            document_kind=PRD_MESSAGE_KIND,
            language=language,
            doc_markdown=doc_markdown,
            structured_requirement_model=structured_requirement_model,
            status="ok" if progress.get("fully_confirmed") else "draft_with_assumptions",
            save_history=save_history,
        )

    def stream_prd_document(
        self,
        session_id: str,
        language: str = "zh",
        save_history: bool = False,
    ) -> Iterator[dict[str, Any]]:
        session = self.get_session(session_id)
        if session is None:
            raise KeyError("Session not found.")

        conversation_messages = self._chat_history_messages(session.messages)
        if not conversation_messages:
            doc_markdown = self._load_prd_template(session, language) or self._default_prd_doc(language)
            structured_requirement_model = self._empty_structured_requirement_model()
            yield {"event": "content", "delta": doc_markdown}
            yield {
                "event": "done",
                **self._build_generated_document_result(
                    session_id=session_id,
                    document_kind=PRD_MESSAGE_KIND,
                    language=language,
                    doc_markdown=doc_markdown,
                    structured_requirement_model=structured_requirement_model,
                    status="template_scaffold" if session.applied_template_id else "insufficient_input",
                    save_history=save_history,
                ),
            }
            return

        structured_requirement_model = self.build_structured_requirement_model(session_id, language)
        progress = self._structured_requirement_progress(structured_requirement_model)
        if not progress["ready_to_generate"]:
            doc_markdown = self._document_quality_gate_block_markdown(
                structured_requirement_model,
                progress,
                language,
                "prd",
                session,
            )
            yield {"event": "content", "delta": doc_markdown}
            yield {
                "event": "done",
                **self._build_generated_document_result(
                    session_id=session_id,
                    document_kind=PRD_MESSAGE_KIND,
                    language=language,
                    doc_markdown=doc_markdown,
                    structured_requirement_model=structured_requirement_model,
                    status="quality_gate_blocked",
                    save_history=False,
                ),
            }
            return
        doc_parts: list[str] = []
        thinking_parts: list[str] = []
        llm_messages = self._build_prd_doc_messages(
            session,
            conversation_messages,
            structured_requirement_model,
            progress,
            language,
        )
        for item in self.llm_client.stream_chat(llm_messages, temperature=0.2):
            text = item.get("text", "")
            if not text:
                continue

            if item.get("type") == "thinking":
                thinking_parts.append(text)
                yield {"event": "thinking", "delta": text}
                continue

            doc_parts.append(text)
            yield {"event": "content", "delta": text}

        doc_markdown = "".join(doc_parts).strip()
        thinking_text = "".join(thinking_parts).strip()
        doc_markdown, content_embedded_thinking = self._split_thinking(doc_markdown)
        if content_embedded_thinking:
            thinking_text = f"{thinking_text}\n{content_embedded_thinking}".strip()

        if not doc_markdown:
            raise LLMError("LLM returned empty streamed PRD document.")

        appended_doc_markdown = self._append_ic_substrate_prd_evidence_appendix(
            doc_markdown,
            session,
            structured_requirement_model,
            language,
        )
        if appended_doc_markdown != doc_markdown:
            appendix_delta = (
                appended_doc_markdown[len(doc_markdown):]
                if appended_doc_markdown.startswith(doc_markdown)
                else f"\n\n{appended_doc_markdown}"
            )
            yield {"event": "content", "delta": appendix_delta}
            doc_markdown = appended_doc_markdown

        if thinking_text:
            yield {"event": "thinking_done", "thinking": thinking_text}
        yield {
            "event": "done",
            **self._build_generated_document_result(
                session_id=session_id,
                document_kind=PRD_MESSAGE_KIND,
                language=language,
                doc_markdown=doc_markdown,
                structured_requirement_model=structured_requirement_model,
                status="ok" if progress.get("fully_confirmed") else "draft_with_assumptions",
                save_history=save_history,
            ),
        }

    def get_saved_design_document(self, session_id: str) -> tuple[Path, str] | None:
        session = self.get_session(session_id)
        if session is None:
            raise KeyError("Session not found.")

        latest_entry = self.session_store.get_latest_document_message(session_id, DESIGN_MESSAGE_KIND)
        resolved = self._resolve_document_entry(latest_entry)
        if resolved is not None:
            return resolved

        design_doc_path = self._design_doc_path(session_id)
        if design_doc_path.exists():
            return design_doc_path, design_doc_path.name
        return None

    def get_saved_prd_document(self, session_id: str) -> tuple[Path, str] | None:
        session = self.get_session(session_id)
        if session is None:
            raise KeyError("Session not found.")

        latest_entry = self.session_store.get_latest_document_message(session_id, PRD_MESSAGE_KIND)
        resolved = self._resolve_document_entry(latest_entry)
        if resolved is not None:
            return resolved

        prd_doc_path = self._prd_doc_path(session_id)
        if prd_doc_path.exists():
            return prd_doc_path, prd_doc_path.name
        return None

    def build_implementation_context(self, session_id: str, language: str = "zh") -> dict[str, Any]:
        session = self.get_session(session_id)
        if session is None:
            raise KeyError("Session not found.")

        prd_result = self.get_saved_prd_document(session_id)
        design_result = self.get_saved_design_document(session_id)

        missing_documents: list[str] = []
        if prd_result is None:
            missing_documents.append("prd")

        if missing_documents:
            return {
                "session_id": session_id,
                "title": session.title,
                "documents_ready": False,
                "missing_documents": missing_documents,
            }

        prd_path, prd_filename = prd_result
        prd_absolute_path = str(prd_path.resolve())
        design_absolute_path = ""
        design_filename = ""
        if design_result is not None:
            design_path, design_filename = design_result
            design_absolute_path = str(design_path.resolve())
        message_count = self._message_count(session.messages)
        structured_requirement_model = (
            self._get_latest_cached_structured_requirement_model(
                session_id,
                STRUCTURED_REQUIREMENT_CANONICAL_CACHE_KEY,
                message_count,
            )
            or self._empty_structured_requirement_model()
        )
        ic_substrate_evidence = self._ic_substrate_readiness_evidence_gate(
            session,
            structured_requirement_model,
        )

        return {
            "session_id": session_id,
            "title": session.title,
            "documents_ready": True,
            "documents": {
                "prd": {
                    "filename": prd_filename,
                    "path": prd_absolute_path,
                },
                **(
                    {
                        "design": {
                            "filename": design_filename,
                            "path": design_absolute_path,
                        }
                    }
                    if design_result is not None
                    else {}
                ),
            },
            "implementation_prompt": self._build_implementation_prompt(
                session_id=session_id,
                session_title=session.title,
                prd_path=prd_absolute_path,
                design_path=design_absolute_path,
                language=language,
                ic_substrate_evidence=ic_substrate_evidence,
            ),
            "ic_substrate_evidence": ic_substrate_evidence,
        }

    def build_browser_handoff_payload(self, session_id: str, language: str = "zh") -> dict[str, Any]:
        session = self.get_session(session_id)
        if session is None:
            raise KeyError("Session not found.")

        prd_result = self.get_saved_prd_document(session_id)
        design_result = self.get_saved_design_document(session_id)

        missing_documents: list[str] = []
        if prd_result is None:
            missing_documents.append("prd")

        if missing_documents:
            return {
                "session_id": session_id,
                "title": session.title,
                "language": self._normalize_language(language),
                "documents_ready": False,
                "missing_documents": missing_documents,
            }

        normalized_language = self._normalize_language(language)
        prd_path, prd_filename = prd_result
        design_filename = ""
        if design_result is not None:
            _, design_filename = design_result
        message_count = self._message_count(session.messages)
        structured_requirement_model = (
            self._get_latest_cached_structured_requirement_model(
                session_id,
                STRUCTURED_REQUIREMENT_CANONICAL_CACHE_KEY,
                message_count,
            )
            or self._empty_structured_requirement_model()
        )
        ic_substrate_evidence = self._ic_substrate_readiness_evidence_gate(
            session,
            structured_requirement_model,
        )
        prd_download_url = self._legacy_document_download_url(session_id, PRD_MESSAGE_KIND)
        design_download_url = (
            self._legacy_document_download_url(session_id, DESIGN_MESSAGE_KIND)
            if design_result is not None
            else ""
        )
        implementation_prompt = self._build_implementation_prompt(
            session_id=session_id,
            session_title=session.title,
            prd_path=prd_filename,
            design_path=design_filename,
            language=normalized_language,
            ic_substrate_evidence=ic_substrate_evidence,
        )
        now = datetime.now(timezone.utc)
        expires_at = (now + timedelta(minutes=DEFAULT_HANDOFF_TTL_MINUTES)).isoformat()

        return {
            "source": "pm",
            "transport": "browser-handoff",
            "session_id": session_id,
            "title": session.title,
            "language": normalized_language,
            "documents_ready": True,
            "handoff_ready": True,
            "methodology_ready": True,
            "implementation_prompt": implementation_prompt,
            "documents": [
                {
                    "kind": "prd",
                    "filename": prd_filename,
                    "mime_type": "text/markdown; charset=utf-8",
                    "download_url": prd_download_url,
                },
            ]
            + (
                [
                    {
                        "kind": "design",
                        "filename": design_filename,
                        "mime_type": "text/markdown; charset=utf-8",
                        "download_url": design_download_url,
                    }
                ]
                if design_result is not None
                else []
            ),
            "ic_substrate_evidence": ic_substrate_evidence,
            "expires_at": expires_at,
        }

    def create_coding_handoff(self, session_id: str, language: str = "zh") -> dict[str, Any]:
        payload = self.build_browser_handoff_payload(session_id, language)
        if not payload.get("documents_ready") or not payload.get("handoff_ready", True):
            return payload

        created_at = datetime.now(timezone.utc)
        expires_at = payload.get("expires_at") or (created_at + timedelta(minutes=DEFAULT_HANDOFF_TTL_MINUTES)).isoformat()
        token = f"hf_{secrets.token_urlsafe(24)}"
        persisted_payload = {
            **payload,
            "created_at": created_at.isoformat(),
            "expires_at": expires_at,
        }
        self.session_store.delete_expired_coding_handoffs(created_at.isoformat())
        self.session_store.create_coding_handoff(
            token=token,
            session_id=session_id,
            payload=persisted_payload,
            created_at=created_at.isoformat(),
            expires_at=expires_at,
        )
        return {
            "handoff_token": token,
            "expires_at": expires_at,
            "payload": persisted_payload,
        }

    def resolve_coding_handoff(self, token: str) -> dict[str, Any] | None:
        record = self.session_store.get_coding_handoff(token)
        if record is None:
            return None

        now = datetime.now(timezone.utc)
        expires_at = self._parse_datetime(record.get("expires_at"))
        if expires_at is None or expires_at <= now:
            return None

        payload = record.get("payload")
        if not isinstance(payload, dict):
            return None
        return payload

    def get_saved_message_document(self, session_id: str, message_id: int) -> tuple[Path, str] | None:
        session = self.get_session(session_id)
        if session is None:
            raise KeyError("Session not found.")

        entry = self.session_store.get_message_document(session_id, message_id)
        return self._resolve_document_entry(entry)

    def build_docx_download(self, file_path: Path, download_name: str) -> tuple[BytesIO, str]:
        markdown = file_path.read_text(encoding="utf-8")
        docx_buffer = BytesIO(self._markdown_to_docx_bytes(markdown))
        docx_buffer.seek(0)
        return docx_buffer, f"{Path(download_name).stem}.docx"

    def _build_structured_requirement_model(self, session: Session, language: str = "zh") -> dict[str, Any]:
        conversation_messages = self._conversation_messages(session.messages)
        if not conversation_messages:
            return self._empty_structured_requirement_model()

        try:
            raw_model = self.llm_client.chat(
                [
                    {
                        "role": "system",
                        "content": self._structured_requirement_model_prompt(session, language),
                    },
                    {
                        "role": "user",
                        "content": json.dumps(conversation_messages, ensure_ascii=False),
                    },
                ],
                temperature=0.1,
            )
        except LLMError:
            # The structured-requirement model is an analysis sidecar, not the primary
            # reply/document output. If this secondary LLM call fails, degrade to an empty
            # model instead of crashing session load / summary refresh.
            return self._empty_structured_requirement_model()
        return self._safe_parse_structured_requirement_model(raw_model)

    def _build_and_cache_structured_requirement_model(
        self,
        session: Session,
        language: str,
        force_refresh: bool = False,
    ) -> dict[str, Any]:
        normalized_language = self._normalize_language(language)
        message_count = self._message_count(session.messages)
        previous_canonical_model = self._get_latest_cached_structured_requirement_model(
            session.id,
            STRUCTURED_REQUIREMENT_CANONICAL_CACHE_KEY,
            message_count - 1,
        )
        canonical_model = None
        if not force_refresh:
            canonical_model = self._get_cached_canonical_structured_requirement_model(
                session.id,
                message_count,
                normalized_language,
            )

        if canonical_model is None:
            canonical_model = self._build_structured_requirement_model(session, normalized_language)
            canonical_model = self._merge_structured_requirement_collection_status(
                canonical_model,
                previous_canonical_model,
            )
            canonical_model = self._apply_recent_choice_confirmation_to_model(
                canonical_model,
                session.messages,
            )
            self._save_structured_requirement_model_cache(
                session.id,
                STRUCTURED_REQUIREMENT_CANONICAL_CACHE_KEY,
                message_count,
                canonical_model,
            )
            structured_requirement_model = canonical_model
        else:
            structured_requirement_model = self._build_structured_requirement_model(
                session,
                normalized_language,
            )

        structured_requirement_model = self._with_canonical_collection_status(
            structured_requirement_model,
            canonical_model,
        )
        self._save_structured_requirement_model_cache(
            session.id,
            normalized_language,
            message_count,
            structured_requirement_model,
        )
        return structured_requirement_model

    def _promote_cached_structured_requirement_model(
        self,
        session: Session,
        language: str,
    ) -> dict[str, Any]:
        """Re-save the latest cached structured requirement model at the current
        message_count without making a new LLM extraction call.

        After the assistant reply is appended, message_count increments but the
        assistant text itself doesn't contain new requirement information.  This
        method looks up the model that was extracted *before* the assistant
        reply (at message_count - 1) and promotes it to the current
        message_count cache slot so that subsequent snapshot reads see it as
        'ready' rather than 'stale'.

        Falls back to a full rebuild if no prior cache entry is found.
        """
        normalized_language = self._normalize_language(language)
        message_count = self._message_count(session.messages)

        # Try to find the model cached during the pre-reply extraction.
        cached_model = self._get_latest_cached_structured_requirement_model(
            session.id,
            normalized_language,
            message_count,
        )
        if cached_model is None:
            cached_model = self._get_latest_cached_structured_requirement_model(
                session.id,
                STRUCTURED_REQUIREMENT_CANONICAL_CACHE_KEY,
                message_count,
            )

        if cached_model is not None:
            # Promote to both the canonical and language cache slots at the
            # current message_count so snapshot reads return sync_status=ready.
            self._save_structured_requirement_model_cache(
                session.id,
                STRUCTURED_REQUIREMENT_CANONICAL_CACHE_KEY,
                message_count,
                cached_model,
            )
            self._save_structured_requirement_model_cache(
                session.id,
                normalized_language,
                message_count,
                cached_model,
            )
            return cached_model

        # Fallback: no prior cache found, do a full rebuild.
        return self._build_and_cache_structured_requirement_model(session, language)

    def _merge_structured_requirement_collection_status(
        self,
        current_model: dict[str, Any],
        previous_model: dict[str, Any] | None,
    ) -> dict[str, Any]:
        current = normalize_structured_requirement_model(current_model)
        if previous_model is None:
            return current

        previous = normalize_structured_requirement_model(previous_model)
        current_status = current["collection_status"]
        previous_status = previous["collection_status"]
        merged_status: dict[str, Any] = {}
        for key in REQUIREMENT_ITEM_KEYS:
            merged_status[key] = self._merge_requirement_status_item(
                current_status.get(key),
                previous_status.get(key),
            )
        current["collection_status"] = merged_status
        current = self._preserve_previous_requesting_department(current, previous)
        return current

    def _preserve_previous_requesting_department(
        self,
        current_model: dict[str, Any],
        previous_model: dict[str, Any],
    ) -> dict[str, Any]:
        current = normalize_structured_requirement_model(current_model)
        previous = normalize_structured_requirement_model(previous_model)
        current_department = str(current["product_context"].get("requesting_department", "")).strip()
        previous_department = str(previous["product_context"].get("requesting_department", "")).strip()
        if current_department or not previous_department:
            return current
        previous_track = self._ic_substrate_intent_track_from_text(previous_department)
        if self._ic_substrate_is_department(previous_track):
            current["product_context"]["requesting_department"] = previous_department
        return current

    def _merge_requirement_status_item(
        self,
        current_item: dict[str, Any] | None,
        previous_item: dict[str, Any] | None,
    ) -> dict[str, Any]:
        current = current_item if isinstance(current_item, dict) else {}
        previous = previous_item if isinstance(previous_item, dict) else {}
        current_status = str(current.get("status", "missing")).strip().lower()
        previous_status = str(previous.get("status", "missing")).strip().lower()

        if current_status == "conflict":
            return current
        if previous_status == "conflict" and current_status != "confirmed":
            return previous

        status_rank = {
            "missing": 0,
            "captured": 1,
            "pending_confirmation": 2,
            "confirmed": 3,
        }
        current_rank = status_rank.get(current_status, 0)
        previous_rank = status_rank.get(previous_status, 0)
        if previous_rank > current_rank:
            return previous
        return current

    def _apply_recent_choice_confirmation_to_model(
        self,
        structured_requirement_model: dict[str, Any],
        messages: list[dict[str, Any]],
    ) -> dict[str, Any]:
        model = normalize_structured_requirement_model(structured_requirement_model)
        confirmed_key = self._recent_option_a_confirmed_requirement_key(messages)
        if not confirmed_key:
            return model

        evidence = self._structured_requirement_evidence_for_key(model, confirmed_key)
        if self._is_degenerate_capture(evidence):
            return model

        item = model["collection_status"].get(confirmed_key)
        if not isinstance(item, dict):
            return model
        if str(item.get("status", "")).strip().lower() == "conflict":
            return model

        item["status"] = "confirmed"
        item["reason"] = "Confirmed via Option A using the assistant's offered version-one wording."
        item["pending_questions"] = []
        return model

    def _recent_option_a_confirmed_requirement_key(self, messages: list[dict[str, Any]]) -> str:
        chat_messages = self._chat_history_messages(messages)
        if len(chat_messages) < 2:
            return ""

        latest_user_index = next(
            (
                index
                for index in range(len(chat_messages) - 1, -1, -1)
                if str(chat_messages[index].get("role", "")).lower() == "user"
            ),
            -1,
        )
        if latest_user_index <= 0:
            return ""

        latest_user_text = str(chat_messages[latest_user_index].get("content", "") or "").strip()
        if not self._looks_like_option_a_confirmation(latest_user_text):
            return ""

        previous_assistant = next(
            (
                chat_messages[index]
                for index in range(latest_user_index - 1, -1, -1)
                if str(chat_messages[index].get("role", "")).lower() == "assistant"
            ),
            None,
        )
        if not previous_assistant:
            return ""

        assistant_text = str(previous_assistant.get("content", "") or "")
        option_a_text = self._extract_option_a_text(assistant_text)
        return self._requirement_key_from_confirmation_text(
            "\n".join([latest_user_text, option_a_text, assistant_text]),
        )

    def _looks_like_option_a_confirmation(self, text: str) -> bool:
        normalized = " ".join(str(text or "").strip().split()).lower()
        if not normalized:
            return False
        return bool(
            re.match(r"^(a|a[.、):：-])\b", normalized)
            or normalized.startswith(("选a", "我选a", "确认a", "按a", "confirm "))
        )

    def _extract_option_a_text(self, assistant_text: str) -> str:
        match = re.search(
            r"(?:^|\n)\s*A[.)、:：-]\s*([\s\S]*?)(?=(?:\n\s*B[.)、:：-]\s*)|$)",
            assistant_text,
            flags=re.IGNORECASE,
        )
        if not match:
            return ""
        return " ".join(match.group(1).split())

    def _requirement_key_from_confirmation_text(self, text: str) -> str:
        normalized = " ".join(str(text or "").lower().split())
        label_patterns = (
            ("acceptance", (r"\bacceptance\b", r"\b验收")),
            ("rules", (r"\bbusiness rules?\b", r"\bcalculation", r"\bformula", r"\bfpy\b", r"\byield loss")),
            ("integrations", (r"\bintegration", r"\bsource system", r"\bdata source")),
            ("pages", (r"\bpages?\b", r"\bscreens?\b", r"\bviews?\b", r"\bentry point", r"\bbrowser url", r"\binteraction flow")),
            ("features", (r"\bfunctional requirements?\b", r"\bfeatures?\b", r"\bvisuali[sz]ation", r"\bchart")),
            ("scenarios", (r"\bcore scenarios?\b", r"\buse scenarios?\b", r"\buser tasks?\b")),
            ("users", (r"\btarget users?\b", r"\bprimary users?\b", r"\bactors?\b")),
            ("scope", (r"\bscope\b", r"\bp0\b", r"\bout of scope\b", r"\bfirst release\b")),
            ("objective", (r"\bbusiness goal\b", r"\bobjective\b", r"\boutcome\b")),
        )
        for key, patterns in label_patterns:
            if any(re.search(pattern, normalized) for pattern in patterns):
                return key
        return ""

    def _save_structured_requirement_model_cache(
        self,
        session_id: str,
        cache_key: str,
        message_count: int,
        structured_requirement_model: dict[str, Any],
    ) -> None:
        self.session_store.save_structured_requirement_cache_entry(
            session_id=session_id,
            language=cache_key,
            message_count=message_count,
            structured_requirement_model=structured_requirement_model,
            updated_at=datetime.now(timezone.utc).isoformat(),
        )

    def _get_cached_structured_requirement_model(
        self,
        session_id: str,
        cache_key: str,
        message_count: int,
    ) -> dict[str, Any] | None:
        cached_entry = self.session_store.get_structured_requirement_cache_entry(session_id, cache_key)
        if cached_entry is None:
            return None
        cached_message_count = self._safe_int(cached_entry.get("message_count"))
        if cached_message_count != message_count:
            return None
        return normalize_structured_requirement_model(cached_entry.get("model"))

    def _get_latest_cached_structured_requirement_model(
        self,
        session_id: str,
        cache_key: str,
        max_message_count: int,
    ) -> dict[str, Any] | None:
        cached_entry = self.session_store.get_structured_requirement_cache_entry(session_id, cache_key)
        if cached_entry is None:
            return None
        cached_message_count = self._safe_int(cached_entry.get("message_count"))
        if cached_message_count < 0 or cached_message_count > max_message_count:
            return None
        return normalize_structured_requirement_model(cached_entry.get("model"))

    def _get_cached_localized_structured_requirement_model(
        self,
        session_id: str,
        language: str,
        message_count: int,
    ) -> dict[str, Any] | None:
        cached_model = self._get_cached_structured_requirement_model(
            session_id,
            language,
            message_count,
        )
        if cached_model is None:
            return None

        canonical_model = self._get_cached_canonical_structured_requirement_model(
            session_id,
            message_count,
            language,
        )
        if canonical_model is None:
            return cached_model
        return self._with_canonical_collection_status(cached_model, canonical_model)

    def _get_cached_canonical_structured_requirement_model(
        self,
        session_id: str,
        message_count: int,
        preferred_language: str | None = None,
    ) -> dict[str, Any] | None:
        cached_model = self._get_cached_structured_requirement_model(
            session_id,
            STRUCTURED_REQUIREMENT_CANONICAL_CACHE_KEY,
            message_count,
        )
        if cached_model is not None:
            return cached_model

        best_model = self._best_cached_structured_requirement_model(
            session_id,
            message_count,
            preferred_language,
        )
        if best_model is not None:
            self._save_structured_requirement_model_cache(
                session_id,
                STRUCTURED_REQUIREMENT_CANONICAL_CACHE_KEY,
                message_count,
                best_model,
            )
        return best_model

    def _best_cached_structured_requirement_model(
        self,
        session_id: str,
        message_count: int,
        preferred_language: str | None = None,
    ) -> dict[str, Any] | None:
        best_model: dict[str, Any] | None = None
        best_score: tuple[int, int, int] | None = None
        for cache_key in self._structured_requirement_fallback_cache_keys(preferred_language):
            candidate = self._get_cached_structured_requirement_model(
                session_id,
                cache_key,
                message_count,
            )
            if candidate is None:
                continue
            score = self._structured_requirement_status_score(candidate)
            if best_score is None or score > best_score:
                best_model = candidate
                best_score = score
        return best_model

    def _structured_requirement_fallback_cache_keys(
        self,
        preferred_language: str | None = None,
    ) -> list[str]:
        cache_keys: list[str] = []
        for cache_key in (
            self._normalize_language(preferred_language) if preferred_language else "",
            *STRUCTURED_REQUIREMENT_CANONICAL_FALLBACK_LANGUAGES,
        ):
            if cache_key and cache_key not in cache_keys:
                cache_keys.append(cache_key)
        return cache_keys

    def _structured_requirement_status_score(self, model: dict[str, Any]) -> tuple[int, int, int]:
        progress = self._structured_requirement_progress(model)
        return (
            self._safe_int(progress.get("collected_count")),
            self._safe_int(progress.get("confirmed_count")),
            -self._safe_int(progress.get("conflict_count")),
        )

    def _with_canonical_collection_status(
        self,
        model: dict[str, Any],
        canonical_model: dict[str, Any],
    ) -> dict[str, Any]:
        localized_model = normalize_structured_requirement_model(model)
        canonical = normalize_structured_requirement_model(canonical_model)
        localized_model["collection_status"] = canonical["collection_status"]
        localized_model["open_questions"] = canonical["open_questions"]
        localized_model = self._preserve_previous_requesting_department(localized_model, canonical_model)
        return localized_model

    def _message_count(self, messages: list[dict[str, Any]]) -> int:
        return len(self._chat_history_messages(messages))

    def _safe_int(self, value: Any) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return -1

    def _hydrate_message_payloads(
        self,
        messages: list[dict[str, Any]],
        session_id: str,
    ) -> list[dict[str, Any]]:
        hydrated: list[dict[str, Any]] = []
        for item in messages:
            payload: dict[str, Any] = {
                "role": str(item.get("role", "")).strip(),
                "content": str(item.get("content", "")),
                "created_at": str(item.get("created_at", "")).strip(),
                "kind": self._message_kind(item),
            }
            display_content = str(item.get("display_content", "")).strip()
            if display_content:
                payload["display_content"] = display_content
            message_id = self._safe_int(item.get("message_id"))
            if message_id >= 0:
                payload["message_id"] = message_id
            thinking = str(item.get("thinking", "")).strip()
            if thinking:
                payload["thinking"] = thinking
            download_filename = str(item.get("download_filename", "")).strip()
            if download_filename:
                payload["download_filename"] = download_filename
            if download_filename and message_id >= 0:
                payload["download_url"] = self._document_download_url(session_id, message_id)
            hydrated.append(payload)
        return hydrated

    def _message_kind(self, message: dict[str, Any]) -> str:
        kind = str(message.get("kind", CHAT_MESSAGE_KIND)).strip()
        return kind or CHAT_MESSAGE_KIND

    def _chat_history_messages(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [item for item in messages if self._message_kind(item) == CHAT_MESSAGE_KIND]

    def _document_download_url(self, session_id: str, message_id: int) -> str:
        return f"/api/sessions/{session_id}/messages/{message_id}/download"

    def _legacy_document_download_url(self, session_id: str, document_kind: str) -> str:
        if document_kind == PRD_MESSAGE_KIND:
            return f"/api/sessions/{session_id}/prd-doc/download"
        return f"/api/sessions/{session_id}/design-doc/download"

    def _resolve_document_entry(self, entry: dict[str, Any] | None) -> tuple[Path, str] | None:
        if not isinstance(entry, dict):
            return None
        storage_path = str(entry.get("storage_path", "")).strip()
        download_filename = str(entry.get("download_filename", "")).strip()
        if not storage_path or not download_filename:
            return None

        file_path = Path(storage_path)
        if not file_path.exists():
            return None
        return file_path, download_filename

    def _session_from_record(self, record: dict[str, Any]) -> Session:
        return Session(
            id=record["session_id"],
            title=record.get("title", ""),
            prompt_template=self._normalize_prompt_template(record.get("prompt_template", PROMPT_TEMPLATE_PERSONAL_PROJECT)),
            applied_template_id=str(record.get("applied_template_id", "")).strip(),
            applied_template_name=str(record.get("applied_template_name", "")).strip(),
            start_function=self._normalize_start_function(record.get("start_function", START_FUNCTION_FROM_SCRATCH)),
            created_at=record["created_at"],
            updated_at=record.get("updated_at", record["created_at"]),
            messages=self._hydrate_message_payloads(
                record.get("messages", []),
                session_id=record["session_id"],
            ),
        )

    def _conversation_messages(self, messages: list[dict[str, Any]]) -> list[dict[str, str]]:
        return [
            {
                "role": str(item.get("role", "")),
                "content": str(item.get("content", "")),
            }
            for item in self._chat_history_messages(messages)
        ]

    def _build_llm_messages(self, system_prompt: str, messages: list[dict[str, Any]]) -> list[dict[str, str]]:
        return [{"role": "system", "content": system_prompt}, *self._conversation_messages(messages)]

    def _resolve_business_template(
        self,
        session: Session,
        language: str | None = None,
    ) -> dict[str, Any] | None:
        if not session.applied_template_id:
            return None
        return self.business_template_library.get_template_prompt_context(
            session.applied_template_id,
            self._normalize_language(language) if language else None,
        )

    def _business_template_pm_addendum(self, session: Session, language: str | None = None) -> str:
        template = self._resolve_business_template(session, language)
        normalized_language = self._normalize_language(language)
        if template is None:
            if not session.applied_template_name:
                return ""
            chain_addendum = self._template_conversation_chain_addendum(
                {"template_name": session.applied_template_name},
                normalized_language,
            )
            return (
                "An applied business requirement template is active for this session.\n"
                f"- Template name: {session.applied_template_name}\n"
                "- Drive discovery using the template structure instead of the generic project interview mode.\n"
                "- Prioritize collecting concrete answers for the next missing section in the template.\n"
                "- Keep questions aligned to the template's intended business domain and scope.\n"
                "- Do not fall back to the personal-project or expert generic prompting patterns.\n\n"
                + chain_addendum
            )

        chain_addendum = self._template_conversation_chain_addendum(template, normalized_language)
        return (
            "An applied business requirement template is active for this session.\n"
            "- Treat this template as the primary requirement-discovery backbone.\n"
            "- Do not use the generic personal-project or expert discovery pattern as the main strategy.\n"
            "- Move section by section through the template and prioritize the highest-value missing information.\n"
            "- Ask questions that help complete the template fields, business rules, and acceptance criteria.\n"
            "- Keep answers grounded in the template's domain and avoid drifting into unrelated discovery tracks.\n"
            "\n"
            + chain_addendum
            + "\n"
            f"- Template context: {json.dumps(template, ensure_ascii=False)}"
        )

    def _template_conversation_chain_addendum(
        self,
        template: dict[str, Any],
        language: str | None = None,
    ) -> str:
        normalized_language = self._normalize_language(language)
        generic_chain = self._generic_template_conversation_chain_addendum(normalized_language)
        if not self._template_matches_ic_substrate_focus(template):
            return generic_chain
        return "\n\n".join(
            (
                generic_chain,
                self._ic_substrate_conversation_chain_addendum(normalized_language),
            )
        )

    def _generic_template_conversation_chain_addendum(self, language: str | None = None) -> str:
        normalized_language = self._normalize_language(language)
        if normalized_language == "zh":
            return (
                "模板对话链路：\n"
                "- 模板启动后，把模板字段转成渐进式访谈链路，而不是一次性填表或罗列章节问题。\n"
                "- 每轮先判断当前已覆盖到哪个链路节点，再只问一个最能推进下一节点的问题。\n"
                "- 默认沿：背景/目标 -> 范围/角色 -> 核心场景 -> 规则/数据 -> 页面/交互 -> 验收/发布 推进；如果模板的 prompt_questions 更具体，优先把它们当作链路队列。\n"
                "- 用户一次给出多个答案时，吸收所有信息，但回复仍只落到一个下一问。\n"
                "- 可以用一句短标签标出当前链路，例如：当前链路：范围 -> 用户角色。"
            )
        if normalized_language == "de":
            return (
                "Vorlagen-Dialogkette:\n"
                "- Nach dem Start einer Vorlage werden die Vorlagenfelder als schrittweise Interviewkette genutzt, nicht als einmaliges Formular oder Kapitel-Checkliste.\n"
                "- In jeder Runde wird zuerst der aktuelle Knoten bestimmt; danach wird genau eine Frage gestellt, die den naechsten Knoten voranbringt.\n"
                "- Standardpfad: Hintergrund/Ziel -> Umfang/Rollen -> Kernszenarien -> Regeln/Daten -> Seiten/Interaktionen -> Abnahme/Release; wenn prompt_questions spezifischer sind, gelten sie als Fragenwarteschlange.\n"
                "- Wenn der Nutzer mehrere Punkte auf einmal beantwortet, werden alle Informationen aufgenommen, die Antwort bleibt aber auf eine naechste Frage fokussiert.\n"
                "- Der aktuelle Knoten darf kurz markiert werden, z. B.: Aktuelle Kette: Umfang -> Nutzerrollen."
            )
        if normalized_language == "ms":
            return (
                "Rantaian dialog templat:\n"
                "- Selepas templat dimulakan, medan templat dijadikan rantaian temu bual berperingkat, bukan borang sekali isi atau senarai bab.\n"
                "- Pada setiap pusingan, kenal pasti nod semasa dahulu, kemudian tanya tepat satu soalan yang paling menggerakkan nod seterusnya.\n"
                "- Laluan lalai: latar belakang/objektif -> skop/peranan -> senario utama -> peraturan/data -> halaman/interaksi -> penerimaan/release; jika prompt_questions lebih khusus, jadikannya barisan soalan.\n"
                "- Jika pengguna menjawab beberapa nod sekali gus, serap semua maklumat, tetapi balasan masih fokus pada satu soalan seterusnya.\n"
                "- Boleh tandakan nod semasa secara ringkas, contohnya: Rantaian semasa: skop -> peranan pengguna."
            )
        return (
            "Template conversation chain:\n"
            "- After a template starts, turn template fields into a progressive interview chain instead of a one-shot form or section checklist.\n"
            "- On every turn, infer the current chain node from the conversation, then ask exactly one question that moves the next node forward.\n"
            "- Default path: background/objective -> scope/roles -> core scenarios -> rules/data -> pages/interactions -> acceptance/release; when template prompt_questions are more specific, treat them as the chain queue.\n"
            "- If the user answers multiple nodes at once, absorb all of it, but keep the reply focused on one next question.\n"
            "- You may label the current node briefly, for example: Current chain: scope -> user roles."
        )

    def _ic_substrate_conversation_chain_addendum(self, language: str | None = None) -> str:
        normalized_language = self._normalize_language(language)
        if normalized_language == "zh":
            return (
                "IC Substrate 专业对话链路：\n"
                "- 系统角色始终是 AI 产品经理，不是制造/质量/工程顾问；目标是帮助讲不清需求的业务部门，把想开发的软件、Web dashboard、流程工具、报表或数据产品讲清楚，沉淀成可交付给开发团队的需求。\n"
                "- 当前 IT scope 只开放 Production、Quality、TDI 和 General 四个同级入口；其他部门链路先隐藏，统一归入 General，不要在首问选项或推荐链路里展开成独立部门。\n"
                "- 入口先做部门/业务 owner 路由：用户当前明显在说 Quality、TDI 或 Production，就直接进入对应链路；如果用户说其他部门、部门未开放或业务 owner 不明确，就进入 General 并继续把软件需求问清楚。\n"
                "- 如果用户只给了“做一个 IC Substrate 系统/平台/工具”这类宽泛表达，没有明确部门和需求形态，第一问只在当前开放范围内确认首版部门或业务 owner：Production、Quality、TDI、General。\n"
                "- 部门首问选项必须只覆盖当前开放入口：Production、Quality、TDI、General；不要列 Customer、EHS、Engineering、Equipment、Finance、IT/Data、Management、Material、Planning 或 Warehouse。\n"
                "- 反问必须先落到软件需求：谁使用、看什么、做什么决策或动作、当前痛点、首版边界、输入输出、数据来源、验收标准；领域知识用于把问题问专业，不要变成全面业务流程审计。\n"
                "- 当用户说“做系统/看板/工具”但没说清形态时，优先确认首版软件形态：dashboard、workflow/case tracking、data query、report/export、alerting、admin console 或跨部门 cockpit；不要直接追完整制造流程。\n"
                "- 软件形态是后端隐形路由，不要要求用户在前端选择；如果用户已经暗示 dashboard、workflow/case tracking、report/export、data query、alerting 或 admin console，就按该形态问一个更专业的问题。\n"
                "- 每轮只问一个专业问题，但问题里可以给 2-5 个业务选项帮助用户快速确认，例如部门/owner 分组、lot / panel / unit 粒度、现行指标口径、现行状态流转或责任边界。\n"
                "- Go Coding handoff gate：即使用户只给一句模糊的软件想法，也不能直接开放 Go Coding；先用一个最高价值问题补齐业务动作、使用者/owner、数据源、集成/写回边界或验收证据中最关键的缺口。只有结构化需求 ready_to_generate=true 时，才提示生成文档；文档生成/确认 OK 后，Go Coding 才能把文档交接给 Vibe Coding 平台。不要提供跳过文档直接 Go Coding 的选项。\n"
                "- 硬性约束：每轮只能有一个问句，不要用“另外/同时/以及/还需要”追加第二个问题；如果两个口径都缺，先问更影响链路边界的那个。\n"
                "- 硬性约束：在用户确认前，TDI 只能写作 TDI，不要写成 TDI（技术/异常/导入/接口）或任何括号解释。\n"
                "- 硬性约束：部门首问的选项说明里也不能展开 TDI；只能写 Production/Quality/TDI 这些部门名，不要把 TDI 解释成技术导入、异常处理、接口集成或其他含义。\n"
                "- 硬性约束：不要自造 TDI case 状态名、SLA 数字、owner 角色或审批层级；不要给 Created/In Progress/Closed、24 小时、QA 签核这类默认选项，除非用户先提供。应询问用户现行状态、每个状态责任方、SLA 口径和关闭条件。\n"
                "- 硬性约束：这个“不自造”规则适用于所有部门；不要替 Production 编 route/站点/yield 公式，不要替 Quality 编 inspection point/defect taxonomy/spec limit/MRB/CAPA 流程，不要替 Finance 编标准成本/实际成本/毛利公式选项，不要替 Equipment 编 OEE/MTBF/MTTR 公式或 alarm code，不要替 EHS 编法规等级/整改 SLA，不要替 Planning 编排程规则，除非用户先提供。\n"
                "- 不要擅自引入未确认的站点缩写、工艺站点名、设备名、供应商名、系统品牌或内部术语；如果需要举例，用“最后生产站出站 / 入库 / QA release / ERP 或财务系统”这类通用表述，或先问用户的组织术语。\n"
                "- 硬性约束：不要自造具体站点缩写、工艺站点、系统品牌或内部系统术语选项，例如 FVI、AOI、E-test、AVI、SAP、EAP、SPC 等；除非用户先提供这些术语。\n"
                "- Production：确认产品族/厂区/线别/工艺路线/lot-panel-unit 粒度、Finished Lot 定义、工序站点 move-in/move-out、WIP/报废/返工、良率/吞吐/周期、异常 hold/release 与 owner；所有 route、站点和公式以用户现场口径为准。\n"
                "- TDI：不要擅自展开缩写，按用户组织内定义执行；若未确认，先确认本项目 TDI 的业务含义，再问触发条件、输入输出、状态流转、责任方/SLA、审批点，以及与上游/下游生产、质量或数据系统的交接。\n"
                "- Quality：确认用户现行检测点、defect code/taxonomy、规格上下限、抽检/全检、retest/rework/scrap/MRB 判定、缺陷 Pareto、root cause 维度、CAPA/改善闭环和验收对账；不要自造缺陷分类、规格规则或 MRB/CAPA 状态。\n"
                "- 当前开放入口平级：如果用户提到 Production、Quality 或 TDI，要切到该部门的软件使用场景；如果用户提到其他部门或不确定归属，就走 General 的通用 PM 软件需求链路，继续确认业务决策/动作、KPI、主数据、流程状态、责任边界、系统来源和验收方式。\n"
                "- 初期不要优先追问权限、部署、菜单、颜色、通用 CRUD，除非它直接影响该部门的首版业务链路边界。"
            )
        if normalized_language == "de":
            return (
                "IC Substrate Experten-Dialogkette:\n"
                "- Die Rolle ist immer AI Product Manager, nicht Manufacturing-, Quality- oder Engineering-Berater. Ziel ist, unklare Anforderungen aus Fachbereichen in Software, Web Dashboards, Workflow Tools, Reports oder Datenprodukte fuer Engineering-Handover zu uebersetzen.\n"
                "- Im aktuellen IT Scope sind Production, Quality, TDI und General als gleichrangige Einstiege aktiv; andere Fachbereiche bleiben verborgen und werden in General zusammengefasst, nicht als eigene Erstfrage-Optionen.\n"
                "- Zuerst nach Fachbereich/Business Owner routen: Wenn Quality, TDI oder Production klar genannt ist, direkt in diesen Track wechseln. Wenn ein anderer oder nicht freigegebener Bereich genannt wird oder der Owner unklar ist, in General wechseln und die Softwareanforderung klaeren.\n"
                "- Bei breiten Wuenschen wie IC Substrate System/Plattform/Tool ohne klaren Bereich zuerst nur im aktiven Scope fragen, welcher First-Version Owner verantwortlich ist: Production, Quality, TDI oder General.\n"
                "- Die Erstfrage zu Bereichen darf nur Production, Quality, TDI und General nennen; Customer, EHS, Engineering, Equipment, Finance, IT/Data, Management, Material, Planning oder Warehouse nicht anbieten.\n"
                "- Jede Rueckfrage muss zuerst die Softwareanforderung klaeren: Nutzer, Sicht/Aktion, Entscheidung, aktueller Schmerz, First-Version Boundary, Inputs/Outputs, Datenquelle und Abnahme. Domainwissen dient schaerferen PM-Fragen, nicht einer kompletten Prozessauditierung.\n"
                "- Wenn der Nutzer System/Dashboard/Tool sagt, aber die Produktform unklar ist, zuerst die First-Version Softwareform klaeren: dashboard, workflow/case tracking, data query, report/export, alerting, admin console oder cross-department cockpit.\n"
                "- Softwareform ist ein verborgenes Backend-Routing, keine Frontend-Auswahl. Wenn der Nutzer dashboard, workflow/case tracking, report/export, data query, alerting oder admin console andeutet, eine fachlich passende PM-Frage stellen.\n"
                "- Pro Runde genau eine professionelle Frage stellen; 2-5 fachliche Optionen sind erlaubt, wenn sie dem Nutzer beim schnellen Einordnen helfen.\n"
                "- Go Coding handoff gate: Auch bei einer vagen Software-Idee Go Coding nicht direkt anbieten. Stelle eine high-value Frage zur wichtigsten Luecke in business action, user/owner, source of truth, integration/writeback boundary oder acceptance evidence. Bei structured requirement ready_to_generate=true zuerst Dokumente erzeugen; Go Coding uebergibt erst nach erzeugtem/geprueftem Dokument an Vibe Coding. Keine Option anbieten, Dokumente zu ueberspringen.\n"
                "- Harte Regel: TDI bis zur Nutzerbestaetigung nur als TDI schreiben, ohne Klammererklaerung oder implizite Bedeutung in Department-Optionen.\n"
                "- Harte Regel: Keine TDI case states, SLA-Zahlen, Owner-Rollen, Approval Levels, Production route/station/yield formulas, Quality inspection points/defect taxonomy/spec limits/MRB/CAPA states, Finance cost formulas, Equipment OEE/MTBF/MTTR formulas, EHS SLA oder Planning-Regeln erfinden.\n"
                "- Keine unbestaetigten Station-Abkuerzungen, Prozessschritte, Equipmentnamen, Lieferanten, Systemmarken oder internen Begriffe einfuehren; Begriffe wie FVI, AOI, E-test, AVI, SAP, EAP, SPC, MES, QMS oder ERP nur verwenden, wenn Nutzer oder Quelle sie bestaetigt.\n"
                "- Production: product family, plant, line, route, lot-panel-unit grain, Finished Lot Definition, move-in/move-out, WIP/scrap/rework, yield/throughput/cycle time, hold/release und Owner klaeren.\n"
                "- TDI: Akronym nicht selbst aufloesen; zuerst projektbezogene Bedeutung, Trigger, Inputs/Outputs, Statusfluss, Owner/SLA, Approval Points und Upstream/Downstream Handoffs klaeren.\n"
                "- Quality: aktuelle inspection points, defect code/taxonomy, spec limits, sampling/full inspection, retest/rework/scrap/MRB disposition, Pareto, root cause, CAPA/Improvement Closure und Abnahmeabgleich klaeren.\n"
                "- Die aktiven Einstiege sind gleichrangig: Bei Production, Quality oder TDI ueber deren Software Use Case fragen; andere oder unklare Bereiche laufen ueber General mit Entscheidung/Aktion, KPI, Master Data, Workflow State, Owner Boundary, Source System und Acceptance."
            )
        if normalized_language == "ms":
            return (
                "Rantaian dialog pakar IC Substrate:\n"
                "- Peranan sistem sentiasa AI Product Manager, bukan penasihat manufacturing, quality atau engineering. Matlamatnya ialah membantu jabatan bisnes yang belum jelas menerangkan software, Web dashboard, workflow tool, report atau data product untuk handover kepada engineering.\n"
                "- Untuk scope IT semasa, Production, Quality, TDI dan General dibuka sebagai entry setara; jabatan lain disembunyikan dan disatukan di bawah General, bukan pilihan jabatan berasingan.\n"
                "- Mula dengan routing jabatan/business owner: jika Quality, TDI atau Production jelas disebut, terus masuk ke track tersebut. Jika jabatan lain disebut, jabatan belum dibuka atau owner belum jelas, masuk ke General dan terus jelaskan keperluan software.\n"
                "- Jika pengguna hanya minta IC Substrate system/platform/tool tanpa jabatan atau bentuk keperluan yang jelas, tanya dahulu first-version owner dalam scope aktif sahaja: Production, Quality, TDI atau General.\n"
                "- Pilihan soalan jabatan pertama mesti hanya meliputi Production, Quality, TDI dan General; jangan tawarkan Customer, EHS, Engineering, Equipment, Finance, IT/Data, Management, Material, Planning atau Warehouse.\n"
                "- Setiap soalan mesti mula-mula menjelaskan keperluan software: pengguna, view/action, keputusan, pain point semasa, first-version boundary, input/output, sumber data dan acceptance. Pengetahuan domain digunakan untuk soalan PM yang tajam, bukan audit proses penuh.\n"
                "- Apabila pengguna menyebut system/dashboard/tool tetapi bentuk produk belum jelas, sahkan dahulu first-version software shape: dashboard, workflow/case tracking, data query, report/export, alerting, admin console atau cross-department cockpit.\n"
                "- Software shape ialah routing backend tersembunyi, bukan pilihan frontend. Jika pengguna sudah membayangkan dashboard, workflow/case tracking, report/export, data query, alerting atau admin console, tanya satu soalan PM yang lebih khusus untuk shape itu.\n"
                "- Tanya tepat satu soalan profesional setiap pusingan; 2-5 pilihan bisnes boleh diberi jika membantu pengguna mengesahkan dengan cepat.\n"
                "- Go Coding handoff gate: walaupun pengguna hanya beri idea software kabur, jangan terus tawarkan Go Coding. Tanya satu soalan high-value untuk gap paling penting dalam business action, user/owner, source of truth, integration/writeback boundary atau acceptance evidence. Jika structured requirement ready_to_generate=true, jana dokumen dahulu; Go Coding hanya handoff dokumen yang sudah dijana/OK ke Vibe Coding. Jangan beri pilihan skip dokumen.\n"
                "- Peraturan keras: tulis TDI hanya sebagai TDI sehingga pengguna mengesahkan maksudnya; jangan tambah penerangan dalam kurungan atau membayangkan makna dalam pilihan jabatan.\n"
                "- Peraturan keras: jangan reka TDI case states, nombor SLA, owner roles, approval levels, Production route/station/yield formulas, Quality inspection points/defect taxonomy/spec limits/MRB/CAPA states, Finance cost formulas, Equipment OEE/MTBF/MTTR formulas, EHS SLA atau Planning rules.\n"
                "- Jangan masukkan station abbreviation, process step, equipment name, supplier, system brand atau istilah dalaman yang belum disahkan; istilah seperti FVI, AOI, E-test, AVI, SAP, EAP, SPC, MES, QMS atau ERP hanya boleh digunakan jika pengguna atau sumber jelas mengesahkan.\n"
                "- Production: sahkan product family, plant, line, route, lot-panel-unit grain, Finished Lot definition, move-in/move-out, WIP/scrap/rework, yield/throughput/cycle time, hold/release dan owner.\n"
                "- TDI: jangan kembangkan akronim sendiri; sahkan maksud TDI untuk projek ini, trigger, input/output, state flow, owner/SLA, approval points dan upstream/downstream handoff.\n"
                "- Quality: sahkan inspection points semasa, defect code/taxonomy, spec limits, sampling/full inspection, retest/rework/scrap/MRB disposition, Pareto, root cause, CAPA/improvement closure dan acceptance reconciliation.\n"
                "- Entry aktif adalah setara: untuk Production, Quality atau TDI, tanya melalui software use case jabatan itu; untuk jabatan lain atau owner tidak jelas, gunakan General dengan business decision/action, KPI, master data, workflow state, ownership boundary, source system dan acceptance."
            )
        return (
            "IC Substrate professional conversation chain:\n"
            "- The role is always an AI product manager, not a manufacturing/quality/engineering consultant. The goal is to help business departments who cannot clearly express needs define software, web dashboards, workflow tools, reports, or data products for engineering handoff.\n"
            "- The current IT scope exposes four equal entry points: Production, Quality, TDI, and General. Hide other department tracks and route them into General instead of listing them as first-question options or recommended chains.\n"
            "- First route by department/business owner: if the user is clearly discussing Quality, TDI, or Production, move directly into that track. If they mention another department, an unopened department, or an unclear owner, move into General and continue clarifying the software requirement.\n"
            "- If the user only gives a broad request like an IC Substrate system/platform/tool without a clear department or need type, first ask only within the active scope: Production, Quality, TDI, or General.\n"
            "- Department-first options must include only Production, Quality, TDI, and General; do not offer Customer, EHS, Engineering, Equipment, Finance, IT/Data, Management, Material, Planning, or Warehouse.\n"
            "- Every question must first clarify the software requirement: user, view or action, decision, current pain, first-version boundary, inputs/outputs, data source, and acceptance. Use domain knowledge to ask sharper PM questions; do not turn the conversation into a full process audit.\n"
            "- When the user says system/dashboard/tool but has not clarified the product shape, first confirm whether the first version is a dashboard, workflow/case tracker, data query, report/export, alerting, admin console, or cross-department cockpit. Do not jump directly into the whole manufacturing process.\n"
            "- Software shape is hidden backend routing, not a frontend choice. If the user already implies dashboard, workflow/case tracking, report/export, data query, alerting, or admin console, ask one more expert PM question for that shape.\n"
            "- Ask one professional question per turn, but include 2-5 domain options when helpful, such as department/owner groups, lot / panel / unit grain, current metric definitions, current state flow, or ownership boundaries.\n"
            "- Go Coding handoff gate: even when the user gives one vague software idea, do not offer Go Coding directly. Ask one high-value question for the most important gap among business action, user/owner, source of truth, integration/writeback boundary, or acceptance evidence. When structured requirement ready_to_generate=true, suggest generating documents first; Go Coding only sends the generated/approved document handoff to the Vibe Coding platform. Never offer an option to skip documents and go directly to coding.\n"
            "- Hard constraint: each turn may contain only one question. Do not append a second question with \"also\", \"and\", \"in addition\", or similar wording; if two definitions are missing, ask the one that affects the boundary most.\n"
            "- Hard constraint: until the user confirms the meaning, write TDI only as TDI. Do not add any parenthetical expansion such as technology, exception, introduction, or interface.\n"
            "- Hard constraint: do not expand TDI inside department-first option descriptions either. Write only Production/Quality/TDI department names; do not explain TDI as technology introduction, exception handling, interface integration, or any other meaning.\n"
            "- Hard constraint: do not invent TDI case state names, SLA numbers, owner roles, or approval levels. Do not provide default options such as Created/In Progress/Closed, 24 hours, or QA sign-off unless the user provided them first. Ask for the user's current states, state owners, SLA definition, and closure criteria.\n"
            "- Hard constraint: this no-invention rule applies to every department. Do not invent Production route/station/yield formulas, Quality inspection points/defect taxonomy/spec limits/MRB/CAPA workflow, Finance standard-cost/actual-cost/margin formula options, Equipment OEE/MTBF/MTTR formulas or alarm codes, EHS compliance levels/corrective-action SLA, or Planning scheduling rules unless the user provided them first.\n"
            "- Do not introduce unconfirmed station abbreviations, process-step names, equipment names, supplier names, system brands, or internal terms. When examples are needed, use generic wording such as final production move-out / warehouse receipt / QA release / ERP or finance system, or first ask for the user's local terminology.\n"
            "- Hard constraint: do not invent station abbreviation, process-step, system-brand, or internal-system options such as FVI, AOI, E-test, AVI, SAP, EAP, SPC, or similar unless the user provided them first.\n"
            "- Production: confirm product family, plant, line, route, lot-panel-unit grain, Finished Lot definition, move-in/move-out stations, WIP/scrap/rework, yield/throughput/cycle-time metrics, abnormal hold/release, and owners. Route, station, and formula definitions must come from the user.\n"
            "- TDI: do not expand the acronym on your own; follow the user's organizational definition. If not confirmed, ask what TDI means in this project, then collect triggers, inputs/outputs, state flow, owner/SLA, approval points, and upstream/downstream production, quality, or data-system handoffs.\n"
            "- Quality: confirm the user's current inspection points, defect code/taxonomy, spec limits, sampling vs. full inspection, retest/rework/scrap/MRB disposition, defect Pareto, root-cause dimensions, CAPA/improvement closure, and validation reconciliation. Do not invent defect categories, spec rules, or MRB/CAPA states.\n"
            "- Active-entry routing: if the user mentions Production, Quality, or TDI, ask through that department's software use case. If they mention another department or unclear ownership, use General's PM software-requirement chain and clarify business decision/action, KPIs, master data, workflow states, ownership boundaries, source systems, and acceptance.\n"
            "- Early turns should not prioritize permissions, deployment, menus, colors, or generic CRUD unless they directly affect that department's first-version business boundary."
        )

    def _template_matches_ic_substrate_focus(self, template: dict[str, Any]) -> bool:
        template_text = json.dumps(
            {
                "template_id": template.get("template_id", ""),
                "template_key": template.get("template_key", ""),
                "template_name": template.get("template_name", ""),
                "business_domain": template.get("business_domain", ""),
                "description": template.get("description", ""),
                "tags": template.get("tags", []),
                "applicable_scenarios": template.get("applicable_scenarios", []),
                "section_titles": template.get("section_titles", []),
            },
            ensure_ascii=False,
        ).lower()
        return any(keyword in template_text for keyword in IC_SUBSTRATE_CHAIN_KEYWORDS)

    def build_conversation_chain_state(
        self,
        session: Session,
        structured_requirement_model: dict[str, Any] | None = None,
        language: str | None = None,
    ) -> dict[str, Any]:
        normalized_language = self._normalize_language(language)
        template = self._resolve_business_template(session, normalized_language)
        model = normalize_structured_requirement_model(structured_requirement_model)
        matches_ic_substrate = self._session_matches_ic_substrate_expert_chain(
            session,
            normalized_language,
            model,
        )
        if template is None and not session.applied_template_name and not matches_ic_substrate:
            return {"enabled": False}

        if template is not None:
            template_context = template
        elif session.applied_template_name:
            template_context = {
                "template_id": session.applied_template_id,
                "template_name": session.applied_template_name,
            }
        else:
            template_context = {
                "template_id": "ic_substrate_inferred_fast_path",
                "template_name": "IC Substrate inferred expert chain",
                "business_domain": "IC Substrate",
            }
        mode = (
            "ic_substrate"
            if matches_ic_substrate or self._template_matches_ic_substrate_focus(template_context)
            else "template"
        )
        nodes = (
            self._ic_substrate_chain_nodes(normalized_language)
            if mode == "ic_substrate"
            else self._generic_template_chain_nodes(normalized_language)
        )
        collection_status = model.get("collection_status", {})

        current_index = 0
        current_node_override: dict[str, Any] | None = None
        for index, node in enumerate(nodes):
            if not self._chain_node_confirmed(collection_status, node):
                current_index = index
                break
        else:
            current_index = max(len(nodes) - 1, 0)

        intent_track = ""
        intent_focus = ""
        intent_product_shape = ""
        if mode == "ic_substrate":
            model_intent_track = self._ic_substrate_intent_track_from_structured_model(model)
            intent_track = model_intent_track or self._ic_substrate_intent_track_from_latest_user_message(session)
            intent_focus = self._ic_substrate_intent_focus_from_latest_user_message(session)
            intent_product_shape = self._ic_substrate_product_shape_from_latest_user_message(session)
            has_user_messages = self._session_has_user_messages(session)
            if not has_user_messages and not intent_track:
                current_index = -1
                current_node_override = self._ic_substrate_scope_triage_node(normalized_language)
            elif not intent_track and not intent_focus:
                if intent_product_shape:
                    current_index = -1
                    current_node_override = self._ic_substrate_track_disambiguation_node(normalized_language)
                else:
                    current_index = -1
                    current_node_override = self._ic_substrate_scope_triage_node(normalized_language)
            elif (intent_focus or intent_product_shape) and not intent_track:
                current_index = -1
                current_node_override = self._ic_substrate_track_disambiguation_node(normalized_language)
            elif intent_track:
                preferred_node = self._ic_substrate_preferred_node_for_intent(intent_track, intent_focus)
                if preferred_node:
                    for index, node in enumerate(nodes):
                        if node.get("node") == preferred_node and not self._chain_node_confirmed(collection_status, node):
                            current_index = index
                            break
                    else:
                        preferred_node = ""
                if preferred_node:
                    pass
                else:
                    for index, node in enumerate(nodes):
                        if not self._ic_substrate_node_matches_intent_track(node, intent_track):
                            continue
                        if not self._chain_node_confirmed(collection_status, node):
                            current_index = index
                            break
                    else:
                        if self._ic_substrate_is_department(intent_track):
                            current_index = -1
                            current_node_override = self._ic_substrate_department_fallback_node(
                                intent_track,
                                normalized_language,
                                intent_focus,
                            )

        complete = bool(nodes) and all(self._chain_node_confirmed(collection_status, node) for node in nodes)
        if complete:
            status = "complete"
        elif self._session_has_user_messages(session):
            status = "in_progress"
        else:
            status = "not_started"

        current_node = current_node_override or (nodes[current_index] if nodes else self._fallback_chain_node(normalized_language))
        node_states = []
        if current_node_override is not None:
            node_states.append(
                {
                    "track": current_node["track"],
                    "node": current_node["node"],
                    "label": current_node["label"],
                    "status": "current",
                }
            )
        for index, node in enumerate(nodes):
            if complete or self._chain_node_confirmed(collection_status, node):
                node_status = "complete"
            elif index == current_index:
                node_status = "current"
            else:
                node_status = "pending"
            node_states.append(
                {
                    "track": node["track"],
                    "node": node["node"],
                    "label": node["label"],
                    "status": node_status,
                }
            )

        return {
            "enabled": True,
            "mode": mode,
            "template_id": session.applied_template_id,
            "template_name": session.applied_template_name or str(template_context.get("template_name", "")),
            "current_track": current_node["track"],
            "current_node": current_node["node"],
            "current_node_label": current_node["label"],
            "current_step_index": current_index + 1 if current_index >= 0 and nodes else 0,
            "total_steps": len(nodes),
            "status": status,
            "next_question_source": self._conversation_chain_question_source(template_context, mode),
            "intent_track": intent_track,
            "intent_focus": intent_focus,
            "intent_product_shape": intent_product_shape,
            "tracks": self._conversation_chain_track_labels(nodes, mode, normalized_language),
            "nodes": node_states,
        }

    def _generic_template_chain_nodes(self, language: str | None = None) -> list[dict[str, Any]]:
        if self._normalize_language(language) == "zh":
            labels = {
                "objective": ("背景目标", "确认业务目标"),
                "scope": ("范围角色", "确认范围边界"),
                "users": ("范围角色", "确认用户角色"),
                "scenarios": ("核心场景", "确认核心场景"),
                "features": ("功能流程", "确认功能需求"),
                "rules": ("规则数据", "确认业务规则"),
                "pages": ("页面交互", "确认页面交互"),
                "integrations": ("规则数据", "确认数据与依赖"),
                "acceptance": ("验收发布", "确认验收标准"),
            }
        else:
            labels = {
                "objective": ("Background", "Confirm objective"),
                "scope": ("Scope", "Confirm scope"),
                "users": ("Roles", "Confirm users"),
                "scenarios": ("Scenarios", "Confirm scenarios"),
                "features": ("Features", "Confirm requirements"),
                "rules": ("Rules/Data", "Confirm business rules"),
                "pages": ("Pages", "Confirm pages and interactions"),
                "integrations": ("Rules/Data", "Confirm data and dependencies"),
                "acceptance": ("Acceptance", "Confirm acceptance criteria"),
            }

        return [
            {
                "track": track,
                "node": key,
                "label": label,
                "status_keys": (key,),
            }
            for key, (track, label) in labels.items()
        ]

    def _ic_substrate_chain_nodes(self, language: str | None = None) -> list[dict[str, Any]]:
        return self._ic_substrate_department_chain_nodes(language)

    def _ic_substrate_department_chain_nodes(self, language: str | None = None) -> list[dict[str, Any]]:
        normalized_language = self._normalize_language(language)
        status_by_suffix = {
            "scope": ("objective", "scope"),
            "metrics": ("features",),
            "workflow": ("rules",),
            "data_acceptance": ("integrations", "acceptance"),
        }
        if normalized_language == "zh":
            specs = {
                "production": [
                    ("scope", "确认产品、厂区、线别、route、lot/panel/unit 和 Finished Lot 边界"),
                    ("metrics", "确认 output、WIP、scrap、rework、cycle time、throughput 和 yield 口径"),
                    ("workflow", "确认 move-in/out、hold/release、rework/scrap 和 Finished Lot 判定流程"),
                    ("data_acceptance", "确认生产记录、站点流转、质量 release、对账和 sign-off"),
                ],
                "tdi": [
                    ("scope", "确认 TDI 在本项目里的业务定义、对象范围和上下游边界"),
                    ("metrics", "确认 case aging、SLA hit rate、open/close count 和 handoff delay 口径"),
                    ("workflow", "确认 TDI trigger、triage、action/approval、handoff、verification、closure 流程"),
                    ("data_acceptance", "确认 TDI 记录、交接数据源、SLA 起止点、回写和关闭验收"),
                ],
                "quality": [
                    ("scope", "确认 inspection point、defect taxonomy、spec limit 和质量 release 边界"),
                    ("metrics", "确认 defect rate、loss ratio、retest/rework/scrap、CAPA aging 和 repeat defect 口径"),
                    ("workflow", "确认 defect capture、disposition、MRB/CAPA、root cause、verification/release 流程"),
                    ("data_acceptance", "确认检测/缺陷/判定数据源、lot genealogy、关闭证据和质量 sign-off"),
                ],
                "general": [
                    ("scope", "确认 General 需求的发起部门、业务 owner、首版软件形态和场景边界"),
                    ("metrics", "确认 General 需求要支撑的决策/动作、成功指标、现行口径和数据粒度"),
                    ("workflow", "确认 General 需求的用户流程、状态、owner、异常处理和闭环方式"),
                    ("data_acceptance", "确认 General 需求的数据源、输出物、验收 owner、sign-off 和待开放部门边界"),
                ],
                "planning": [
                    ("scope", "确认 demand/forecast、产能边界和首版排产业务目标"),
                    ("metrics", "确认计划达成、产能负载、WIP aging 和交期承诺口径"),
                    ("workflow", "确认 forecast lock、排程 release、dispatch 变更和 expedite 流程"),
                    ("data_acceptance", "确认计划数据源、产能模型、commit 版本和验收对账"),
                ],
                "engineering": [
                    ("scope", "确认 route/recipe/spec/parameter、NPI 或工程变更边界"),
                    ("metrics", "确认 qualification pass rate、ECN aging 和变更周期口径"),
                    ("workflow", "确认 change request、DOE/试作、review、release/rollback 流程"),
                    ("data_acceptance", "确认工程数据源、release gate、版本控制和验收责任"),
                ],
                "equipment": [
                    ("scope", "确认设备范围、area/line、关键机台和生产/质量影响边界"),
                    ("metrics", "确认 uptime/OEE、downtime、PM compliance、MTBF/MTTR 口径"),
                    ("workflow", "确认 alarm/down、维修动作、PM、release 和 recurrence review 流程"),
                    ("data_acceptance", "确认设备数据源、维修记录、lot 关联和停机归因验收"),
                ],
                "material": [
                    ("scope", "确认 BOM/料号、供应商、来料批次和供应风险边界"),
                    ("metrics", "确认 incoming pass rate、缺料风险、库存覆盖和供应商批次口径"),
                    ("workflow", "确认 procurement、IQC、发料、hold、替代料审批流程"),
                    ("data_acceptance", "确认物料主数据、库存/IQC 来源、lot 追溯和可用性验收"),
                ],
                "warehouse": [
                    ("scope", "确认 Finished Lot 入库、FG/WIP 库存、包装和出货边界"),
                    ("metrics", "确认 inventory aging、on-time shipment、hold stock 和周转口径"),
                    ("workflow", "确认 receive、store、pick/pack、hold check、ship 流程"),
                    ("data_acceptance", "确认库存/出货数据源、QA/customer hold 和追溯验收"),
                ],
                "customer": [
                    ("scope", "确认 customer/program、forecast/commit、客诉/RMA/8D 边界"),
                    ("metrics", "确认 commit hit rate、complaint aging、8D closure 和 RMA recurrence 口径"),
                    ("workflow", "确认客户需求/问题、内部映射、owner assignment、response、closure 流程"),
                    ("data_acceptance", "确认客户数据源、customer lot 到内部 lot 追溯和回复验收"),
                ],
                "finance": [
                    ("scope", "确认 cost object、cost center、损失类型和财务责任边界"),
                    ("metrics", "确认 scrap/rework/loss cost、variance 和 margin impact 口径"),
                    ("workflow", "确认 loss event、成本计算、责任归因、finance review、month-end lock 流程"),
                    ("data_acceptance", "确认财务/生产损失数据源、月结对账和金额 sign-off"),
                ],
                "ehs": [
                    ("scope", "确认 incident、chemical/hazard、permit 和合规场景边界"),
                    ("metrics", "确认 incident aging、corrective action closure、permit compliance 口径"),
                    ("workflow", "确认 report、risk assessment、containment、corrective action、verification 流程"),
                    ("data_acceptance", "确认 EHS 数据源、整改证据、法规口径和关闭验收"),
                ],
                "it_data": [
                    ("scope", "确认 source of truth、master data、接口和治理边界"),
                    ("metrics", "确认 interface success、latency、data quality 和 master-data completeness 口径"),
                    ("workflow", "确认 data change、validation、interface sync、reconciliation、remediation 流程"),
                    ("data_acceptance", "确认系统/表名、business key、权限审计、SLA 和 sign-off"),
                ],
                "management": [
                    ("scope", "确认经营 KPI、例会节奏、owner action 和跨部门升级边界"),
                    ("metrics", "确认 target/actual gap、action aging、closure rate 和 escalation 口径"),
                    ("workflow", "确认 KPI review、gap detection、owner action、escalation、closure 流程"),
                    ("data_acceptance", "确认目标版本、行动项来源、关闭证据和管理层 sign-off"),
                ],
            }
        elif normalized_language == "de":
            specs = {
                "production": [
                    ("scope", "Produkt, Werk, Linie, Route, lot/panel/unit und Finished Lot Boundary klaeren"),
                    ("metrics", "Output, WIP, scrap, rework, cycle time, throughput und yield Definitionen klaeren"),
                    ("workflow", "move-in/out, hold/release, rework/scrap und Finished Lot Entscheidungsprozess klaeren"),
                    ("data_acceptance", "Produktionsdaten, Stationsbewegung, Quality release, Abgleich und sign-off klaeren"),
                ],
                "tdi": [
                    ("scope", "Projektbezogene TDI Bedeutung, Objektumfang und Upstream/Downstream Boundary klaeren"),
                    ("metrics", "case aging, SLA hit rate, open/close count und handoff delay Definitionen klaeren"),
                    ("workflow", "TDI trigger, triage, action/approval, handoff, verification und closure Workflow klaeren"),
                    ("data_acceptance", "TDI Records, Handoff-Datenquellen, SLA Start/Ende, Writeback und Closure Acceptance klaeren"),
                ],
                "quality": [
                    ("scope", "Inspection points, defect taxonomy, spec limits und Quality release Boundary klaeren"),
                    ("metrics", "defect rate, loss ratio, retest/rework/scrap, CAPA aging und repeat defect Definitionen klaeren"),
                    ("workflow", "defect capture, disposition, MRB/CAPA, root cause, verification/release Workflow klaeren"),
                    ("data_acceptance", "Inspection/defect/disposition Quellen, lot genealogy, Closure Evidence und Quality sign-off klaeren"),
                ],
                "general": [
                    ("scope", "General Requesting Bereich, Business Owner, First-Version Softwareform und Szenario-Grenze klaeren"),
                    ("metrics", "General Business Decision/Action, Success Metrics, aktuelle Definitionen und Datengranularitaet klaeren"),
                    ("workflow", "General Nutzerprozess, Status, Owner, Exception Handling und Closure klaeren"),
                    ("data_acceptance", "General Datenquellen, Outputs, Acceptance Owner, Sign-off und Grenzen zu noch nicht freigegebenen Bereichen klaeren"),
                ],
                "planning": [
                    ("scope", "Demand/forecast, Capacity Boundary und First-Version Scheduling-Ziel klaeren"),
                    ("metrics", "Plan attainment, capacity loading, WIP aging und commit Definitionen klaeren"),
                    ("workflow", "Forecast lock, schedule release, dispatch change und expedite Workflow klaeren"),
                    ("data_acceptance", "Planning Quellen, Capacity Model, Commit Version und Abgleich klaeren"),
                ],
                "engineering": [
                    ("scope", "Route/recipe/spec/parameter, NPI oder Engineering Change Boundary klaeren"),
                    ("metrics", "Qualification pass rate, ECN aging und change cycle Definitionen klaeren"),
                    ("workflow", "Change request, DOE/trial, review, release und rollback Workflow klaeren"),
                    ("data_acceptance", "Engineering Quellen, release gates, Versionierung und Acceptance Owner klaeren"),
                ],
                "equipment": [
                    ("scope", "Equipment Scope, area/line, kritische Tools und Production/Quality Impact Boundary klaeren"),
                    ("metrics", "uptime/OEE, downtime, PM compliance und MTBF/MTTR Definitionen klaeren"),
                    ("workflow", "alarm/down, maintenance action, PM, release und recurrence review Workflow klaeren"),
                    ("data_acceptance", "Equipment Quellen, Maintenance Records, Lot-Bezug und Downtime Attribution klaeren"),
                ],
                "material": [
                    ("scope", "BOM/material number, supplier, incoming lot und supply risk Boundary klaeren"),
                    ("metrics", "incoming pass rate, shortage risk, inventory coverage und supplier lot Definitionen klaeren"),
                    ("workflow", "Procurement, IQC, Issue to Production, Hold und Substitution Approval Workflow klaeren"),
                    ("data_acceptance", "Material master, inventory/IQC Quellen, Lot Traceability und Usability Acceptance klaeren"),
                ],
                "warehouse": [
                    ("scope", "Finished Lot receipt, FG/WIP inventory, packing und shipment Boundary klaeren"),
                    ("metrics", "inventory aging, on-time shipment, hold stock und turnover Definitionen klaeren"),
                    ("workflow", "receive, store, pick/pack, hold check und ship Workflow klaeren"),
                    ("data_acceptance", "Inventory/shipping Quellen, QA/customer hold und Traceability Acceptance klaeren"),
                ],
                "customer": [
                    ("scope", "Customer/program, forecast/commit, complaint/RMA/8D Boundary klaeren"),
                    ("metrics", "commit hit rate, complaint aging, 8D closure und RMA recurrence Definitionen klaeren"),
                    ("workflow", "Customer demand/issue, internal mapping, owner assignment, response und closure Workflow klaeren"),
                    ("data_acceptance", "Customer Quellen, customer-lot zu internal-lot Traceability und Response Acceptance klaeren"),
                ],
                "finance": [
                    ("scope", "Cost object, cost center, loss type und Finance Responsibility Boundary klaeren"),
                    ("metrics", "scrap/rework/loss cost, variance und margin impact Definitionen klaeren"),
                    ("workflow", "Loss event, cost calculation, responsibility attribution, finance review und month-end lock Workflow klaeren"),
                    ("data_acceptance", "Finance/production-loss Quellen, month-end reconciliation und amount sign-off klaeren"),
                ],
                "ehs": [
                    ("scope", "Incident, chemical/hazard, permit und Compliance Scenario Boundary klaeren"),
                    ("metrics", "incident aging, corrective-action closure und permit-compliance Definitionen klaeren"),
                    ("workflow", "Report, risk assessment, containment, corrective action und verification Workflow klaeren"),
                    ("data_acceptance", "EHS Quellen, corrective evidence, compliance taxonomy und closure acceptance klaeren"),
                ],
                "it_data": [
                    ("scope", "Source of truth, master data, interfaces und Governance Boundary klaeren"),
                    ("metrics", "interface success, latency, data quality und master-data completeness Definitionen klaeren"),
                    ("workflow", "Data change, validation, interface sync, reconciliation und remediation Workflow klaeren"),
                    ("data_acceptance", "Systeme/Tabellen, business keys, access audit, SLA und sign-off klaeren"),
                ],
                "management": [
                    ("scope", "Operating KPIs, meeting cadence, owner actions und cross-department escalation Boundary klaeren"),
                    ("metrics", "target/actual gap, action aging, closure rate und escalation Definitionen klaeren"),
                    ("workflow", "KPI review, gap detection, owner action, escalation und closure Workflow klaeren"),
                    ("data_acceptance", "Target versions, action-item Quellen, closure evidence und Management sign-off klaeren"),
                ],
            }
        elif normalized_language == "ms":
            specs = {
                "production": [
                    ("scope", "Sahkan product, plant, line, route, lot/panel/unit dan Finished Lot boundary"),
                    ("metrics", "Sahkan definisi output, WIP, scrap, rework, cycle time, throughput dan yield"),
                    ("workflow", "Sahkan workflow move-in/out, hold/release, rework/scrap dan Finished Lot decision"),
                    ("data_acceptance", "Sahkan production records, station movement, quality release, reconciliation dan sign-off"),
                ],
                "tdi": [
                    ("scope", "Sahkan maksud TDI untuk projek, object scope dan upstream/downstream boundary"),
                    ("metrics", "Sahkan definisi case aging, SLA hit rate, open/close count dan handoff delay"),
                    ("workflow", "Sahkan workflow TDI trigger, triage, action/approval, handoff, verification dan closure"),
                    ("data_acceptance", "Sahkan TDI records, sumber data handoff, SLA start/end, writeback dan closure acceptance"),
                ],
                "quality": [
                    ("scope", "Sahkan inspection points, defect taxonomy, spec limits dan quality release boundary"),
                    ("metrics", "Sahkan definisi defect rate, loss ratio, retest/rework/scrap, CAPA aging dan repeat defect"),
                    ("workflow", "Sahkan workflow defect capture, disposition, MRB/CAPA, root cause, verification/release"),
                    ("data_acceptance", "Sahkan sumber inspection/defect/disposition, lot genealogy, closure evidence dan quality sign-off"),
                ],
                "general": [
                    ("scope", "Sahkan requesting department, business owner, first-version software shape dan scenario boundary untuk General"),
                    ("metrics", "Sahkan business decision/action, success metric, definisi semasa dan data grain untuk General"),
                    ("workflow", "Sahkan user workflow, status, owner, exception handling dan closure untuk General"),
                    ("data_acceptance", "Sahkan data sources, outputs, acceptance owner, sign-off dan boundary jabatan belum dibuka untuk General"),
                ],
                "planning": [
                    ("scope", "Sahkan demand/forecast, capacity boundary dan objektif scheduling versi pertama"),
                    ("metrics", "Sahkan definisi plan attainment, capacity loading, WIP aging dan commit"),
                    ("workflow", "Sahkan workflow forecast lock, schedule release, dispatch change dan expedite"),
                    ("data_acceptance", "Sahkan sumber planning, capacity model, commit version dan reconciliation"),
                ],
                "engineering": [
                    ("scope", "Sahkan route/recipe/spec/parameter, NPI atau engineering-change boundary"),
                    ("metrics", "Sahkan qualification pass rate, ECN aging dan change-cycle definitions"),
                    ("workflow", "Sahkan workflow change request, DOE/trial, review, release dan rollback"),
                    ("data_acceptance", "Sahkan sumber engineering, release gates, version control dan acceptance owners"),
                ],
                "equipment": [
                    ("scope", "Sahkan equipment scope, area/line, critical tools dan production/quality impact boundary"),
                    ("metrics", "Sahkan definisi uptime/OEE, downtime, PM compliance dan MTBF/MTTR"),
                    ("workflow", "Sahkan workflow alarm/down, maintenance action, PM, release dan recurrence review"),
                    ("data_acceptance", "Sahkan equipment sources, maintenance records, lot linkage dan downtime attribution acceptance"),
                ],
                "material": [
                    ("scope", "Sahkan BOM/material number, supplier, incoming lot dan supply-risk boundary"),
                    ("metrics", "Sahkan incoming pass rate, shortage risk, inventory coverage dan supplier-lot definitions"),
                    ("workflow", "Sahkan workflow procurement, IQC, issue-to-production, hold dan substitution approval"),
                    ("data_acceptance", "Sahkan material master, inventory/IQC sources, lot traceability dan usability acceptance"),
                ],
                "warehouse": [
                    ("scope", "Sahkan Finished Lot receipt, FG/WIP inventory, packing dan shipment boundary"),
                    ("metrics", "Sahkan inventory aging, on-time shipment, hold stock dan turnover definitions"),
                    ("workflow", "Sahkan workflow receive, store, pick/pack, hold check dan ship"),
                    ("data_acceptance", "Sahkan inventory/shipping sources, QA/customer hold dan traceability acceptance"),
                ],
                "customer": [
                    ("scope", "Sahkan customer/program, forecast/commit dan complaint/RMA/8D boundary"),
                    ("metrics", "Sahkan commit hit rate, complaint aging, 8D closure dan RMA recurrence definitions"),
                    ("workflow", "Sahkan workflow customer demand/issue, internal mapping, owner assignment, response dan closure"),
                    ("data_acceptance", "Sahkan customer sources, customer-lot to internal-lot traceability dan response acceptance"),
                ],
                "finance": [
                    ("scope", "Sahkan cost object, cost center, loss type dan finance responsibility boundary"),
                    ("metrics", "Sahkan scrap/rework/loss cost, variance dan margin-impact definitions"),
                    ("workflow", "Sahkan workflow loss event, cost calculation, responsibility attribution, finance review dan month-end lock"),
                    ("data_acceptance", "Sahkan finance/production-loss sources, month-end reconciliation dan amount sign-off"),
                ],
                "ehs": [
                    ("scope", "Sahkan incident, chemical/hazard, permit dan compliance scenario boundary"),
                    ("metrics", "Sahkan incident aging, corrective-action closure dan permit-compliance definitions"),
                    ("workflow", "Sahkan workflow report, risk assessment, containment, corrective action dan verification"),
                    ("data_acceptance", "Sahkan EHS sources, corrective evidence, compliance taxonomy dan closure acceptance"),
                ],
                "it_data": [
                    ("scope", "Sahkan source of truth, master data, interfaces dan governance boundary"),
                    ("metrics", "Sahkan interface success, latency, data quality dan master-data completeness definitions"),
                    ("workflow", "Sahkan workflow data change, validation, interface sync, reconciliation dan remediation"),
                    ("data_acceptance", "Sahkan systems/tables, business keys, access audit, SLA dan sign-off"),
                ],
                "management": [
                    ("scope", "Sahkan operating KPIs, meeting cadence, owner actions dan cross-department escalation boundary"),
                    ("metrics", "Sahkan target/actual gap, action aging, closure rate dan escalation definitions"),
                    ("workflow", "Sahkan workflow KPI review, gap detection, owner action, escalation dan closure"),
                    ("data_acceptance", "Sahkan target versions, action-item sources, closure evidence dan management sign-off"),
                ],
            }
        else:
            specs = {
                "production": [
                    ("scope", "Confirm product, plant, line, route, lot/panel/unit, and Finished Lot boundary"),
                    ("metrics", "Confirm output, WIP, scrap, rework, cycle time, throughput, and yield definitions"),
                    ("workflow", "Confirm move-in/out, hold/release, rework/scrap, and Finished Lot decision workflow"),
                    ("data_acceptance", "Confirm production records, station movement, quality release, reconciliation, and sign-off"),
                ],
                "tdi": [
                    ("scope", "Confirm project-specific TDI definition, object scope, and upstream/downstream boundary"),
                    ("metrics", "Confirm case aging, SLA hit rate, open/close count, and handoff-delay definitions"),
                    ("workflow", "Confirm TDI trigger, triage, action/approval, handoff, verification, and closure workflow"),
                    ("data_acceptance", "Confirm TDI records, handoff data sources, SLA start/end, writeback, and closure acceptance"),
                ],
                "quality": [
                    ("scope", "Confirm inspection points, defect taxonomy, spec limits, and quality-release boundary"),
                    ("metrics", "Confirm defect rate, loss ratio, retest/rework/scrap, CAPA aging, and repeat-defect definitions"),
                    ("workflow", "Confirm defect capture, disposition, MRB/CAPA, root cause, verification, and release workflow"),
                    ("data_acceptance", "Confirm inspection/defect/disposition sources, lot genealogy, closure evidence, and quality sign-off"),
                ],
                "general": [
                    ("scope", "Confirm General requesting department, business owner, first-version software shape, and scenario boundary"),
                    ("metrics", "Confirm General business decision/action, success metric, current definitions, and data grain"),
                    ("workflow", "Confirm General user workflow, status, owner, exception handling, and closure method"),
                    ("data_acceptance", "Confirm General data sources, outputs, acceptance owner, sign-off, and unopened-department boundary"),
                ],
                "planning": [
                    ("scope", "Confirm demand/forecast, capacity boundary, and first-version scheduling objective"),
                    ("metrics", "Confirm plan attainment, capacity loading, WIP aging, and commit definitions"),
                    ("workflow", "Confirm forecast lock, schedule release, dispatch change, and expedite workflow"),
                    ("data_acceptance", "Confirm planning sources, capacity model, commit version, and reconciliation"),
                ],
                "engineering": [
                    ("scope", "Confirm route/recipe/spec/parameter, NPI, or engineering-change boundary"),
                    ("metrics", "Confirm qualification pass rate, ECN aging, and change-cycle definitions"),
                    ("workflow", "Confirm change request, DOE/trial, review, release, and rollback workflow"),
                    ("data_acceptance", "Confirm engineering sources, release gates, version control, and acceptance owners"),
                ],
                "equipment": [
                    ("scope", "Confirm equipment scope, area/line, critical tools, and production/quality impact boundary"),
                    ("metrics", "Confirm uptime/OEE, downtime, PM compliance, and MTBF/MTTR definitions"),
                    ("workflow", "Confirm alarm/down, maintenance action, PM, release, and recurrence review workflow"),
                    ("data_acceptance", "Confirm equipment sources, maintenance records, lot linkage, and downtime attribution acceptance"),
                ],
                "material": [
                    ("scope", "Confirm BOM/material number, supplier, incoming lot, and supply-risk boundary"),
                    ("metrics", "Confirm incoming pass rate, shortage risk, inventory coverage, and supplier-lot definitions"),
                    ("workflow", "Confirm procurement, IQC, issue-to-production, hold, and substitution approval workflow"),
                    ("data_acceptance", "Confirm material master, inventory/IQC sources, lot traceability, and usability acceptance"),
                ],
                "warehouse": [
                    ("scope", "Confirm Finished Lot receipt, FG/WIP inventory, packing, and shipment boundary"),
                    ("metrics", "Confirm inventory aging, on-time shipment, hold stock, and turnover definitions"),
                    ("workflow", "Confirm receive, store, pick/pack, hold check, and ship workflow"),
                    ("data_acceptance", "Confirm inventory/shipping sources, QA/customer hold, and traceability acceptance"),
                ],
                "customer": [
                    ("scope", "Confirm customer/program, forecast/commit, complaint/RMA/8D boundary"),
                    ("metrics", "Confirm commit hit rate, complaint aging, 8D closure, and RMA recurrence definitions"),
                    ("workflow", "Confirm customer demand/issue, internal mapping, owner assignment, response, and closure workflow"),
                    ("data_acceptance", "Confirm customer sources, customer-lot to internal-lot traceability, and response acceptance"),
                ],
                "finance": [
                    ("scope", "Confirm cost object, cost center, loss type, and finance responsibility boundary"),
                    ("metrics", "Confirm scrap/rework/loss cost, variance, and margin-impact definitions"),
                    ("workflow", "Confirm loss event, cost calculation, responsibility attribution, finance review, and month-end lock workflow"),
                    ("data_acceptance", "Confirm finance/production-loss sources, month-end reconciliation, and amount sign-off"),
                ],
                "ehs": [
                    ("scope", "Confirm incident, chemical/hazard, permit, and compliance scenario boundary"),
                    ("metrics", "Confirm incident aging, corrective-action closure, and permit-compliance definitions"),
                    ("workflow", "Confirm report, risk assessment, containment, corrective action, and verification workflow"),
                    ("data_acceptance", "Confirm EHS sources, corrective evidence, compliance taxonomy, and closure acceptance"),
                ],
                "it_data": [
                    ("scope", "Confirm source of truth, master data, interfaces, and governance boundary"),
                    ("metrics", "Confirm interface success, latency, data quality, and master-data completeness definitions"),
                    ("workflow", "Confirm data change, validation, interface sync, reconciliation, and remediation workflow"),
                    ("data_acceptance", "Confirm systems/tables, business keys, access audit, SLA, and sign-off"),
                ],
                "management": [
                    ("scope", "Confirm operating KPIs, meeting cadence, owner actions, and cross-department escalation boundary"),
                    ("metrics", "Confirm target/actual gap, action aging, closure rate, and escalation definitions"),
                    ("workflow", "Confirm KPI review, gap detection, owner action, escalation, and closure workflow"),
                    ("data_acceptance", "Confirm target versions, action-item sources, closure evidence, and management sign-off"),
                ],
            }

        department_order = ACTIVE_IC_SUBSTRATE_DEPARTMENTS
        nodes: list[dict[str, Any]] = []
        for department in department_order:
            department_specs = specs[department]
            track = self._ic_substrate_department_label(department, language)
            for suffix, label in department_specs:
                nodes.append(
                    {
                        "track": track,
                        "department": department,
                        "node": f"{department}_{suffix}",
                        "label": label,
                        "status_keys": status_by_suffix[suffix],
                    }
                )
        return nodes

    def _conversation_chain_track_labels(
        self,
        nodes: list[dict[str, Any]],
        mode: str,
        language: str | None = None,
    ) -> list[str]:
        node_tracks = [str(node["track"]) for node in nodes]
        return self._unique_strings(node_tracks)

    def _ic_substrate_node_matches_intent_track(self, node: dict[str, Any], intent_track: str) -> bool:
        track = intent_track.strip().lower()
        if not track:
            return False
        department = str(node.get("department", "")).strip().lower()
        if department:
            return department == track
        return str(node.get("track", "")).strip().lower() == track

    def _chain_node_confirmed(self, collection_status: dict[str, Any], node: dict[str, Any]) -> bool:
        status_keys = node.get("status_keys")
        if not isinstance(status_keys, tuple):
            return False
        for key in status_keys:
            item = collection_status.get(key)
            if not isinstance(item, dict):
                return False
            status_value = str(item.get("status", "")).strip().lower()
            if status_value != CONVERSATION_CHAIN_STATUS_CONFIRMED:
                return False
        return True

    def _conversation_chain_question_source(self, template: dict[str, Any], mode: str) -> str:
        if mode == "ic_substrate":
            return "ic_substrate_department_first_chain"
        prompt_questions = template.get("prompt_questions")
        if isinstance(prompt_questions, list) and prompt_questions:
            return "template_prompt_questions"
        return "generic_template_chain"

    def _ic_substrate_production_tdi_quality_playbook_guidance(
        self,
        track: str,
        language: str | None = None,
    ) -> str:
        key = track.strip().lower()
        if key not in {"production", "tdi", "quality"}:
            return ""

        if self._normalize_language(language) == "zh":
            playbooks = {
                "production": {
                    "decision": "Finished Lot 完工判定、WIP/hold/release 处置、返工/报废责任、瓶颈站点、产出与周期改善优先级、standard-cost/cost simulation",
                    "kpi": "yield、output、WIP aging、scrap、rework、hold aging、cycle time、throughput、move queue；名称和公式以现场现行口径为准",
                    "master": "product family、plant、line、route、operation/station、lot/panel/unit、hold reason、rework loop、owner；不要自造 route 或站点名",
                    "workflow": "lot release -> move-in/out -> hold/release -> rework/scrap -> Finished Lot 判定 -> 产量/质量/仓储对账确认；状态名由用户提供",
                    "source": "生产记录、站点流转、WIP/hold/报废/返工记录、质量 release、入库或交接记录；系统名和表名由用户确认",
                    "acceptance": "Production owner、Quality owner、必要时 Warehouse/Planning owner 对 Finished Lot 判定点、数量、状态、时间窗和对账差异 sign-off",
                    "expert_checks": "yield 必须问 numerator/denominator、FPY/final yield/lot yield 差异、rework/scrap/hold 是否纳入；成本模拟必须问 standard-cost formula owner、Activity Rate/MOH 来源、Processing Time 来源、Yield 分母、Panel Utilization 规则和 SAP/Finance 写回边界；WIP aging 必须问 clock start/stop、pause 条件、cutoff timezone；Finished Lot 必须问质量 release、入库/交接和对账差异如何处理",
                    "ladder": "先问首版业务动作（排产/派工、WIP hold、Finished Lot、产量节拍、效率复盘）；再问 lot/panel/unit 与 route/station/time window；再问状态名、owner、异常处置；最后问 source of truth、对账、刷新和验收证据",
                },
                "tdi": {
                    "decision": "TDI 业务定义、触发边界、case 分类、状态机、owner/SLA、审批/验证、跨部门 handoff 和关闭条件",
                    "kpi": "case aging、SLA hit rate、open/close count、handoff delay、approval aging、reopen/repeat issue；名称和公式以用户 TDI 口径为准",
                    "master": "TDI case、trigger type、input/output、state、priority、owner、approval point、linked lot/project、closure evidence；不要展开 TDI",
                    "workflow": "trigger -> triage -> owner assignment -> action/approval -> handoff -> verification -> writeback -> closure；状态名由用户提供",
                    "source": "用户确认的 TDI 记录、生产/质量/工程/数据交接记录、审批/验证证据；不要预设 MES/QMS/ERP 等系统名",
                    "acceptance": "TDI owner、上下游业务 owner、最终验收 owner 对关闭条件、SLA 起止点、回写边界、重开规则和证据留存确认",
                    "expert_checks": "TDI 只能按用户现场定义处理；case 必须问 trigger source、case category、priority、linked lot/project；SLA 必须问 clock start/pause/stop、handoff owner matrix、approval/verification evidence；关闭必须问 closure/reopen rule、writeback target 和历史 case 迁移",
                    "ladder": "先问 TDI 在现场的定义和 case 触发边界；再问 case 类型、优先级、状态机、owner/SLA；再问 handoff、approval、verification、writeback；最后问 closure/reopen、证据留存和历史 case 迁移",
                },
                "quality": {
                    "decision": "检测覆盖、缺陷判定、MRB/CAPA 是否适用、retest/rework/scrap disposition、root cause 分析和质量 release 条件",
                    "kpi": "defect rate、loss ratio、retest/rework/scrap count、MRB aging、CAPA aging、repeat defect、release cycle time；公式以质量现行报表为准",
                    "master": "inspection point、defect code/taxonomy、spec limit、sampling rule、disposition reason、lot genealogy、responsible owner、release evidence；不要自造分类或规格",
                    "workflow": "inspection -> defect capture -> disposition/MRB -> root cause -> action/CAPA if used -> verification -> release/sign-off",
                    "source": "检测记录、缺陷记录、判定/处置记录、MRB/CAPA 记录、root cause 和验证证据；系统名和表名由用户确认",
                    "acceptance": "Quality owner、Production/Engineering owner、必要时 Customer owner 对缺陷口径、处置规则、release gate 和关闭证据 sign-off",
                    "expert_checks": "defect rate 必须问 denominator、inspection coverage、defect code hierarchy、repeat defect 定义；spec/sampling 必须问版本、生效时间和例外处理；MRB/CAPA 必须问触发条件、disposition owner、verification evidence、release gate 和 customer/internal sign-off",
                    "ladder": "先问首版质量动作（inspection coverage、defect disposition、release gate、MRB/CAPA、root cause、趋势分析）；再问 defect taxonomy、spec/sampling、lot genealogy；再问 disposition owner 与 closure evidence；最后问 release sign-off、客户/内部验收和证据留存",
                },
            }
            playbook = playbooks[key]
            product_shapes = self._ic_substrate_department_product_shapes(key, language)
            return (
                "部门专家 PM 访谈框架：\n"
                f"- 常见首版软件形态：{product_shapes}\n"
                f"- 软件要支撑的业务决策/动作：{playbook['decision']}\n"
                f"- 看板/报表要展示的 KPI/口径：{playbook['kpi']}\n"
                f"- 软件需要识别的主数据/对象：{playbook['master']}\n"
                f"- 软件要承载或反映的流程状态：{playbook['workflow']}\n"
                f"- 软件数据来源与接口边界：{playbook['source']}\n"
                f"- 软件验收与责任边界：{playbook['acceptance']}\n"
                f"- 专家必确认清单：{playbook['expert_checks']}\n"
                f"- 专家追问梯子：{playbook['ladder']}"
            )

        playbooks = {
            "production": {
                "decision": "Finished Lot completion, WIP/hold/release disposition, bottleneck station, rework/scrap responsibility, output and cycle-time improvement priority, standard-cost/cost simulation",
                "kpi": "yield, output, WIP aging, scrap, rework, hold aging, cycle time, throughput, move queue using the site's current names and formulas",
                "master": "product family, plant, line, route, operation/station, lot/panel/unit, hold reason, rework loop, owner; do not invent route or station names",
                "workflow": "lot release -> move-in/out -> hold/release -> rework/scrap -> Finished Lot decision -> production/quality/warehouse reconciliation, with user-provided state names",
                "source": "production records, station movement, WIP/hold/scrap/rework records, quality release, warehouse or handoff records; user confirms system/table names",
                "acceptance": "Production, Quality, and when needed Warehouse/Planning owners sign off Finished Lot decision point, quantities, states, time window, and reconciliation gaps",
                "expert_checks": "for yield, confirm numerator/denominator, FPY/final yield/lot yield differences, and whether rework/scrap/hold is included; for cost simulation, confirm standard-cost formula owner, Activity Rate/MOH source, Processing Time source, Yield denominator, Panel Utilization rule, and SAP/Finance writeback boundary; for WIP aging, confirm clock start/stop, pause conditions, and cutoff timezone; for Finished Lot, confirm quality release, warehouse/handoff, and reconciliation-gap handling",
                "ladder": "first ask the v1 business action such as scheduling/dispatch, WIP hold, Finished Lot, output rhythm, or efficiency review; then lot/panel/unit with route/station/time window; then state names, owners, and exception handling; finally source of truth, reconciliation, refresh, and acceptance evidence",
            },
            "tdi": {
                "decision": "TDI business definition, trigger boundary, case category, state machine, owner/SLA, approval/verification, cross-functional handoff, and closure condition",
                "kpi": "case aging, SLA hit rate, open/close count, handoff delay, approval aging, reopen/repeat issue using the user's TDI definitions",
                "master": "TDI case, trigger type, input/output, state, priority, owner, approval point, linked lot/project, closure evidence; do not expand TDI",
                "workflow": "trigger -> triage -> owner assignment -> action/approval -> handoff -> verification -> writeback -> closure, with user-provided state names",
                "source": "user-confirmed TDI records, production/quality/engineering/data handoff records, and approval/verification evidence; do not assume MES/QMS/ERP names",
                "acceptance": "TDI owner, upstream/downstream business owners, and final acceptance owner confirm closure condition, SLA start/end, writeback boundary, reopen rule, and evidence retention",
                "expert_checks": "treat TDI only as the user's site-defined term; for cases, confirm trigger source, case category, priority, and linked lot/project; for SLA, confirm clock start/pause/stop, handoff owner matrix, and approval/verification evidence; for closure, confirm closure/reopen rule, writeback target, and historical case migration",
                "ladder": "first ask the user's TDI definition and case trigger boundary; then case type, priority, state machine, owner/SLA; then handoff, approval, verification, and writeback; finally closure/reopen, evidence retention, and historical case migration",
            },
            "quality": {
                "decision": "inspection coverage, defect disposition, whether MRB/CAPA applies, retest/rework/scrap disposition, root-cause analysis, and quality release gates",
                "kpi": "defect rate, loss ratio, retest/rework/scrap count, MRB aging, CAPA aging, repeat defect, release cycle time using current Quality formulas",
                "master": "inspection point, defect code/taxonomy, spec limit, sampling rule, disposition reason, lot genealogy, responsible owner, release evidence; do not invent categories or specs",
                "workflow": "inspection -> defect capture -> disposition/MRB -> root cause -> action/CAPA if used -> verification -> release/sign-off",
                "source": "inspection, defect, disposition, MRB/CAPA, root-cause, and verification records; user confirms system/table names",
                "acceptance": "Quality, Production/Engineering, and when needed Customer owners sign off defect definition, disposition rule, release gate, and closure evidence",
                "expert_checks": "for defect rate, confirm denominator, inspection coverage, defect code hierarchy, and repeat-defect definition; for spec/sampling, confirm version, effective time, and exception handling; for MRB/CAPA, confirm trigger, disposition owner, verification evidence, release gate, and customer/internal sign-off",
                "ladder": "first ask the v1 quality action such as inspection coverage, defect disposition, release gate, MRB/CAPA, root cause, or trend analysis; then defect taxonomy, spec/sampling, and lot genealogy; then disposition owner and closure evidence; finally release sign-off, customer/internal acceptance, and evidence retention",
            },
        }
        playbook = playbooks[key]
        product_shapes = self._ic_substrate_department_product_shapes(key, language)
        return (
            "Department-expert PM interview playbook:\n"
            f"- Common first-version software shapes: {product_shapes}\n"
            f"- Business decision/action the software must support: {playbook['decision']}\n"
            f"- Dashboard/report KPI and definition: {playbook['kpi']}\n"
            f"- Master data/object the software must identify: {playbook['master']}\n"
            f"- Workflow states the software must carry or reflect: {playbook['workflow']}\n"
            f"- Software data sources and integration boundary: {playbook['source']}\n"
            f"- Software acceptance and ownership boundary: {playbook['acceptance']}\n"
            f"- Expert must-confirm checklist: {playbook['expert_checks']}\n"
            f"- Expert question ladder: {playbook['ladder']}"
        )

    def _ic_substrate_department_product_shapes(self, department: str, language: str | None = None) -> str:
        key = department.strip().lower()
        normalized_language = self._normalize_language(language)
        if normalized_language == "zh":
            product_shapes = {
                "production": "生产看板、排产/预测 simulation、capacity loading、WIP/hold/release tracking、Finished Lot 判定、良率/吞吐/周期分析、standard-cost/cost simulation、异常告警、交接对账",
                "tdi": "case tracking、handoff dashboard、SLA aging、审批/验证流、异常告警、数据回写对账",
                "quality": "质量看板、缺陷下钻、MRB/CAPA case tracking、release sign-off、报表导出、异常告警",
                "general": "通用业务看板、workflow/case tracking、data query、report/export、alerting、admin console、跨部门 cockpit",
                "planning": "排产看板、capacity loading、dispatch priority、commit 风险预警、forecast-to-schedule gap、expedite tracking",
                "engineering": "recipe/spec change tracking、NPI/qualification dashboard、DOE/trial lot 记录、root cause action tracking、release gate sign-off",
                "equipment": "downtime dashboard、PM execution tracking、alarm/event triage、spare-part risk、equipment release、lot-impact analysis",
                "material": "来料质量看板、shortage risk、supplier lot traceability、替代料审批、IQC issue tracking、库存可用性预警",
                "warehouse": "Finished Lot 入库看板、pick/pack/ship tracking、inventory aging、shipping hold、QA/customer release gate、traceability report",
                "customer": "customer commit dashboard、forecast/order tracking、complaint/RMA/8D case tracking、program milestone、customer spec compliance、response SLA",
                "finance": "scrap/rework cost dashboard、loss attribution、cost center variance、margin impact、month-end reconciliation、management report export",
                "ehs": "incident tracking、corrective action workflow、chemical usage dashboard、permit/compliance calendar、environmental report、audit evidence repository",
                "it_data": "data quality dashboard、interface SLA monitor、master data workflow、lineage/query catalog、access audit、reconciliation console",
                "management": "war room cockpit、KPI scorecard、target/actual gap review、owner action tracking、escalation board、meeting pack export",
            }
            return product_shapes.get(key, "dashboard、workflow/case tracking、report/export、alerting、admin console")
        if normalized_language == "de":
            product_shapes = {
                "production": "Production Dashboard, scheduling/forecast simulation, capacity loading, WIP/hold/release Tracking, Finished Lot Entscheidung, Yield/Throughput/Cycle-Time Analyse, standard-cost/cost simulation, Exception Alerting, Handoff-Reconciliation",
                "tdi": "case tracking, handoff dashboard, SLA aging, approval/verification flow, exception alerting, data writeback reconciliation",
                "quality": "Quality Dashboard, Defect Drill-down, MRB/CAPA case tracking, Release Sign-off, Report Export, Exception Alerting",
                "general": "General business dashboard, workflow/case tracking, data query, report/export, alerting, admin console, cross-department cockpit",
                "planning": "Scheduling Dashboard, Capacity Loading, Dispatch Priority, Commit-Risk Alerting, Forecast-to-Schedule Gap, Expedite Tracking",
                "engineering": "recipe/spec change tracking, NPI/qualification dashboard, DOE/trial-lot records, root-cause action tracking, release-gate sign-off",
                "equipment": "Downtime Dashboard, PM execution tracking, alarm/event triage, spare-part risk, equipment release, lot-impact analysis",
                "material": "Incoming-Quality Dashboard, shortage risk, supplier-lot traceability, substitute-material approval, IQC issue tracking, inventory availability alerting",
                "warehouse": "Finished Lot Receipt Dashboard, pick/pack/ship tracking, inventory aging, shipping hold, QA/customer release gate, traceability report",
                "customer": "Customer Commit Dashboard, forecast/order tracking, complaint/RMA/8D case tracking, program milestone, customer-spec compliance, response SLA",
                "finance": "scrap/rework cost dashboard, loss attribution, cost-center variance, margin impact, month-end reconciliation, management report export",
                "ehs": "incident tracking, corrective-action workflow, chemical usage dashboard, permit/compliance calendar, environmental report, audit evidence repository",
                "it_data": "data-quality dashboard, interface SLA monitor, master-data workflow, lineage/query catalog, access audit, reconciliation console",
                "management": "war-room cockpit, KPI scorecard, target/actual gap review, owner action tracking, escalation board, meeting-pack export",
            }
            return product_shapes.get(key, "dashboard, workflow/case tracking, report/export, alerting, admin console")
        if normalized_language == "ms":
            product_shapes = {
                "production": "production dashboard, scheduling/forecast simulation, capacity loading, WIP/hold/release tracking, Finished Lot decision, yield/throughput/cycle-time analysis, standard-cost/cost simulation, abnormal alerting, handoff reconciliation",
                "tdi": "case tracking, handoff dashboard, SLA aging, approval/verification flow, abnormal alerting, data writeback reconciliation",
                "quality": "quality dashboard, defect drill-down, MRB/CAPA case tracking, release sign-off, report export, abnormal alerting",
                "general": "general business dashboard, workflow/case tracking, data query, report/export, alerting, admin console, cross-department cockpit",
                "planning": "schedule dashboard, capacity loading, dispatch priority, commit-risk alerting, forecast-to-schedule gap, expedite tracking",
                "engineering": "recipe/spec change tracking, NPI/qualification dashboard, DOE/trial-lot records, root-cause action tracking, release-gate sign-off",
                "equipment": "downtime dashboard, PM execution tracking, alarm/event triage, spare-part risk, equipment release, lot-impact analysis",
                "material": "incoming-quality dashboard, shortage risk, supplier-lot traceability, substitute-material approval, IQC issue tracking, inventory availability alerting",
                "warehouse": "Finished Lot receipt dashboard, pick/pack/ship tracking, inventory aging, shipping hold, QA/customer release gate, traceability report",
                "customer": "customer commit dashboard, forecast/order tracking, complaint/RMA/8D case tracking, program milestone, customer-spec compliance, response SLA",
                "finance": "scrap/rework cost dashboard, loss attribution, cost-center variance, margin impact, month-end reconciliation, management report export",
                "ehs": "incident tracking, corrective-action workflow, chemical usage dashboard, permit/compliance calendar, environmental report, audit evidence repository",
                "it_data": "data-quality dashboard, interface SLA monitor, master-data workflow, lineage/query catalog, access audit, reconciliation console",
                "management": "war-room cockpit, KPI scorecard, target/actual gap review, owner action tracking, escalation board, meeting-pack export",
            }
            return product_shapes.get(key, "dashboard, workflow/case tracking, report/export, alerting, admin console")

        product_shapes = {
            "production": "production dashboard, scheduling/forecast simulation, capacity loading, WIP/hold/release tracking, Finished Lot decision, yield/throughput/cycle-time analysis, standard-cost/cost simulation, abnormal alerting, handoff reconciliation",
            "tdi": "case tracking, handoff dashboard, SLA aging, approval/verification flow, abnormal alerting, data writeback reconciliation",
            "quality": "quality dashboard, defect drill-down, MRB/CAPA case tracking, release sign-off, report export, abnormal alerting",
            "general": "general business dashboard, workflow/case tracking, data query, report/export, alerting, admin console, cross-department cockpit",
            "planning": "schedule dashboard, capacity loading, dispatch priority, commit-risk alerting, forecast-to-schedule gap, expedite tracking",
            "engineering": "recipe/spec change tracking, NPI/qualification dashboard, DOE/trial-lot records, root-cause action tracking, release-gate sign-off",
            "equipment": "downtime dashboard, PM execution tracking, alarm/event triage, spare-part risk, equipment release, lot-impact analysis",
            "material": "incoming-quality dashboard, shortage risk, supplier-lot traceability, substitute-material approval, IQC issue tracking, inventory availability alerting",
            "warehouse": "Finished Lot receipt dashboard, pick/pack/ship tracking, inventory aging, shipping hold, QA/customer release gate, traceability report",
            "customer": "customer commit dashboard, forecast/order tracking, complaint/RMA/8D case tracking, program milestone, customer-spec compliance, response SLA",
            "finance": "scrap/rework cost dashboard, loss attribution, cost-center variance, margin impact, month-end reconciliation, management report export",
            "ehs": "incident tracking, corrective-action workflow, chemical usage dashboard, permit/compliance calendar, environmental report, audit evidence repository",
            "it_data": "data-quality dashboard, interface SLA monitor, master-data workflow, lineage/query catalog, access audit, reconciliation console",
            "management": "war-room cockpit, KPI scorecard, target/actual gap review, owner action tracking, escalation board, meeting-pack export",
        }
        return product_shapes.get(key, "dashboard, workflow/case tracking, report/export, alerting, admin console")

    def _fallback_chain_node(self, language: str | None = None) -> dict[str, Any]:
        normalized_language = self._normalize_language(language)
        if normalized_language == "zh":
            return {"track": "模板链路", "node": "not_available", "label": "待开始", "status_keys": ()}
        if normalized_language == "de":
            return {"track": "Vorlagenkette", "node": "not_available", "label": "Noch nicht gestartet", "status_keys": ()}
        if normalized_language == "ms":
            return {"track": "Rantaian templat", "node": "not_available", "label": "Belum bermula", "status_keys": ()}
        return {"track": "Template chain", "node": "not_available", "label": "Not started", "status_keys": ()}

    def _ic_substrate_track_disambiguation_node(self, language: str | None = None) -> dict[str, Any]:
        normalized_language = self._normalize_language(language)
        if normalized_language == "zh":
            return {
                "track": "Routing",
                "node": "track_disambiguation",
                "label": "确认需求发起部门或业务 owner",
                "status_keys": (),
            }
        if normalized_language == "de":
            return {
                "track": "Routing",
                "node": "track_disambiguation",
                "label": "Anfordernden Bereich oder Business Owner klaeren",
                "status_keys": (),
            }
        if normalized_language == "ms":
            return {
                "track": "Routing",
                "node": "track_disambiguation",
                "label": "Sahkan jabatan pemohon atau business owner",
                "status_keys": (),
            }
        return {
            "track": "Routing",
            "node": "track_disambiguation",
            "label": "Confirm the requesting department or business owner",
            "status_keys": (),
        }

    def _ic_substrate_scope_triage_node(self, language: str | None = None) -> dict[str, Any]:
        normalized_language = self._normalize_language(language)
        if normalized_language == "zh":
            return {
                "track": "Routing",
                "node": "scope_triage",
                "label": "确认需求发起部门、业务 owner 和首版场景",
                "status_keys": (),
            }
        if normalized_language == "de":
            return {
                "track": "Routing",
                "node": "scope_triage",
                "label": "Anfordernden Bereich, Business Owner und First-Version Szenario klaeren",
                "status_keys": (),
            }
        if normalized_language == "ms":
            return {
                "track": "Routing",
                "node": "scope_triage",
                "label": "Sahkan jabatan pemohon, business owner dan senario versi pertama",
                "status_keys": (),
            }
        return {
            "track": "Routing",
            "node": "scope_triage",
            "label": "Confirm requesting department, business owner, and first-version scenario",
            "status_keys": (),
        }

    def _ic_substrate_department_fallback_node(
        self,
        department: str,
        language: str | None = None,
        intent_focus: str | None = None,
    ) -> dict[str, Any]:
        label = self._ic_substrate_department_label(department, language)
        focus = str(intent_focus or "").strip().lower()
        normalized_language = self._normalize_language(language)
        if normalized_language == "zh":
            labels_by_focus = {
                "metric_definition": f"确认 {label} 的 KPI、成本/数量口径和数据粒度",
                "workflow_state": f"确认 {label} 的流程状态、owner、SLA 和关闭条件",
                "data_integration": f"确认 {label} 的数据源、主数据、接口和对账方式",
                "alert_exception": f"确认 {label} 的异常阈值、升级规则和闭环证据",
                "drilldown_analysis": f"确认 {label} 的分析维度、追溯路径和根因闭环",
                "dashboard_view": f"确认 {label} 的看板决策场景、核心 KPI 和默认维度",
                "export_reporting": f"确认 {label} 的报表接收人、冻结口径和推送频率",
                "permission_role": f"确认 {label} 的角色权限、审批边界和最终责任人",
            }
            node_suffix = focus if focus in labels_by_focus else "department_discovery"
            return {
                "track": label,
                "node": f"{department}_{node_suffix}",
                "label": labels_by_focus.get(focus, f"确认 {label} 的业务目标、流程边界和数据口径"),
                "status_keys": (),
            }
        if normalized_language == "de":
            labels_by_focus = {
                "metric_definition": f"{label} KPIs, Kosten-/Mengenlogik und Datengranularitaet klaeren",
                "workflow_state": f"{label} Workflow States, Owner, SLA und Closure Criteria klaeren",
                "data_integration": f"{label} Datenquellen, Master Data, Interfaces und Reconciliation klaeren",
                "alert_exception": f"{label} Exception Thresholds, Escalation Rules und Closure Evidence klaeren",
                "drilldown_analysis": f"{label} Analyse-Dimensionen, Traceability Path und Root-Cause Closure klaeren",
                "dashboard_view": f"{label} Dashboard Decision Scenario, Core KPIs und Default Dimensions klaeren",
                "export_reporting": f"{label} Report Empfaenger, Frozen Definitions und Delivery Cadence klaeren",
                "permission_role": f"{label} Rollenrechte, Approval Boundaries und accountable Owner klaeren",
            }
            node_suffix = focus if focus in labels_by_focus else "department_discovery"
            return {
                "track": label,
                "node": f"{department}_{node_suffix}",
                "label": labels_by_focus.get(focus, f"{label} Ziele, Prozessgrenze und Datenlogik klaeren"),
                "status_keys": (),
            }
        if normalized_language == "ms":
            labels_by_focus = {
                "metric_definition": f"Sahkan KPI {label}, definisi kos/kuantiti dan data grain",
                "workflow_state": f"Sahkan workflow states, owner, SLA dan closure criteria untuk {label}",
                "data_integration": f"Sahkan sumber data, master data, interface dan reconciliation untuk {label}",
                "alert_exception": f"Sahkan exception thresholds, escalation rules dan closure evidence untuk {label}",
                "drilldown_analysis": f"Sahkan analysis dimensions, traceability path dan root-cause closure untuk {label}",
                "dashboard_view": f"Sahkan dashboard decision scenario, core KPIs dan default dimensions untuk {label}",
                "export_reporting": f"Sahkan report recipients, frozen definitions dan delivery cadence untuk {label}",
                "permission_role": f"Sahkan role permissions, approval boundaries dan accountable owners untuk {label}",
            }
            node_suffix = focus if focus in labels_by_focus else "department_discovery"
            return {
                "track": label,
                "node": f"{department}_{node_suffix}",
                "label": labels_by_focus.get(focus, f"Sahkan matlamat, process boundary dan data definitions untuk {label}"),
                "status_keys": (),
            }
        labels_by_focus = {
            "metric_definition": f"Confirm {label} KPIs, cost/quantity definitions, and data grain",
            "workflow_state": f"Confirm {label} workflow states, owners, SLA, and closure criteria",
            "data_integration": f"Confirm {label} data sources, master data, interfaces, and reconciliation",
            "alert_exception": f"Confirm {label} exception thresholds, escalation rules, and closure evidence",
            "drilldown_analysis": f"Confirm {label} analysis dimensions, traceability path, and root-cause closure",
            "dashboard_view": f"Confirm {label} dashboard decision scenario, core KPIs, and default dimensions",
            "export_reporting": f"Confirm {label} report recipients, frozen definitions, and delivery cadence",
            "permission_role": f"Confirm {label} role permissions, approval boundaries, and accountable owners",
        }
        node_suffix = focus if focus in labels_by_focus else "department_discovery"
        return {
            "track": label,
            "node": f"{department}_{node_suffix}",
            "label": labels_by_focus.get(focus, f"Confirm {label} goals, process boundary, and data definitions"),
            "status_keys": (),
        }

    def _ic_substrate_is_department(self, department: str) -> bool:
        return department.strip().lower() in ACTIVE_IC_SUBSTRATE_DEPARTMENTS

    def _ic_substrate_department_label(self, department: str, language: str | None = None) -> str:
        labels = {
            "production": ("Production", "Production"),
            "tdi": ("TDI", "TDI"),
            "quality": ("Quality", "Quality"),
            "general": ("General", "General"),
            "planning": ("Planning/PMC", "Planning/PMC"),
            "engineering": ("Engineering/Process", "Engineering/Process"),
            "equipment": ("Equipment/Maintenance", "Equipment/Maintenance"),
            "material": ("Material/Procurement", "Material/Procurement"),
            "warehouse": ("Warehouse/Logistics", "Warehouse/Logistics"),
            "customer": ("Customer/Program", "Customer/Program"),
            "finance": ("Finance/Cost", "Finance/Cost"),
            "ehs": ("EHS", "EHS"),
            "it_data": ("IT/Data Governance", "IT/Data Governance"),
            "management": ("Management/Ops Excellence", "Management/Ops Excellence"),
        }
        zh_label, en_label = labels.get(department.strip().lower(), (department, department))
        return zh_label if self._normalize_language(language) == "zh" else en_label

    def _ic_substrate_department_playbook_guidance(
        self,
        department: str,
        language: str | None = None,
    ) -> str:
        key = department.strip().lower()
        if not self._ic_substrate_is_department(key):
            return ""
        if key in {"production", "tdi", "quality"}:
            return self._ic_substrate_production_tdi_quality_playbook_guidance(key, language)

        if self._normalize_language(language) == "zh":
            playbooks = {
                "general": {
                    "decision": "其他部门或不明确需求的首版软件目标、业务决策/动作、MVP 边界和待开放部门边界",
                    "kpi": "业务成功指标、当前报表口径、处理时效、异常数量、使用频率；公式以用户现行口径为准",
                    "master": "requesting department、business owner、primary user、business object、status、output artifact、acceptance owner",
                    "workflow": "request -> review/operate -> output/report/action -> exception handling -> sign-off/closure",
                    "source": "用户确认的数据源、人工台账、现有报表、上下游系统；不要预设系统名",
                    "acceptance": "业务 owner、使用者、IT/Data owner 对首版范围、输出物、数据口径和验收标准确认",
                },
                "planning": {
                    "decision": "排产承诺、产能缺口、dispatch 优先级、交期风险升级",
                    "kpi": "plan attainment、capacity loading、WIP aging、commit hit rate",
                    "master": "customer demand、forecast version、route capacity、priority class",
                    "workflow": "forecast lock -> capacity check -> schedule release -> dispatch change -> expedite/commit update",
                    "source": "计划表、产能模型、生产 WIP、客户交期承诺；系统名未确认前用通用描述",
                    "acceptance": "计划 owner、生产 owner、客户/项目 owner 对同一 commit 版本 sign-off",
                },
                "engineering": {
                    "decision": "recipe/spec/route 变更、NPI/qualification release、异常 root cause 关闭",
                    "kpi": "change cycle time、qualification pass rate、ECN aging、repeat issue rate",
                    "master": "route、recipe、spec、parameter、ECN/ECR、trial lot、release gate",
                    "workflow": "change request -> impact assessment -> trial/DOE -> review -> release/rollback",
                    "source": "工程变更记录、试作数据、规格文件、生产/质量反馈；不要自造系统名",
                    "acceptance": "工程 owner、生产 owner、质量 owner 对 release 条件和回滚条件确认",
                },
                "equipment": {
                    "decision": "downtime 归因、PM 执行闭环、备件风险、设备状态是否影响生产/质量",
                    "kpi": "uptime/OEE、downtime minutes、PM compliance、MTBF/MTTR；公式以用户现行口径为准",
                    "master": "equipment id、area/line、PM plan、alarm category、spare part、maintenance owner",
                    "workflow": "alarm/down -> triage -> maintenance action -> production release -> recurrence review",
                    "source": "设备状态记录、维修记录、PM 计划、生产批次/质量结果；不要自造 EAP/SPC 等术语",
                    "acceptance": "设备 owner、生产 owner、质量 owner 确认停机归因和 release 证据",
                },
                "material": {
                    "decision": "来料质量、缺料风险、替代料使用、供应商/批次对良率和交期影响",
                    "kpi": "incoming pass rate、shortage risk、inventory coverage、supplier lot issue rate",
                    "master": "material number、BOM、supplier、incoming lot、IQC result、substitute rule",
                    "workflow": "demand -> procurement/incoming -> IQC -> issue to production -> hold/substitution",
                    "source": "物料主数据、BOM、来料批次、库存、IQC 结果；系统名未确认前不指定品牌",
                    "acceptance": "物料 owner、质量 owner、生产/计划 owner 对可用性和风险归因确认",
                },
                "warehouse": {
                    "decision": "Finished Lot 入库、出货冻结、库存周转、包装/客户限制是否满足",
                    "kpi": "inventory aging、shipment on-time、hold stock、turnover、traceability completeness",
                    "master": "FG/WIP inventory、lot、packing spec、carrier、ship-to/customer restriction",
                    "workflow": "receive -> store -> pick/pack -> QA/customer hold check -> ship -> proof of delivery",
                    "source": "库存记录、包装/出货记录、质量 release、客户限制；不要自造承运商或系统名",
                    "acceptance": "仓储 owner、质量 owner、客户/项目 owner 对发货条件和追溯证据确认",
                },
                "customer": {
                    "decision": "forecast/commit 管理、客诉/RMA/8D 优先级、客户规格影响和沟通 SLA",
                    "kpi": "commit hit rate、complaint aging、8D closure time、RMA recurrence、customer spec compliance",
                    "master": "customer、program、customer lot、order/forecast、spec、complaint/RMA/8D case",
                    "workflow": "customer demand/issue -> internal mapping -> owner assignment -> response -> closure confirmation",
                    "source": "客户需求、订单/forecast、客诉/RMA/8D 记录、内部 lot 追溯；客户术语以用户提供为准",
                    "acceptance": "客户/项目 owner、质量 owner、生产/工程 owner 对回复口径和关闭证据确认",
                },
                "finance": {
                    "decision": "scrap/rework/loss cost 归因、cost center 责任、报价/毛利影响、月结对账",
                    "kpi": "scrap cost、rework cost、loss amount、cost center variance、margin impact；公式以财务现行口径为准",
                    "master": "cost center、product/customer、process step、loss reason、standard/actual cost definition",
                    "workflow": "loss event -> cost calculation -> responsibility attribution -> finance review -> month-end lock",
                    "source": "生产损失记录、返工/报废记录、成本中心、财务月结数据；不要自造标准成本或实际成本公式",
                    "acceptance": "财务 owner、生产/质量 owner、责任部门 owner 对金额和归因 sign-off",
                },
                "ehs": {
                    "decision": "incident 等级、化学品/危化风险、废液废气合规、整改优先级和关闭证据",
                    "kpi": "incident aging、corrective action closure、permit compliance、chemical usage variance、repeat incident",
                    "master": "chemical、hazard class、permit、incident type、corrective action、responsible owner",
                    "workflow": "incident/report -> risk assessment -> containment -> corrective action -> verification -> closure",
                    "source": "事件记录、化学品台账、permit/合规记录、整改证据；法规等级以用户现场口径为准",
                    "acceptance": "EHS owner、现场责任 owner、管理层/合规 owner 对整改证据和关闭条件确认",
                },
                "it_data": {
                    "decision": "source of truth、master data owner、接口 SLA、数据质量、权限审计和 lineage",
                    "kpi": "interface success rate、data latency、data quality issue aging、master-data completeness、access audit findings",
                    "master": "system/source、business key、master data、data owner、interface contract、access role",
                    "workflow": "data change -> validation -> interface sync -> reconciliation -> issue remediation",
                    "source": "源系统、接口日志、主数据表、权限审计、对账记录；系统品牌和表名由用户确认",
                    "acceptance": "IT/Data owner、业务 data owner、下游使用方对数据口径和 SLA sign-off",
                },
                "management": {
                    "decision": "经营 KPI 优先级、目标/actual gap、owner action、跨部门升级和例会节奏",
                    "kpi": "daily/weekly/monthly KPI、target gap、action aging、closure rate、escalation count",
                    "master": "KPI definition、target、owner、meeting cadence、action item、escalation rule",
                    "workflow": "KPI review -> gap detection -> owner action -> escalation -> closure/sign-off",
                    "source": "各部门指标、行动项、例会纪要、目标版本；不要混用未确认的统计口径",
                    "acceptance": "管理层 owner、部门 owner 对 KPI 口径、行动闭环和升级规则确认",
                },
            }
            playbook = playbooks.get(key, {})
            if not playbook:
                return ""
            product_shapes = self._ic_substrate_department_product_shapes(key, language)
            return (
                "PM 访谈框架：\n"
                f"- 常见首版软件形态：{product_shapes}\n"
                f"- 软件要支撑的业务决策/动作：{playbook['decision']}\n"
                f"- 看板/报表要展示的 KPI/口径：{playbook['kpi']}\n"
                f"- 软件需要识别的主数据/对象：{playbook['master']}\n"
                f"- 软件要承载或反映的流程状态：{playbook['workflow']}\n"
                f"- 软件数据来源与接口边界：{playbook['source']}\n"
                f"- 软件验收与责任边界：{playbook['acceptance']}"
            )

        playbooks = {
            "general": {
                "decision": "first-version software goal for another or unclear department, business decision/action, MVP boundary, and unopened-department boundary",
                "kpi": "business success metric, current report definition, processing time, exception volume, usage frequency, using the user's current formulas",
                "master": "requesting department, business owner, primary user, business object, status, output artifact, acceptance owner",
                "workflow": "request -> review/operate -> output/report/action -> exception handling -> sign-off/closure",
                "source": "user-confirmed data sources, manual trackers, existing reports, upstream/downstream systems; do not presume system names",
                "acceptance": "business owner, users, and IT/Data owner confirm first-version scope, outputs, data definitions, and acceptance criteria",
            },
            "planning": {
                "decision": "schedule commitment, capacity gap, dispatch priority, delivery-risk escalation",
                "kpi": "plan attainment, capacity loading, WIP aging, commit hit rate",
                "master": "customer demand, forecast version, route capacity, priority class",
                "workflow": "forecast lock -> capacity check -> schedule release -> dispatch change -> expedite/commit update",
                "source": "planning tables, capacity model, production WIP, customer commit; keep system names generic until confirmed",
                "acceptance": "planning, production, and customer/program owners sign off the same commit version",
            },
            "engineering": {
                "decision": "recipe/spec/route changes, NPI/qualification release, abnormal root-cause closure",
                "kpi": "change cycle time, qualification pass rate, ECN aging, repeat issue rate",
                "master": "route, recipe, spec, parameter, ECN/ECR, trial lot, release gate",
                "workflow": "change request -> impact assessment -> trial/DOE -> review -> release/rollback",
                "source": "engineering change records, trial data, specs, production/quality feedback; do not invent system names",
                "acceptance": "engineering, production, and quality owners confirm release and rollback criteria",
            },
            "equipment": {
                "decision": "downtime attribution, PM closure, spare-part risk, equipment impact on production/quality",
                "kpi": "uptime/OEE, downtime minutes, PM compliance, MTBF/MTTR using the user's current formulas",
                "master": "equipment id, area/line, PM plan, alarm category, spare part, maintenance owner",
                "workflow": "alarm/down -> triage -> maintenance action -> production release -> recurrence review",
                "source": "equipment status, maintenance records, PM plans, lot/quality outcomes; do not invent EAP/SPC terms",
                "acceptance": "equipment, production, and quality owners confirm downtime attribution and release evidence",
            },
            "material": {
                "decision": "incoming quality, shortage risk, substitute-material use, supplier/lot impact on yield and delivery",
                "kpi": "incoming pass rate, shortage risk, inventory coverage, supplier-lot issue rate",
                "master": "material number, BOM, supplier, incoming lot, IQC result, substitution rule",
                "workflow": "demand -> procurement/incoming -> IQC -> issue to production -> hold/substitution",
                "source": "material master, BOM, incoming lot, inventory, IQC results; do not name system brands until confirmed",
                "acceptance": "material, quality, production/planning owners confirm usability and risk attribution",
            },
            "warehouse": {
                "decision": "Finished Lot receipt, shipping hold, inventory turnover, packing/customer restrictions",
                "kpi": "inventory aging, shipment on-time, hold stock, turnover, traceability completeness",
                "master": "FG/WIP inventory, lot, packing spec, carrier, ship-to/customer restriction",
                "workflow": "receive -> store -> pick/pack -> QA/customer hold check -> ship -> proof of delivery",
                "source": "inventory, packing/shipping, quality release, customer restrictions; do not invent carriers or systems",
                "acceptance": "warehouse, quality, and customer/program owners confirm shipping gates and traceability evidence",
            },
            "customer": {
                "decision": "forecast/commit management, complaint/RMA/8D priority, customer-spec impact, communication SLA",
                "kpi": "commit hit rate, complaint aging, 8D closure time, RMA recurrence, customer-spec compliance",
                "master": "customer, program, customer lot, order/forecast, spec, complaint/RMA/8D case",
                "workflow": "customer demand/issue -> internal mapping -> owner assignment -> response -> closure confirmation",
                "source": "customer demand, order/forecast, complaint/RMA/8D records, internal lot traceability; use user-provided terminology",
                "acceptance": "customer/program, quality, production/engineering owners confirm response definition and closure evidence",
            },
            "finance": {
                "decision": "scrap/rework/loss-cost attribution, cost-center responsibility, quote/margin impact, month-end reconciliation",
                "kpi": "scrap cost, rework cost, loss amount, cost-center variance, margin impact using Finance's current formulas",
                "master": "cost center, product/customer, process step, loss reason, standard/actual cost definition",
                "workflow": "loss event -> cost calculation -> responsibility attribution -> finance review -> month-end lock",
                "source": "production loss, rework/scrap records, cost center, finance close data; do not invent costing formulas",
                "acceptance": "finance, production/quality, and responsible department owners sign off amount and attribution",
            },
            "ehs": {
                "decision": "incident level, chemical/hazard risk, wastewater/exhaust compliance, corrective-action priority and evidence",
                "kpi": "incident aging, corrective-action closure, permit compliance, chemical usage variance, repeat incident",
                "master": "chemical, hazard class, permit, incident type, corrective action, responsible owner",
                "workflow": "incident/report -> risk assessment -> containment -> corrective action -> verification -> closure",
                "source": "incident records, chemical register, permit/compliance records, corrective evidence; use user's compliance taxonomy",
                "acceptance": "EHS, site owner, and management/compliance owners confirm evidence and closure criteria",
            },
            "it_data": {
                "decision": "source of truth, master-data owner, interface SLA, data quality, access audit, lineage",
                "kpi": "interface success rate, data latency, data-quality issue aging, master-data completeness, access audit findings",
                "master": "system/source, business key, master data, data owner, interface contract, access role",
                "workflow": "data change -> validation -> interface sync -> reconciliation -> issue remediation",
                "source": "source systems, interface logs, master data, access audit, reconciliation records; user confirms system/table names",
                "acceptance": "IT/Data owner, business data owner, and downstream users sign off data definitions and SLA",
            },
            "management": {
                "decision": "operating KPI priority, target/actual gap, owner action, cross-department escalation, meeting cadence",
                "kpi": "daily/weekly/monthly KPI, target gap, action aging, closure rate, escalation count",
                "master": "KPI definition, target, owner, meeting cadence, action item, escalation rule",
                "workflow": "KPI review -> gap detection -> owner action -> escalation -> closure/sign-off",
                "source": "department metrics, action items, meeting notes, target versions; do not mix unconfirmed definitions",
                "acceptance": "management and department owners confirm KPI definitions, action closure, and escalation rules",
            },
        }
        playbook = playbooks.get(key, {})
        if not playbook:
            return ""
        product_shapes = self._ic_substrate_department_product_shapes(key, language)
        return (
            "PM interview playbook:\n"
            f"- Common first-version software shapes: {product_shapes}\n"
            f"- Business decision/action the software must support: {playbook['decision']}\n"
            f"- Dashboard/report KPI and definition: {playbook['kpi']}\n"
            f"- Master data/object the software must identify: {playbook['master']}\n"
            f"- Workflow states the software must carry or reflect: {playbook['workflow']}\n"
            f"- Software data sources and integration boundary: {playbook['source']}\n"
            f"- Software acceptance and ownership boundary: {playbook['acceptance']}"
        )

    def _latest_user_message_text(self, session: Session) -> str:
        for message in reversed(session.messages):
            if message.get("role") == "user":
                return str(message.get("content", ""))
        return ""

    def _ic_substrate_intent_track_from_latest_user_message(self, session: Session) -> str:
        user_texts = self._user_message_texts(session)
        if not user_texts:
            return ""

        latest_text = user_texts[-1]
        latest_track = self._ic_substrate_intent_track_from_text(latest_text)
        prior_track = ""
        for previous_text in reversed(user_texts[:-1]):
            prior_track = self._ic_substrate_intent_track_from_text(previous_text)
            if prior_track:
                break

        if prior_track and self._ic_substrate_should_preserve_prior_track(
            latest_text,
            latest_track,
            prior_track,
        ):
            return prior_track
        return latest_track

    def _ic_substrate_intent_track_from_structured_model(self, model: dict[str, Any]) -> str:
        product_context = model.get("product_context") if isinstance(model.get("product_context"), dict) else {}
        department = str(product_context.get("requesting_department", "")).strip()
        if not department:
            return ""
        track = self._ic_substrate_intent_track_from_text(department)
        return track if self._ic_substrate_is_department(track) else ""

    def _user_message_texts(self, session: Session) -> list[str]:
        return [
            str(message.get("content", ""))
            for message in session.messages
            if message.get("role") == "user" and str(message.get("content", "")).strip()
        ]

    def _ic_substrate_should_preserve_prior_track(
        self,
        latest_text: str,
        latest_track: str,
        prior_track: str,
    ) -> bool:
        if not prior_track:
            return False
        if not latest_track:
            return True
        if latest_track == prior_track:
            return False
        if self._ic_substrate_has_explicit_track_name(latest_text, latest_track):
            return False
        if latest_track in {"production", "quality"}:
            return not self._ic_substrate_has_strong_track_signal(latest_text, latest_track)
        return False

    def _ic_substrate_has_explicit_track_name(self, text: str, track: str) -> bool:
        normalized = text.lower()
        explicit_keywords = {
            "production": ("production", "生产", "产线"),
            "tdi": (
                "tdi",
                "case/sla",
                "case sla",
                "case tracker",
                "case tracking",
                "case handoff",
                "request intake",
                "triage",
                "sla",
                "工程需求",
                "需求单",
                "需求流程",
                "case追踪",
                "case 跟踪",
                "case流程",
                "case 流程",
                "跨部门 handoff",
                "跨部门交接",
                "跨部门移交",
                "handoff",
                "验证闭环",
                "验证进度",
                "验证看板",
                "验证计划",
                "工程验证",
                "doe",
                "validation",
                "qualification",
                "trial lot",
                "engineering data",
                "工程数据",
                "数据映射",
                "recipe和spec",
                "recipe/spec",
                "spec参数",
                "参数对比",
                "参数查询",
                "对比查询",
                "试验",
                "试验批",
                "closure",
            ),
            "quality": ("quality", "品质", "质量"),
            "general": ("general", "通用", "其他", "其它", "其他部门", "别的部门", "不确定", "跨部门"),
            "planning": ("planning", "pmc", "计划"),
            "engineering": ("engineering", "工艺", "工程"),
            "equipment": ("equipment", "设备"),
            "material": ("material", "procurement", "材料", "物料", "采购"),
            "warehouse": ("warehouse", "logistics", "仓库", "物流"),
            "customer": ("customer", "program", "sales", "客户", "销售"),
            "finance": ("finance", "cost", "财务", "成本"),
            "ehs": ("ehs", "环保", "安全"),
            "it_data": ("it/data", "it data", "it 数据", "it 部门", "data governance", "数据治理"),
            "management": ("management", "管理层", "经营"),
        }
        return any(keyword in normalized for keyword in explicit_keywords.get(track.strip().lower(), ()))

    def _ic_substrate_has_strong_track_signal(self, text: str, track: str) -> bool:
        normalized = text.lower()
        strong_keywords = {
            "production": (
                "production",
                "生产",
                "产线",
                "线别",
                "finished lot",
                "wip",
                "throughput",
                "cycle time",
            ),
            "quality": (
                "quality",
                "品质",
                "质量",
                "检测",
                "检验",
                "inspection",
                "inspection coverage",
                "sampling",
                "aoi",
                "fvi",
                "e-test",
                "coverage",
                "false call",
                "missed defect",
                "检验覆盖率",
                "检测覆盖率",
                "覆盖率",
                "抽样",
                "全检",
                "漏检",
                "误判",
                "defect",
                "缺陷",
                "缺陷pareto",
                "缺陷分布",
                "不良原因",
                "不良分布",
                "不良看板",
                "mrb",
                "capa",
                "pareto",
                "root cause",
            ),
            "tdi": (
                "tdi",
                "case/sla",
                "case tracker",
                "handoff",
                "验证闭环",
                "验证进度",
                "验证看板",
                "验证计划",
                "工程验证",
                "doe",
                "validation",
                "qualification",
                "trial lot",
                "engineering data",
                "工程数据",
                "数据映射",
                "recipe和spec",
                "recipe/spec",
                "spec参数",
                "参数对比",
                "参数查询",
                "对比查询",
                "试验",
                "试验批",
            ),
        }
        return any(keyword in normalized for keyword in strong_keywords.get(track.strip().lower(), ()))

    def _ic_substrate_track_from_template(self, template: dict[str, Any] | None) -> str:
        """Infer department track from an applied business template's metadata."""
        if not isinstance(template, dict):
            return ""
        for field in ("business_domain", "template_category", "template_key", "template_id"):
            track = self._ic_substrate_intent_track_from_text(str(template.get(field, "")))
            if track:
                return track
        return ""

    def _ic_substrate_intent_track_from_text(self, text: str) -> str:
        """Detect department track from free text using domain_pack business_objects."""
        lowered = (text or "").lower()
        if not lowered:
            return ""

        # Department aliases (display names + common abbreviations)
        department_aliases = {
            "production": ("production", "生产", "prod", "manufacturing", "fertigung", "pengeluaran"),
            "quality": ("quality", "qdm", "qa", "qc", "质量", "品质", "qualitaet", "kualiti"),
            "tdi": ("tdi", "工艺", "engineering data", "technology development", "teknologi"),
        }
        for track, aliases in department_aliases.items():
            if any(alias in lowered for alias in aliases):
                return track

        # Fall back to scanning domain_pack business_objects
        from .ic_substrate_domain import load_ic_substrate_domain_pack
        pack = load_ic_substrate_domain_pack()
        departments = pack.get("departments", {}) if isinstance(pack, dict) else {}
        scores: dict[str, int] = {}
        for dept_key, dept_info in departments.items():
            if dept_key == "general":
                continue
            if not isinstance(dept_info, dict):
                continue
            objects = dept_info.get("business_objects") or []
            if not isinstance(objects, list):
                continue
            score = sum(1 for obj in objects if isinstance(obj, str) and obj.lower() in lowered)
            if score:
                scores[dept_key] = score
        if not scores:
            return ""
        # Pick the department with the strongest evidence
        best_track = max(scores.items(), key=lambda item: item[1])[0]
        return best_track if self._ic_substrate_is_department(best_track) else ""

    def _ic_substrate_intent_focus_from_latest_user_message(self, session: Session) -> str:
        user_texts = self._user_message_texts(session)
        if not user_texts:
            return ""

        latest_text = user_texts[-1]
        latest_focus = self._ic_substrate_intent_focus_from_text(latest_text)
        if latest_focus:
            return latest_focus

        latest_track = self._ic_substrate_intent_track_from_text(latest_text)
        if latest_track:
            return ""
        prior_track = ""
        for previous_text in reversed(user_texts[:-1]):
            prior_track = self._ic_substrate_intent_track_from_text(previous_text)
            if prior_track:
                break
        if latest_track and prior_track and latest_track != prior_track:
            return ""

        for previous_text in reversed(user_texts[:-1]):
            prior_focus = self._ic_substrate_intent_focus_from_text(previous_text)
            if prior_focus:
                return prior_focus
        return ""

    def _ic_substrate_product_shape_from_latest_user_message(self, session: Session) -> str:
        user_texts = self._user_message_texts(session)
        if not user_texts:
            return ""

        latest_shape = self._ic_substrate_product_shape_from_text(user_texts[-1])
        if latest_shape and latest_shape != "dashboard":
            return latest_shape

        for previous_text in reversed(user_texts[:-1]):
            prior_shape = self._ic_substrate_product_shape_from_text(previous_text)
            if prior_shape and prior_shape != "dashboard":
                return prior_shape
        if latest_shape:
            return latest_shape
        for previous_text in reversed(user_texts[:-1]):
            prior_shape = self._ic_substrate_product_shape_from_text(previous_text)
            if prior_shape:
                return prior_shape
        return ""

    def _ic_substrate_department_from_product_shape(self, product_shape: str) -> str:
        shape = product_shape.strip().lower()
        shape_departments = {
            "planning_simulation": "production",
            "wip_status_dashboard": "production",
            "dispatch_priority_expedite_tracker": "production",
            "lot_hold_release_tracker": "production",
            "finished_lot_handoff_dashboard": "production",
            "cycle_time_bottleneck_dashboard": "production",
            "production_cost_simulation": "production",
            "production_delivery_commit_risk_dashboard": "production",
            "production_equipment_downtime_oee_dashboard": "production",
            "production_material_shortage_readiness_dashboard": "production",
            "yield_dashboard": "quality",
            "quality_spc_process_capability_dashboard": "quality",
            "quality_iqc_supplier_lot_issue_tracker": "quality",
            "defect_pareto_dashboard": "quality",
            "inspection_coverage_dashboard": "quality",
            "quality_release_evidence_dashboard": "quality",
            "quality_mrb_disposition_tracker": "quality",
            "scrap_rework_responsibility_tracker": "quality",
            "quality_capa_8d_closure_tracker": "quality",
            "validation_tracker": "tdi",
            "tdi_npi_handoff_readiness_tracker": "tdi",
            "tdi_trial_lot_issue_tracker": "tdi",
            "engineering_change_approval_tracker": "tdi",
            "engineering_data_query": "tdi",
        }
        return shape_departments.get(shape, "")

    def _ic_substrate_product_shape_from_text(self, text: str) -> str:
        """Match a product_shape key from domain_pack.json against free text.

        Uses both the shape key (e.g. 'planning_simulation') and its label
        (e.g. 'Planning simulation') as anchors. Picks the longest match
        so multi-word labels beat single-word keys.
        """
        lowered = (text or "").lower()
        if not lowered:
            return ""

        from .ic_substrate_domain import load_ic_substrate_domain_pack
        pack = load_ic_substrate_domain_pack()
        shapes = pack.get("product_shapes", {}) if isinstance(pack, dict) else {}

        aliases: dict[str, str] = {
            "workflow": "workflow_tracker",
            "case tracker": "workflow_tracker",
            "scheduling": "planning_simulation",
            "schedule": "planning_simulation",
            "forecast": "planning_simulation",
            "forecasting": "planning_simulation",
            "capacity loading": "planning_simulation",
            "report": "report_export",
            "export": "report_export",
            "query": "data_query",
            "search": "data_query",
            "alert": "alerting",
            "alarm": "alerting",
            "admin": "admin_tool",
            "console": "admin_tool",
            "dashboard": "dashboard",
            "tracker": "workflow_tracker",
        }
        candidates: list[tuple[int, str]] = []
        for key, info in shapes.items():
            if not isinstance(info, dict):
                continue
            key_lower = key.lower().replace("_", " ")
            label = str(info.get("label") or "").lower()
            anchors = [key_lower, label]
            for anchor, mapped_key in aliases.items():
                if mapped_key == key:
                    anchors.append(anchor)
            for anchor in anchors:
                if anchor and anchor in lowered:
                    candidates.append((len(anchor), key))
        if not candidates:
            return ""
        candidates.sort(reverse=True)
        return candidates[0][1]

    def _ic_substrate_intent_focus_from_text(self, text: str) -> str:
        """Detect a soft focus hint from glossary seed terms.

        Returns the first matching glossary term (lowercased) or empty string.
        Used only as a routing hint, not as ground truth.
        """
        lowered = (text or "").lower()
        if not lowered:
            return ""
        from .ic_substrate_domain import load_ic_substrate_domain_pack
        pack = load_ic_substrate_domain_pack()
        terms = pack.get("glossary_seed_terms", []) if isinstance(pack, dict) else []
        if not isinstance(terms, list):
            return ""
        for term in terms:
            term_lower = str(term or "").lower()
            if term_lower and term_lower in lowered:
                return term_lower
        return ""

    def _ic_substrate_preferred_node_for_intent(self, intent_track: str, intent_focus: str) -> str:
        track = intent_track.strip().lower()
        focus = intent_focus.strip().lower()
        if not track or not focus:
            return ""

        if self._ic_substrate_is_department(track):
            focus_suffix = {
                "metric_definition": "metrics",
                "dashboard_view": "metrics",
                "export_reporting": "data_acceptance",
                "data_integration": "data_acceptance",
                "permission_role": "data_acceptance",
                "workflow_state": "workflow",
                "alert_exception": "workflow",
                "drilldown_analysis": "workflow",
            }.get(focus)
            if focus_suffix:
                return f"{track}_{focus_suffix}"
            return f"{track}_scope"
        return ""

    def _ic_substrate_current_node_question_guidance(
        self,
        chain_state: dict[str, Any],
        language: str | None = None,
    ) -> str:
        if chain_state.get("mode") != "ic_substrate":
            return ""

        node = str(chain_state.get("current_node", "")).strip()
        department_guidance = self._ic_substrate_department_question_guidance(chain_state, language)
        if department_guidance:
            return department_guidance
        current_track = str(chain_state.get("current_track", "")).strip()
        track_playbook = self._ic_substrate_production_tdi_quality_playbook_guidance(current_track, language)

        if self._normalize_language(language) == "zh":
            guidance_by_node = {
                "scope_triage": (
                    "当前节点专业追问方向：\n"
                    "- 用户只给了宽泛目标，没有明确部门/业务 owner 或需求形态；第一问先确认需求来自哪个部门、谁是首版 owner，不要直接问字段、页面或技术栈。\n"
                    "- 当前 IT scope 只开放 Production、Quality、TDI、General；首问选项只能列这四个入口，不要展开其他部门。\n"
                    "- 首问选项里不要展开 TDI，也不要自造 EAP/SPC/MES/QMS/ERP 等未确认系统或内部术语。\n"
                    "- 好问题示例：这个 IC Substrate 需求首版主要由哪个入口发起并负责验收：Production、Quality、TDI，还是 General？"
                ),
                "track_disambiguation": (
                    "当前节点专业追问方向：\n"
                    "- 用户已经表达了需求形态，但没有说明发起部门或业务 owner；先问部门归属，不要默认套到 Production/TDI/Quality。\n"
                    "- 当前 IT scope 只开放 Production、Quality、TDI、General；如果用户想做其他部门，归入 General，不要展开隐藏部门专家链路。\n"
                    "- 好问题示例：这个需求当前应归到哪个已开放入口来定义首版：Production、Quality、TDI，还是 General？"
                ),
                "production_scope": (
                    "当前节点专业追问方向：\n"
                    "- 优先确认 Production 的业务对象和边界：product family、plant、line、route、lot/panel/unit 粒度、Finished Lot 的判定点、时间窗口。\n"
                    "- 不要擅自给出未确认的具体站点缩写；如果用户还没给站点名，用最后生产站出站、入库、QA release 这类通用判定点。\n"
                    "- 如果 Finished Lot 判定点和粒度都缺，先问 Finished Lot 判定点，下一轮再问粒度；不要用“另外”追加第二问。\n"
                    "- 好问题示例：首版 Production 里 Finished Lot 的完工判定以哪个时点为准：最后生产站出站、入库，还是 QA release？"
                ),
                "production_flow": (
                    "当前节点专业追问方向：\n"
                    "- 优先确认工序和站点流转：route/operation/station、move-in/move-out、hold/release、rework loop、equipment/recipe 是否要纳入。\n"
                    "- 好问题示例：Production flow 里哪些站点是首版必须串起来的关键节点？每个 lot 在这些站点需要记录 move-in、move-out、hold、release、rework 哪些状态？"
                ),
                "production_metrics": (
                    "当前节点专业追问方向：\n"
                    "- 优先确认用户现行指标公式和数据口径：input、output、good、scrap、rework、WIP、cycle time、throughput、良率类指标的计算边界。\n"
                    "- 不要替用户预设 FPY/final yield/lot yield 等名称或公式；先问现场现在怎么命名和计算。\n"
                    "- 好问题示例：你们现在老板看的核心 Production 指标叫什么，分母/分子、统计粒度和时间窗口分别是什么，报废和返工是否单独拆出口径？"
                ),
                "tdi_definition": (
                    "当前节点专业追问方向：\n"
                    "- 优先确认 TDI 在你们组织里的定义；在用户确认前，只写 TDI，不要加括号解释或替用户展开。\n"
                    "- 好问题示例：这个项目里 TDI 具体指哪条业务链路？是新产品/新工艺导入试作，还是 Production/Quality 数据接口集成，或者你们内部另有定义？"
                ),
                "tdi_handoff": (
                    "当前节点专业追问方向：\n"
                    "- 优先确认 TDI 的触发、输入输出、状态机、owner、SLA、审批点，以及它和上游/下游生产、质量或数据系统的交接边界。\n"
                    "- 不要自造状态名、SLA 数字、owner 角色或审批层级；先问用户现在实际使用的状态和口径。\n"
                    "- 好问题示例：你们现在一个 TDI case 从触发到关闭实际有哪些状态，每个状态由哪个角色负责，SLA 是按哪个起止点计算，什么条件才算关闭？"
                ),
                "quality_rules": (
                    "当前节点专业追问方向：\n"
                    "- 优先确认用户现行检测和判定规则：inspection point、defect code/taxonomy、spec limit、sampling/full inspection、retest/rework/scrap/MRB disposition。\n"
                    "- 不要自造检测点、缺陷分类、规格上下限或 MRB/CAPA 状态；先问用户现行质量口径。\n"
                    "- 好问题示例：Quality 首版要覆盖你们现行哪些检测点和缺陷分类，缺陷发生后的判定规则、责任 owner 和关闭证据现在分别是什么？"
                ),
                "quality_drilldown": (
                    "当前节点专业追问方向：\n"
                    "- 优先确认质量分析和闭环：defect Pareto、root cause 维度、lot genealogy、station/equipment/recipe 关联、CAPA/改善措施和验证结果。\n"
                    "- 不要替用户预设 root cause 维度或 CAPA 关闭标准；先问当前报表和会议怎么追因。\n"
                    "- 好问题示例：质量下钻时你们现在最常用的 root cause 维度是什么，CAPA 如果适用，需要哪些验证数据才算关闭？"
                ),
                "acceptance": (
                    "当前节点专业追问方向：\n"
                    "- 优先确认验收和对账：Production/TDI/Quality 三条链路各自的验收口径、数据延迟、历史回补、系统对账、owner sign-off。\n"
                    "- 好问题示例：首版上线验收时，Production、TDI、Quality 分别要和哪些系统或报表对账，允许的数据延迟是多少，谁最终 sign-off？"
                ),
            }
            base_guidance = guidance_by_node.get(node, "")
            if base_guidance and track_playbook:
                return base_guidance + "\n" + track_playbook
            return base_guidance

        guidance_by_node = {
                "scope_triage": (
                    "Current-node professional question guidance:\n"
                    "- The user only gave a broad goal without a clear department/business owner or need type. First confirm the requesting department and first-version owner; do not jump into fields, pages, or tech stack.\n"
                    "- The current IT scope exposes only Production, Quality, TDI, and General. The first question may list only these four entry points.\n"
                    "- Do not expand TDI in first-question options, and do not invent unconfirmed system/internal terms such as EAP/SPC/MES/QMS/ERP.\n"
                    "- Strong question example: Which open entry point is requesting and accepting the first IC Substrate version: Production, Quality, TDI, or General?"
                ),
            "track_disambiguation": (
                "Current-node professional question guidance:\n"
                "- The user expressed a need focus but did not identify the requesting department or business owner. Ask for department ownership first instead of defaulting to Production/TDI/Quality.\n"
                "- The current IT scope exposes only Production, Quality, TDI, and General. If the need belongs to another department, route it to General instead of continuing a hidden expert chain.\n"
                "- Strong question example: Which opened entry point should own this first version: Production, Quality, TDI, or General?"
            ),
            "production_scope": (
                "Current-node professional question guidance:\n"
                "- First confirm the Production business object and boundary: product family, plant, line, route, lot/panel/unit grain, Finished Lot decision point, and time window.\n"
                "- Do not invent specific station abbreviations; if the user has not named the station, use generic decision points such as final production move-out, warehouse receipt, or QA release.\n"
                "- If both Finished Lot decision point and grain are missing, ask the Finished Lot decision point first and leave grain for the next turn; do not append a second question.\n"
                "- Strong question example: In the first Production scope, which decision point defines Finished Lot completion: final production move-out, warehouse receipt, or QA release?"
            ),
            "production_flow": (
                "Current-node professional question guidance:\n"
                "- First confirm process and station movement: route/operation/station, move-in/move-out, hold/release, rework loop, and whether equipment/recipe matter.\n"
                "- Strong question example: Which key stations must the first Production flow connect, and should each lot track move-in, move-out, hold, release, and rework states at those stations?"
            ),
            "production_metrics": (
                "Current-node professional question guidance:\n"
                "- First confirm the user's current metric formulas and grain: input, output, good, scrap, rework, WIP, cycle time, throughput, and yield-related boundaries.\n"
                "- Do not prescribe FPY/final yield/lot yield names or formulas. Ask how the site names and calculates the metric today.\n"
                "- Strong question example: What is the current Production metric leadership reads, what are its numerator/denominator, grain, and time window, and are scrap/rework split out?"
            ),
            "tdi_definition": (
                "Current-node professional question guidance:\n"
                "- First confirm what TDI means in the user's organization. Until confirmed, write only TDI and do not add parenthetical expansions.\n"
                "- Strong question example: In this project, which business chain does TDI refer to: new product/process trial introduction, Production/Quality data integration, or another internal definition?"
            ),
            "tdi_handoff": (
                "Current-node professional question guidance:\n"
                "- First confirm TDI trigger, inputs/outputs, state machine, owner, SLA, approval points, and handoff boundaries with upstream/downstream production, quality, or data systems.\n"
                "- Do not invent state names, SLA numbers, owner roles, or approval levels. First ask for the user's actual states and definitions.\n"
                "- Strong question example: What states does a TDI case actually move through from trigger to closure in your organization, who owns each state, how is SLA measured, and what makes the case closed?"
            ),
            "quality_rules": (
                "Current-node professional question guidance:\n"
                "- First confirm the user's current inspection and disposition rules: inspection point, defect code/taxonomy, spec limits, sampling/full inspection, retest/rework/scrap/MRB disposition.\n"
                "- Do not invent inspection points, defect categories, spec limits, or MRB/CAPA states. Ask for the user's current Quality definitions.\n"
                "- Strong question example: Which current inspection points and defect categories are in scope, and what are the existing disposition owner and closure evidence?"
            ),
            "quality_drilldown": (
                "Current-node professional question guidance:\n"
                "- First confirm quality analysis closure: defect Pareto, root-cause dimensions, lot genealogy, station/equipment/recipe linkage, CAPA/improvement action, and validation result.\n"
                "- Do not prescribe root-cause dimensions or CAPA closure criteria. Ask how the current report or review meeting investigates root cause.\n"
                "- Strong question example: In today's Quality review, which dimensions are used for root-cause drill-down, and if CAPA applies, what validation evidence closes it?"
            ),
            "acceptance": (
                "Current-node professional question guidance:\n"
                "- First confirm acceptance and reconciliation: sign-off criteria for Production/TDI/Quality, data latency, historical backfill, system reconciliation, and owner approval.\n"
                "- Strong question example: At launch acceptance, which systems or reports must Production, TDI, and Quality reconcile against, what latency is allowed, and who signs off?"
            ),
        }
        base_guidance = guidance_by_node.get(node, "")
        if base_guidance and track_playbook:
            return base_guidance + "\n" + track_playbook
        return base_guidance

    def _ic_substrate_department_question_guidance(
        self,
        chain_state: dict[str, Any],
        language: str | None = None,
    ) -> str:
        department = str(chain_state.get("intent_track", "")).strip().lower()
        if not self._ic_substrate_is_department(department):
            return ""
        playbook_guidance = self._ic_substrate_department_playbook_guidance(department, language)
        current_node = str(chain_state.get("current_node", "")).strip()
        current_node_label = str(chain_state.get("current_node_label", "")).strip()

        if self._normalize_language(language) == "zh":
            node_suffix = current_node.removeprefix(f"{department}_")
            node_guidance_by_suffix = {
                "scope": "- 当前专家链路节点先确认首版软件形态、目标用户、使用场景、业务对象、决策/动作、首版边界和验收 owner；不要先跳到页面细节或技术实现。",
                "metrics": "- 当前专家链路节点先确认软件要展示/计算的 KPI 名称、公式、分子分母、时间窗、粒度、排除项，以及用户在例会/报表/看板里如何使用。",
                "workflow": "- 当前专家链路节点先确认软件要承载的触发条件、状态流转、owner、SLA 起止点、异常升级、关闭证据和待办/通知边界。",
                "data_acceptance": "- 当前专家链路节点先确认软件数据的 source of truth、主数据、接口/对账、权限审计、数据延迟、刷新频率和最终 sign-off。",
            }
            node_guidance = ""
            if current_node_label:
                node_guidance = f"当前专家链路节点：{current_node_label}\n{node_guidance_by_suffix.get(node_suffix, '')}".strip()
            guidance_by_department = {
                "production": (
                    "当前部门专业追问方向：Production\n"
                    "- 先确认 Production 想开发的软件形态和使用场景：生产看板、WIP/hold/release tracking、Finished Lot 判定、良率/吞吐/周期分析、异常告警或交接对账；再追 product family、plant、line、route、lot/panel/unit 粒度、WIP/scrap/rework 和 owner。\n"
                    "- 好问题示例：Production 首版这个系统主要给谁用来做什么：看良率/产出 dashboard、追 WIP/hold/release 状态，还是做 Finished Lot 完工判定和对账？"
                ),
                "tdi": (
                    "当前部门专业追问方向：TDI\n"
                    "- 先确认 TDI 想开发的软件形态和使用场景：case tracking、handoff dashboard、SLA aging、审批/验证流、异常告警或数据回写对账；不要擅自展开 TDI，再追本项目 TDI 定义、触发条件、输入输出、状态流转、owner/SLA、审批点和交接边界。\n"
                    "- 好问题示例：TDI 首版这个系统主要是用来追 case 状态/SLA、管理跨部门 handoff，还是做审批验证和关闭对账？"
                ),
                "quality": (
                    "当前部门专业追问方向：Quality\n"
                    "- 先确认 Quality 想开发的软件形态和使用场景：质量看板、缺陷下钻、MRB/CAPA case tracking、release sign-off、报表导出或异常告警；再追 inspection point、defect code/taxonomy、spec limit、MRB 判定、root cause、CAPA/改善闭环和 release 证据。\n"
                    "- 好问题示例：Quality 首版这个系统主要是给谁用来做什么：看缺陷/良率 dashboard、追 MRB/CAPA 流程，还是做 release/sign-off 对账？"
                ),
                "general": (
                    "当前部门专业追问方向：General\n"
                    "- 先确认 General 需求的真实发起部门、业务 owner、首版软件形态和使用场景：通用业务看板、workflow/case tracking、data query、report/export、alerting、admin console 或跨部门 cockpit；其他隐藏部门不要展开成独立专家链路。\n"
                    "- 好问题示例：General 首版这个系统主要给谁用来完成什么业务动作：看一个业务 dashboard、追一个流程/case 状态，还是查询/导出一份固定口径的数据？"
                ),
                "planning": (
                    "当前部门专业追问方向：Planning/PMC\n"
                    "- 先确认 Planning/PMC 想开发的软件形态和使用场景：排产看板、capacity loading、dispatch priority、commit 风险预警、forecast-to-schedule gap 或 expedite tracking；再追 demand/forecast、产能约束、排产规则、WIP aging、交期承诺和异常升级。\n"
                    "- 好问题示例：Planning/PMC 首版这个系统主要给谁用来做什么：看产能缺口 dashboard、排 lot dispatch 优先级，还是追客户 commit 风险和 expedite 闭环？"
                ),
                "engineering": (
                    "当前部门专业追问方向：Engineering/Process\n"
                    "- 先确认 Engineering/Process 想开发的软件形态和使用场景：recipe/spec change tracking、NPI/qualification dashboard、DOE/trial lot 记录、root cause action tracking 或 release gate sign-off；再追 route/recipe/spec/parameter、工程变更、试作数据和回滚条件。\n"
                    "- 好问题示例：Engineering 首版这个系统主要是管理 recipe/spec 变更、NPI qualification 进度，还是追异常 root cause 和 release gate sign-off？"
                ),
                "equipment": (
                    "当前部门专业追问方向：Equipment/Maintenance\n"
                    "- 先确认 Equipment/Maintenance 想开发的软件形态和使用场景：downtime dashboard、PM execution tracking、alarm/event triage、spare-part risk、equipment release 或 lot-impact analysis；再追 uptime/OEE、downtime 原因、PM 计划、MTBF/MTTR 和对 Production/Quality 的影响。\n"
                    "- 好问题示例：Equipment 首版这个系统主要给谁用来做什么：看 downtime/OEE dashboard、追 PM 执行闭环，还是把停机事件关联到 lot、station、recipe 或 defect 结果？"
                ),
                "material": (
                    "当前部门专业追问方向：Material/Procurement\n"
                    "- 先确认 Material/Procurement 想开发的软件形态和使用场景：来料质量看板、shortage risk、supplier lot traceability、替代料审批、IQC issue tracking 或库存可用性预警；再追 BOM/料号、供应商、来料批次、IQC、库存、替代料和对良率/交期的影响。\n"
                    "- 好问题示例：Material 首版这个系统主要是追供应商来料质量、库存缺料风险，还是替代料审批和 supplier lot 到生产 lot 的追溯？"
                ),
                "warehouse": (
                    "当前部门专业追问方向：Warehouse/Logistics\n"
                    "- 先确认 Warehouse/Logistics 想开发的软件形态和使用场景：Finished Lot 入库看板、pick/pack/ship tracking、inventory aging、shipping hold、QA/customer release gate 或 traceability report；再追 FG/WIP 库存、批次追溯、包装/发货和客户交付窗口。\n"
                    "- 好问题示例：Warehouse 首版这个系统主要给谁用来做什么：看 Finished Lot 入库/库存 aging、追出货状态，还是做 QA/customer hold release 和批次追溯？"
                ),
                "customer": (
                    "当前部门专业追问方向：Customer/Program/Sales/FAE\n"
                    "- 先确认 Customer/Program 想开发的软件形态和使用场景：customer commit dashboard、forecast/order tracking、complaint/RMA/8D case tracking、program milestone、customer spec compliance 或 response SLA；再追 customer lot 到内部 lot/panel、defect code 和责任部门的追溯。\n"
                    "- 好问题示例：Customer/Program 首版这个系统主要给谁用来做什么：看 forecast/commit 风险、追客户 complaint/RMA/8D 闭环，还是管理客户规格和回复 SLA？"
                ),
                "finance": (
                    "当前部门专业追问方向：Finance/Cost\n"
                    "- 先确认 Finance/Cost 想开发的软件形态和使用场景：scrap/rework cost dashboard、loss attribution、cost center variance、margin impact、month-end reconciliation 或 management report export；再追金额口径、责任归因、产品/客户/工序维度和月结锁定规则。\n"
                    "- 好问题示例：Finance 首版这个系统主要给谁用来做什么：看报废/返工损失 dashboard、做 cost center 归因，还是支持月结对账和管理报表导出？"
                ),
                "ehs": (
                    "当前部门专业追问方向：EHS\n"
                    "- 先确认 EHS 想开发的软件形态和使用场景：incident tracking、corrective action workflow、chemical usage dashboard、permit/compliance calendar、environmental report 或 audit evidence repository；再追事件等级、整改证据、法规口径、owner 和关闭条件。\n"
                    "- 好问题示例：EHS 首版这个系统主要给谁用来做什么：追 incident/整改闭环、看化学品/排放合规 dashboard，还是生成法规/稽核报表？"
                ),
                "it_data": (
                    "当前部门专业追问方向：IT/Data Governance\n"
                    "- 先确认 IT/Data Governance 想开发的软件形态和使用场景：data quality dashboard、interface SLA monitor、master data workflow、lineage/query catalog、access audit 或 reconciliation console；再追 source of truth、business key、数据 owner、接口合约、回写责任和系统 owner。\n"
                    "- 好问题示例：IT/Data 首版这个系统主要给谁用来做什么：监控接口 SLA、治理 master data，还是做 source of truth/lineage 和权限审计？"
                ),
                "management": (
                    "当前部门专业追问方向：Management/Ops Excellence\n"
                    "- 先确认 Management/Ops Excellence 想开发的软件形态和使用场景：war room cockpit、KPI scorecard、target/actual gap review、owner action tracking、escalation board 或 meeting pack export；再追 KPI 口径、例会节奏、owner action、升级规则、闭环证据和 sign-off。\n"
                    "- 好问题示例：Management 首版这个系统主要给谁用来做什么：看经营 KPI scorecard、追 owner action 闭环，还是支持 war room 跨部门升级和例会输出？"
                ),
            }
            base_guidance = guidance_by_department.get(department, "")
            if node_guidance:
                base_guidance = (node_guidance + ("\n" + base_guidance if base_guidance else "")).strip()
            if base_guidance and playbook_guidance:
                return base_guidance + "\n" + playbook_guidance
            return base_guidance or playbook_guidance

        node_suffix = current_node.removeprefix(f"{department}_")
        node_guidance_by_suffix = {
            "scope": "- This expert-chain node first confirms first-version software shape, target user, use case, business object, decision/action, boundary, and acceptance owner. Do not jump to page details or implementation.",
            "metrics": "- This expert-chain node first confirms the KPI the software must show/calculate, formula, numerator/denominator, time window, grain, exclusions, and how users consume it in meetings, reports, or dashboards.",
            "workflow": "- This expert-chain node first confirms the workflow the software must carry: trigger, state flow, owner, SLA start/end, escalation, closure evidence, and task/notification boundary.",
            "data_acceptance": "- This expert-chain node first confirms software data source of truth, master data, interfaces/reconciliation, access audit, data latency, refresh cadence, and final sign-off.",
        }
        node_guidance = ""
        if current_node_label:
            node_guidance = f"Current expert-chain node: {current_node_label}\n{node_guidance_by_suffix.get(node_suffix, '')}".strip()
        guidance_by_department = {
            "production": (
                "Current department guidance: Production\n"
                "- First confirm the Production software shape and use case: production dashboard, WIP/hold/release tracking, Finished Lot decision, yield/throughput/cycle-time analysis, abnormal alerting, or handoff reconciliation. Then clarify product family, plant, line, route, lot/panel/unit grain, WIP/scrap/rework, and owners.\n"
                "- Strong question example: For the first Production version, who uses this system and for what main job: yield/output dashboard, WIP/hold/release tracking, or Finished Lot completion and reconciliation?"
            ),
            "tdi": (
                "Current department guidance: TDI\n"
                "- First confirm the TDI software shape and use case: case tracking, handoff dashboard, SLA aging, approval/verification flow, abnormal alerting, or writeback reconciliation. Do not expand TDI; then clarify this project's TDI definition, trigger, inputs/outputs, state flow, owner/SLA, approval points, and handoff boundary.\n"
                "- Strong question example: For the first TDI version, is the main job case/SLA tracking, cross-department handoff management, or approval, verification, and closure reconciliation?"
            ),
            "quality": (
                "Current department guidance: Quality\n"
                "- First confirm the Quality software shape and use case: quality dashboard, defect drill-down, MRB/CAPA case tracking, release sign-off, report export, or abnormal alerting. Then clarify inspection point, defect code/taxonomy, spec limit, MRB disposition, root cause, CAPA/improvement closure, and release evidence.\n"
                "- Strong question example: For the first Quality version, who uses this system and for what main job: defect/yield dashboard, MRB/CAPA tracking, or release/sign-off reconciliation?"
            ),
            "general": (
                "Current department guidance: General\n"
                "- First confirm the real requesting department, business owner, first-version software shape, and use case: general business dashboard, workflow/case tracking, data query, report/export, alerting, admin console, or cross-department cockpit. Do not expand hidden departments into separate expert chains.\n"
                "- Strong question example: For the first General version, who uses this system and for what main business action: reading a business dashboard, tracking workflow/case status, or querying/exporting data with a fixed definition?"
            ),
            "planning": (
                "Current department guidance: Planning/PMC\n"
                "- First confirm the Planning/PMC software shape and use case: schedule dashboard, capacity loading, dispatch priority, commit-risk alerting, forecast-to-schedule gap, or expedite tracking. Then clarify demand/forecast, capacity constraints, scheduling rules, WIP aging, delivery commitment, and escalation.\n"
                "- Strong question example: For the first Planning/PMC version, who uses this system and for what main job: capacity-gap dashboard, lot dispatch priority, or customer commit risk and expedite closure?"
            ),
            "engineering": (
                "Current department guidance: Engineering/Process\n"
                "- First confirm the Engineering/Process software shape and use case: recipe/spec change tracking, NPI/qualification dashboard, DOE/trial-lot records, root-cause action tracking, or release-gate sign-off. Then clarify route/recipe/spec/parameter, engineering change, trial data, and rollback criteria.\n"
                "- Strong question example: For the first Engineering version, is the main job recipe/spec change management, NPI qualification progress, or abnormal root-cause and release-gate sign-off?"
            ),
            "equipment": (
                "Current department guidance: Equipment/Maintenance\n"
                "- First confirm the Equipment/Maintenance software shape and use case: downtime dashboard, PM execution tracking, alarm/event triage, spare-part risk, equipment release, or lot-impact analysis. Then clarify uptime/OEE, downtime reason, PM plan, MTBF/MTTR, and Production/Quality impact.\n"
                "- Strong question example: For the first Equipment version, who uses this system and for what main job: downtime/OEE dashboard, PM closure tracking, or linking downtime events to lots, stations, recipes, or defect outcomes?"
            ),
            "material": (
                "Current department guidance: Material/Procurement\n"
                "- First confirm the Material/Procurement software shape and use case: incoming-quality dashboard, shortage risk, supplier-lot traceability, substitute-material approval, IQC issue tracking, or inventory availability alerting. Then clarify BOM/material number, supplier, incoming lot, IQC, inventory, substitute rules, and yield/delivery impact.\n"
                "- Strong question example: For the first Material version, is the main job supplier incoming quality, shortage-risk monitoring, substitute-material approval, or supplier lot to production lot traceability?"
            ),
            "warehouse": (
                "Current department guidance: Warehouse/Logistics\n"
                "- First confirm the Warehouse/Logistics software shape and use case: Finished Lot receipt dashboard, pick/pack/ship tracking, inventory aging, shipping hold, QA/customer release gate, or traceability report. Then clarify FG/WIP inventory, lot traceability, packing/shipping, and customer delivery window.\n"
                "- Strong question example: For the first Warehouse version, who uses this system and for what main job: Finished Lot receipt/inventory aging, shipment tracking, or QA/customer hold release and lot traceability?"
            ),
            "customer": (
                "Current department guidance: Customer/Program/Sales/FAE\n"
                "- First confirm the Customer/Program software shape and use case: customer commit dashboard, forecast/order tracking, complaint/RMA/8D case tracking, program milestone, customer-spec compliance, or response SLA. Then clarify customer lot to internal lot/panel, defect code, and responsible department traceability.\n"
                "- Strong question example: For the first Customer/Program version, is the main job forecast/commit risk, complaint/RMA/8D closure, or customer-spec and response-SLA management?"
            ),
            "finance": (
                "Current department guidance: Finance/Cost\n"
                "- First confirm the Finance/Cost software shape and use case: scrap/rework cost dashboard, loss attribution, cost-center variance, margin impact, month-end reconciliation, or management report export. Then clarify amount definitions, responsibility attribution, product/customer/process dimensions, and month-end lock rules.\n"
                "- Strong question example: For the first Finance version, who uses this system and for what main job: scrap/rework loss dashboard, cost-center attribution, or month-end reconciliation and management report export?"
            ),
            "ehs": (
                "Current department guidance: EHS\n"
                "- First confirm the EHS software shape and use case: incident tracking, corrective-action workflow, chemical usage dashboard, permit/compliance calendar, environmental report, or audit evidence repository. Then clarify incident level, corrective evidence, compliance taxonomy, owners, and closure criteria.\n"
                "- Strong question example: For the first EHS version, is the main job incident/corrective-action closure, chemical/emission compliance dashboard, or compliance/audit report generation?"
            ),
            "it_data": (
                "Current department guidance: IT/Data Governance\n"
                "- First confirm the IT/Data Governance software shape and use case: data-quality dashboard, interface SLA monitor, master-data workflow, lineage/query catalog, access audit, or reconciliation console. Then clarify source of truth, business key, data owner, interface contract, writeback responsibility, and system owner.\n"
                "- Strong question example: For the first IT/Data version, who uses this system and for what main job: interface SLA monitoring, master-data governance, source-of-truth/lineage, or access audit?"
            ),
            "management": (
                "Current department guidance: Management/Ops Excellence\n"
                "- First confirm the Management/Ops Excellence software shape and use case: war-room cockpit, KPI scorecard, target/actual gap review, owner action tracking, escalation board, or meeting-pack export. Then clarify KPI definitions, meeting cadence, owner actions, escalation rules, closure evidence, and sign-off.\n"
                "- Strong question example: For the first Management version, who uses this system and for what main job: operating KPI scorecard, owner-action closure, or war-room escalation and meeting output?"
            ),
        }
        base_guidance = guidance_by_department.get(department, "")
        if node_guidance:
            base_guidance = (node_guidance + ("\n" + base_guidance if base_guidance else "")).strip()
        if base_guidance and playbook_guidance:
            return base_guidance + "\n" + playbook_guidance
        return base_guidance or playbook_guidance

    def _ic_substrate_product_shape_question_guidance(
        self,
        chain_state: dict[str, Any],
        language: str | None = None,
    ) -> str:
        if chain_state.get("mode") != "ic_substrate":
            return ""

        shape = str(chain_state.get("intent_product_shape", "")).strip()
        if not shape:
            return ""

        track = str(chain_state.get("intent_track", "")).strip().lower() or "general"
        track_label = self._ic_substrate_department_label(track, language) if self._ic_substrate_is_department(track) else "General"

        if self._normalize_language(language) == "zh":
            guidance_by_shape = {
                "dashboard": (
                    f"软件形态追问方向：{track_label} dashboard / cockpit\n"
                    "- 优先确认首屏服务的业务决策、核心 KPI、默认维度、刷新频率、下钻路径和谁负责验收；不要先问颜色、卡片数量或图表库。\n"
                    "- 专家问题模板：这个 dashboard 首屏是给谁在什么会议或班次里做什么决策，默认必须看到哪 3 个 KPI，以及点击后要下钻到 lot、panel、station、defect code 还是 owner action？"
                ),
                "workflow_tracker": (
                    f"软件形态追问方向：{track_label} workflow / case tracking\n"
                    "- 优先确认触发条件、对象、状态流转、owner、SLA 起止点、异常升级、关闭证据和重开规则；不要自造状态名或审批层级。\n"
                    "- 专家问题模板：这个 case 从触发到关闭现在实际有哪些状态，每个状态谁负责处理，什么证据可以让系统判定为已关闭或需要升级？"
                ),
                "report_export": (
                    f"软件形态追问方向：{track_label} report / export\n"
                    "- 优先确认报表接收人、使用场景、冻结时间点、指标口径、字段粒度、权限、推送频率和与线上看板的对账关系。\n"
                    "- 专家问题模板：这份报表是给每日/每周例会冻结使用，还是给管理层/客户分享，导出时必须锁定哪个时间窗和哪套 KPI 口径？"
                ),
                "data_query": (
                    f"软件形态追问方向：{track_label} data query / drilldown\n"
                    "- 优先确认查询对象、业务主键、筛选维度、返回粒度、权限边界、保留周期和 source of truth；不要自造表名、字段名或 join key。\n"
                    "- 专家问题模板：用户查询时最常用的业务对象是什么，必须用哪个 key 定位，返回结果要停在汇总层、lot/panel 明细层，还是要继续追到事件/状态历史？"
                ),
                "alerting": (
                    f"软件形态追问方向：{track_label} alerting\n"
                    "- 优先确认触发阈值、判定窗口、去重/抑制规则、通知对象、处置动作、升级路径和关闭证据；不要自造阈值数字或 SLA。\n"
                    "- 专家问题模板：这个告警现在按单个对象触发还是按某个维度累计触发，触发后谁必须在什么业务动作里处理，什么证据才能关闭告警？"
                ),
                "admin_tool": (
                    f"软件形态追问方向：{track_label} admin console / configuration\n"
                    "- 优先确认谁维护配置、配置对象、审批/生效规则、版本审计、回滚方式和误配置影响；不要把它降级成普通 CRUD。\n"
                    "- 专家问题模板：这个配置由谁维护，变更后什么时候生效，是否需要审批和版本留痕，如果配置错误会影响哪个业务流程或指标？"
                ),
            }
            return guidance_by_shape.get(shape, "")

        guidance_by_shape = {
            "dashboard": (
                f"Software-shape guidance: {track_label} dashboard / cockpit\n"
                "- First confirm the decision served by the first screen, core KPIs, default dimensions, refresh cadence, drill path, and acceptance owner before colors, card count, or chart libraries.\n"
                "- Expert question template: Who uses the dashboard in which meeting or shift to make what decision, which 3 KPIs must be visible by default, and should drill-down go to lot, panel, station, defect code, or owner action?"
            ),
            "workflow_tracker": (
                f"Software-shape guidance: {track_label} workflow / case tracking\n"
                "- First confirm trigger, object, state flow, owner, SLA start/end, escalation, closure evidence, and reopen rules. Do not invent state names or approval levels.\n"
                "- Expert question template: What states does the case actually move through today, who owns each state, and what evidence lets the system mark it closed or escalated?"
            ),
            "report_export": (
                f"Software-shape guidance: {track_label} report / export\n"
                "- First confirm recipients, use occasion, freeze time, metric definitions, field grain, permissions, delivery cadence, and reconciliation to the live dashboard.\n"
                "- Expert question template: Is this report frozen for daily/weekly review or shared with leadership/customers, and which time window and KPI definition must be locked at export?"
            ),
            "data_query": (
                f"Software-shape guidance: {track_label} data query / drill-down\n"
                "- First confirm query object, business key, filter dimensions, return grain, access boundary, retention, and source of truth. Do not invent table names, field names, or join keys.\n"
                "- Expert question template: What business object do users search most often, which key identifies it, and should results stop at summary, lot/panel detail, or event/status history?"
            ),
            "alerting": (
                f"Software-shape guidance: {track_label} alerting\n"
                "- First confirm trigger threshold, judgment window, dedupe/suppression rules, notification target, action, escalation path, and closure evidence. Do not invent threshold numbers or SLA.\n"
                "- Expert question template: Does the alert trigger per object or by accumulated threshold over a dimension, who must act, and what evidence closes it?"
            ),
            "admin_tool": (
                f"Software-shape guidance: {track_label} admin console / configuration\n"
                "- First confirm who maintains configuration, configurable object, approval/effective rule, version audit, rollback, and business impact of misconfiguration. Do not reduce it to generic CRUD.\n"
                "- Expert question template: Who maintains this configuration, when does a change become effective, does it need approval/version history, and which workflow or metric is affected if it is wrong?"
            ),
        }
        return guidance_by_shape.get(shape, "")

    def _ic_substrate_intent_focus_question_guidance(
        self,
        chain_state: dict[str, Any],
        language: str | None = None,
    ) -> str:
        if chain_state.get("mode") != "ic_substrate":
            return ""

        focus = str(chain_state.get("intent_focus", "")).strip()
        if not focus:
            return ""

        if self._normalize_language(language) == "zh":
            guidance_by_focus = {
                "metric_definition": (
                    "用户需求形态追问方向：指标口径\n"
                    "- 优先问用户现行指标公式、分子分母、时间窗、数据粒度和排除项；不要先问页面布局，也不要替用户编标准成本/实际成本/OEE/良率等公式选项。\n"
                    "- 好问题示例：这个指标在你们现在的报表里分母和分子分别是什么，统计粒度按 lot、panel、unit 还是 cost center，rework/scrap 是否从口径里单独拆出？"
                ),
                "workflow_state": (
                    "用户需求形态追问方向：流程/状态流转\n"
                    "- 优先问用户现行触发条件、状态机、owner、SLA、审批点和关闭条件；不要先问通用功能清单，也不要自造状态名、角色名或 SLA 数字。\n"
                    "- 好问题示例：这个 case 在你们现行流程里从触发到关闭有哪些状态，每个状态由谁处理，SLA 从哪个节点开始算，什么条件算完成或超时？"
                ),
                "data_integration": (
                    "用户需求形态追问方向：数据源/接口\n"
                    "- 优先问 source of truth、关键字段、join key、刷新频率、数据延迟、回写目标和对账方式；不要自造系统品牌、表名、接口名或主键规则。\n"
                    "- 好问题示例：这条数据链路在你们现有系统里的 source of truth 是哪个，业务主键如何对齐，允许的数据延迟和对账方式是什么？"
                ),
                "alert_exception": (
                    "用户需求形态追问方向：异常/告警\n"
                    "- 优先问用户现行触发阈值、判定窗口、通知对象、处置动作、升级规则和关闭证据；不要自造阈值数值、通知角色或升级层级。\n"
                    "- 好问题示例：这个异常在你们现在是按单笔对象触发，还是按某个业务维度在一段时间内累计触发，触发后必须留下什么关闭证据？"
                ),
                "drilldown_analysis": (
                    "用户需求形态追问方向：下钻/根因分析\n"
                    "- 优先问 drill path、分析维度、保留粒度、关联对象和 root cause 闭环证据。\n"
                    "- 好问题示例：下钻时最关键的路径是 product -> line -> station -> defect code，还是 lot genealogy -> equipment/recipe -> root cause？"
                ),
                "dashboard_view": (
                    "用户需求形态追问方向：看板/图表\n"
                    "- 优先问业务决策场景、核心 KPI、默认维度、刷新频率和首屏排序；不要先问颜色或组件样式。\n"
                    "- 好问题示例：这个看板首屏是给老板看异常排行、良率趋势，还是给工程师看可下钻明细？默认按 product、line、station 还是 customer 排序？"
                ),
                "export_reporting": (
                    "用户需求形态追问方向：导出/报表推送\n"
                    "- 优先问接收人、频率、格式、冻结口径、权限和与线上看板的对账关系。\n"
                    "- 好问题示例：导出的数据是给每日例会冻结使用，还是给客户/管理层分享？导出后是否必须和看板同一时间窗、同一良率口径对账？"
                ),
                "permission_role": (
                    "用户需求形态追问方向：角色/权限\n"
                    "- 只有当权限直接影响当前部门的业务操作边界时才深挖；优先问角色能看什么、改什么、审批什么和谁最终负责。\n"
                    "- 好问题示例：这个部门里哪些角色只能看汇总，哪些角色可以处理异常、审批状态变更或关闭 action item？"
                ),
            }
            return guidance_by_focus.get(focus, "")

        guidance_by_focus = {
            "metric_definition": (
                "User-need focus guidance: metric definition\n"
                "- Ask the user's current metric formula, numerator/denominator, time window, grain, and exclusions before page layout. Do not invent standard-cost, actual-cost, OEE, or yield formula options.\n"
                "- Strong question example: In your current report, what are the numerator and denominator, is the grain lot/panel/unit/cost center, and should rework/scrap be split out?"
            ),
            "workflow_state": (
                "User-need focus guidance: workflow/state flow\n"
                "- Ask the user's current trigger, state machine, owner, SLA, approval point, and closure condition before generic feature lists. Do not invent state names, role names, or SLA numbers.\n"
                "- Strong question example: In your current process, what states does the case move through from trigger to closure, who owns each state, where does SLA start, and what makes it complete or overdue?"
            ),
            "data_integration": (
                "User-need focus guidance: data source/integration\n"
                "- Ask source of truth, key fields, join keys, refresh cadence, latency, writeback target, and reconciliation. Do not invent system brands, table names, API names, or key rules.\n"
                "- Strong question example: In your existing systems, what is the source of truth, how do business keys align, and what latency/reconciliation rule is acceptable?"
            ),
            "alert_exception": (
                "User-need focus guidance: exception/alert\n"
                "- Ask the user's current trigger threshold, judgment window, notification target, action, escalation, and closure evidence. Do not invent threshold numbers, notification roles, or escalation levels.\n"
                "- Strong question example: Does the exception trigger per object or by accumulated threshold over a business dimension/time window, and what closure evidence is required?"
            ),
            "drilldown_analysis": (
                "User-need focus guidance: drill-down/root-cause analysis\n"
                "- Ask drill path, dimensions, retained grain, linked objects, and root-cause closure evidence.\n"
                "- Strong question example: Is the critical path product -> line -> station -> defect code, or lot genealogy -> equipment/recipe -> root cause?"
            ),
            "dashboard_view": (
                "User-need focus guidance: dashboard/chart\n"
                "- Ask decision scenario, core KPI, default dimension, refresh cadence, and first-screen sorting before colors or component style.\n"
                "- Strong question example: Is the first screen for leadership anomaly ranking/yield trend, or for engineers to drill into detail, and should it default by product, line, station, or customer?"
            ),
            "export_reporting": (
                "User-need focus guidance: export/report push\n"
                "- Ask recipients, cadence, format, frozen metric definition, permissions, and reconciliation with the live dashboard.\n"
                "- Strong question example: Is the export for frozen daily review or customer/leadership sharing, and must it reconcile to the dashboard with the same time window and yield definition?"
            ),
            "permission_role": (
                "User-need focus guidance: role/permission\n"
                "- Only dig into permissions when they directly affect the current department's operating boundary; ask what each role can view, change, approve, and ultimately own.\n"
                "- Strong question example: In this department, which roles can only view summaries, and which roles can handle exceptions, approve status changes, or close action items?"
            ),
        }
        return guidance_by_focus.get(focus, "")

    def _conversation_chain_state_for_prompt(self, session: Session, language: str) -> str:
        normalized_language = self._normalize_language(language)
        structured_requirement_model = self._latest_structured_requirement_model_for_prompt(
            session,
            normalized_language,
        )
        if (
            not session.applied_template_id
            and not session.applied_template_name
            and not self._session_matches_ic_substrate_expert_chain(
                session,
                normalized_language,
                structured_requirement_model,
            )
        ):
            return ""

        chain_state = self.build_conversation_chain_state(
            session,
            structured_requirement_model,
            normalized_language,
        )
        if not chain_state.get("enabled"):
            return ""
        focus_question_guidance = self._ic_substrate_intent_focus_question_guidance(
            chain_state,
            normalized_language,
        )
        product_shape_guidance = self._ic_substrate_product_shape_question_guidance(
            chain_state,
            normalized_language,
        )
        node_question_guidance = self._ic_substrate_current_node_question_guidance(
            chain_state,
            normalized_language,
        )
        expert_prd_quality_gate = self._ic_substrate_expert_prd_quality_gate_for_prompt(
            chain_state,
            normalized_language,
        )
        evidence_gap_guidance = self._ic_substrate_missing_evidence_question_guidance(
            session,
            structured_requirement_model,
            normalized_language,
        )
        runtime_guardrails = self._ic_substrate_runtime_guardrails_for_prompt(
            chain_state,
            normalized_language,
        )
        convergence_guidance = self._requirement_convergence_guidance_for_prompt(
            structured_requirement_model,
            normalized_language,
        )
        fast_prd_guidance = self._fast_prd_discovery_guidance_for_prompt(
            session,
            structured_requirement_model,
            normalized_language,
        )

        if normalized_language == "zh":
            state_text = (
                "当前对话链路状态：\n"
                f"- 链路类型：{chain_state.get('mode', '')}\n"
                f"- 当前轨道：{chain_state.get('current_track', '')}\n"
                f"- 当前节点：{chain_state.get('current_node_label', '')}\n"
                f"- 进度：{chain_state.get('current_step_index', 0)}/{chain_state.get('total_steps', 0)}\n"
                f"- 下一问来源：{chain_state.get('next_question_source', '')}\n"
                f"- 用户意图路由：{chain_state.get('intent_track', '') or '未明确'}\n"
                f"- 需求形态路由：{chain_state.get('intent_focus', '') or '未明确'}\n"
                f"- 软件形态路由：{chain_state.get('intent_product_shape', '') or '未明确'}\n"
                "- 回答时优先尊重用户当前意图路由和需求形态路由；当前节点是建议推进点，不是必须照走的固定剧本。如果需求形态和节点指南冲突，优先按用户当前需求形态提问。\n"
                "- 如果需求形态明确但用户没有说清发起部门或业务 owner，先问部门/owner，不要默认套到 Production/TDI/Quality。"
            )
            if focus_question_guidance:
                state_text += "\n" + focus_question_guidance
            if product_shape_guidance:
                state_text += "\n" + product_shape_guidance
            if node_question_guidance:
                state_text += "\n" + node_question_guidance
            if expert_prd_quality_gate:
                state_text += "\n" + expert_prd_quality_gate
            if evidence_gap_guidance:
                state_text += "\n" + evidence_gap_guidance
            if runtime_guardrails:
                state_text += "\n" + runtime_guardrails
            if fast_prd_guidance:
                state_text += "\n" + fast_prd_guidance
            if convergence_guidance:
                state_text += "\n" + convergence_guidance
            return state_text

        if normalized_language == "de":
            state_text = (
                "Aktueller Dialogkettenstatus:\n"
                f"- Kettentyp: {chain_state.get('mode', '')}\n"
                f"- Aktueller Track: {chain_state.get('current_track', '')}\n"
                f"- Aktueller Knoten: {chain_state.get('current_node_label', '')}\n"
                f"- Fortschritt: {chain_state.get('current_step_index', 0)}/{chain_state.get('total_steps', 0)}\n"
                f"- Quelle der naechsten Frage: {chain_state.get('next_question_source', '')}\n"
                f"- Nutzer-Intent-Routing: {chain_state.get('intent_track', '') or 'unklar'}\n"
                f"- Bedarfsform-Routing: {chain_state.get('intent_focus', '') or 'unklar'}\n"
                f"- Softwareform-Routing: {chain_state.get('intent_product_shape', '') or 'unklar'}\n"
                "- Respektiere zuerst den aktuellen Nutzer-Intent und die Bedarfsform. Der aktuelle Knoten ist ein empfohlener naechster Schritt, kein starres Skript. Wenn Bedarfsform und Knotenguide kollidieren, nach der aktuellen Bedarfsform fragen.\n"
                "- Wenn die Bedarfsform klar ist, aber anfordernder Bereich oder Business Owner fehlen, zuerst Bereich/Owner fragen statt default auf Production/TDI/Quality zu setzen."
            )
            if focus_question_guidance:
                state_text += "\n" + focus_question_guidance
            if product_shape_guidance:
                state_text += "\n" + product_shape_guidance
            if node_question_guidance:
                state_text += "\n" + node_question_guidance
            if expert_prd_quality_gate:
                state_text += "\n" + expert_prd_quality_gate
            if evidence_gap_guidance:
                state_text += "\n" + evidence_gap_guidance
            if runtime_guardrails:
                state_text += "\n" + runtime_guardrails
            if fast_prd_guidance:
                state_text += "\n" + fast_prd_guidance
            if convergence_guidance:
                state_text += "\n" + convergence_guidance
            return state_text

        if normalized_language == "ms":
            state_text = (
                "Status rantaian dialog semasa:\n"
                f"- Mod rantaian: {chain_state.get('mode', '')}\n"
                f"- Track semasa: {chain_state.get('current_track', '')}\n"
                f"- Nod semasa: {chain_state.get('current_node_label', '')}\n"
                f"- Kemajuan: {chain_state.get('current_step_index', 0)}/{chain_state.get('total_steps', 0)}\n"
                f"- Sumber soalan seterusnya: {chain_state.get('next_question_source', '')}\n"
                f"- Routing intent pengguna: {chain_state.get('intent_track', '') or 'belum jelas'}\n"
                f"- Routing bentuk keperluan: {chain_state.get('intent_focus', '') or 'belum jelas'}\n"
                f"- Routing bentuk software: {chain_state.get('intent_product_shape', '') or 'belum jelas'}\n"
                "- Utamakan intent pengguna dan bentuk keperluan semasa. Nod semasa ialah cadangan langkah seterusnya, bukan skrip tetap. Jika panduan bentuk keperluan bercanggah dengan panduan nod, tanya mengikut bentuk keperluan semasa.\n"
                "- Jika bentuk keperluan jelas tetapi jabatan pemohon atau business owner belum dikenal pasti, tanya jabatan/owner dahulu dan jangan default kepada Production/TDI/Quality."
            )
            if focus_question_guidance:
                state_text += "\n" + focus_question_guidance
            if product_shape_guidance:
                state_text += "\n" + product_shape_guidance
            if node_question_guidance:
                state_text += "\n" + node_question_guidance
            if expert_prd_quality_gate:
                state_text += "\n" + expert_prd_quality_gate
            if evidence_gap_guidance:
                state_text += "\n" + evidence_gap_guidance
            if runtime_guardrails:
                state_text += "\n" + runtime_guardrails
            if fast_prd_guidance:
                state_text += "\n" + fast_prd_guidance
            if convergence_guidance:
                state_text += "\n" + convergence_guidance
            return state_text

        state_text = (
            "Current conversation chain state:\n"
            f"- Chain mode: {chain_state.get('mode', '')}\n"
            f"- Current track: {chain_state.get('current_track', '')}\n"
            f"- Current node: {chain_state.get('current_node_label', '')}\n"
            f"- Progress: {chain_state.get('current_step_index', 0)}/{chain_state.get('total_steps', 0)}\n"
            f"- Next-question source: {chain_state.get('next_question_source', '')}\n"
            f"- User-intent route: {chain_state.get('intent_track', '') or 'unclear'}\n"
            f"- User-need focus route: {chain_state.get('intent_focus', '') or 'unclear'}\n"
            f"- Software-shape route: {chain_state.get('intent_product_shape', '') or 'unclear'}\n"
            "- Prioritize the user's current intent route and need-focus route. The current node is a suggested next step, not a fixed script. If need-focus guidance conflicts with node guidance, ask according to the user's current need focus.\n"
            "- If the need focus is clear but the user did not identify the requesting department or business owner, ask department/owner first instead of defaulting it to Production/TDI/Quality."
        )
        if focus_question_guidance:
            state_text += "\n" + focus_question_guidance
        if product_shape_guidance:
            state_text += "\n" + product_shape_guidance
        if node_question_guidance:
            state_text += "\n" + node_question_guidance
        if expert_prd_quality_gate:
            state_text += "\n" + expert_prd_quality_gate
        if evidence_gap_guidance:
            state_text += "\n" + evidence_gap_guidance
        if runtime_guardrails:
            state_text += "\n" + runtime_guardrails
        if fast_prd_guidance:
            state_text += "\n" + fast_prd_guidance
        if convergence_guidance:
            state_text += "\n" + convergence_guidance
        return state_text

    def _latest_structured_requirement_model_for_prompt(
        self,
        session: Session,
        language: str,
    ) -> dict[str, Any]:
        normalized_language = self._normalize_language(language)
        message_count = self._message_count(session.messages)
        structured_requirement_model = self._get_latest_cached_structured_requirement_model(
            session.id,
            normalized_language,
            message_count,
        )
        if structured_requirement_model is None:
            structured_requirement_model = self._get_latest_cached_structured_requirement_model(
                session.id,
                STRUCTURED_REQUIREMENT_CANONICAL_CACHE_KEY,
                message_count,
            )
        return structured_requirement_model or self._empty_structured_requirement_model()

    def _pm_methodology_state_for_prompt(self, session: Session, language: str) -> str:
        normalized_language = self._normalize_language(language)
        structured_requirement_model = self._latest_structured_requirement_model_for_prompt(
            session,
            normalized_language,
        )
        progress = self._structured_requirement_progress(structured_requirement_model)
        state = self.build_pm_methodology_state(
            structured_requirement_model,
            normalized_language,
        )
        checks = state.get("checks")
        if not isinstance(checks, list):
            return ""
        actionable_checks = [
            check
            for check in checks
            if isinstance(check, dict)
            and check.get("status") != "ready"
            and (check.get("evidence") or check.get("status") != "missing")
        ]
        if not actionable_checks:
            return ""

        limited_checks = actionable_checks[:3]
        if normalized_language == "zh":
            lines = [
                "PM 方法论状态（advisory，不是生成门禁）：",
                f"- 方法论证据分：{state.get('score', 0)}%",
                f"- 建议优先追问方法：{state.get('recommended_next_method', '') or '无'}",
                "- 当前可作为 PRD 质量备注的方法论缺口：",
            ]
            for check in limited_checks:
                lines.append(
                    f"  - {check.get('method', '')} / {check.get('label', '')}: "
                    f"{check.get('next_question', '')}"
                )
            lines.extend(
                [
                    "- PM Methodology 只作为质量参考和文档增强线索，不得阻断生成文档或 Go Coding。",
                    "- 不要为了提高方法论分数单独追问；下一问必须服从结构化需求 readiness state machine。",
                    "- 当 structured requirement ready_to_generate=true 时，提示生成文档，即使 PM Methodology 分数未 ready。",
                ]
            )
            return "\n".join(lines)

        lines = [
            "PM methodology state (advisory, not a generation gate):",
            f"- Method evidence score: {state.get('score', 0)}%",
            f"- Recommended next method: {state.get('recommended_next_method', '') or 'none'}",
            "- Current PM methodology gaps for PRD quality notes:",
        ]
        for check in limited_checks:
            lines.append(
                f"  - {check.get('method', '')} / {check.get('label', '')}: "
                f"{check.get('next_question', '')}"
            )
        lines.extend(
            [
                "- PM Methodology is advisory and must not block document generation or Go Coding.",
                "- Do not ask separate questions just to lift the methodology score; the next question must follow the structured requirement readiness state machine.",
                "- When structured requirement ready_to_generate=true, tell the user to generate documents even if PM Methodology is not ready.",
            ]
        )
        if progress.get("ready_to_generate"):
            lines.append(
                "- Structured requirements are ready now, so do not open new methodology clarification questions unless the user adds new scope."
            )
        return "\n".join(lines)

    def _requirement_convergence_guidance_for_prompt(
        self,
        structured_requirement_model: dict[str, Any],
        language: str,
    ) -> str:
        progress = self._structured_requirement_progress(structured_requirement_model)
        total_count = self._safe_int(progress.get("total_count"))
        collected_count = self._safe_int(progress.get("collected_count"))
        confirmed_count = self._safe_int(progress.get("confirmed_count"))
        conflict_count = self._safe_int(progress.get("conflict_count"))
        if total_count <= 0:
            return ""
        if conflict_count > 0:
            if language == "zh":
                return "收口规则：当前存在冲突项。下一轮优先澄清冲突，不要继续开新问题。"
            if language == "de":
                return "Konvergenzregel: Es gibt Konflikte. Klaere als Naechstes den Konflikt, statt neue Themen zu oeffnen."
            if language == "ms":
                return "Peraturan penutupan: Terdapat konflik. Utamakan penjelasan konflik sebelum membuka soalan baharu."
            return "Convergence rule: There are conflicting items. Clarify the conflict next instead of opening a new topic."
        if collected_count >= total_count and confirmed_count < total_count:
            if language == "zh":
                return (
                    "收口规则：需求信息已经收集完整但尚未全部确认。下一轮不要继续挖新细节；"
                    "请用简短方式总结待确认项，并只问用户是否确认或要修改其中一个点。"
                )
            if language == "de":
                return (
                    "Konvergenzregel: Die Anforderungsinformationen sind gesammelt, aber noch nicht voll bestaetigt. "
                    "Frage nicht nach neuen Details; fasse die offenen Bestaetigungen kurz zusammen und frage nur, ob sie bestaetigt oder ein Punkt geaendert werden soll."
                )
            if language == "ms":
                return (
                    "Peraturan penutupan: Maklumat keperluan sudah lengkap dikumpulkan tetapi belum disahkan sepenuhnya. "
                    "Jangan gali butiran baharu; ringkaskan item yang perlu disahkan dan tanya sama ada pengguna mengesahkan atau mahu mengubah satu perkara."
                )
            return (
                "Convergence rule: Requirement information is fully collected but not fully confirmed. "
                "Do not ask for new detail; briefly summarize the pending confirmations and ask only whether the user confirms or wants to change one point."
            )
        if confirmed_count >= total_count:
            if language == "zh":
                return "收口规则：需求已全部确认。下一轮应提示可以生成文档，除非用户主动补充新范围。"
            if language == "de":
                return "Konvergenzregel: Alle Anforderungen sind bestaetigt. Weise als Naechstes auf die Dokumenterstellung hin, ausser der Nutzer erweitert den Umfang."
            if language == "ms":
                return "Peraturan penutupan: Semua keperluan telah disahkan. Seterusnya cadangkan penjanaan dokumen kecuali pengguna menambah skop baharu."
            return "Convergence rule: All requirements are confirmed. Suggest generating documents next unless the user adds new scope."
        return ""

    def _fast_prd_discovery_guidance_for_prompt(
        self,
        session: Session,
        structured_requirement_model: dict[str, Any],
        language: str,
    ) -> str:
        """Keep discovery concise while gating Go Coding on structured readiness."""
        if session.start_function == START_FUNCTION_IMPROVE_DRAFT:
            return ""

        progress = self._structured_requirement_progress(structured_requirement_model)
        coverage = self._safe_int(progress.get("collection_coverage_percentage"))
        confirmed = self._safe_int(progress.get("confirmed_count"))
        total = self._safe_int(progress.get("total_count"))
        conflicts = self._safe_int(progress.get("conflict_count"))
        _, pm_methodology_state = self._pm_methodology_ready_for_generation(
            structured_requirement_model,
            language,
        )
        if progress.get("fully_confirmed"):
            return ""
        methodology_score = self._safe_int(pm_methodology_state.get("score"))
        methodology_missing = len(pm_methodology_state.get("missing_evidence", []))

        if language == "zh":
            return (
                "Go Coding readiness discovery：目标是用专家链路收集足够需求信息，而不是提前产出半成品文档。\n"
                "- 从零开始时，不要只反问。每次回复先给 2-3 个短句：已理解、推荐理解、当前最大缺口。\n"
                "- response budget：正文最多 5 lines；每轮只问 1 个最高杠杆问题，不要输出长段落、完整 PRD 或多题清单。\n"
                "- 不要承诺用户现在可以打开 Go Coding；只有 structured requirement ready_to_generate=true 时，才提示生成文档。Go Coding 只能在文档生成/确认 OK 后，把文档交接给 Vibe Coding 平台。PM Methodology 只作质量参考，不阻断生成。\n"
                "- 未确认信息可作为待确认假设辅助追问，但不得当成事实，也不得作为绕过 readiness 的理由。\n"
                "- 如果结构化 gate 已经 ready，不要继续开新问题；收口为确认并生成文档，不要提供跳过文档直接 Go Coding 的选项。\n"
                f"- 当前结构化覆盖率 {coverage}%，已确认 {confirmed}/{total}，conflict_count={conflicts}，PM Methodology {methodology_score}% / gaps={methodology_missing}（仅 advisory）。如果结构化 gate 未 ready，只问最阻塞文档质量的一个结构化缺口。"
            )
        if language == "de":
            return (
                "Go Coding readiness discovery: Nutze die Expertenkette, um genug Requirements zu sammeln, nicht um ein fruehes Teildokument zu erzwingen.\n"
                "- Beim Start from scratch nicht nur Rueckfragen stellen. Jede Antwort nennt kurz: verstanden, empfohlene Interpretation, groesste Luecke.\n"
                "- response budget: maximal 5 lines; pro Runde genau 1 high-leverage Frage, keine langen Abschnitte, kein vollstaendiges PRD, keine Frage-Liste.\n"
                "- Versprich Go Coding nicht als direkten Coding-Start. Bei structured requirement ready_to_generate=true zuerst Dokumente erzeugen; Go Coding uebergibt erst nach erzeugtem/geprueftem Dokument an Vibe Coding. PM Methodology ist nur advisory.\n"
                "- Annahmen helfen beim Nachfragen, sind aber nie bestaetigte Fakten und duerfen readiness nicht umgehen.\n"
                "- Wenn das strukturierte Gate ready ist, keine neue Discovery starten; auf Bestaetigung und Dokumenterzeugung konvergieren, ohne Dokument-Skip-Option.\n"
                f"- Aktuelle Abdeckung {coverage}%, bestaetigt {confirmed}/{total}, conflict_count={conflicts}, PM Methodology {methodology_score}% / gaps={methodology_missing} (nur advisory). Wenn das strukturierte Gate nicht ready ist, frage nur die eine groesste strukturierte Qualitaetsluecke."
            )
        if language == "ms":
            return (
                "Go Coding readiness discovery: gunakan expert chain untuk kumpul maklumat cukup, bukan memaksa dokumen separuh siap.\n"
                "- Untuk start from scratch, jangan hanya bertanya. Setiap jawapan ringkaskan: difahami, tafsiran dicadang, gap terbesar.\n"
                "- response budget: maksimum 5 lines; setiap pusingan hanya 1 soalan high-leverage, tiada perenggan panjang, PRD penuh atau senarai soalan.\n"
                "- Jangan janji Go Coding sebagai mula coding langsung. Jika structured requirement ready_to_generate=true, jana dokumen dahulu; Go Coding hanya handoff dokumen yang sudah dijana/OK ke Vibe Coding. PM Methodology hanya advisory.\n"
                "- Andaian boleh bantu discovery tetapi bukan fakta sah dan tidak boleh memintas readiness.\n"
                "- Jika structured gate ready, jangan buka discovery baharu; tutup kepada pengesahan dan penjanaan dokumen, tanpa pilihan skip dokumen.\n"
                f"- Liputan semasa {coverage}%, disahkan {confirmed}/{total}, conflict_count={conflicts}, PM Methodology {methodology_score}% / gaps={methodology_missing} (advisory sahaja). Jika structured gate belum ready, tanya satu gap kualiti berstruktur paling penting sahaja."
            )
        return (
            "Go Coding readiness discovery: use the expert chain to collect enough requirements, not to force an early partial document.\n"
            "- For start from scratch, do not only ask back. Each reply briefly states: understood, recommended interpretation, biggest gap.\n"
            "- response budget: keep the main reply within 5 lines; ask exactly 1 high-leverage question per round. Do not write long paragraphs, a full PRD, or a list of questions.\n"
            "- Do not present Go Coding as a direct coding start. When structured requirement ready_to_generate=true, suggest generating documents first; Go Coding only hands the generated/approved document package to Vibe Coding. PM Methodology is advisory only.\n"
            "- Assumptions may guide discovery, but they are not confirmed facts and must not bypass readiness.\n"
            "- If the structured gate is ready, stop opening new discovery and converge on confirmation and document generation. Never offer a skip-document path to Go Coding.\n"
            f"- Current collection coverage is {coverage}%, confirmed {confirmed}/{total}, conflict_count={conflicts}, PM Methodology {methodology_score}% / gaps={methodology_missing} (advisory only). If the structured gate is not ready, ask only the single largest structured quality gap."
        )

    def _skill_style_ai_pm_method_prompt(self, language: str | None = None) -> str:
        normalized_language = self._normalize_language(language)
        if normalized_language == "zh":
            return (
                "AI PM skill-style 工作法：\n"
                "- 这套工作法借鉴 agent skill 的小而清晰原则：先对齐 mental model，再产出文档；不要把它写给用户看成方法论说明。\n"
                "- 像专业访谈 skill 一样推进：沿需求决策树逐支拆解，先解决会改变产品边界的依赖问题，再问局部细节。\n"
                "- 每一轮只问一个问题；如果一个问题可由当前对话、附件、模板或结构化模型推断，就不要再问用户。\n"
                "- 每个问题必须带一个可快速确认的推荐答案或选项示例，例如：'我建议首版先按 lot 粒度，因为它最接近现有追溯和责任边界；是否按这个口径？'\n"
                "- 面向指令遵循较弱的内网模型时，最后一段必须使用 A/B/C 选项格式：A. 同意建议口径；B. 补充实际口径；C. 暂记待确认。不要只留下开放式问题。\n"
                "- 推荐答案必须明确标记为建议或假设，不得伪装成已确认事实；如果用户不同意，以用户口径为准。\n"
                "- 建立共享领域语言：持续识别关键名词、状态、KPI、对象和 owner；发现同词异义、同义词或模糊词时，立即用一个问题澄清 canonical term。\n"
                "- 对 IC Substrate，优先统一部门、业务对象、粒度、状态、指标口径、数据源、验收 owner；不要自造现场术语、状态名、公式、系统名或 SLA。\n"
                "- 当用户给出业务术语时，把它沉淀为后续 PRD 的 glossary/definition；当术语未确认时，写成 open question 或 assumption。\n"
                "- 追问必须服务 PRD 质量门：problem、business goal、requesting department、primary user、core scenario、decision/action、data source、business rule、workflow state、acceptance criteria、out-of-scope。\n"
                "- 只有结构化需求 gate ready 时，才允许提示生成文档；PM Methodology 只作质量参考，不阻断生成。\n"
                "- 如果还缺信息，只问那个最阻塞 PRD 可交付质量的缺口，并说明为什么它影响文档质量。"
            )
        if normalized_language == "de":
            return (
                "AI-PM Skill-Style Arbeitsweise:\n"
                "- Nutze kleine, klare Skill-Prinzipien: zuerst gemeinsames Mental Model, dann Dokument. Erklaere diese Methode dem Nutzer nicht als Theorie.\n"
                "- Arbeite entlang des Requirement-Decision-Trees; klaere zuerst Abhaengigkeiten, die Produktgrenzen veraendern, dann Details.\n"
                "- Pro Runde genau eine Frage. Wenn die Antwort aus Konversation, Anhang, Template oder strukturiertem Modell ableitbar ist, frage den Nutzer nicht erneut.\n"
                "- Jede Frage enthaelt eine empfohlene Antwort oder konkrete Optionen, damit der Nutzer schnell bestaetigen kann.\n"
                "- Fuer intern gehostete Modelle mit schwaecherer Instruktionsbefolgung muss der letzte Absatz A/B/C-Optionen enthalten: A. Empfehlung bestaetigen; B. echte Fachdefinition ergaenzen; C. als offen markieren. Keine rein offene Frage am Ende.\n"
                "- Empfehlungen muessen als Empfehlung oder Annahme markiert sein, nie als bestaetigte Tatsache. Nutzerdefinitionen haben Vorrang.\n"
                "- Baue eine gemeinsame Fachsprache auf: erkenne Begriffe, Status, KPIs, Objekte und Owner; bei Mehrdeutigkeit sofort mit einer Frage den canonical term klaeren.\n"
                "- Fuer IC Substrate zuerst Bereich, Business Object, Grain, Status, KPI-Definition, Datenquelle und Acceptance Owner vereinheitlichen; keine Site-Begriffe, Status, Formeln, Systeme oder SLA erfinden.\n"
                "- Nutzerbegriffe als spaetere PRD Glossary/Definition sichern; unbestaetigte Begriffe als Open Question oder Assumption markieren.\n"
                "- Fragen dienen dem PRD Quality Gate: Problem, Business Goal, Requesting Department, Primary User, Core Scenario, Decision/Action, Data Source, Business Rule, Workflow State, Acceptance Criteria, Out-of-Scope.\n"
                "- Wenn diese Bloecke dokumentreif sind, keine neuen Themen oeffnen; mit einer Bestaetigungsfrage abschliessen und Dokumentgenerierung vorschlagen."
            )
        if normalized_language == "ms":
            return (
                "Kaedah kerja AI PM gaya skill:\n"
                "- Ikut prinsip skill yang kecil dan jelas: selaraskan mental model dahulu, kemudian hasilkan dokumen. Jangan terangkan kaedah ini sebagai teori kepada pengguna.\n"
                "- Gerakkan temu bual mengikut requirement decision tree; selesaikan dependency yang mengubah boundary produk dahulu, kemudian butiran kecil.\n"
                "- Tanya tepat satu soalan setiap pusingan. Jika jawapan boleh disimpulkan daripada perbualan, lampiran, templat atau structured model, jangan tanya semula.\n"
                "- Setiap soalan mesti ada jawapan cadangan atau pilihan contoh supaya pengguna boleh sahkan dengan cepat.\n"
                "- Untuk model dalaman yang kurang patuh arahan, perenggan akhir mesti guna pilihan A/B/C: A. sahkan cadangan; B. tambah definisi sebenar; C. simpan sebagai belum disahkan. Jangan akhiri dengan soalan terbuka sahaja.\n"
                "- Cadangan mesti dilabel sebagai cadangan atau assumption, bukan fakta sah. Definisi pengguna sentiasa mengatasi cadangan.\n"
                "- Bina shared domain language: kenal pasti term, status, KPI, objek dan owner; jika istilah kabur atau overloaded, tanya satu soalan untuk canonical term.\n"
                "- Untuk IC Substrate, utamakan penyelarasan department, business object, grain, status, KPI definition, data source dan acceptance owner; jangan reka site term, status, formula, system name atau SLA.\n"
                "- Simpan istilah pengguna sebagai glossary/definition untuk PRD; istilah belum sah masuk sebagai open question atau assumption.\n"
                "- Soalan mesti menyokong PRD quality gate: problem, business goal, requesting department, primary user, core scenario, decision/action, data source, business rule, workflow state, acceptance criteria, out-of-scope.\n"
                "- Jika blok ini sudah cukup untuk dokumen, jangan buka topik baharu; tutup dengan soalan pengesahan dan cadangkan penjanaan dokumen."
            )
        return (
            "AI PM skill-style operating method:\n"
            "- Use small, sharp skill principles: align the mental model first, then produce the document. Do not explain this method to the user as theory.\n"
            "- Interview along the requirement decision tree; resolve dependencies that change product boundaries before local details.\n"
            "- Ask exactly one question per turn. If the answer can be inferred from conversation, attachment, template, or structured model, do not ask the user again.\n"
            "- Every question must include a recommended answer or concrete options so the user can confirm quickly.\n"
            "- For internally hosted models with weaker instruction following, the final paragraph must use plain A/B/C options: A. use a practical v1 assumption and continue; B. provide exact wording or an exception; C. leave it pending. Do not end with only an open-ended question.\n"
            "- Mark recommendations as suggestions or assumptions, never as confirmed facts. The user's definition wins.\n"
            "- Build shared domain language: identify terms, states, KPIs, objects, and owners; when a term is ambiguous, overloaded, or conflicting, ask one question to establish the canonical term.\n"
            "- For IC Substrate, prioritize department, business object, grain, state, KPI definition, data source, and acceptance owner; do not invent site terms, states, formulas, system names, or SLAs.\n"
            "- Preserve user-provided terms as later PRD glossary/definitions; keep unconfirmed terms as open questions or assumptions.\n"
            "- Questions must serve the PRD quality gate: problem, business goal, requesting department, primary user, core scenario, decision/action, data source, business rule, workflow state, acceptance criteria, out-of-scope.\n"
            "- If these blocks are document-ready, stop opening new topics; ask a confirmation question and suggest document generation."
        )

    def _structured_requirement_skill_extraction_guidance(self, language: str | None = None) -> str:
        normalized_language = self._normalize_language(language)
        if normalized_language == "zh":
            return (
                "Skill-style 抽取补充规则：\n"
                "- 从对话中抽取共享领域语言：业务术语、KPI 名称、状态名、对象粒度、owner、数据源、验收口径。\n"
                "- 不新增 schema；把术语定义放入 business_rules、data_and_dependencies、risks_and_notes 或 open_questions 的最贴近位置。\n"
                "- 对推荐答案、假设、待确认术语要保持 pending_confirmation 或 open question，不要升级为 confirmed。\n"
                "- 如果用户确认了 canonical term、公式、状态、owner 或验收标准，要尽量标成 confirmed，并保留用户原话口径。\n"
                "- 看板/指标/KPI 类需求的硬门禁：数据源字段（integrations / data_and_dependencies）和 KPI 公式字段（rules / business_rules）在拿到具体数据接口（来源系统 + 视图/API + 主键字段 + 刷新）且每个指标公式（分子/分母、时间窗、排除项）明确、或用户明确接受某条假设之前，最多 pending_confirmation；含糊的“从 MES 取”不算 confirmed。"
            )
        if normalized_language == "de":
            return (
                "Skill-Style Extraktionsregeln:\n"
                "- Extrahiere gemeinsame Fachsprache: Business Terms, KPI-Namen, State Names, Object Grain, Owner, Datenquellen und Acceptance Definitions.\n"
                "- Schema nicht erweitern; Termdefinitionen in business_rules, data_and_dependencies, risks_and_notes oder open_questions ablegen.\n"
                "- Empfehlungen, Annahmen und unbestaetigte Begriffe bleiben pending_confirmation oder open question, nicht confirmed.\n"
                "- Wenn der Nutzer canonical term, Formel, State, Owner oder Acceptance bestaetigt, als confirmed erfassen und Nutzerwortlaut bewahren.\n"
                "- Hard gate for dashboard/metric/KPI requirements: keep the data-source area (integrations / data_and_dependencies) and the KPI-formula area (rules / business_rules) at most pending_confirmation until the concrete data interface (source system + view/API + key fields + refresh) AND each metric's formula (numerator/denominator, time window, exclusions) are captured, OR the user explicitly accepted a stated assumption. A vague 'from MES' is not confirmed."
            )
        if normalized_language == "ms":
            return (
                "Peraturan ekstraksi gaya skill:\n"
                "- Ekstrak shared domain language: business terms, KPI names, state names, object grain, owner, data sources dan acceptance definitions.\n"
                "- Jangan tambah schema; letakkan definisi term di business_rules, data_and_dependencies, risks_and_notes atau open_questions yang paling sesuai.\n"
                "- Recommended answers, assumptions dan unconfirmed terms kekal pending_confirmation atau open question, bukan confirmed.\n"
                "- Jika pengguna sahkan canonical term, formula, state, owner atau acceptance criteria, tandakan sebagai confirmed dan kekalkan wording pengguna.\n"
                "- Gerbang keras untuk requirement dashboard/metric/KPI: kekalkan area data-source (integrations / data_and_dependencies) dan area formula KPI (rules / business_rules) paling tinggi pending_confirmation sehingga antara muka data konkrit (sistem sumber + view/API + key fields + refresh) DAN formula setiap metrik (numerator/denominator, time window, exclusions) ditangkap, ATAU pengguna terima andaian yang dinyatakan. Jawapan kabur 'dari MES' bukan confirmed."
            )
        return (
            "Skill-style extraction rules:\n"
            "- Extract shared domain language: business terms, KPI names, state names, object grain, owners, data sources, and acceptance definitions.\n"
            "- Do not add schema; place term definitions in the closest existing areas such as business_rules, data_and_dependencies, risks_and_notes, or open_questions.\n"
            "- Keep recommended answers, assumptions, and unconfirmed terms as pending_confirmation or open questions, not confirmed facts.\n"
            "- When the user confirms a canonical term, formula, state, owner, or acceptance standard, mark the closest requirement area confirmed and preserve the user's wording.\n"
            "- HARD GATE for dashboard/metric/KPI requirements: keep the data-source area (integrations / data_and_dependencies) and the KPI-formula area (rules / business_rules) at most pending_confirmation until the concrete data interface (source system + view/API + key fields + refresh) AND each metric's formula (numerator/denominator, time window, exclusions) are captured, OR the user explicitly accepted a stated assumption. A vague 'from MES' is not confirmed."
        )

    def _ic_substrate_structured_extraction_contract(
        self,
        session: Session,
        language: str | None = None,
    ) -> str:
        template = self._resolve_business_template(session, language)
        template_context = template or {
            "template_id": session.applied_template_id,
            "template_name": session.applied_template_name,
        }
        if not self._template_matches_ic_substrate_focus(template_context):
            return ""

        normalized_language = self._normalize_language(language)
        if normalized_language == "zh":
            return (
                "IC Substrate 结构化抽取合同：\n"
                "- 不新增 JSON schema；把专家访谈证据映射到现有字段，并保留用户原话口径。\n"
                "- product_context：抽取 requesting_department 只能是 Production、Quality、TDI 或 General；business_owner、software_type、primary_user、decision_or_action、acceptance_owner 必须来自用户确认或标为待确认。\n"
                "- functional_requirements.feature_details：每个 feature 都要尽量写清 trigger、processing_logic、inputs、outputs、exception_cases；围绕 lot/panel/unit/case/page/action 的业务动作，不写泛泛页面功能。\n"
                "- business_rules：存放 KPI/公式、状态定义、缺陷分类、放行/关闭规则、SLA 起止点、权限/owner 规则；未确认公式或状态必须写成 draft assumption 或 open question。\n"
                "- data_and_dependencies：存放 source of truth、对象粒度、字段来源、刷新频率、对账逻辑、历史数据迁移、接口边界；不要自造 MES/QMS/ERP/SAP 表名。\n"
                "- acceptance_criteria：存放可验收证据，包括主流程、异常流程、数据准确性、导出/下载、跨部门 sign-off、证据留存和关闭条件。\n"
                "- collection_status：只有用户明确确认的字段才能 confirmed；从模板、AI 推荐或附件推断出的内容最多 pending_confirmation；矛盾内容标 conflict，关键缺口保留 pending_questions。\n"
                "- 生成硬门禁：`integrations`（数据接口）在拿到具体 source-of-truth（来源系统 + 视图/API + 主键/字段 + 刷新频率）或用户明确接受某条假设之前最多 pending_confirmation、不能 confirmed；`rules`（KPI 公式）在每个指标都有具体公式（分子/分母、时间窗、排除项）或明确假设之前不能 confirmed。“从 MES 取”这类含糊回答只能 pending_confirmation。被接受的假设写进 open_questions/business_rules 并标注“ASSUMPTION: …”。"
            )
        if normalized_language == "de":
            return (
                "IC Substrate structured extraction contract:\n"
                "- Do not add JSON schema. Map expert interview evidence into existing fields and preserve the user's wording.\n"
                "- product_context: requesting_department must be Production, Quality, TDI, or General; business_owner, software_type, primary_user, decision_or_action, and acceptance_owner need user confirmation or remain pending.\n"
                "- functional_requirements.feature_details: capture trigger, processing_logic, inputs, outputs, and exception_cases for each feature around lot/panel/unit/case/page/action business actions, not generic page features.\n"
                "- business_rules: store KPI/formula, state definition, defect taxonomy, release/closure rule, SLA start-end, permission/owner rule; unconfirmed formulas or states are draft assumptions or open questions.\n"
                "- data_and_dependencies: store source of truth, object grain, field source, refresh frequency, reconciliation logic, historical migration, and interface boundary. Do not invent MES/QMS/ERP/SAP table names.\n"
                "- acceptance_criteria: store verifiable evidence for main flow, exception flow, data accuracy, export/download, cross-functional sign-off, evidence retention, and closure condition.\n"
                "- collection_status: mark confirmed only when the user explicitly confirms it; template evidence, AI recommendations, or attachment inference are at most pending_confirmation; contradictions are conflict and key gaps keep pending_questions.\n"
                "- GENERATION HARD GATE: keep `integrations` (data interface) at most pending_confirmation until a concrete source-of-truth is captured (source system + view/API + key fields + refresh cadence) OR the user explicitly accepts a stated assumption; keep `rules` (KPI formulas) unconfirmed until every metric has a concrete formula (numerator/denominator, time window, exclusions) OR an explicit assumption. Vague answers like 'from MES' stay pending_confirmation. Record accepted assumptions in open_questions/business_rules as 'ASSUMPTION: ...'."
            )
        if normalized_language == "ms":
            return (
                "Kontrak ekstraksi berstruktur IC Substrate:\n"
                "- Jangan tambah JSON schema. Petakan bukti interview pakar ke field sedia ada dan kekalkan wording pengguna.\n"
                "- product_context: requesting_department mesti Production, Quality, TDI atau General; business_owner, software_type, primary_user, decision_or_action dan acceptance_owner mesti disahkan pengguna atau kekal pending.\n"
                "- functional_requirements.feature_details: untuk setiap feature, tangkap trigger, processing_logic, inputs, outputs dan exception_cases sekitar business action lot/panel/unit/case/page/action, bukan fungsi halaman umum.\n"
                "- business_rules: simpan KPI/formula, state definition, defect taxonomy, release/closure rule, SLA start-end, permission/owner rule; formula atau state belum sah ialah draft assumption atau open question.\n"
                "- data_and_dependencies: simpan source of truth, object grain, field source, refresh frequency, reconciliation logic, historical migration dan interface boundary. Jangan reka nama table MES/QMS/ERP/SAP.\n"
                "- acceptance_criteria: simpan evidence yang boleh diverifikasi untuk main flow, exception flow, data accuracy, export/download, cross-functional sign-off, evidence retention dan closure condition.\n"
                "- collection_status: confirmed hanya jika pengguna sahkan dengan jelas; template evidence, AI recommendation atau attachment inference paling tinggi pending_confirmation; contradiction ialah conflict dan key gaps kekalkan pending_questions.\n"
                "- GERBANG KERAS PENJANAAN: kekalkan `integrations` (antara muka data) paling tinggi pending_confirmation sehingga source-of-truth konkrit ditangkap (sistem sumber + view/API + key fields + refresh cadence) ATAU pengguna terima andaian yang dinyatakan; kekalkan `rules` (formula KPI) belum confirmed sehingga setiap metrik ada formula konkrit (numerator/denominator, time window, exclusions) ATAU andaian eksplisit. Jawapan kabur seperti 'dari MES' kekal pending_confirmation. Rekod andaian diterima dalam open_questions/business_rules sebagai 'ASSUMPTION: ...'."
            )
        return (
            "IC Substrate structured extraction contract:\n"
            "- Do not add JSON schema. Map expert interview evidence into existing fields and preserve the user's wording.\n"
            "- product_context: requesting_department must be Production, Quality, TDI, or General; business_owner, software_type, primary_user, decision_or_action, and acceptance_owner need user confirmation or remain pending.\n"
            "- functional_requirements.feature_details: capture trigger, processing_logic, inputs, outputs, and exception_cases for each feature around lot/panel/unit/case/page/action business actions, not generic page features.\n"
            "- business_rules: store KPI/formula, state definition, defect taxonomy, release/closure rule, SLA start-end, permission/owner rule; unconfirmed formulas or states are draft assumptions or open questions.\n"
            "- data_and_dependencies: store source of truth, object grain, field source, refresh frequency, reconciliation logic, historical migration, and interface boundary. Do not invent MES/QMS/ERP/SAP table names.\n"
            "- acceptance_criteria: store verifiable evidence for main flow, exception flow, data accuracy, export/download, cross-functional sign-off, evidence retention, and closure condition.\n"
            "- collection_status: mark confirmed only when the user explicitly confirms it; template evidence, AI recommendations, or attachment inference are at most pending_confirmation; contradictions are conflict and key gaps keep pending_questions.\n"
            "- GENERATION HARD GATE: keep `integrations` (data interface) at most pending_confirmation until a concrete source-of-truth is captured (source system + view/API + key fields + refresh cadence) OR the user explicitly accepts a stated assumption; keep `rules` (KPI formulas) unconfirmed until every metric has a concrete formula (numerator/denominator, time window, exclusions) OR an explicit assumption. Vague answers like 'from MES' stay pending_confirmation. Record accepted assumptions in open_questions/business_rules as 'ASSUMPTION: ...'."
        )

    def _prd_skill_style_document_guidance(self, language: str | None = None) -> str:
        normalized_language = self._normalize_language(language)
        if normalized_language == "zh":
            return (
                "Skill-style PRD 写作规则：\n"
                "- PRD 不是聊天纪要；它要体现经过访谈收敛后的共享语言、产品边界和工程可交付决策。\n"
                "- 在文档前半部分加入简洁的 Glossary / Definitions，列出已确认的业务术语、KPI、状态、对象粒度和 owner；未确认术语进入 Open Questions。\n"
                "- User Stories 必须覆盖真实业务场景，而不是只列页面功能；优先使用“作为某角色，我希望完成某动作，以便达成某业务结果”。\n"
                "- Implementation Decisions 只写产品/接口/数据/流程层面的决策，不写易过期的具体代码文件路径。\n"
                "- Testing / Acceptance 要以外部可观察行为为准，覆盖主流程、异常流程、数据口径、权限/owner 和文档中标注的验收标准。\n"
                "- Out of Scope 要明确写出本版不做什么，特别是未开放部门、未确认公式、未确认系统接口和未确认状态流。"
            )
        if normalized_language == "de":
            return (
                "Skill-Style PRD Regeln:\n"
                "- Das PRD ist kein Chat-Protokoll; es zeigt gemeinsame Sprache, Produktgrenzen und umsetzbare Entscheidungen.\n"
                "- Fuege frueh eine knappe Glossary / Definitions Sektion ein: bestaetigte Begriffe, KPIs, States, Object Grain und Owner; unbestaetigte Begriffe in Open Questions.\n"
                "- User Stories muessen reale Business-Szenarien abdecken, nicht nur Seitenfunktionen.\n"
                "- Implementation Decisions beschreiben Produkt-, Interface-, Daten- und Prozessentscheidungen; keine schnell veraltenden Dateipfade.\n"
                "- Testing / Acceptance prueft extern beobachtbares Verhalten, Hauptfluss, Ausnahmen, Datenlogik, Rollen/Owner und Acceptance Standards.\n"
                "- Out of Scope nennt explizit, was diese Version nicht macht."
            )
        if normalized_language == "ms":
            return (
                "Peraturan PRD gaya skill:\n"
                "- PRD bukan ringkasan chat; ia mesti menunjukkan shared language, product boundary dan keputusan yang boleh dihantar kepada engineering.\n"
                "- Tambah Glossary / Definitions ringkas di bahagian awal: confirmed terms, KPI, states, object grain dan owner; unconfirmed terms masuk Open Questions.\n"
                "- User Stories mesti meliputi senario bisnes sebenar, bukan hanya fungsi halaman.\n"
                "- Implementation Decisions tulis keputusan product/interface/data/process; jangan tulis file path kod yang mudah lapuk.\n"
                "- Testing / Acceptance berdasarkan externally observable behavior, main flow, exception flow, data definitions, roles/owners dan acceptance standards.\n"
                "- Out of Scope nyatakan dengan jelas apa yang tidak dibuat dalam versi ini."
            )
        return (
            "Skill-style PRD writing rules:\n"
            "- The PRD is not a chat transcript; it must show the converged shared language, product boundary, and engineering-ready decisions.\n"
            "- Add a concise Glossary / Definitions section near the top for confirmed business terms, KPIs, states, object grain, and owners; unresolved terms go to Open Questions.\n"
            "- User Stories must cover real business scenarios, not only page features. Prefer: As a role, I want to perform an action, so that a business outcome is achieved.\n"
            "- Implementation Decisions describe product, interface, data, and workflow decisions; do not include fragile code file paths.\n"
            "- Testing / Acceptance should verify externally observable behavior, main flow, exception flow, data definitions, roles/owners, and the documented acceptance standards.\n"
            "- Out of Scope must explicitly state what this version will not do, especially unopened departments, unconfirmed formulas, unconfirmed system integrations, and unconfirmed state flows."
        )

    def _ic_substrate_prd_document_contract(self, session: Session, language: str | None = None) -> str:
        template = self._resolve_business_template(session, language)
        template_context = template or {
            "template_id": session.applied_template_id,
            "template_name": session.applied_template_name,
        }
        if not self._template_matches_ic_substrate_focus(template_context):
            return ""

        normalized_language = self._normalize_language(language)
        if normalized_language == "zh":
            return (
                "IC Substrate URD/PRD 专家文档合同：\n"
                "- 文档必须像资深 IC Substrate 产品经理交付给业务和 IT 的需求包，不是聊天总结。\n"
                "- 前半部分必须包含 Glossary / Definitions：现场确认的业务术语、对象粒度、KPI/公式、状态名、owner、数据源；未确认项进入 Open Questions，不要隐式假设。\n"
                "- Production/TDI/Quality/General 只按用户已确认的入口写，不要展开隐藏部门链路；其他部门诉求归入 General 或 Out of Scope。\n"
                "- Functional Requirements 必须按业务动作组织：谁在什么触发条件下，对哪个 lot/panel/unit/case/page/action 做什么，系统输出什么判断、看板、提醒、导出或回写。\n"
                "- Data & Dependencies 必须写清 source of truth、字段/对象粒度、刷新频率、对账逻辑、历史数据迁移和未确认接口；不要自造 MES/QMS/ERP/SAP 表名。\n"
                "- Business Rules 必须区分已确认规则、draft assumption 和 open question；公式、SLA、状态流、缺陷分类、放行/关闭条件没有用户确认时不能写成事实。\n"
                "- Acceptance Criteria 必须能被业务验收：主流程、异常流程、权限/owner、数据准确性、导出/下载、跨部门签核和证据留存。"
            )
        if normalized_language == "de":
            return (
                "IC Substrate URD/PRD Expert Document Contract:\n"
                "- The document must read like a senior IC Substrate PM handoff to business and IT, not a chat summary.\n"
                "- Include early Glossary / Definitions: confirmed business terms, object grain, KPI/formula, state names, owners, and data sources; unresolved items go to Open Questions.\n"
                "- Write only the confirmed entry track among Production/TDI/Quality/General; keep hidden departments under General or Out of Scope.\n"
                "- Functional Requirements must be organized by business action: who does what, under which trigger, to which lot/panel/unit/case/page/action, and what judgement, dashboard, alert, export, or writeback the system produces.\n"
                "- Data & Dependencies must state source of truth, field/object grain, refresh frequency, reconciliation logic, historical migration, and unconfirmed interfaces. Do not invent MES/QMS/ERP/SAP table names.\n"
                "- Business Rules must separate confirmed rules, draft assumptions, and open questions; unconfirmed formulas, SLAs, state flows, defect taxonomy, release/closure rules are not facts.\n"
                "- Acceptance Criteria must be business-verifiable: main flow, exception flow, role/owner, data accuracy, export/download, cross-functional sign-off, and evidence retention."
            )
        if normalized_language == "ms":
            return (
                "Kontrak dokumen pakar IC Substrate URD/PRD:\n"
                "- Dokumen mesti kelihatan seperti handoff PM IC Substrate senior kepada business dan IT, bukan ringkasan chat.\n"
                "- Sertakan Glossary / Definitions awal: confirmed business terms, object grain, KPI/formula, state names, owners dan data sources; item belum jelas masuk Open Questions.\n"
                "- Tulis hanya entry track Production/TDI/Quality/General yang disahkan pengguna; hidden departments kekal dalam General atau Out of Scope.\n"
                "- Functional Requirements mesti disusun mengikut business action: siapa buat apa, trigger apa, object lot/panel/unit/case/page/action mana, dan system menghasilkan judgement, dashboard, alert, export atau writeback apa.\n"
                "- Data & Dependencies mesti nyatakan source of truth, field/object grain, refresh frequency, reconciliation logic, historical migration dan unconfirmed interfaces. Jangan reka nama table MES/QMS/ERP/SAP.\n"
                "- Business Rules mesti bezakan confirmed rules, draft assumptions dan open questions; formula, SLA, state flow, defect taxonomy, release/closure rules yang belum disahkan bukan fakta.\n"
                "- Acceptance Criteria mesti boleh diverifikasi oleh business: main flow, exception flow, role/owner, data accuracy, export/download, cross-functional sign-off dan evidence retention."
            )
        return (
            "IC Substrate URD/PRD expert document contract:\n"
            "- The document must read like a senior IC Substrate PM handoff to business and IT, not a chat summary.\n"
            "- Include early Glossary / Definitions: confirmed business terms, object grain, KPI/formula, state names, owners, and data sources; unresolved items go to Open Questions.\n"
            "- Write only the confirmed entry track among Production/TDI/Quality/General; keep hidden departments under General or Out of Scope.\n"
            "- Functional Requirements must be organized by business action: who does what, under which trigger, to which lot/panel/unit/case/page/action, and what judgement, dashboard, alert, export, or writeback the system produces.\n"
            "- Data & Dependencies must state source of truth, field/object grain, refresh frequency, reconciliation logic, historical migration, and unconfirmed interfaces. Do not invent MES/QMS/ERP/SAP table names.\n"
            "- Business Rules must separate confirmed rules, draft assumptions, and open questions; unconfirmed formulas, SLAs, state flows, defect taxonomy, release/closure rules are not facts.\n"
            "- Acceptance Criteria must be business-verifiable: main flow, exception flow, role/owner, data accuracy, export/download, cross-functional sign-off, and evidence retention."
        )

    def _ic_substrate_expert_prd_quality_gate_for_prompt(
        self,
        chain_state: dict[str, Any],
        language: str | None = None,
    ) -> str:
        if chain_state.get("mode") != "ic_substrate":
            return ""

        track = str(chain_state.get("intent_track") or chain_state.get("current_track") or "").strip().lower()
        if track not in {"production", "tdi", "quality", "general"}:
            track = "general"

        normalized_language = self._normalize_language(language)
        if normalized_language == "zh":
            track_checks = {
                "production": (
                    "Production 专家追问优先补齐：1) 首版业务动作是排产/派工、WIP hold 处置、Finished Lot 判定、产量节拍监控还是成本/效率复盘；"
                    "2) 对象粒度是 lot/panel/unit/route/station/shift/day 哪一层；"
                    "3) WIP、hold、rework、scrap、release、finished 的现场状态名和责任人；"
                    "4) 数量、时间窗、跨 Production/Quality/Warehouse 的对账和验收证据。"
                ),
                "tdi": (
                    "TDI 专家追问优先补齐：1) 用户现场 TDI 的业务定义和 case 触发边界；"
                    "2) case 分类、优先级、状态机、owner/SLA 起止点；"
                    "3) input/output、handoff、approval、verification、writeback、closure/reopen 规则；"
                    "4) 关闭证据、跨部门签核和历史 case 迁移边界。"
                ),
                "quality": (
                    "Quality 专家追问优先补齐：1) 首版要解决的是 inspection coverage、defect disposition、release gate、MRB/CAPA、root cause 还是质量趋势分析；"
                    "2) defect taxonomy、spec limit、sampling/full inspection、lot genealogy、waiver/deviation 的现场定义；"
                    "3) retest/rework/scrap/release 的判定规则和 owner；"
                    "4) 质量放行、关闭验证、客户/内部签核和证据留存。"
                ),
                "general": (
                    "General 专家追问优先补齐：1) 发起部门/业务 owner；2) 首版软件形态和目标用户；"
                    "3) 这个系统要支撑的业务动作或决策；4) 能进入 URD/PRD 的范围边界、验收证据和明确不做事项。"
                ),
            }
            return (
                "IC Substrate 专家 PM 质量门：\n"
                "- 下一问必须补齐一个可写进 URD/PRD 的字段，而不是泛泛展示行业知识。\n"
                "- 追问优先级：业务动作/决策 -> 目标用户/owner -> 业务对象与粒度 -> KPI/公式/状态定义 -> 流程状态与责任边界 -> 数据来源/对账/刷新频率 -> 验收证据/签核/不做范围。\n"
                f"- 当前轨道校验：{track_checks[track]}\n"
                "- A/B/C 选项只能用于确认路径、口径或待确认事实；不得把未确认的公式、站点、状态、系统名、SLA 或 owner 伪装成事实。\n"
                "- 如果关键字段已足够生成首版文档，不要继续发散追问；转为请用户确认是否生成 URD/PRD。"
            )

        if normalized_language == "de":
            track_checks = {
                "production": (
                    "Production: zuerst klaeren, ob v1 Scheduling/Dispatch, WIP-Hold-Disposition, Finished-Lot-Entscheidung, Output-Rhythmus-Monitoring oder Kosten-/Effizienz-Review stuetzt; danach Objektgranularitaet, Site-State-Namen, Owner, Reconciliation und Acceptance Evidence."
                ),
                "tdi": (
                    "TDI: zuerst die TDI-Definition des Nutzers und die Case-Trigger-Grenze bestaetigen; danach Case-Klasse, Prioritaet, State Machine, Owner/SLA-Start-Ende, Handoff, Approval, Verification, Writeback, Closure/Reopen und Evidence."
                ),
                "quality": (
                    "Quality: zuerst klaeren, ob v1 Inspection Coverage, Defect Disposition, Release Gate, MRB/CAPA, Root Cause oder Quality Trend Analysis abdeckt; danach Taxonomy, Spec/Sampling, Disposition Owner, Release Evidence und Sign-off."
                ),
                "general": (
                    "General: zuerst anfordernden Bereich/Business Owner, v1-Softwareform, Zielnutzer, Business Decision/Action, Scope Boundary, Acceptance Evidence und explizite Out-of-Scope-Punkte klaeren."
                ),
            }
            return (
                "IC Substrate Expert-PM-Quality-Gate:\n"
                "- Die naechste Frage muss ein URD/PRD-faehiges Feld fuellen, nicht nur Domainwissen zeigen.\n"
                "- Prioritaet: Business Action/Decision -> User/Owner -> Business Object and Grain -> KPI/Formula/State Definition -> Workflow and Ownership Boundary -> Data Source/Reconciliation/Refresh -> Acceptance Evidence/Sign-off/Out-of-Scope.\n"
                f"- Aktueller Track-Check: {track_checks[track]}\n"
                "- A/B/C-Optionen duerfen nur Pfade, Definitionen oder Unbekanntes bestaetigen. Keine unbestaetigten Formeln, Stationen, States, Systeme, SLAs oder Owner als Fakten darstellen.\n"
                "- Wenn die Schluesselfelder fuer ein erstes Dokument reichen, nicht weiter ausweiten; den Nutzer um Bestaetigung zur URD/PRD-Generierung bitten."
            )

        if normalized_language == "ms":
            track_checks = {
                "production": (
                    "Production: sahkan dahulu sama ada v1 menyokong scheduling/dispatch, WIP hold disposition, Finished Lot decision, output rhythm monitoring atau cost/efficiency review; kemudian object grain, nama state di site, owner, reconciliation dan acceptance evidence."
                ),
                "tdi": (
                    "TDI: sahkan dahulu definisi TDI pengguna dan trigger boundary case; kemudian case class, priority, state machine, owner/SLA start-end, handoff, approval, verification, writeback, closure/reopen dan evidence."
                ),
                "quality": (
                    "Quality: sahkan dahulu sama ada v1 meliputi inspection coverage, defect disposition, release gate, MRB/CAPA, root cause atau quality trend analysis; kemudian taxonomy, spec/sampling, disposition owner, release evidence dan sign-off."
                ),
                "general": (
                    "General: kenal pasti requesting department/business owner, first-version software shape, target user, business decision/action, scope boundary, acceptance evidence dan explicit out-of-scope items."
                ),
            }
            return (
                "IC Substrate Expert PM quality gate:\n"
                "- Soalan seterusnya mesti melengkapkan satu field yang sedia masuk URD/PRD, bukan sekadar menunjukkan pengetahuan domain.\n"
                "- Keutamaan: business action/decision -> user/owner -> business object and grain -> KPI/formula/state definition -> workflow and ownership boundary -> data source/reconciliation/refresh -> acceptance evidence/sign-off/out-of-scope.\n"
                f"- Semakan track semasa: {track_checks[track]}\n"
                "- Pilihan A/B/C hanya untuk mengesahkan path, definition atau unknowns. Jangan jadikan formula, station, state, system, SLA atau owner yang belum disahkan sebagai fakta.\n"
                "- Jika key fields sudah cukup untuk first document, berhenti mengembangkan soalan dan minta pengguna sahkan penjanaan URD/PRD."
            )

        track_checks = {
            "production": (
                "Production expert check: first clarify whether v1 supports scheduling/dispatch, WIP hold disposition, Finished Lot decision, output rhythm monitoring, or cost/efficiency review; then object grain, site state names, owners, reconciliation, and acceptance evidence."
            ),
            "tdi": (
                "TDI expert check: first confirm the user's TDI definition and case trigger boundary; then case class, priority, state machine, owner/SLA start-end, handoff, approval, verification, writeback, closure/reopen, and evidence."
            ),
            "quality": (
                "Quality expert check: first clarify whether v1 covers inspection coverage, defect disposition, release gate, MRB/CAPA, root cause, or quality trend analysis; then taxonomy, spec/sampling, disposition owner, release evidence, and sign-off."
            ),
            "general": (
                "General expert check: first identify requesting department/business owner, first-version software shape, target user, supported business decision/action, scope boundary, acceptance evidence, and explicit out-of-scope items."
            ),
        }
        return (
            "IC Substrate expert PM quality gate:\n"
            "- The next question must fill one URD/PRD-ready field, not merely show domain knowledge.\n"
            "- Priority: business action/decision -> user/owner -> business object and grain -> KPI/formula/state definition -> workflow and ownership boundary -> data source/reconciliation/refresh -> acceptance evidence/sign-off/out-of-scope.\n"
            f"- Current track check: {track_checks[track]}\n"
            "- A/B/C options may confirm paths, definitions, or unknowns only. Do not present unconfirmed formulas, stations, states, systems, SLAs, or owners as facts.\n"
            "- If the key fields are ready for a first document, stop expanding and ask the user to confirm URD/PRD generation."
        )

    def _ic_substrate_missing_evidence_question_guidance(
        self,
        session: Session | None,
        structured_requirement_model: dict[str, Any],
        language: str | None = None,
    ) -> str:
        gate = self._ic_substrate_readiness_evidence_gate(session, structured_requirement_model)
        if not gate:
            return ""
        checks = gate.get("checks")
        if not isinstance(checks, list):
            return ""
        missing_checks = [check for check in checks if isinstance(check, dict) and not check.get("ready")]
        if not missing_checks:
            return ""
        department_key = str(gate.get("department_specific_evidence", "")).strip().lower()
        if department_key:
            missing_checks = sorted(
                missing_checks,
                key=lambda check: 0
                if str(check.get("key", "")).strip().lower().startswith(f"{department_key}_")
                else 1,
            )

        normalized_language = self._normalize_language(language)
        if normalized_language == "zh":
            heading = "IC Substrate 下一问证据缺口："
            intro = (
                "- 下一问优先补齐下列缺口中的 1 个；把 follow-up 改写成自然中文问题，"
                "并给 A/B/C 选项帮助业务方选择口径。"
            )
            label_prefix = "缺口"
            follow_prefix = "建议追问"
            close = "- 如果用户回答已覆盖某缺口，不要重复问；转向下一个未满足证据项。"
        elif normalized_language == "de":
            heading = "IC Substrate Evidence-Gaps fuer die naechste Frage:"
            intro = (
                "- Die naechste Frage soll genau einen der folgenden Gaps schliessen; "
                "formuliere die Follow-up-Frage natuerlich auf Deutsch und nutze A/B/C zur Definition."
            )
            label_prefix = "Gap"
            follow_prefix = "Empfohlene Rueckfrage"
            close = "- Wenn die Nutzerantwort einen Gap bereits abdeckt, nicht wiederholen; zum naechsten offenen Evidence Item wechseln."
        elif normalized_language == "ms":
            heading = "Gap evidence IC Substrate untuk soalan seterusnya:"
            intro = (
                "- Soalan seterusnya perlu menutup satu gap di bawah; tulis semula follow-up sebagai soalan Bahasa Melayu "
                "yang natural dan gunakan A/B/C untuk bantu pengguna pilih definisi."
            )
            label_prefix = "Gap"
            follow_prefix = "Cadangan soalan"
            close = "- Jika jawapan pengguna sudah meliputi gap itu, jangan ulang; beralih kepada evidence item seterusnya."
        else:
            heading = "IC Substrate evidence gaps for the next question:"
            intro = (
                "- The next question should close exactly one gap below; rewrite the follow-up as a natural English question "
                "and use A/B/C options to help the business owner choose a definition."
            )
            label_prefix = "Gap"
            follow_prefix = "Suggested follow-up"
            close = "- If the user already covered a gap, do not repeat it; move to the next missing evidence item."

        prioritized_checks = missing_checks[:3]
        lines = [heading, intro]
        for index, check in enumerate(prioritized_checks, start=1):
            key = self._single_line_markdown(str(check.get("key", "")).strip())
            label = self._single_line_markdown(str(check.get("label", "")).strip())
            follow_up = self._single_line_markdown(str(check.get("if_missing", "")).strip())
            lines.append(f"- {label_prefix} {index}: {label or key}")
            if follow_up:
                lines.append(f"  - {follow_prefix}: {follow_up}")
        lines.append(close)
        return "\n".join(lines)

    def _ic_substrate_runtime_guardrails_for_prompt(
        self,
        chain_state: dict[str, Any],
        language: str | None = None,
    ) -> str:
        if chain_state.get("mode") != "ic_substrate":
            return ""
        if self._normalize_language(language) == "zh":
            return (
                "运行时硬约束：\n"
                "- 这是本轮 prompt 的最终规则，优先级高于前面的模板样例和 Template context。\n"
                "- 每轮只能问一个问题；围绕当前部门/owner、当前需求形态路由和当前节点推进，不要把多个缺口合成连续追问。\n"
                "- 模板来源术语只能作为证据，不要自动变成选项；FVI、AOI、E-test、AVI、SAP、EAP、SPC、MES、QMS、ERP 等术语只有在用户或明确来源已确认适用时才能进入选项。\n"
                "- TDI 只能写作 TDI；不要展开缩写，不要在括号里解释，也不要在部门选项里暗示含义。\n"
                "- 不要自造公式、状态、站点、系统名、缺陷分类、SLA 数字或 owner 角色；这些都要问用户现场现行定义。\n"
                "- 如果用户的问题很宽泛，第一问先确认来自哪个入口或首版业务 owner：Production、Quality、TDI、General；如果用户属于其他部门或归属不清，归入 General，不要展开隐藏部门；如果部门已明确，就先确认首版软件形态、目标用户、使用场景和要支撑的业务决策/动作，再按 KPI/口径、主数据、流程状态、数据来源、责任边界来问。"
            )
        if self._normalize_language(language) == "de":
            return (
                "Runtime-Hard-Constraints:\n"
                "- Dies sind die finalen Regeln fuer diesen Prompt und haben Vorrang vor frueheren Template-Beispielen und Template context.\n"
                "- Pro Runde genau eine Frage stellen; entlang aktuellem Bereich/Owner, Bedarfsform-Routing und aktuellem Knoten vorgehen, statt mehrere Luecken in eine Antwort zu stapeln.\n"
                "- Begriffe aus der Vorlage sind Evidenz, keine Default-Optionen. Begriffe wie FVI, AOI, E-test, AVI, SAP, EAP, SPC, MES, QMS oder ERP duerfen nur in Optionen erscheinen, wenn Nutzer oder klare Quelle sie bestaetigt.\n"
                "- TDI nur als TDI schreiben. Akronym nicht aufloesen, keine Klammererklaerung und keine implizite Bedeutung in Department-Optionen.\n"
                "- Keine Formeln, Status, Stationen, Systemnamen, Defect Categories, SLA-Zahlen oder Owner-Rollen erfinden. Immer nach aktuellen Site-Definitionen des Nutzers fragen.\n"
                "- Wenn die Anfrage breit ist, zuerst den Einstieg oder First-Version Business Owner fragen: Production, Quality, TDI oder General. Andere oder unklare Bereiche in General routen und nicht als verborgene Department-Ketten ausbauen. Wenn der Bereich klar ist, zuerst Softwareform, Zielnutzer, Use Case und Business Decision/Action klaeren, dann KPI-Definitionen, Master Data, Workflow States, Datenquellen und Ownership Boundary."
            )
        if self._normalize_language(language) == "ms":
            return (
                "Peraturan keras runtime:\n"
                "- Ini ialah peraturan akhir untuk prompt ini dan lebih utama daripada contoh templat serta Template context terdahulu.\n"
                "- Tanya tepat satu soalan setiap pusingan; gerakkan perbualan mengikut jabatan/owner semasa, need-focus route dan nod semasa, bukan menggabungkan banyak jurang dalam satu balasan.\n"
                "- Istilah daripada templat ialah bukti, bukan pilihan default. Istilah seperti FVI, AOI, E-test, AVI, SAP, EAP, SPC, MES, QMS atau ERP hanya boleh masuk pilihan jika pengguna atau sumber jelas mengesahkan ia terpakai.\n"
                "- Tulis TDI hanya sebagai TDI. Jangan kembangkan akronim, tambah penerangan dalam kurungan atau membayangkan makna dalam pilihan jabatan.\n"
                "- Jangan reka formula, status, station, system name, defect category, nombor SLA atau owner role. Tanya definisi semasa di site pengguna.\n"
                "- Jika permintaan luas, tanya dahulu entry atau first-version business owner: Production, Quality, TDI atau General. Jika jabatan lain atau ownership belum jelas, route ke General dan jangan buka hidden department chain. Jika jabatan jelas, sahkan dahulu software shape, target user, use case dan business decision/action, kemudian tanya KPI definitions, master data, workflow states, data sources dan ownership boundary."
            )
        return (
            "Runtime hard constraints:\n"
            "- These are the final rules for this prompt and take priority over earlier template examples and Template context.\n"
            "- Ask exactly one question per turn; advance by the current department/owner, need-focus route, and current node instead of stacking multiple gaps into one reply.\n"
            "- Source terms from the template are evidence, not default options. Terms such as FVI, AOI, E-test, AVI, SAP, EAP, SPC, MES, QMS, or ERP may enter options only when the user or an explicit source confirms they apply.\n"
            "- Write TDI only as TDI. Do not expand the acronym, add parenthetical explanations, or imply a meaning inside department options.\n"
            "- Do not invent formulas, states, stations, system names, defect categories, SLA numbers, or owner roles. Ask for the user's current site definitions.\n"
            "- If the request is broad, first ask which entry point or first-version business owner it comes from: Production, Quality, TDI, or General. If it belongs to another department or ownership is unclear, route to General and do not open hidden department chains. If department is clear, first confirm the first-version software shape, target user, use case, and business decision/action the software must support, then ask through KPI definitions, master data, workflow states, data sources, and ownership boundary."
        )

    def _business_template_document_context(self, session: Session, language: str | None = None) -> str:
        template = self._resolve_business_template(session, language)
        if template is None:
            if not session.applied_template_name:
                return ""
            return (
                "Applied business template:\n"
                + json.dumps(
                    {
                        "template_name": session.applied_template_name,
                        "template_id": session.applied_template_id,
                    },
                    ensure_ascii=False,
                )
            )
        return "Applied business template:\n" + json.dumps(template, ensure_ascii=False)

    def _ic_substrate_readiness_evidence_gate(
        self,
        session: Session | None,
        structured_requirement_model: dict[str, Any],
    ) -> dict[str, Any]:
        if session is None:
            return {}

        template = self._resolve_business_template(session)
        template_context = template or {
            "template_id": session.applied_template_id,
            "template_name": session.applied_template_name,
        }
        if not self._template_matches_ic_substrate_focus(template_context):
            return {}

        model = normalize_structured_requirement_model(structured_requirement_model)
        product_context = model.get("product_context", {})
        collection_status = model.get("collection_status", {})

        def collect_text(value: Any) -> list[str]:
            if isinstance(value, str):
                return [value]
            if isinstance(value, list):
                items: list[str] = []
                for entry in value:
                    items.extend(collect_text(entry))
                return items
            if isinstance(value, dict):
                items = []
                for entry in value.values():
                    items.extend(collect_text(entry))
                return items
            return []

        def first_evidence(values: list[Any], keywords: list[str] | None = None) -> str:
            texts = [text.strip() for value in values for text in collect_text(value) if text.strip()]
            if not texts:
                return ""
            if keywords:
                normalized_keywords = [keyword.lower() for keyword in keywords]
                for text in texts:
                    lowered = text.lower()
                    if any(keyword in lowered for keyword in normalized_keywords):
                        return text[:220]
            return texts[0][:220]

        all_text = "\n".join(collect_text(model)).lower()
        data_text = "\n".join(collect_text(model.get("data_and_dependencies", []))).lower()
        acceptance_text = "\n".join(collect_text(model.get("acceptance_criteria", []))).lower()
        department = str(product_context.get("requesting_department", "")).strip().lower()
        department_key = self._ic_substrate_intent_track_from_structured_model(model).lower() or department
        has_pending_or_conflict = any(
            isinstance(item, dict)
            and str(item.get("status", "")).strip().lower() in {"pending_confirmation", "conflict"}
            for item in collection_status.values()
        )
        has_missing = any(
            isinstance(item, dict)
            and str(item.get("status", "")).strip().lower() == "missing"
            for item in collection_status.values()
        )
        checks = [
            {
                "key": "entry_owner",
                "label": "Confirmed entry department and business/acceptance owner",
                "ready": department in ACTIVE_IC_SUBSTRATE_DEPARTMENTS
                and bool(
                    str(product_context.get("business_owner", "")).strip()
                    or str(product_context.get("acceptance_owner", "")).strip()
                ),
                "evidence": first_evidence(
                    [
                        product_context.get("requesting_department", ""),
                        product_context.get("business_owner", ""),
                        product_context.get("acceptance_owner", ""),
                    ]
                ),
                "if_missing": "Ask which entry owns v1 and who signs off; do not assume owner roles.",
            },
            {
                "key": "business_action",
                "label": "Business action or decision the software supports",
                "ready": bool(str(product_context.get("decision_or_action", "")).strip()),
                "evidence": first_evidence([product_context.get("decision_or_action", "")]),
                "if_missing": "Ask the specific business decision/action before detailing pages or technology.",
            },
            {
                "key": "object_grain",
                "label": "Business object and grain",
                "ready": any(
                    keyword in all_text
                    for keyword in [
                        "lot",
                        "panel",
                        "unit",
                        "case",
                        "route",
                        "station",
                        "对象",
                        "粒度",
                        "工序",
                        "站点",
                        "批",
                    ]
                ),
                "evidence": first_evidence(
                    collect_text(model),
                    ["lot", "panel", "unit", "case", "route", "station", "对象", "粒度", "工序", "站点"],
                ),
                "if_missing": "Ask the lot/panel/unit/case grain and the route/station/time-window boundary.",
            },
            {
                "key": "workflow_state_owner",
                "label": "Workflow states, owner, and exception handling",
                "ready": any(
                    keyword in all_text
                    for keyword in [
                        "state",
                        "status",
                        "owner",
                        "hold",
                        "release",
                        "closure",
                        "rework",
                        "scrap",
                        "状态",
                        "责任",
                        "放行",
                        "关闭",
                        "返工",
                        "报废",
                    ]
                ),
                "evidence": first_evidence(
                    collect_text(model),
                    ["state", "status", "owner", "hold", "release", "closure", "状态", "责任", "放行", "关闭"],
                ),
                "if_missing": "Ask current state names, responsible owner, and how exceptions are closed.",
            },
            {
                "key": "data_reconciliation",
                "label": "Data source, source of truth, refresh, and reconciliation boundary",
                "ready": bool(data_text)
                and any(
                    keyword in data_text
                    for keyword in [
                        "source",
                        "truth",
                        "refresh",
                        "reconciliation",
                        "interface",
                        "system",
                        "数据源",
                        "刷新",
                        "对账",
                        "接口",
                        "系统",
                    ]
                ),
                "evidence": first_evidence(
                    [model.get("data_and_dependencies", [])],
                    ["source", "truth", "refresh", "reconciliation", "interface", "数据源", "刷新", "对账", "接口"],
                ),
                "if_missing": "Ask source of truth, refresh frequency, reconciliation rule, and unconfirmed interfaces.",
            },
            {
                "key": "acceptance_evidence",
                "label": "Business-verifiable acceptance evidence",
                "ready": bool(acceptance_text)
                and any(
                    keyword in acceptance_text
                    for keyword in [
                        "accept",
                        "evidence",
                        "sign-off",
                        "verify",
                        "验收",
                        "证据",
                        "签核",
                        "验证",
                    ]
                ),
                "evidence": first_evidence(
                    [model.get("acceptance_criteria", [])],
                    ["accept", "evidence", "sign-off", "verify", "验收", "证据", "签核", "验证"],
                ),
                "if_missing": "Ask which evidence proves the PRD is correct: main flow, exceptions, data accuracy, export/download, sign-off, and retention.",
            },
            {
                "key": "uncertainty_handling",
                "label": "Unconfirmed terms remain visible",
                "ready": bool(model.get("open_questions")) or has_pending_or_conflict or not has_missing,
                "evidence": first_evidence([model.get("open_questions", [])])
                or ("pending_confirmation/conflict exists" if has_pending_or_conflict else ""),
                "if_missing": "If any formula, status, system, station, SLA, or owner is not confirmed, list it in Open Questions or assumptions.",
            },
        ]
        department_specific_checks = {
            "production": [
                {
                    "key": "production_route_time_boundary",
                    "label": "Production route, station, and time-window boundary",
                    "ready": any(
                        keyword in all_text
                        for keyword in ["route", "station", "move-in", "move-out", "工序", "站点", "入站", "出站"]
                    )
                    and any(keyword in all_text for keyword in ["shift", "day", "hour", "time", "班次", "天", "小时", "时间"]),
                    "evidence": first_evidence(
                        collect_text(model),
                        ["route", "station", "move-in", "move-out", "工序", "站点", "班次", "时间"],
                    ),
                    "if_missing": "Ask the route/station scope and whether the metric is cut by shift, hour, day, lot close, or move-out time.",
                },
                {
                    "key": "production_kpi_formula_grain",
                    "label": "Production KPI formula, numerator/denominator, and grain",
                    "ready": any(
                        keyword in all_text
                        for keyword in ["yield", "throughput", "wip", "cycle time", "产出", "良率", "在制", "周期"]
                    )
                    and any(keyword in all_text for keyword in ["numerator", "denominator", "分子", "分母", "formula", "公式"]),
                    "evidence": first_evidence(
                        collect_text(model),
                        ["yield", "throughput", "wip", "cycle time", "numerator", "denominator", "良率", "分子", "分母"],
                    ),
                    "if_missing": "Ask the KPI formula, numerator/denominator, excluded lots, and lot/panel/unit aggregation rule.",
                },
                {
                    "key": "production_dispatch_exception_control",
                    "label": "Dispatch, bottleneck, hold, and exception action control",
                    "ready": any(
                        keyword in all_text
                        for keyword in ["dispatch", "priority", "bottleneck", "hold", "aging", "rework", "派工", "优先级", "瓶颈", "锁批", "超期", "返工"]
                    ),
                    "evidence": first_evidence(
                        collect_text(model),
                        ["dispatch", "priority", "bottleneck", "hold", "aging", "rework", "派工", "优先级", "瓶颈", "锁批"],
                    ),
                    "if_missing": "Ask what action the dashboard drives when WIP is aging, held, late, bottlenecked, or waiting for dispatch.",
                },
            ],
            "quality": [
                {
                    "key": "quality_defect_disposition",
                    "label": "Quality defect taxonomy, severity, and disposition rule",
                    "ready": any(
                        keyword in all_text
                        for keyword in ["defect code", "defect type", "severity", "mrb", "retest", "rework", "scrap", "缺陷代码", "缺陷类型", "严重度", "判定", "复测", "返工", "报废"]
                    ),
                    "evidence": first_evidence(
                        collect_text(model),
                        ["defect code", "defect type", "severity", "mrb", "retest", "rework", "scrap", "缺陷代码", "缺陷类型", "严重度", "判定"],
                    ),
                    "if_missing": "Ask the defect taxonomy, severity levels, and how each defect is dispositioned to retest, rework, scrap, MRB, or release.",
                },
                {
                    "key": "quality_inspection_coverage",
                    "label": "Quality inspection coverage, sampling, and false-call handling",
                    "ready": any(
                        keyword in all_text
                        for keyword in ["inspection", "sampling", "coverage", "aoi", "fvi", "e-test", "false call", "漏检", "误判", "抽样", "覆盖率", "检验", "检测"]
                    ),
                    "evidence": first_evidence(
                        collect_text(model),
                        ["inspection", "sampling", "coverage", "aoi", "fvi", "e-test", "false call", "抽样", "覆盖率", "检验"],
                    ),
                    "if_missing": "Ask which inspection stations feed the requirement, sampling or full inspection rules, and how false calls or missed defects are corrected.",
                },
                {
                    "key": "quality_capa_traceability",
                    "label": "Quality CAPA, root-cause, closure/reopen, and traceability",
                    "ready": any(
                        keyword in all_text
                        for keyword in ["capa", "root cause", "8d", "closure", "reopen", "traceability", "责任部门", "根因", "关闭", "重开", "追溯"]
                    ),
                    "evidence": first_evidence(
                        collect_text(model),
                        ["capa", "root cause", "8d", "closure", "reopen", "traceability", "根因", "关闭", "重开", "追溯"],
                    ),
                    "if_missing": "Ask how root cause, responsible department, CAPA owner, closure evidence, reopen condition, and lot traceability are proven.",
                },
            ],
            "tdi": [
                {
                    "key": "tdi_request_triage_sla",
                    "label": "TDI request intake, triage, priority, owner, and SLA",
                    "ready": any(
                        keyword in all_text
                        for keyword in ["case", "ticket", "triage", "intake", "工单", "案例", "受理", "分派", "请求入口"]
                    )
                    and any(
                        keyword in all_text
                        for keyword in ["priority", "sla", "owner", "status", "优先级", "时效", "负责人", "状态"]
                    ),
                    "evidence": first_evidence(
                        collect_text(model),
                        ["case", "ticket", "triage", "intake", "priority", "sla", "owner", "status", "工单", "受理", "优先级", "负责人"],
                    ),
                    "if_missing": "Ask how TDI requests enter, how priority is assigned, who owns each status, and what SLA or escalation rule applies.",
                },
                {
                    "key": "tdi_engineering_data_mapping",
                    "label": "TDI engineering data mapping across product, revision, spec, route, and parameter",
                    "ready": any(
                        keyword in all_text
                        for keyword in ["product", "revision", "spec", "recipe", "parameter", "route", "ecn", "npi", "产品", "版本", "规格", "参数", "工艺路线", "工程变更", "新产品"]
                    ),
                    "evidence": first_evidence(
                        collect_text(model),
                        ["product", "revision", "spec", "recipe", "parameter", "route", "ecn", "npi", "产品", "版本", "规格", "参数"],
                    ),
                    "if_missing": "Ask which product/revision/spec/route/parameter records TDI manages and how mismatches are reconciled.",
                },
                {
                    "key": "tdi_request_writeback_approval",
                    "label": "TDI writeback target, approval, versioning, and audit trail",
                    "ready": any(
                        keyword in all_text
                        for keyword in ["writeback", "approval", "version", "audit", "effective date", "change log", "回写", "审批", "版本", "审计", "生效日期", "变更记录"]
                    ),
                    "evidence": first_evidence(
                        collect_text(model),
                        ["writeback", "approval", "version", "audit", "effective date", "change log", "回写", "审批", "版本", "审计"],
                    ),
                    "if_missing": "Ask the writeback target, approval chain, version rule, effective date, and audit trail before treating a TDI workflow as executable.",
                },
            ],
        }
        checks.extend(department_specific_checks.get(department_key, []))
        missing = [check["key"] for check in checks if not check["ready"]]
        return {
            "enabled": True,
            "department_specific_evidence": department_key if department_key in department_specific_checks else "",
            "missing_evidence": missing,
            "checks": checks,
            "mandatory_rules": [
                "Treat each ready check as evidence, not as permission to invent nearby facts.",
                "If a check is not ready, include its if_missing text in Open Questions or assumptions.",
                "Never invent formulas, station names, system/table names, state names, SLA values, or owner roles to satisfy this gate.",
            ],
        }

    def _structured_requirement_model_prompt(self, session: Session, language: str) -> str:
        prompt_parts = [build_structured_requirement_model_prompt(language)]
        prompt_parts.append(self._structured_requirement_skill_extraction_guidance(language))
        prompt_parts.append(self._ic_substrate_structured_extraction_contract(session, language))
        template_addendum = self._business_template_pm_addendum(session, language)
        if template_addendum:
            prompt_parts.append(
                "Template-aware extraction rules:\n"
                "- Use the applied business template as additional context for what information matters most.\n"
                "- Keep the structured requirement schema unchanged.\n"
                "- If the template contains fields not represented directly in the schema, map them into the closest schema section or preserve them as open questions.\n"
                + "\n"
                + template_addendum
            )
        return "\n\n".join(part for part in prompt_parts if part)

    def _build_design_doc_messages(
        self,
        session: Session,
        messages: list[dict[str, Any]],
        structured_requirement_model: dict[str, Any],
        progress: dict[str, Any],
        seed_markdown: str,
        language: str,
    ) -> list[dict[str, str]]:
        language = self._normalize_language(language)
        content_label = CONVERSATION_LABELS.get(language, CONVERSATION_LABELS["en"])
        summary_label = SUMMARY_LABELS.get(language, SUMMARY_LABELS["en"])
        draft_mode = "draft_with_assumptions" if not progress.get("fully_confirmed") else "confirmed_design_doc"
        business_template_context = self._business_template_document_context(session, language)
        business_template_block = f"\n\n{business_template_context}" if business_template_context else ""
        document_quality_gate = self._document_quality_gate(
            structured_requirement_model,
            progress,
            draft_mode,
            session,
            language,
        )
        return [
            {"role": "system", "content": self._design_doc_prompt(session, language)},
            {
                "role": "user",
                "content": (
                    "Design document scaffold:\n"
                    + seed_markdown
                    + "\n\nCollection progress:\n"
                    + json.dumps(progress, ensure_ascii=False)
                    + f"\n\nGeneration mode:\n{draft_mode}"
                    + "\n\nDocument quality gate:\n"
                    + json.dumps(document_quality_gate, ensure_ascii=False)
                    + f"\n\n{content_label}:\n"
                    + json.dumps(self._conversation_messages(messages), ensure_ascii=False)
                    + f"\n\n{summary_label}:\n"
                    + json.dumps(structured_requirement_model, ensure_ascii=False)
                    + business_template_block
                ),
            },
        ]

    def _document_quality_gate(
        self,
        structured_requirement_model: dict[str, Any],
        progress: dict[str, Any],
        draft_mode: str,
        session: Session | None = None,
        language: str = "zh",
    ) -> dict[str, Any]:
        model = normalize_structured_requirement_model(structured_requirement_model)
        collection_status = model.get("collection_status", {})
        confirmed_items: list[str] = []
        pending_confirmation_items: list[dict[str, Any]] = []
        conflict_items: list[dict[str, Any]] = []
        missing_items: list[str] = []
        for key in REQUIREMENT_ITEM_KEYS:
            item = collection_status.get(key)
            status = str(item.get("status", "missing")).strip().lower() if isinstance(item, dict) else "missing"
            if status == "confirmed":
                confirmed_items.append(key)
            elif status == "conflict":
                conflict_items.append(
                    {
                        "item": key,
                        "reason": str(item.get("reason", "")).strip() if isinstance(item, dict) else "",
                        "pending_questions": item.get("pending_questions", []) if isinstance(item, dict) else [],
                    }
                )
            elif status == "missing":
                missing_items.append(key)
            else:
                pending_confirmation_items.append(
                    {
                        "item": key,
                        "status": status,
                        "reason": str(item.get("reason", "")).strip() if isinstance(item, dict) else "",
                        "pending_questions": item.get("pending_questions", []) if isinstance(item, dict) else [],
                    }
                )

        gate = {
            "generation_mode": draft_mode,
            "progress": progress,
            "confirmed_items": confirmed_items,
            "pending_confirmation_items": pending_confirmation_items,
            "conflict_items": conflict_items,
            "missing_items": missing_items,
            "pm_methodology_state": self.build_pm_methodology_state(model, language),
            "mandatory_document_rules": [
                "Use confirmed_items as facts.",
                "Treat pending_confirmation_items as draft assumptions or explicit open questions.",
                "Do not present captured or pending_confirmation items as confirmed facts.",
                "Include conflicts and missing items in the open-questions or risk section.",
                "Keep document sections complete enough for review, but label uncertainty visibly.",
            ],
        }
        ic_substrate_gate = self._ic_substrate_readiness_evidence_gate(session, model)
        if ic_substrate_gate:
            gate["ic_substrate_readiness_evidence"] = ic_substrate_gate
        return gate

    def _append_ic_substrate_prd_evidence_appendix(
        self,
        doc_markdown: str,
        session: Session | None,
        structured_requirement_model: dict[str, Any],
        language: str,
    ) -> str:
        gate = self._ic_substrate_readiness_evidence_gate(session, structured_requirement_model)
        if not gate:
            return doc_markdown

        heading = self._ic_substrate_prd_evidence_appendix_heading(language)
        if heading in doc_markdown or "IC Substrate Expert Evidence Appendix" in doc_markdown:
            return doc_markdown

        appendix = self._format_ic_substrate_prd_evidence_appendix(gate, language)
        if not appendix:
            return doc_markdown
        return f"{doc_markdown.rstrip()}\n\n{appendix}"

    def _ic_substrate_prd_evidence_appendix_heading(self, language: str) -> str:
        normalized = self._normalize_language(language)
        if normalized == "zh":
            return "## 9. IC Substrate 专家证据附录"
        if normalized == "de":
            return "## 9. IC Substrate Experten-Evidence-Anhang"
        if normalized == "ms":
            return "## 9. Lampiran Evidence Pakar IC Substrate"
        return "## 9. IC Substrate Expert Evidence Appendix"

    def _format_ic_substrate_prd_evidence_appendix(
        self,
        gate: dict[str, Any],
        language: str,
    ) -> str:
        checks = gate.get("checks")
        if not isinstance(checks, list) or not checks:
            return ""

        normalized = self._normalize_language(language)
        if normalized == "zh":
            labels = {
                "heading": self._ic_substrate_prd_evidence_appendix_heading(language),
                "summary": "证据状态",
                "missing": "缺失证据",
                "none": "无",
                "ready": "就绪",
                "not_ready": "待补齐",
                "evidence": "证据",
                "follow_up": "待确认追问",
                "rules": "强制规则",
            }
        elif normalized == "de":
            labels = {
                "heading": self._ic_substrate_prd_evidence_appendix_heading(language),
                "summary": "Evidence-Status",
                "missing": "Fehlende Evidence",
                "none": "Keine",
                "ready": "Bereit",
                "not_ready": "Offen",
                "evidence": "Evidence",
                "follow_up": "Zu klaerende Rueckfrage",
                "rules": "Pflichtregeln",
            }
        elif normalized == "ms":
            labels = {
                "heading": self._ic_substrate_prd_evidence_appendix_heading(language),
                "summary": "Status evidence",
                "missing": "Evidence belum lengkap",
                "none": "Tiada",
                "ready": "Ready",
                "not_ready": "Belum ready",
                "evidence": "Evidence",
                "follow_up": "Soalan pengesahan",
                "rules": "Peraturan wajib",
            }
        else:
            labels = {
                "heading": self._ic_substrate_prd_evidence_appendix_heading(language),
                "summary": "Evidence status",
                "missing": "Missing evidence",
                "none": "None",
                "ready": "Ready",
                "not_ready": "Missing",
                "evidence": "Evidence",
                "follow_up": "Required follow-up",
                "rules": "Mandatory rules",
            }

        ready_count = sum(1 for check in checks if isinstance(check, dict) and check.get("ready"))
        total_count = sum(1 for check in checks if isinstance(check, dict))
        missing = gate.get("missing_evidence") if isinstance(gate.get("missing_evidence"), list) else []
        missing_text = ", ".join(str(item) for item in missing) if missing else labels["none"]
        lines = [
            labels["heading"],
            "",
            f"- **{labels['summary']}**: {ready_count}/{total_count}",
            f"- **{labels['missing']}**: {missing_text}",
            "",
        ]

        for check in checks:
            if not isinstance(check, dict):
                continue
            label = self._single_line_markdown(str(check.get("label", "")).strip() or str(check.get("key", "")))
            status = labels["ready"] if check.get("ready") else labels["not_ready"]
            evidence = self._single_line_markdown(str(check.get("evidence", "")).strip())
            follow_up = self._single_line_markdown(str(check.get("if_missing", "")).strip())
            lines.append(f"- **{label}**: {status}")
            if evidence:
                lines.append(f"  - {labels['evidence']}: {evidence}")
            if not check.get("ready") and follow_up:
                lines.append(f"  - {labels['follow_up']}: {follow_up}")

        mandatory_rules = gate.get("mandatory_rules")
        if isinstance(mandatory_rules, list) and mandatory_rules:
            lines.extend(["", f"**{labels['rules']}**"])
            for rule in mandatory_rules:
                rule_text = self._single_line_markdown(str(rule).strip())
                if rule_text:
                    lines.append(f"- {rule_text}")
        return "\n".join(lines).strip()

    def _single_line_markdown(self, text: str) -> str:
        return " ".join(text.replace("|", "\\|").split())

    def _document_quality_gate_block_markdown(
        self,
        structured_requirement_model: dict[str, Any],
        progress: dict[str, Any],
        language: str,
        document_type: str,
        session: Session | None = None,
    ) -> str:
        language = self._normalize_language(language)
        gate = self._document_quality_gate(
            structured_requirement_model,
            progress,
            "quality_gate_blocked",
            session,
            language,
        )
        pending_items = gate["pending_confirmation_items"]
        conflict_items = gate["conflict_items"]
        missing_items = gate["missing_items"]

        if language == "zh":
            title = "正式文档质量门槛未通过"
            doc_label = "PRD" if document_type == "prd" else "系统设计文档"
            intro = (
                f"当前不会生成正式{doc_label}，因为仍有需求项未完成确认。"
                "请先完成下面的确认项，再生成正式文档。"
            )
            progress_line = (
                f"- 文档就绪度：{progress.get('readiness_percentage', 0)}%\n"
                f"- 收集覆盖率：{progress.get('collection_coverage_percentage', 0)}%\n"
                f"- 确认完成度：{progress.get('confirmation_percentage', 0)}%\n"
                f"- 核心项已确认：{'是' if progress.get('core_requirements_confirmed') else '否'}\n"
                f"- 待确认项：{progress.get('pending_confirmation_count', 0)}\n"
                f"- 冲突项：{progress.get('conflict_count', 0)}"
            )
            pending_title = "待确认项"
            conflict_title = "冲突项"
            missing_title = "缺失项"
            pm_methodology_title = "PM 方法论缺口"
            evidence_title = "IC Substrate 专家证据缺口"
            next_step = "下一步：请在对话中确认上述问题；确认完成后再生成正式文档。"
            empty = "无"
        elif language == "de":
            title = "Qualitaetsgate fuer das formale Dokument nicht erfuellt"
            doc_label = "PRD" if document_type == "prd" else "Systemdesign-Dokument"
            intro = (
                f"Das formale {doc_label} wird noch nicht erzeugt, weil nicht alle Anforderungen bestaetigt sind. "
                "Bitte bestaetige die folgenden Punkte zuerst."
            )
            progress_line = (
                f"- Dokumentreife: {progress.get('readiness_percentage', 0)}%\n"
                f"- Erfassungsquote: {progress.get('collection_coverage_percentage', 0)}%\n"
                f"- Bestaetigungsstand: {progress.get('confirmation_percentage', 0)}%\n"
                f"- Kernpunkte bestaetigt: {'Ja' if progress.get('core_requirements_confirmed') else 'Nein'}\n"
                f"- Offene Bestaetigungen: {progress.get('pending_confirmation_count', 0)}\n"
                f"- Konflikte: {progress.get('conflict_count', 0)}"
            )
            pending_title = "Offene Bestaetigungen"
            conflict_title = "Konflikte"
            missing_title = "Fehlende Punkte"
            pm_methodology_title = "PM Methodik-Luecken"
            evidence_title = "IC Substrate Expert Evidence Gaps"
            next_step = "Naechster Schritt: Bestaetige diese Punkte im Dialog und erzeuge danach das formale Dokument."
            empty = "Keine"
        elif language == "ms":
            title = "Pintu kualiti dokumen rasmi belum lulus"
            doc_label = "PRD" if document_type == "prd" else "dokumen reka bentuk sistem"
            intro = (
                f"Dokumen rasmi {doc_label} belum akan dijana kerana masih ada item keperluan yang belum disahkan. "
                "Sila sahkan item berikut dahulu."
            )
            progress_line = (
                f"- Kesediaan dokumen: {progress.get('readiness_percentage', 0)}%\n"
                f"- Liputan kutipan: {progress.get('collection_coverage_percentage', 0)}%\n"
                f"- Kemajuan pengesahan: {progress.get('confirmation_percentage', 0)}%\n"
                f"- Item teras disahkan: {'Ya' if progress.get('core_requirements_confirmed') else 'Tidak'}\n"
                f"- Item menunggu pengesahan: {progress.get('pending_confirmation_count', 0)}\n"
                f"- Konflik: {progress.get('conflict_count', 0)}"
            )
            pending_title = "Item menunggu pengesahan"
            conflict_title = "Konflik"
            missing_title = "Item belum lengkap"
            pm_methodology_title = "Jurang metodologi PM"
            evidence_title = "Jurang evidence pakar IC Substrate"
            next_step = "Langkah seterusnya: sahkan item ini dalam perbualan, kemudian jana dokumen rasmi."
            empty = "Tiada"
        else:
            title = "Formal Document Quality Gate Not Passed"
            doc_label = "PRD" if document_type == "prd" else "System Design Document"
            intro = (
                f"The formal {doc_label} will not be generated yet because some requirement areas are not confirmed. "
                "Confirm the items below first, then generate the formal document."
            )
            progress_line = (
                f"- Document readiness: {progress.get('readiness_percentage', 0)}%\n"
                f"- Collection coverage: {progress.get('collection_coverage_percentage', 0)}%\n"
                f"- Confirmation progress: {progress.get('confirmation_percentage', 0)}%\n"
                f"- Core items confirmed: {'Yes' if progress.get('core_requirements_confirmed') else 'No'}\n"
                f"- Pending confirmation: {progress.get('pending_confirmation_count', 0)}\n"
                f"- Conflicts: {progress.get('conflict_count', 0)}"
            )
            pending_title = "Pending Confirmation"
            conflict_title = "Conflicts"
            missing_title = "Missing Items"
            pm_methodology_title = "PM Methodology Gaps"
            evidence_title = "IC Substrate Expert Evidence Gaps"
            next_step = "Next step: confirm these items in the conversation, then generate the formal document."
            empty = "None"

        def format_pending(values: list[dict[str, Any]]) -> list[str]:
            if not values:
                return [f"- {empty}"]
            lines = []
            for item in values:
                question = ""
                questions = item.get("pending_questions")
                if isinstance(questions, list) and questions:
                    question = str(questions[0]).strip()
                reason = str(item.get("reason", "")).strip()
                suffix = question or reason or str(item.get("status", "")).strip()
                lines.append(f"- {item.get('item')}: {suffix}".rstrip())
            return lines

        def format_names(values: list[Any]) -> list[str]:
            if not values:
                return [f"- {empty}"]
            return [f"- {value}" for value in values]

        def format_ic_substrate_evidence_gaps() -> list[str]:
            ic_gate = gate.get("ic_substrate_readiness_evidence")
            if not isinstance(ic_gate, dict):
                return []
            checks = ic_gate.get("checks")
            if not isinstance(checks, list):
                return []
            lines = [f"## {evidence_title}"]
            missing_lines = []
            for raw_check in checks:
                if not isinstance(raw_check, dict) or raw_check.get("ready"):
                    continue
                label = str(raw_check.get("label", raw_check.get("key", ""))).strip()
                next_question = str(raw_check.get("if_missing", "")).strip()
                suffix = f": {next_question}" if next_question else ""
                missing_lines.append(f"- {label}{suffix}")
            if not missing_lines:
                missing_lines = [f"- {empty}"]
            return [*lines, *missing_lines, ""]

        def format_pm_methodology_gaps() -> list[str]:
            pm_state = gate.get("pm_methodology_state")
            if not isinstance(pm_state, dict):
                return []
            checks = pm_state.get("checks")
            if not isinstance(checks, list):
                return []
            missing_lines = []
            for raw_check in checks:
                if not isinstance(raw_check, dict) or raw_check.get("ready"):
                    continue
                label = str(raw_check.get("label", raw_check.get("key", ""))).strip()
                method = str(raw_check.get("method", "")).strip()
                next_question = str(raw_check.get("next_question", "")).strip()
                label_text = f"{label} ({method})" if method else label
                suffix = f": {next_question}" if next_question else ""
                missing_lines.append(f"- {label_text}{suffix}")
            if not missing_lines:
                missing_lines = [f"- {empty}"]
            return [f"## {pm_methodology_title}", *missing_lines, ""]

        return "\n".join(
            [
                f"# {title}",
                "",
                intro,
                "",
                "## Progress",
                progress_line,
                "",
                f"## {pending_title}",
                *format_pending(pending_items),
                "",
                f"## {conflict_title}",
                *format_pending(conflict_items),
                "",
                f"## {missing_title}",
                *format_names(missing_items),
                "",
                *format_pm_methodology_gaps(),
                *format_ic_substrate_evidence_gaps(),
                f"> {next_step}",
            ]
        )

    def _append_message(
        self,
        session_id: str,
        role: str,
        content: str,
        thinking: str = "",
        kind: str = CHAT_MESSAGE_KIND,
        download_filename: str = "",
        storage_path: str = "",
        display_content: str = "",
        created_at: str | None = None,
    ) -> int:
        created_at_value = created_at or datetime.now(timezone.utc).isoformat()
        return self.session_store.append_message(
            session_id=session_id,
            role=role,
            content=content,
            created_at=created_at_value,
            thinking=thinking,
            kind=kind,
            download_filename=download_filename,
            storage_path=storage_path,
            display_content=display_content,
        )

    def _require_session(self, session_id: str) -> Session:
        session = self.get_session(session_id)
        if session is None:
            raise KeyError("Session not found.")
        return session

    def _session_has_user_messages(self, session: Session) -> bool:
        return any(item.get("role") == "user" for item in session.messages)

    def _update_session_title_from_message(self, session_id: str, user_message: str, language: str) -> None:
        title = self._derive_session_title(user_message, language)
        if title:
            self.session_store.update_session_title(session_id, title)

    def _derive_session_title(self, user_message: str, language: str) -> str:
        collapsed = " ".join(user_message.split())
        return self.session_store.format_session_title(collapsed, language)

    def _default_design_doc(self, language: str) -> str:
        language = self._normalize_language(language)
        return DESIGN_DOC_EMPTY_BY_LANGUAGE.get(language, DESIGN_DOC_EMPTY_BY_LANGUAGE["en"])

    def _build_design_doc_seed_markdown(
        self,
        structured_requirement_model: dict[str, Any],
        progress: dict[str, Any],
        language: str,
    ) -> str:
        language = self._normalize_language(language)
        model = normalize_structured_requirement_model(structured_requirement_model)

        copy = {
            "title": "# System Design Document (Draft Scaffold)",
            "draft_hint": (
                "> This design draft is assembled from the structured requirement model first, "
                "then refined by the LLM."
            ),
            "missing_hint": "> Missing or unconfirmed information is explicitly marked as TBD.",
            "tbd": "TBD",
            "readiness_label": "Document readiness",
            "progress_label": "Collection coverage",
            "confirmation_label": "Confirmation progress",
            "sections": {
                "scope_goals": "## 1. Scope and Goals",
                "scope_in": "### 1.1 In Scope",
                "scope_out": "### 1.2 Out of Scope",
                "roles": "## 2. User Roles and Participants",
                "use_cases": "## 3. System Use Cases",
                "functional": "## 4. Functional Requirements",
                "feature_overview": "### 4.1 Feature Overview",
                "feature_details": "### 4.2 Feature Details",
                "business_rules": "### 4.3 Business Rules",
                "non_functional": "## 5. Non-functional Requirements",
                "architecture": "## 6. High-level Architecture Design",
                "modules": "## 7. Module Responsibilities",
                "module_candidates": "### 7.1 Candidate Modules",
                "page_touchpoints": "### 7.2 Page / Touchpoint Notes",
                "api": "## 8. API Design (Draft)",
                "data_model": "## 9. Data Model and Database Design",
                "dependencies": "### 9.1 Known Data / Dependency Inputs",
                "key_flows": "## 10. Key Flows / Sequence Notes",
                "security": "## 11. Security, Privacy, and Compliance",
                "observability": "## 12. Observability and Operations",
                "deployment": "## 13. Deployment and Environment Planning",
                "testing": "## 14. Testing and Acceptance Plan",
                "risks": "## 15. Risks, Trade-offs, and Assumptions",
                "milestones": "## 16. Milestones and Delivery Plan",
                "open_questions": "## 17. Open Questions / Missing Inputs",
            },
            "fields": {
                "project_name": "Project name",
                "requirement_name": "Requirement name",
                "background": "Background",
                "objective": "Objective",
                "description": "Description",
                "trigger": "Trigger",
                "processing_logic": "Processing logic",
                "inputs": "Inputs",
                "outputs": "Outputs",
                "exception_cases": "Exception cases",
                "page_name": "Page name",
                "entry_point": "Entry point",
                "page_elements": "Page elements",
                "button_actions": "Button actions",
                "draft_note": "Draft note",
            },
            "feature_label": "Feature",
            "page_label": "Page",
        }
        if language == "zh":
            copy = {
                "title": "# 系统设计文档（草稿骨架）",
                "draft_hint": "> 该设计文档会先基于结构化需求生成稳定骨架，再由模型补充和润色。",
                "missing_hint": "> 缺失或未确认的信息会明确标记为 TBD。",
                "tbd": "TBD",
                "readiness_label": "文档就绪度",
                "progress_label": "收集覆盖率",
                "confirmation_label": "确认完成度",
                "sections": {
                    "scope_goals": "## 1. 范围与目标",
                    "scope_in": "### 1.1 本次范围",
                    "scope_out": "### 1.2 非本次范围",
                    "roles": "## 2. 用户角色与参与方",
                    "use_cases": "## 3. 系统用例",
                    "functional": "## 4. 功能需求",
                    "feature_overview": "### 4.1 功能概述",
                    "feature_details": "### 4.2 功能明细",
                    "business_rules": "### 4.3 业务规则",
                    "non_functional": "## 5. 非功能需求",
                    "architecture": "## 6. 高层架构设计",
                    "modules": "## 7. 模块职责划分",
                    "module_candidates": "### 7.1 候选模块",
                    "page_touchpoints": "### 7.2 页面 / 触点说明",
                    "api": "## 8. API 设计（草案）",
                    "data_model": "## 9. 数据模型与数据库设计",
                    "dependencies": "### 9.1 已识别的数据 / 依赖输入",
                    "key_flows": "## 10. 关键流程 / 时序说明",
                    "security": "## 11. 安全、隐私与合规",
                    "observability": "## 12. 可观测性与运维",
                    "deployment": "## 13. 部署与环境规划",
                    "testing": "## 14. 测试与验收方案",
                    "risks": "## 15. 风险、权衡与假设",
                    "milestones": "## 16. 里程碑与交付计划",
                    "open_questions": "## 17. 待确认问题 / 缺失输入",
                },
                "fields": {
                    "project_name": "项目名称",
                    "requirement_name": "需求名称",
                    "background": "背景说明",
                    "objective": "目标",
                    "description": "功能描述",
                    "trigger": "触发方式",
                    "processing_logic": "处理逻辑",
                    "inputs": "输入项",
                    "outputs": "输出结果",
                    "exception_cases": "异常情况",
                    "page_name": "页面名称",
                    "entry_point": "入口位置",
                    "page_elements": "页面元素",
                    "button_actions": "按钮动作",
                    "draft_note": "草稿说明",
                },
                "feature_label": "功能",
                "page_label": "页面",
            }

        tbd = copy["tbd"]

        def normalize_list(values: Any) -> list[str]:
            if not isinstance(values, list):
                return []
            return [str(item).strip() for item in values if str(item).strip()]

        def value_or_tbd(value: Any) -> str:
            normalized = str(value or "").strip()
            return normalized or tbd

        def bullet_lines(values: Any) -> list[str]:
            normalized = normalize_list(values)
            if not normalized:
                return ["", f"- {tbd}"]
            return ["", *[f"- {item}" for item in normalized]]

        def numbered_lines(values: Any) -> list[str]:
            normalized = normalize_list(values)
            if not normalized:
                return ["", f"1. {tbd}"]
            return ["", *[f"{index + 1}. {item}" for index, item in enumerate(normalized)]]

        def feature_lines() -> list[str]:
            features = model.get("functional_requirements", {}).get("feature_details", [])
            if not isinstance(features, list):
                return ["", f"- {tbd}"]

            filtered: list[dict[str, Any]] = []
            for item in features:
                if not isinstance(item, dict):
                    continue
                if any(
                    [
                        str(item.get("feature_name", "")).strip(),
                        str(item.get("description", "")).strip(),
                        str(item.get("trigger", "")).strip(),
                        str(item.get("processing_logic", "")).strip(),
                        normalize_list(item.get("inputs")),
                        normalize_list(item.get("outputs")),
                        normalize_list(item.get("exception_cases")),
                    ]
                ):
                    filtered.append(item)

            if not filtered:
                return ["", f"- {tbd}"]

            lines = [""]
            for index, item in enumerate(filtered, start=1):
                title = (
                    str(item.get("feature_name", "")).strip()
                    or str(item.get("description", "")).strip()
                    or tbd
                )
                lines.append(f"#### {copy['feature_label']} {index}: {title}")
                lines.append("")
                lines.append(f"- {copy['fields']['description']}: {value_or_tbd(item.get('description'))}")
                lines.append(f"- {copy['fields']['trigger']}: {value_or_tbd(item.get('trigger'))}")
                lines.append(
                    f"- {copy['fields']['processing_logic']}: {value_or_tbd(item.get('processing_logic'))}"
                )
                lines.append(
                    f"- {copy['fields']['inputs']}: {', '.join(normalize_list(item.get('inputs'))) or tbd}"
                )
                lines.append(
                    f"- {copy['fields']['outputs']}: {', '.join(normalize_list(item.get('outputs'))) or tbd}"
                )
                lines.append(
                    f"- {copy['fields']['exception_cases']}: "
                    f"{', '.join(normalize_list(item.get('exception_cases'))) or tbd}"
                )
                if index < len(filtered):
                    lines.append("")
            return lines

        def page_lines() -> list[str]:
            pages = model.get("page_and_interaction", {}).get("pages", [])
            if not isinstance(pages, list):
                return ["", f"- {tbd}"]

            filtered: list[dict[str, Any]] = []
            for item in pages:
                if not isinstance(item, dict):
                    continue
                if any(
                    [
                        str(item.get("page_name", "")).strip(),
                        str(item.get("entry_point", "")).strip(),
                        normalize_list(item.get("page_elements")),
                        normalize_list(item.get("button_actions")),
                    ]
                ):
                    filtered.append(item)

            if not filtered:
                return ["", f"- {tbd}"]

            lines = [""]
            for index, item in enumerate(filtered, start=1):
                title = (
                    str(item.get("page_name", "")).strip()
                    or str(item.get("entry_point", "")).strip()
                    or tbd
                )
                lines.append(f"#### {copy['page_label']} {index}: {title}")
                lines.append("")
                lines.append(f"- {copy['fields']['page_name']}: {value_or_tbd(item.get('page_name'))}")
                lines.append(f"- {copy['fields']['entry_point']}: {value_or_tbd(item.get('entry_point'))}")
                lines.append(
                    f"- {copy['fields']['page_elements']}: "
                    f"{', '.join(normalize_list(item.get('page_elements'))) or tbd}"
                )
                lines.append(
                    f"- {copy['fields']['button_actions']}: "
                    f"{', '.join(normalize_list(item.get('button_actions'))) or tbd}"
                )
                if index < len(filtered):
                    lines.append("")
            return lines

        candidate_modules: list[str] = []
        for item in model.get("functional_requirements", {}).get("feature_details", []):
            if not isinstance(item, dict):
                continue
            module_name = str(item.get("feature_name", "")).strip() or str(item.get("description", "")).strip()
            if module_name:
                candidate_modules.append(module_name)
        for item in model.get("page_and_interaction", {}).get("pages", []):
            if not isinstance(item, dict):
                continue
            module_name = str(item.get("page_name", "")).strip() or str(item.get("entry_point", "")).strip()
            if module_name:
                candidate_modules.append(module_name)
        candidate_modules = list(dict.fromkeys(candidate_modules))

        pending_questions: list[str] = []
        collection_status = model.get("collection_status", {})
        if isinstance(collection_status, dict):
            for item in collection_status.values():
                if not isinstance(item, dict):
                    continue
                pending_questions.extend(normalize_list(item.get("pending_questions")))
        open_questions = list(
            dict.fromkeys([*normalize_list(model.get("open_questions")), *pending_questions])
        )

        risk_notes = normalize_list(model.get("risks_and_notes"))
        if not progress.get("fully_confirmed"):
            risk_notes = list(
                dict.fromkeys(
                    [
                        f"{copy['fields']['draft_note']}: "
                        + (
                            "该文档仍包含基于未完全确认需求的草稿假设。"
                            if language == "zh"
                            else "This document still contains draft assumptions because not all requirements are fully confirmed."
                        ),
                        *risk_notes,
                    ]
                )
            )

        lines: list[str] = [
            copy["title"],
            "",
            copy["draft_hint"],
            copy["missing_hint"],
            (
                f"> {copy['readiness_label']}: {progress.get('readiness_percentage', 0)}% | "
                f"{copy['progress_label']}: {progress.get('collection_coverage_percentage', 0)}% | "
                f"{copy['confirmation_label']}: {progress.get('confirmation_percentage', 0)}%"
            ),
            "",
            copy["sections"]["scope_goals"],
            "",
            f"- {copy['fields']['project_name']}: {value_or_tbd(model.get('document_info', {}).get('project_name'))}",
            f"- {copy['fields']['requirement_name']}: {value_or_tbd(model.get('document_info', {}).get('requirement_name'))}",
            f"- {copy['fields']['background']}: {value_or_tbd(model.get('background', {}).get('summary'))}",
            f"- {copy['fields']['objective']}: {value_or_tbd(model.get('background', {}).get('objective'))}",
            "",
            copy["sections"]["scope_in"],
            *bullet_lines(model.get("scope", {}).get("in_scope")),
            "",
            copy["sections"]["scope_out"],
            *bullet_lines(model.get("scope", {}).get("out_of_scope")),
            "",
            copy["sections"]["roles"],
            *bullet_lines(model.get("users_and_scenarios", {}).get("target_users")),
            "",
            copy["sections"]["use_cases"],
            *numbered_lines(model.get("users_and_scenarios", {}).get("core_scenarios")),
            "",
            copy["sections"]["functional"],
            "",
            copy["sections"]["feature_overview"],
            "",
            value_or_tbd(model.get("functional_requirements", {}).get("overview")),
            "",
            copy["sections"]["feature_details"],
            *feature_lines(),
            "",
            copy["sections"]["business_rules"],
            *bullet_lines(model.get("business_rules")),
            "",
            copy["sections"]["non_functional"],
            *bullet_lines([]),
            "",
            copy["sections"]["architecture"],
            *bullet_lines([]),
            "",
            copy["sections"]["modules"],
            "",
            copy["sections"]["module_candidates"],
            *bullet_lines(candidate_modules),
            "",
            copy["sections"]["page_touchpoints"],
            *page_lines(),
            "",
            copy["sections"]["api"],
            *bullet_lines([]),
            "",
            copy["sections"]["data_model"],
            "",
            copy["sections"]["dependencies"],
            *bullet_lines(model.get("data_and_dependencies")),
            "",
            copy["sections"]["key_flows"],
            *numbered_lines(model.get("page_and_interaction", {}).get("interaction_flow")),
            "",
            copy["sections"]["security"],
            *bullet_lines([]),
            "",
            copy["sections"]["observability"],
            *bullet_lines([]),
            "",
            copy["sections"]["deployment"],
            *bullet_lines([]),
            "",
            copy["sections"]["testing"],
            *bullet_lines(model.get("acceptance_criteria")),
            "",
            copy["sections"]["risks"],
            *bullet_lines(risk_notes),
            "",
            copy["sections"]["milestones"],
            *bullet_lines([]),
            "",
            copy["sections"]["open_questions"],
            *bullet_lines(open_questions),
        ]
        return "\n".join(lines)

    def _readiness_phase_directive_for_prompt(self, session: Session, language: str) -> str:
        """Authoritative, deterministic readiness directive injected before the model speaks.

        The single hard gate is the structured "Fully Confirmed" state; PM Methodology is an
        advisory quality score (shown on the right) that must NOT block generation - otherwise
        the conversation circles forever on hard-to-satisfy heuristic checks. Phase + next gap
        are computed from the same progress the panel renders, so chat stays aligned with the
        metrics by construction.
        """
        normalized = self._normalize_language(language)
        model = self._latest_structured_requirement_model_for_prompt(session, normalized)
        progress = self._structured_requirement_progress(model)
        _, pm_state = self._pm_methodology_ready_for_generation(model, normalized)
        structured_ready = bool(progress.get("ready_to_generate"))
        has_prd = self.get_saved_prd_document(session.id) is not None
        cov = self._safe_int(progress.get("collection_coverage_percentage"))
        conf = self._safe_int(progress.get("confirmation_percentage"))
        confirmed = self._safe_int(progress.get("confirmed_count"))
        total = self._safe_int(progress.get("total_count"))
        score = self._safe_int(pm_state.get("score"))
        zh = normalized == "zh"

        # Phase 1 - collecting: the structured Fully Confirmed gate is not passed yet.
        if not structured_ready:
            blocker = self._next_readiness_blocker(model, progress, pm_state)
            blocker_question = str(blocker.get("question", "")).strip()
            blocker_label = str(blocker.get("label", "")).strip()
            if zh:
                return (
                    "就绪状态机（权威指示，优先级最高，覆盖任何相反说法）：\n"
                    f"- 阶段=采集中。结构化门禁未过：已确认 {confirmed}/{total}（覆盖 {cov}%、确认 {conf}%）。PM Methodology {score}% 仅作质量参考，不阻断生成。\n"
                    "- 严禁声称“需求已足够/已完整/可以生成文档/可以 Go Coding”，严禁让用户点 Generate 或 Open Vibe Coding；它们只有结构化全部确认后才会亮。\n"
                    "- 本轮只补这一个结构化缺口：只问一个问题，结尾给 A/B/C。不要为方法论分数单独追问。\n"
                    "- 数据接口与每个 KPI 公式是上线必备项：若当前缺口是数据接口或公式且用户给不出确切值，A/B/C 必须有一项为“采用以下假设并继续”（该假设记入 ASSUMPTIONS）；绝不能因含糊回答（如“从 MES 取”）就标确认。\n"
                    f"- 下一个缺口（{blocker_label}）：{blocker_question}"
                )
            return (
                "READINESS STATE MACHINE (authoritative, highest priority, overrides any contrary statement):\n"
                f"- Phase = collecting. Structured gate not passed: {confirmed}/{total} confirmed (coverage {cov}%, confirmation {conf}%). PM Methodology {score}% is an advisory quality score only and does NOT block generation.\n"
                "- Do NOT claim the requirement is enough/complete/ready, and do NOT tell the user to click Generate or Open Vibe Coding; those unlock only after every structured item is confirmed.\n"
                "- This turn close exactly one structured gap: one question, end with A/B/C. Do not raise separate questions just to lift the methodology score.\n"
                "- The data interface and every KPI formula are mandatory for go-live: if the current gap is the data interface or a formula and the user has no exact value, one of the A/B/C options MUST be 'use this stated assumption and continue' (recorded under ASSUMPTIONS); never mark them confirmed on a vague answer like 'from MES'.\n"
                f"- Next gap ({blocker_label}): {blocker_question}"
            )

        # Phase 2 - ready to generate: structured fully confirmed, document not produced yet.
        if not has_prd:
            if zh:
                return (
                    "就绪状态机（权威指示，优先级最高）：\n"
                    f"- 阶段=可生成。结构化需求已全部确认，右侧 “Generate Documents” 按钮已可点（PM Methodology {score}% 为参考分）。\n"
                    "- 请告诉用户需求已就绪、点击右侧 “Generate Documents” 生成正式文档；可顺带提一句方法论上还能补强的点，但不要当作阻断项、也不要因此不让生成。\n"
                    "- 生成文档之前还不要声称可以 Go Coding。"
                )
            return (
                "READINESS STATE MACHINE (authoritative, highest priority):\n"
                f"- Phase = ready to generate. All structured items are confirmed; the right-side \"Generate Documents\" button is enabled (PM Methodology {score}% is advisory).\n"
                "- Tell the user the requirement is ready and to click \"Generate Documents\"; you may note optional methodology improvements but never treat them as blockers or withhold generation.\n"
                "- Do not claim Go Coding is ready until the document has been generated."
            )

        # Phase 3 - ready for handoff: structured confirmed and the document exists.
        if zh:
            return (
                "就绪状态机（权威指示，优先级最高）：\n"
                "- 阶段=可交接。结构化已全部确认且正式文档已生成。\n"
                "- 可以引导用户点击右侧 Open Vibe Coding 进入编码交接；不要再开新澄清问题，除非出现冲突或新范围。"
            )
        return (
            "READINESS STATE MACHINE (authoritative, highest priority):\n"
            "- Phase = ready for handoff. Structured requirements are confirmed and the document exists.\n"
            "- Guide the user to click Open Vibe Coding for the coding handoff; do not open new clarification questions unless a conflict or new scope appears."
        )

    def _pm_prompt(self, session: Session, language: str) -> str:
        language = self._normalize_language(language)
        normalized = self._normalize_prompt_template(session.prompt_template)
        base_prompt = PM_SYSTEM_PROMPT_ZH if language == "zh" else PM_SYSTEM_PROMPT
        prompt_parts = [base_prompt]
        prompt_parts.append(self._readiness_phase_directive_for_prompt(session, language))
        prompt_parts.append(self._skill_style_ai_pm_method_prompt(language))
        methodology_state_addendum = self._pm_methodology_state_for_prompt(session, language)
        if methodology_state_addendum:
            prompt_parts.append(methodology_state_addendum)
        template_addendum = self._business_template_pm_addendum(session, language)
        if template_addendum:
            prompt_parts.append(template_addendum)
        elif normalized == PROMPT_TEMPLATE_PERSONAL_PROJECT:
            addendum = PERSONAL_PROJECT_PM_ADDENDUM_ZH_V2 if language == "zh" else PERSONAL_PROJECT_PM_ADDENDUM_V2
            prompt_parts.append(addendum)
            if self._session_matches_ic_substrate_expert_chain(session, language):
                prompt_parts.append(self._ic_substrate_conversation_chain_addendum(language))
        chain_state_addendum = self._conversation_chain_state_for_prompt(session, language)
        if chain_state_addendum:
            prompt_parts.append(chain_state_addendum)
        draft_completion_addendum = self._draft_completion_pm_addendum(session, language)
        if draft_completion_addendum:
            prompt_parts.append(draft_completion_addendum)
        prompt_parts.append(DEFAULT_TECH_STACK_POLICY_ZH if language == "zh" else DEFAULT_TECH_STACK_POLICY)
        prompt_parts.append(self._language_output_instruction(language))
        return "\n\n".join(part for part in prompt_parts if part)

    def _design_doc_prompt(self, session: Session, language: str) -> str:
        language = self._normalize_language(language)
        normalized = self._normalize_prompt_template(session.prompt_template)
        base_prompt = DESIGN_DOC_SYSTEM_PROMPT_ZH if language == "zh" else DESIGN_DOC_SYSTEM_PROMPT
        prompt_parts = [base_prompt]
        if session.applied_template_id:
            prompt_parts.append(
                "A business requirement template is active for this session.\n"
                "- Respect the template's domain, section priorities, and business framing.\n"
                "- Keep the design document aligned to the collected facts and the template context.\n"
                "- Do not treat this session as a generic personal-project interview."
            )
        elif normalized == PROMPT_TEMPLATE_PERSONAL_PROJECT:
            addendum = (
                PERSONAL_PROJECT_DESIGN_DOC_ADDENDUM_ZH_V2
                if language == "zh"
                else PERSONAL_PROJECT_DESIGN_DOC_ADDENDUM_V2
            )
            prompt_parts.append(addendum)
        prompt_parts.append(DEFAULT_TECH_STACK_POLICY_ZH if language == "zh" else DEFAULT_TECH_STACK_POLICY)
        prompt_parts.append(
            "Scaffold handling rules:\n"
            "- A design document scaffold will be provided in the user message.\n"
            "- Use that scaffold as the primary structure and preserve its section order.\n"
            "- Expand or rewrite section content only when it is supported by the conversation or the structured requirement model.\n"
            "- Keep unknown items explicitly marked as TBD; do not silently remove placeholders."
        )
        prompt_parts.append(self._language_output_instruction(language))
        return "\n\n".join(part for part in prompt_parts if part)

    def _prd_doc_prompt(self, session: Session, language: str) -> str:
        language = self._normalize_language(language)
        prompt_parts = [PRD_DOC_SYSTEM_PROMPT]
        if session.applied_template_id:
            prompt_parts.append(
                "A business requirement template is active for this session.\n"
                "- Use the applied template as the primary document structure instead of the generic simple PRD template.\n"
                "- Follow the template section order closely.\n"
                "- Keep missing facts marked as assumptions or open questions rather than inventing content."
            )
        prompt_parts.append(self._prd_skill_style_document_guidance(language))
        prompt_parts.append(self._ic_substrate_prd_document_contract(session, language))
        prompt_parts.append(self._language_output_instruction(language))
        return "\n\n".join(part for part in prompt_parts if part)

    def _build_implementation_prompt(
        self,
        session_id: str,
        session_title: str,
        prd_path: str,
        design_path: str,
        language: str,
        ic_substrate_evidence: dict[str, Any] | None = None,
    ) -> str:
        normalized = self._normalize_language(language)
        template = IMPLEMENTATION_PROMPT_TEMPLATE_BY_LANGUAGE.get(normalized, IMPLEMENTATION_PROMPT_TEMPLATE_EN)
        design_instruction = self._implementation_design_instruction(design_path, normalized)
        prompt = template.format(
            session_id=session_id,
            session_title=session_title or "Untitled Session",
            prd_path=prd_path,
            design_path=design_path,
            design_instruction=design_instruction,
        )
        if not ic_substrate_evidence:
            return prompt.strip()

        if normalized == "zh":
            evidence_note = (
                "IC Substrate 交接证据：\n"
                "- handoff payload 可能包含 `ic_substrate_evidence`，含 entry_owner、business_action、object_grain、workflow_state_owner、data_reconciliation、acceptance_evidence、uncertainty_handling 等就绪检查。\n"
                "- ready 项可作为实现证据；missing 项必须写入 README/ASSUMPTIONS/Open Questions。不要自造公式、站点、系统名、状态、SLA 或 owner。\n"
                "- 保留 source of truth 与集成/写回边界；未经业务 owner 与 IT 明确批准前，不要实现生产写回、自动化或 release/disposition 等动作。"
            )
        elif normalized == "de":
            evidence_note = (
                "IC Substrate handoff evidence:\n"
                "- The handoff payload may include `ic_substrate_evidence` with checks such as entry_owner, business_action, object_grain, workflow_state_owner, data_reconciliation, acceptance_evidence, and uncertainty_handling.\n"
                "- Treat ready checks as implementation evidence; put missing checks into README/ASSUMPTIONS/Open Questions. Do not invent formulas, stations, systems, states, SLAs, or owners.\n"
                "- Preserve the source of truth and integration/writeback boundary; do not implement production writeback, automation, or release/disposition actions until business owner and IT approval is explicit."
            )
        elif normalized == "ms":
            evidence_note = (
                "IC Substrate handoff evidence:\n"
                "- The handoff payload may include `ic_substrate_evidence` with checks such as entry_owner, business_action, object_grain, workflow_state_owner, data_reconciliation, acceptance_evidence, and uncertainty_handling.\n"
                "- Treat ready checks as implementation evidence; put missing checks into README/ASSUMPTIONS/Open Questions. Do not invent formulas, stations, systems, states, SLAs, or owners.\n"
                "- Preserve the source of truth and integration/writeback boundary; do not implement production writeback, automation, or release/disposition actions until business owner and IT approval is explicit."
            )
        else:
            evidence_note = (
                "IC Substrate handoff evidence:\n"
                "- The handoff payload may include `ic_substrate_evidence` with checks such as entry_owner, business_action, object_grain, workflow_state_owner, data_reconciliation, acceptance_evidence, and uncertainty_handling.\n"
                "- Treat ready checks as implementation evidence; put missing checks into README/ASSUMPTIONS/Open Questions. Do not invent formulas, stations, systems, states, SLAs, or owners.\n"
                "- Preserve the source of truth and integration/writeback boundary; do not implement production writeback, automation, or release/disposition actions until business owner and IT approval is explicit."
            )
        return f"{prompt}\n\n{evidence_note}".strip()

    def _implementation_design_instruction(self, design_path: str, language: str) -> str:
        if design_path:
            if language == "zh":
                return f"2. 系统设计文档：{design_path}"
            if language == "de":
                return f"2. Systemdesign-Dokument: {design_path}"
            if language == "ms":
                return f"2. Dokumen reka bentuk sistem: {design_path}"
            return f"2. System design document: {design_path}"
        if language == "zh":
            return (
                "2. 暂无系统设计文档。No system design document is available yet；请以需求文档为唯一产品依据，"
                "选择最小可运行技术方案，并把架构、数据模型、接口、字段和剩余技术假设写入 README 或 ASSUMPTIONS.md。"
            )
        if language == "de":
            return (
                "2. No system design document is available yet. Nutze das Requirement-Dokument als einzige Produktquelle, "
                "waehle die kleinste lauffaehige technische Loesung und dokumentiere Architektur, Datenmodell, APIs, Felder und technische Annahmen in README oder ASSUMPTIONS.md."
            )
        if language == "ms":
            return (
                "2. No system design document is available yet. Gunakan dokumen keperluan sebagai satu-satunya sumber produk, "
                "pilih penyelesaian teknikal paling kecil yang boleh berjalan, dan rekod seni bina, model data, API, field serta andaian teknikal dalam README atau ASSUMPTIONS.md."
            )
        return (
            "2. No system design document is available yet. Use the requirements document as the only product source of truth, "
            "choose the smallest runnable technical approach, and record architecture, data model, APIs, fields, and remaining technical assumptions in README or ASSUMPTIONS.md."
        )

    def _normalize_language(self, language: str | None) -> str:
        normalized = str(language or "").strip().lower()
        if normalized in SUPPORTED_OUTPUT_LANGUAGES:
            return normalized
        return "zh"

    def _language_for_user_message(self, language: str | None, user_message: str) -> str:
        _ = user_message
        return self._normalize_language(language)

    def _parse_datetime(self, raw_value: Any) -> datetime | None:
        try:
            parsed = datetime.fromisoformat(str(raw_value))
        except (TypeError, ValueError):
            return None
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed

    def _language_output_instruction(self, language: str) -> str:
        normalized = self._normalize_language(language)
        return OUTPUT_LANGUAGE_INSTRUCTIONS.get(normalized, OUTPUT_LANGUAGE_INSTRUCTIONS["en"])

    def _ensure_choice_question_format(self, text: str, language: str) -> str:
        stripped = text.strip()
        if not stripped:
            return stripped
        if not self._looks_like_clarification_question(stripped, language):
            return stripped
        if self._has_choice_options(stripped):
            return stripped
        return f"{stripped}\n\n{self._fallback_choice_block(language)}"

    def _looks_like_clarification_question(self, text: str, language: str) -> bool:
        normalized = self._normalize_language(language)
        if text.rstrip().endswith(("?", "？")):
            return True
        lowered = text.lower()
        if normalized == "zh":
            return bool(re.search(r"(请确认|是否|是不是|能否|要不要|你希望|你们希望|按.*口径|这个口径)", text))
        if normalized == "de":
            return bool(re.search(r"\b(bitte bestaetigen|bestaetigen|welche|welcher|welches|soll|koennen sie)\b", lowered))
        if normalized == "ms":
            return bool(re.search(r"\b(sila sahkan|adakah|bolehkah|yang mana|patut|anda mahu)\b", lowered))
        return bool(
            re.search(
                r"\b(please confirm|confirm|which|what|do you|does this|should we|would you|can you|could you)\b",
                lowered,
            )
        )

    def _has_choice_options(self, text: str) -> bool:
        option_matches = re.findall(
            r"(?im)(?:^|\n|\s)(?:[A-DＡ-Ｄ][\.\)\]、：:]|选项\s*[A-DＡ-Ｄ]|Option\s*[A-D])\s+",
            text,
        )
        return len(option_matches) >= 2

    def _fallback_choice_block(self, language: str) -> str:
        normalized = self._normalize_language(language)
        if normalized == "zh":
            return (
                "为了继续推进，我先给三个选项：\n"
                "A. 先按一个可落地的 v1 假设推进\n"
                "B. 我补充真实业务口径或例外情况\n"
                "C. 这个点先保持待确认"
            )
        if normalized == "de":
            return (
                "Zum Weiterkommen schlage ich drei Optionen vor:\n"
                "A. Mit einer praktikablen V1-Annahme fortfahren\n"
                "B. Ich ergaenze die echte Fachdefinition oder Ausnahme\n"
                "C. Diesen Punkt vorerst offen lassen"
            )
        if normalized == "ms":
            return (
                "Untuk teruskan, saya cadangkan tiga pilihan:\n"
                "A. Teruskan dengan andaian v1 yang praktikal\n"
                "B. Saya tambah definisi bisnes sebenar atau pengecualian\n"
                "C. Kekalkan perkara ini sebagai belum disahkan"
            )
        return (
            "To keep moving, choose one option:\n"
            "A. Use a practical v1 assumption and continue\n"
            "B. I will provide the exact wording or an exception\n"
            "C. Leave this pending for now"
        )

    def _normalize_start_function(self, start_function: str | None) -> str:
        normalized = str(start_function or START_FUNCTION_FROM_SCRATCH).strip().lower()
        if normalized in START_FUNCTION_VALUES:
            return normalized
        raise ValueError(
            f"Unsupported start_function `{start_function}`. "
            f"Supported: {', '.join(sorted(START_FUNCTION_VALUES))}."
        )

    def _draft_completion_pm_addendum(self, session: Session, language: str | None = None) -> str:
        if session.start_function != START_FUNCTION_IMPROVE_DRAFT:
            return ""

        normalized_language = self._normalize_language(language)
        if normalized_language == "zh":
            return (
                "半成品需求书完善模式：\n"
                "- 用户不是从零开始，而是上传或粘贴了半成品需求书；先利用附件和对话里已有内容，不要重复询问已经明确的信息。\n"
                "- 每次回复先简短归纳：已明确、推断但待确认、缺失、冲突。只保留和 PRD 质量有关的高信号内容。\n"
                "- 下一问只追一个最影响 PRD 产出质量的缺口，优先级为：业务目标/范围、使用者与 owner、核心场景、业务规则、数据源/口径、流程状态、验收标准、out-of-scope。\n"
                "- Draft completion：不要引入快速半成品文档概念；用附件 + 专家链路补齐最关键缺口。只有 structured requirement ready_to_generate=true 时，才提示生成文档；文档生成/确认 OK 后，Go Coding 才能把文档交接给 Vibe Coding 平台。\n"
                "- 附件推断永远是待确认，不得写成已确认事实；如果附件与用户口径冲突，直接指出冲突并请用户确认一个版本。\n"
                "- 对 Production/Quality/TDI 仍使用对应专家链路，但问题必须围绕补齐 draft 缺口，而不是重新做流程审计。\n"
                "- 最后一段必须给 A/B/C 选项，帮助用户快速确认、修正或暂存该缺口。"
            )
        if normalized_language == "de":
            return (
                "Draft-Completion-Modus:\n"
                "- Der Nutzer startet nicht bei null, sondern verbessert einen vorhandenen Requirement-Draft; nutze vorhandene Anhangs- und Dialoginhalte und frage klare Punkte nicht erneut.\n"
                "- Jede Antwort fasst kurz zusammen: bestaetigt, abgeleitet aber zu bestaetigen, fehlend, Konflikt.\n"
                "- Die naechste Frage schliesst genau die eine Luecke, die die PRD-Qualitaet am meisten blockiert: Ziel/Scope, Nutzer/Owner, Kernscenario, Regel, Datenquelle/Definition, Workflow-State, Acceptance oder Out-of-scope.\n"
                "- Draft completion: kein fruehes Teildokument versprechen; nutze Anhang + Expertenkette, um die wichtigste Luecke zu schliessen. Bei structured requirement ready_to_generate=true zuerst Dokumente erzeugen; Go Coding uebergibt erst danach an Vibe Coding.\n"
                "- Anhangsableitungen sind immer pending confirmation, nie bestaetigte Fakten.\n"
                "- Fuer Production/Quality/TDI bleibt die Expertenkette aktiv, aber sie dient der Draft-Lueckenschliessung statt einer neuen Prozessauditierung.\n"
                "- Der letzte Absatz muss A/B/C Optionen zur schnellen Bestaetigung, Korrektur oder Pending-Markierung enthalten."
            )
        if normalized_language == "ms":
            return (
                "Mod melengkapkan draft requirement:\n"
                "- Pengguna bukan bermula dari kosong; gunakan kandungan lampiran dan perbualan sedia ada, jangan tanya semula perkara yang sudah jelas.\n"
                "- Setiap jawapan ringkaskan secara pendek: sudah jelas, inferens perlu disahkan, masih kurang, konflik.\n"
                "- Soalan seterusnya hanya menutup satu gap yang paling menghalang kualiti PRD: business goal/scope, user/owner, core scenario, business rule, data source/definition, workflow state, acceptance atau out-of-scope.\n"
                "- Draft completion: jangan janji dokumen separuh siap awal; gunakan lampiran + expert chain untuk menutup gap paling penting. Jika structured requirement ready_to_generate=true, jana dokumen dahulu; Go Coding hanya handoff dokumen itu ke Vibe Coding selepas dokumen OK.\n"
                "- Inferens daripada lampiran sentiasa pending confirmation, bukan fakta sah.\n"
                "- Untuk Production/Quality/TDI, kekalkan expert chain tetapi fokus pada melengkapkan gap draft, bukan audit proses baharu.\n"
                "- Perenggan akhir mesti ada pilihan A/B/C untuk sahkan, betulkan atau simpan pending."
            )
        return (
            "Draft completion mode:\n"
            "- The user is not starting from scratch; they are improving an existing draft requirement. Use attachment and conversation content first, and do not re-ask facts already present.\n"
            "- In each reply, briefly separate: confirmed, inferred but pending confirmation, missing, and conflicts. Keep only PRD-quality-relevant signal.\n"
            "- Ask exactly one next question that closes the biggest PRD-quality gap: business goal/scope, user/owner, core scenario, business rule, data source/definition, workflow state, acceptance criteria, or out-of-scope.\n"
            "- Draft completion: do not promise an early partial document; use the attachment plus expert chain to close the biggest gap. Once structured requirement ready_to_generate=true, generate documents first; Go Coding only hands that generated/approved document package to Vibe Coding.\n"
            "- Attachment-derived content is pending confirmation, never confirmed fact. If it conflicts with the user's wording, name the conflict and ask which version wins.\n"
            "- Production/Quality/TDI expert chains still apply, but use them to close draft gaps instead of restarting a process audit.\n"
            "- The final paragraph must include A/B/C options so the user can confirm, correct, or keep the gap pending."
        )

    def _normalize_prompt_template(self, prompt_template: str | None) -> str:
        normalized = str(prompt_template or "").strip().lower()
        if normalized == PROMPT_TEMPLATE_STANDARD:
            return PROMPT_TEMPLATE_STANDARD
        return PROMPT_TEMPLATE_PERSONAL_PROJECT

    def _default_prd_doc(self, language: str) -> str:
        language = self._normalize_language(language)
        return PRD_EMPTY_BY_LANGUAGE.get(language, PRD_EMPTY_BY_LANGUAGE["en"])

    def _build_generated_document_result(
        self,
        session_id: str,
        document_kind: str,
        language: str,
        doc_markdown: str,
        structured_requirement_model: dict[str, Any],
        status: str,
        save_history: bool,
    ) -> dict[str, Any]:
        if status == "quality_gate_blocked":
            persisted = {
                "filename": "",
                "download_url": "",
                "saved_at": datetime.now(timezone.utc).isoformat(),
            }
        elif save_history:
            persisted = self._persist_generated_document(
                session_id=session_id,
                document_kind=document_kind,
                language=language,
                doc_markdown=doc_markdown,
            )
        else:
            persisted = self._save_generated_document_snapshot(
                session_id=session_id,
                document_kind=document_kind,
                language=language,
                doc_markdown=doc_markdown,
            )

        return {
            "session_id": session_id,
            "document_markdown": doc_markdown,
            "document_type": DOCUMENT_TYPE_BY_MESSAGE_KIND[document_kind],
            "filename": persisted["filename"],
            "download_url": persisted["download_url"],
            "saved_at": persisted["saved_at"],
            "summary": structured_requirement_model,
            "structured_requirement_model": structured_requirement_model,
            "status": status,
            "prd_v0_ready": False,
        }

    def _persist_generated_document(
        self,
        session_id: str,
        document_kind: str,
        language: str,
        doc_markdown: str,
    ) -> dict[str, Any]:
        created_at = datetime.now(timezone.utc)
        file_path, download_filename = self._write_generated_document_files(
            session_id=session_id,
            document_kind=document_kind,
            language=language,
            doc_markdown=doc_markdown,
            created_at=created_at,
        )
        message_id = self._append_message(
            session_id=session_id,
            role="assistant",
            content=doc_markdown,
            kind=document_kind,
            download_filename=download_filename,
            storage_path=str(file_path),
            created_at=created_at.isoformat(),
        )
        return {
            "message_id": message_id,
            "filename": download_filename,
            "download_url": self._document_download_url(session_id, message_id),
            "saved_at": created_at.isoformat(),
        }

    def _save_generated_document_snapshot(
        self,
        session_id: str,
        document_kind: str,
        language: str,
        doc_markdown: str,
    ) -> dict[str, str]:
        created_at = datetime.now(timezone.utc)
        _, download_filename = self._write_generated_document_files(
            session_id=session_id,
            document_kind=document_kind,
            language=language,
            doc_markdown=doc_markdown,
            created_at=created_at,
        )
        return {
            "filename": download_filename,
            "download_url": self._legacy_document_download_url(session_id, document_kind),
            "saved_at": created_at.isoformat(),
        }

    def _write_generated_document_files(
        self,
        session_id: str,
        document_kind: str,
        language: str,
        doc_markdown: str,
        created_at: datetime,
    ) -> tuple[Path, str]:
        directory = self._document_directory(document_kind)
        directory.mkdir(parents=True, exist_ok=True)
        download_filename = self._build_document_download_filename(
            document_kind,
            language,
            created_at,
            doc_markdown,
        )
        versioned_path = (directory / download_filename).resolve()
        versioned_path.write_text(doc_markdown, encoding="utf-8")
        self._latest_document_path(session_id, document_kind).write_text(doc_markdown, encoding="utf-8")
        return versioned_path, download_filename

    def _document_directory(self, document_kind: str) -> Path:
        if document_kind == PRD_MESSAGE_KIND:
            return self.prd_docs_dir
        return self.design_docs_dir

    def _latest_document_path(self, session_id: str, document_kind: str) -> Path:
        if document_kind == PRD_MESSAGE_KIND:
            return self._prd_doc_path(session_id)
        return self._design_doc_path(session_id)

    def _design_doc_path(self, session_id: str) -> Path:
        return self.design_docs_dir / f"{session_id}.md"

    def _prd_doc_path(self, session_id: str) -> Path:
        return self.prd_docs_dir / f"{session_id}.md"

    def _build_document_download_filename(
        self,
        document_kind: str,
        language: str,
        created_at: datetime,
        doc_markdown: str = "",
    ) -> str:
        normalized_language = self._normalize_language(language)
        document_label = DOCUMENT_FILENAME_LABELS.get(document_kind, DOCUMENT_FILENAME_LABELS[DESIGN_MESSAGE_KIND]).get(
            normalized_language,
            DOCUMENT_FILENAME_LABELS[document_kind]["en"],
        )
        timestamp = created_at.strftime("%Y%m%d-%H%M%S-%f")
        return f"{document_label}-{timestamp}.md"

    def _markdown_to_docx_bytes(self, markdown: str) -> bytes:
        numbering_state = {"next_ordered_num_id": DOCX_ORDERED_NUM_ID_START}
        body_parts = self._markdown_to_docx_body(markdown, numbering_state)
        document_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            "<w:body>"
            + "".join(body_parts)
            + (
                "<w:sectPr>"
                f'<w:pgSz w:w="{DOCX_PAGE_WIDTH_DXA}" w:h="{DOCX_PAGE_HEIGHT_DXA}"/>'
                f'<w:pgMar w:top="{DOCX_PAGE_MARGIN_DXA}" w:right="{DOCX_PAGE_MARGIN_DXA}" '
                f'w:bottom="{DOCX_PAGE_MARGIN_DXA}" w:left="{DOCX_PAGE_MARGIN_DXA}" '
                'w:header="708" w:footer="708" w:gutter="0"/>'
                "</w:sectPr>"
            )
            + "</w:body></w:document>"
        )
        content_types_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/word/document.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
            '<Override PartName="/word/styles.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
            '<Override PartName="/word/numbering.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>'
            "</Types>"
        )
        rels_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
            'Target="word/document.xml"/>'
            "</Relationships>"
        )
        document_rels_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" '
            'Target="styles.xml"/>'
            '<Relationship Id="rId2" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" '
            'Target="numbering.xml"/>'
            "</Relationships>"
        )

        buffer = BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("[Content_Types].xml", content_types_xml)
            archive.writestr("_rels/.rels", rels_xml)
            archive.writestr("word/_rels/document.xml.rels", document_rels_xml)
            archive.writestr("word/document.xml", document_xml)
            archive.writestr("word/styles.xml", self._docx_styles_xml())
            archive.writestr(
                "word/numbering.xml",
                self._docx_numbering_xml(numbering_state["next_ordered_num_id"]),
            )
        return buffer.getvalue()

    def _markdown_to_docx_body(self, markdown: str, numbering_state: dict[str, int]) -> list[str]:
        markdown = self._plain_text_math_for_docx(markdown)
        lines = markdown.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        body_parts: list[str] = []
        index = 0
        active_list_type = ""
        active_ordered_num_id = 0

        while index < len(lines):
            raw_line = lines[index]
            line = raw_line.rstrip()
            stripped = line.strip()
            if not stripped:
                body_parts.append(self._docx_paragraph(""))
                active_list_type = ""
                active_ordered_num_id = 0
                index += 1
                continue

            fence_match = re.match(r"^\s*```([\w-]*)\s*$", line)
            if fence_match:
                active_list_type = ""
                active_ordered_num_id = 0
                language = fence_match.group(1).strip().lower()
                code_lines: list[str] = []
                index += 1
                while index < len(lines) and not re.match(r"^\s*```\s*$", lines[index]):
                    code_lines.append(lines[index])
                    index += 1
                if index < len(lines):
                    index += 1
                if language == "mermaid":
                    body_parts.append(self._docx_paragraph("Mermaid diagram source:", bold=True))
                for code_line in code_lines or [""]:
                    body_parts.append(self._docx_paragraph(code_line, code=True))
                continue

            if re.match(r"^\s*([-*_])(?:\s*\1){2,}\s*$", line):
                body_parts.append(self._docx_horizontal_rule())
                active_list_type = ""
                active_ordered_num_id = 0
                index += 1
                continue

            heading_match = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)
            if heading_match:
                level = min(len(heading_match.group(1)), 6)
                body_parts.append(self._docx_paragraph(heading_match.group(2), heading_level=level))
                active_list_type = ""
                active_ordered_num_id = 0
                index += 1
                continue

            if self._is_markdown_table_start(lines, index):
                table_rows, next_index = self._collect_markdown_table(lines, index)
                body_parts.append(self._docx_table(table_rows))
                active_list_type = ""
                active_ordered_num_id = 0
                index = next_index
                continue

            unordered_match = re.match(r"^(\s*)[-*+]\s+(.+)$", line)
            ordered_match = re.match(r"^(\s*)(\d+)[.)]\s+(.+)$", line)
            if unordered_match:
                level = self._docx_list_level(unordered_match.group(1))
                body_parts.append(
                    self._docx_paragraph(
                        unordered_match.group(2),
                        numbering_id=DOCX_BULLET_NUM_ID,
                        numbering_level=level,
                    )
                )
                active_list_type = "unordered"
                active_ordered_num_id = 0
                index += 1
                continue
            if ordered_match:
                level = self._docx_list_level(ordered_match.group(1))
                if active_list_type != "ordered" or active_ordered_num_id <= 0:
                    active_ordered_num_id = numbering_state["next_ordered_num_id"]
                    numbering_state["next_ordered_num_id"] += 1
                body_parts.append(
                    self._docx_paragraph(
                        ordered_match.group(3),
                        numbering_id=active_ordered_num_id,
                        numbering_level=level,
                    )
                )
                active_list_type = "ordered"
                index += 1
                continue

            quote_match = re.match(r"^\s*>\s?(.*)$", line)
            if quote_match:
                body_parts.append(self._docx_paragraph(quote_match.group(1), italic=True))
                active_list_type = ""
                active_ordered_num_id = 0
                index += 1
                continue

            body_parts.append(self._docx_paragraph(stripped))
            active_list_type = ""
            active_ordered_num_id = 0
            index += 1

        return body_parts

    def _plain_text_math_for_docx(self, markdown: str) -> str:
        text = markdown
        text = re.sub(
            r"\$\$([\s\S]*?)\$\$",
            lambda match: "\n" + self._latex_to_plain_formula(match.group(1)) + "\n",
            text,
        )
        text = re.sub(
            r"\\\[([\s\S]*?)\\\]",
            lambda match: "\n" + self._latex_to_plain_formula(match.group(1)) + "\n",
            text,
        )
        text = re.sub(
            r"\\\(([\s\S]*?)\\\)",
            lambda match: self._latex_to_plain_formula(match.group(1)),
            text,
        )
        return text

    def _latex_to_plain_formula(self, formula: str) -> str:
        normalized = " ".join(formula.replace("\n", " ").split())
        normalized = re.sub(r"\\text\s*\{([^{}]*)\}", r"\1", normalized)
        normalized = re.sub(r"\\mathrm\s*\{([^{}]*)\}", r"\1", normalized)

        def replace_frac(match: re.Match[str]) -> str:
            numerator = self._latex_to_plain_formula(match.group(1))
            denominator = self._latex_to_plain_formula(match.group(2))
            return f"({numerator}) / ({denominator})"

        previous = None
        while previous != normalized:
            previous = normalized
            normalized = re.sub(r"\\frac\s*\{([^{}]*)\}\s*\{([^{}]*)\}", replace_frac, normalized)

        normalized = normalized.replace("\\times", "x")
        normalized = normalized.replace("\\cdot", "*")
        normalized = normalized.replace("\\%", "%")
        normalized = normalized.replace("\\_", "_")
        normalized = normalized.replace("\\&", "&")
        normalized = re.sub(r"\\[a-zA-Z]+", "", normalized)
        normalized = normalized.replace("{", "").replace("}", "")
        normalized = re.sub(r"\s+", " ", normalized).strip()
        normalized = re.sub(r"\s*([=+*/()x-])\s*", r" \1 ", normalized)
        normalized = re.sub(r"\s+", " ", normalized).strip()
        return normalized

    def _docx_paragraph(
        self,
        text: str,
        *,
        heading_level: int = 0,
        bold: bool = False,
        italic: bool = False,
        code: bool = False,
        numbering_id: int = 0,
        numbering_level: int = 0,
    ) -> str:
        paragraph_props = ""
        if heading_level:
            paragraph_props = (
                "<w:pPr>"
                f'<w:pStyle w:val="Heading{heading_level}"/>'
                f'<w:outlineLvl w:val="{heading_level - 1}"/>'
                "</w:pPr>"
            )
            return (
                "<w:p>"
                + paragraph_props
                + self._docx_run(text)
                + "</w:p>"
            )

        run_props = ""
        paragraph_props = self._docx_paragraph_props(numbering_id, numbering_level)
        if code:
            run_props = '<w:rPr><w:rFonts w:ascii="Courier New" w:hAnsi="Courier New"/><w:sz w:val="18"/></w:rPr>'
        runs = self._docx_inline_runs(text, bold=bold, italic=italic, run_props=run_props)
        return f"<w:p>{paragraph_props}{runs}</w:p>"

    def _docx_paragraph_props(self, numbering_id: int = 0, numbering_level: int = 0) -> str:
        if numbering_id <= 0:
            return ""
        return (
            "<w:pPr>"
            "<w:numPr>"
            f'<w:ilvl w:val="{max(0, numbering_level)}"/>'
            f'<w:numId w:val="{numbering_id}"/>'
            "</w:numPr>"
            "</w:pPr>"
        )

    def _docx_horizontal_rule(self) -> str:
        return (
            "<w:p>"
            "<w:pPr>"
            "<w:pBdr>"
            '<w:bottom w:val="single" w:sz="6" w:space="1" w:color="B7C4D8"/>'
            "</w:pBdr>"
            '<w:spacing w:before="120" w:after="160"/>'
            "</w:pPr>"
            "</w:p>"
        )

    def _docx_list_level(self, leading_whitespace: str) -> int:
        expanded = leading_whitespace.replace("\t", "    ")
        return min(len(expanded) // 2, 2)

    def _docx_inline_runs(self, text: str, *, bold: bool = False, italic: bool = False, run_props: str = "") -> str:
        if run_props:
            return self._docx_run(text, raw_props=run_props)

        parts: list[str] = []
        pattern = re.compile(r"(`[^`]+`|\*\*[^*]+\*\*)")
        position = 0
        for match in pattern.finditer(text):
            if match.start() > position:
                parts.append(self._docx_run(text[position : match.start()], bold=bold, italic=italic))
            token = match.group(0)
            if token.startswith("`"):
                parts.append(
                    self._docx_run(
                        token[1:-1],
                        raw_props='<w:rPr><w:rFonts w:ascii="Courier New" w:hAnsi="Courier New"/></w:rPr>',
                    )
                )
            else:
                parts.append(self._docx_run(token[2:-2], bold=True, italic=italic))
            position = match.end()
        if position < len(text):
            parts.append(self._docx_run(text[position:], bold=bold, italic=italic))
        return "".join(parts) or self._docx_run("")

    def _docx_run(
        self,
        text: str,
        *,
        bold: bool = False,
        italic: bool = False,
        size: int = 0,
        raw_props: str = "",
    ) -> str:
        props = raw_props
        if not props and (bold or italic or size):
            prop_parts = ["<w:rPr>"]
            if bold:
                prop_parts.append("<w:b/>")
            if italic:
                prop_parts.append("<w:i/>")
            if size:
                prop_parts.append(f'<w:sz w:val="{size}"/>')
            prop_parts.append("</w:rPr>")
            props = "".join(prop_parts)
        return f'<w:r>{props}<w:t xml:space="preserve">{escape(text)}</w:t></w:r>'

    def _is_markdown_table_start(self, lines: list[str], index: int) -> bool:
        if index + 1 >= len(lines):
            return False
        header = lines[index]
        divider = lines[index + 1]
        return "|" in header and bool(re.match(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$", divider))

    def _collect_markdown_table(self, lines: list[str], index: int) -> tuple[list[list[str]], int]:
        rows = [self._split_markdown_table_row(lines[index])]
        index += 2
        while index < len(lines) and "|" in lines[index] and lines[index].strip():
            rows.append(self._split_markdown_table_row(lines[index]))
            index += 1
        return rows, index

    def _split_markdown_table_row(self, line: str) -> list[str]:
        return [
            cell.strip()
            for cell in line.strip().strip("|").split("|")
        ]

    def _docx_table(self, rows: list[list[str]]) -> str:
        if not rows:
            return self._docx_paragraph("")
        column_count = max(len(row) for row in rows)
        if column_count <= 0:
            return self._docx_paragraph("")
        normalized_rows = [row + [""] * (column_count - len(row)) for row in rows]
        column_widths = self._docx_table_column_widths(column_count)
        border_xml = (
            '<w:top w:val="single" w:sz="4" w:space="0" w:color="D9E2F3"/>'
            '<w:left w:val="single" w:sz="4" w:space="0" w:color="D9E2F3"/>'
            '<w:bottom w:val="single" w:sz="4" w:space="0" w:color="D9E2F3"/>'
            '<w:right w:val="single" w:sz="4" w:space="0" w:color="D9E2F3"/>'
            '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="D9E2F3"/>'
            '<w:insideV w:val="single" w:sz="4" w:space="0" w:color="D9E2F3"/>'
        )
        table_parts = [
            "<w:tbl>",
            (
                "<w:tblPr>"
                f'<w:tblW w:w="{DOCX_CONTENT_WIDTH_DXA}" w:type="dxa"/>'
                "<w:tblBorders>"
                + border_xml
                + "</w:tblBorders>"
                '<w:tblLook w:firstRow="1" w:lastRow="0" w:firstColumn="0" w:lastColumn="0" '
                'w:noHBand="0" w:noVBand="1"/>'
                "</w:tblPr>"
            ),
            "<w:tblGrid>",
            "".join(f'<w:gridCol w:w="{width}"/>' for width in column_widths),
            "</w:tblGrid>",
        ]
        for row_index, row in enumerate(normalized_rows):
            table_parts.append("<w:tr>")
            for column_index, cell in enumerate(row):
                width = column_widths[column_index]
                shading = '<w:shd w:val="clear" w:color="auto" w:fill="EAF2FF"/>' if row_index == 0 else ""
                table_parts.append(
                    "<w:tc>"
                    f'<w:tcPr><w:tcW w:w="{width}" w:type="dxa"/>'
                    + '<w:tcMar><w:top w:w="80" w:type="dxa"/><w:left w:w="120" w:type="dxa"/>'
                    + '<w:bottom w:w="80" w:type="dxa"/><w:right w:w="120" w:type="dxa"/></w:tcMar>'
                    + shading
                    + "</w:tcPr>"
                    + self._docx_paragraph(cell, bold=row_index == 0)
                    + "</w:tc>"
                )
            table_parts.append("</w:tr>")
        table_parts.append("</w:tbl>")
        return "".join(table_parts)

    def _docx_table_column_widths(self, column_count: int) -> list[int]:
        base_width = DOCX_CONTENT_WIDTH_DXA // column_count
        widths = [base_width] * column_count
        widths[-1] += DOCX_CONTENT_WIDTH_DXA - sum(widths)
        return widths

    def _docx_styles_xml(self) -> str:
        heading_styles = []
        heading_sizes = {1: 32, 2: 28, 3: 25, 4: 23, 5: 22, 6: 21}
        for level in range(1, 7):
            heading_styles.append(
                f'<w:style w:type="paragraph" w:styleId="Heading{level}">'
                f'<w:name w:val="heading {level}"/>'
                '<w:basedOn w:val="Normal"/>'
                '<w:next w:val="Normal"/>'
                '<w:qFormat/>'
                f'<w:pPr><w:keepNext/><w:spacing w:before="{240 if level <= 2 else 180}" '
                f'w:after="{160 if level <= 2 else 100}"/>'
                f'<w:outlineLvl w:val="{level - 1}"/></w:pPr>'
                '<w:rPr><w:b/>'
                f'<w:sz w:val="{heading_sizes[level]}"/>'
                '<w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="Microsoft YaHei"/>'
                "</w:rPr>"
                "</w:style>"
            )
        return (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            "<w:docDefaults>"
            "<w:rPrDefault><w:rPr>"
            '<w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="Microsoft YaHei"/>'
            '<w:sz w:val="22"/>'
            '<w:lang w:val="en-US" w:eastAsia="zh-CN"/>'
            "</w:rPr></w:rPrDefault>"
            '<w:pPrDefault><w:pPr><w:spacing w:after="120"/></w:pPr></w:pPrDefault>'
            "</w:docDefaults>"
            '<w:style w:type="paragraph" w:default="1" w:styleId="Normal">'
            '<w:name w:val="Normal"/>'
            '<w:qFormat/>'
            "</w:style>"
            + "".join(heading_styles)
            + "</w:styles>"
        )

    def _docx_numbering_xml(self, next_ordered_num_id: int) -> str:
        ordered_nums = []
        for num_id in range(DOCX_ORDERED_NUM_ID_START, max(next_ordered_num_id, DOCX_ORDERED_NUM_ID_START)):
            ordered_nums.append(
                f'<w:num w:numId="{num_id}"><w:abstractNumId w:val="2"/></w:num>'
            )
        return (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:numbering xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            '<w:abstractNum w:abstractNumId="1">'
            '<w:multiLevelType w:val="hybridMultilevel"/>'
            + self._docx_numbering_levels("bullet")
            + "</w:abstractNum>"
            '<w:abstractNum w:abstractNumId="2">'
            '<w:multiLevelType w:val="hybridMultilevel"/>'
            + self._docx_numbering_levels("decimal")
            + "</w:abstractNum>"
            f'<w:num w:numId="{DOCX_BULLET_NUM_ID}"><w:abstractNumId w:val="1"/></w:num>'
            + "".join(ordered_nums)
            + "</w:numbering>"
        )

    def _docx_numbering_levels(self, number_format: str) -> str:
        levels = []
        for level in range(3):
            left = 720 + (level * 360)
            if number_format == "bullet":
                levels.append(
                    f'<w:lvl w:ilvl="{level}">'
                    '<w:start w:val="1"/>'
                    '<w:numFmt w:val="bullet"/>'
                    '<w:lvlText w:val="•"/>'
                    '<w:lvlJc w:val="left"/>'
                    f'<w:pPr><w:ind w:left="{left}" w:hanging="360"/></w:pPr>'
                    '<w:rPr><w:rFonts w:ascii="Symbol" w:hAnsi="Symbol"/></w:rPr>'
                    "</w:lvl>"
                )
            else:
                levels.append(
                    f'<w:lvl w:ilvl="{level}">'
                    '<w:start w:val="1"/>'
                    '<w:numFmt w:val="decimal"/>'
                    '<w:lvlText w:val="%1."/>'
                    '<w:lvlJc w:val="left"/>'
                    f'<w:pPr><w:ind w:left="{left}" w:hanging="360"/></w:pPr>'
                    "</w:lvl>"
                )
        return "".join(levels)

    def _safe_parse_structured_requirement_model(self, raw_model: str) -> dict[str, Any]:
        parsed = self._parse_json_from_model_output(raw_model)
        if parsed is None:
            fallback = self._empty_structured_requirement_model()
            # Strip <think> blocks before echoing raw LLM output back into the model.
            # Otherwise model reasoning leaks into open_questions and then into the PRD.
            safe_raw, _ = self._split_thinking(raw_model or "")
            safe_raw = safe_raw.strip() or "<no parseable content>"
            fallback["open_questions"] = [f"Structured requirement parse failed. Raw output: {safe_raw}"]
            return fallback

        return normalize_structured_requirement_model(parsed)

    def _split_thinking(self, text: str) -> tuple[str, str]:
        think_regex = re.compile(r"<think>([\s\S]*?)</think>", re.IGNORECASE)
        thinking_parts = [chunk.strip() for chunk in think_regex.findall(text) if chunk.strip()]
        cleaned = think_regex.sub("", text).strip()
        return cleaned, "\n\n".join(thinking_parts)

    def _parse_json_from_model_output(self, raw: str) -> dict[str, Any] | None:
        if not raw:
            return None

        cleaned, _ = self._split_thinking(raw)
        candidates = [cleaned]

        fenced = re.findall(r"```(?:json)?\s*([\s\S]*?)```", cleaned, flags=re.IGNORECASE)
        candidates.extend(fenced)
        for candidate in list(candidates):
            candidates.extend(self._json_candidate_variants(candidate))

        for candidate in candidates:
            obj = self._try_load_first_json_object(candidate)
            if obj is not None:
                return obj
        return None

    def _json_candidate_variants(self, text: str) -> list[str]:
        return [self._remove_json_trailing_commas(text)]

    def _remove_json_trailing_commas(self, text: str) -> str:
        cleaned = text.strip().lstrip("\ufeff")
        if not cleaned:
            return cleaned

        result: list[str] = []
        in_string = False
        escaped = False
        index = 0
        while index < len(cleaned):
            ch = cleaned[index]
            if in_string:
                result.append(ch)
                if escaped:
                    escaped = False
                elif ch == "\\":
                    escaped = True
                elif ch == '"':
                    in_string = False
                index += 1
                continue

            if ch == '"':
                in_string = True
                result.append(ch)
                index += 1
                continue

            if ch == ",":
                lookahead = index + 1
                while lookahead < len(cleaned) and cleaned[lookahead].isspace():
                    lookahead += 1
                if lookahead < len(cleaned) and cleaned[lookahead] in "}]":
                    index += 1
                    continue

            result.append(ch)
            index += 1
        return "".join(result)

    def _try_load_first_json_object(self, text: str) -> dict[str, Any] | None:
        stripped = text.strip()
        if not stripped:
            return None

        # First, try whole text directly.
        try:
            parsed = json.loads(stripped)
            return parsed if isinstance(parsed, dict) else None
        except json.JSONDecodeError:
            pass

        # Then, scan for the first balanced JSON object.
        start = stripped.find("{")
        while start != -1:
            depth = 0
            in_string = False
            escaped = False
            for i in range(start, len(stripped)):
                ch = stripped[i]
                if in_string:
                    if escaped:
                        escaped = False
                    elif ch == "\\":
                        escaped = True
                    elif ch == '"':
                        in_string = False
                    continue
                if ch == '"':
                    in_string = True
                elif ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        snippet = stripped[start : i + 1]
                        try:
                            parsed = json.loads(snippet)
                            return parsed if isinstance(parsed, dict) else None
                        except json.JSONDecodeError:
                            break
            start = stripped.find("{", start + 1)
        return None

    def _empty_structured_requirement_model(self) -> dict[str, Any]:
        return empty_structured_requirement_model()

    def _build_prd_doc_messages(
        self,
        session: Session,
        messages: list[dict[str, Any]],
        structured_requirement_model: dict[str, Any],
        progress: dict[str, Any],
        language: str,
    ) -> list[dict[str, str]]:
        language = self._normalize_language(language)
        content_label = CONVERSATION_LABELS.get(language, CONVERSATION_LABELS["en"])
        summary_label = SUMMARY_LABELS.get(language, SUMMARY_LABELS["en"])
        template_content = self._load_prd_template(session, language)
        draft_mode = "draft_with_assumptions" if not progress.get("fully_confirmed") else "confirmed_prd"
        business_template_context = self._business_template_document_context(session, language)
        business_template_block = f"\n\n{business_template_context}" if business_template_context else ""
        document_quality_gate = self._document_quality_gate(
            structured_requirement_model,
            progress,
            draft_mode,
            session,
            language,
        )
        return [
            {"role": "system", "content": self._prd_doc_prompt(session, language)},
            {
                "role": "user",
                "content": (
                    "PRD template:\n"
                    + template_content
                    + "\n\nCollection progress:\n"
                    + json.dumps(progress, ensure_ascii=False)
                    + f"\n\nGeneration mode:\n{draft_mode}"
                    + "\n\nDocument quality gate:\n"
                    + json.dumps(document_quality_gate, ensure_ascii=False)
                    + f"\n\n{content_label}:\n"
                    + json.dumps(self._conversation_messages(messages), ensure_ascii=False)
                    + f"\n\n{summary_label}:\n"
                    + json.dumps(structured_requirement_model, ensure_ascii=False)
                    + business_template_block
                ),
            },
        ]

    def _load_prd_template(self, session: Session, language: str) -> str:
        if session.applied_template_id:
            template_markdown = self.business_template_library.get_template_markdown(
                session.applied_template_id,
                self._normalize_language(language),
            )
            if template_markdown:
                return template_markdown

        normalized = self._normalize_language(language)
        filename = PRD_TEMPLATE_FILE_BY_LANGUAGE.get(normalized, PRD_TEMPLATE_FILE_BY_LANGUAGE["en"])
        template_path = self.prd_templates_dir / filename
        if not template_path.exists():
            return ""
        return template_path.read_text(encoding="utf-8")

    def _structured_requirement_progress(self, structured_requirement_model: dict[str, Any]) -> dict[str, Any]:
        collection_status = structured_requirement_model.get("collection_status")
        if not isinstance(collection_status, dict):
            collection_status = {}

        statuses_by_key: list[tuple[str, str]] = []
        for key in REQUIREMENT_ITEM_KEYS:
            item = collection_status.get(key)
            if isinstance(item, dict):
                status_value = str(item.get("status", "missing")).strip().lower()
            else:
                status_value = "missing"
            if status_value not in STRUCTURED_REQUIREMENT_STATUS_READINESS_POINTS:
                status_value = "missing"
            statuses_by_key.append((key, status_value))

        statuses_by_name = dict(statuses_by_key)
        statuses = [status for _, status in statuses_by_key]
        total_count = len(statuses)
        confirmed_count = sum(1 for status in statuses if status == "confirmed")
        collected_count = sum(1 for status in statuses if status != "missing")
        conflict_count = sum(1 for status in statuses if status == "conflict")
        pending_confirmation_count = sum(
            1
            for status in statuses
            if status not in {"missing", "confirmed", "conflict"}
        )
        collection_coverage_percentage = (
            round((collected_count / total_count) * 100) if total_count else 0
        )
        confirmation_percentage = (
            round((confirmed_count / total_count) * 100) if total_count else 0
        )
        open_question_count = len(self._string_list(structured_requirement_model.get("open_questions")))
        pending_question_count = 0
        for item in collection_status.values():
            if isinstance(item, dict):
                pending_question_count += len(self._string_list(item.get("pending_questions")))
        # Top-level open_questions are PRD caveats/notes, not a chat-loop gate. Only
        # field-level pending_questions block generation because they are tied to a
        # specific structured requirement item the user still needs to confirm.
        blocking_question_count = pending_question_count
        fully_confirmed = (
            total_count > 0
            and confirmed_count == total_count
            and conflict_count == 0
            and blocking_question_count == 0
        )
        total_weight = sum(
            STRUCTURED_REQUIREMENT_PROGRESS_WEIGHTS.get(key, 1.0)
            for key, _ in statuses_by_key
        )
        earned_weight = sum(
            STRUCTURED_REQUIREMENT_PROGRESS_WEIGHTS.get(key, 1.0)
            * STRUCTURED_REQUIREMENT_STATUS_READINESS_POINTS.get(status, 0.0)
            for key, status in statuses_by_key
        )
        readiness_percentage = round((earned_weight / total_weight) * 100) if total_weight else 0
        if fully_confirmed:
            readiness_percentage = 100
        elif conflict_count:
            readiness_percentage = min(readiness_percentage, 69)
        elif pending_confirmation_count or blocking_question_count:
            readiness_percentage = min(readiness_percentage, 94)
        core_requirements_confirmed = all(
            statuses_by_name.get(key) == "confirmed"
            for key in STRUCTURED_REQUIREMENT_GENERATION_CORE_KEYS
        )
        # Formal-document gate (kept in sync with frontend structuredRequirementProgress.ts):
        # every structured requirement item must be confirmed. This app no longer
        # treats pending fields as a PRD V0/draft handoff path.
        ready_to_generate = fully_confirmed

        return {
            "total_count": total_count,
            "confirmed_count": confirmed_count,
            "collected_count": collected_count,
            "pending_confirmation_count": pending_confirmation_count,
            "conflict_count": conflict_count,
            "readiness_percentage": readiness_percentage,
            "collection_coverage_percentage": collection_coverage_percentage,
            "confirmation_percentage": confirmation_percentage,
            "fully_confirmed": fully_confirmed,
            "core_requirements_confirmed": core_requirements_confirmed,
            "open_question_count": open_question_count,
            "pending_question_count": pending_question_count,
            "blocking_question_count": blocking_question_count,
            "ready_to_generate": ready_to_generate,
        }

    def _can_generate_v0_prd(
        self,
        progress: dict[str, Any],
        conversation_messages: list[dict[str, Any]],
    ) -> bool:
        """Return True when the conversation is enough for a PRD V0, even before Final readiness."""
        conflict_count = self._safe_int(progress.get("conflict_count"))
        if conflict_count > 0:
            return False

        user_seed_texts = self._prd_v0_requirement_seed_texts(conversation_messages)
        user_text = "\n".join(user_seed_texts).strip()
        if len(user_text) < PRD_V0_MINIMUM_USER_SEED_LENGTH:
            return False

        collection_coverage_percentage = self._safe_int(progress.get("collection_coverage_percentage"))
        collected_count = self._safe_int(progress.get("collected_count"))
        return (
            collection_coverage_percentage >= 20
            or collected_count >= 1
            or len(user_text) >= PRD_V0_MINIMUM_USER_SEED_LENGTH
        )

    def _session_matches_ic_substrate_fast_path(self, session: Session, language: str) -> bool:
        template = self._resolve_business_template(session, language)
        if template is not None:
            return self._template_matches_ic_substrate_focus(template)
        if session.applied_template_name:
            return self._template_matches_ic_substrate_focus({"template_name": session.applied_template_name})
        latest_department = self._ic_substrate_intent_track_from_latest_user_message(session)
        if latest_department in {"production", "quality", "tdi"}:
            return True
        product_shape = self._ic_substrate_product_shape_from_latest_user_message(session)
        shape_department = self._ic_substrate_department_from_product_shape(product_shape)
        return shape_department in {"production", "quality", "tdi"}

    def _session_matches_ic_substrate_expert_chain(
        self,
        session: Session,
        language: str,
        structured_requirement_model: dict[str, Any] | None = None,
    ) -> bool:
        normalized_language = self._normalize_language(language)
        if self._session_matches_ic_substrate_fast_path(session, normalized_language):
            return True

        model = (
            normalize_structured_requirement_model(structured_requirement_model)
            if structured_requirement_model is not None
            else self._latest_structured_requirement_model_for_prompt(session, normalized_language)
        )
        model_department = self._ic_substrate_intent_track_from_structured_model(model)
        if model_department in {"production", "quality", "tdi"}:
            return True

        product_shape = self._ic_substrate_product_shape_from_model_or_template(
            session,
            model,
            normalized_language,
        )
        shape_department = self._ic_substrate_department_from_product_shape(product_shape)
        return shape_department in {"production", "quality", "tdi"}

    def _prd_v0_requirement_seed_texts(self, conversation_messages: list[dict[str, Any]]) -> list[str]:
        return [
            text
            for message in conversation_messages
            if message.get("role") == "user"
            for text in [str(message.get("content", "")).strip()]
            if self._is_prd_v0_requirement_seed(text)
        ]

    def _is_prd_v0_requirement_seed(self, content: str) -> bool:
        """A short choice-only A/B/C route reply is not enough to produce a quality PRD V0."""
        text = str(content or "").strip()
        if len(text) < PRD_V0_MINIMUM_USER_SEED_LENGTH:
            return False
        return not (
            self._is_prd_v0_choice_only_reply(text)
            or self._is_prd_v0_non_requirement_reply(text)
        )

    def _is_prd_v0_choice_only_reply(self, content: str) -> bool:
        text = str(content or "").strip()
        if self._has_prd_v0_seed_slot_marker(text):
            return False
        return (
            len(text) <= 160
            and "\n" not in text
            and re.match(r"^[ABC]\s*[\.)、:：-]\s+\S[\s\S]*$", text, re.IGNORECASE) is not None
        )

    def _has_prd_v0_seed_slot_marker(self, content: str) -> bool:
        normalized = str(content or "").strip().lower()
        return any(
            marker in normalized
            for marker in [
                "first action:",
                "owner/user:",
                "owner:",
                "user:",
                "source:",
                "business_action",
                "primary_user_or_owner",
                "source_of_truth",
                "integration_writeback_boundary",
                "acceptance_evidence",
                "source of truth:",
                "kpi/acceptance:",
                "acceptance:",
                "boundary:",
                "首版动作",
                "使用者",
                "主要用户",
                "数据源",
                "验收证据",
                "写回边界",
                "集成/写回边界",
            ]
        )

    def _is_prd_v0_non_requirement_reply(self, content: str) -> bool:
        text = re.sub(r"[\s。.!！?？,，;；:：、~-]+", " ", str(content or "").strip().lower()).strip()
        if not text or len(text) > 60:
            return False

        requirement_signals = [
            "做",
            "系统",
            "软件",
            "看板",
            "报表",
            "查询",
            "追踪",
            "提醒",
            "dashboard",
            "tracker",
            "alert",
            "query",
            "report",
            "system",
            "app",
            "build",
        ]
        if any(signal in text for signal in requirement_signals):
            return False

        generic_uncertainty_markers = [
            "我不知道",
            "不知道",
            "不清楚",
            "没想好",
            "随便",
            "都可以",
            "not sure",
            "i do not know",
            "i don't know",
            "i dont know",
            "no idea",
            "whatever",
            "anything",
            "keine ahnung",
            "weiss nicht",
            "egal",
            "tidak tahu",
            "tak tahu",
            "terserah",
        ]
        generic_acknowledgements = {
            "ok",
            "okay",
            "yes",
            "no",
            "thanks",
            "thank you",
            "好的",
            "收到",
            "可以",
            "行",
            "ja",
            "nein",
            "ya",
            "tidak",
            "boleh",
        }
        return text in generic_acknowledgements or any(marker in text for marker in generic_uncertainty_markers)
