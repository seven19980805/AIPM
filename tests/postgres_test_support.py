from __future__ import annotations

import os
import uuid
from pathlib import Path
from unittest import TestCase

from app.services.session_store import PostgreSQLSessionStore


TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://aipm:aipm_local_dev@127.0.0.1:5432/aipm",
)


def create_postgres_test_store(
    test_case: TestCase,
    storage_dir: str | Path,
) -> PostgreSQLSessionStore:
    store = PostgreSQLSessionStore(
        TEST_DATABASE_URL,
        storage_dir=storage_dir,
        schema=f"test_{uuid.uuid4().hex}",
    )
    test_case.addCleanup(store.close, drop_schema=True)
    return store
