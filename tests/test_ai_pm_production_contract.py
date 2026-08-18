import tempfile
import unittest
from pathlib import Path

from flask import Flask

from app.api import api
from app.services.build_brief import render_build_brief
from app.services.coding_contract import (
    build_coding_contract,
    render_coding_contract_markdown,
)
from app.services.intake_workflow import enforce_interview_response_contract
from app.services.requirement_collector import (
    STRUCTURED_REQUIREMENT_CANONICAL_CACHE_KEY,
    RequirementCollectorService,
)
from tests.postgres_test_support import create_postgres_test_store
from app.services.structured_requirement_model import (
    REQUIREMENT_ITEM_KEYS,
    apply_delivery_evidence_gates,
    normalize_structured_requirement_model,
)


class RecordingLLMClient:
    def __init__(self) -> None:
        self.calls: list[list[dict[str, str]]] = []

    def chat(self, messages, temperature=0.3):
        self.calls.append(messages)
        return "# Oversized PRD\n\n" + ("Generic implementation detail. " * 500)

    def stream_chat(self, messages, temperature=0.3):
        self.calls.append(messages)
        yield {"type": "content", "text": "# Oversized PRD\n\n"}
        yield {"type": "content", "text": "Generic implementation detail. " * 500}


def confirmed_requirement_model() -> dict:
    confirmed = {
        key: {
            "status": "confirmed",
            "reason": "Confirmed by the business owner.",
            "pending_questions": [],
        }
        for key in REQUIREMENT_ITEM_KEYS
    }
    return normalize_structured_requirement_model(
        {
            "document_info": {
                "project_name": "Yield Review",
                "requirement_name": "Finished lot yield dashboard",
            },
            "product_context": {
                "requesting_department": "Quality",
                "business_owner": "Quality manager",
                "software_type": "Dashboard",
                "primary_user": "Quality engineer",
                "decision_or_action": "Prioritize lots for defect review",
                "acceptance_owner": "Quality manager",
            },
            "background": {
                "summary": "Daily finished-lot review is manual.",
                "objective": "Reduce daily review time from 60 minutes to 15 minutes.",
            },
            "scope": {
                "in_scope": ["Read-only finished-lot dashboard", "CSV export"],
                "out_of_scope": ["Production writeback"],
            },
            "users_and_scenarios": {
                "target_users": ["Quality engineer"],
                "core_scenarios": ["Filter a plant and inspect yield-loss Pareto"],
            },
            "functional_requirements": {
                "overview": "Filter, inspect, and export lot-yield evidence.",
                "feature_details": [
                    {
                        "feature_name": "Yield overview",
                        "description": "Show finished-lot yield and loss.",
                        "trigger": "User opens the dashboard.",
                        "processing_logic": "Apply plant and date filters.",
                        "inputs": ["SQL Server finished-lot records"],
                        "outputs": ["Yield KPI", "Loss Pareto"],
                        "exception_cases": ["No lots in the selected period"],
                    }
                ],
            },
            "page_and_interaction": {
                "pages": [
                    {
                        "page_name": "Yield dashboard",
                        "entry_point": "Navigation / Quality / Yield",
                        "page_elements": ["Plant filter", "Yield KPI", "Pareto chart"],
                        "button_actions": ["Export CSV"],
                    }
                ],
                "interaction_flow": ["Filter plant", "Inspect Pareto", "Export evidence"],
            },
            "business_rules": ["Yield uses the approved finished-lot formula."],
            "data_and_dependencies": [
                "Read finished-lot records from SQL Server.",
                "SAP master data is read-only.",
                "Excel/CSV upload is an optional fallback.",
            ],
            "risks_and_notes": ["Formula changes require Quality owner approval."],
            "acceptance_criteria": [
                "Quality engineer can identify the top loss code for a selected plant.",
                "The dashboard does not write data back to SQL Server or SAP.",
            ],
            "collection_status": confirmed,
        }
    )


class AIProductionIntakeContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.llm_client = RecordingLLMClient()
        self.service = RequirementCollectorService(
            self.llm_client,
            create_postgres_test_store(self, self.tmpdir.name),
        )
        app = Flask(__name__)
        app.extensions["requirement_collector"] = self.service
        app.register_blueprint(api)
        app.testing = True
        self.client = app.test_client()

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_new_intake_contract_requires_one_of_three_business_routes(self) -> None:
        response = self.client.post(
            "/api/sessions",
            json={"language": "en", "intake_mode": "scratch"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("business_route", response.get_json()["error"])

    def test_scratch_draft_and_template_are_first_class_modes(self) -> None:
        scratch = self.client.post(
            "/api/sessions",
            json={
                "language": "en",
                "intake_mode": "scratch",
                "business_route": "production",
            },
        )
        draft = self.client.post(
            "/api/sessions",
            json={
                "language": "en",
                "intake_mode": "draft",
                "business_route": "tdi",
                "start_function": "improve_draft",
            },
        )
        template = self.client.post(
            "/api/sessions",
            json={
                "language": "en",
                "intake_mode": "template",
                "business_route": "quality",
                "template_id": "qdm_finished_lot_yield_dashboard_template_en",
            },
        )

        self.assertEqual(scratch.status_code, 201)
        self.assertEqual(draft.status_code, 201)
        self.assertEqual(template.status_code, 201)
        self.assertEqual(scratch.get_json()["launch_context"]["mode"], "scratch")
        self.assertEqual(draft.get_json()["launch_context"]["mode"], "draft")
        self.assertEqual(template.get_json()["launch_context"]["mode"], "template")
        self.assertEqual(
            [
                scratch.get_json()["launch_context"]["business_route"],
                draft.get_json()["launch_context"]["business_route"],
                template.get_json()["launch_context"]["business_route"],
            ],
            ["production", "tdi", "quality"],
        )

    def test_launch_contract_has_a_bounded_single_question_interview(self) -> None:
        response = self.client.post(
            "/api/sessions",
            json={
                "language": "en",
                "intake_mode": "scratch",
                "business_route": "quality",
            },
        )
        context = response.get_json()["launch_context"]

        self.assertEqual(context["version"], 2)
        self.assertLessEqual(context["question_budget"]["maximum"], 8)
        self.assertEqual(
            context["question"],
            "What business action should the first release improve?",
        )
        self.assertNotIn(
            "General",
            [suggestion["label"] for suggestion in context["suggestions"]],
        )

    def test_invalid_new_business_route_is_rejected(self) -> None:
        response = self.client.post(
            "/api/sessions",
            json={
                "language": "en",
                "intake_mode": "scratch",
                "business_route": "general",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("production, quality, or tdi", response.get_json()["error"].lower())

    def test_direct_user_statements_advance_progress_without_reconfirmation(self) -> None:
        session = self.service.create_session(
            language="en",
            intake_mode="scratch",
            business_route="quality",
        )

        prompt = self.service._structured_requirement_model_prompt(session, "en")

        self.assertIn(
            "A direct, unambiguous declarative statement from the user is explicit confirmation",
            prompt,
        )
        self.assertIn(
            "Do not require a later yes/confirm turn",
            prompt,
        )
        self.assertIn(
            "Template baselines, AI suggestions, and attachment inferences remain unconfirmed",
            prompt,
        )

    def test_template_catalog_exposes_all_enabled_business_templates(self) -> None:
        templates = self.service.list_business_templates()
        template_keys = {item["template_key"] for item in templates}

        self.assertEqual(
            template_keys,
            {
                "abf_yield_analysis",
                "ai_pm_production_flow",
                "ai_pm_quality_inspection",
                "ai_pm_tdi_request",
                "business_process_requirement",
                "finance_management_business_requirement",
                "forum_community_business_requirement",
                "human_resource_management_business_requirement",
                "individual_chart_requirement",
                "logistics_warehouse_business_requirement",
                "multiple_chart_requirement",
                "qdm_finished_lot_yield_dashboard",
                "shopping_mall_business_requirement",
                "training_system_business_requirement",
            },
        )


class CompactBuildBriefContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.llm_client = RecordingLLMClient()
        self.service = RequirementCollectorService(
            self.llm_client,
            create_postgres_test_store(self, self.tmpdir.name),
        )

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_ready_document_is_a_deterministic_bounded_build_brief(self) -> None:
        session = self.service.create_session(
            language="en",
            starter_department="quality",
        )
        self.service._append_message(
            session.id,
            "user",
            "Build a read-only finished-lot yield dashboard.",
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

        result = self.service.build_prd_document(
            session.id,
            language="en",
            save_history=True,
        )
        brief = result["document_markdown"]

        self.assertEqual(self.llm_client.calls, [])
        self.assertLessEqual(len(brief), 6000)
        self.assertTrue(brief.startswith("# Build Brief"))
        self.assertIn("## Outcome", brief)
        self.assertIn("## Scope", brief)
        self.assertIn("## Workflow & Screens", brief)
        self.assertIn("## Rules & Data", brief)
        self.assertIn("## Acceptance", brief)
        self.assertIn("## Open Items", brief)
        self.assertIn("SQL Server", brief)
        self.assertIn("SAP", brief)
        self.assertIn("Excel/CSV", brief)
        self.assertNotIn("Glossary", brief)
        self.assertNotIn("User Stories", brief)
        self.assertNotIn("System Architecture", brief)
        self.assertIn("Build-Brief", result["filename"])

    def test_page_details_are_advisory_when_build_decisions_are_confirmed(self) -> None:
        model = confirmed_requirement_model()
        model["collection_status"]["pages"] = {
            "status": "missing",
            "reason": "Screens can be derived from the confirmed workflow.",
            "pending_questions": ["Confirm exact layout later."],
        }

        progress = self.service._structured_requirement_progress(model)

        self.assertFalse(progress["fully_confirmed"])
        self.assertTrue(progress["core_requirements_confirmed"])
        self.assertTrue(progress["ready_to_generate"])
        self.assertEqual(progress["blocking_question_count"], 0)

    def test_build_brief_preserves_a_compact_data_mapping_owner(self) -> None:
        model = confirmed_requirement_model()
        model["data_and_dependencies"][0] = (
            "SQL Server read-only views provide SPC records; production view and "
            "field mapping remain an explicit adapter configuration owned by the data owner."
        )

        brief = render_build_brief(
            model,
            title="Data boundary",
            intake_mode="scratch",
            business_route="quality",
            language="en",
        )

        self.assertIn("owned by the data owner.", brief)

    def test_approved_sources_with_read_only_boundary_do_not_add_unconfirmed_marker(self) -> None:
        model = confirmed_requirement_model()
        model["data_and_dependencies"] = [
            "Read finished-lot records from SQL Server.",
            "SAP master data is read-only.",
            "No source-system writeback.",
        ]

        brief = render_build_brief(
            model,
            title="Approved read-only boundary",
            intake_mode="scratch",
            business_route="quality",
            language="en",
        )

        self.assertIn("No source-system writeback.", brief)
        self.assertNotIn("Unconfirmed data source", brief)

    def test_unapproved_postgresql_source_is_removed_without_losing_read_only_boundary(self) -> None:
        model = confirmed_requirement_model()
        model["data_and_dependencies"] = [
            "Read-only access to fabricated PostgreSQL QA source named DEMO_ALPHA.",
            "No source-system writeback.",
        ]

        brief = render_build_brief(
            model,
            title="Unapproved operational database",
            intake_mode="scratch",
            business_route="quality",
            language="en",
        )

        self.assertNotIn("PostgreSQL", brief)
        self.assertNotIn("DEMO_ALPHA", brief)
        self.assertIn("No source-system writeback.", brief)
        self.assertIn("Unconfirmed data source", brief)
        self.assertIn(
            "Allowed data paths: SQL Server, SAP, MES, QIS/QMS, or manual Excel/CSV upload.",
            brief,
        )

    def test_read_write_boundary_survives_source_cleanup_in_every_language(self) -> None:
        boundaries = {
            "en": "No source-system writeback.",
            "zh": "不向生产系统回写。",
            "de": "Ohne Rückschreiben ins Quellsystem.",
            "ms": "Tanpa tulis balik ke sistem pengeluaran.",
        }
        unapproved = {
            "en": "Read-only access to MySQL quality records.",
            "zh": "只读获取 MySQL 质量记录。",
            "de": "Nur lesender Zugriff auf MySQL-Qualitaetsdaten.",
            "ms": "Akses baca sahaja ke rekod kualiti MySQL.",
        }

        for language, boundary in boundaries.items():
            with self.subTest(language=language):
                model = confirmed_requirement_model()
                model["data_and_dependencies"] = [unapproved[language], boundary]

                brief = render_build_brief(
                    model,
                    title="Boundary retention",
                    intake_mode="scratch",
                    business_route="quality",
                    language=language,
                )

                self.assertIn(boundary, brief)
                self.assertNotIn("MySQL", brief)

    def test_other_named_operational_databases_are_not_treated_as_approved_paths(self) -> None:
        for source in ("MySQL", "Oracle", "MongoDB"):
            with self.subTest(source=source):
                model = confirmed_requirement_model()
                model["data_and_dependencies"] = [
                    f"Read-only access to {source} quality records.",
                    "No source-system writeback.",
                ]

                brief = render_build_brief(
                    model,
                    title="Other unapproved operational database",
                    intake_mode="scratch",
                    business_route="quality",
                    language="en",
                )

                self.assertNotIn(source, brief)
                self.assertIn("No source-system writeback.", brief)
                self.assertIn("Unconfirmed data source", brief)

    def test_confirmed_objective_hides_resolved_launch_question(self) -> None:
        model = confirmed_requirement_model()
        model["open_questions"] = [
            "What single business action should the first Quality release improve?"
        ]

        brief = render_build_brief(
            model,
            title="Resolved launch question",
            intake_mode="scratch",
            business_route="quality",
            language="en",
        )

        self.assertNotIn("What single business action", brief)
        self.assertIn("- Risk: Formula changes require Quality owner approval.", brief)

    def test_primary_user_is_not_repeated_as_an_unlabeled_target_user(self) -> None:
        model = confirmed_requirement_model()

        brief = render_build_brief(
            model,
            title="Deduplicated users",
            intake_mode="scratch",
            business_route="quality",
            language="en",
        )

        self.assertIn("- Primary user: Quality engineer", brief)
        self.assertNotIn("\n- Quality engineer\n", brief)

    def test_build_brief_deduplicates_spacing_and_display_word_variants(self) -> None:
        model = confirmed_requirement_model()
        model["scope"]["in_scope"] = [
            "展示受影响批次列表",
            "受影响批次列表",
        ]
        model["acceptance_criteria"] = [
            "质量工程师能在5分钟内找出首要缺陷及受影响批次",
            "质量工程师能在 5 分钟内找出首要缺陷及受影响批次",
        ]

        brief = render_build_brief(
            model,
            title="去重验证",
            intake_mode="scratch",
            business_route="quality",
            language="zh",
        )

        self.assertEqual(1, brief.count("受影响批次列表"))
        self.assertEqual(1, brief.count("首要缺陷及受影响批次"))

    def test_mes_and_qis_read_only_paths_reach_delivery_artifacts(self) -> None:
        model = confirmed_requirement_model()
        model["data_and_dependencies"] = [
            "Read defect records directly from QIS/MES; the first release is read-only.",
            "Excel upload is an optional fallback.",
        ]

        brief = render_build_brief(
            model,
            title="Approved shop-floor sources",
            intake_mode="draft",
            business_route="quality",
            language="en",
        )
        contract = build_coding_contract(
            model,
            session_id="approved-source-session",
            title="Approved shop-floor sources",
            workflow_mode="draft",
            language="en",
        )
        dependency_text = " ".join(
            item["requirement"] for item in contract["data_dependencies"]
        )

        self.assertIn("QIS", brief)
        self.assertIn("MES", brief)
        self.assertNotIn("Unconfirmed data source", brief)
        self.assertIn("QIS", dependency_text)
        self.assertIn("MES", dependency_text)
        self.assertNotIn("Unconfirmed data source", dependency_text)
        self.assertEqual(
            ["mes", "qis", "file_upload"],
            contract["data_policy"]["referenced_sources"],
        )

    def test_coding_contract_uses_build_brief_delivery_language(self) -> None:
        contract = build_coding_contract(
            confirmed_requirement_model(),
            session_id="build-brief-language",
            title="Build Brief delivery",
            workflow_mode="scratch",
            language="en",
            has_prd_document=True,
        )

        markdown = render_coding_contract_markdown(contract)

        self.assertIn("Ready for Build Brief:", markdown)
        self.assertIn("Use the Build Brief only as supporting context.", markdown)
        self.assertIn("## Data Dependencies", markdown)
        self.assertIn("**DD-003**", markdown)
        self.assertIn("Excel/CSV", markdown)
        self.assertNotIn("Ready for documents:", markdown)
        self.assertNotIn("PRD and design document", markdown)


class InterviewResponseContractTest(unittest.TestCase):
    def test_confirmed_summary_is_limited_to_three_bullets(self) -> None:
        raw = (
            "**Confirmed facts**\n"
            "- Primary user: quality engineer\n"
            "- Action: review high-loss lots\n"
            "- Scope: read-only dashboard\n"
            "- Data: SQL Server view\n\n"
            "Which acceptance outcome matters most?\n\n"
            "A. Review completed in two minutes\n"
            "B. Export completed without errors\n"
            "C. Leave acceptance pending"
        )

        guarded = enforce_interview_response_contract(raw)

        self.assertIn("- Primary user: quality engineer", guarded)
        self.assertIn("- Scope: read-only dashboard", guarded)
        self.assertNotIn("- Data: SQL Server view", guarded)
        self.assertIn("A. Review completed in two minutes", guarded)
        self.assertIn("C. Leave acceptance pending", guarded)

    def test_repeated_model_question_is_removed_without_losing_options(self) -> None:
        raw = (
            "Confirmed: read-only SPC dashboard with no write-back.\n\n"
            "Biggest gap: What rule defines an out-of-control process?\n\n"
            "A) Western Electric rules.\n"
            "B) Nelson rules.\n"
            "C) Cpk threshold only.\n\n"
            "Which fits your v1 scope best?"
        )

        guarded = enforce_interview_response_contract(raw)

        self.assertEqual(guarded.count("?"), 1)
        self.assertIn("What rule defines an out-of-control process?", guarded)
        self.assertIn("A) Western Electric rules.", guarded)
        self.assertNotIn("Which fits your v1 scope best", guarded)
        self.assertLessEqual(len(guarded), 1200)

    def test_question_without_terminal_mark_gets_one_question_mark(self) -> None:
        examples = (
            ("Should the first version:", "Should the first version?"),
            (
                "For the Verified to Closed transition, does approval come from:",
                "For the Verified to Closed transition, does approval come from?",
            ),
        )
        for question, expected in examples:
            with self.subTest(question=question):
                raw = (
                    "One question:\n"
                    f"{question}\n"
                    "A. Use the named owner\n"
                    "B. Use an automatic rule"
                )

                guarded = enforce_interview_response_contract(raw)

                self.assertEqual(guarded.count("?"), 1)
                self.assertIn(expected, guarded)

    def test_model_choices_are_limited_to_three(self) -> None:
        raw = (
            "Who can approve the transition?\n\n"
            "A. TDI lead\n"
            "B. Assigned engineer\n"
            "C. Original requester\n"
            "D. Automatic closure\n"
            "E. Use a default assumption"
        )

        guarded = enforce_interview_response_contract(raw)

        self.assertIn("A. TDI lead", guarded)
        self.assertIn("C. Original requester", guarded)
        self.assertNotIn("D. Automatic closure", guarded)
        self.assertNotIn("E. Use a default assumption", guarded)

    def test_metric_rule_needs_a_formula_threshold_or_named_spc_rule(self) -> None:
        model = confirmed_requirement_model()
        model["functional_requirements"]["overview"] = "SPC dashboard"
        model["business_rules"] = ["Flag an out-of-control process."]

        guarded = apply_delivery_evidence_gates(model, language="en")

        self.assertEqual(
            guarded["collection_status"]["rules"]["status"],
            "pending_confirmation",
        )
        self.assertIn(
            "formula, threshold, time window, or SPC rule",
            guarded["collection_status"]["rules"]["pending_questions"][0],
        )

        model["business_rules"] = ["Flag one point beyond 3 sigma."]
        concrete = apply_delivery_evidence_gates(model, language="en")

        self.assertEqual(
            concrete["collection_status"]["rules"]["status"],
            "confirmed",
        )

    def test_generic_acceptance_metric_does_not_trigger_spc_formula_gate(self) -> None:
        confirmed = {
            key: {
                "status": "confirmed",
                "reason": "Confirmed by the business owner.",
                "pending_questions": [],
            }
            for key in REQUIREMENT_ITEM_KEYS
        }
        model = normalize_structured_requirement_model(
            {
                "document_info": {
                    "project_name": "Expense Approval",
                    "requirement_name": "Expense and payment tracking",
                },
                "background": {
                    "objective": "Reduce approval time from three days to one day.",
                },
                "users_and_scenarios": {
                    "target_users": ["Employee", "Finance specialist"],
                    "core_scenarios": ["Submit and approve an expense claim"],
                },
                "functional_requirements": {
                    "overview": "Expense submission, approval, and SAP payment-status tracking.",
                },
                "business_rules": [
                    "Duplicate invoices are blocked.",
                    "Rejected claims require a reason.",
                ],
                "risks_and_notes": [
                    "Pilot with ten finance users and promote after the acceptance metric is met."
                ],
                "acceptance_criteria": ["Approval completes within one business day."],
                "collection_status": confirmed,
            }
        )

        guarded = apply_delivery_evidence_gates(model, language="en")

        self.assertEqual(
            guarded["collection_status"]["rules"]["status"],
            "confirmed",
        )
        self.assertEqual(
            guarded["collection_status"]["rules"]["pending_questions"],
            [],
        )

    def test_cpk_requires_a_confirmed_source_field_or_formula(self) -> None:
        model = confirmed_requirement_model()
        model["functional_requirements"]["overview"] = "SPC/Cpk dashboard"
        model["business_rules"] = ["Flag Cpk below 1.33."]

        missing_definition = apply_delivery_evidence_gates(model, language="en")

        self.assertEqual(
            missing_definition["collection_status"]["rules"]["status"],
            "pending_confirmation",
        )
        self.assertIn(
            "confirmed source field or an approved formula",
            missing_definition["collection_status"]["rules"]["pending_questions"][0],
        )

        model["data_and_dependencies"].append(
            "Cpk is supplied by a confirmed SQL Server read-only source field."
        )
        concrete = apply_delivery_evidence_gates(model, language="en")

        self.assertEqual(
            concrete["collection_status"]["rules"]["status"],
            "confirmed",
        )

    def test_field_level_open_question_blocks_the_matching_decision(self) -> None:
        model = confirmed_requirement_model()
        model["document_info"] = {
            "project_name": "TDI Request Tracker",
            "requirement_name": "Request closure workflow",
        }
        model["background"] = {
            "summary": "Request closure ownership is unclear.",
            "objective": "Make TDI request closure traceable.",
        }
        model["functional_requirements"] = {
            "overview": "Track TDI request status and ownership.",
            "feature_details": [],
        }
        model["users_and_scenarios"] = {
            "target_users": ["TDI engineer"],
            "core_scenarios": ["Review and close a verified request."],
        }
        model["acceptance_criteria"] = [
            "A TDI engineer can see the approver for a closed request."
        ]
        model["business_rules"] = ["Requests move from Verified to Closed."]
        model["risks_and_notes"] = []
        model["open_questions"] = [
            "Who may approve the transition from Verified to Closed?"
        ]

        guarded = apply_delivery_evidence_gates(model, language="en")

        self.assertEqual(
            guarded["collection_status"]["rules"]["status"],
            "pending_confirmation",
        )
        self.assertEqual(
            guarded["collection_status"]["rules"]["pending_questions"],
            model["open_questions"],
        )


if __name__ == "__main__":
    unittest.main()
