"""
CodeAlpha Backend Internship - Task 1: Simple URL Shortener
Stack: Flask (Python) + SQLite
"""
import os
import re
import secrets
import sqlite3
import string
from urllib.parse import urlparse

from flask import Flask, g, jsonify, redirect, render_template, request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "urls.db")
ALPHABET = string.ascii_letters + string.digits
CODE_LENGTH = 6
RESERVED = {"api", "static", "shorten", "links"}
CUSTOM_RE = re.compile(r"^[A-Za-z0-9_-]{3,20}$")

app = Flask(__name__)


# ---------- Database helpers ----------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    with sqlite3.connect(DATABASE) as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                short_code TEXT NOT NULL UNIQUE,
                original_url TEXT NOT NULL,
                clicks INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


# ---------- Logic helpers ----------
def normalize_url(raw):
    """Return a valid http/https URL or None."""
    raw = (raw or "").strip()
    if not raw:
        return None
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", raw):
        raw = "https://" + raw
    parsed = urlparse(raw)
    if parsed.scheme not in ("http", "https") or not parsed.netloc or "." not in parsed.netloc:
        return None
    return raw


def generate_code(db):
    while True:
        code = "".join(secrets.choice(ALPHABET) for _ in range(CODE_LENGTH))
        exists = db.execute("SELECT 1 FROM urls WHERE short_code = ?", (code,)).fetchone()
        if not exists and code not in RESERVED:
            return code


def row_to_dict(row):
    return {
        "short_code": row["short_code"],
        "short_url": request.host_url + row["short_code"],
        "original_url": row["original_url"],
        "clicks": row["clicks"],
        "created_at": row["created_at"],
    }


# ---------- Routes ----------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/shorten", methods=["POST"])
def shorten():
    data = request.get_json(silent=True) or {}
    url = normalize_url(data.get("url"))
    if not url:
        return jsonify(error="Enter a valid link, for example https://example.com/page"), 400

    db = get_db()
    custom = (data.get("custom_code") or "").strip()

    if custom:
        if not CUSTOM_RE.match(custom):
            return jsonify(error="Custom code must be 3-20 characters: letters, numbers, - or _"), 400
        if custom.lower() in RESERVED:
            return jsonify(error="That code is reserved. Try another one."), 400
        if db.execute("SELECT 1 FROM urls WHERE short_code = ?", (custom,)).fetchone():
            return jsonify(error="That code is already taken. Try another one."), 409
        code = custom
    else:
        # Same long URL -> reuse its auto-generated short code
        existing = db.execute(
            "SELECT * FROM urls WHERE original_url = ? ORDER BY id LIMIT 1", (url,)
        ).fetchone()
        if existing:
            return jsonify(row_to_dict(existing)), 200
        code = generate_code(db)

    db.execute("INSERT INTO urls (short_code, original_url) VALUES (?, ?)", (code, url))
    db.commit()
    row = db.execute("SELECT * FROM urls WHERE short_code = ?", (code,)).fetchone()
    return jsonify(row_to_dict(row)), 201


@app.route("/api/links")
def list_links():
    rows = get_db().execute("SELECT * FROM urls ORDER BY id DESC LIMIT 10").fetchall()
    return jsonify([row_to_dict(r) for r in rows])


@app.route("/api/links/<code>")
def link_info(code):
    row = get_db().execute("SELECT * FROM urls WHERE short_code = ?", (code,)).fetchone()
    if row is None:
        return jsonify(error="Short link not found"), 404
    return jsonify(row_to_dict(row))


@app.route("/<code>")
def follow(code):
    db = get_db()
    row = db.execute("SELECT * FROM urls WHERE short_code = ?", (code,)).fetchone()
    if row is None:
        return render_template("index.html", not_found=code), 404
    db.execute("UPDATE urls SET clicks = clicks + 1 WHERE id = ?", (row["id"],))
    db.commit()
    return redirect(row["original_url"], code=302)


init_db()

if __name__ == "__main__":
    app.run(debug=True)
