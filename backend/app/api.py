import sqlite3

from fastapi import APIRouter, Body, Depends, Query, Response, status

from app.database import get_db
from app.schemas import (
    ChatRequest,
    ChatResponse,
    ChunkResponse,
    MessageResponse,
    NotebookCreate,
    NotebookResponse,
    NotebookUpdate,
    SourceCreate,
    SourceResponse,
    SourceUpdate,
)
from app.services import (
    ChatService,
    NotebookService,
    RetrievalService,
    SourceService,
)


router = APIRouter(prefix="/api")


@router.post(
    "/notebooks",
    response_model=NotebookResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_notebook(
    request: NotebookCreate,
    db: sqlite3.Connection = Depends(get_db),
) -> dict:
    return NotebookService(db).create(request.title)


@router.get("/notebooks", response_model=list[NotebookResponse])
async def list_notebooks(db: sqlite3.Connection = Depends(get_db)) -> list[dict]:
    return NotebookService(db).list_all()


@router.patch("/notebooks/{notebook_id}", response_model=NotebookResponse)
async def rename_notebook(
    notebook_id: int,
    request: NotebookUpdate,
    db: sqlite3.Connection = Depends(get_db),
) -> dict:
    return NotebookService(db).rename(notebook_id, request.title)


@router.delete("/notebooks/{notebook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notebook(
    notebook_id: int,
    db: sqlite3.Connection = Depends(get_db),
) -> Response:
    NotebookService(db).delete(notebook_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/notebooks/{notebook_id}/sources",
    response_model=SourceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_source(
    notebook_id: int,
    request: SourceCreate,
    db: sqlite3.Connection = Depends(get_db),
) -> dict:
    return SourceService(db).create_pasted(
        notebook_id=notebook_id,
        title=request.title,
        content=request.content,
    )


@router.post(
    "/notebooks/{notebook_id}/sources/upload",
    response_model=SourceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_source(
    notebook_id: int,
    filename: str = Query(min_length=1, max_length=160),
    content: bytes = Body(
        min_length=1,
        media_type="application/octet-stream",
    ),
    db: sqlite3.Connection = Depends(get_db),
) -> dict:
    return SourceService(db).create_uploaded_text(
        notebook_id=notebook_id,
        filename=filename,
        content=content,
    )


@router.get("/notebooks/{notebook_id}/sources", response_model=list[SourceResponse])
async def list_sources(
    notebook_id: int,
    db: sqlite3.Connection = Depends(get_db),
) -> list[dict]:
    return SourceService(db).list_for_notebook(notebook_id)


@router.patch("/sources/{source_id}", response_model=SourceResponse)
async def update_source(
    source_id: int,
    request: SourceUpdate,
    db: sqlite3.Connection = Depends(get_db),
) -> dict:
    return SourceService(db).update(
        source_id=source_id,
        title=request.title,
        enabled=request.enabled,
    )


@router.delete("/sources/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_source(
    source_id: int,
    db: sqlite3.Connection = Depends(get_db),
) -> Response:
    SourceService(db).delete(source_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/notebooks/{notebook_id}/chat", response_model=ChatResponse)
async def chat(
    notebook_id: int,
    request: ChatRequest,
    db: sqlite3.Connection = Depends(get_db),
) -> dict:
    return ChatService(db).answer(notebook_id, request.question)


@router.get("/notebooks/{notebook_id}/messages", response_model=list[MessageResponse])
async def list_messages(
    notebook_id: int,
    db: sqlite3.Connection = Depends(get_db),
) -> list[dict]:
    return ChatService(db).list_messages(notebook_id)


@router.get("/chunks/{chunk_id}", response_model=ChunkResponse)
async def get_chunk(
    chunk_id: int,
    db: sqlite3.Connection = Depends(get_db),
) -> dict:
    return RetrievalService(db).get_chunk(chunk_id)
