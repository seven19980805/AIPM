import os
from pathlib import Path

from flask import Blueprint, abort, render_template, send_from_directory

main = Blueprint("main", __name__)


def _frontend_dist_dir() -> Path:
    configured = os.getenv("FRONTEND_DIST_DIR", "").strip()
    if configured:
        return Path(configured)
    return Path(__file__).resolve().parents[1] / "frontend" / "dist"


@main.route("/")
def index():
    dist_dir = _frontend_dist_dir()
    if (dist_dir / "index.html").is_file():
        return send_from_directory(dist_dir, "index.html")
    return render_template("index.html")


@main.route("/<path:path>")
def frontend_asset_or_spa(path: str):
    dist_dir = _frontend_dist_dir()
    if not (dist_dir / "index.html").is_file():
        abort(404)

    requested_path = dist_dir / path
    if requested_path.is_file():
        return send_from_directory(dist_dir, path)

    return send_from_directory(dist_dir, "index.html")
