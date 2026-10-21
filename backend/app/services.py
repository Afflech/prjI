import sqlite3
from typing import Any

from fastapi import HTTPException, status

from app.repositories import MessageRepository, NotebookRepository, SourceRepository


def not_found(resource: str, resource_id: int) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "error": "NotFound",
            "message": f"{resource} not found",
            "details": {"id": resource_id},
        },
    )


class NotebookService:
    def __init__(self, db: sqlite3.Connection):
        self.notebooks = NotebookRepository(db)

    def create(self, title: str) -> dict[str, Any]:
        return self.notebooks.create(title.strip())

    def list_all(self) -> list[dict[str, Any]]:
        return self.notebooks.list_all()

    def get_required(self, notebook_id: int) -> dict[str, Any]:
        notebook = self.notebooks.get(notebook_id)
        if notebook is None:
            raise not_found("Notebook", notebook_id)
        return notebook

    def rename(self, notebook_id: int, title: str) -> dict[str, Any]:
        self.get_required(notebook_id)
        return self.notebooks.rename(notebook_id, title.strip())

    def delete(self, notebook_id: int) -> None:
        if not self.notebooks.delete(notebook_id):
            raise not_found("Notebook", notebook_id)


class SourceService:
    def __init__(self, db: sqlite3.Connection):
        self.notebooks = NotebookRepository(db)
        self.sources = SourceRepository(db)

    def create_pasted(
        self,
        notebook_id: int,
        title: str,
        content: str,
    ) -> dict[str, Any]:
        if self.notebooks.get(notebook_id) is None:
            raise not_found("Notebook", notebook_id)
        return self.sources.create_pasted(notebook_id, title.strip(), content)

    def list_for_notebook(self, notebook_id: int) -> list[dict[str, Any]]:
        if self.notebooks.get(notebook_id) is None:
            raise not_found("Notebook", notebook_id)
        return self.sources.list_for_notebook(notebook_id)

    def update(
        self,
        source_id: int,
        title: str | None = None,
        enabled: bool | None = None,
    ) -> dict[str, Any]:
        if self.sources.get(source_id) is None:
            raise not_found("Source", source_id)
        normalized_title = title.strip() if title is not None else None
        return self.sources.update(source_id, normalized_title, enabled)

    def delete(self, source_id: int) -> None:
        if not self.sources.delete(source_id):
            raise not_found("Source", source_id)


class ChatService:
    def __init__(self, db: sqlite3.Connection):
        self.notebooks = NotebookRepository(db)
        self.sources = SourceRepository(db)
        self.messages = MessageRepository(db)

    def list_messages(self, notebook_id: int) -> list[dict[str, Any]]:
        if self.notebooks.get(notebook_id) is None:
            raise not_found("Notebook", notebook_id)
        return self.messages.list_for_notebook(notebook_id)

    def answer(self, notebook_id: int, question: str) -> dict[str, Any]:
        if self.notebooks.get(notebook_id) is None:
            raise not_found("Notebook", notebook_id)

        user_message = self.messages.create(
            notebook_id=notebook_id,
            role="user",
            content=question,
        )
        enabled_sources = self.sources.list_enabled_for_notebook(notebook_id)
        source_titles = ", ".join(source["title"] for source in enabled_sources)
        if source_titles:
            answer = (
                "Mock answer based on enabled sources: "
                f"{source_titles}. Question: {question}"
            )
        else:
            answer = (
                "Mock answer: no enabled sources are ready yet. "
                f"Question: {question}"
            )

        assistant_message = self.messages.create(
            notebook_id=notebook_id,
            role="assistant",
            content=answer,
            citations=[],
        )
        return {
            "answer": answer,
            "citations": [],
            "user_message": user_message,
            "assistant_message": assistant_message,
        }
