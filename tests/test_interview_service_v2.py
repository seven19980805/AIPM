from __future__ import annotations

import json
from copy import deepcopy
import tempfile
import unittest

from app.api import _session_detail_payload
from app.services.interview_state import decision_has_required_evidence_v2
from app.services.requirement_collector import RequirementCollectorService
from app.services.structured_requirement_model import empty_structured_requirement_model
from tests.postgres_test_support import create_postgres_test_store


class ProtocolLLMClient:
    def __init__(self) -> None:
        self.calls: list[list[dict[str, str]]] = []
        self.stream_calls: list[list[dict[str, str]]] = []
        self.structured_model = empty_structured_requirement_model()
        self.stream_text = "Recorded."

    def chat(self, messages, temperature: float = 0.3) -> str:
        self.calls.append(messages)
        return json.dumps(self.structured_model, ensure_ascii=False)

    def stream_chat(self, messages, temperature: float = 0.3):
        self.stream_calls.append(messages)
        yield {"type": "content", "text": self.stream_text}


class InterviewServiceV2Test(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.llm = ProtocolLLMClient()
        self.service = RequirementCollectorService(
            self.llm,
            create_postgres_test_store(self, self.tmpdir.name),
        )
        self.session = self.service.create_session(language="en")

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_request_example_persists_one_server_owned_proposal(self) -> None:
        result = self.service.send_user_message(
            self.session.id,
            "",
            "en",
            reply_context={
                "decision_id": "outcome",
                "action": "request_example",
            },
        )

        self.assertEqual([], self.llm.calls)
        self.assertEqual([], self.llm.stream_calls)
        self.assertEqual(
            "confirm_proposal",
            result["interview_state"]["next_decision"]["mode"],
        )
        stored = self.service.get_session(self.session.id)
        proposal = stored.messages[-1]["metadata"]["interview_turn"]["proposal"]
        self.assertEqual("outcome", proposal["decision_id"])
        self.assertEqual(
            proposal["proposal_id"],
            result["interview_state"]["next_decision"]["proposal"]["proposal_id"],
        )

    def test_free_yes_only_confirms_latest_single_proposal(self) -> None:
        example = self.service.send_user_message(
            self.session.id,
            "",
            "en",
            reply_context={
                "decision_id": "outcome",
                "action": "request_example",
            },
        )
        proposal_id = example["interview_state"]["next_decision"]["proposal"][
            "proposal_id"
        ]

        result = self.service.send_user_message(self.session.id, "yes", "en")

        model = result["structured_requirement_model"]
        self.assertEqual("confirmed", model["collection_status"]["objective"]["status"])
        self.assertEqual("missing", model["collection_status"]["users"]["status"])
        self.assertEqual("", model["product_context"]["primary_user"])
        self.assertEqual(
            "actor_action",
            result["interview_state"]["next_decision"]["decision_id"],
        )
        accepted = self.service.get_session(self.session.id).messages[-1]["metadata"]
        self.assertEqual(proposal_id, accepted["interview_turn"]["accepted_proposal_id"])

    def test_stale_proposal_id_does_not_mutate_the_model(self) -> None:
        self.service.send_user_message(
            self.session.id,
            "",
            "en",
            reply_context={
                "decision_id": "outcome",
                "action": "request_example",
            },
        )

        result = self.service.send_user_message(
            self.session.id,
            "",
            "en",
            reply_context={
                "decision_id": "outcome",
                "action": "accept_proposal",
                "proposal_id": "stale-id",
            },
        )

        self.assertEqual(
            "missing",
            result["structured_requirement_model"]["collection_status"]["objective"][
                "status"
            ],
        )
        self.assertEqual(
            "outcome",
            result["interview_state"]["next_decision"]["decision_id"],
        )
        self.assertIn("proposal", result["assistant_message"].lower())

    def test_streamed_llm_question_never_reaches_assistant_content(self) -> None:
        model = empty_structured_requirement_model()
        model["background"]["objective"] = "Reduce false-fail escapes by 15%."
        model["collection_status"]["objective"].update(
            {
                "status": "confirmed",
                "reason": "The user explicitly stated a measurable result.",
                "pending_questions": [],
            }
        )
        self.llm.structured_model = model
        self.llm.stream_text = (
            "Confirmed:\n"
            "- Outcome: reduce false-fail escapes by 15%.\n\n"
            "Who will use it?\n"
            "A. I will answer now\n"
            "B. Show an example\n"
            "C. Leave pending"
        )

        events = list(
            self.service.stream_user_message(
                self.session.id,
                "Reduce false-fail escapes by 15%.",
                "en",
            )
        )

        visible_content = "".join(
            str(event.get("delta", ""))
            for event in events
            if event.get("event") == "content"
        )
        summary = next(event for event in events if event.get("event") == "summary")
        stored = self.service.get_session(self.session.id).messages[-1]["content"]
        self.assertNotIn("Who will", visible_content)
        self.assertNotIn("A.", visible_content)
        self.assertEqual(visible_content, stored)
        self.assertEqual(
            "actor_action",
            summary["interview_state"]["next_decision"]["decision_id"],
        )

    def test_vague_answer_offers_defer_without_confirming_or_repeating_question(self) -> None:
        model = empty_structured_requirement_model()
        model["background"]["objective"] = "Improve production visibility."
        model["collection_status"]["objective"].update(
            {
                "status": "captured",
                "reason": "The direction is clear but no measurable result is stated.",
                "pending_questions": [
                    "What measurable result should improve?"
                ],
            }
        )
        self.llm.structured_model = model
        self.llm.stream_text = (
            "Captured: improve production visibility.\n\n"
            "What measurable result should improve?"
        )

        events = list(
            self.service.stream_user_message(
                self.session.id,
                "Improve production visibility.",
                "en",
            )
        )

        summary = next(event for event in events if event.get("event") == "summary")
        decision = summary["interview_state"]["next_decision"]
        self.assertEqual("outcome", decision["decision_id"])
        self.assertEqual("free_text", decision["mode"])
        self.assertIsNone(decision["proposal"])
        self.assertTrue(decision["can_defer"])
        self.assertNotEqual(
            "confirmed",
            summary["structured_requirement_model"]["collection_status"]["objective"][
                "status"
            ],
        )

        stored = self.service.get_session(self.session.id).messages[-1]
        self.assertNotIn("What measurable", stored["content"])
        turn = stored["metadata"]["interview_turn"]
        self.assertEqual("outcome", turn["decision_id"])
        self.assertEqual("clarification", turn["kind"])
        self.assertEqual(1, turn["attempt"])

    def test_defer_moves_to_next_evidence_area_and_persists_as_assumption(self) -> None:
        model = empty_structured_requirement_model()
        model["background"]["objective"] = "Improve production visibility."
        model["collection_status"]["objective"].update(
            {
                "status": "captured",
                "reason": "The direction is clear but not measurable.",
                "pending_questions": ["What measurable result should improve?"],
            }
        )
        self.llm.structured_model = model
        self.llm.stream_text = "Captured: improve production visibility."
        list(
            self.service.stream_user_message(
                self.session.id,
                "Improve production visibility.",
                "en",
            )
        )

        result = self.service.send_user_message(
            self.session.id,
            "",
            "en",
            reply_context={
                "decision_id": "outcome",
                "action": "defer_decision",
            },
        )

        self.assertEqual(
            "actor_action",
            result["interview_state"]["next_decision"]["decision_id"],
        )
        self.assertEqual(1, result["interview_state"]["brief"]["assumption_count"])
        self.assertEqual(
            "captured",
            result["structured_requirement_model"]["collection_status"]["objective"][
                "status"
            ],
        )
        stored = self.service.get_session(self.session.id)
        turn = stored.messages[-1]["metadata"]["interview_turn"]
        self.assertEqual("outcome", turn["deferred_decision_id"])
        reloaded_state = self.service.build_interview_state(
            stored,
            result["structured_requirement_model"],
            "en",
        )
        self.assertEqual(
            "actor_action",
            reloaded_state["next_decision"]["decision_id"],
        )
        self.assertEqual(1, reloaded_state["brief"]["assumption_count"])

    def test_second_incomplete_answer_auto_defers_instead_of_asking_again(self) -> None:
        model = empty_structured_requirement_model()
        model["background"]["objective"] = "Improve production visibility."
        model["collection_status"]["objective"].update(
            {
                "status": "captured",
                "reason": "The direction is clear but not measurable.",
                "pending_questions": ["What measurable result should improve?"],
            }
        )
        self.llm.structured_model = model
        self.llm.stream_text = "Captured the direction, but no metric is available."

        list(
            self.service.stream_user_message(
                self.session.id,
                "Improve production visibility.",
                "en",
            )
        )
        events = list(
            self.service.stream_user_message(
                self.session.id,
                "Make it generally easier to see.",
                "en",
            )
        )

        visible_content = "".join(
            str(event.get("delta", ""))
            for event in events
            if event.get("event") == "content"
        )
        summary = next(event for event in events if event.get("event") == "summary")
        self.assertEqual(
            "actor_action",
            summary["interview_state"]["next_decision"]["decision_id"],
        )
        self.assertEqual(1, summary["interview_state"]["brief"]["assumption_count"])
        self.assertIn("TBD", visible_content)
        stored_turn = self.service.get_session(self.session.id).messages[-1][
            "metadata"
        ]["interview_turn"]
        self.assertEqual("deferred", stored_turn["kind"])
        self.assertEqual(
            "clarification_exhausted",
            stored_turn["deferred"]["reason"],
        )
        self.assertEqual("outcome", stored_turn["deferred"]["decision_id"])
        self.assertEqual(
            "Improve production visibility.",
            stored_turn["deferred"]["evidence"],
        )

    def test_deferred_tbd_is_rendered_in_the_build_brief(self) -> None:
        vague_model = empty_structured_requirement_model()
        vague_model["background"]["objective"] = "Improve production visibility."
        vague_model["collection_status"]["objective"].update(
            {
                "status": "captured",
                "reason": "No measurable target yet.",
                "pending_questions": ["What measurable result should improve?"],
            }
        )
        self.llm.structured_model = vague_model
        self.llm.stream_text = "Captured the direction."
        list(
            self.service.stream_user_message(
                self.session.id,
                "Improve production visibility.",
                "en",
            )
        )
        self.service.send_user_message(
            self.session.id,
            "",
            "en",
            reply_context={
                "decision_id": "outcome",
                "action": "defer_decision",
            },
        )

        model = self._fast_ready_model()
        model["background"]["objective"] = "Improve production visibility."
        model["collection_status"]["objective"].update(
            {
                "status": "captured",
                "reason": "No measurable target yet.",
                "pending_questions": ["What measurable result should improve?"],
            }
        )
        self.service.build_structured_requirement_model = lambda *args, **kwargs: model

        result = self.service.build_prd_document(
            self.session.id,
            "en",
            save_history=False,
        )

        self.assertEqual("draft_with_assumptions", result["status"])
        self.assertIn("TBD: Measurable business outcome", result["document_markdown"])
        self.assertIn("Improve production visibility.", result["document_markdown"])

    def test_explicit_actor_answer_advances_even_if_strict_user_completeness_is_pending(self) -> None:
        previous = empty_structured_requirement_model()
        previous["background"]["objective"] = "Reduce false-fail escapes by 15%."
        previous["collection_status"]["objective"].update(
            {
                "status": "confirmed",
                "reason": "Explicitly confirmed.",
                "pending_questions": [],
            }
        )
        self.service._save_interview_model_at_current_message_count(
            self.session,
            previous,
            "en",
        )

        model = deepcopy(previous)
        model["product_context"]["primary_user"] = "Shift supervisor"
        model["users_and_scenarios"].update(
            {
                "target_users": ["Shift supervisor"],
                "core_scenarios": [
                    "Shift supervisor schedules retests from yield trends by product code."
                ],
            }
        )
        model["collection_status"]["users"].update(
            {
                "status": "pending_confirmation",
                "reason": "The primary user is explicit; additional users remain for strict review.",
                "pending_questions": ["Are there any other target users?"],
            }
        )
        model["collection_status"]["scenarios"].update(
            {
                "status": "confirmed",
                "reason": "The business action was explicitly stated.",
                "pending_questions": [],
            }
        )
        self.llm.structured_model = model
        self.llm.stream_text = (
            "Confirmed: The primary user is a shift supervisor, who schedules retests "
            "from yield trends by product code."
        )

        events = list(
            self.service.stream_user_message(
                self.session.id,
                "A shift supervisor schedules retests from yield trends by product code.",
                "en",
            )
        )

        summary = next(event for event in events if event.get("event") == "summary")
        self.assertEqual(2, summary["interview_state"]["brief"]["confirmed_decisions"])
        self.assertEqual(
            "v1_flow",
            summary["interview_state"]["next_decision"]["decision_id"],
        )
        self.assertEqual(
            "confirmed",
            summary["structured_requirement_model"]["collection_status"]["users"][
                "status"
            ],
        )

    def test_explicit_v1_flow_answer_promotes_only_the_active_decision(self) -> None:
        before = empty_structured_requirement_model()
        before["background"]["objective"] = "Reduce false-fail escapes by 15%."
        before["product_context"].update(
            {
                "primary_user": "Shift supervisor",
                "decision_or_action": "Choose lots for retest",
            }
        )
        before["users_and_scenarios"]["target_users"] = ["Shift supervisor"]
        for key in ("objective", "users"):
            before["collection_status"][key].update(
                {
                    "status": "confirmed",
                    "reason": "Explicitly confirmed.",
                    "pending_questions": [],
                }
            )
        self.service._save_interview_model_at_current_message_count(
            self.session,
            before,
            "en",
        )

        extracted = deepcopy(before)
        extracted["scope"].update(
            {
                "in_scope": [
                    "Show yield trends",
                    "Drill into abnormal lots",
                    "Produce a retest list",
                ],
                "out_of_scope": ["Automated disposition"],
            }
        )
        extracted["users_and_scenarios"]["core_scenarios"] = [
            "The supervisor drills into abnormal lots and produces a retest list."
        ]
        extracted["functional_requirements"]["feature_details"] = [
            {
                "feature_name": "Yield trends",
                "description": "Show yield trends.",
            }
        ]
        extracted["collection_status"]["scope"].update(
            {
                "status": "confirmed",
                "reason": "The user explicitly defined the boundary.",
                "pending_questions": [],
            }
        )
        extracted["collection_status"]["scenarios"].update(
            {
                "status": "captured",
                "reason": "The scenario was extracted from the explicit answer.",
                "pending_questions": [],
            }
        )
        extracted["collection_status"]["features"].update(
            {
                "status": "pending_confirmation",
                "reason": "The features were extracted from the explicit answer.",
                "pending_questions": ["What are the specific features needed?"],
            }
        )
        self.llm.structured_model = extracted
        self.llm.stream_text = (
            "Confirmed first-release scope and core scenario."
        )

        events = list(
            self.service.stream_user_message(
                self.session.id,
                (
                    "V1 shows yield trends, lets the supervisor drill into abnormal "
                    "lots, and produces a retest list; automated disposition is out."
                ),
                "en",
            )
        )

        summary = next(event for event in events if event.get("event") == "summary")
        model = summary["structured_requirement_model"]
        self.assertEqual("confirmed", model["collection_status"]["scope"]["status"])
        self.assertEqual("confirmed", model["collection_status"]["scenarios"]["status"])
        self.assertEqual("confirmed", model["collection_status"]["features"]["status"])
        self.assertEqual(
            "data_boundary",
            summary["interview_state"]["next_decision"]["decision_id"],
        )
        self.assertEqual(
            "missing",
            model["collection_status"]["integrations"]["status"],
        )

    def test_v1_flow_advances_when_extractor_omits_scenario_and_overview(self) -> None:
        before = empty_structured_requirement_model()
        before["background"]["objective"] = "Reduce defect escapes by 15%."
        before["product_context"].update(
            {
                "primary_user": "Quality engineer",
                "decision_or_action": (
                    "Decide which product and lot to investigate first"
                ),
            }
        )
        before["users_and_scenarios"]["target_users"] = ["Quality engineer"]
        for key in ("objective", "users"):
            before["collection_status"][key]["status"] = "confirmed"
        self.service._save_interview_model_at_current_message_count(
            self.session,
            before,
            "en",
        )

        extracted = deepcopy(before)
        extracted["scope"].update(
            {
                "in_scope": [
                    "Show defect trends",
                    "Affected lots with drill-down",
                ],
                "out_of_scope": ["Automated disposition"],
            }
        )
        extracted["collection_status"]["scope"]["status"] = "confirmed"
        extracted["collection_status"]["features"]["status"] = "confirmed"
        self.llm.structured_model = extracted
        self.llm.stream_text = (
            "Confirmed first-release scenario and scope: Show defect trends; "
            "Affected lots with drill-down."
        )

        events = list(
            self.service.stream_user_message(
                self.session.id,
                (
                    "Show defect trends and affected lots with drill-down; "
                    "automated disposition is out of scope."
                ),
                "en",
            )
        )

        summary = next(event for event in events if event.get("event") == "summary")
        model = summary["structured_requirement_model"]
        self.assertTrue(model["users_and_scenarios"]["core_scenarios"])
        self.assertTrue(model["functional_requirements"]["overview"])
        self.assertEqual(
            "data_boundary",
            summary["interview_state"]["next_decision"]["decision_id"],
        )
        for key in ("scope", "scenarios", "features"):
            self.assertEqual(
                "confirmed",
                model["collection_status"][key]["status"],
            )

    def test_chinese_v1_flow_option_advances_when_extractor_omits_scenario(self) -> None:
        before = empty_structured_requirement_model()
        before["background"]["objective"] = "下季度将缺陷漏出率降低 15%。"
        before["product_context"].update(
            {
                "primary_user": "质量工程师",
                "decision_or_action": "决定优先调查的产品和批次",
            }
        )
        before["users_and_scenarios"]["target_users"] = ["质量工程师"]
        for key in ("objective", "users"):
            before["collection_status"][key]["status"] = "confirmed"
        self.service._save_interview_model_at_current_message_count(
            self.session,
            before,
            "zh",
        )

        extracted = deepcopy(before)
        extracted["scope"].update(
            {
                "in_scope": ["展示缺陷趋势", "受影响批次下钻"],
                "out_of_scope": ["自动判定"],
            }
        )
        extracted["collection_status"]["scope"]["status"] = "confirmed"
        self.llm.structured_model = extracted
        self.llm.stream_text = "已确认首版场景与范围。"

        events = list(
            self.service.stream_user_message(
                self.session.id,
                "首版展示缺陷趋势和受影响批次并支持下钻；不包含自动判定。",
                "zh",
            )
        )

        summary = next(event for event in events if event.get("event") == "summary")
        model = summary["structured_requirement_model"]
        self.assertTrue(model["users_and_scenarios"]["core_scenarios"])
        self.assertTrue(model["functional_requirements"]["overview"])
        self.assertEqual(
            "data_boundary",
            summary["interview_state"]["next_decision"]["decision_id"],
        )
        for key in ("scope", "scenarios", "features"):
            self.assertEqual(
                "confirmed",
                model["collection_status"][key]["status"],
            )

    def test_one_broad_answer_advances_every_evidence_valid_fast_decision(self) -> None:
        before = empty_structured_requirement_model()
        self.service._save_interview_model_at_current_message_count(
            self.session,
            before,
            "en",
        )

        extracted = deepcopy(before)
        extracted["background"]["objective"] = (
            "Reduce risky-batch identification time to under 3 minutes."
        )
        extracted["product_context"].update(
            {
                "primary_user": "Bakery manager",
                "decision_or_action": "Choose which batches to remake",
            }
        )
        extracted["users_and_scenarios"].update(
            {
                "target_users": ["Bakery manager"],
                "core_scenarios": [
                    "Review batch defect trends and choose batches to remake."
                ],
            }
        )
        extracted["scope"].update(
            {
                "in_scope": ["Show batch defect trends and alerts"],
                "out_of_scope": ["Automated disposal"],
            }
        )
        extracted["functional_requirements"]["overview"] = (
            "Dashboard for batch defect trends and alerts."
        )
        extracted["data_and_dependencies"] = [
            "Read-only fictional CSV upload keyed by synthetic batch ID.",
            "Refresh every 30 minutes.",
        ]
        extracted["acceptance_criteria"] = [
            "The manager identifies risky batches within 3 minutes.",
            "The dashboard matches a 20-row fixture exactly.",
        ]
        for key in (
            "objective",
            "users",
            "scope",
            "scenarios",
            "features",
            "integrations",
            "acceptance",
        ):
            extracted["collection_status"][key].update(
                {
                    "status": "captured",
                    "reason": "Extracted from the user's broad answer.",
                    "pending_questions": [],
                }
            )
        self.llm.structured_model = extracted
        self.llm.stream_text = "Captured the requested outcome and first-release evidence."

        events = list(
            self.service.stream_user_message(
                self.session.id,
                (
                    "Reduce risky-batch identification time to under 3 minutes. "
                    "A bakery manager uses a dashboard to choose which batches to remake. "
                    "V1 shows defect trends and alerts; automated disposal is out. "
                    "Use a read-only fictional CSV refreshed every 30 minutes and keyed by "
                    "synthetic batch ID. Acceptance is a decision within 3 minutes and an "
                    "exact match against a 20-row fixture."
                ),
                "en",
            )
        )

        summary = next(event for event in events if event.get("event") == "summary")
        state = summary["interview_state"]
        model = summary["structured_requirement_model"]
        self.assertEqual(5, state["brief"]["confirmed_decisions"])
        self.assertEqual("brief_ready", state["stage"])
        self.assertTrue(state["actions"]["can_generate_brief"])
        self.assertEqual(
            "pending_confirmation",
            model["collection_status"]["users"]["status"],
        )
        self.assertEqual(
            "pending_confirmation",
            model["collection_status"]["scenarios"]["status"],
        )
        self.assertEqual(
            "pending_confirmation",
            model["collection_status"]["features"]["status"],
        )

    def test_non_active_hallucinated_evidence_is_not_promoted_without_turn_grounding(
        self,
    ) -> None:
        before = empty_structured_requirement_model()
        before["background"]["objective"] = (
            "Reduce risky-batch identification time to under 3 minutes."
        )
        before["collection_status"]["objective"].update(
            {
                "status": "confirmed",
                "reason": "Explicitly confirmed.",
                "pending_questions": [],
            }
        )
        self.service._save_interview_model_at_current_message_count(
            self.session,
            before,
            "en",
        )

        extracted = deepcopy(before)
        extracted["product_context"].update(
            {
                "primary_user": "Bakery manager",
                "decision_or_action": "Choose which batches to remake",
            }
        )
        extracted["users_and_scenarios"].update(
            {
                "target_users": ["Bakery manager"],
                "core_scenarios": [
                    "Inspect a fabricated defect dashboard before remaking a batch."
                ],
            }
        )
        extracted["scope"].update(
            {
                "in_scope": ["Fabricated defect dashboard and alerts"],
                "out_of_scope": ["Automated disposal"],
            }
        )
        extracted["functional_requirements"]["overview"] = (
            "Fabricated defect dashboard and alerts."
        )
        extracted["data_and_dependencies"] = [
            "Read-only fabricated SQL view refreshed every 15 minutes."
        ]
        extracted["acceptance_criteria"] = [
            "The fabricated dashboard matches the source within 1%."
        ]
        for key, status in {
            "users": "captured",
            "scope": "confirmed",
            "scenarios": "captured",
            "features": "captured",
            "integrations": "captured",
            "acceptance": "captured",
        }.items():
            extracted["collection_status"][key].update(
                {
                    "status": status,
                    "reason": "Extractor output.",
                    "pending_questions": [],
                }
            )
        self.llm.structured_model = extracted
        self.llm.stream_text = "Captured the user and action."

        events = list(
            self.service.stream_user_message(
                self.session.id,
                "A bakery manager decides which batches to remake.",
                "en",
            )
        )

        summary = next(event for event in events if event.get("event") == "summary")
        state = summary["interview_state"]
        model = summary["structured_requirement_model"]
        self.assertEqual(2, state["brief"]["confirmed_decisions"])
        self.assertEqual("v1_flow", state["next_decision"]["decision_id"])
        self.assertEqual(
            "captured",
            model["collection_status"]["scenarios"]["status"],
        )
        self.assertEqual(
            "captured",
            model["collection_status"]["features"]["status"],
        )
        self.assertEqual(
            "captured",
            model["collection_status"]["integrations"]["status"],
        )
        self.assertEqual(
            "captured",
            model["collection_status"]["acceptance"]["status"],
        )
        self.assertEqual([], model["users_and_scenarios"]["core_scenarios"])
        self.assertEqual([], model["scope"]["in_scope"])
        self.assertEqual([], model["scope"]["out_of_scope"])
        self.assertEqual("", model["functional_requirements"]["overview"])
        self.assertEqual([], model["data_and_dependencies"])
        self.assertEqual([], model["acceptance_criteria"])

    def test_mixed_grounded_and_hallucinated_fragments_do_not_promote_a_decision(
        self,
    ) -> None:
        previous = empty_structured_requirement_model()
        current = deepcopy(previous)
        current["scope"].update(
            {
                "in_scope": [
                    "Show yield trends",
                    "Send SMS alerts to the CFO",
                ],
                "out_of_scope": ["Automated disposition"],
            }
        )

        self.assertFalse(
            self.service._decision_has_turn_grounded_evidence(
                previous,
                current,
                (("scope.in_scope", "scope.out_of_scope"),),
                (
                    "V1 shows yield trends; automated disposition is out. "
                    "No SMS alerts or CFO workflow was requested."
                ),
            )
        )

    def test_grounding_rejects_reversed_polarity_and_mismatched_units(self) -> None:
        bad_pairs = (
            ("Writeback is allowed", "Writeback is not allowed."),
            ("允许回写", "不允许回写。"),
            ("自动处置", "不包含自动处置。"),
            (
                "Reduce cycle time to 15 hours",
                "Reduce cycle time to 15 minutes.",
            ),
        )
        for fragment, user_message in bad_pairs:
            with self.subTest(fragment=fragment, user_message=user_message):
                self.assertFalse(
                    self.service._text_fragment_is_grounded(
                        fragment,
                        user_message,
                    )
                )

        self.assertTrue(
            self.service._text_fragment_is_grounded(
                "Reduce cycle time to 15 minutes",
                "Reduce cycle time to 15 minutes.",
            )
        )

    def test_approved_shop_floor_and_cjk_upload_answers_are_captured(self) -> None:
        answers = {
            "qis": "Read inspection results from QIS, read-only, refreshed hourly.",
            "qms": "Read CAPA records from QMS, read-only, refreshed hourly.",
            "cjk_upload": "由用户手动上传良率数据，首版只读，每小时刷新。",
        }

        for label, user_message in answers.items():
            with self.subTest(source=label):
                previous = self._fast_ready_model()
                previous["data_and_dependencies"] = []
                previous["collection_status"]["integrations"].update(
                    {"status": "missing", "reason": "", "pending_questions": []}
                )
                extracted = deepcopy(previous)

                promoted = self.service._promote_explicit_active_decision_answer(
                    self.session,
                    previous_model=previous,
                    extracted_model=extracted,
                    decision_id="data_boundary",
                    user_message=user_message,
                    language="zh" if label == "cjk_upload" else "en",
                )

                self.assertTrue(
                    promoted["data_and_dependencies"],
                    f"{label} answer must reach the structured model",
                )

    def test_explicit_data_boundary_survives_extractor_omission(self) -> None:
        previous = self._fast_ready_model()
        previous["data_and_dependencies"] = []
        previous["acceptance_criteria"] = []
        for key in ("integrations", "acceptance"):
            previous["collection_status"][key].update(
                {
                    "status": "missing",
                    "reason": "",
                    "pending_questions": [],
                }
            )
        self.service._save_interview_model_at_current_message_count(
            self.session,
            previous,
            "en",
        )

        extracted = deepcopy(previous)
        extracted["data_and_dependencies"] = [
            "Refresh the dashboard every 30 minutes."
        ]
        extracted["collection_status"]["integrations"].update(
            {
                "status": "captured",
                "reason": "The extractor retained cadence but omitted the source.",
                "pending_questions": [],
            }
        )
        user_message = (
            "Use a read-only fictional CSV refreshed every 30 minutes and keyed "
            "by synthetic lot ID."
        )

        promoted = self.service._promote_explicit_active_decision_answer(
            self.session,
            previous_model=previous,
            extracted_model=extracted,
            decision_id="data_boundary",
            user_message=user_message,
            language="en",
        )

        self.assertEqual(
            "confirmed",
            promoted["collection_status"]["integrations"]["status"],
        )
        self.assertTrue(
            any(
                "read-only fictional CSV" in item
                for item in promoted["data_and_dependencies"]
            )
        )
        self.assertTrue(
            decision_has_required_evidence_v2(promoted, "data_boundary")
        )

    def test_next_decision_preserves_previously_confirmed_list_evidence(self) -> None:
        previous = self._fast_ready_model()
        original_scope = list(previous["scope"]["in_scope"])
        previous["data_and_dependencies"] = []
        previous["acceptance_criteria"] = []
        for key in ("integrations", "acceptance"):
            previous["collection_status"][key].update(
                {
                    "status": "missing",
                    "reason": "",
                    "pending_questions": [],
                }
            )

        extracted = deepcopy(previous)
        extracted["scope"]["in_scope"] = [
            "A paraphrased dashboard scope not stated in this turn."
        ]
        extracted["data_and_dependencies"] = [
            "Read approved SAP quality data with writeback disabled."
        ]
        extracted["collection_status"]["integrations"].update(
            {
                "status": "captured",
                "reason": "Extractor output.",
                "pending_questions": [],
            }
        )
        user_message = (
            "Read from SQL Server and keep the first release read-only with no "
            "source-system writeback."
        )

        promoted = self.service._promote_explicit_active_decision_answer(
            self.session,
            previous_model=previous,
            extracted_model=extracted,
            decision_id="data_boundary",
            user_message=user_message,
            language="en",
        )

        self.assertEqual(original_scope, promoted["scope"]["in_scope"])
        self.assertTrue(decision_has_required_evidence_v2(promoted, "v1_flow"))
        self.assertTrue(
            any(
                "SQL Server" in item
                for item in promoted["data_and_dependencies"]
            )
        )
        self.assertFalse(
            any(
                "SAP quality data" in item
                for item in promoted["data_and_dependencies"]
            )
        )
        self.assertEqual(
            "confirmed",
            promoted["collection_status"]["integrations"]["status"],
        )

    def test_explicit_acceptance_evidence_survives_extractor_omission(self) -> None:
        previous = self._fast_ready_model()
        previous["acceptance_criteria"] = []
        previous["collection_status"]["acceptance"].update(
            {
                "status": "missing",
                "reason": "",
                "pending_questions": [],
            }
        )
        extracted = deepcopy(previous)
        user_message = (
            "The quality engineer can identify the top defect and affected "
            "lots within five minutes."
        )

        promoted = self.service._promote_explicit_active_decision_answer(
            self.session,
            previous_model=previous,
            extracted_model=extracted,
            decision_id="acceptance",
            user_message=user_message,
            language="en",
        )

        self.assertIn(user_message.rstrip("."), promoted["acceptance_criteria"])
        self.assertEqual(
            "confirmed",
            promoted["collection_status"]["acceptance"]["status"],
        )
        self.assertTrue(decision_has_required_evidence_v2(promoted, "acceptance"))

    def test_acceptance_evidence_deduplicates_spacing_variants(self) -> None:
        previous = self._fast_ready_model()
        previous["acceptance_criteria"] = []
        previous["collection_status"]["acceptance"]["status"] = "missing"
        extracted = deepcopy(previous)
        extracted["acceptance_criteria"] = [
            "质量工程师能在5分钟内找出首要缺陷及受影响批次"
        ]
        extracted["collection_status"]["acceptance"]["status"] = "captured"

        promoted = self.service._promote_explicit_active_decision_answer(
            self.session,
            previous_model=previous,
            extracted_model=extracted,
            decision_id="acceptance",
            user_message="质量工程师能在 5 分钟内找出首要缺陷及受影响批次。",
            language="zh",
        )

        self.assertEqual(1, len(promoted["acceptance_criteria"]))
        self.assertEqual(
            "confirmed",
            promoted["collection_status"]["acceptance"]["status"],
        )

    def test_chinese_authoritative_summary_uses_native_punctuation(self) -> None:
        model = self._fast_ready_model()
        model["acceptance_criteria"] = [
            "质量工程师能在 5 分钟内找出首要缺陷及受影响批次"
        ]

        summary = self.service._authoritative_interview_summary(
            model,
            "acceptance",
            "zh",
        )

        self.assertEqual(
            "已确认验收证据：质量工程师能在 5 分钟内找出首要缺陷及受影响批次。",
            summary,
        )

    def test_assistant_summary_uses_the_active_decision_label(self) -> None:
        previous = empty_structured_requirement_model()
        previous["background"]["objective"] = "Reduce escapes by 15%."
        previous["collection_status"]["objective"].update(
            {
                "status": "confirmed",
                "reason": "Explicitly confirmed.",
                "pending_questions": [],
            }
        )
        self.service._save_interview_model_at_current_message_count(
            self.session,
            previous,
            "en",
        )

        extracted = deepcopy(previous)
        extracted["product_context"].update(
            {
                "primary_user": "Quality engineer",
                "decision_or_action": "Prioritize affected lots for investigation",
            }
        )
        extracted["users_and_scenarios"]["target_users"] = ["Quality engineer"]
        extracted["collection_status"]["users"].update(
            {
                "status": "captured",
                "reason": "Extractor output.",
                "pending_questions": [],
            }
        )
        self.llm.structured_model = extracted
        self.llm.stream_text = "Confirmed core scenario: investigate affected lots."

        events = list(
            self.service.stream_user_message(
                self.session.id,
                (
                    "A quality engineer uses defect trends to prioritize "
                    "affected lots for investigation."
                ),
                "en",
            )
        )

        content = next(
            event["delta"]
            for event in events
            if event.get("event") == "content"
        )
        summary = next(event for event in events if event.get("event") == "summary")
        self.assertIn("Confirmed user and business action:", content)
        self.assertNotIn("core scenario", content.casefold())
        self.assertEqual(
            "v1_flow",
            summary["interview_state"]["next_decision"]["decision_id"],
        )

    def test_explicit_measurable_outcome_survives_extractor_paraphrase(self) -> None:
        previous = empty_structured_requirement_model()
        extracted = deepcopy(previous)
        extracted["background"]["objective"] = (
            "Enable the supervisor to identify risky lots quickly."
        )
        extracted["collection_status"]["objective"].update(
            {
                "status": "captured",
                "reason": "The extractor paraphrased away the target.",
                "pending_questions": [],
            }
        )
        user_message = (
            "Reduce risky-lot identification time to under 3 minutes."
        )

        promoted = self.service._promote_explicit_active_decision_answer(
            self.session,
            previous_model=previous,
            extracted_model=extracted,
            decision_id="outcome",
            user_message=user_message,
            language="en",
        )

        self.assertEqual(
            user_message.rstrip("."),
            promoted["background"]["objective"],
        )
        self.assertEqual(
            "confirmed",
            promoted["collection_status"]["objective"]["status"],
        )
        self.assertTrue(
            decision_has_required_evidence_v2(promoted, "outcome")
        )

    def test_clarification_question_does_not_promote_speculative_v1_flow_evidence(self) -> None:
        before = empty_structured_requirement_model()
        before["background"]["objective"] = "Reduce false-fail escapes by 15%."
        before["product_context"].update(
            {
                "primary_user": "Shift supervisor",
                "decision_or_action": "Choose lots for retest",
            }
        )
        before["users_and_scenarios"]["target_users"] = ["Shift supervisor"]
        for key in ("objective", "users"):
            before["collection_status"][key]["status"] = "confirmed"
        self.service._save_interview_model_at_current_message_count(
            self.session,
            before,
            "en",
        )

        speculative = deepcopy(before)
        speculative["scope"]["in_scope"] = ["Automated disposition"]
        speculative["users_and_scenarios"]["core_scenarios"] = [
            "Automatically dispose abnormal lots."
        ]
        speculative["functional_requirements"]["overview"] = (
            "Automatically dispose abnormal lots."
        )
        for key in ("scope", "scenarios", "features"):
            speculative["collection_status"][key]["status"] = "captured"
        self.llm.structured_model = speculative
        self.llm.stream_text = "Automated disposition would expand the first release."

        events = list(
            self.service.stream_user_message(
                self.session.id,
                "Should V1 include automated disposition?",
                "en",
            )
        )

        summary = next(event for event in events if event.get("event") == "summary")
        self.assertEqual(
            "v1_flow",
            summary["interview_state"]["next_decision"]["decision_id"],
        )
        for key in ("scope", "scenarios", "features"):
            self.assertNotEqual(
                "confirmed",
                summary["structured_requirement_model"]["collection_status"][key][
                    "status"
                ],
            )

    def test_off_topic_statement_does_not_fabricate_v1_flow_evidence(self) -> None:
        before = empty_structured_requirement_model()
        before["background"]["objective"] = "Reduce defect escapes by 15%."
        before["product_context"].update(
            {
                "primary_user": "Quality engineer",
                "decision_or_action": "Decide which lot to investigate first",
            }
        )
        before["users_and_scenarios"]["target_users"] = ["Quality engineer"]
        for key in ("objective", "users"):
            before["collection_status"][key]["status"] = "confirmed"
        self.service._save_interview_model_at_current_message_count(
            self.session,
            before,
            "en",
        )

        self.llm.structured_model = deepcopy(before)
        self.llm.stream_text = "Understood. Let me know once your team has decided."

        off_topic = "Let me check with my team tomorrow and get back to you."
        events = list(
            self.service.stream_user_message(
                self.session.id,
                off_topic,
                "en",
            )
        )

        summary = next(event for event in events if event.get("event") == "summary")
        model = summary["structured_requirement_model"]
        self.assertEqual(
            "v1_flow",
            summary["interview_state"]["next_decision"]["decision_id"],
        )
        for key in ("scope", "scenarios", "features"):
            self.assertNotEqual(
                "confirmed",
                model["collection_status"][key]["status"],
            )
        self.assertEqual([], model["scope"]["in_scope"])
        self.assertEqual([], model["users_and_scenarios"]["core_scenarios"])
        self.assertEqual("", model["functional_requirements"]["overview"])

    def test_session_payload_exposes_the_same_authoritative_state(self) -> None:
        payload = _session_detail_payload(self.service, self.session, "zh")

        self.assertEqual("2.0", payload["interview_state"]["schema_version"])
        self.assertEqual(
            payload["interview_state"],
            payload["launch_context"]["interview_state"],
        )

    def test_five_fast_decisions_unlock_build_brief_before_strict_review(self) -> None:
        model = self._fast_ready_model()
        self.service._append_message(self.session.id, "user", "Seed the fast decisions.")
        self.service.build_structured_requirement_model = lambda *args, **kwargs: model

        result = self.service.build_prd_document(
            self.session.id,
            "en",
            save_history=False,
        )

        self.assertEqual("draft_with_assumptions", result["status"])
        self.assertIn("Build Brief", result["document_markdown"])

    def test_saved_brief_uses_model_fingerprint_and_becomes_stale_on_change(self) -> None:
        model = self._fast_ready_model()
        self.service._append_message(self.session.id, "user", "Seed the fast decisions.")
        session = self.service.get_session(self.session.id)
        self.service._save_interview_model_at_current_message_count(
            session,
            model,
            "en",
        )
        self.service.build_structured_requirement_model = lambda *args, **kwargs: model

        self.service.build_prd_document(self.session.id, "en", save_history=True)

        session_with_brief = self.service.get_session(self.session.id)
        document_message = next(
            message
            for message in session_with_brief.messages
            if message["kind"] == "prd_doc"
        )
        self.assertTrue(
            document_message["metadata"]["document"]["source_model_fingerprint"]
        )
        current_state = self.service.build_interview_state(
            session_with_brief,
            model,
            "en",
        )
        self.assertEqual("current", current_state["brief"]["document_status"])

        changed = deepcopy(model)
        changed["business_rules"] = ["Only Quality may change the yield threshold."]
        changed["collection_status"]["rules"].update(
            {
                "status": "confirmed",
                "reason": "Explicitly confirmed.",
                "pending_questions": [],
            }
        )
        self.service._save_interview_model_at_current_message_count(
            session_with_brief,
            changed,
            "en",
        )
        stale_state = self.service.build_interview_state(
            self.service.get_session(self.session.id),
            changed,
            "en",
        )
        self.assertEqual("stale", stale_state["brief"]["document_status"])

    def test_strict_review_stops_prompting_after_two_free_text_turns(self) -> None:
        model = self._fast_ready_model()
        self.service._append_message(self.session.id, "user", "Seed the fast decisions.")
        session = self.service.get_session(self.session.id)
        self.service._save_interview_model_at_current_message_count(
            session,
            model,
            "en",
        )
        self.service.build_structured_requirement_model = lambda *args, **kwargs: model
        self.service.build_prd_document(self.session.id, "en", save_history=True)

        self.llm.structured_model = model
        self.llm.stream_text = "No additional delivery evidence was confirmed."
        first = list(
            self.service.stream_user_message(
                self.session.id,
                "I do not know those details yet.",
                "en",
            )
        )
        first_summary = next(
            event for event in first if event.get("event") == "summary"
        )
        self.assertEqual(
            "question",
            first_summary["interview_state"]["review"]["input_mode"],
        )
        self.assertEqual(
            1,
            first_summary["interview_state"]["review"]["asked_count"],
        )

        second = list(
            self.service.stream_user_message(
                self.session.id,
                "They are still not available.",
                "en",
            )
        )
        second_summary = next(
            event for event in second if event.get("event") == "summary"
        )
        state = second_summary["interview_state"]
        self.assertEqual("strict_review", state["stage"])
        self.assertEqual("manual", state["review"]["input_mode"])
        self.assertEqual(2, state["review"]["asked_count"])
        self.assertIsNone(state["next_decision"])
        self.assertFalse(state["actions"]["can_handoff"])

    def test_strict_review_explanation_questions_do_not_consume_the_turn_cap(
        self,
    ) -> None:
        model = self._fast_ready_model()
        self.service._append_message(self.session.id, "user", "Seed the fast decisions.")
        session = self.service.get_session(self.session.id)
        self.service._save_interview_model_at_current_message_count(
            session,
            model,
            "en",
        )
        self.service.build_structured_requirement_model = lambda *args, **kwargs: model
        self.service.build_prd_document(self.session.id, "en", save_history=True)

        self.service._append_message(
            self.session.id,
            "user",
            "What does that mean?",
        )
        self.service._append_message(
            self.session.id,
            "user",
            "Why do you need it?",
        )

        session = self.service.get_session(self.session.id)
        self.assertEqual(
            0,
            self.service._strict_review_user_turn_count(session.messages),
        )
        state = self.service.build_interview_state(session, model, "en")
        self.assertEqual("question", state["review"]["input_mode"])
        self.assertIsNotNone(state["next_decision"])

    def test_handoff_requires_confirmed_ownership_and_a_current_brief(self) -> None:
        model = self._fast_ready_model()
        model["data_and_dependencies"] = [
            "Read-only SQL Server view dbo.v_e_test_results; no source-system writeback.",
            "Join by lot_id and product_code; fields include yield_pct and loss_code.",
            "Refresh the view every five minutes.",
        ]
        model["business_rules"] = ["Only Quality may change the yield threshold."]
        model["collection_status"]["rules"].update(
            {
                "status": "confirmed",
                "reason": "Explicitly confirmed.",
                "pending_questions": [],
            }
        )
        model["product_context"].update(
            {
                "business_owner": "Manufacturing Manager",
                "acceptance_owner": "Quality Manager",
            }
        )
        self.service._append_message(self.session.id, "user", "Seed strict review.")
        session = self.service.get_session(self.session.id)
        self.service._save_interview_model_at_current_message_count(session, model, "en")
        active_model = {"value": model}
        self.service.build_structured_requirement_model = (
            lambda *args, **kwargs: active_model["value"]
        )
        self.service.build_prd_document(self.session.id, "en", save_history=True)

        ownership_blocked = self.service.build_browser_handoff_payload(
            self.session.id,
            "en",
        )

        self.assertFalse(ownership_blocked["handoff_ready"])
        self.assertEqual(
            "ownership",
            ownership_blocked["interview_state"]["next_decision"]["decision_id"],
        )

        confirmed = deepcopy(model)
        confirmed["collection_status"]["ownership"].update(
            {
                "status": "confirmed",
                "reason": "Both owners were explicitly confirmed.",
                "pending_questions": [],
            }
        )
        self.service._save_interview_model_at_current_message_count(
            self.service.get_session(self.session.id),
            confirmed,
            "en",
        )
        active_model["value"] = confirmed
        stale = self.service.build_browser_handoff_payload(self.session.id, "en")
        self.assertFalse(stale["handoff_ready"])
        self.assertEqual("stale", stale["interview_state"]["brief"]["document_status"])

        self.service.build_prd_document(self.session.id, "en", save_history=True)
        ready = self.service.build_browser_handoff_payload(self.session.id, "en")
        self.assertTrue(ready["handoff_ready"])
        self.assertEqual("handoff_ready", ready["interview_state"]["stage"])

    @staticmethod
    def _fast_ready_model() -> dict:
        model = empty_structured_requirement_model()
        model["background"]["objective"] = "Reduce escapes by 15%."
        model["product_context"].update(
            {
                "primary_user": "Shift supervisor",
                "decision_or_action": "Schedule retests",
            }
        )
        model["users_and_scenarios"].update(
            {
                "target_users": ["Shift supervisor"],
                "core_scenarios": ["Inspect abnormal lots and schedule retests"],
            }
        )
        model["scope"]["in_scope"] = ["Yield dashboard"]
        model["functional_requirements"]["overview"] = "Yield trend and lot drill-down"
        model["data_and_dependencies"] = [
            "Read-only SQL Server e-test results",
            "No source-system writeback",
        ]
        model["acceptance_criteria"] = ["Latest lot is visible within five minutes"]
        for key in (
            "objective",
            "users",
            "scope",
            "scenarios",
            "features",
            "integrations",
            "acceptance",
        ):
            model["collection_status"][key].update(
                {
                    "status": "confirmed",
                    "reason": "Explicitly confirmed.",
                    "pending_questions": [],
                }
            )
        return model


if __name__ == "__main__":
    unittest.main()
