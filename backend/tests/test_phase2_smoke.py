import importlib
import asyncio
import sys
from pathlib import Path

from httpx import ASGITransport, AsyncClient


def test_notebook_source_chat_smoke(tmp_path, monkeypatch):
    asyncio.run(run_smoke_test(tmp_path, monkeypatch))


async def run_smoke_test(tmp_path, monkeypatch):
    monkeypatch.setenv("NOTEBOOKLM_DB_PATH", str(tmp_path / "smoke.db"))
    backend_dir = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(backend_dir))

    main = importlib.import_module("app.main")
    database = importlib.import_module("app.database")
    database.init_db()

    transport = ASGITransport(app=main.app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        notebook_response = await client.post(
            "/api/notebooks",
            json={"title": "Algorithms"},
        )
        assert notebook_response.status_code == 201
        notebook = notebook_response.json()
        assert notebook["title"] == "Algorithms"

        list_notebooks_response = await client.get("/api/notebooks")
        assert list_notebooks_response.status_code == 200
        assert [item["id"] for item in list_notebooks_response.json()] == [
            notebook["id"]
        ]

        rename_response = await client.patch(
            f"/api/notebooks/{notebook['id']}",
            json={"title": "Algorithms 101"},
        )
        assert rename_response.status_code == 200
        assert rename_response.json()["title"] == "Algorithms 101"

        blank_notebook_response = await client.post(
            "/api/notebooks",
            json={"title": "   "},
        )
        assert blank_notebook_response.status_code == 422

        source_response = await client.post(
            f"/api/notebooks/{notebook['id']}/sources",
            json={
                "title": "Lecture notes",
                "content": "Binary search halves the search range each step.",
            },
        )
        assert source_response.status_code == 201
        source = source_response.json()
        assert source["status"] == "ready"
        assert source["enabled"] is True

        update_response = await client.patch(
            f"/api/sources/{source['id']}",
            json={"enabled": False},
        )
        assert update_response.status_code == 200
        assert update_response.json()["enabled"] is False

        restore_response = await client.patch(
            f"/api/sources/{source['id']}",
            json={"enabled": True},
        )
        assert restore_response.status_code == 200
        assert restore_response.json()["enabled"] is True

        chat_response = await client.post(
            f"/api/notebooks/{notebook['id']}/chat",
            json={"question": "What does binary search do?"},
        )
        assert chat_response.status_code == 200
        chat = chat_response.json()
        assert "Retrieval preview answer" in chat["answer"]
        assert chat["user_message"]["role"] == "user"
        assert chat["assistant_message"]["role"] == "assistant"

        history_response = await client.get(
            f"/api/notebooks/{notebook['id']}/messages"
        )
        assert history_response.status_code == 200
        history = history_response.json()
        assert [message["role"] for message in history] == ["user", "assistant"]

        list_sources_response = await client.get(
            f"/api/notebooks/{notebook['id']}/sources"
        )
        assert list_sources_response.status_code == 200
        assert list_sources_response.json()[0]["enabled"] is True

        delete_source_response = await client.delete(f"/api/sources/{source['id']}")
        assert delete_source_response.status_code == 204

        empty_sources_response = await client.get(
            f"/api/notebooks/{notebook['id']}/sources"
        )
        assert empty_sources_response.status_code == 200
        assert empty_sources_response.json() == []

        delete_notebook_response = await client.delete(
            f"/api/notebooks/{notebook['id']}"
        )
        assert delete_notebook_response.status_code == 204

        missing_history_response = await client.get(
            f"/api/notebooks/{notebook['id']}/messages"
        )
        assert missing_history_response.status_code == 404
