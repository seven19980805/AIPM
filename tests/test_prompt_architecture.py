import tempfile
import unittest
from pathlib import Path

from app.services.requirement_collector import (
    STRUCTURED_REQUIREMENT_CANONICAL_CACHE_KEY,
    RequirementCollectorService,
)
from tests.postgres_test_support import create_postgres_test_store
from app.services.structured_requirement_model import (
    REQUIREMENT_ITEM_KEYS,
    normalize_structured_requirement_model,
)


def confirmed_requirement_model() -> dict:
    statuses = {
        key: {
            "status": "confirmed",
            "reason": "Explicitly confirmed by the user.",
            "pending_questions": [],
        }
        for key in REQUIREMENT_ITEM_KEYS
    }
    return normalize_structured_requirement_model(
        {
            "document_info": {
                "project_name": "Quality Review",
                "requirement_name": "Finished-lot review",
            },
            "product_context": {
                "requesting_department": "Quality",
                "business_owner": "Quality manager",
                "software_type": "Dashboard",
                "primary_user": "Quality engineer",
                "decision_or_action": "Prioritize lots for review",
                "acceptance_owner": "Quality manager",
            },
            "background": {
                "summary": "The current review is manual.",
                "objective": "Reduce review time from 60 to 15 minutes.",
            },
            "scope": {
                "in_scope": ["Read-only lot review", "CSV export"],
                "out_of_scope": ["Source-system writeback"],
            },
            "users_and_scenarios": {
                "target_users": ["Quality engineer"],
                "core_scenarios": ["Filter a plant and review loss evidence"],
            },
            "functional_requirements": {
                "overview": "Filter, inspect, and export evidence.",
                "feature_details": [
                    {
                        "feature_name": "Lot review",
                        "description": "Show finished-lot yield and loss.",
                        "trigger": "User opens the dashboard.",
                        "processing_logic": "Apply plant and date filters.",
                        "inputs": ["Finished-lot records"],
                        "outputs": ["Yield KPI", "Loss Pareto"],
                        "exception_cases": ["No lots in the period"],
                    }
                ],
            },
            "page_and_interaction": {
                "pages": [],
                "interaction_flow": ["Filter", "Review", "Export"],
            },
            "business_rules": [
                "Yield = good finished lots / total finished lots x 100 for the selected date window."
            ],
            "data_and_dependencies": [
                "SQL Server read-only view with explicit field mapping.",
                "SAP product master data is read-only.",
                "Excel/CSV upload is an optional fallback.",
            ],
            "acceptance_criteria": [
                "Quality engineer identifies the top loss code in under 2 minutes."
            ],
            "collection_status": statuses,
        }
    )


class PromptArchitectureContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.service = RequirementCollectorService(
            object(),
            create_postgres_test_store(self, self.tmpdir.name),
        )
        self.quality_template_id = next(
            item["template_id"]
            for item in self.service.list_business_templates()
            if item.get("business_route") == "quality"
        )

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_interview_prompts_are_compact_and_have_one_authoritative_contract(self) -> None:
        sessions = {
            "scratch": self.service.create_session(
                language="en",
                intake_mode="scratch",
                business_route="quality",
            ),
            "draft": self.service.create_session(
                language="en",
                intake_mode="draft",
                business_route="quality",
            ),
            "template": self.service.create_session(
                template_id=self.quality_template_id,
                language="en",
                intake_mode="template",
                business_route="quality",
            ),
        }

        for mode, session in sessions.items():
            with self.subTest(mode=mode):
                prompt = self.service._pm_prompt(session, "en")
                lowered = prompt.lower()

                self.assertLessEqual(len(prompt), 7000)
                self.assertIn(
                    "assistant messages summarize at most two newly confirmed facts",
                    lowered,
                )
                self.assertNotIn("exactly one question at the end", lowered)
                self.assertIn("RUNTIME STATE (authoritative)", prompt)
                self.assertNotIn("System Design Document", prompt)
                self.assertNotIn("Skill-style AI PM method", prompt)
                self.assertNotIn("Current conversation chain state", prompt)
                self.assertNotIn("DEFAULT TECHNOLOGY STACK POLICY", prompt)

        template_prompt = self.service._pm_prompt(sessions["template"], "en")
        self.assertIn("TEMPLATE BASELINE (unconfirmed)", template_prompt)
        self.assertIn("Quality Inspection Baseline", template_prompt)
        self.assertIn(
            '"sections":["Outcome","User and Owner","First-release Scope"',
            template_prompt,
        )
        self.assertIn(
            "What evidence lets the acceptance owner sign off?",
            template_prompt,
        )

    def test_structured_extraction_prompt_is_compact_and_never_creates_assumptions(self) -> None:
        sessions = [
            self.service.create_session(
                language="en",
                intake_mode="scratch",
                business_route="quality",
            ),
            self.service.create_session(
                template_id=self.quality_template_id,
                language="en",
                intake_mode="template",
                business_route="quality",
            ),
        ]

        for session in sessions:
            prompt = self.service._structured_requirement_model_prompt(session, "en")

            # Raised from 7000 for the writeback_authorization contract field:
            # its schema entry plus the one-line extraction rule cost ~280 chars,
            # and the extraction prompt had no slack left.
            self.assertLessEqual(len(prompt), 7300)
            self.assertIn("Output strict JSON only", prompt)
            self.assertIn(
                "A direct, unambiguous declarative statement from the user is explicit confirmation",
                prompt,
            )
            self.assertIn(
                "An A/B/C reply confirms only the exact option text",
                prompt,
            )
            self.assertIn("feature_details: at most 6", prompt)
            self.assertNotIn("Formulate a reasonable", prompt)
            self.assertNotIn("When the user selects Option A", prompt)
            self.assertNotIn("Upgrade the status", prompt)

    def test_ready_runtime_state_stops_the_interview_without_methodology_noise(self) -> None:
        session = self.service.create_session(
            language="en",
            intake_mode="scratch",
            business_route="quality",
        )
        self.service._append_message(
            session.id,
            "user",
            "Build a read-only finished-lot review dashboard.",
        )
        current = self.service._require_session(session.id)
        message_count = self.service._message_count(current.messages)
        model = confirmed_requirement_model()
        for cache_key in {STRUCTURED_REQUIREMENT_CANONICAL_CACHE_KEY, "en"}:
            self.service._save_structured_requirement_model_cache(
                session.id,
                cache_key,
                message_count,
                model,
            )

        prompt = self.service._pm_prompt(
            self.service._require_session(session.id),
            "en",
        )

        self.assertIn('"phase":"brief_ready"', prompt)
        self.assertIn("VISIBLE RESPONSE CONTRACT", prompt)
        self.assertNotIn("PM methodology state", prompt)
        self.assertNotIn("PM Methodology is advisory", prompt)

    def test_legacy_template_without_route_metadata_gets_a_concrete_route(self) -> None:
        session = self.service.create_session(
            template_id="qdm_finished_lot_yield_dashboard_template_zh_cn",
            language="en",
        )

        interview_prompt = self.service._pm_prompt(session, "en")
        extraction_prompt = self.service._structured_requirement_model_prompt(session, "en")

        self.assertIn("route: Quality", interview_prompt)
        self.assertIn('"intake":"template","route":"quality"', extraction_prompt)

    def test_advisory_pages_never_block_a_core_business_rule(self) -> None:
        session = self.service.create_session(
            language="en",
            intake_mode="scratch",
            business_route="quality",
        )
        self.service._append_message(
            session.id,
            "user",
            "The yield formula is still undecided.",
        )
        current = self.service._require_session(session.id)
        message_count = self.service._message_count(current.messages)
        model = confirmed_requirement_model()
        model["collection_status"]["pages"] = {
            "status": "pending_confirmation",
            "reason": "Layout is advisory.",
            "pending_questions": ["What exact page layout should be used?"],
        }
        model["collection_status"]["rules"] = {
            "status": "pending_confirmation",
            "reason": "The formula is not confirmed.",
            "pending_questions": ["What exact yield formula should version one use?"],
        }
        for cache_key in {STRUCTURED_REQUIREMENT_CANONICAL_CACHE_KEY, "en"}:
            self.service._save_structured_requirement_model_cache(
                session.id,
                cache_key,
                message_count,
                model,
            )

        prompt = self.service._pm_prompt(
            self.service._require_session(session.id),
            "en",
        )

        self.assertIn('"phase":"brief_ready"', prompt)
        self.assertIn('"rules":"pending_confirmation"', prompt)
        self.assertIn('"next_gap":""', prompt)
        self.assertNotIn("What exact yield formula should version one use?", prompt)
        self.assertNotIn("What exact page layout should be used?", prompt)


if __name__ == "__main__":
    unittest.main()


class _BudgetLLM:
    def chat(self, messages, temperature: float = 0.3) -> str:
        return "{}"

    def stream_chat(self, messages, temperature: float = 0.3):
        yield {"type": "content", "text": "ok"}


class ExtractionPromptBudgetTest(unittest.TestCase):
    """The budget must hold for every template, not just one sample."""

    EXTRACTION_PROMPT_MAX_CHARS = 7300

    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.service = RequirementCollectorService(
            _BudgetLLM(),
            create_postgres_test_store(self, self.tmpdir.name),
        )

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_every_template_and_language_stays_inside_the_budget(self) -> None:
        templates = self.service.list_business_templates()

        for template in templates:
            for language in ("en", "zh", "de", "ms"):
                with self.subTest(
                    template=template["template_id"], language=language
                ):
                    session = self.service.create_session(
                        language=language,
                        intake_mode="template",
                        business_route=template.get("business_route") or "quality",
                        template_id=template["template_id"],
                    )
                    prompt = self.service._structured_requirement_model_prompt(
                        self.service.get_session(session.id), language
                    )

                    self.assertLessEqual(
                        len(prompt),
                        self.EXTRACTION_PROMPT_MAX_CHARS,
                        f"{template['template_id']} / {language} overruns the "
                        f"extraction budget at {len(prompt)} chars",
                    )
