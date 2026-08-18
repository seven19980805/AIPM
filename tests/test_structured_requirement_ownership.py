import unittest

from app.services.structured_requirement_model import (
    REQUIREMENT_ITEM_KEYS,
    STRUCTURED_REQUIREMENT_MODEL_SYSTEM_PROMPT,
    apply_delivery_evidence_gates,
    empty_structured_requirement_model,
    normalize_structured_requirement_model,
)


class StructuredRequirementOwnershipTest(unittest.TestCase):
    def test_empty_model_has_an_independent_missing_ownership_status(self) -> None:
        model = empty_structured_requirement_model()

        self.assertIn("ownership", REQUIREMENT_ITEM_KEYS)
        self.assertEqual(
            {
                "status": "missing",
                "reason": "",
                "pending_questions": [],
            },
            model["collection_status"]["ownership"],
        )

    def test_legacy_owner_values_are_evidence_not_automatic_confirmation(self) -> None:
        model = normalize_structured_requirement_model(
            {
                "product_context": {
                    "business_owner": "Quality manager",
                    "acceptance_owner": "Plant director",
                },
                "collection_status": {
                    "users": {
                        "status": "missing",
                        "reason": "",
                        "pending_questions": [],
                    },
                },
            }
        )

        self.assertEqual("Quality manager", model["product_context"]["business_owner"])
        self.assertEqual("Plant director", model["product_context"]["acceptance_owner"])
        self.assertEqual("missing", model["collection_status"]["ownership"]["status"])
        self.assertEqual("missing", model["collection_status"]["users"]["status"])

    def test_owner_question_blocks_ownership_without_changing_users(self) -> None:
        model = apply_delivery_evidence_gates(
            {
                "open_questions": [
                    "Who is the business owner and who is the acceptance owner?",
                ],
                "collection_status": {
                    "users": {
                        "status": "confirmed",
                        "reason": "The target user was explicitly confirmed.",
                        "pending_questions": [],
                    },
                },
            }
        )

        self.assertEqual(
            "pending_confirmation",
            model["collection_status"]["ownership"]["status"],
        )
        self.assertEqual("confirmed", model["collection_status"]["users"]["status"])

    def test_prompt_requires_separate_confirmation_of_both_owner_roles(self) -> None:
        prompt = STRUCTURED_REQUIREMENT_MODEL_SYSTEM_PROMPT.lower()

        self.assertIn("business owner", prompt)
        self.assertIn("acceptance owner", prompt)
        self.assertIn("independently confirmed", prompt)
        # The schema declares the status shape once for every tracked key.
        self.assertIn("ownership", prompt)
        self.assertIn('"status": "missing|captured|pending_confirmation', prompt)


if __name__ == "__main__":
    unittest.main()
