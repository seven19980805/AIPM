from __future__ import annotations

import unittest

from app.services.interview_protocol import (
    ProposalValidationError,
    apply_proposal_to_model,
    build_decision_proposal,
    resolve_proposal_from_messages,
    sanitize_assistant_summary,
)
from app.services.structured_requirement_model import empty_structured_requirement_model


class InterviewReplyProtocolTest(unittest.TestCase):
    def test_outcome_proposal_only_confirms_the_outcome(self) -> None:
        model = empty_structured_requirement_model()
        proposal = build_decision_proposal("outcome", model, "zh")

        updated = apply_proposal_to_model(model, proposal)

        self.assertEqual("confirmed", updated["collection_status"]["objective"]["status"])
        self.assertIn("15%", updated["background"]["objective"])
        self.assertEqual("missing", updated["collection_status"]["users"]["status"])
        self.assertEqual("", updated["product_context"]["primary_user"])
        self.assertEqual([], updated["users_and_scenarios"]["target_users"])

    def test_outcome_proposal_uses_captured_context_instead_of_a_fixed_domain(self) -> None:
        model = empty_structured_requirement_model()
        model["background"]["objective"] = "Improve production visibility."

        proposal = build_decision_proposal("outcome", model, "en")

        self.assertIn("Improve production visibility", proposal["text"])
        self.assertIn("15%", proposal["text"])
        self.assertNotIn("e-test", proposal["text"].lower())
        self.assertEqual(
            proposal["text"],
            proposal["patch"]["background.objective"],
        )

    def test_acceptance_uses_latest_single_server_proposal(self) -> None:
        proposal = build_decision_proposal(
            "outcome",
            empty_structured_requirement_model(),
            "en",
        )
        messages = [
            {
                "role": "assistant",
                "content": proposal["text"],
                "metadata": {"interview_turn": {"proposal": proposal}},
            }
        ]

        resolved = resolve_proposal_from_messages(
            messages,
            {
                "decision_id": "outcome",
                "action": "accept_proposal",
                "proposal_id": proposal["proposal_id"],
            },
        )

        self.assertEqual(proposal, resolved)

    def test_missing_multi_fact_and_stale_proposals_are_rejected(self) -> None:
        proposal = build_decision_proposal(
            "outcome",
            empty_structured_requirement_model(),
            "en",
        )
        with self.assertRaises(ProposalValidationError):
            resolve_proposal_from_messages([], None, free_text="yes")

        multi_fact = {
            **proposal,
            "patch": {
                **proposal["patch"],
                "product_context.primary_user": "Shift supervisor",
            },
            "allowed_fields": [
                *proposal["allowed_fields"],
                "product_context.primary_user",
            ],
        }
        with self.assertRaises(ProposalValidationError):
            resolve_proposal_from_messages(
                [
                    {
                        "role": "assistant",
                        "metadata": {"interview_turn": {"proposal": multi_fact}},
                    }
                ],
                None,
                free_text="yes",
            )

        with self.assertRaises(ProposalValidationError):
            resolve_proposal_from_messages(
                [
                    {
                        "role": "assistant",
                        "metadata": {"interview_turn": {"proposal": proposal}},
                    }
                ],
                {
                    "decision_id": "outcome",
                    "action": "accept_proposal",
                    "proposal_id": "stale-proposal-id",
                },
            )

    def test_free_yes_accepts_only_the_latest_assistant_proposal(self) -> None:
        older = build_decision_proposal(
            "outcome",
            empty_structured_requirement_model(),
            "en",
        )
        messages = [
            {
                "role": "assistant",
                "metadata": {"interview_turn": {"proposal": older}},
            },
            {"role": "user", "content": "What does that mean?", "metadata": {}},
            {"role": "assistant", "content": "An explanation only.", "metadata": {}},
        ]

        with self.assertRaises(ProposalValidationError):
            resolve_proposal_from_messages(messages, None, free_text="yes")

    def test_llm_question_and_generic_choices_are_removed_from_summary(self) -> None:
        raw = (
            "Confirmed:\n"
            "- Business outcome: reduce false fails by 15%.\n"
            "- Scope: yield dashboard.\n"
            "- Owner: quality manager.\n\n"
            "Who is the business owner?\n"
            "A. I will provide the exact answer now\n"
            "B. Show me one concrete example\n"
            "C. Leave this pending"
        )

        sanitized = sanitize_assistant_summary(raw, "en")

        self.assertIn("Business outcome", sanitized)
        self.assertIn("Scope", sanitized)
        self.assertNotIn("Owner:", sanitized)
        self.assertNotIn("Who is", sanitized)
        self.assertNotIn("A.", sanitized)
        self.assertNotIn("Show me", sanitized)

    def test_llm_stage_instruction_is_removed_from_summary(self) -> None:
        raw = (
            "Confirmed: primary user is the bakery manager.\n\n"
            "The interview is now complete. Please generate the Build Brief."
        )

        sanitized = sanitize_assistant_summary(raw, "en")

        self.assertEqual(
            "Confirmed: primary user is the bakery manager.",
            sanitized,
        )

        inline = sanitize_assistant_summary(
            (
                "Outcome is under three minutes and automated disposition is "
                "out of scope. The Build Brief is ready to be generated."
            ),
            "en",
        )
        self.assertIn("Outcome is under three minutes", inline)
        self.assertNotIn("Build Brief", inline)


if __name__ == "__main__":
    unittest.main()
