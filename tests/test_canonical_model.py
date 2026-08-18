"""One canonical model per session; UI language is presentation only.

The structured model holds the user's own words, so it can never be translated
without breaking the verbatim grounding chain every safety gate depends on.
That makes the model canonical by necessity: the authoritative state and every
gate must be identical no matter which language the UI asks for.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from copy import deepcopy

from app.api import _session_detail_payload
from app.services.interview_state import decision_has_required_evidence_v2
from app.services.requirement_collector import (
    STRUCTURED_REQUIREMENT_CANONICAL_CACHE_KEY,
    RequirementCollectorService,
)
from app.services.structured_requirement_model import (
    empty_structured_requirement_model,
)
from tests.postgres_test_support import create_postgres_test_store


LANGUAGES = ("en", "zh", "de", "ms")


class CanonicalLLM:
    def __init__(self) -> None:
        self.structured_model = empty_structured_requirement_model()
        self.stream_text = "Recorded."
        self.chat_calls = 0

    def chat(self, messages, temperature: float = 0.3) -> str:
        self.chat_calls += 1
        return json.dumps(self.structured_model, ensure_ascii=False)

    def stream_chat(self, messages, temperature: float = 0.3):
        yield {"type": "content", "text": self.stream_text}


def _confirmed_model() -> dict:
    model = empty_structured_requirement_model()
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
    model["data_and_dependencies"] = [
        "Read lot records from MES; the first release is read-only.",
    ]
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
        "integrations",
    ):
        model["collection_status"][key]["status"] = "confirmed"
    return model


class CanonicalModelTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.llm = CanonicalLLM()
        self.service = RequirementCollectorService(
            self.llm,
            create_postgres_test_store(self, self.tmpdir.name),
        )
        self.session = self.service.create_session(language="en")

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def _seed(self, model: dict) -> None:
        self.service._save_interview_model_at_current_message_count(
            self.session, model, "en"
        )

    def test_snapshot_model_is_identical_in_every_language(self) -> None:
        self._seed(_confirmed_model())

        snapshots = {
            language: self.service.get_structured_requirement_snapshot(
                self.session.id, language
            )["structured_requirement_model"]
            for language in LANGUAGES
        }

        baseline = snapshots["en"]
        for language in LANGUAGES[1:]:
            self.assertEqual(
                baseline,
                snapshots[language],
                f"{language} model diverges from the canonical model",
            )

    def test_gates_are_identical_in_every_language(self) -> None:
        self._seed(_confirmed_model())

        decisions = (
            "outcome",
            "actor_action",
            "v1_flow",
            "data_boundary",
            "acceptance",
            "ownership",
        )
        for decision_id in decisions:
            with self.subTest(decision_id=decision_id):
                results = {
                    language: decision_has_required_evidence_v2(
                        self.service.get_structured_requirement_snapshot(
                            self.session.id, language
                        )["structured_requirement_model"],
                        decision_id,
                    )
                    for language in LANGUAGES
                }
                self.assertEqual(
                    1,
                    len(set(results.values())),
                    f"{decision_id} gate differs by language: {results}",
                )

    def test_authoritative_state_is_identical_in_every_language(self) -> None:
        self._seed(_confirmed_model())

        states = {
            language: _session_detail_payload(
                self.service,
                self.service.get_session(self.session.id),
                language,
            )["interview_state"]
            for language in LANGUAGES
        }
        baseline = states["en"]
        for language in LANGUAGES[1:]:
            state = states[language]
            self.assertEqual(
                baseline["stage"],
                state["stage"],
                f"{language} stage diverges",
            )
            self.assertEqual(
                baseline["brief"],
                state["brief"],
                f"{language} brief counters diverge",
            )
            self.assertEqual(
                (baseline["next_decision"] or {}).get("decision_id"),
                (state["next_decision"] or {}).get("decision_id"),
                f"{language} active decision diverges",
            )

    def test_only_presentation_copy_changes_with_language(self) -> None:
        model = _confirmed_model()
        # Leave one decision open so a card exists to localize.
        model["acceptance_criteria"] = []
        model["collection_status"]["acceptance"]["status"] = "missing"
        self._seed(model)

        questions = {
            language: (
                _session_detail_payload(
                    self.service,
                    self.service.get_session(self.session.id),
                    language,
                )["interview_state"]["next_decision"]
                or {}
            ).get("question", "")
            for language in LANGUAGES
        }

        self.assertEqual(
            len(LANGUAGES),
            len({question for question in questions.values() if question}),
            f"decision copy should be localized, got {questions}",
        )


class LegacyLocalizedCacheTest(CanonicalModelTest):
    """Historical sessions cached one model per language."""

    def test_legacy_localized_entries_do_not_split_the_state(self) -> None:
        canonical = _confirmed_model()
        self._seed(canonical)

        # A legacy session also carries divergent per-language entries written
        # before the canonical model existed.
        stale = deepcopy(canonical)
        stale["background"]["objective"] = ""
        stale["data_and_dependencies"] = []
        stale["collection_status"]["objective"]["status"] = "missing"
        stale["collection_status"]["integrations"]["status"] = "missing"
        message_count = self.service._message_count(
            self.service.get_session(self.session.id).messages
        )
        for language in ("zh", "de"):
            self.service._save_structured_requirement_model_cache(
                self.session.id,
                language,
                message_count,
                stale,
            )

        snapshots = {
            language: self.service.get_structured_requirement_snapshot(
                self.session.id, language
            )["structured_requirement_model"]
            for language in LANGUAGES
        }
        for language in LANGUAGES:
            self.assertEqual(
                "Reduce defect escapes by 15% next quarter.",
                snapshots[language]["background"]["objective"],
                f"{language} fell back to a stale localized model",
            )
            self.assertTrue(
                decision_has_required_evidence_v2(
                    snapshots[language], "data_boundary"
                ),
                f"{language} lost the confirmed data boundary",
            )

    def test_canonical_entry_is_adopted_when_only_localized_exist(self) -> None:
        model = _confirmed_model()
        message_count = self.service._message_count(
            self.service.get_session(self.session.id).messages
        )
        # Simulate a pre-canonical session: only a localized entry exists.
        self.service._save_structured_requirement_model_cache(
            self.session.id, "zh", message_count, model
        )

        snapshot = self.service.get_structured_requirement_snapshot(
            self.session.id, "en"
        )["structured_requirement_model"]

        self.assertEqual(
            "Reduce defect escapes by 15% next quarter.",
            snapshot["background"]["objective"],
        )
        adopted = self.service._get_cached_structured_requirement_model(
            self.session.id,
            STRUCTURED_REQUIREMENT_CANONICAL_CACHE_KEY,
            message_count,
        )
        self.assertIsNotNone(adopted, "the localized model must be adopted")


class CanonicalExtractionLanguageTest(CanonicalModelTest):
    """Extraction must be deterministic and must not translate the user."""

    def _extraction_prompt(self, request_language: str) -> str:
        self.service._append_message(
            self.session.id, "user", "只读获取 MES 批次记录。"
        )
        session = self.service.get_session(self.session.id)
        return self.service._structured_requirement_model_prompt(
            session, request_language
        )

    def test_extraction_language_follows_the_session_not_the_request(self) -> None:
        self.service.set_session_language(self.session.id, "zh")

        for request_language in LANGUAGES:
            with self.subTest(request_language=request_language):
                prompt = self._extraction_prompt(request_language)
                self.assertIn(
                    "Output all field values in Simplified Chinese.",
                    prompt,
                    "extraction must stay in the session language so the "
                    "canonical model keeps the user's own words",
                )

    def test_a_request_language_never_rewrites_the_canonical_model(self) -> None:
        self.service.set_session_language(self.session.id, "zh")
        model = _confirmed_model()
        model["background"]["objective"] = "下季度将缺陷漏出率降低 15%。"
        self._seed(model)

        for language in LANGUAGES:
            snapshot = self.service.get_structured_requirement_snapshot(
                self.session.id, language
            )["structured_requirement_model"]
            self.assertEqual(
                "下季度将缺陷漏出率降低 15%。",
                snapshot["background"]["objective"],
                f"{language} request rewrote canonical evidence",
            )


class CanonicalCacheHygieneTest(CanonicalModelTest):
    def test_only_the_canonical_slot_is_written(self) -> None:
        self._seed(_confirmed_model())
        self.service._promote_cached_structured_requirement_model(
            self.service.get_session(self.session.id), "de"
        )

        raw = self.service.session_store.get_session(self.session.id)
        cache = raw["structured_requirement_cache"]
        if isinstance(cache, str):
            cache = json.loads(cache)

        self.assertEqual(
            {STRUCTURED_REQUIREMENT_CANONICAL_CACHE_KEY},
            set(cache),
            f"per-language cache slots must not be written any more: {set(cache)}",
        )

    def test_the_localized_read_path_is_gone(self) -> None:
        self.assertFalse(
            hasattr(
                self.service,
                "_get_cached_localized_structured_requirement_model",
            ),
            "the localized read path caused the divergence and must not survive",
        )


class SessionLanguageTest(CanonicalModelTest):
    def test_session_language_is_persisted_and_readable(self) -> None:
        session = self.service.create_session(language="zh")

        stored = self.service.get_session(session.id)

        self.assertEqual("zh", stored.language)

    def test_session_language_can_be_changed_and_persists(self) -> None:
        session = self.service.create_session(language="en")

        self.service.set_session_language(session.id, "de")

        self.assertEqual("de", self.service.get_session(session.id).language)

    def test_legacy_session_without_a_language_gets_a_usable_default(self) -> None:
        session = self.service.create_session(language="en")
        self.service.session_store.set_session_language(session.id, "")

        stored = self.service.get_session(session.id)

        self.assertIn(stored.language, {"en", "de", "zh", "ms"})


if __name__ == "__main__":
    unittest.main()


class SessionLanguageEndpointTest(unittest.TestCase):
    """PATCH /api/sessions/<id>/language is the only write path for it."""

    def setUp(self) -> None:
        from flask import Flask

        from app.api import api

        self.tmpdir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.service = RequirementCollectorService(
            CanonicalLLM(),
            create_postgres_test_store(self, self.tmpdir.name),
        )
        app = Flask(__name__)
        app.extensions["requirement_collector"] = self.service
        app.register_blueprint(api)
        app.testing = True
        self.client = app.test_client()
        self.session = self.service.create_session(language="en")

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def _patch(self, language: str):
        return self.client.patch(
            f"/api/sessions/{self.session.id}/language",
            json={"language": language},
        )

    def test_an_explicit_switch_persists_and_echoes_the_new_language(self) -> None:
        response = self._patch("zh")

        self.assertEqual(200, response.status_code)
        self.assertEqual("zh", response.get_json()["language"])
        self.assertEqual("zh", self.service.get_session(self.session.id).language)

    def test_reading_a_session_never_changes_its_language(self) -> None:
        self._patch("zh")

        for language in LANGUAGES:
            self.client.get(
                f"/api/sessions/{self.session.id}?language={language}"
            )

        self.assertEqual("zh", self.service.get_session(self.session.id).language)

    def test_message_request_language_never_changes_the_session_language(self) -> None:
        response = self.client.post(
            f"/api/sessions/{self.session.id}/messages",
            json={
                "message": "Read lot records from MES without writing back.",
                "language": "zh",
            },
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual("en", self.service.get_session(self.session.id).language)

    def test_stream_request_language_never_changes_the_session_language(self) -> None:
        response = self.client.post(
            f"/api/sessions/{self.session.id}/messages/stream",
            json={
                "message": "Read lot records from MES without writing back.",
                "language": "de",
            },
        )

        self.assertEqual(200, response.status_code)
        self.assertIn(b"event: done", response.data)
        self.assertEqual("en", self.service.get_session(self.session.id).language)

    def test_an_unsupported_language_is_rejected(self) -> None:
        response = self._patch("fr")

        self.assertEqual(400, response.status_code)
        self.assertEqual("en", self.service.get_session(self.session.id).language)

    def test_an_unknown_session_reports_not_found(self) -> None:
        response = self.client.patch(
            "/api/sessions/does-not-exist/language",
            json={"language": "zh"},
        )

        self.assertEqual(404, response.status_code)

    def test_the_switch_does_not_rewrite_canonical_evidence(self) -> None:
        model = _confirmed_model()
        model["background"]["objective"] = "Reduce defect escapes by 15% next quarter."
        self.service._save_interview_model_at_current_message_count(
            self.session, model, "en"
        )

        self._patch("zh")

        snapshot = self.service.get_structured_requirement_snapshot(
            self.session.id, "zh"
        )["structured_requirement_model"]
        self.assertEqual(
            "Reduce defect escapes by 15% next quarter.",
            snapshot["background"]["objective"],
        )
