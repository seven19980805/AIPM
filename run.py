import logging
import os
from pathlib import Path

from app import create_app


def load_dotenv() -> None:
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()

        if value and ((value[0] == value[-1]) and value[0] in {"'", '"'}):
            value = value[1:-1]

        os.environ.setdefault(key, value)


load_dotenv()
app = create_app()
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "False").lower() in {"1", "true", "yes", "on"}

    if debug:
        # Flask's built-in server is dev-only; keep it behind an explicit DEBUG=True opt-in.
        logger.warning("Starting Flask development server (DEBUG=True). Do not use this in production.")
        app.run(debug=True, host=host, port=port)
    else:
        from waitress import serve

        threads = int(os.getenv("WAITRESS_THREADS", "8"))
        logger.info("Starting waitress on %s:%s with %d threads", host, port, threads)
        serve(app, host=host, port=port, threads=threads)
