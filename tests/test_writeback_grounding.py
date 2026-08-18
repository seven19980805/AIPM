"""Writeback authorization must come from the user's own words.

The four authorization fields ride the same turn-grounding chain as every other
evidence field, and they may only change while the writeback decision is the
active one. An extractor cannot invent them, a side-branch answer cannot leak
into them, and a stale authorization cannot outlive the source it named.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from copy import deepcopy

from app.services.interview_protocol import (
    ProposalValidationError,
    build_decision_proposal,
)
from app.services.interview_state import decision_has_required_evidence_v2
from app.services.requirement_collector import RequirementCollectorService
from app.services.structured_requirement_model import (
    empty_structured_requirement_model,
)
from tests.postgres_test_support import create_postgres_test_store


AUTHORIZATION = {
    "target_system": "MES",
    "action": "Post the QA disposition to the lot record",
    "authorization_owner": "Quality manager",
    "acceptance_evidence": "MES shows the posted disposition within 5 minutes.",
}

WRITEBACK_ANSWER = (
    "Write back to MES: post the QA disposition to the lot record, authorized by "
    "the Quality manager; MES shows the posted disposition within 5 minutes."
)


class GroundingLLM:
    def __init__(self) -> None:
        self.structured_model = empty_structured_requirement_model()
        self.stream_text = "Recorded."

    def chat(self, messages, temperature: float = 0.3) -> str:
        return json.dumps(self.structured_model, ensure_ascii=False)

    def stream_chat(self, messages, temperature: float = 0.3):
        yield {"type": "content", "text": self.stream_text}


class WritebackGroundingTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.llm = GroundingLLM()
        self.service = RequirementCollectorService(
            self.llm,
            create_postgres_test_store(self, self.tmpdir.name),
        )
        self.session = self.service.create_session(language="en")

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def _base_model(self) -> dict:
        model = empty_structured_requirement_model()
        model["data_and_dependencies"] = [
            "Read lot records from MES; the first release is read-only.",
            "Write the disposition back to MES by posting the QA decision.",
        ]
        return model

    def _promote(self, previous, extracted, decision_id, user_message):
        return self.service._promote_explicit_active_decision_answer(
            self.session,
            previous_model=previous,
            extracted_model=extracted,
            decision_id=decision_id,
            user_message=user_message,
            language="en",
        )

    def test_extractor_cannot_invent_an_authorization(self) -> None:
        previous = self._base_model()
        extracted = deepcopy(previous)
        extracted["writeback_authorization"] = dict(AUTHORIZATION)

        promoted = self._promote(
            previous,
            extracted,
            "writeback",
            "Yes, writeback to MES would be useful eventually.",
        )

        authorization = promoted["writeback_authorization"]
        self.assertEqual("", authorization["authorization_owner"])
        self.assertEqual("", authorization["acceptance_evidence"])
        self.assertEqual("pending", authorization["status"])
        self.assertFalse(
            decision_has_required_evidence_v2(promoted, "data_boundary")
        )

    def test_side_branch_answer_cannot_fill_the_authorization(self) -> None:
        previous = self._base_model()
        extracted = deepcopy(previous)
        extracted["product_context"]["business_owner"] = "Quality manager"
        extracted["writeback_authorization"] = dict(AUTHORIZATION)

        promoted = self._promote(
            previous,
            extracted,
            "ownership",
            "The Quality manager owns the business result and signs off acceptance.",
        )

        authorization = promoted["writeback_authorization"]
        self.assertEqual("", authorization["authorization_owner"])
        self.assertEqual("pending", authorization["status"])

    def test_the_users_own_writeback_answer_is_kept(self) -> None:
        previous = self._base_model()
        extracted = deepcopy(previous)
        extracted["writeback_authorization"] = dict(AUTHORIZATION)

        promoted = self._promote(previous, extracted, "writeback", WRITEBACK_ANSWER)

        authorization = promoted["writeback_authorization"]
        self.assertEqual("MES", authorization["target_system"])
        self.assertEqual("Quality manager", authorization["authorization_owner"])
        self.assertEqual("authorized", authorization["status"])
        self.assertTrue(
            decision_has_required_evidence_v2(promoted, "data_boundary")
        )

    def test_authorization_survives_a_later_unrelated_turn(self) -> None:
        previous = self._base_model()
        previous["writeback_authorization"] = dict(AUTHORIZATION)
        extracted = deepcopy(previous)
        extracted["writeback_authorization"] = {
            key: "" for key in AUTHORIZATION
        }

        promoted = self._promote(
            previous,
            extracted,
            "acceptance",
            "The quality engineer can identify the top defect within 5 minutes.",
        )

        self.assertEqual(
            "authorized",
            promoted["writeback_authorization"]["status"],
        )


class WritebackEscapeTest(WritebackGroundingTest):
    """Declining the writeback must end the decision, not loop on it."""

    ESCAPE = {
        "en": "Keep the first release read-only; no writeback to any source system.",
        "zh": "保持首版只读，不向任何源系统回写。",
    }

    def test_read_only_escape_drops_the_writeback_request(self) -> None:
        for language, answer in self.ESCAPE.items():
            with self.subTest(language=language):
                previous = self._base_model()
                extracted = deepcopy(previous)

                promoted = self.service._promote_explicit_active_decision_answer(
                    self.session,
                    previous_model=previous,
                    extracted_model=extracted,
                    decision_id="writeback",
                    user_message=answer,
                    language=language,
                )

                from app.services.data_source_policy import classify_data_paths

                classification = classify_data_paths(
                    promoted["data_and_dependencies"],
                    writeback_authorization=promoted["writeback_authorization"],
                )
                self.assertFalse(
                    classification["pending_writeback"],
                    "the read-only escape must clear the pending writeback",
                )
                self.assertTrue(
                    decision_has_required_evidence_v2(promoted, "data_boundary")
                )

    def test_escape_keeps_the_read_only_source(self) -> None:
        previous = self._base_model()
        extracted = deepcopy(previous)

        promoted = self.service._promote_explicit_active_decision_answer(
            self.session,
            previous_model=previous,
            extracted_model=extracted,
            decision_id="writeback",
            user_message=self.ESCAPE["en"],
            language="en",
        )

        joined = " ".join(promoted["data_and_dependencies"])
        self.assertIn("MES", joined)
        self.assertNotIn("Write the disposition back", joined)


class WritebackJourneyTest(WritebackGroundingTest):
    """The full journey a user actually takes through the streamed API."""

    def _ready_model(self) -> dict:
        model = self._base_model()
        model["background"]["objective"] = "Reduce defect escapes by 15% next quarter."
        model["product_context"].update(
            {
                "primary_user": "Quality engineer",
                "decision_or_action": "Pick lots to investigate",
                "business_owner": "Quality manager",
                "acceptance_owner": "Quality manager",
            }
        )
        model["users_and_scenarios"].update(
            {
                "target_users": ["Quality engineer"],
                "core_scenarios": ["Drill into affected lots."],
            }
        )
        model["scope"]["in_scope"] = ["Defect trend dashboard"]
        model["functional_requirements"]["overview"] = "Show defect trends."
        model["acceptance_criteria"] = [
            "The engineer can identify the top defect within 5 minutes."
        ]
        for key in (
            "objective",
            "users",
            "scope",
            "scenarios",
            "features",
            "acceptance",
        ):
            model["collection_status"][key]["status"] = "confirmed"
        return model

    def _stream(self, model, answer):
        self.service._save_interview_model_at_current_message_count(
            self.session, model, "en"
        )
        self.llm.structured_model = deepcopy(model)
        events = list(
            self.service.stream_user_message(self.session.id, answer, "en")
        )
        return next(
            event for event in events if event.get("event") == "summary"
        )

    def test_clicking_the_authorization_option_completes_the_decision(self) -> None:
        summary = self._stream(
            self._ready_model(),
            "Write back to MES: post the QA disposition to the lot record, "
            "authorized by the Quality manager; MES shows the posted "
            "disposition within 5 minutes.",
        )

        state = summary["interview_state"]
        model = summary["structured_requirement_model"]
        self.assertEqual(
            "authorized",
            model["writeback_authorization"]["status"],
        )
        self.assertNotEqual(
            "writeback",
            (state["next_decision"] or {}).get("decision_id"),
        )

    def test_clicking_the_read_only_option_completes_the_decision(self) -> None:
        summary = self._stream(
            self._ready_model(),
            "Keep the first release read-only; no writeback to any source system.",
        )

        state = summary["interview_state"]
        self.assertNotEqual(
            "writeback",
            (state["next_decision"] or {}).get("decision_id"),
        )
        self.assertEqual(
            "pending",
            summary["structured_requirement_model"]["writeback_authorization"][
                "status"
            ],
        )


class StaleAuthorizationTest(unittest.TestCase):
    def test_authorization_for_a_system_that_is_no_longer_the_target(self) -> None:
        model = empty_structured_requirement_model()
        model["data_and_dependencies"] = [
            "Read finished-lot records from SQL Server; the first release is read-only.",
            "Write the corrected yield back to SQL Server by updating the lot row.",
        ]
        model["writeback_authorization"] = dict(AUTHORIZATION)

        self.assertFalse(
            decision_has_required_evidence_v2(model, "data_boundary"),
            "an authorization naming MES cannot authorize a SQL Server writeback",
        )


class ProposalBoundaryTest(unittest.TestCase):
    def test_no_other_decision_can_patch_the_authorization(self) -> None:
        model = empty_structured_requirement_model()

        for decision_id in ("outcome", "v1_flow", "data_boundary", "acceptance"):
            with self.subTest(decision_id=decision_id):
                proposal = build_decision_proposal(decision_id, model, "en")
                self.assertNotIn(
                    "writeback_authorization",
                    proposal["patch"],
                )

    def test_a_forged_cross_decision_patch_is_rejected(self) -> None:
        from app.services.interview_protocol import validate_proposal

        forged = {
            "proposal_id": "proposal-forged",
            "decision_id": "outcome",
            "text": "Authorize the writeback.",
            "allowed_fields": ["writeback_authorization"],
            "patch": {"writeback_authorization": dict(AUTHORIZATION)},
        }

        with self.assertRaises(ProposalValidationError):
            validate_proposal(forged)


if __name__ == "__main__":
    unittest.main()
