from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from psycopg.types.json import Jsonb

from .session_store import PostgreSQLSessionStore


def migrate_sqlite_to_postgres(
    sqlite_path: str | Path,
    store: PostgreSQLSessionStore,
) -> dict[str, int]:
    """Copy the legacy SQLite data into PostgreSQL without deleting the source."""
    source_path = Path(sqlite_path)
    if not source_path.is_file():
        raise FileNotFoundError(f"SQLite source database not found: {source_path}")

    source = sqlite3.connect(source_path)
    source.row_factory = sqlite3.Row
    try:
        sessions = _read_table(source, "sessions")
        messages = _read_table(source, "messages")
        handoffs = _read_table(source, "coding_handoffs")
    finally:
        source.close()

    session_ids = {str(row["id"]) for row in sessions}
    valid_messages = [
        row for row in messages if str(row["session_id"]) in session_ids
    ]
    valid_handoffs = [
        row for row in handoffs if str(row["session_id"]) in session_ids
    ]

    with store._connect() as target:
        for row in sessions:
            target.execute(
                """
                INSERT INTO sessions (
                    id,
                    title,
                    prompt_template,
                    applied_template_id,
                    applied_template_name,
                    start_function,
                    structured_requirement_cache,
                    created_at,
                    updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    prompt_template = EXCLUDED.prompt_template,
                    applied_template_id = EXCLUDED.applied_template_id,
                    applied_template_name = EXCLUDED.applied_template_name,
                    start_function = EXCLUDED.start_function,
                    structured_requirement_cache = EXCLUDED.structured_requirement_cache,
                    created_at = EXCLUDED.created_at,
                    updated_at = EXCLUDED.updated_at
                """,
                (
                    row["id"],
                    _value(row, "title", ""),
                    _value(row, "prompt_template", "personal_project"),
                    _value(row, "applied_template_id", ""),
                    _value(row, "applied_template_name", ""),
                    _value(row, "start_function", "from_scratch"),
                    Jsonb(_parse_json_dict(_value(row, "structured_requirement_cache", "{}"))),
                    row["created_at"],
                    row["updated_at"],
                ),
            )

        for row in valid_messages:
            target.execute(
                """
                INSERT INTO messages (
                    id,
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
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    session_id = EXCLUDED.session_id,
                    role = EXCLUDED.role,
                    content = EXCLUDED.content,
                    display_content = EXCLUDED.display_content,
                    thinking = EXCLUDED.thinking,
                    kind = EXCLUDED.kind,
                    download_filename = EXCLUDED.download_filename,
                    storage_path = EXCLUDED.storage_path,
                    created_at = EXCLUDED.created_at
                """,
                (
                    row["id"],
                    row["session_id"],
                    row["role"],
                    row["content"],
                    _value(row, "display_content", ""),
                    _value(row, "thinking", ""),
                    _value(row, "kind", "chat"),
                    _value(row, "download_filename", ""),
                    _value(row, "storage_path", ""),
                    row["created_at"],
                ),
            )

        for row in valid_handoffs:
            target.execute(
                """
                INSERT INTO coding_handoffs (
                    token,
                    session_id,
                    payload_json,
                    created_at,
                    expires_at,
                    consumed_at
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (token) DO UPDATE SET
                    session_id = EXCLUDED.session_id,
                    payload_json = EXCLUDED.payload_json,
                    created_at = EXCLUDED.created_at,
                    expires_at = EXCLUDED.expires_at,
                    consumed_at = EXCLUDED.consumed_at
                """,
                (
                    row["token"],
                    row["session_id"],
                    Jsonb(_parse_json_dict(row["payload_json"])),
                    row["created_at"],
                    row["expires_at"],
                    _value(row, "consumed_at", ""),
                ),
            )

        target.execute(
            """
            SELECT setval(
                pg_get_serial_sequence('messages', 'id'),
                COALESCE((SELECT MAX(id) FROM messages), 1),
                EXISTS(SELECT 1 FROM messages)
            )
            """
        )

    report = {
        "sessions": len(sessions),
        "messages": len(valid_messages),
        "coding_handoffs": len(valid_handoffs),
    }
    if len(valid_messages) != len(messages):
        report["skipped_orphan_messages"] = len(messages) - len(valid_messages)
    if len(valid_handoffs) != len(handoffs):
        report["skipped_orphan_coding_handoffs"] = len(handoffs) - len(valid_handoffs)
    return report


def _read_table(connection: sqlite3.Connection, table_name: str) -> list[sqlite3.Row]:
    exists = connection.execute(
        """
        SELECT 1
        FROM sqlite_master
        WHERE type = 'table' AND name = ?
        """,
        (table_name,),
    ).fetchone()
    if exists is None:
        return []
    return connection.execute(f'SELECT * FROM "{table_name}"').fetchall()


def _value(row: sqlite3.Row, key: str, default: Any) -> Any:
    return row[key] if key in row.keys() and row[key] is not None else default


def _parse_json_dict(raw_value: Any) -> dict[str, Any]:
    if isinstance(raw_value, dict):
        return raw_value
    try:
        parsed = json.loads(str(raw_value))
    except (TypeError, ValueError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}
