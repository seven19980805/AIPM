from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from app import _register_session_store_shutdown


class AppLifecycleTest(unittest.TestCase):
    def test_postgres_pool_is_registered_for_process_shutdown(self) -> None:
        store = Mock()

        with patch("app.atexit.register") as register:
            _register_session_store_shutdown(store)

        register.assert_called_once_with(store.close)


if __name__ == "__main__":
    unittest.main()
