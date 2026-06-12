import os
from pathlib import Path
from app import create_app

# Load environment variables from .env file first
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

# Load environment variables before creating app
load_dotenv()
app = create_app()


if __name__ == "__main__":
    # Debug: print the actual values
    print(f"HOST from env: {os.getenv('HOST')}")
    print(f"PORT from env: {os.getenv('PORT')}")
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "True").lower() in {"1", "true", "yes", "on"}
    
    print(f"Using host: {host}, port: {port}")
    app.run(debug=debug, host=host, port=port)
