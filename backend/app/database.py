import sqlite3
from collections.abc import AsyncIterator
from pathlib import Path
import os


DEFAULT_DB_PATH = Path(__file__).resolve().parents[1] / "data" / "app.db"


SCHEMA = """
CREATE TABLE IF NOT EXISTS notebooks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    notebook_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    type TEXT NOT NULL,
    content TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL,
    enabled INTEGER NOT NULL DEFAULT 1,
    error TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (notebook_id) REFERENCES notebooks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    notebook_id INTEGER NOT NULL,
    page INTEGER,
    text TEXT NOT NULL,
    embedding TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE CASCADE,
    FOREIGN KEY (notebook_id) REFERENCES notebooks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    notebook_id INTEGER NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    citations TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (notebook_id) REFERENCES notebooks(id) ON DELETE CASCADE
);
"""


def database_path() -> Path:
    return Path(os.environ.get("NOTEBOOKLM_DB_PATH", DEFAULT_DB_PATH))


def connect_db() -> sqlite3.Connection:
    path = database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


async def get_db() -> AsyncIterator[sqlite3.Connection]:
    connection = connect_db()
    try:
        yield connection
    finally:
        connection.close()


def init_db() -> None:
    with connect_db() as connection:
        connection.executescript(SCHEMA)
        from app.services import SourceService

        SourceService(connection).backfill_missing_chunks()
