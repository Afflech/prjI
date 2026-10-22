import importlib
import sys
from pathlib import Path

import pytest


def load_backend(tmp_path, monkeypatch, name: str):
    monkeypatch.setenv("NOTEBOOKLM_DB_PATH", str(tmp_path / f"{name}.db"))
    backend_dir = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(backend_dir))

    database = importlib.import_module("app.database")
    repositories = importlib.import_module("app.repositories")
    services = importlib.import_module("app.services")
    database.init_db()
    return database, repositories, services


def test_init_db_backfills_ready_sources_without_chunks(tmp_path, monkeypatch):
    database, repositories, services = load_backend(tmp_path, monkeypatch, "backfill")

    with database.connect_db() as db:
        notebook = repositories.NotebookRepository(db).create("Legacy notebook")
        source = repositories.SourceRepository(db).create_pasted(
            notebook_id=notebook["id"],
            title="Legacy notes",
            content="Legacy source explains vector clocks and causal ordering.",
        )
        assert services.RetrievalService(db).search(notebook["id"], "vector clocks") == []

    database.init_db()

    with database.connect_db() as db:
        results = services.RetrievalService(db).search(notebook["id"], "vector clocks")

    assert results
    assert results[0][0]["source_id"] == source["id"]


def test_ingestion_failure_rolls_back_ready_source(tmp_path, monkeypatch):
    database, repositories, services = load_backend(tmp_path, monkeypatch, "ingest")

    with database.connect_db() as db:
        notebook = repositories.NotebookRepository(db).create("Rollback notebook")

        def fail_embedding(text: str):
            raise RuntimeError("embedding failed")

        monkeypatch.setattr(services, "embed_text", fail_embedding)
        with pytest.raises(RuntimeError, match="embedding failed"):
            services.SourceService(db).create_pasted(
                notebook_id=notebook["id"],
                title="Broken notes",
                content="This source should not persist as ready.",
            )

        sources = repositories.SourceRepository(db).list_for_notebook(notebook["id"])

    assert sources == []


def test_short_query_requires_token_overlap(tmp_path, monkeypatch):
    database, repositories, services = load_backend(tmp_path, monkeypatch, "short-query")

    with database.connect_db() as db:
        notebook = repositories.NotebookRepository(db).create("Short query")
        services.SourceService(db).create_pasted(
            notebook_id=notebook["id"],
            title="Museum notes",
            content="We study art in an old museum.",
        )
        result = services.ChatService(db).answer(notebook["id"], "AI")

    assert result["citations"] == []
    assert "no relevant enabled source chunks" in result["answer"]


def test_chat_failure_does_not_leave_unpaired_user_message(tmp_path, monkeypatch):
    database, repositories, services = load_backend(tmp_path, monkeypatch, "chat")

    with database.connect_db() as db:
        notebook = repositories.NotebookRepository(db).create("Chat rollback")

        def fail_search(self, notebook_id: int, query: str):
            raise RuntimeError("retrieval failed")

        monkeypatch.setattr(services.RetrievalService, "search", fail_search)
        with pytest.raises(RuntimeError, match="retrieval failed"):
            services.ChatService(db).answer(notebook["id"], "A failed question")

        messages = repositories.MessageRepository(db).list_for_notebook(notebook["id"])

    assert messages == []
