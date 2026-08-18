import atexit
import logging
import os
from pathlib import Path


def _load_dotenv() -> None:
    env_path = Path(__file__).resolve().parent.parent / ".env"
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

        # Keep already-exported env vars as highest priority.
        os.environ.setdefault(key, value)


def _register_session_store_shutdown(session_store) -> None:
    atexit.register(session_store.close)


def create_app():
    from flask import Flask, request

    from .services.asr_client import ASRConfig, DoubaoASRClient
    from .services.llm_client import LLMConfig, MiniMaxChatClient
    from .services.requirement_collector import RequirementCollectorService
    from .services.session_store import PostgreSQLSessionStore

    _load_dotenv()
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
    app = Flask(__name__)

    # Server configuration
    app.config["HOST"] = os.getenv("HOST", "0.0.0.0")
    app.config["PORT"] = int(os.getenv("PORT", "8000"))

    # CORS configuration
    app.config["CORS_ORIGINS"] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://localhost:5173,http://localhost:9530",
        ).split(",")
        if origin.strip()
    ]
    app.config["CORS_ALLOW_METHODS"] = "GET, POST, DELETE, OPTIONS"
    app.config["DATABASE_URL"] = os.getenv("DATABASE_URL", "")
    app.config["DOCUMENT_STORAGE_PATH"] = os.getenv(
        "DOCUMENT_STORAGE_PATH",
        str(Path(__file__).resolve().parent.parent / "data"),
    )

    # LLM configuration
    app.config["LLM_PROVIDER"] = os.getenv("LLM_PROVIDER", "openai_compatible")
    app.config["LLM_BASE_URL"] = os.getenv("LLM_BASE_URL", "https://api.minimaxi.com/v1")
    app.config["LLM_API_KEY"] = os.getenv("LLM_API_KEY", "")
    app.config["LLM_MODEL"] = os.getenv("LLM_MODEL", "MiniMax-M2.7")
    app.config["LLM_TIMEOUT_SECONDS"] = int(os.getenv("LLM_TIMEOUT_SECONDS", "500"))
    app.config["LLM_PROXY_URL"] = os.getenv("LLM_PROXY_URL", "")
    app.config["LLM_MAX_RETRIES"] = int(os.getenv("LLM_MAX_RETRIES", "2"))
    app.config["LLM_DEBUG_STREAM"] = os.getenv("LLM_DEBUG_STREAM", "false").lower() in {"1", "true", "yes", "on"}
    app.config["LLM_GCP_PROJECT_ID"] = os.getenv("LLM_GCP_PROJECT_ID", "")
    app.config["LLM_GCP_LOCATION"] = os.getenv("LLM_GCP_LOCATION", "global")
    app.config["LLM_GCP_CREDENTIALS_PATH"] = os.getenv(
        "LLM_GCP_CREDENTIALS_PATH",
        os.getenv("GOOGLE_APPLICATION_CREDENTIALS", ""),
    )
    
    # ASR configuration
    app.config["ASR_APP_ID"] = os.getenv("ASR_APP_ID", "")
    app.config["ASR_ACCESS_TOKEN"] = os.getenv("ASR_ACCESS_TOKEN", "")
    app.config["ASR_SECRET_KEY"] = os.getenv("ASR_SECRET_KEY", "")
    app.config["ASR_BASE_URL"] = os.getenv("ASR_BASE_URL", "")

    session_store = PostgreSQLSessionStore(
        app.config["DATABASE_URL"],
        storage_dir=app.config["DOCUMENT_STORAGE_PATH"],
    )
    _register_session_store_shutdown(session_store)

    llm_config = LLMConfig(
        provider=app.config["LLM_PROVIDER"],
        base_url=app.config["LLM_BASE_URL"],
        api_key=app.config["LLM_API_KEY"],
        model=app.config["LLM_MODEL"],
        timeout_seconds=app.config["LLM_TIMEOUT_SECONDS"],
        proxy_url=app.config["LLM_PROXY_URL"],
        max_retries=app.config["LLM_MAX_RETRIES"],
        debug_stream=app.config["LLM_DEBUG_STREAM"],
        google_project_id=app.config["LLM_GCP_PROJECT_ID"],
        google_location=app.config["LLM_GCP_LOCATION"],
        google_credentials_path=app.config["LLM_GCP_CREDENTIALS_PATH"],
    )
    llm_config.validate_for_startup()
    llm_client = MiniMaxChatClient(llm_config)
    app.extensions["requirement_collector"] = RequirementCollectorService(llm_client, session_store)
    
    # Initialize ASR client
    asr_client = DoubaoASRClient(
        ASRConfig(
            app_id=app.config["ASR_APP_ID"],
            access_token=app.config["ASR_ACCESS_TOKEN"],
            secret_key=app.config["ASR_SECRET_KEY"],
            base_url=app.config["ASR_BASE_URL"]
        )
    )
    app.extensions["asr_client"] = asr_client

    def _allowed_cors_origin() -> str:
        """Return the Origin header iff it matches the configured allow-list."""
        origin = request.headers.get("Origin", "")
        allowed = app.config["CORS_ORIGINS"]
        return origin if origin and origin in allowed else ""

    # Handle OPTIONS requests explicitly
    @app.route("/api/<path:path>", methods=["OPTIONS"])
    def handle_options(path):
        response = app.make_response()
        origin = _allowed_cors_origin()
        if origin:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Vary"] = "Origin"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            response.headers["Access-Control-Allow-Methods"] = app.config["CORS_ALLOW_METHODS"]
            response.headers["Access-Control-Allow-Credentials"] = "true"
        return response

    @app.after_request
    def add_api_cors_headers(response):
        if request.path.startswith("/api/"):
            origin = _allowed_cors_origin()
            if origin:
                response.headers["Access-Control-Allow-Origin"] = origin
                response.headers["Vary"] = "Origin"
                response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
                response.headers["Access-Control-Allow-Methods"] = app.config["CORS_ALLOW_METHODS"]
                response.headers["Access-Control-Allow-Credentials"] = "true"
        return response

    from .api import api
    from .routes import main

    app.register_blueprint(main)
    app.register_blueprint(api)
    return app
