from __future__ import annotations

import json
import re
from collections.abc import Iterator
from datetime import datetime, timezone
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from psycopg import sql
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from psycopg_pool import ConnectionPool


class PostgreSQLSessionStore:
    DEFAULT_PROMPT_TEMPLATE = "personal_project"
    DEFAULT_APPLIED_TEMPLATE_ID = ""
    DEFAULT_APPLIED_TEMPLATE_NAME = ""
    DEFAULT_START_FUNCTION = "from_scratch"
    DEFAULT_LANGUAGE = "en"
    SUPPORTED_LANGUAGES = frozenset({"en", "de", "zh", "ms"})
    SESSION_TITLE_MAX_CHARS = 10
    SESSION_TITLE_MAX_ENGLISH_WORDS = 5
    SESSION_TITLE_ELLIPSIS = "..."
    CJK_TEXT_RE = re.compile(r"[\u3400-\u9fff]")
    LATIN_TEXT_RE = re.compile(r"[A-Za-z]")
    SCHEMA_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

    def __init__(
        self,
        database_url: str,
        *,
        storage_dir: str | Path,
        schema: str = "public",
        pool_min_size: int = 1,
        pool_max_size: int = 10,
    ) -> None:
        if not str(database_url or "").strip():
            raise ValueError("DATABASE_URL is required.")
        if not self.SCHEMA_PATTERN.fullmatch(schema):
            raise ValueError("PostgreSQL schema name is invalid.")

        self.database_url = database_url
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.schema = schema
        self._pool = ConnectionPool(
            conninfo=database_url,
            min_size=pool_min_size,
            max_size=pool_max_size,
            kwargs={"row_factory": dict_row},
            open=True,
        )
        self._pool.wait(timeout=10)
        self._init_db()

    @contextmanager
    def _connect(self) -> Iterator[Any]:
        with self._pool.connection() as connection:
            connection.execute(
                sql.SQL("SET search_path TO {}, public").format(
                    sql.Identifier(self.schema)
                )
            )
            yield connection

    def _init_db(self) -> None:
        with self._pool.connection() as connection:
            connection.execute(
                sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(
                    sql.Identifier(self.schema)
                )
            )
            connection.execute(
                sql.SQL("SET search_path TO {}, public").format(
                    sql.Identifier(self.schema)
                )
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL DEFAULT '',
                    prompt_template TEXT NOT NULL DEFAULT 'personal_project',
                    applied_template_id TEXT NOT NULL DEFAULT '',
                    applied_template_name TEXT NOT NULL DEFAULT '',
                    start_function TEXT NOT NULL DEFAULT 'from_scratch',
                    language TEXT NOT NULL DEFAULT 'en',
                    structured_requirement_cache JSONB NOT NULL DEFAULT '{}'::jsonb,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                ALTER TABLE sessions
                ADD COLUMN IF NOT EXISTS language
                TEXT NOT NULL DEFAULT 'en'
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id BIGSERIAL PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    display_content TEXT NOT NULL DEFAULT '',
                    thinking TEXT NOT NULL DEFAULT '',
                    kind TEXT NOT NULL DEFAULT 'chat',
                    download_filename TEXT NOT NULL DEFAULT '',
                    storage_path TEXT NOT NULL DEFAULT '',
                    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
                )
                """
            )
            connection.execute(
                """
                ALTER TABLE messages
                ADD COLUMN IF NOT EXISTS metadata
                JSONB NOT NULL DEFAULT '{}'::jsonb
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS coding_handoffs (
                    token TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    payload_json JSONB NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    consumed_at TEXT NOT NULL DEFAULT '',
                    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    name TEXT PRIMARY KEY,
                    applied_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_sessions_updated_at
                ON sessions(updated_at DESC, created_at DESC)
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_messages_session_id
                ON messages(session_id, id)
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_coding_handoffs_expires_at
                ON coding_handoffs(expires_at)
                """
            )
        self.backfill_session_languages()

    def close(self, *, drop_schema: bool = False) -> None:
        if drop_schema and self.schema != "public":
            with self._pool.connection() as connection:
                connection.execute(
                    sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(
                        sql.Identifier(self.schema)
                    )
                )
        self._pool.close()

    @classmethod
    def format_session_title(cls, title: str, language: str | None = None) -> str:
        normalized_title = " ".join((title or "").split())
        if cls._should_limit_title_by_english_words(normalized_title, language):
            words = normalized_title.split()
            if len(words) <= cls.SESSION_TITLE_MAX_ENGLISH_WORDS:
                return normalized_title
            prefix = " ".join(words[: cls.SESSION_TITLE_MAX_ENGLISH_WORDS]).rstrip()
            return f"{prefix}{cls.SESSION_TITLE_ELLIPSIS}"

        if len(normalized_title) <= cls.SESSION_TITLE_MAX_CHARS:
            return normalized_title
        prefix = normalized_title[: cls.SESSION_TITLE_MAX_CHARS].rstrip()
        return f"{prefix}{cls.SESSION_TITLE_ELLIPSIS}"

    @classmethod
    def _should_limit_title_by_english_words(
        cls,
        title: str,
        language: str | None = None,
    ) -> bool:
        normalized_language = (language or "").lower()
        if normalized_language.startswith("en"):
            return True
        return bool(cls.LATIN_TEXT_RE.search(title)) and not cls.CJK_TEXT_RE.search(title)

    def create_session(
        self,
        session_id: str,
        created_at: str,
        title: str = "",
        prompt_template: str = DEFAULT_PROMPT_TEMPLATE,
        applied_template_id: str = DEFAULT_APPLIED_TEMPLATE_ID,
        applied_template_name: str = DEFAULT_APPLIED_TEMPLATE_NAME,
        start_function: str = DEFAULT_START_FUNCTION,
        language: str = DEFAULT_LANGUAGE,
    ) -> dict[str, Any]:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO sessions (
                    id,
                    title,
                    prompt_template,
                    applied_template_id,
                    applied_template_name,
                    start_function,
                    language,
                    structured_requirement_cache,
                    created_at,
                    updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    session_id,
                    self.format_session_title(title),
                    prompt_template,
                    applied_template_id,
                    applied_template_name,
                    start_function,
                    self._normalize_language(language),
                    Jsonb({}),
                    created_at,
                    created_at,
                ),
            )
        created = self.get_session(session_id)
        if created is None:
            raise RuntimeError("Failed to create session.")
        return created

    def list_sessions(self) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    s.id AS session_id,
                    s.title,
                    s.prompt_template,
                    s.applied_template_id,
                    s.applied_template_name,
                    s.start_function,
                    s.language,
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
                    s.start_function,
                    s.language,
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
                    "prompt_template": row["prompt_template"]
                    or self.DEFAULT_PROMPT_TEMPLATE,
                    "applied_template_id": row["applied_template_id"]
                    or self.DEFAULT_APPLIED_TEMPLATE_ID,
                    "applied_template_name": row["applied_template_name"]
                    or self.DEFAULT_APPLIED_TEMPLATE_NAME,
                    "start_function": row["start_function"]
                    or self.DEFAULT_START_FUNCTION,
                    "language": self._normalize_language(row["language"]),
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "message_count": int(row["message_count"] or 0),
                    "last_message_preview": preview,
                }
            )
        return sessions

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            session_row = connection.execute(
                """
                SELECT
                    id,
                    title,
                    prompt_template,
                    applied_template_id,
                    applied_template_name,
                    start_function,
                    language,
                    structured_requirement_cache,
                    created_at,
                    updated_at
                FROM sessions
                WHERE id = %s
                """,
                (session_id,),
            ).fetchone()
            if session_row is None:
                return None
            message_rows = connection.execute(
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
                    metadata,
                    created_at
                FROM messages
                WHERE session_id = %s
                ORDER BY id ASC
                """,
                (session_id,),
            ).fetchall()

        messages: list[dict[str, Any]] = []
        for row in message_rows:
            item: dict[str, Any] = {
                "message_id": int(row["id"]),
                "role": row["role"],
                "content": row["content"],
                "created_at": row["created_at"],
                "kind": row["kind"] or "chat",
                "metadata": self._parse_json_dict(row["metadata"]),
            }
            for key in (
                "display_content",
                "thinking",
                "download_filename",
                "storage_path",
            ):
                if row[key]:
                    item[key] = row[key]
            messages.append(item)

        return {
            "session_id": session_row["id"],
            "title": self.format_session_title(session_row["title"] or ""),
            "prompt_template": session_row["prompt_template"]
            or self.DEFAULT_PROMPT_TEMPLATE,
            "applied_template_id": session_row["applied_template_id"]
            or self.DEFAULT_APPLIED_TEMPLATE_ID,
            "applied_template_name": session_row["applied_template_name"]
            or self.DEFAULT_APPLIED_TEMPLATE_NAME,
            "start_function": session_row["start_function"]
            or self.DEFAULT_START_FUNCTION,
            "language": self._normalize_language(session_row["language"]),
            "structured_requirement_cache": self._parse_json_dict(
                session_row["structured_requirement_cache"]
            ),
            "created_at": session_row["created_at"],
            "updated_at": session_row["updated_at"],
            "messages": messages,
        }

    SESSION_LANGUAGE_BACKFILL = "session_language_backfill_v1"

    def backfill_session_languages(self, *, force: bool = False) -> int:
        """Recover the working language of sessions created before the column.

        ``ALTER TABLE ... ADD COLUMN language ... DEFAULT 'en'`` marks every
        historical row English. The structured-requirement cache already records
        which languages a session was actually worked in, so the dominant
        non-canonical cache key is the honest answer. Runs once, is recorded in
        ``schema_migrations``, and never overrides a language a user has since
        chosen. Read-modify-write only; no row is deleted and no cache touched.
        """

        with self._connect() as connection:
            if not force:
                applied = connection.execute(
                    "SELECT 1 FROM schema_migrations WHERE name = %s",
                    (self.SESSION_LANGUAGE_BACKFILL,),
                ).fetchone()
                if applied is not None:
                    return 0
            cursor = connection.execute(
                """
                UPDATE sessions AS s
                SET language = ranked.key
                FROM (
                    SELECT
                        id,
                        key,
                        ROW_NUMBER() OVER (
                            PARTITION BY id
                            ORDER BY message_count DESC, key
                        ) AS position
                    FROM (
                        SELECT
                            s.id AS id,
                            entry.key AS key,
                            COALESCE(
                                NULLIF(entry.value ->> 'message_count', '')::INT,
                                -1
                            ) AS message_count
                        FROM sessions AS s
                        CROSS JOIN LATERAL jsonb_each(
                            s.structured_requirement_cache
                        ) AS entry
                        WHERE jsonb_typeof(entry.value) = 'object'
                          AND entry.key = ANY(%s)
                          AND entry.value ->> 'message_count' ~ '^-?[0-9]+$'
                    ) AS scored
                ) AS ranked
                WHERE s.id = ranked.id
                  AND ranked.position = 1
                  AND s.language <> ranked.key
                """,
                (list(self.SUPPORTED_LANGUAGES),),
            )
            corrected = cursor.rowcount
            connection.execute(
                """
                INSERT INTO schema_migrations (name, applied_at)
                VALUES (%s, %s)
                ON CONFLICT (name) DO NOTHING
                """,
                (
                    self.SESSION_LANGUAGE_BACKFILL,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            return corrected

    def set_session_language(self, session_id: str, language: str) -> None:
        with self._connect() as connection:
            result = connection.execute(
                """
                UPDATE sessions
                SET language = %s
                WHERE id = %s
                """,
                (self._normalize_language(language), session_id),
            )
            if result.rowcount == 0:
                raise KeyError("Session not found.")

    @classmethod
    def _normalize_language(cls, language: object) -> str:
        normalized = str(language or "").strip().lower()
        if normalized in cls.SUPPORTED_LANGUAGES:
            return normalized
        return cls.DEFAULT_LANGUAGE

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
        metadata: dict[str, Any] | None = None,
    ) -> int:
        with self._connect() as connection:
            row = connection.execute(
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
                    metadata,
                    created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
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
                    Jsonb(metadata or {}),
                    created_at,
                ),
            ).fetchone()
            connection.execute(
                """
                UPDATE sessions
                SET updated_at = %s
                WHERE id = %s
                """,
                (created_at, session_id),
            )
        return int(row["id"])

    def get_message_document(
        self,
        session_id: str,
        message_id: int,
    ) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT id, kind, download_filename, storage_path
                FROM messages
                WHERE session_id = %s AND id = %s
                """,
                (session_id, message_id),
            ).fetchone()
        return self._document_from_row(row)

    def get_latest_document_message(
        self,
        session_id: str,
        kind: str,
    ) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT id, kind, download_filename, storage_path
                FROM messages
                WHERE session_id = %s AND kind = %s
                ORDER BY id DESC
                LIMIT 1
                """,
                (session_id, kind),
            ).fetchone()
        return self._document_from_row(row)

    @staticmethod
    def _document_from_row(row: Any) -> dict[str, Any] | None:
        if row is None:
            return None
        return {
            "message_id": int(row["id"]),
            "kind": row["kind"] or "chat",
            "download_filename": row["download_filename"] or "",
            "storage_path": row["storage_path"] or "",
        }

    def update_session_title(self, session_id: str, title: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "UPDATE sessions SET title = %s WHERE id = %s",
                (self.format_session_title(title), session_id),
            )

    def update_session_prompt_template(
        self,
        session_id: str,
        prompt_template: str,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                "UPDATE sessions SET prompt_template = %s WHERE id = %s",
                (prompt_template, session_id),
            )

    def update_session_applied_template(
        self,
        session_id: str,
        applied_template_id: str,
        applied_template_name: str,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE sessions
                SET
                    applied_template_id = %s,
                    applied_template_name = %s,
                    structured_requirement_cache = '{}'::jsonb
                WHERE id = %s
                """,
                (applied_template_id, applied_template_name, session_id),
            )

    def get_structured_requirement_cache_entry(
        self,
        session_id: str,
        language: str,
    ) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT structured_requirement_cache
                FROM sessions
                WHERE id = %s
                """,
                (session_id,),
            ).fetchone()
        if row is None:
            return None
        cache = self._parse_json_dict(row["structured_requirement_cache"])
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
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT structured_requirement_cache
                FROM sessions
                WHERE id = %s
                FOR UPDATE
                """,
                (session_id,),
            ).fetchone()
            if row is None:
                raise KeyError("Session not found.")

            cache = self._parse_json_dict(row["structured_requirement_cache"])
            current_entry = cache.get(normalized_language)
            current_message_count = -1
            if isinstance(current_entry, dict):
                try:
                    current_message_count = int(
                        current_entry.get("message_count", -1)
                    )
                except (TypeError, ValueError):
                    current_message_count = -1
            if current_message_count > message_count:
                return

            cache[normalized_language] = {
                "message_count": int(message_count),
                "updated_at": updated_at,
                "model": structured_requirement_model,
            }
            connection.execute(
                """
                UPDATE sessions
                SET structured_requirement_cache = %s
                WHERE id = %s
                """,
                (Jsonb(cache), session_id),
            )

    def delete_session(self, session_id: str) -> bool:
        with self._connect() as connection:
            cursor = connection.execute(
                "DELETE FROM sessions WHERE id = %s",
                (session_id,),
            )
        return cursor.rowcount > 0

    def create_coding_handoff(
        self,
        token: str,
        session_id: str,
        payload: dict[str, Any],
        created_at: str,
        expires_at: str,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO coding_handoffs (
                    token,
                    session_id,
                    payload_json,
                    created_at,
                    expires_at,
                    consumed_at
                )
                VALUES (%s, %s, %s, %s, %s, '')
                """,
                (token, session_id, Jsonb(payload), created_at, expires_at),
            )

    def get_coding_handoff(self, token: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    token,
                    session_id,
                    payload_json,
                    created_at,
                    expires_at,
                    consumed_at
                FROM coding_handoffs
                WHERE token = %s
                """,
                (token,),
            ).fetchone()
        if row is None:
            return None
        return {
            "token": row["token"],
            "session_id": row["session_id"],
            "payload": self._parse_json_dict(row["payload_json"]),
            "created_at": row["created_at"],
            "expires_at": row["expires_at"],
            "consumed_at": row["consumed_at"] or "",
        }

    def mark_coding_handoff_consumed(
        self,
        token: str,
        consumed_at: str,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE coding_handoffs
                SET consumed_at = %s
                WHERE token = %s
                """,
                (consumed_at, token),
            )

    def delete_expired_coding_handoffs(self, now_iso: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "DELETE FROM coding_handoffs WHERE expires_at <= %s",
                (now_iso,),
            )

    @staticmethod
    def _parse_json_dict(raw_value: Any) -> dict[str, Any]:
        if not raw_value:
            return {}
        if isinstance(raw_value, dict):
            return raw_value
        try:
            parsed = json.loads(str(raw_value))
        except (TypeError, ValueError, json.JSONDecodeError):
            return {}
        return parsed if isinstance(parsed, dict) else {}
