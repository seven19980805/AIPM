"""The writeback decision must be askable, answerable, and escapable.

Read-only is the default, so the decision never appears unless the user asked to
write into a source system. Once it appears it must be completable: either by
authorizing the writeback or by dropping it and staying read-only.
"""

from __future__ import annotations

import unittest

from app.services.interview_state import build_interview_state_v2
from app.services.structured_requirement_model import (
    empty_structured_requirement_model,
)


def _fast_ready_model() -> dict:
    model = empty_structured_requirement_model()
    model["background"]["objective"] = "Reduce defect escapes by 15% next quarter."
    model["product_context"].update(
        {
            "primary_user": "Quality engineer",
            "decision_or_action": "Decide which lot to investigate first",
            "business_owner": "Quality manager",
            "acceptance_owner": "Quality manager",
        }
    )
    model["users_and_scenarios"].update(
        {
            "target_users": ["Quality engineer"],
            "core_scenarios": ["Filter defect trends and drill into lots."],
        }
    )
    model["scope"]["in_scope"] = ["Defect trend dashboard"]
    model["functional_requirements"]["overview"] = "Show defect trends with drill-down."
    model["acceptance_criteria"] = [
        "The quality engineer can identify the top defect within 5 minutes."
    ]
    for key in ("objective", "users", "scope", "scenarios", "features", "acceptance"):
        model["collection_status"][key]["status"] = "confirmed"
    return model


def _read_only_model() -> dict:
    model = _fast_ready_model()
    model["data_and_dependencies"] = [
        "Read lot records from MES; the first release is read-only.",
    ]
    model["collection_status"]["integrations"]["status"] = "confirmed"
    return model


def _writeback_requested_model() -> dict:
    model = _fast_ready_model()
    model["data_and_dependencies"] = [
        "Read lot records from MES; the first release is read-only.",
        "Write the disposition back to MES by posting the QA decision.",
    ]
    return model


def _state(model: dict, language: str = "en") -> dict:
    return build_interview_state_v2(
        model,
        language=language,
        business_route="quality",
    )


class WritebackDecisionVisibilityTest(unittest.TestCase):
    def test_read_only_sessions_are_never_asked_about_writeback(self) -> None:
        state = _state(_read_only_model())
        next_decision = state["next_decision"] or {}

        self.assertNotEqual("writeback", next_decision.get("decision_id"))

    def test_requested_writeback_becomes_the_active_decision(self) -> None:
        state = _state(_writeback_requested_model())
        next_decision = state["next_decision"] or {}

        self.assertEqual("writeback", next_decision["decision_id"])
        self.assertGreaterEqual(len(next_decision["options"]), 2)

    def test_the_decision_offers_a_read_only_escape(self) -> None:
        state = _state(_writeback_requested_model())
        options = [
            option["text"] for option in state["next_decision"]["options"]
        ]

        self.assertTrue(
            any("read-only" in text.casefold() for text in options),
            f"no read-only escape among {options}",
        )

    def test_the_decision_asks_for_all_four_facts(self) -> None:
        for language in ("en", "zh", "de", "ms"):
            with self.subTest(language=language):
                state = _state(_writeback_requested_model(), language=language)
                next_decision = state["next_decision"]

                self.assertEqual("writeback", next_decision["decision_id"])
                self.assertTrue(next_decision["question"].strip())
                self.assertTrue(next_decision["label"].strip())
                self.assertGreaterEqual(len(next_decision["options"]), 2)

    def test_writeback_cannot_be_deferred_into_a_permanent_assumption(self) -> None:
        state = build_interview_state_v2(
            _writeback_requested_model(),
            language="en",
            business_route="quality",
            defer_available_decision_id="writeback",
        )

        self.assertEqual("writeback", state["next_decision"]["decision_id"])
        self.assertFalse(
            state["next_decision"]["can_defer"],
            "deferring writeback would leave it pending forever",
        )

    def test_writeback_does_not_change_the_five_decision_brief(self) -> None:
        state = _state(_writeback_requested_model())

        self.assertEqual(5, state["brief"]["total_decisions"])

    def test_authorized_writeback_leaves_the_decision_behind(self) -> None:
        model = _writeback_requested_model()
        model["writeback_authorization"] = {
            "target_system": "MES",
            "action": "Post the QA disposition to the lot record",
            "authorization_owner": "Quality manager",
            "acceptance_evidence": "MES shows the posted disposition within 5 minutes.",
        }
        model["collection_status"]["integrations"]["status"] = "confirmed"

        state = _state(model)
        next_decision = state["next_decision"] or {}

        self.assertNotEqual("writeback", next_decision.get("decision_id"))


class DataBoundaryOptionsTest(unittest.TestCase):
    def test_shop_floor_sources_are_offered_in_every_language(self) -> None:
        model = _fast_ready_model()

        for language in ("en", "zh", "de", "ms"):
            with self.subTest(language=language):
                state = build_interview_state_v2(
                    model,
                    language=language,
                    business_route="quality",
                )
                next_decision = state["next_decision"]
                self.assertEqual("data_boundary", next_decision["decision_id"])
                combined = " ".join(
                    option["text"] for option in next_decision["options"]
                )
                self.assertTrue(
                    "MES" in combined or "QIS" in combined or "QMS" in combined,
                    f"no shop-floor source offered: {combined}",
                )


class OptionPresentationTest(unittest.TestCase):
    """Long authorization answers must stay readable in the single card."""

    MAX_LABEL_CHARS = 80

    def test_every_option_has_a_short_label_but_keeps_the_full_answer(self) -> None:
        for language in ("en", "zh", "de", "ms"):
            with self.subTest(language=language):
                state = _state(_writeback_requested_model(), language=language)
                options = state["next_decision"]["options"]

                for option in options:
                    self.assertTrue(option["text"].strip())
                    self.assertIn("label", option)
                    self.assertTrue(option["label"].strip())
                    self.assertLessEqual(
                        len(option["label"]),
                        self.MAX_LABEL_CHARS,
                        f"{language} label too long to scan: {option['label']}",
                    )

    def test_labels_stay_distinct_so_options_remain_choosable(self) -> None:
        state = _state(_writeback_requested_model())
        labels = [option["label"] for option in state["next_decision"]["options"]]

        self.assertEqual(len(labels), len(set(labels)))

    def test_short_options_keep_their_text_as_the_label(self) -> None:
        model = _fast_ready_model()
        state = build_interview_state_v2(
            model, language="en", business_route="quality"
        )
        options = state["next_decision"]["options"]

        for option in options:
            if len(option["text"]) <= self.MAX_LABEL_CHARS:
                self.assertEqual(option["text"], option["label"])


if __name__ == "__main__":
    unittest.main()
