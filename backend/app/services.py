import json
import sqlite3
from typing import Any

from fastapi import HTTPException, status

from app.embeddings import (
    embed_text as provider_embed_text,
    searchable_tokens,
    tokenize,
)
from app.limits import MAX_SOURCE_CONTENT_CHARS, MAX_UPLOAD_BYTES
from app.repositories import (
    ChunkRepository,
    MessageRepository,
    NotebookRepository,
    SourceRepository,
)


CHUNK_WORDS = 90
CHUNK_OVERLAP = 20
MAX_RETRIEVAL_RESULTS = 3
SUPPORTED_UPLOAD_SUFFIXES = {
    ".txt": "text_file",
    ".md": "markdown_file",
    ".markdown": "markdown_file",
}


def embed_text(text: str) -> list[float]:
    return provider_embed_text(text)


def cosine_similarity(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right, strict=False))


def chunk_text(text: str) -> list[str]:
    words = text.split()
    if not words:
        return []
    chunks: list[str] = []
    step = CHUNK_WORDS - CHUNK_OVERLAP
    for start in range(0, len(words), step):
        chunk_words = words[start : start + CHUNK_WORDS]
        if not chunk_words:
            break
        chunks.append(" ".join(chunk_words))
        if start + CHUNK_WORDS >= len(words):
            break
    return chunks


def validate_source_content(content: str) -> str:
    stripped = content.strip()
    if not stripped:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Source content cannot be blank",
        )
    if len(stripped) > MAX_SOURCE_CONTENT_CHARS:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Source content must be at most {MAX_SOURCE_CONTENT_CHARS} characters",
        )
    return stripped


def source_type_for_filename(filename: str) -> str:
    lower_filename = filename.strip().lower()
    for suffix, source_type in SUPPORTED_UPLOAD_SUFFIXES.items():
        if lower_filename.endswith(suffix):
            return source_type
    raise HTTPException(
        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        detail="Only .txt, .md, and .markdown uploads are supported",
    )


def decode_text_upload(content: bytes) -> str:
    if not content:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Uploaded file cannot be empty",
        )
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Uploaded file must be at most {MAX_UPLOAD_BYTES} bytes",
        )
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded TXT/MD file must be UTF-8 encoded",
        ) from exc


def chunk_records_for_source(source: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "source_id": source["id"],
            "notebook_id": source["notebook_id"],
            "page": None,
            "text": chunk,
            "embedding": json.dumps(embed_text(chunk)),
        }
        for chunk in chunk_text(source.get("content", ""))
    ]


def citation_from_chunk(chunk: dict[str, Any], score: float) -> dict[str, Any]:
    return {
        "chunk_id": chunk["id"],
        "source_id": chunk["source_id"],
        "source_title": chunk["source_title"],
        "page": chunk["page"],
        "quote": chunk["text"][:240],
        "score": round(score, 4),
    }


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
        self.chunks = ChunkRepository(db)

    def create_pasted(
        self,
        notebook_id: int,
        title: str,
        content: str,
    ) -> dict[str, Any]:
        return self.create_text_source(
            notebook_id=notebook_id,
            title=title,
            content=content,
            source_type="pasted_text",
        )

    def create_uploaded_text(
        self,
        notebook_id: int,
        filename: str,
        content: bytes,
    ) -> dict[str, Any]:
        return self.create_text_source(
            notebook_id=notebook_id,
            title=filename.strip(),
            content=decode_text_upload(content),
            source_type=source_type_for_filename(filename),
        )

    def create_text_source(
        self,
        notebook_id: int,
        title: str,
        content: str,
        source_type: str,
    ) -> dict[str, Any]:
        if self.notebooks.get(notebook_id) is None:
            raise not_found("Notebook", notebook_id)
        normalized_content = validate_source_content(content)
        try:
            source = self.sources.create_text_source(
                notebook_id=notebook_id,
                title=title.strip(),
                content=normalized_content,
                source_type=source_type,
                commit=False,
            )
            chunk_records = chunk_records_for_source(
                {**source, "content": normalized_content}
            )
            self.chunks.create_many(chunk_records, commit=False)
            self.sources.db.commit()
            return self.sources.get(source["id"])
        except Exception:
            self.sources.db.rollback()
            raise

    def backfill_missing_chunks(self) -> int:
        indexed = 0
        try:
            for source in self.sources.list_ready_without_chunks():
                chunk_records = chunk_records_for_source(source)
                self.chunks.create_many(chunk_records, commit=False)
                indexed += len(chunk_records)
            self.sources.db.commit()
        except Exception:
            self.sources.db.rollback()
            raise
        return indexed

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
        self.retrieval = RetrievalService(db)

    def list_messages(self, notebook_id: int) -> list[dict[str, Any]]:
        if self.notebooks.get(notebook_id) is None:
            raise not_found("Notebook", notebook_id)
        return self.messages.list_for_notebook(notebook_id)

    def answer(self, notebook_id: int, question: str) -> dict[str, Any]:
        if self.notebooks.get(notebook_id) is None:
            raise not_found("Notebook", notebook_id)

        retrieved = self.retrieval.search(notebook_id, question)
        citations = [
            citation_from_chunk(chunk, score)
            for chunk, score in retrieved
        ]
        if citations:
            evidence_preview = " ".join(
                citation["quote"] for citation in citations[:2]
            )
            answer = (
                "Retrieval preview answer based on cited source chunks: "
                f"{evidence_preview}"
            )
        else:
            answer = (
                "Retrieval preview answer: no relevant enabled source chunks found. "
                f"Question: {question}"
            )

        try:
            user_message = self.messages.create(
                notebook_id=notebook_id,
                role="user",
                content=question,
                commit=False,
            )
            assistant_message = self.messages.create(
                notebook_id=notebook_id,
                role="assistant",
                content=answer,
                citations=citations,
                commit=False,
            )
            self.messages.db.commit()
        except Exception:
            self.messages.db.rollback()
            raise
        return {
            "answer": answer,
            "citations": citations,
            "user_message": user_message,
            "assistant_message": assistant_message,
        }


class RetrievalService:
    def __init__(self, db: sqlite3.Connection):
        self.chunks = ChunkRepository(db)

    def get_chunk(self, chunk_id: int) -> dict[str, Any]:
        chunk = self.chunks.get(chunk_id)
        if chunk is None:
            raise not_found("Chunk", chunk_id)
        return chunk

    def search(
        self,
        notebook_id: int,
        query: str,
    ) -> list[tuple[dict[str, Any], float]]:
        query_vector = embed_text(query)
        query_tokens = searchable_tokens(query)
        if not query_tokens:
            return []
        scored: list[tuple[dict[str, Any], float]] = []
        for chunk in self.chunks.list_searchable_for_notebook(notebook_id):
            chunk_tokens = searchable_tokens(chunk["text"])
            if not query_tokens.intersection(chunk_tokens):
                continue
            chunk_vector = json.loads(chunk["embedding"] or "[]")
            score = cosine_similarity(query_vector, chunk_vector)
            if score > 0:
                scored.append((chunk, score))
        scored.sort(key=lambda item: item[1], reverse=True)
        return scored[:MAX_RETRIEVAL_RESULTS]
