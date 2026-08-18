from __future__ import annotations

import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path

from flask import Flask

from app.api import api
from app.services.coding_contract import (
    build_coding_contract,
    build_delivery_workflow,
    render_coding_contract_markdown,
)
from app.services.requirement_collector import (
    STRUCTURED_REQUIREMENT_CANONICAL_CACHE_KEY,
    RequirementCollectorService,
)
from tests.postgres_test_support import create_postgres_test_store
from app.services.structured_requirement_model import (
    REQUIREMENT_ITEM_KEYS,
    normalize_structured_requirement_model,
)


@contextmanager
def _postgres_test_store(storage_dir: str):
    cleanup_case = unittest.TestCase()
    store = create_postgres_test_store(cleanup_case, storage_dir)
    try:
        yield store
    finally:
        cleanup_case.doCleanups()


def _confirmed_model() -> dict:
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
                "overview": "Filter, inspect and export lot-yield evidence.",
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
                "Read-only SQL Server view dbo.finished_lot_yield; no source-system writeback.",
                "Join by lot_id and plant_id; fields include yield_pct and loss_code.",
                "Refresh the view every five minutes.",
            ],
            "risks_and_notes": ["Formula changes require Quality owner approval."],
            "acceptance_criteria": [
                "Quality engineer can identify the top loss code for a selected plant.",
                "The dashboard does not write data back to SQL Server or SAP.",
            ],
            "collection_status": confirmed,
        }
    )


def test_scratch_and_template_use_different_interview_routes() -> None:
    model = _confirmed_model()
    model["collection_status"]["features"]["status"] = "missing"

    scratch = build_delivery_workflow(model, workflow_mode="scratch", language="en")
    template = build_delivery_workflow(model, workflow_mode="template", language="en")

    assert scratch["workflow_mode"] == "scratch"
    assert template["workflow_mode"] == "template"
    assert scratch["phases"][0]["key"] == "discover"
    assert template["phases"][0]["key"] == "validate_baseline"
    assert scratch["current_phase"] == "define_solution"
    assert template["current_phase"] == "close_template_gaps"
    assert scratch["blocking_fields"][0]["key"] == "features"
    assert not scratch["ready_for_documents"]


def test_draft_is_a_first_class_gap_closing_workflow() -> None:
    model = _confirmed_model()
    model["collection_status"]["rules"]["status"] = "missing"

    draft = build_delivery_workflow(model, workflow_mode="draft", language="en")

    assert draft["workflow_mode"] == "draft"
    assert draft["phases"][0]["key"] == "extract_draft"
    assert draft["current_phase"] == "close_draft_gaps"
    assert draft["blocking_fields"][0]["key"] == "rules"


def test_delivery_workflow_moves_to_package_then_handoff() -> None:
    model = _confirmed_model()

    before_document = build_delivery_workflow(
        model,
        workflow_mode="scratch",
        language="zh",
        has_prd_document=False,
    )
    after_document = build_delivery_workflow(
        model,
        workflow_mode="scratch",
        language="zh",
        has_prd_document=True,
    )

    assert before_document["current_phase"] == "package"
    assert before_document["ready_for_documents"]
    assert not before_document["ready_for_handoff"]
    assert after_document["current_phase"] == "handoff"
    assert after_document["ready_for_handoff"]


def test_coding_contract_is_low_ambiguity_and_small_model_ready() -> None:
    contract = build_coding_contract(
        _confirmed_model(),
        session_id="session-1",
        title="Yield Review",
        workflow_mode="template",
        template_id="yield-template",
        template_name="Yield dashboard template",
        language="en",
    )

    assert contract["schema_version"] == "1.0"
    assert contract["workflow_mode"] == "template"
    assert contract["source"]["template_id"] == "yield-template"
    assert contract["features"][0]["id"] == "F-001"
    assert contract["screens"][0]["id"] == "UI-001"
    assert contract["business_rules"][0]["id"] == "BR-001"
    assert contract["acceptance_tests"][0]["id"] == "AC-001"
    assert contract["implementation_packets"][0]["id"] == "P-01"
    assert contract["implementation_packets"][-1]["id"] == "P-05"
    assert contract["execution_policy"]["primary_source"] == "coding_contract"
    assert contract["delivery_readiness"]["ready_for_documents"]
    assert contract["data_policy"]["writeback_default"] == "forbidden"
    assert {item["type"] for item in contract["data_policy"]["allowed_sources"]} == {
        "sql_server",
        "sap",
        "mes",
        "qis",
        "qms",
        "file_upload",
    }

    markdown = render_coding_contract_markdown(contract)
    assert "# Coding Contract" in markdown
    assert "P-01" in markdown
    assert "F-001" in markdown
    assert "AC-001" in markdown
    assert "Do not invent" in markdown


def test_coding_contract_carries_blockers_instead_of_inventing() -> None:
    model = _confirmed_model()
    model["collection_status"]["integrations"] = {
        "status": "conflict",
        "reason": "SQL Server and SAP ownership disagree.",
        "pending_questions": ["Which system is the source of truth?"],
    }

    contract = build_coding_contract(
        model,
        session_id="session-2",
        title="Blocked integration",
        workflow_mode="scratch",
        language="en",
    )

    assert not contract["delivery_readiness"]["ready_for_documents"]
    assert contract["blockers"] == [
        {
            "key": "integrations",
            "status": "conflict",
            "reason": "SQL Server and SAP ownership disagree.",
            "questions": ["Which system is the source of truth?"],
        }
    ]
    assert "Which system is the source of truth?" in contract["unresolved_items"]


