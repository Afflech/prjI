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

    def create_text_source(
        self,
        notebook_id: int,
        title: str,
        content: str,
        source_type: str,
        commit: bool = True,
    ) -> dict[str, Any]:
        cursor = self.db.execute(
            """
            INSERT INTO sources (notebook_id, title, type, content, status, enabled)
            VALUES (?, ?, ?, ?, 'ready', 1)
            """,
            (notebook_id, title, source_type, content),
        )
        if commit:
            self.db.commit()
        return self.get(cursor.lastrowid)

    def create_pasted(
        self,
        notebook_id: int,
        title: str,
        content: str,
        commit: bool = True,
    ) -> dict[str, Any]:
        return self.create_text_source(
            notebook_id=notebook_id,
            title=title,
            content=content,
            source_type="pasted_text",
            commit=commit,
        )

    def list_ready_without_chunks(self) -> list[dict[str, Any]]:
        rows = self.db.execute(
            """
            SELECT sources.id, sources.notebook_id, sources.title, sources.type,
                   sources.content, sources.status, sources.enabled, sources.error,
                   sources.created_at, sources.updated_at
            FROM sources
            LEFT JOIN chunks ON chunks.source_id = sources.id
            WHERE sources.status = 'ready'
              AND sources.content != ''
            GROUP BY sources.id
            HAVING COUNT(chunks.id) = 0
            ORDER BY sources.id ASC
            """
        ).fetchall()
        return [row_to_dict(row) for row in rows]

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


class ChunkRepository:
    def __init__(self, db: sqlite3.Connection):
        self.db = db

    def create_many(self, chunks: list[dict[str, Any]], commit: bool = True) -> None:
        if not chunks:
            return
        self.db.executemany(
            """
            INSERT INTO chunks (source_id, notebook_id, page, text, embedding)
            VALUES (:source_id, :notebook_id, :page, :text, :embedding)
            """,
            chunks,
        )
        if commit:
            self.db.commit()

    def get(self, chunk_id: int) -> dict[str, Any] | None:
        row = self.db.execute(
            """
            SELECT chunks.id, chunks.source_id, chunks.notebook_id, chunks.page,
                   chunks.text, chunks.embedding, chunks.created_at,
                   sources.title AS source_title
            FROM chunks
            JOIN sources ON sources.id = chunks.source_id
            WHERE chunks.id = ?
            """,
            (chunk_id,),
        ).fetchone()
        return row_to_dict(row)

    def list_searchable_for_notebook(self, notebook_id: int) -> list[dict[str, Any]]:
        rows = self.db.execute(
            """
            SELECT chunks.id, chunks.source_id, chunks.notebook_id, chunks.page,
                   chunks.text, chunks.embedding, chunks.created_at,
                   sources.title AS source_title
            FROM chunks
            JOIN sources ON sources.id = chunks.source_id
            WHERE chunks.notebook_id = ?
              AND sources.enabled = 1
              AND sources.status = 'ready'
            ORDER BY chunks.id ASC
            """,
            (notebook_id,),
        ).fetchall()
        return [row_to_dict(row) for row in rows]


class MessageRepository:
    def __init__(self, db: sqlite3.Connection):
        self.db = db

    def create(
        self,
        notebook_id: int,
        role: str,
        content: str,
        citations: list[dict[str, Any]] | None = None,
        commit: bool = True,
    ) -> dict[str, Any]:
        cursor = self.db.execute(
            """
            INSERT INTO messages (notebook_id, role, content, citations)
            VALUES (?, ?, ?, ?)
            """,
            (notebook_id, role, content, json.dumps(citations or [])),
        )
        if commit:
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
