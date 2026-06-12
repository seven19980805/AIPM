from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path
from typing import Any


class SQLiteSessionStore:
    DEFAULT_PROMPT_TEMPLATE = "personal_project"
    DEFAULT_APPLIED_TEMPLATE_ID = ""
    DEFAULT_APPLIED_TEMPLATE_NAME = ""
    SESSION_TITLE_MAX_CHARS = 10
    SESSION_TITLE_MAX_ENGLISH_WORDS = 5
    SESSION_TITLE_ELLIPSIS = "..."
    CJK_TEXT_RE = re.compile(r"[\u3400-\u9fff]")
    LATIN_TEXT_RE = re.compile(r"[A-Za-z]")

    def __init__(self, db_path: str) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL DEFAULT '',
                    prompt_template TEXT NOT NULL DEFAULT 'personal_project',
                    applied_template_id TEXT NOT NULL DEFAULT '',
                    applied_template_name TEXT NOT NULL DEFAULT '',
                    structured_requirement_cache TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    display_content TEXT NOT NULL DEFAULT '',
                    thinking TEXT NOT NULL DEFAULT '',
                    kind TEXT NOT NULL DEFAULT 'chat',
                    download_filename TEXT NOT NULL DEFAULT '',
                    storage_path TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS coding_handoffs (
                    token TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    consumed_at TEXT NOT NULL DEFAULT '',
                    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_sessions_updated_at
                ON sessions(updated_at DESC, created_at DESC);

                CREATE INDEX IF NOT EXISTS idx_messages_session_id
                ON messages(session_id, id);

                CREATE INDEX IF NOT EXISTS idx_coding_handoffs_expires_at
                ON coding_handoffs(expires_at);
                """
            )
            self._ensure_session_columns(conn)
            self._ensure_message_columns(conn)

    @classmethod
    def format_session_title(cls, title: str, language: str | None = None) -> str:
        normalized_title = " ".join((title or "").split())
        if cls._should_limit_title_by_english_words(normalized_title, language):
            words = normalized_title.split()
            if len(words) <= cls.SESSION_TITLE_MAX_ENGLISH_WORDS:
                return normalized_title
            return f"{' '.join(words[:cls.SESSION_TITLE_MAX_ENGLISH_WORDS]).rstrip()}{cls.SESSION_TITLE_ELLIPSIS}"

        if len(normalized_title) <= cls.SESSION_TITLE_MAX_CHARS:
            return normalized_title
        return f"{normalized_title[:cls.SESSION_TITLE_MAX_CHARS].rstrip()}{cls.SESSION_TITLE_ELLIPSIS}"

    @classmethod
    def _should_limit_title_by_english_words(cls, title: str, language: str | None = None) -> bool:
        normalized_language = (language or "").lower()
        if normalized_language.startswith("en"):
            return True
        return bool(cls.LATIN_TEXT_RE.search(title)) and not cls.CJK_TEXT_RE.search(title)

    def _ensure_session_columns(self, conn: sqlite3.Connection) -> None:
        existing_columns = {
            str(row["name"])
            for row in conn.execute("PRAGMA table_info(sessions)").fetchall()
        }
        if "prompt_template" not in existing_columns:
            conn.execute(
                """
                ALTER TABLE sessions
                ADD COLUMN prompt_template TEXT NOT NULL DEFAULT 'personal_project'
                """
            )
        if "structured_requirement_cache" not in existing_columns:
            conn.execute(
                """
                ALTER TABLE sessions
                ADD COLUMN structured_requirement_cache TEXT NOT NULL DEFAULT '{}'
                """
            )
        if "applied_template_id" not in existing_columns:
            conn.execute(
                """
                ALTER TABLE sessions
                ADD COLUMN applied_template_id TEXT NOT NULL DEFAULT ''
                """
            )
        if "applied_template_name" not in existing_columns:
            conn.execute(
                """
                ALTER TABLE sessions
                ADD COLUMN applied_template_name TEXT NOT NULL DEFAULT ''
                """
            )

    def _ensure_message_columns(self, conn: sqlite3.Connection) -> None:
        existing_columns = {
            str(row["name"])
            for row in conn.execute("PRAGMA table_info(messages)").fetchall()
        }
        if "kind" not in existing_columns:
            conn.execute(
                """
                ALTER TABLE messages
                ADD COLUMN kind TEXT NOT NULL DEFAULT 'chat'
                """
            )
        if "display_content" not in existing_columns:
            conn.execute(
                """
                ALTER TABLE messages
                ADD COLUMN display_content TEXT NOT NULL DEFAULT ''
                """
            )
        if "download_filename" not in existing_columns:
            conn.execute(
                """
                ALTER TABLE messages
                ADD COLUMN download_filename TEXT NOT NULL DEFAULT ''
                """
            )
        if "storage_path" not in existing_columns:
            conn.execute(
                """
                ALTER TABLE messages
                ADD COLUMN storage_path TEXT NOT NULL DEFAULT ''
                """
            )

    def create_session(
        self,
        session_id: str,
        created_at: str,
        title: str = "",
        prompt_template: str = DEFAULT_PROMPT_TEMPLATE,
        applied_template_id: str = DEFAULT_APPLIED_TEMPLATE_ID,
        applied_template_name: str = DEFAULT_APPLIED_TEMPLATE_NAME,
    ) -> dict[str, Any]:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO sessions (
                    id,
                    title,
                    prompt_template,
                    applied_template_id,
                    applied_template_name,
                    structured_requirement_cache,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    self.format_session_title(title),
                    prompt_template,
                    applied_template_id,
                    applied_template_name,
                    "{}",
                    created_at,
                    created_at,
                ),
            )
            conn.commit()
        created = self.get_session(session_id)
        if created is None:
            raise RuntimeError("Failed to create session.")
        return created

    def list_sessions(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    s.id AS session_id,
                    s.title,
                    s.prompt_template,
                    s.applied_template_id,
                    s.applied_template_name,
                    s.created_at,
                    s.updated_at,
                    COUNT(m.id) AS message_count,
                    COALESCE(
                        (
                            SELECT COALESCE(NULLIF(display_content, ''), content)
                            FROM messages latest_assistant
                            WHERE latest_assistant.session_id = s.id
                              AND latest_assistant.role = 'assistant'
                              AND latest_assistant.kind = 'chat'
                            ORDER BY latest_assistant.id DESC
                            LIMIT 1
                        ),
                        (
                            SELECT COALESCE(NULLIF(display_content, ''), content)
                            FROM messages latest
                            WHERE latest.session_id = s.id
                              AND latest.kind = 'chat'
                            ORDER BY latest.id DESC
                            LIMIT 1
                        ),
                        ''
                    ) AS last_message_preview
                FROM sessions s
                LEFT JOIN messages m ON m.session_id = s.id
                GROUP BY
                    s.id,
                    s.title,
                    s.prompt_template,
                    s.applied_template_id,
                    s.applied_template_name,
                    s.created_at,
                    s.updated_at
                ORDER BY s.updated_at DESC, s.created_at DESC
                """
            ).fetchall()

        sessions: list[dict[str, Any]] = []
        for row in rows:
            preview = " ".join((row["last_message_preview"] or "").split())
            if len(preview) > 88:
                preview = f"{preview[:85].rstrip()}..."

            sessions.append(
                {
                    "session_id": row["session_id"],
                    "title": self.format_session_title(row["title"] or ""),
                    "prompt_template": row["prompt_template"] or self.DEFAULT_PROMPT_TEMPLATE,
                    "applied_template_id": row["applied_template_id"] or self.DEFAULT_APPLIED_TEMPLATE_ID,
                    "applied_template_name": row["applied_template_name"] or self.DEFAULT_APPLIED_TEMPLATE_NAME,
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "message_count": int(row["message_count"] or 0),
                    "last_message_preview": preview,
                }
            )
        return sessions

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            session_row = conn.execute(
                """
                SELECT
                    id,
                    title,
                    prompt_template,
                    applied_template_id,
                    applied_template_name,
                    structured_requirement_cache,
                    created_at,
                    updated_at
                FROM sessions
                WHERE id = ?
                """,
                (session_id,),
            ).fetchone()
            if session_row is None:
                return None

            message_rows = conn.execute(
                """
                SELECT
                    id,
                    role,
                    content,
                    display_content,
                    thinking,
                    kind,
                    download_filename,
                    storage_path,
                    created_at
                FROM messages
                WHERE session_id = ?
                ORDER BY id ASC
                """,
                (session_id,),
            ).fetchall()

        messages = []
        for row in message_rows:
            item: dict[str, Any] = {
                "message_id": int(row["id"]),
                "role": row["role"],
                "content": row["content"],
                "created_at": row["created_at"],
                "kind": row["kind"] or "chat",
            }
            if row["display_content"]:
                item["display_content"] = row["display_content"]
            if row["thinking"]:
                item["thinking"] = row["thinking"]
            if row["download_filename"]:
                item["download_filename"] = row["download_filename"]
            if row["storage_path"]:
                item["storage_path"] = row["storage_path"]
            messages.append(item)

        return {
            "session_id": session_row["id"],
            "title": self.format_session_title(session_row["title"] or ""),
            "prompt_template": session_row["prompt_template"] or self.DEFAULT_PROMPT_TEMPLATE,
            "applied_template_id": session_row["applied_template_id"] or self.DEFAULT_APPLIED_TEMPLATE_ID,
            "applied_template_name": session_row["applied_template_name"] or self.DEFAULT_APPLIED_TEMPLATE_NAME,
            "structured_requirement_cache": self._parse_structured_requirement_cache(
                session_row["structured_requirement_cache"]
            ),
            "created_at": session_row["created_at"],
            "updated_at": session_row["updated_at"],
            "messages": messages,
        }

    def append_message(
        self,
        session_id: str,
        role: str,
        content: str,
        created_at: str,
        thinking: str = "",
        kind: str = "chat",
        download_filename: str = "",
        storage_path: str = "",
        display_content: str = "",
    ) -> int:
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO messages (
                    session_id,
                    role,
                    content,
                    display_content,
                    thinking,
                    kind,
                    download_filename,
                    storage_path,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    role,
                    content,
                    display_content,
                    thinking,
                    kind,
                    download_filename,
                    storage_path,
                    created_at,
                ),
            )
            conn.execute(
                """
                UPDATE sessions
                SET updated_at = ?
                WHERE id = ?
                """,
                (created_at, session_id),
            )
            conn.commit()
        return int(cursor.lastrowid)

    def get_message_document(self, session_id: str, message_id: int) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT id, kind, download_filename, storage_path
                FROM messages
                WHERE session_id = ? AND id = ?
                """,
                (session_id, message_id),
            ).fetchone()

        if row is None:
            return None

        return {
            "message_id": int(row["id"]),
            "kind": row["kind"] or "chat",
            "download_filename": row["download_filename"] or "",
            "storage_path": row["storage_path"] or "",
        }

    def get_latest_document_message(self, session_id: str, kind: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT id, kind, download_filename, storage_path
                FROM messages
                WHERE session_id = ? AND kind = ?
                ORDER BY id DESC
                LIMIT 1
                """,
                (session_id, kind),
            ).fetchone()

        if row is None:
            return None

        return {
            "message_id": int(row["id"]),
            "kind": row["kind"] or "chat",
            "download_filename": row["download_filename"] or "",
            "storage_path": row["storage_path"] or "",
        }

    def update_session_title(self, session_id: str, title: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE sessions
                SET title = ?
                WHERE id = ?
                """,
                (self.format_session_title(title), session_id),
            )
            conn.commit()

    def update_session_prompt_template(self, session_id: str, prompt_template: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE sessions
                SET prompt_template = ?
                WHERE id = ?
                """,
                (prompt_template, session_id),
            )
            conn.commit()

    def update_session_applied_template(
        self,
        session_id: str,
        applied_template_id: str,
        applied_template_name: str,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE sessions
                SET applied_template_id = ?, applied_template_name = ?, structured_requirement_cache = '{}'
                WHERE id = ?
                """,
                (applied_template_id, applied_template_name, session_id),
            )
            conn.commit()

    def get_structured_requirement_cache_entry(
        self,
        session_id: str,
        language: str,
    ) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT structured_requirement_cache
                FROM sessions
                WHERE id = ?
                """,
                (session_id,),
            ).fetchone()

        if row is None:
            return None

        cache = self._parse_structured_requirement_cache(row["structured_requirement_cache"])
        entry = cache.get(str(language).strip().lower())
        return entry if isinstance(entry, dict) else None

    def save_structured_requirement_cache_entry(
        self,
        session_id: str,
        language: str,
        message_count: int,
        structured_requirement_model: dict[str, Any],
        updated_at: str,
    ) -> None:
        normalized_language = str(language).strip().lower()
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT structured_requirement_cache
                FROM sessions
                WHERE id = ?
                """,
                (session_id,),
            ).fetchone()
            if row is None:
                raise KeyError("Session not found.")

            cache = self._parse_structured_requirement_cache(row["structured_requirement_cache"])
            current_entry = cache.get(normalized_language)
            current_message_count = -1
            if isinstance(current_entry, dict):
                try:
                    current_message_count = int(current_entry.get("message_count", -1))
                except (TypeError, ValueError):
                    current_message_count = -1

            if current_message_count > message_count:
                return

            cache[normalized_language] = {
                "message_count": int(message_count),
                "updated_at": updated_at,
                "model": structured_requirement_model,
            }
            conn.execute(
                """
                UPDATE sessions
                SET structured_requirement_cache = ?
                WHERE id = ?
                """,
                (json.dumps(cache, ensure_ascii=False), session_id),
            )
            conn.commit()

    def delete_session(self, session_id: str) -> bool:
        with self._connect() as conn:
            cursor = conn.execute(
                """
                DELETE FROM sessions
                WHERE id = ?
                """,
                (session_id,),
            )
            conn.commit()
        return cursor.rowcount > 0

    def create_coding_handoff(
        self,
        token: str,
        session_id: str,
        payload: dict[str, Any],
        created_at: str,
        expires_at: str,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO coding_handoffs (
                    token,
                    session_id,
                    payload_json,
                    created_at,
                    expires_at,
                    consumed_at
                )
                VALUES (?, ?, ?, ?, ?, '')
                """,
                (
                    token,
                    session_id,
                    json.dumps(payload, ensure_ascii=False),
                    created_at,
                    expires_at,
                ),
            )
            conn.commit()

    def get_coding_handoff(self, token: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT token, session_id, payload_json, created_at, expires_at, consumed_at
                FROM coding_handoffs
                WHERE token = ?
                """,
                (token,),
            ).fetchone()

        if row is None:
            return None

        payload = self._parse_json_dict(row["payload_json"])
        return {
            "token": row["token"],
            "session_id": row["session_id"],
            "payload": payload,
            "created_at": row["created_at"],
            "expires_at": row["expires_at"],
            "consumed_at": row["consumed_at"] or "",
        }

    def mark_coding_handoff_consumed(self, token: str, consumed_at: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE coding_handoffs
                SET consumed_at = ?
                WHERE token = ?
                """,
                (consumed_at, token),
            )
            conn.commit()

    def delete_expired_coding_handoffs(self, now_iso: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                DELETE FROM coding_handoffs
                WHERE expires_at <= ?
                """,
                (now_iso,),
            )
            conn.commit()

    def _parse_structured_requirement_cache(self, raw_value: Any) -> dict[str, Any]:
        if not raw_value:
            return {}
        if isinstance(raw_value, dict):
            return raw_value
        try:
            parsed = json.loads(str(raw_value))
        except (TypeError, ValueError, json.JSONDecodeError):
            return {}
        return parsed if isinstance(parsed, dict) else {}

    def _parse_json_dict(self, raw_value: Any) -> dict[str, Any]:
        if isinstance(raw_value, dict):
            return raw_value
        try:
            parsed = json.loads(str(raw_value))
        except (TypeError, ValueError, json.JSONDecodeError):
            return {}
        return parsed if isinstance(parsed, dict) else {}