def test_handoff_puts_coding_contract_before_supporting_documents() -> None:
    with tempfile.TemporaryDirectory() as tmpdir, _postgres_test_store(tmpdir) as store:
        service = RequirementCollectorService(
            object(),
            store,
        )
        session = service.create_session(language="en")
        model = _confirmed_model()
        service._save_structured_requirement_model_cache(
            session.id,
            STRUCTURED_REQUIREMENT_CANONICAL_CACHE_KEY,
            0,
            model,
        )
        prd_path = service._prd_doc_path(session.id)
        prd_path.parent.mkdir(parents=True, exist_ok=True)
        prd_path.write_text("# PRD\n\nSupporting product detail.", encoding="utf-8")

        payload = service.build_browser_handoff_payload(session.id, "en")

        assert payload["handoff_ready"]
        assert payload["workflow_mode"] == "scratch"
        assert payload["coding_contract"]["contract_kind"] == "small_model_coding_contract"
        assert payload["documents"][0]["kind"] == "coding_contract"
        assert payload["documents"][0]["download_url"].endswith("/coding-contract?language=en")
        assert payload["documents"][1]["kind"] == "prd"
        assert "PRIMARY EXECUTION CONTRACT" in payload["implementation_prompt"]
        assert "Build Brief:" in payload["implementation_prompt"]
        assert "Supporting PRD:" not in payload["implementation_prompt"]
        assert "Supporting design:" not in payload["implementation_prompt"]
        assert '"id":"P-01"' in payload["implementation_prompt"]


def test_handoff_refuses_a_saved_prd_when_contract_has_blockers() -> None:
    with tempfile.TemporaryDirectory() as tmpdir, _postgres_test_store(tmpdir) as store:
        service = RequirementCollectorService(
            object(),
            store,
        )
        session = service.create_session(language="en")
        model = _confirmed_model()
        model["collection_status"]["acceptance"]["status"] = "missing"
        service._save_structured_requirement_model_cache(
            session.id,
            STRUCTURED_REQUIREMENT_CANONICAL_CACHE_KEY,
            0,
            model,
        )
        prd_path = service._prd_doc_path(session.id)
        prd_path.parent.mkdir(parents=True, exist_ok=True)
        prd_path.write_text("# PRD\n\nNot actually ready.", encoding="utf-8")

        handoff = service.create_coding_handoff(session.id, "en")

        assert "handoff_token" not in handoff
        assert not handoff["handoff_ready"]
        assert handoff["handoff_gaps"][0]["key"] == "acceptance"


def test_coding_contract_endpoint_serves_markdown_and_json() -> None:
    with tempfile.TemporaryDirectory() as tmpdir, _postgres_test_store(tmpdir) as store:
        service = RequirementCollectorService(
            object(),
            store,
        )
        session = service.create_session(language="en")
        service._save_structured_requirement_model_cache(
            session.id,
            STRUCTURED_REQUIREMENT_CANONICAL_CACHE_KEY,
            0,
            _confirmed_model(),
        )
        prd_path = service._prd_doc_path(session.id)
        prd_path.parent.mkdir(parents=True, exist_ok=True)
        prd_path.write_text("# PRD", encoding="utf-8")

        app = Flask(__name__)
        app.extensions["requirement_collector"] = service
        app.register_blueprint(api)
        client = app.test_client()

        markdown_response = client.get(
            f"/api/sessions/{session.id}/coding-contract?language=en"
        )
        json_response = client.get(
            f"/api/sessions/{session.id}/coding-contract?language=en&format=json"
        )

        assert markdown_response.status_code == 200
        assert markdown_response.mimetype == "text/markdown"
        assert "# Coding Contract" in markdown_response.get_data(as_text=True)
        assert "attachment; filename=coding-contract.md" in str(
            markdown_response.headers["Content-Disposition"]
        )
        assert json_response.status_code == 200
        assert json_response.get_json()["features"][0]["id"] == "F-001"


def test_scratch_and_template_sessions_expose_distinct_delivery_workflows() -> None:
    with tempfile.TemporaryDirectory() as tmpdir, _postgres_test_store(tmpdir) as store:
        service = RequirementCollectorService(
            object(),
            store,
        )
        scratch = service.create_session(language="en")
        template = service.create_session(
            template_id="qdm_finished_lot_yield_dashboard_template_en",
            language="en",
        )
        model = _confirmed_model()
        model["collection_status"]["objective"]["status"] = "missing"

        scratch_state = service.build_conversation_chain_state(scratch, model, "en")
        template_state = service.build_conversation_chain_state(template, model, "en")
        scratch_prompt = service._readiness_phase_directive_for_prompt(scratch, "en")
        template_prompt = service._readiness_phase_directive_for_prompt(template, "en")

        assert scratch_state["workflow_mode"] == "scratch"
        assert template_state["workflow_mode"] == "template"
        assert scratch_state["delivery_workflow"]["phases"][0]["key"] == "discover"
        assert template_state["delivery_workflow"]["phases"][0]["key"] == "validate_baseline"
        assert "INTERVIEW ROUTE = SCRATCH DISCOVERY" in scratch_prompt
        assert "INTERVIEW ROUTE = TEMPLATE VALIDATION" in template_prompt
