#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.services.session_store import PostgreSQLSessionStore
from app.services.sqlite_migration import migrate_sqlite_to_postgres


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Copy the legacy AI PM Assistant SQLite data into PostgreSQL.",
    )
    parser.add_argument("sqlite_path", type=Path)
    parser.add_argument(
        "--database-url",
        default=os.getenv("DATABASE_URL", ""),
        help="PostgreSQL connection URL (or set DATABASE_URL).",
    )
    parser.add_argument(
        "--storage-dir",
        type=Path,
        default=PROJECT_ROOT / "data",
    )
    parser.add_argument("--schema", default="public")
    args = parser.parse_args()
    if not args.database_url:
        parser.error("--database-url or DATABASE_URL is required")

    store = PostgreSQLSessionStore(
        args.database_url,
        storage_dir=args.storage_dir,
        schema=args.schema,
    )
    try:
        report = migrate_sqlite_to_postgres(args.sqlite_path, store)
        with store._connect() as connection:
            target_counts = {
                table: int(
                    connection.execute(f'SELECT COUNT(*) AS count FROM "{table}"')
                    .fetchone()["count"]
                )
                for table in ("sessions", "messages", "coding_handoffs")
            }
        expected_counts = {
            table: report[table]
            for table in ("sessions", "messages", "coding_handoffs")
        }
        if target_counts != expected_counts:
            raise RuntimeError(
                "Migration verification failed: "
                f"expected={expected_counts}, target={target_counts}"
            )
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
        return 0
    finally:
        store.close()


if __name__ == "__main__":
    raise SystemExit(main())
