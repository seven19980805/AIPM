from __future__ import annotations

import tempfile
import unittest
import uuid

from psycopg_pool import PoolClosed

from app.services.session_store import PostgreSQLSessionStore
from tests.postgres_test_support import TEST_DATABASE_URL


class PostgreSQLSessionStoreResourceTests(unittest.TestCase):
    def test_pool_rejects_operations_after_explicit_close(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            store = PostgreSQLSessionStore(
                TEST_DATABASE_URL,
                storage_dir=tmpdir,
                schema=f"test_close_{uuid.uuid4().hex}",
            )
            store.close(drop_schema=True)

            with self.assertRaises(PoolClosed):
                store.list_sessions()


if __name__ == "__main__":
    unittest.main()
