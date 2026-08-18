import sys
import tempfile
import unittest
from pathlib import Path

from flask import Flask


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.api import api
from app.services.requirement_collector import RequirementCollectorService
from tests.postgres_test_support import create_postgres_test_store


class FakeLLMClient:
    def chat(self, messages, temperature=0.3):
        raise AssertionError("Session launch must not call the LLM.")

    def stream_chat(self, messages, temperature=0.3):
        raise AssertionError("Session launch must not call the LLM.")


class SessionLaunchTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.service = RequirementCollectorService(
            FakeLLMClient(),
            create_postgres_test_store(self, self.tmpdir.name),
        )

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def _launch_context(self, session_id: str, language: str = "en") -> dict:
        session = self.service.get_session(session_id)
        self.assertIsNotNone(session)
        snapshot = self.service.get_structured_requirement_snapshot(session_id, language)
        return self.service.build_session_launch_context(
            session,
            language,
            structured_requirement_model=snapshot["structured_requirement_model"],
            conversation_chain_state=snapshot["conversation_chain_state"],
        )

    def test_template_launch_is_actionable_without_fabricating_messages(self) -> None:
        session = self.service.create_session(
            template_id="qdm_finished_lot_yield_dashboard_template_en",
            language="en",
        )

        launch_context = self._launch_context(session.id)

        self.assertEqual(session.messages, [])
        self.assertEqual(launch_context["version"], 2)
        self.assertEqual(launch_context["mode"], "template")
        self.assertEqual(launch_context["status"], "not_started")
        self.assertEqual(
            launch_context["source"]["id"],
            "qdm_finished_lot_yield_dashboard_template_en",
        )
        self.assertEqual(
            launch_context["title"],
            "QDM Finished Lot Yield Dashboard Requirement Template",
        )
        self.assertIn("Finished Lot", launch_context["description"])
        self.assertEqual(
            launch_context["question"],
            "Which real scenario should this template support first?",
        )
        self.assertEqual(len(launch_context["stages"]), 5)
        self.assertEqual(launch_context["stages"][0]["status"], "current")
        self.assertEqual(
            [suggestion["label"] for suggestion in launch_context["suggestions"]],
            ["Business outcome", "Current workflow", "Data source"],
        )

    def test_template_launch_context_is_rebuilt_after_reload(self) -> None:
        session = self.service.create_session(
            template_id="business_process_requirement_template_en",
            language="en",
        )

        first = self._launch_context(session.id)
        reloaded = self._launch_context(session.id)

        self.assertEqual(reloaded, first)
        self.assertEqual(reloaded["source"]["type"], "template")
        self.assertEqual(reloaded["stages"][0]["key"], "outcome")

    def test_plain_session_has_a_lightweight_conversation_launch(self) -> None:
        session = self.service.create_session(language="en")

        launch_context = self._launch_context(session.id)

        self.assertEqual(launch_context["mode"], "scratch")
        self.assertEqual(launch_context["source"]["type"], "scratch")
        self.assertIn("business action", launch_context["question"].lower())
        self.assertEqual(len(launch_context["stages"]), 5)
        self.assertEqual(
            [suggestion["label"] for suggestion in launch_context["suggestions"]],
            ["Production", "Quality", "TDI"],
        )


class SessionLaunchApiTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.service = RequirementCollectorService(
            FakeLLMClient(),
            create_postgres_test_store(self, self.tmpdir.name),
        )
        app = Flask(__name__)
        app.extensions["requirement_collector"] = self.service
        app.register_blueprint(api)
        app.testing = True
        self.client = app.test_client()

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_create_and_get_return_the_same_launch_contract(self) -> None:
        created_response = self.client.post(
            "/api/sessions",
            json={
                "language": "en",
                "template_id": "business_process_requirement_template_en",
                "template_start_mode": "guided",
            },
        )

        self.assertEqual(created_response.status_code, 201)
        created = created_response.get_json()
        loaded_response = self.client.get(
            f"/api/sessions/{created['session_id']}?language=en",
        )
        self.assertEqual(loaded_response.status_code, 200)
        loaded = loaded_response.get_json()

        self.assertEqual(created["launch_context"], loaded["launch_context"])
        self.assertEqual(created["launch_context"]["mode"], "template")
        self.assertEqual(created["messages"], [])
        self.assertEqual(loaded["messages"], [])


if __name__ == "__main__":
    unittest.main()
