#!/usr/bin/env python3
"""Runtime regression checks for the IC Substrate expert PM flow.

Unlike the static contract verifier, this script imports the service layer and
executes the starter-department path with a fake LLM and temporary SQLite DB.
It catches regressions where the code still contains the right strings but the
actual prompt/gate state no longer routes like an expert PM.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from app import create_app
    from app.services.requirement_collector import (
        RequirementCollectorService,
        STRUCTURED_REQUIREMENT_CANONICAL_CACHE_KEY,
    )
    from app.services.session_store import SQLiteSessionStore
except ModuleNotFoundError as exc:
    missing = exc.name or "dependency"
    print(
        "FAIL: runtime verifier requires backend dependencies. "
        f"Install requirements.txt first; missing module: {missing}",
        file=sys.stderr,
    )
    raise SystemExit(1) from exc


TEMPLATE_ID = "qdm_finished_lot_yield_dashboard_template_zh_cn"


class SparseInternalModel:
    """Fake internal model that intentionally omits requesting_department."""

    def chat(self, *args: Any, **kwargs: Any) -> str:
        _ = args, kwargs
        return json.dumps(
            {
                "background": {"objective": "Build an IC Substrate dashboard"},
                "product_context": {"software_type": "dashboard"},
                "collection_status": {},
            }
        )


class FirstQuestionThenSparseExtraction:
    """Fake model for API message flow: question first, sparse JSON second."""

    def __init__(self) -> None:
        self.chat_count = 0

    def chat(self, *args: Any, **kwargs: Any) -> str:
        _ = args, kwargs
        self.chat_count += 1
        if self.chat_count % 2 == 1:
            return "请确认这个系统首版要解决哪个质量业务动作？"
        return json.dumps(
            {
                "background": {"objective": "Build a defect dashboard"},
                "product_context": {"software_type": "dashboard"},
                "collection_status": {},
            }
        )


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def make_service(tmp_dir: str) -> RequirementCollectorService:
    store = SQLiteSessionStore(str(Path(tmp_dir) / "rqmd.sqlite3"))
    return RequirementCollectorService(SparseInternalModel(), store)


def canonical_model(service: RequirementCollectorService, session_id: str, message_count: int) -> dict[str, Any]:
    model = service._get_latest_cached_structured_requirement_model(
        session_id,
        STRUCTURED_REQUIREMENT_CANONICAL_CACHE_KEY,
        message_count,
    )
    require(model is not None, f"missing canonical structured model at message_count={message_count}")
    return model


def assert_starter_department_runtime() -> None:
    expected = {
        "Production": {
            "gate_keys": {
                "production_route_time_boundary",
                "production_kpi_formula_grain",
                "production_dispatch_exception_control",
            },
            "prompt_markers": ["Production route", "Production KPI", "A/B/C"],
        },
        "Quality": {
            "gate_keys": {
                "quality_defect_disposition",
                "quality_inspection_coverage",
                "quality_capa_traceability",
            },
            "prompt_markers": ["Quality defect taxonomy", "Quality inspection coverage", "A/B/C"],
        },
        "TDI": {
            "gate_keys": {
                "tdi_request_triage_sla",
                "tdi_engineering_data_mapping",
                "tdi_request_writeback_approval",
            },
            "prompt_markers": ["TDI request intake", "TDI engineering data mapping", "A/B/C"],
        },
    }

    with tempfile.TemporaryDirectory() as tmp:
        service = make_service(tmp)
        for department, contract in expected.items():
            session = service.create_session(
                template_id=TEMPLATE_ID,
                language="zh",
                starter_department=department,
            )
            model = canonical_model(service, session.id, 0)
            actual_department = str(model["product_context"].get("requesting_department", "")).strip()
            require(actual_department == department, f"{department}: starter department not cached")

            chain_state = service.build_conversation_chain_state(session, model, "zh")
            require(chain_state["current_track"] == department, f"{department}: chain did not route to starter track")

            gate = service._ic_substrate_readiness_evidence_gate(session, model)
            require(
                str(gate.get("department_specific_evidence", "")).lower() == department.lower(),
                f"{department}: readiness gate missing department-specific evidence route",
            )
            gate_keys = {str(check.get("key", "")) for check in gate["checks"] if isinstance(check, dict)}
            missing_gate_keys = contract["gate_keys"] - gate_keys
            require(not missing_gate_keys, f"{department}: missing gate keys {sorted(missing_gate_keys)}")

            prompt_state = service._conversation_chain_state_for_prompt(session, "zh")
            require("IC Substrate 下一问证据缺口" in prompt_state, f"{department}: prompt missing evidence-gap section")
            missing_markers = [marker for marker in contract["prompt_markers"] if marker not in prompt_state]
            require(not missing_markers, f"{department}: prompt missing markers {missing_markers}")


def assert_sparse_extraction_preserves_department() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        service = make_service(tmp)
        session = service.create_session(
            template_id=TEMPLATE_ID,
            language="zh",
            starter_department="Quality",
        )
        service._append_message(session.id, "user", "想做一个缺陷看板")
        refreshed_session = service.get_session(session.id)
        require(refreshed_session is not None, "failed to reload session after user message")

        model = service._build_and_cache_structured_requirement_model(refreshed_session, "zh")
        department = str(model["product_context"].get("requesting_department", "")).strip()
        require(department == "Quality", "sparse extraction lost starter department")

        chain_state = service.build_conversation_chain_state(refreshed_session, model, "zh")
        require(chain_state["current_track"] == "Quality", "sparse extraction lost Quality chain route")


def assert_language_locked_evidence_guidance() -> None:
    language_markers = {
        "en": "IC Substrate evidence gaps for the next question",
        "zh": "IC Substrate 下一问证据缺口",
        "de": "IC Substrate Evidence-Gaps fuer die naechste Frage",
        "ms": "Gap evidence IC Substrate untuk soalan seterusnya",
    }
    with tempfile.TemporaryDirectory() as tmp:
        service = make_service(tmp)
        for language, marker in language_markers.items():
            session = service.create_session(
                template_id=TEMPLATE_ID,
                language=language,
                starter_department="Quality",
            )
            prompt_state = service._conversation_chain_state_for_prompt(session, language)
            require(marker in prompt_state, f"{language}: missing localized evidence guidance marker")


def assert_api_starter_department_contract() -> None:
    expected_tracks = {
        "Production": "Production",
        "Quality": "Quality",
        "TDI": "TDI",
    }
    with tempfile.TemporaryDirectory() as tmp:
        previous_db_path = os.environ.get("SQLITE_DB_PATH")
        os.environ["SQLITE_DB_PATH"] = str(Path(tmp) / "api-rqmd.sqlite3")
        try:
            app = create_app()
        finally:
            if previous_db_path is None:
                os.environ.pop("SQLITE_DB_PATH", None)
            else:
                os.environ["SQLITE_DB_PATH"] = previous_db_path

        app.config.update(TESTING=True)
        client = app.test_client()
        for department, expected_track in expected_tracks.items():
            response = client.post(
                "/api/sessions",
                json={
                    "template_id": TEMPLATE_ID,
                    "template_start_mode": "guided",
                    "starter_department": department,
                },
                headers={"X-Language": "zh"},
            )
            require(response.status_code == 201, f"{department}: API create session failed: {response.status_code}")
            payload = response.get_json() or {}
            model = payload.get("structured_requirement_model")
            require(isinstance(model, dict), f"{department}: API missing structured requirement model")
            product_context = model.get("product_context")
            require(isinstance(product_context, dict), f"{department}: API missing product_context")
            require(
                product_context.get("requesting_department") == department,
                f"{department}: API response lost starter department",
            )
            chain_state = payload.get("conversation_chain_state")
            require(isinstance(chain_state, dict), f"{department}: API missing conversation_chain_state")
            require(
                chain_state.get("current_track") == expected_track,
                f"{department}: API chain_state current_track mismatch",
            )


def assert_api_first_message_preserves_expert_route() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        previous_db_path = os.environ.get("SQLITE_DB_PATH")
        os.environ["SQLITE_DB_PATH"] = str(Path(tmp) / "api-message-rqmd.sqlite3")
        try:
            app = create_app()
        finally:
            if previous_db_path is None:
                os.environ.pop("SQLITE_DB_PATH", None)
            else:
                os.environ["SQLITE_DB_PATH"] = previous_db_path

        app.extensions["requirement_collector"].llm_client = FirstQuestionThenSparseExtraction()
        app.config.update(TESTING=True)
        client = app.test_client()

        create_response = client.post(
            "/api/sessions",
            json={
                "template_id": TEMPLATE_ID,
                "template_start_mode": "guided",
                "starter_department": "Quality",
            },
            headers={"X-Language": "zh"},
        )
        require(create_response.status_code == 201, f"API create session failed: {create_response.status_code}")
        session_id = (create_response.get_json() or {}).get("session_id")
        require(isinstance(session_id, str) and session_id, "API create session missing session_id")

        message_response = client.post(
            f"/api/sessions/{session_id}/messages",
            json={
                "message": "想做一个缺陷看板",
                "language": "zh",
            },
        )
        require(message_response.status_code == 200, f"API send message failed: {message_response.status_code}")
        payload = message_response.get_json() or {}
        assistant_message = str(payload.get("assistant_message", ""))
        require("A. 同意按上面的建议口径" in assistant_message, "API assistant message missing zh fallback choices")

        model = payload.get("structured_requirement_model")
        require(isinstance(model, dict), "API message response missing structured requirement model")
        product_context = model.get("product_context")
        require(isinstance(product_context, dict), "API message response missing product_context")
        require(
            product_context.get("requesting_department") == "Quality",
            "API first message sparse extraction lost starter department",
        )
        chain_state = payload.get("conversation_chain_state")
        require(isinstance(chain_state, dict), "API message response missing conversation_chain_state")
        require(
            chain_state.get("current_track") == "Quality",
            "API first message sparse extraction lost Quality chain route",
        )
        require(payload.get("structured_requirement_sync_status") == "ready", "API message response not marked ready")


def main() -> None:
    assert_starter_department_runtime()
    assert_sparse_extraction_preserves_department()
    assert_language_locked_evidence_guidance()
    assert_api_starter_department_contract()
    assert_api_first_message_preserves_expert_route()
    print("IC Substrate runtime expert PM contracts verified.")


if __name__ == "__main__":
    main()
