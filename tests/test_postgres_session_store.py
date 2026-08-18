from __future__ import annotations

import os
import tempfile
import unittest
import uuid
from pathlib import Path

from app.services import session_store as session_store_module


TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://aipm:aipm_local_dev@127.0.0.1:5432/aipm",
)


class PostgreSQLSessionStoreTest(unittest.TestCase):
    def _create_store(self):
        store_class = session_store_module.PostgreSQLSessionStore
        tmpdir = tempfile.TemporaryDirectory()
        schema = f"test_session_store_{uuid.uuid4().hex}"
        store = store_class(
            TEST_DATABASE_URL,
            storage_dir=Path(tmpdir.name),
            schema=schema,
        )
        self.addCleanup(tmpdir.cleanup)
        self.addCleanup(store.close, drop_schema=True)
        return store

    def test_persists_unicode_session_state_across_store_restart(self) -> None:
        store_class = getattr(session_store_module, "PostgreSQLSessionStore", None)
        self.assertIsNotNone(
            store_class,
            "PostgreSQLSessionStore must replace the SQLite runtime store.",
        )

        schema = f"test_session_store_{uuid.uuid4().hex}"
        with tempfile.TemporaryDirectory() as tmpdir:
            store = store_class(
                TEST_DATABASE_URL,
                storage_dir=Path(tmpdir),
                schema=schema,
            )
            store.create_session(
                "session-中文",
                "2026-07-24T04:00:00+00:00",
                title="中文持久化验证",
            )
            message_id = store.append_message(
                "session-中文",
                "user",
                "生产计划员需要查看缺料批次。",
                "2026-07-24T04:01:00+00:00",
            )
            store.save_structured_requirement_cache_entry(
                "session-中文",
                "zh",
                1,
                {"background": {"objective": "减少缺料停线"}},
                "2026-07-24T04:02:00+00:00",
            )
            store.close()

            reopened = store_class(
                TEST_DATABASE_URL,
                storage_dir=Path(tmpdir),
                schema=schema,
            )
            try:
                session = reopened.get_session("session-中文")
                self.assertIsNotNone(session)
                self.assertEqual("中文持久化验证", session["title"])
                self.assertEqual(message_id, session["messages"][0]["message_id"])
                self.assertEqual(
                    "生产计划员需要查看缺料批次。",
                    session["messages"][0]["content"],
                )
                cache = reopened.get_structured_requirement_cache_entry(
                    "session-中文",
                    "zh",
                )
                self.assertEqual(
                    "减少缺料停线",
                    cache["model"]["background"]["objective"],
                )
            finally:
                reopened.close(drop_schema=True)

    def test_messages_schema_has_non_null_jsonb_metadata_default(self) -> None:
        store = self._create_store()

        with store._connect() as connection:
            column = connection.execute(
                """
                SELECT data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_schema = %s
                  AND table_name = 'messages'
                  AND column_name = 'metadata'
                """,
                (store.schema,),
            ).fetchone()

        self.assertIsNotNone(column)
        self.assertEqual("jsonb", column["data_type"])
        self.assertEqual("NO", column["is_nullable"])
        self.assertIn("'{}'::jsonb", column["column_default"])

    def test_startup_non_destructively_adds_metadata_to_legacy_messages_table(
        self,
    ) -> None:
        store_class = session_store_module.PostgreSQLSessionStore
        schema = f"test_session_store_{uuid.uuid4().hex}"

        with tempfile.TemporaryDirectory() as tmpdir:
            legacy_store = store_class(
                TEST_DATABASE_URL,
                storage_dir=Path(tmpdir),
                schema=schema,
            )
            legacy_store.create_session(
                "legacy-session",
                "2026-07-24T04:00:00+00:00",
            )
            legacy_store.append_message(
                "legacy-session",
                "user",
                "legacy content",
                "2026-07-24T04:01:00+00:00",
            )
            with legacy_store._connect() as connection:
                connection.execute(
                    "ALTER TABLE messages DROP COLUMN IF EXISTS metadata"
                )
            legacy_store.close()

            reopened = store_class(
                TEST_DATABASE_URL,
                storage_dir=Path(tmpdir),
                schema=schema,
            )
            try:
                session = reopened.get_session("legacy-session")
                self.assertEqual(
                    {},
                    session["messages"][0]["metadata"],
                )
                self.assertEqual(
                    "legacy content",
                    session["messages"][0]["content"],
                )
            finally:
                reopened.close(drop_schema=True)

    def test_message_metadata_round_trips_and_legacy_calls_default_to_empty(
        self,
    ) -> None:
        store = self._create_store()
        store.create_session(
            "metadata-session",
            "2026-07-24T04:00:00+00:00",
        )
        proposal_metadata = {
            "interview_turn": {
                "decision_id": "outcome",
                "proposal": {
                    "proposal_id": "proposal-1",
                    "text": "季度内将误判逃逸率降低 15%",
                },
            }
        }
        store.append_message(
            "metadata-session",
            "assistant",
            "可以采用这个目标。",
            "2026-07-24T04:01:00+00:00",
            metadata=proposal_metadata,
        )
        store.append_message(
            "metadata-session",
            "user",
            "旧调用仍可用",
            "2026-07-24T04:02:00+00:00",
        )

        messages = store.get_session("metadata-session")["messages"]
        self.assertEqual(proposal_metadata, messages[0]["metadata"])
        self.assertEqual({}, messages[1]["metadata"])

    def test_supports_complete_session_and_document_contract(self) -> None:
        store = self._create_store()
        created_at = "2026-07-24T05:00:00+00:00"
        store.create_session("session-1", created_at, title="Initial title")
        chat_id = store.append_message(
            "session-1",
            "assistant",
            "model-only content",
            "2026-07-24T05:01:00+00:00",
            display_content="用户可见内容",
        )
        document_id = store.append_message(
            "session-1",
            "assistant",
            "# 开发简报",
            "2026-07-24T05:02:00+00:00",
            kind="prd_doc",
            download_filename="开发简报.docx",
            storage_path="/tmp/开发简报.md",
        )

        sessions = store.list_sessions()
        self.assertEqual(1, len(sessions))
        self.assertEqual("用户可见内容", sessions[0]["last_message_preview"])
        self.assertEqual(2, sessions[0]["message_count"])
        self.assertEqual(
            document_id,
            store.get_latest_document_message("session-1", "prd_doc")[
                "message_id"
            ],
        )
        self.assertEqual(
            chat_id,
            store.get_message_document("session-1", chat_id)["message_id"],
        )

        store.update_session_title("session-1", "Updated title")
        store.update_session_prompt_template("session-1", "standard")
        store.update_session_applied_template(
            "session-1",
            "template-1",
            "模板一",
        )
        session = store.get_session("session-1")
        self.assertEqual("Updated title", session["title"])
        self.assertEqual("standard", session["prompt_template"])
        self.assertEqual("template-1", session["applied_template_id"])
        self.assertEqual({}, session["structured_requirement_cache"])

        self.assertTrue(store.delete_session("session-1"))
        self.assertFalse(store.delete_session("session-1"))
        self.assertIsNone(store.get_message_document("session-1", document_id))

    def test_supports_coding_handoff_lifecycle(self) -> None:
        store = self._create_store()
        store.create_session(
            "session-2",
            "2026-07-24T06:00:00+00:00",
            title="交接测试",
        )
        store.create_coding_handoff(
            "hf_test",
            "session-2",
            {"title": "中文交接", "documents_ready": True},
            "2026-07-24T06:01:00+00:00",
            "2026-07-24T07:00:00+00:00",
        )

        handoff = store.get_coding_handoff("hf_test")
        self.assertEqual("中文交接", handoff["payload"]["title"])
        self.assertEqual("", handoff["consumed_at"])

        store.mark_coding_handoff_consumed(
            "hf_test",
            "2026-07-24T06:05:00+00:00",
        )
        self.assertEqual(
            "2026-07-24T06:05:00+00:00",
            store.get_coding_handoff("hf_test")["consumed_at"],
        )

        store.delete_expired_coding_handoffs("2026-07-24T08:00:00+00:00")
        self.assertIsNone(store.get_coding_handoff("hf_test"))


if __name__ == "__main__":
    unittest.main()
