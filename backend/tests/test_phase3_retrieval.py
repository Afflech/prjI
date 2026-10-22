import asyncio
import importlib
import sys
from pathlib import Path

from httpx import ASGITransport, AsyncClient


def test_retrieval_citations_and_disabled_sources(tmp_path, monkeypatch):
    asyncio.run(run_retrieval_test(tmp_path, monkeypatch))


async def run_retrieval_test(tmp_path, monkeypatch):
    monkeypatch.setenv("NOTEBOOKLM_DB_PATH", str(tmp_path / "retrieval.db"))
    backend_dir = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(backend_dir))

    main = importlib.import_module("app.main")
    database = importlib.import_module("app.database")
    database.init_db()

    transport = ASGITransport(app=main.app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        notebook_response = await client.post(
            "/api/notebooks",
            json={"title": "Data structures"},
        )
        assert notebook_response.status_code == 201
        notebook = notebook_response.json()

        source_response = await client.post(
            f"/api/notebooks/{notebook['id']}/sources",
            json={
                "title": "Trees.md",
                "content": (
                    "AVL trees rotate after insertions to keep the tree balanced. "
                    "Balanced trees keep search, insert, and delete operations fast."
                ),
            },
        )
        assert source_response.status_code == 201
        source = source_response.json()

        chat_response = await client.post(
            f"/api/notebooks/{notebook['id']}/chat",
            json={"question": "How do AVL trees stay balanced?"},
        )
        assert chat_response.status_code == 200
        chat = chat_response.json()
        assert chat["citations"]
        citation = chat["citations"][0]
        assert citation["source_id"] == source["id"]
        assert citation["source_title"] == "Trees.md"
        assert citation["chunk_id"]
        assert "AVL trees rotate" in citation["quote"]

        evidence_response = await client.get(f"/api/chunks/{citation['chunk_id']}")
        assert evidence_response.status_code == 200
        evidence = evidence_response.json()
        assert evidence["id"] == citation["chunk_id"]
        assert evidence["source_id"] == source["id"]
        assert "Balanced trees" in evidence["text"]

        disable_response = await client.patch(
            f"/api/sources/{source['id']}",
            json={"enabled": False},
        )
        assert disable_response.status_code == 200

        disabled_chat_response = await client.post(
            f"/api/notebooks/{notebook['id']}/chat",
            json={"question": "How do AVL trees stay balanced?"},
        )
        assert disabled_chat_response.status_code == 200
        disabled_chat = disabled_chat_response.json()
        assert disabled_chat["citations"] == []
        assert "no relevant enabled source chunks" in disabled_chat["answer"]


def test_upload_txt_md_and_unicode_retrieval(tmp_path, monkeypatch):
    asyncio.run(run_upload_unicode_test(tmp_path, monkeypatch))


async def run_upload_unicode_test(tmp_path, monkeypatch):
    monkeypatch.setenv("NOTEBOOKLM_DB_PATH", str(tmp_path / "upload.db"))
    backend_dir = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(backend_dir))

    main = importlib.import_module("app.main")
    database = importlib.import_module("app.database")
    database.init_db()

    transport = ASGITransport(app=main.app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        notebook_response = await client.post(
            "/api/notebooks",
            json={"title": "Tieng Viet"},
        )
        assert notebook_response.status_code == 201
        notebook = notebook_response.json()

        upload_response = await client.post(
            f"/api/notebooks/{notebook['id']}/sources/upload",
            params={"filename": "do-thi.md"},
            content=(
                "# Do thi\n\n"
                "Đồ thị có đỉnh và cạnh. Thuật toán BFS duyệt các đỉnh theo lớp."
            ).encode("utf-8"),
            headers={"content-type": "text/markdown; charset=utf-8"},
        )
        assert upload_response.status_code == 201
        source = upload_response.json()
        assert source["type"] == "markdown_file"

        chat_response = await client.post(
            f"/api/notebooks/{notebook['id']}/chat",
            json={"question": "BFS duyệt đồ thị như thế nào?"},
        )
        assert chat_response.status_code == 200
        chat = chat_response.json()
        assert chat["citations"]
        assert chat["citations"][0]["source_id"] == source["id"]
        assert "Đồ thị" in chat["citations"][0]["quote"]

        invalid_upload = await client.post(
            f"/api/notebooks/{notebook['id']}/sources/upload",
            params={"filename": "scan.pdf"},
            content=b"PDF comes later",
            headers={"content-type": "application/pdf"},
        )
        assert invalid_upload.status_code == 415
