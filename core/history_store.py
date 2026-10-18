"""Local storage for NyayaAI: uploaded PDFs, their summaries and chat history.

Everything stays on this computer, inside the ./data folder:
    data/nyayaai.db   SQLite database (documents, summaries, messages)
    data/pdfs/        copies of the uploaded PDFs, named by their SHA-256 hash

Each PDF is identified by the SHA-256 hash of its bytes, so uploading the
same file again brings back its summary and its whole chat history.
"""

import json
import re
import sqlite3
import time
from contextlib import closing
from pathlib import Path

DATA_DIR = Path("data")
PDF_DIR = DATA_DIR / "pdfs"
DB_PATH = DATA_DIR / "nyayaai.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    id           TEXT PRIMARY KEY,
    name         TEXT NOT NULL,
    created_at   REAL NOT NULL,
    updated_at   REAL NOT NULL,
    summary_json TEXT
);

CREATE TABLE IF NOT EXISTS messages (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_id     TEXT NOT NULL,
    role       TEXT NOT NULL,
    payload    TEXT NOT NULL,
    created_at REAL NOT NULL,
    FOREIGN KEY (doc_id) REFERENCES documents(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_messages_doc ON messages(doc_id, id);
"""


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _pdf_path(doc_id: str) -> Path:
    # doc_id is always a SHA-256 hex string; refuse anything else so it can
    # never be used to reach files outside the data folder.
    if not re.fullmatch(r"[0-9a-f]{64}", doc_id):
        raise ValueError("Invalid document id.")
    return PDF_DIR / f"{doc_id}.pdf"


def init_db() -> None:
    PDF_DIR.mkdir(parents=True, exist_ok=True)

    with closing(_connect()) as conn, conn:
        conn.executescript(SCHEMA)


# ---------------------------------------------------------------- documents
def save_document(doc_id: str, name: str, pdf_bytes: bytes) -> None:
    """Store the PDF and register it. Does nothing if it already exists."""
    path = _pdf_path(doc_id)

    if not path.exists():
        path.write_bytes(pdf_bytes)

    now = time.time()

    with closing(_connect()) as conn, conn:
        conn.execute(
            "INSERT OR IGNORE INTO documents "
            "(id, name, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (doc_id, name[:200], now, now),
        )


def touch_document(doc_id: str) -> None:
    """Move a document to the top of the history list."""
    with closing(_connect()) as conn, conn:
        conn.execute(
            "UPDATE documents SET updated_at = ? WHERE id = ?",
            (time.time(), doc_id),
        )


def get_document(doc_id: str) -> dict | None:
    with closing(_connect()) as conn:
        row = conn.execute(
            "SELECT * FROM documents WHERE id = ?", (doc_id,)
        ).fetchone()

    if row is None:
        return None

    summary = None
    if row["summary_json"]:
        try:
            summary = json.loads(row["summary_json"])
        except json.JSONDecodeError:
            summary = None

    return {
        "id": row["id"],
        "name": row["name"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "summary": summary,
    }


def list_documents() -> list[dict]:
    """All documents, most recently used first."""
    with closing(_connect()) as conn:
        rows = conn.execute(
            "SELECT id, name, created_at, updated_at "
            "FROM documents ORDER BY updated_at DESC"
        ).fetchall()

    return [dict(row) for row in rows]


def get_pdf_bytes(doc_id: str) -> bytes | None:
    path = _pdf_path(doc_id)
    return path.read_bytes() if path.exists() else None


def save_summary(doc_id: str, summary: dict) -> None:
    with closing(_connect()) as conn, conn:
        conn.execute(
            "UPDATE documents SET summary_json = ? WHERE id = ?",
            (json.dumps(summary, default=str), doc_id),
        )


def delete_document(doc_id: str) -> None:
    """Delete a PDF, its summary and its chat history."""
    with closing(_connect()) as conn, conn:
        conn.execute("DELETE FROM messages WHERE doc_id = ?", (doc_id,))
        conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))

    _pdf_path(doc_id).unlink(missing_ok=True)


def delete_all() -> None:
    """Delete every stored PDF, summary and chat."""
    with closing(_connect()) as conn, conn:
        conn.execute("DELETE FROM messages")
        conn.execute("DELETE FROM documents")

    for pdf in PDF_DIR.glob("*.pdf"):
        pdf.unlink(missing_ok=True)


# ----------------------------------------------------------------- messages
def add_message(doc_id: str, role: str, payload) -> None:
    """Save one chat message.

    role "user": payload is the question text (str).
    role "assistant": payload is the result dict from the workflow.
    """
    now = time.time()

    with closing(_connect()) as conn, conn:
        conn.execute(
            "INSERT INTO messages (doc_id, role, payload, created_at) "
            "VALUES (?, ?, ?, ?)",
            (doc_id, role, json.dumps(payload, default=str), now),
        )
        conn.execute(
            "UPDATE documents SET updated_at = ? WHERE id = ?",
            (now, doc_id),
        )


def load_messages(doc_id: str) -> list[dict]:
    """Chat history for one PDF, oldest first.

    Returns dicts shaped like {"role": "user", "content": "..."} or
    {"role": "assistant", "data": {...}}.
    """
    with closing(_connect()) as conn:
        rows = conn.execute(
            "SELECT role, payload FROM messages "
            "WHERE doc_id = ? ORDER BY id",
            (doc_id,),
        ).fetchall()

    messages = []

    for row in rows:
        try:
            payload = json.loads(row["payload"])
        except json.JSONDecodeError:
            continue

        if row["role"] == "user":
            messages.append({"role": "user", "content": payload})
        else:
            messages.append({"role": "assistant", "data": payload})

    return messages