"""Adding sessions.language must not mislabel existing sessions.

The column default marks every historical row English. Sessions that were
actually worked in another language must be recovered from the evidence already
in their structured-requirement cache, or extraction would translate the user's
own words and break the grounding chain every gate depends on.
"""

from __future__ import annotations

import tempfile
import unittest

from app.services.requirement_collector import (
    STRUCTURED_REQUIREMENT_CANONICAL_CACHE_KEY,
    RequirementCollectorService,
)
from app.services.structured_requirement_model import (
    empty_structured_requirement_model,
)
from tests.postgres_test_support import create_postgres_test_store


class BackfillLLM:
    def chat(self, messages, temperature: float = 0.3) -> str:
        return "{}"

    def stream_chat(self, messages, temperature: float = 0.3):
        yield {"type": "content", "text": "ok"}


class SessionLanguageBackfillTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.store = create_postgres_test_store(self, self.tmpdir.name)
        self.service = RequirementCollectorService(BackfillLLM(), self.store)

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def _legacy_session(self, cache_languages: dict[str, int]) -> str:
        session = self.service.create_session(language="en")
        for language, message_count in cache_languages.items():
            self.service._save_structured_requirement_model_cache(
                session.id,
                language,
                message_count,
                empty_structured_requirement_model(),
            )
        # The naive column default marks every historical row English.
        self.store.set_session_language(session.id, "en")
        return session.id

    def test_a_chinese_session_is_recovered_from_its_cache(self) -> None:
        session_id = self._legacy_session({"zh": 8})

        self.store.backfill_session_languages(force=True)

        self.assertEqual("zh", self.service.get_session(session_id).language)

    def test_the_most_used_language_wins(self) -> None:
        session_id = self._legacy_session({"en": 2, "zh": 9, "de": 4})

        self.store.backfill_session_languages(force=True)

        self.assertEqual("zh", self.service.get_session(session_id).language)

    def test_an_english_session_is_left_alone(self) -> None:
        session_id = self._legacy_session({"en": 6})

        self.store.backfill_session_languages(force=True)

        self.assertEqual("en", self.service.get_session(session_id).language)

    def test_the_canonical_slot_is_not_mistaken_for_a_language(self) -> None:
        session = self.service.create_session(language="en")
        self.service._save_structured_requirement_model_cache(
            session.id,
            STRUCTURED_REQUIREMENT_CANONICAL_CACHE_KEY,
            5,
            empty_structured_requirement_model(),
        )
        self.store.set_session_language(session.id, "en")

        self.store.backfill_session_languages(force=True)

        self.assertEqual("en", self.service.get_session(session.id).language)

    def test_a_session_without_a_cache_is_left_alone(self) -> None:
        session = self.service.create_session(language="ms")

        self.store.backfill_session_languages(force=True)

        self.assertEqual("ms", self.service.get_session(session.id).language)

    def test_the_backfill_runs_once_and_respects_a_later_choice(self) -> None:
        session_id = self._legacy_session({"zh": 8})
        self.store.backfill_session_languages(force=True)
        self.assertEqual("zh", self.service.get_session(session_id).language)

        # The user then explicitly picks English in the UI.
        self.service.set_session_language(session_id, "en")
        # A later start-up must not undo that choice.
        self.store.backfill_session_languages()

        self.assertEqual("en", self.service.get_session(session_id).language)

    def test_the_backfill_is_idempotent(self) -> None:
        self._legacy_session({"zh": 8})

        first = self.store.backfill_session_languages(force=True)
        second = self.store.backfill_session_languages(force=True)

        self.assertEqual(1, first)
        self.assertEqual(0, second)


if __name__ == "__main__":
    unittest.main()
