from __future__ import annotations

import json
import os
import sqlite3
import tempfile
import unittest
import uuid
from pathlib import Path

from app.services.session_store import PostgreSQLSessionStore
from app.services.sqlite_migration import migrate_sqlite_to_postgres


TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://aipm:aipm_local_dev@127.0.0.1:5432/aipm",
)


class SQLiteToPostgreSQLMigrationTest(unittest.TestCase):
    def test_migrates_all_rows_unicode_json_and_ids_idempotently(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            sqlite_path = Path(tmpdir) / "legacy.sqlite3"
            self._create_legacy_database(sqlite_path)
            schema = f"test_migration_{uuid.uuid4().hex}"
            store = PostgreSQLSessionStore(
                TEST_DATABASE_URL,
                storage_dir=Path(tmpdir),
                schema=schema,
            )
            self.addCleanup(store.close, drop_schema=True)

            first_report = migrate_sqlite_to_postgres(sqlite_path, store)
            second_report = migrate_sqlite_to_postgres(sqlite_path, store)

            self.assertEqual(
                {
                    "sessions": 1,
                    "messages": 2,
                    "coding_handoffs": 1,
                    "skipped_orphan_messages": 1,
                },
                first_report,
            )
            self.assertEqual(first_report, second_report)

            session = store.get_session("session-中文")
            self.assertEqual("中文迁移测试", session["title"])
            self.assertEqual([41, 42], [item["message_id"] for item in session["messages"]])
            self.assertEqual("需要减少生产停线。", session["messages"][0]["content"])
            self.assertEqual(
                "减少停线",
                session["structured_requirement_cache"]["zh"]["model"]["objective"],
            )
            handoff = store.get_coding_handoff("handoff-中文")
            self.assertEqual("开发交接", handoff["payload"]["title"])

            next_message_id = store.append_message(
                "session-中文",
                "assistant",
                "迁移后新增",
                "2026-07-24T09:05:00+00:00",
            )
            self.assertEqual(43, next_message_id)

    @staticmethod
    def _create_legacy_database(sqlite_path: Path) -> None:
        connection = sqlite3.connect(sqlite_path)
        try:
            connection.executescript(
                """
                CREATE TABLE sessions (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    prompt_template TEXT NOT NULL,
                    applied_template_id TEXT NOT NULL,
                    applied_template_name TEXT NOT NULL,
                    start_function TEXT NOT NULL,
                    structured_requirement_cache TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    display_content TEXT NOT NULL,
                    thinking TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    download_filename TEXT NOT NULL,
                    storage_path TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE coding_handoffs (
                    token TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    consumed_at TEXT NOT NULL
                );
                """
            )
            connection.execute(
                """
                INSERT INTO sessions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "session-中文",
                    "中文迁移测试",
                    "personal_project",
                    "template-1",
                    "中文模板",
                    "from_template",
                    json.dumps(
                        {
                            "zh": {
                                "message_count": 2,
                                "model": {"objective": "减少停线"},
                            }
                        },
                        ensure_ascii=False,
                    ),
                    "2026-07-24T09:00:00+00:00",
                    "2026-07-24T09:02:00+00:00",
                ),
            )
            connection.executemany(
                """
                INSERT INTO messages VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        41,
                        "session-中文",
                        "user",
                        "需要减少生产停线。",
                        "",
                        "",
                        "chat",
                        "",
                        "",
                        "2026-07-24T09:01:00+00:00",
                    ),
                    (
                        42,
                        "session-中文",
                        "assistant",
                        "已记录目标。",
                        "已记录目标。",
                        "",
                        "chat",
                        "",
                        "",
                        "2026-07-24T09:02:00+00:00",
                    ),
                    (
                        99,
                        "deleted-session",
                        "user",
                        "不可达的孤儿消息",
                        "",
                        "",
                        "chat",
                        "",
                        "",
                        "2026-07-24T09:04:00+00:00",
                    ),
                ],
            )
            connection.execute(
                """
                INSERT INTO coding_handoffs VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    "handoff-中文",
                    "session-中文",
                    json.dumps({"title": "开发交接"}, ensure_ascii=False),
                    "2026-07-24T09:03:00+00:00",
                    "2026-07-24T10:03:00+00:00",
                    "",
                ),
            )
            connection.commit()
        finally:
            connection.close()
