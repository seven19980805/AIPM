import json
import sys
import tempfile
import unittest
import zipfile
from io import BytesIO
from pathlib import Path
from xml.etree import ElementTree


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.services.business_template_library import BusinessTemplateLibrary
from app.services.requirement_collector import (
    PRD_MESSAGE_KIND,
    STRUCTURED_REQUIREMENT_CANONICAL_CACHE_KEY,
    RequirementCollectorService,
)
from app.services.session_store import SQLiteSessionStore
from app.services.structured_requirement_model import REQUIREMENT_ITEM_KEYS, normalize_structured_requirement_model


class FakeLLMClient:
    def __init__(self) -> None:
        self.calls: list[list[dict[str, str]]] = []
        self.stream_calls: list[list[dict[str, str]]] = []
        self.chat_response = "# Generated PRD\n\nGenerated from seeded example requirements."
        self.stream_response_parts: list[dict[str, str]] | None = None

    def chat(self, messages: list[dict[str, str]], temperature: float = 0.3) -> str:
        self.calls.append(messages)
        return self.chat_response

    def stream_chat(self, messages: list[dict[str, str]], temperature: float = 0.3):
        self.stream_calls.append(messages)
        if self.stream_response_parts is not None:
            yield from self.stream_response_parts
            return
        yield {"type": "content", "text": "# Generated Streamed Document\n\n"}
        yield {"type": "content", "text": "Generated from seeded example requirements."}


class TemplateExampleStartTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        db_path = Path(self.tmpdir.name) / "rqmd.sqlite3"
        self.llm_client = FakeLLMClient()
        self.service = RequirementCollectorService(
            self.llm_client,
            SQLiteSessionStore(str(db_path)),
        )
        self.template_id = "business_process_requirement_template_en"

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def _cache_requirement_model(self, session_id: str, model: dict, language: str = "en") -> None:
        session = self.service._require_session(session_id)
        message_count = self.service._message_count(session.messages)
        for cache_key in {STRUCTURED_REQUIREMENT_CANONICAL_CACHE_KEY, language}:
            self.service._save_structured_requirement_model_cache(
                session_id,
                cache_key,
                message_count,
                model,
            )

    def _cache_ready_requirement_model(self, session_id: str) -> None:
        collection_status = {
            key: {
                "status": "confirmed",
                "reason": "Confirmed for document generation.",
                "pending_questions": [],
            }
            for key in REQUIREMENT_ITEM_KEYS
        }
        model = normalize_structured_requirement_model(
            {
                "document_info": {"project_name": "Lot yield dashboard"},
                "background": {
                    "objective": "Track lot yield losses for Quality review with a target to cut review time by 20%.",
                    "summary": "Quality needs a v1 lot yield dashboard, with production writeback deferred to a later phase.",
                },
                "product_context": {
                    "requesting_department": "Quality",
                    "primary_user": "Quality manager",
                    "decision_or_action": "Review yield loss by lot and defect type.",
                    "software_type": "Dashboard",
                    "business_owner": "Quality manager",
                    "acceptance_owner": "Quality manager",
                },
                "scope": {
                    "in_scope": ["P0 first release: lot yield loss dashboard"],
                    "out_of_scope": ["Later phase: production writeback"],
                },
                "users_and_scenarios": {
                    "target_users": ["Quality manager"],
                    "core_scenarios": ["Review yield loss by lot"],
                },
                "functional_requirements": {
                    "overview": "Dashboard, filters, export, and drilldown.",
                    "feature_details": [
                        {
                            "feature_name": "Yield loss dashboard",
                            "description": "Show loss by lot and defect type.",
                            "inputs": ["QIS/MES export"],
                            "outputs": ["Dashboard and export"],
                        }
                    ],
                },
                "page_and_interaction": {
                    "pages": [
                        {
                            "page_name": "Yield dashboard",
                            "entry_point": "Dashboard home",
                            "primary_actions": ["Filter", "Export"],
                        }
                    ],
                },
                "business_rules": [
                    "P0 must show lot yield losses before export or production writeback.",
                    "No production writeback before approval.",
                ],
                "data_and_dependencies": ["QIS/MES export"],
                "risks_and_notes": ["Risk: QIS/MES export freshness may delay daily review."],
                "acceptance_criteria": [
                    "Success metric: Quality manager verifies loss by lot within 10 minutes.",
                ],
                "collection_status": collection_status,
            }
        )
        self._cache_requirement_model(session_id, model)

    def _pm_chat_calls(self) -> list[list[dict[str, str]]]:
        return [
            call
            for call in self.llm_client.calls
            if call
            and (
                "principal Product Manager" in call[0].get("content", "")
                or "方法论扎实的产品经理" in call[0].get("content", "")
            )
        ]

    def _cache_methodology_incomplete_requirement_model(self, session_id: str) -> None:
        collection_status = {
            key: {
                "status": "confirmed",
                "reason": "Confirmed for document generation.",
                "pending_questions": [],
            }
            for key in REQUIREMENT_ITEM_KEYS
        }
        model = normalize_structured_requirement_model(
            {
                "document_info": {"project_name": "Thin dashboard"},
                "background": {
                    "objective": "Track a quality signal.",
                    "summary": "A thin dashboard requirement.",
                },
                "collection_status": collection_status,
            }
        )
        self._cache_requirement_model(session_id, model)

    def test_guided_template_session_stays_empty(self) -> None:
        session = self.service.create_session(
            template_id=self.template_id,
            language="en",
        )

        self.assertEqual(session.applied_template_id, self.template_id)
        self.assertEqual(session.messages, [])

    def test_guided_template_prompt_uses_conversation_chain(self) -> None:
        session = self.service.create_session(
            template_id=self.template_id,
            language="en",
        )

        prompt = self.service._pm_prompt(session, "en")

        self.assertIn("Template conversation chain", prompt)
        self.assertIn("progressive interview chain", prompt)
        self.assertNotIn("IC Substrate initial chain", prompt)

    def test_pm_prompt_uses_skill_style_discovery_method(self) -> None:
        session = self.service.create_session(
            template_id="qdm_finished_lot_yield_dashboard_template_zh_cn",
            language="zh",
        )

        prompt = self.service._pm_prompt(session, "zh")

        self.assertIn("AI PM skill-style 工作法", prompt)
        self.assertIn("沿需求决策树逐支拆解", prompt)
        self.assertIn("每个问题必须带一个可快速确认的推荐答案或选项示例", prompt)
        self.assertIn("建立共享领域语言", prompt)
        self.assertIn("PRD 质量门", prompt)
        self.assertIn("PM Methodology 只作质量参考", prompt)
        self.assertIn("最后一段必须使用 A/B/C 选项格式", prompt)

    def test_pm_prompt_treats_methodology_gaps_as_advisory_when_structured_ready(self) -> None:
        session = self.service.create_session(language="en", starter_department="quality")
        self.service._append_message(session.id, "user", "Build a thin quality dashboard.")
        self._cache_methodology_incomplete_requirement_model(session.id)

        prompt = self.service._pm_prompt(self.service._require_session(session.id), "en")

        self.assertIn("PM methodology state", prompt)
        self.assertIn("PM Methodology is advisory", prompt)
        self.assertIn("Phase = ready to generate", prompt)
        self.assertNotIn("Hard gate: while PM Methodology is not ready_for_pm_review", prompt)
        self.assertNotIn("do NOT tell the user to generate documents", prompt)
        self.assertNotIn("The next assistant turn must ask the first methodology gap", prompt)
        self.assertNotIn(
            "Only suggest document generation when structured requirement ready_to_generate=true AND PM Methodology ready_for_pm_review=true",
            prompt,
        )

    def test_false_ready_assistant_reply_is_replaced_when_gate_is_not_ready(self) -> None:
        self.llm_client.chat_response = (
            "We now have enough detail to generate the requirements document. "
            "Click Generate Document to produce the full PRD/URD."
        )
        session = self.service.create_session(template_id=self.template_id, language="en")

        result = self.service.send_user_message(session.id, "Build a thin dashboard.", language="en")

        self.assertIn("Not ready to generate the formal document yet", result["assistant_message"])
        self.assertIn("Next, close one highest-value gap", result["assistant_message"])
        self.assertIn("A. Use a practical v1 assumption", result["assistant_message"])
        self.assertIn("B. I will provide the exact", result["assistant_message"])
        self.assertIn("C. Leave this pending for now", result["assistant_message"])
        self.assertNotIn("suggested interpretation above", result["assistant_message"])
        self.assertNotIn("Click Generate Document", result["assistant_message"])

    def test_handoff_finalization_prompt_is_treated_as_generation_ready_claim(self) -> None:
        text = (
            "To confirm handoff readiness, would you like to finalize the documented "
            "requirements for the v1 Availability Dashboard? "
            "A. Yes — generate the requirements document and proceed to handoff."
        )

        self.assertTrue(self.service._assistant_claims_document_generation_ready(text))

    def test_ready_generation_claim_is_not_replaced_when_structured_gate_is_ready(self) -> None:
        session = self.service.create_session(language="en", starter_department="quality")
        self.service._append_message(session.id, "user", "Build a thin dashboard.")
        self._cache_methodology_incomplete_requirement_model(session.id)
        assistant_text = "Requirements are ready. Click Generate Documents to produce the PRD."

        guarded = self.service._guard_assistant_readiness_response(
            session.id,
            assistant_text,
            "en",
        )

        self.assertEqual(guarded, assistant_text)

    def test_ready_clarification_question_is_replaced_with_generate_documents_cta(self) -> None:
        session = self.service.create_session(language="en", starter_department="quality")
        self.service._append_message(session.id, "user", "Build a lot yield dashboard.")
        self._cache_ready_requirement_model(session.id)
        assistant_text = (
            "Understood. I propose the following v1 acceptance criteria. "
            "Please confirm this matches your expectation.\n\n"
            "Choose one option: A. Confirm this point with a clear version-one assumption "
            "B. I will provide the real business wording or exception "
            "C. Keep this point pending for now"
        )

        guarded = self.service._guard_assistant_readiness_response(
            session.id,
            assistant_text,
            "en",
        )

        self.assertIn("Generate Documents", guarded)
        self.assertNotIn("Choose one option", guarded)
        self.assertNotIn("A. Confirm", guarded)
        self.assertNotIn("Keep this point pending", guarded)

    def test_ready_clarification_question_with_saved_prd_is_replaced_with_go_coding_cta(self) -> None:
        session = self.service.create_session(language="en", starter_department="quality")
        self.service._append_message(session.id, "user", "Build a lot yield dashboard.")
        self._cache_ready_requirement_model(session.id)
        self.service._build_generated_document_result(
            session_id=session.id,
            document_kind=PRD_MESSAGE_KIND,
            language="en",
            doc_markdown="# Lot Yield Dashboard PRD\n\nReady for handoff.",
            structured_requirement_model=self.service.build_structured_requirement_model(session.id, "en"),
            status="ok",
            save_history=True,
        )
        assistant_text = (
            "Please confirm this matches your expectation, or adjust as needed. "
            "Once confirmed, the requirements are ready for document generation.\n\n"
            "A. Confirm this point with a clear version-one assumption\n"
            "B. I will provide the real business wording or exception\n"
            "C. Keep this point pending for now"
        )

        guarded = self.service._guard_assistant_readiness_response(
            session.id,
            assistant_text,
            "en",
        )

        self.assertIn("Go Coding", guarded)
        self.assertIn("Vibe Coding", guarded)
        self.assertNotIn("A. Confirm", guarded)
        self.assertNotIn("Keep this point pending", guarded)

    def test_saved_prd_generation_cta_is_replaced_with_go_coding_cta(self) -> None:
        session = self.service.create_session(language="en", starter_department="quality")
        self.service._append_message(session.id, "user", "Build a lot yield dashboard.")
        self._cache_ready_requirement_model(session.id)
        self.service._build_generated_document_result(
            session_id=session.id,
            document_kind=PRD_MESSAGE_KIND,
            language="en",
            doc_markdown="# Lot Yield Dashboard PRD\n\nReady for handoff.",
            structured_requirement_model=self.service.build_structured_requirement_model(session.id, "en"),
            status="ok",
            save_history=True,
        )
        assistant_text = (
            "Great, your confirmation is noted. All structural requirements are final.\n\n"
            "Next step: Click Generate Documents on the right to create the formal "
            "requirements document. Once the document is generated and approved, you can "
            "use Go Coding / Vibe Coding to hand it off for implementation."
        )

        guarded = self.service._guard_assistant_readiness_response(
            session.id,
            assistant_text,
            "en",
        )

        self.assertIn("has been generated", guarded)
        self.assertIn("Go Coding", guarded)
        self.assertIn("Vibe Coding", guarded)
        self.assertNotIn("Generate Documents", guarded)

    def test_open_questions_do_not_block_ready_structured_model(self) -> None:
        session = self.service.create_session(language="en", starter_department="quality")
        self.service._append_message(session.id, "user", "Build a thin dashboard.")
        collection_status = {
            key: {
                "status": "confirmed",
                "reason": "Confirmed for document generation.",
                "pending_questions": [],
            }
            for key in REQUIREMENT_ITEM_KEYS
        }
        model = normalize_structured_requirement_model(
            {
                "document_info": {"project_name": "Thin dashboard"},
                "background": {"objective": "Track a quality signal."},
                "open_questions": ["Provide the 3-5 example defect codes."],
                "collection_status": collection_status,
            }
        )
        self._cache_requirement_model(session.id, model)
        assistant_text = (
            "Not ready to generate the formal document yet: the right-side readiness gate has not passed. "
            "Collection coverage is 100%, confirmation progress is 100%, and PM Methodology is 77%.\n\n"
            "Next, close one highest-value gap: Page layout and dashboard UI design not defined.\n\n"
            "Choose one option: A. Confirm open question with a clear version-one assumption "
            "B. I will provide the real open question wording or exception "
            "C. Keep this point pending for now"
        )

        guarded = self.service._guard_assistant_readiness_response(
            session.id,
            assistant_text,
            "en",
        )

        self.assertIn("Generate Documents", guarded)
        self.assertNotIn("Not ready", guarded)
        self.assertNotIn("PM Methodology", guarded)
        self.assertNotIn("Choose one option", guarded)
        self.assertNotIn("Page layout", guarded)

    def test_recent_option_a_confirmation_promotes_matching_structured_item(self) -> None:
        session = self.service.create_session(language="en", starter_department="quality")
        self.service._append_message(session.id, "user", "Build a quality yield dashboard.")
        self.service._append_message(
            session.id,
            "assistant",
            (
                "Not ready to generate the formal document yet: the right-side readiness gate has not passed.\n\n"
                "Next, close one highest-value gap: Please confirm the page elements and interaction flow.\n\n"
                "Choose one option:\n"
                "A. Use the current captured wording for pages: Yield Dashboard / Browser URL (no authentication)\n"
                "B. I will provide the exact pages wording or an exception\n"
                "C. Leave this pending for now"
            ),
        )
        self.service._append_message(
            session.id,
            "user",
            "A. Use the current captured wording for pages: Yield Dashboard / Browser URL (no authentication)",
        )
        model = normalize_structured_requirement_model(
            {
                "page_and_interaction": {
                    "pages": [
                        {
                            "page_name": "Yield Dashboard",
                            "entry_point": "Browser URL",
                        }
                    ]
                },
                "collection_status": {
                    "pages": {
                        "status": "captured",
                        "reason": "Page wording captured but not marked confirmed by the model.",
                        "pending_questions": ["Please confirm the page elements and interaction flow."],
                    }
                },
            }
        )

        promoted = self.service._apply_recent_choice_confirmation_to_model(
            model,
            self.service._require_session(session.id).messages,
        )

        self.assertEqual(promoted["collection_status"]["pages"]["status"], "confirmed")
        self.assertEqual(promoted["collection_status"]["pages"]["pending_questions"], [])

    def test_stream_false_ready_reply_emits_replacement_when_gate_is_not_ready(self) -> None:
        self.llm_client.chat_response = "# Not structured JSON"
        self.llm_client.stream_response_parts = [
            {
                "type": "content",
                "text": (
                    "We now have enough detail to generate the requirements document. "
                    "Click Generate Document to produce the full PRD/URD."
                ),
            }
        ]
        session = self.service.create_session(template_id=self.template_id, language="en")

        events = list(self.service.stream_user_message(session.id, "Build a thin dashboard.", language="en"))
        replacement_events = [event for event in events if event.get("event") == "replace_content"]
        saved_session = self.service._require_session(session.id)

        self.assertTrue(replacement_events)
        self.assertIn("Not ready to generate the formal document yet", str(replacement_events[-1].get("content")))
        self.assertIn("Not ready to generate the formal document yet", saved_session.messages[-1]["content"])
        self.assertNotIn("suggested interpretation above", saved_session.messages[-1]["content"])
        self.assertNotIn("Click Generate Document", saved_session.messages[-1]["content"])

    def test_open_clarification_question_gets_choice_fallback(self) -> None:
        text = "我理解你想做排产预测系统。首版主要服务哪个部门？"

        formatted = self.service._ensure_choice_question_format(text, "zh")

        self.assertIn("A. 先按一个可落地的 v1 假设推进", formatted)
        self.assertIn("B. 我补充真实业务口径或例外情况", formatted)
        self.assertIn("C. 这个点先保持待确认", formatted)
        self.assertNotIn("按上面的建议口径", formatted)
        self.assertNotIn("建议回复 A、B、C", formatted)

    def test_existing_choice_question_is_not_duplicated(self) -> None:
        text = "请选择首版入口：\nA. Production\nB. Quality\nC. TDI"

        formatted = self.service._ensure_choice_question_format(text, "zh")

        self.assertEqual(formatted, text)

    def test_streamed_open_question_gets_ui_language_choice_fallback_before_save(self) -> None:
        self.llm_client.stream_response_parts = [
            {"type": "content", "text": "Which department owns this first-version requirement?"}
        ]
        session = self.service.create_session(language="zh")

        events: list[dict[str, object]] = []
        for event in self.service.stream_user_message(
            session.id,
            "我想做一个 IC Substrate dashboard",
            language="en",
        ):
            events.append(event)
            if event.get("event") == "assistant_done":
                break

        streamed_text = "".join(
            str(event.get("delta", ""))
            for event in events
            if event.get("event") == "content"
        )
        refreshed = self.service.get_session(session.id)
        self.assertIsNotNone(refreshed)

        self.assertIn("Which department owns this first-version requirement?", streamed_text)
        self.assertIn("A. Use a practical v1 assumption and continue", streamed_text)
        self.assertIn("B. I will provide the exact wording or an exception", streamed_text)
        self.assertIn("C. Leave this pending for now", streamed_text)
        self.assertNotIn("suggested interpretation above", streamed_text)
        self.assertNotIn("Reply with A, B, C", streamed_text)
        self.assertNotIn("同意按上面的建议口径", streamed_text)
        self.assertEqual(refreshed.messages[-1]["content"], streamed_text)

    def test_streamed_reply_returns_fresh_structured_summary_before_done(self) -> None:
        self.llm_client.stream_response_parts = [
            {"type": "content", "text": "请确认首版数据源。\n\nA. MES mock data\nB. 手工 CSV"}
        ]
        session = self.service.create_session(language="zh")

        events = list(
            self.service.stream_user_message(
                session.id,
                "我想做一个 IC Substrate Quality dashboard",
                language="zh",
            )
        )
        event_names = [str(event.get("event")) for event in events]

        self.assertIn("assistant_done", event_names)
        self.assertIn("summary", event_names)
        self.assertLess(event_names.index("assistant_done"), event_names.index("summary"))
        self.assertLess(event_names.index("summary"), event_names.index("done"))
        self.assertEqual(event_names[-1], "done")
        summary_event = next(event for event in events if event.get("event") == "summary")
        self.assertEqual(summary_event.get("structured_requirement_sync_status"), "ready")
        self.assertIn("structured_requirement_model", summary_event)
        self.assertIn("pm_methodology_state", summary_event)
        self.assertEqual(len(self.llm_client.stream_calls), 1)
        self.assertEqual(len(self.llm_client.calls), 1)

    def test_streamed_reply_promotes_cache_without_redundant_extraction(self) -> None:
        """After the assistant reply, the structured requirement model should be
        promoted from the pre-reply cache to the post-reply message_count
        without making a second LLM extraction call."""
        self.llm_client.stream_response_parts = [
            {"type": "content", "text": "Next question about data sources.\n\nA. MES\nB. CSV"}
        ]
        session = self.service.create_session(language="zh")

        events = list(
            self.service.stream_user_message(
                session.id,
                "我想做一个 IC Substrate Quality dashboard",
                language="zh",
            )
        )

        # Exactly 1 regular chat call for the pre-reply structured extraction, and 1 stream
        # call for the LLM-driven reply. There must NOT be a second extraction after the
        # reply - the post-reply summary uses cache promotion, not a new LLM call.
        extraction_calls = len(self.llm_client.calls)
        self.assertEqual(extraction_calls, 1, (
            f"Expected exactly 1 extraction LLM call, got {extraction_calls}. "
            "The post-reply extraction should use cache promotion, not a new LLM call."
        ))
        self.assertEqual(len(self.llm_client.stream_calls), 1)

        # The summary event should carry the promoted model.
        summary_event = next(event for event in events if event.get("event") == "summary")
        self.assertEqual(summary_event.get("structured_requirement_sync_status"), "ready")
        self.assertIn("structured_requirement_model", summary_event)
        self.assertIn("pm_methodology_state", summary_event)
        self.assertIn("ic_substrate_evidence_state", summary_event)

        # The post-reply snapshot should also see sync_status=ready (not stale),
        # because the cache was promoted to the current message_count.
        snapshot = self.service.get_structured_requirement_snapshot(session.id, "zh")
        self.assertEqual(snapshot["structured_requirement_sync_status"], "ready")

    def test_streamed_reply_is_llm_driven_with_fresh_structured_state(self) -> None:
        # The reply is LLM-streamed (no deterministic planner). Structured extraction
        # runs once BEFORE the reply so the readiness directive in the prompt reflects the
        # latest turn, and the post-reply summary is promoted from cache (no extra call).
        self.llm_client.chat_response = json.dumps(
            normalize_structured_requirement_model(
                {
                    "document_info": {"project_name": "Equipment availability dashboard"},
                    "background": {
                        "objective": "Reduce downtime through supervisor intervention.",
                        "summary": "Production supervisor needs an availability dashboard.",
                    },
                }
            )
        )
        self.llm_client.stream_response_parts = [
            {"type": "content", "text": "What machine states should the first version show?\n\nA. Up/Down only\nB. Up/Down/Idle"}
        ]
        session = self.service.create_session(language="en")

        events = list(
            self.service.stream_user_message(
                session.id,
                "Production first action: equipment downtime dashboard for supervisors.",
                language="en",
            )
        )
        streamed_text = "".join(
            str(event.get("delta", ""))
            for event in events
            if event.get("event") == "content"
        )

        self.assertEqual(len(self.llm_client.stream_calls), 1)
        self.assertEqual(len(self.llm_client.calls), 1)
        self.assertIn("What machine states", streamed_text)

    def test_methodology_priority_recognizes_v1_first_release_scope_boundary(self) -> None:
        model = normalize_structured_requirement_model(
            {
                "document_info": {"project_name": "Equipment availability dashboard"},
                "background": {
                    "objective": "Reduce overall equipment downtime by 10% through real-time monitoring.",
                    "summary": "v1 availability dashboard for production supervisor intervention.",
                },
                "product_context": {
                    "primary_user": "Production supervisor",
                    "decision_or_action": "Dispatch technician when a machine is down for more than 5 minutes.",
                },
                "scope": {
                    "in_scope": ["First release is Availability only dashboard for downtime monitoring."],
                    "out_of_scope": [
                        "Performance speed-loss and Quality yield-loss are excluded from v1.",
                        "No MES/SAP writeback, scheduling changes, or maintenance ticket creation.",
                    ],
                },
                "functional_requirements": {
                    "overview": "Machine cards, downtime reason chart, affected lot drill-down.",
                },
                "business_rules": ["Visual alert when downtime exceeds 5 minutes."],
            }
        )

        state = self.service.build_pm_methodology_state(model, "en")
        priority_check = next(check for check in state["checks"] if check["key"] == "prioritization")

        self.assertEqual(priority_check["status"], "ready")

    def test_non_question_summary_does_not_get_choice_fallback(self) -> None:
        text = "已确认：首版聚焦 Production 的排产预测，目标用户是 planner。"

        formatted = self.service._ensure_choice_question_format(text, "zh")

        self.assertEqual(formatted, text)

    def test_structured_requirement_prompt_extracts_shared_domain_language(self) -> None:
        session = self.service.create_session(
            template_id="qdm_finished_lot_yield_dashboard_template_zh_cn",
            language="zh",
        )

        prompt = self.service._structured_requirement_model_prompt(session, "zh")

        self.assertIn("Skill-style 抽取补充规则", prompt)
        self.assertIn("共享领域语言", prompt)
        self.assertIn("业务术语、KPI 名称、状态名、对象粒度、owner、数据源、验收口径", prompt)
        self.assertIn("不新增 schema", prompt)
        self.assertIn("不要升级为 confirmed", prompt)

    def test_prd_prompt_uses_skill_style_document_rules(self) -> None:
        session = self.service.create_session(
            template_id="qdm_finished_lot_yield_dashboard_template_zh_cn",
            language="zh",
        )

        prompt = self.service._prd_doc_prompt(session, "zh")

        self.assertIn("Skill-style PRD 写作规则", prompt)
        self.assertIn("PRD 不是聊天纪要", prompt)
        self.assertIn("Glossary / Definitions", prompt)
        self.assertIn("User Stories 必须覆盖真实业务场景", prompt)
        self.assertIn("Implementation Decisions", prompt)
        self.assertIn("Out of Scope", prompt)

    def test_user_message_response_language_follows_ui_language_selection(self) -> None:
        session = self.service.create_session(language="en")

        self.service.send_user_message(session.id, "我想做一个排产预测系统", language="en")

        first_system_prompt = self._pm_chat_calls()[0][0]["content"]
        self.assertIn("Respond entirely in English", first_system_prompt)
        self.assertNotIn("输出语言要求", first_system_prompt)

    def test_attachment_display_message_stays_separate_from_model_context(self) -> None:
        session = self.service.create_session(language="zh")
        display_message = "请结合附件继续梳理需求。\n\n[附件：cost-model.pptx]"
        full_message = f"{display_message}\n\n[附件：cost-model.pptx]\n完整PPT解析内容和图表说明"

        self.service.send_user_message(
            session.id,
            full_message,
            language="zh",
            display_message=display_message,
        )

        refreshed = self.service.get_session(session.id)
        self.assertIsNotNone(refreshed)
        self.assertEqual(refreshed.messages[0]["content"], full_message)
        self.assertEqual(refreshed.messages[0]["display_content"], display_message)
        self.assertEqual(self._pm_chat_calls()[0][-1]["content"], full_message)

    def test_collection_status_does_not_regress_after_confirmation(self) -> None:
        previous_status = {
            key: {"status": "missing", "reason": "", "pending_questions": []}
            for key in REQUIREMENT_ITEM_KEYS
        }
        previous_status["rules"] = {
            "status": "confirmed",
            "reason": "User confirmed the cost formula.",
            "pending_questions": [],
        }
        previous_status["integrations"] = {
            "status": "captured",
            "reason": "SAP was mentioned.",
            "pending_questions": ["Confirm source of truth."],
        }
        current_status = {
            key: {"status": "missing", "reason": "", "pending_questions": []}
            for key in REQUIREMENT_ITEM_KEYS
        }
        current_status["rules"] = {
            "status": "pending_confirmation",
            "reason": "LLM wants to re-confirm the formula.",
            "pending_questions": ["Is the formula correct?"],
        }
        current_status["integrations"] = {
            "status": "missing",
            "reason": "",
            "pending_questions": [],
        }

        merged = self.service._merge_structured_requirement_collection_status(
            {"collection_status": current_status},
            {"collection_status": previous_status},
        )

        self.assertEqual(merged["collection_status"]["rules"]["status"], "confirmed")
        self.assertEqual(merged["collection_status"]["integrations"]["status"], "captured")

    def test_generation_readiness_requires_full_structured_confirmation(self) -> None:
        # Formal documents are only generated once every structured requirement
        # item is confirmed and no field-level pending questions remain.
        collection_status = {
            key: {"status": "confirmed", "reason": "Confirmed.", "pending_questions": []}
            for key in REQUIREMENT_ITEM_KEYS
        }
        ready_model = normalize_structured_requirement_model(
            {"collection_status": collection_status, "open_questions": []}
        )

        ready_progress = self.service._structured_requirement_progress(ready_model)

        self.assertTrue(ready_progress["fully_confirmed"])
        self.assertTrue(ready_progress["ready_to_generate"])

        open_notes_model = normalize_structured_requirement_model(
            {
                "collection_status": collection_status,
                "open_questions": ["Confirm API auth and rate limits."],
            }
        )
        open_notes_progress = self.service._structured_requirement_progress(open_notes_model)

        self.assertTrue(open_notes_progress["fully_confirmed"])
        self.assertTrue(open_notes_progress["ready_to_generate"])
        self.assertEqual(open_notes_progress["open_question_count"], 1)
        self.assertEqual(open_notes_progress["blocking_question_count"], 0)

        collection_status["acceptance"] = {
            "status": "confirmed",
            "reason": "Acceptance candidate exists.",
            "pending_questions": ["Confirm acceptance owner."],
        }
        with_assumptions_model = normalize_structured_requirement_model(
            {
                "collection_status": collection_status,
                "open_questions": ["Confirm API auth and rate limits."],
            }
        )

        with_assumptions_progress = self.service._structured_requirement_progress(with_assumptions_model)

        # Not "fully confirmed" because a field-level pending question remains.
        self.assertFalse(with_assumptions_progress["fully_confirmed"])
        self.assertEqual(with_assumptions_progress["pending_question_count"], 1)
        self.assertEqual(with_assumptions_progress["open_question_count"], 1)
        self.assertEqual(with_assumptions_progress["blocking_question_count"], 1)
        # ... and generation stays locked; field-level unknowns must be resolved in chat.
        self.assertFalse(with_assumptions_progress["ready_to_generate"])

    def test_generation_readiness_blocks_on_conflict_or_low_coverage(self) -> None:
        # Conflict blocks readiness even at full coverage.
        conflict_status = {
            key: {"status": "confirmed", "reason": "Confirmed.", "pending_questions": []}
            for key in REQUIREMENT_ITEM_KEYS
        }
        conflict_status["scope"] = {"status": "conflict", "reason": "Conflicting scope.", "pending_questions": []}
        conflict_progress = self.service._structured_requirement_progress(
            normalize_structured_requirement_model({"collection_status": conflict_status})
        )
        self.assertFalse(conflict_progress["ready_to_generate"])

        # One missing field still blocks the formal document gate.
        one_missing = {
            key: {"status": "confirmed", "reason": "Confirmed.", "pending_questions": []}
            for key in REQUIREMENT_ITEM_KEYS
        }
        one_missing["pages"] = {"status": "missing", "reason": "", "pending_questions": []}
        one_missing_progress = self.service._structured_requirement_progress(
            normalize_structured_requirement_model({"collection_status": one_missing})
        )
        self.assertFalse(one_missing_progress["ready_to_generate"])

        # Too many missing fields (low coverage) blocks readiness.
        low_coverage = {
            key: {"status": "confirmed", "reason": "Confirmed.", "pending_questions": []}
            for key in REQUIREMENT_ITEM_KEYS
        }
        for key in ("pages", "rules", "integrations", "acceptance"):
            low_coverage[key] = {"status": "missing", "reason": "", "pending_questions": []}
        low_coverage_progress = self.service._structured_requirement_progress(
            normalize_structured_requirement_model({"collection_status": low_coverage})
        )
        self.assertFalse(low_coverage_progress["ready_to_generate"])

    def test_prd_document_appends_deterministic_document_qa(self) -> None:
        session = self.service.create_session(language="en", starter_department="production")
        self.service._append_message(session.id, "user", "Build a production line dashboard.")
        collection_status = {
            key: {"status": "confirmed", "reason": "Confirmed.", "pending_questions": []}
            for key in REQUIREMENT_ITEM_KEYS
        }
        model = normalize_structured_requirement_model(
            {
                "document_info": {"project_name": "Production Line Dashboard"},
                "product_context": {
                    "requesting_department": "Production",
                    "primary_user": "Supervisors",
                    "decision_or_action": "Identify lines behind schedule.",
                    "software_type": "Dashboard",
                    "acceptance_owner": "Supervisor",
                },
                "background": {
                    "objective": "Enable supervisors to monitor current shift production performance.",
                    "summary": "Supervisors compare plan vs actual from MES.",
                },
                "scope": {
                    "in_scope": ["Real-time current shift dashboard"],
                    "out_of_scope": ["Export", "History", "Mobile"],
                },
                "users_and_scenarios": {
                    "target_users": ["Production supervisors"],
                    "core_scenarios": ["Review current shift output by line and product"],
                },
                "functional_requirements": {
                    "overview": "Show line/product plan vs actual and behind indicator.",
                },
                "business_rules": ["Behind schedule when actual < plan."],
                "page_and_interaction": {
                    "pages": [{"page_name": "Shift Dashboard", "entry_point": "Direct URL"}],
                },
                "data_and_dependencies": ["MES provides plan and actual pieces"],
                "acceptance_criteria": ["Supervisor cross-checks dashboard counts against MES report."],
                "open_questions": [
                    "What is the exact shift duration, start time, and end time?",
                    "How often should the dashboard refresh?",
                    "Is SSO or VPN authentication required?",
                    "Which MES API or database view provides the data?",
                    "Are there any branding or color constraints?",
                    "Should supervisors sort or filter by line or product?",
                ],
                "collection_status": collection_status,
            }
        )
        self._cache_requirement_model(session.id, model)
        self.llm_client.chat_response = "# Production Line Dashboard PRD\n\nConfirmed requirement."

        result = self.service.build_prd_document(session.id, "en", save_history=True)
        markdown = result["document_markdown"]

        self.assertIn("## Document QA", markdown)
        self.assertIn("System-counted open questions**: 6", markdown)
        self.assertIn("Production readiness**: Blocked", markdown)
        self.assertIn("Behind-schedule rule may be wrong", markdown)
        self.assertIn("Which MES API or database view provides the data?", markdown)
        self.assertIn("Are there any branding or color constraints?", markdown)
        self.assertIn("Document QA", self.service.get_saved_prd_document(session.id)[0].read_text())

    def test_design_document_qa_flags_default_stack_and_mock_assumptions(self) -> None:
        session = self.service.create_session(language="en", starter_department="production")
        self.service._append_message(session.id, "user", "Build a production line dashboard.")
        collection_status = {
            key: {"status": "confirmed", "reason": "Confirmed.", "pending_questions": []}
            for key in REQUIREMENT_ITEM_KEYS
        }
        model = normalize_structured_requirement_model(
            {
                "document_info": {"project_name": "Production Line Dashboard"},
                "background": {"objective": "Monitor current shift output."},
                "scope": {"in_scope": ["Real-time dashboard"], "out_of_scope": ["Mobile"]},
                "users_and_scenarios": {
                    "target_users": ["Supervisors"],
                    "core_scenarios": ["Open dashboard mid-shift"],
                },
                "functional_requirements": {"overview": "Plan vs actual table."},
                "business_rules": ["Behind schedule when actual < plan."],
                "page_and_interaction": {"pages": [{"page_name": "Shift Dashboard"}]},
                "data_and_dependencies": ["MES data"],
                "acceptance_criteria": ["Cross-check with MES report."],
                "open_questions": ["Which MES system API is available?", "What is the refresh cadence?"],
                "collection_status": collection_status,
            }
        )
        self._cache_requirement_model(session.id, model)
        self.llm_client.chat_response = (
            "# System Design Document\n\n"
            "Default technology stack: Frontend static HTML/CSS/vanilla JS, Backend: C#, Database: SQLite.\n\n"
            "Use mock MES data for demo. Real-time dashboard uses manual refresh only."
        )

        result = self.service.build_system_design_document(session.id, "en", save_history=True)
        markdown = result["document_markdown"]

        self.assertIn("## Document QA", markdown)
        self.assertIn("Technology stack appears to be a system default or demo assumption", markdown)
        self.assertIn("Mock/demo data is acceptable for prototype validation only", markdown)
        self.assertIn("Real-time wording conflicts with manual/TBD refresh behavior", markdown)
        self.assertIn("Real MES integration is not yet specified", markdown)

    def test_coding_handoff_requires_saved_prd_document(self) -> None:
        session = self.service.create_session(language="en", starter_department="quality")
        self.service._append_message(session.id, "user", "Build a lot yield dashboard.")
        self._cache_ready_requirement_model(session.id)
        calls_before = len(self.llm_client.calls)

        payload = self.service.build_browser_handoff_payload(session.id, "en")

        self.assertFalse(payload["documents_ready"])
        self.assertEqual(payload["missing_documents"], ["prd"])
        self.assertEqual(len(self.llm_client.calls), calls_before)
        self.assertIsNone(self.service.get_saved_prd_document(session.id))

    def test_coding_handoff_uses_saved_prd_document(self) -> None:
        session = self.service.create_session(language="en", starter_department="quality")
        self.service._append_message(session.id, "user", "Build a lot yield dashboard.")
        self._cache_ready_requirement_model(session.id)
        self.llm_client.chat_response = "# Lot Yield Dashboard PRD\n\nReady for Vibe Coding handoff."

        document_result = self.service.build_prd_document(session.id, "en", save_history=True)
        handoff_result = self.service.create_coding_handoff(session.id, "en")

        self.assertIn(document_result["status"], {"ok", "draft_with_assumptions"})
        self.assertIn("handoff_token", handoff_result)
        self.assertTrue(handoff_result["payload"]["documents_ready"])
        self.assertEqual(handoff_result["payload"]["documents"][0]["kind"], "prd")
        self.assertIn("Lot Yield Dashboard PRD", self.service.get_saved_prd_document(session.id)[0].read_text())

    def test_prd_generation_not_blocked_by_advisory_pm_methodology(self) -> None:
        # PM Methodology is advisory: with the structured "Fully Confirmed" gate passed,
        # generation proceeds even when the methodology score is low (no quality_gate_blocked).
        session = self.service.create_session(language="en", starter_department="quality")
        self.service._append_message(session.id, "user", "Build a thin dashboard.")
        self._cache_methodology_incomplete_requirement_model(session.id)
        self.llm_client.chat_response = "# Thin Dashboard PRD\n\nGenerated with advisory methodology."

        document_result = self.service.build_prd_document(session.id, "en", save_history=True)

        self.assertNotEqual(document_result["status"], "quality_gate_blocked")
        self.assertIn("Thin Dashboard PRD", document_result["document_markdown"])
        self.assertIsNotNone(self.service.get_saved_prd_document(session.id))

    def test_coding_handoff_allows_prd_with_advisory_pm_methodology(self) -> None:
        # Handoff (Go Coding) is gated on the document existing + structured confirmation,
        # not on the advisory PM Methodology score.
        session = self.service.create_session(language="en", starter_department="quality")
        self.service._append_message(session.id, "user", "Build a thin dashboard.")
        self._cache_methodology_incomplete_requirement_model(session.id)
        self.service._build_generated_document_result(
            session_id=session.id,
            document_kind=PRD_MESSAGE_KIND,
            language="en",
            doc_markdown="# Thin Dashboard PRD\n\nLegacy saved PRD.",
            structured_requirement_model=self.service.build_structured_requirement_model(session.id, "en"),
            status="ok",
            save_history=True,
        )

        handoff_result = self.service.create_coding_handoff(session.id, "en")

        self.assertIn("handoff_token", handoff_result)
        self.assertTrue(handoff_result["payload"]["documents_ready"])
        self.assertTrue(handoff_result["payload"]["handoff_ready"])

    def test_convergence_guidance_stops_open_ended_questions_when_collection_complete(self) -> None:
        collection_status = {
            key: {"status": "confirmed", "reason": "Confirmed.", "pending_questions": []}
            for key in REQUIREMENT_ITEM_KEYS
        }
        collection_status["rules"] = {
            "status": "pending_confirmation",
            "reason": "Candidate rule needs final confirmation.",
            "pending_questions": ["Confirm the formula."],
        }

        guidance = self.service._requirement_convergence_guidance_for_prompt(
            {"collection_status": collection_status},
            "zh",
        )

        self.assertIn("不要继续挖新细节", guidance)
        self.assertIn("确认", guidance)

    def test_ic_substrate_template_prompt_uses_active_department_routing(self) -> None:
        session = self.service.create_session(
            template_id="qdm_finished_lot_yield_dashboard_template_zh_cn",
            language="zh",
        )

        prompt = self.service._pm_prompt(session, "zh")

        self.assertIn("模板对话链路", prompt)
        self.assertIn("IC Substrate 专业对话链路", prompt)
        self.assertIn("AI 产品经理，不是制造/质量/工程顾问", prompt)
        self.assertIn("软件、Web dashboard、流程工具、报表或数据产品", prompt)
        self.assertIn("当前 IT scope 只开放 Production、Quality、TDI 和 General 四个同级入口", prompt)
        self.assertIn("其他部门链路先隐藏，统一归入 General", prompt)
        self.assertIn("首问选项只能列这四个入口", prompt)
        self.assertIn("Production、Quality、TDI，还是 General", prompt)
        self.assertNotIn("Customer/Program、EHS、Engineering/Process", prompt)
        self.assertNotIn("Warehouse/Logistics", prompt)
        self.assertNotIn("核心制造链路的专业样板，不是唯一入口", prompt)
        self.assertIn("部门/业务 owner 路由", prompt)
        self.assertIn("来自哪个部门", prompt)
        self.assertIn("反问必须先落到软件需求", prompt)
        self.assertIn("首版软件形态", prompt)
        self.assertIn("Finished Lot", prompt)
        self.assertIn("MRB", prompt)
        self.assertIn("CAPA", prompt)
        self.assertIn("不要擅自展开缩写", prompt)
        self.assertIn("不要擅自引入未确认的站点缩写", prompt)
        self.assertIn("每轮只能有一个问句", prompt)
        self.assertIn("2-5 个业务选项", prompt)
        self.assertIn("TDI 只能写作 TDI", prompt)
        self.assertIn("部门首问的选项说明里也不能展开 TDI", prompt)
        self.assertIn("不要自造 TDI case 状态名、SLA 数字、owner 角色或审批层级", prompt)
        self.assertIn("Created/In Progress/Closed、24 小时、QA 签核", prompt)
        self.assertIn("不要替 Production 编 route/站点/yield 公式", prompt)
        self.assertIn("不要替 Quality 编 inspection point/defect taxonomy/spec limit/MRB/CAPA 流程", prompt)
        self.assertIn("FVI、AOI、E-test、AVI、SAP、EAP、SPC", prompt)
        self.assertIn("不要擅自引入未确认的站点缩写、工艺站点名、设备名、供应商名、系统品牌", prompt)
        self.assertIn("需求形态明确但用户没有说清发起部门或业务 owner", prompt)
        self.assertIn("先问部门/owner", prompt)
        self.assertIn("当前开放入口平级", prompt)
        self.assertNotIn("核心主线", prompt)
        self.assertNotIn("Planning/PMC", prompt)
        self.assertNotIn("Equipment/Maintenance", prompt)
        self.assertNotIn("Finance/Cost", prompt)
        self.assertIn("当前节点专业追问方向", prompt)

    def test_ic_substrate_template_prompt_has_german_expert_chain(self) -> None:
        session = self.service.create_session(
            template_id="qdm_finished_lot_yield_dashboard_template_de",
            language="de",
        )

        prompt = self.service._pm_prompt(session, "de")
        snapshot = self.service.get_structured_requirement_snapshot(session.id, "de")
        chain_state = snapshot["conversation_chain_state"]

        self.assertIn("Vorlagen-Dialogkette", prompt)
        self.assertIn("IC Substrate Experten-Dialogkette", prompt)
        self.assertIn("AI Product Manager", prompt)
        self.assertIn("Production, Quality, TDI und General", prompt)
        self.assertIn("Harte Regel: TDI", prompt)
        self.assertIn("Runtime-Hard-Constraints", prompt)
        self.assertNotIn("Template conversation chain", prompt)
        self.assertEqual(chain_state["current_node_label"], "Anfordernden Bereich, Business Owner und First-Version Szenario klaeren")
        production_scope = next(node for node in chain_state["nodes"] if node["node"] == "production_scope")
        self.assertIn("Produkt, Werk, Linie", production_scope["label"])

    def test_ic_substrate_template_prompt_has_malay_expert_chain(self) -> None:
        session = self.service.create_session(
            template_id="qdm_finished_lot_yield_dashboard_template_ms",
            language="ms",
        )

        prompt = self.service._pm_prompt(session, "ms")
        snapshot = self.service.get_structured_requirement_snapshot(session.id, "ms")
        chain_state = snapshot["conversation_chain_state"]

        self.assertIn("Rantaian dialog templat", prompt)
        self.assertIn("Rantaian dialog pakar IC Substrate", prompt)
        self.assertIn("Production, Quality, TDI dan General", prompt)
        self.assertIn("Peraturan keras: tulis TDI hanya sebagai TDI", prompt)
        self.assertIn("Peraturan keras runtime", prompt)
        self.assertNotIn("Template conversation chain", prompt)
        self.assertEqual(chain_state["current_node_label"], "Sahkan jabatan pemohon, business owner dan senario versi pertama")
        production_scope = next(node for node in chain_state["nodes"] if node["node"] == "production_scope")
        self.assertIn("Sahkan product, plant, line", production_scope["label"])

    def test_ic_substrate_runtime_guardrails_follow_template_context(self) -> None:
        session = self.service.create_session(
            template_id="qdm_finished_lot_yield_dashboard_template_zh_cn",
            language="zh",
        )

        prompt = self.service._pm_prompt(session, "zh")

        self.assertGreater(prompt.index("运行时硬约束"), prompt.index("Template context"))
        self.assertIn("本轮 prompt 的最终规则", prompt)
        self.assertIn("每轮只能问一个问题", prompt)
        self.assertIn("模板来源术语只能作为证据，不要自动变成选项", prompt)
        self.assertIn("TDI 只能写作 TDI", prompt)
        self.assertIn("不要自造公式、状态、站点、系统名、缺陷分类、SLA 数字或 owner 角色", prompt)
        self.assertIn("第一问先确认来自哪个入口或首版业务 owner", prompt)

    def test_no_template_ic_substrate_session_preserves_expert_chain_from_cached_model(self) -> None:
        session = self.service.create_session(language="zh")
        self.service._append_message(session.id, "user", "我想做一个电测站点的良率损失dashboard")
        self.service._append_message(
            session.id,
            "user",
            "B. 趋势分析与汇报：生产主管或质量经理需要按班次/日/周查看良率损失结构。",
        )
        self.service._append_message(
            session.id,
            "user",
            "B. 质量经理为主：按产品、测试程序、缺陷类型分析损失结构占比，生产主管可作为辅助使用者。",
        )

        cached_model = self.service._empty_structured_requirement_model()
        cached_model["product_context"]["requesting_department"] = "Quality"
        cached_model["product_context"]["software_type"] = "Dashboard"
        cached_model["background"]["summary"] = "电测站点良率损失 Dashboard，用于 Quality 趋势分析与汇报。"
        self.service._save_structured_requirement_model_cache(
            session.id,
            STRUCTURED_REQUIREMENT_CANONICAL_CACHE_KEY,
            3,
            cached_model,
        )
        self.service._append_message(
            session.id,
            "user",
            "A. 来自电测设备（ATE/测试机）直接上报的测试项目代码。",
        )
        session = self.service._require_session(session.id)

        prompt = self.service._pm_prompt(session, "zh")
        chain_state = self.service.build_conversation_chain_state(session, cached_model, "zh")

        self.assertIn("IC Substrate 专业对话链路", prompt)
        self.assertIn("当前对话链路状态", prompt)
        self.assertIn("链路类型：ic_substrate", prompt)
        self.assertIn("运行时硬约束", prompt)
        self.assertTrue(chain_state["enabled"])
        self.assertEqual(chain_state["mode"], "ic_substrate")
        self.assertEqual(chain_state["intent_track"], "quality")

    def test_ic_substrate_guided_session_exposes_chain_state(self) -> None:
        session = self.service.create_session(
            template_id="qdm_finished_lot_yield_dashboard_template_zh_cn",
            language="zh",
        )

        snapshot = self.service.get_structured_requirement_snapshot(session.id, "zh")
        chain_state = snapshot["conversation_chain_state"]

        self.assertTrue(chain_state["enabled"])
        self.assertEqual(chain_state["mode"], "ic_substrate")
        self.assertEqual(chain_state["current_track"], "Routing")
        self.assertEqual(chain_state["current_node"], "scope_triage")
        self.assertEqual(chain_state["current_node_label"], "确认需求发起部门、业务 owner 和首版场景")
        self.assertEqual(chain_state["current_step_index"], 0)
        self.assertEqual(chain_state["status"], "not_started")
        self.assertEqual(chain_state["next_question_source"], "ic_substrate_department_first_chain")
        self.assertEqual(chain_state["total_steps"], 16)
        self.assertEqual(
            set(chain_state["tracks"]),
            {
                "Production",
                "TDI",
                "Quality",
                "General",
            },
        )
        self.assertEqual(chain_state["nodes"][0]["node"], "scope_triage")
        self.assertEqual(chain_state["nodes"][0]["status"], "current")
        self.assertIn("production_scope", [node["node"] for node in chain_state["nodes"]])
        self.assertIn("production_metrics", [node["node"] for node in chain_state["nodes"]])
        self.assertIn("production_workflow", [node["node"] for node in chain_state["nodes"]])
        self.assertIn("production_data_acceptance", [node["node"] for node in chain_state["nodes"]])
        self.assertIn("tdi_scope", [node["node"] for node in chain_state["nodes"]])
        self.assertIn("tdi_metrics", [node["node"] for node in chain_state["nodes"]])
        self.assertIn("tdi_workflow", [node["node"] for node in chain_state["nodes"]])
        self.assertIn("tdi_data_acceptance", [node["node"] for node in chain_state["nodes"]])
        self.assertIn("quality_scope", [node["node"] for node in chain_state["nodes"]])
        self.assertIn("quality_metrics", [node["node"] for node in chain_state["nodes"]])
        self.assertIn("quality_workflow", [node["node"] for node in chain_state["nodes"]])
        self.assertIn("quality_data_acceptance", [node["node"] for node in chain_state["nodes"]])
        self.assertIn("general_scope", [node["node"] for node in chain_state["nodes"]])
        self.assertIn("general_metrics", [node["node"] for node in chain_state["nodes"]])
        self.assertIn("general_workflow", [node["node"] for node in chain_state["nodes"]])
        self.assertIn("general_data_acceptance", [node["node"] for node in chain_state["nodes"]])
        self.assertNotIn("planning_scope", [node["node"] for node in chain_state["nodes"]])
        self.assertNotIn("finance_metrics", [node["node"] for node in chain_state["nodes"]])
        self.assertNotIn("it_data_data_acceptance", [node["node"] for node in chain_state["nodes"]])

    def test_ic_substrate_active_departments_have_expert_chains(self) -> None:
        session = self.service.create_session(
            template_id="qdm_finished_lot_yield_dashboard_template_zh_cn",
            language="zh",
        )

        snapshot = self.service.get_structured_requirement_snapshot(session.id, "zh")
        nodes = snapshot["conversation_chain_state"]["nodes"]

        for department in (
            "production",
            "tdi",
            "quality",
            "general",
        ):
            with self.subTest(department=department):
                department_nodes = [node["node"] for node in nodes if node["node"].startswith(f"{department}_")]
                self.assertIn(f"{department}_scope", department_nodes)
                self.assertIn(f"{department}_metrics", department_nodes)
                self.assertIn(f"{department}_workflow", department_nodes)
                self.assertIn(f"{department}_data_acceptance", department_nodes)
        hidden_departments = (
            "planning",
            "engineering",
            "equipment",
            "material",
            "warehouse",
            "customer",
            "finance",
            "ehs",
            "it_data",
            "management",
        )
        node_names = [node["node"] for node in nodes]
        for department in hidden_departments:
            with self.subTest(hidden_department=department):
                self.assertFalse(any(node_name.startswith(f"{department}_") for node_name in node_names))

    def test_non_template_session_disables_chain_state(self) -> None:
        session = self.service.create_session(language="en")

        snapshot = self.service.get_structured_requirement_snapshot(session.id, "en")

        self.assertEqual(snapshot["conversation_chain_state"], {"enabled": False})

    def test_prd_generation_strips_embedded_thinking(self) -> None:
        self.llm_client.chat_response = "<think>private reasoning</think>\n# Clean PRD\n\nReady."
        session = self.service.create_session(
            template_id=self.template_id,
            language="en",
        )
        # Seed minimal user message so build_prd_document calls the LLM stub
        self.service.send_user_message(session.id, "We want to track lot yield.", language="en")
        self._cache_ready_requirement_model(session.id)

        result = self.service.build_prd_document(session.id, "en", save_history=False)

        # The LLM-authored core content must appear and the raw <think> tag must never leak through.
        self.assertIn("# Clean PRD", result["document_markdown"])
        self.assertIn("Ready.", result["document_markdown"])
        self.assertNotIn("<think>", result["document_markdown"])
        self.assertNotIn("</think>", result["document_markdown"])

    def test_prd_generation_falls_back_to_template_when_model_returns_empty(self) -> None:
        # When the LLM only produces a <think> block, the parsed body is empty
        # and build_prd_document falls back to the loaded template scaffold.
        self.llm_client.chat_response = "<think>private reasoning only</think>"
        session = self.service.create_session(
            template_id=self.template_id,
            language="en",
        )
        self.service.send_user_message(session.id, "We want to track lot yield.", language="en")
        self._cache_ready_requirement_model(session.id)

        result = self.service.build_prd_document(session.id, "en", save_history=False)

        self.assertTrue(result["document_markdown"].lstrip().startswith("#"))
        self.assertNotIn("<think>", result["document_markdown"])
        self.assertNotIn("</think>", result["document_markdown"])

    def test_prd_generation_blocks_before_readiness(self) -> None:
        session = self.service.create_session(
            template_id=self.template_id,
            language="en",
        )
        self.service.send_user_message(session.id, "We want to track lot yield.", language="en")
        calls_before = len(self.llm_client.calls)

        result = self.service.build_prd_document(session.id, "en", save_history=False)

        self.assertEqual(result["status"], "quality_gate_blocked")
        self.assertIn("Formal Document Quality Gate Not Passed", result["document_markdown"])
        self.assertEqual(len(self.llm_client.calls), calls_before)

    def test_document_generation_messages_include_quality_gate(self) -> None:
        session = self.service.create_session(language="en")
        self.service._append_message(session.id, "user", "We need a cost simulation dashboard.")
        session = self.service.get_session(session.id)
        self.assertIsNotNone(session)
        collection_status = {
            key: {"status": "missing", "reason": "", "pending_questions": []}
            for key in REQUIREMENT_ITEM_KEYS
        }
        collection_status["objective"] = {
            "status": "confirmed",
            "reason": "Business goal is clear.",
            "pending_questions": [],
        }
        collection_status["rules"] = {
            "status": "pending_confirmation",
            "reason": "Formula candidate needs final confirmation.",
            "pending_questions": ["Confirm the cost formula."],
        }
        model = {
            "background": {"objective": "Simulate cost by activity rate.", "summary": ""},
            "collection_status": collection_status,
        }
        progress = self.service._structured_requirement_progress(
            normalize_structured_requirement_model(model),
        )
        chat_messages = self.service._chat_history_messages(session.messages)

        prd_payload = self.service._build_prd_doc_messages(
            session,
            chat_messages,
            model,
            progress,
            "en",
        )[1]["content"]
        design_payload = self.service._build_design_doc_messages(
            session,
            chat_messages,
            model,
            progress,
            "# System Design Document\n\nTBD",
            "en",
        )[1]["content"]

        self.assertIn("Document quality gate", prd_payload)
        self.assertIn("pending_confirmation_items", prd_payload)
        self.assertIn("Do not present captured or pending_confirmation items as confirmed facts", prd_payload)
        self.assertIn("Document quality gate", design_payload)
        self.assertIn("Confirm the cost formula.", design_payload)

    def test_docx_export_uses_word_structure_for_headings_lists_and_tables(self) -> None:
        markdown = "\n".join(
            [
                "# Export Quality",
                "",
                "---",
                "",
                "## Scope",
                "",
                "- First bullet",
                "- **Second bullet** with `code`",
                "",
                "1. First ordered item",
                "2. Second ordered item",
                "",
                "| Area | Status |",
                "|------|--------|",
                "| Objective | Confirmed |",
            ]
        )

        docx_bytes = self.service._markdown_to_docx_bytes(markdown)

        with zipfile.ZipFile(BytesIO(docx_bytes)) as archive:
            names = set(archive.namelist())
            self.assertIn("word/styles.xml", names)
            self.assertIn("word/numbering.xml", names)
            document_xml = archive.read("word/document.xml").decode("utf-8")
            numbering_xml = archive.read("word/numbering.xml").decode("utf-8")

        root = ElementTree.fromstring(document_xml)
        namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

        self.assertEqual(document_xml.count("•"), 0)
        self.assertEqual(document_xml.count("---"), 0)
        self.assertGreaterEqual(len(root.findall(".//w:pStyle", namespace)), 2)
        self.assertGreaterEqual(len(root.findall(".//w:numPr", namespace)), 4)
        self.assertGreaterEqual(len(root.findall(".//w:tblGrid", namespace)), 1)
        self.assertGreaterEqual(len(root.findall(".//w:shd", namespace)), 1)
        self.assertIn('w:val="bullet"', numbering_xml)
        self.assertIn('w:val="decimal"', numbering_xml)

    def test_structured_requirement_prompt_contains_option_a_extraction_rules(self) -> None:
        session = self.service.create_session(language="zh")
        prompt = self.service._structured_requirement_model_prompt(session, "zh")
        self.assertIn("When the user selects Option A", prompt)
        self.assertIn("Identify which blocker label is being confirmed", prompt)
        self.assertIn("Formulate a reasonable, concrete version-one assumption", prompt)
        self.assertIn("Upgrade the status of the corresponding key(s)", prompt)
