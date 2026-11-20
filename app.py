"""Minimal Flask server for the Netskope Client Local Log Analyzer.

The analyzer is a self-contained HTML app (all logic runs in the browser),
so this server only serves static files:
  /                      -> index.html (latest build)
  /releases/             -> list of versioned builds
  /releases/<file>.html  -> a specific versioned build
  /healthz               -> health check
"""
import os
from pathlib import Path

from flask import Flask, abort, send_from_directory

BASE_DIR = Path(__file__).resolve().parent
RELEASES_DIR = BASE_DIR / "releases"

app = Flask(__name__, static_folder=None)


@app.after_request
def security_headers(resp):
    resp.headers.setdefault("X-Content-Type-Options", "nosniff")
    resp.headers.setdefault("Referrer-Policy", "no-referrer")
    return resp


@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/releases/")
def list_releases():
    if not RELEASES_DIR.is_dir():
        abort(404)
    files = sorted(p.name for p in RELEASES_DIR.glob("*.html"))
    items = "".join(f'<li><a href="/releases/{f}">{f}</a></li>' for f in files)
    return f"<!doctype html><title>Releases</title><h1>Releases</h1><ul>{items}</ul>"


@app.route("/releases/<path:filename>")
def release(filename):
    if not filename.endswith(".html"):
        abort(404)
    return send_from_directory(RELEASES_DIR, filename)


@app.route("/healthz")
def healthz():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5502")))
