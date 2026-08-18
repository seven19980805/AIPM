from __future__ import annotations

import json
import unittest
from unittest.mock import Mock

from flask import Flask

from app.api import api


class InterviewApiV2Test(unittest.TestCase):
    def setUp(self) -> None:
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.register_blueprint(api)
        self.service = Mock()
        self.app.extensions["requirement_collector"] = self.service
        self.client = self.app.test_client()

    def test_post_messages_accepts_id_only_reply_context(self) -> None:
        self.service.send_user_message.return_value = {
            "assistant_message": "One proposal you can use.",
            "interview_state": {
                "schema_version": "2.0",
                "stage": "brief_discovery",
            },
        }

        response = self.client.post(
            "/api/sessions/session-1/messages",
            json={
                "message": "",
                "language": "en",
                "reply_context": {
                    "decision_id": "outcome",
                    "action": "request_example",
                },
            },
        )

        self.assertEqual(200, response.status_code)
        self.service.send_user_message.assert_called_once_with(
            "session-1",
            "",
            "en",
            "",
            reply_context={
                "decision_id": "outcome",
                "action": "request_example",
            },
        )

    def test_stream_summary_preserves_interview_state(self) -> None:
        self.service.stream_user_message.return_value = iter(
            [
                {"event": "content", "delta": "Recorded."},
                {
                    "event": "summary",
                    "interview_state": {
                        "schema_version": "2.0",
                        "stage": "brief_discovery",
                    },
                },
                {"event": "done"},
            ]
        )

        response = self.client.post(
            "/api/sessions/session-1/messages/stream",
            json={"message": "A measurable outcome", "language": "en"},
        )

        self.assertEqual(200, response.status_code)
        body = response.get_data(as_text=True)
        summary_line = next(
            line
            for line in body.splitlines()
            if line.startswith("data: ") and '"interview_state"' in line
        )
        payload = json.loads(summary_line.removeprefix("data: "))
        self.assertEqual("2.0", payload["interview_state"]["schema_version"])
        self.service.stream_user_message.assert_called_once_with(
            "session-1",
            "A measurable outcome",
            "en",
            "",
            reply_context=None,
        )

    def test_accepts_defer_decision_without_client_supplied_content(self) -> None:
        self.service.send_user_message.return_value = {
            "assistant_message": "Saved as an assumption.",
            "interview_state": {
                "schema_version": "2.0",
                "stage": "brief_discovery",
            },
        }

        response = self.client.post(
            "/api/sessions/session-1/messages",
            json={
                "language": "en",
                "reply_context": {
                    "decision_id": "outcome",
                    "action": "defer_decision",
                },
            },
        )

        self.assertEqual(200, response.status_code)
        self.service.send_user_message.assert_called_once_with(
            "session-1",
            "",
            "en",
            "",
            reply_context={
                "decision_id": "outcome",
                "action": "defer_decision",
            },
        )

    def test_rejects_client_proposal_without_proposal_id(self) -> None:
        response = self.client.post(
            "/api/sessions/session-1/messages",
            json={
                "reply_context": {
                    "decision_id": "outcome",
                    "action": "accept_proposal",
                    "proposal": {"text": "Client supplied content"},
                }
            },
        )

        self.assertEqual(400, response.status_code)
        self.assertIn("proposal_id", response.get_json()["error"])
        self.service.send_user_message.assert_not_called()


if __name__ == "__main__":
    unittest.main()
