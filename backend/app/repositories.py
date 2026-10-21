import json
import sqlite3
from typing import Any


def row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    data = dict(row)
    if "enabled" in data:
        data["enabled"] = bool(data["enabled"])
    if "citations" in data:
        data["citations"] = json.loads(data["citations"])
    return data


class NotebookRepository:
    def __init__(self, db: sqlite3.Connection):
        self.db = db

    def create(self, title: str) -> dict[str, Any]:
        cursor = self.db.execute(
            "INSERT INTO notebooks (title) VALUES (?)",
            (title,),
        )
        self.db.commit()
        return self.get(cursor.lastrowid)

    def list_all(self) -> list[dict[str, Any]]:
        rows = self.db.execute(
            """
            SELECT id, title, created_at, updated_at
            FROM notebooks
            ORDER BY updated_at DESC, id DESC
            """
        ).fetchall()
        return [row_to_dict(row) for row in rows]

    def get(self, notebook_id: int) -> dict[str, Any] | None:
        row = self.db.execute(
            """
            SELECT id, title, created_at, updated_at
            FROM notebooks
            WHERE id = ?
            """,
            (notebook_id,),
        ).fetchone()
        return row_to_dict(row)

    def rename(self, notebook_id: int, title: str) -> dict[str, Any] | None:
        self.db.execute(
            """
            UPDATE notebooks
            SET title = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (title, notebook_id),
        )
        self.db.commit()
        return self.get(notebook_id)

    def delete(self, notebook_id: int) -> bool:
        cursor = self.db.execute("DELETE FROM notebooks WHERE id = ?", (notebook_id,))
        self.db.commit()
        return cursor.rowcount > 0


class SourceRepository:
    def __init__(self, db: sqlite3.Connection):
        self.db = db

    def create_pasted(
        self,
        notebook_id: int,
        title: str,
        content: str,
    ) -> dict[str, Any]:
        cursor = self.db.execute(
            """
            INSERT INTO sources (notebook_id, title, type, content, status, enabled)
            VALUES (?, ?, 'pasted_text', ?, 'ready', 1)
            """,
            (notebook_id, title, content),
        )
        self.db.commit()
        return self.get(cursor.lastrowid)

    def list_for_notebook(self, notebook_id: int) -> list[dict[str, Any]]:
        rows = self.db.execute(
            """
            SELECT id, notebook_id, title, type, status, enabled, error,
                   created_at, updated_at
            FROM sources
            WHERE notebook_id = ?
            ORDER BY created_at DESC, id DESC
            """,
            (notebook_id,),
        ).fetchall()
        return [row_to_dict(row) for row in rows]

    def list_enabled_for_notebook(self, notebook_id: int) -> list[dict[str, Any]]:
        rows = self.db.execute(
            """
            SELECT id, notebook_id, title, type, status, enabled, error,
                   created_at, updated_at
            FROM sources
            WHERE notebook_id = ? AND enabled = 1 AND status = 'ready'
            ORDER BY created_at DESC, id DESC
            """,
            (notebook_id,),
        ).fetchall()
        return [row_to_dict(row) for row in rows]

    def get(self, source_id: int) -> dict[str, Any] | None:
        row = self.db.execute(
            """
            SELECT id, notebook_id, title, type, status, enabled, error,
                   created_at, updated_at
            FROM sources
            WHERE id = ?
            """,
            (source_id,),
        ).fetchone()
        return row_to_dict(row)

    def update(
        self,
        source_id: int,
        title: str | None = None,
        enabled: bool | None = None,
    ) -> dict[str, Any] | None:
        assignments: list[str] = []
        values: list[Any] = []
        if title is not None:
            assignments.append("title = ?")
            values.append(title)
        if enabled is not None:
            assignments.append("enabled = ?")
            values.append(1 if enabled else 0)

        assignments.append("updated_at = CURRENT_TIMESTAMP")
        values.append(source_id)
        self.db.execute(
            f"UPDATE sources SET {', '.join(assignments)} WHERE id = ?",
            values,
        )
        self.db.commit()
        return self.get(source_id)

    def delete(self, source_id: int) -> bool:
        cursor = self.db.execute("DELETE FROM sources WHERE id = ?", (source_id,))
        self.db.commit()
        return cursor.rowcount > 0


class MessageRepository:
    def __init__(self, db: sqlite3.Connection):
        self.db = db

    def create(
        self,
        notebook_id: int,
        role: str,
        content: str,
        citations: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        cursor = self.db.execute(
            """
            INSERT INTO messages (notebook_id, role, content, citations)
            VALUES (?, ?, ?, ?)
            """,
            (notebook_id, role, content, json.dumps(citations or [])),
        )
        self.db.commit()
        return self.get(cursor.lastrowid)

    def get(self, message_id: int) -> dict[str, Any] | None:
        row = self.db.execute(
            """
            SELECT id, notebook_id, role, content, citations, created_at
            FROM messages
            WHERE id = ?
            """,
            (message_id,),
        ).fetchone()
        return row_to_dict(row)

    def list_for_notebook(self, notebook_id: int) -> list[dict[str, Any]]:
        rows = self.db.execute(
            """
            SELECT id, notebook_id, role, content, citations, created_at
            FROM messages
            WHERE notebook_id = ?
            ORDER BY id ASC
            """,
            (notebook_id,),
        ).fetchall()
        return [row_to_dict(row) for row in rows]
