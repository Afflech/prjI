# Mini NotebookLM

Mini NotebookLM is a Project I web app for source-grounded study Q&A.
Users will create notebooks, add PDF/TXT/MD or pasted text sources, then chat
against enabled sources with citations back to original chunks.

## Current Status

Phase 3 ingestion and retrieval is in place. The backend exposes notebook,
pasted source, chunking, retrieval-preview chat, citations, and chunk evidence
APIs backed by SQLite. Full frontend workflows and Docker features are planned
for later phases.

Start with:

- `PROJECT_PLAN.md` for the source-of-truth implementation plan.
- `docs/design.md` for the intended architecture.
- `docs/project-roadmap.md` for phase order and acceptance criteria.
- `docs/mvp-smoke-test.md` for future manual verification steps.
- `reports/phase-0-baseline.md` for the initial Phase 0 report.

## Target Stack

- Backend: FastAPI, SQLite, local hash embeddings for the MVP, Gemini provider
  abstraction later.
- Frontend: React + Vite.
- Retrieval: chunking with overlap, FAISS search when available, NumPy cosine
  fallback.
- LLM: mock/retrieval-preview provider first, Gemini later.

## Target MVP Features

- Create, rename, and delete notebooks.
- Add PDF/TXT/MD files and pasted text sources.
- Ingest sources with text extraction, chunking, embeddings, and vector storage.
- Enable or disable individual sources before chat.
- Keep chat history per notebook.
- Return citations and expose citation details in a UI evidence panel.

## Run

Backend:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements.txt
.venv/bin/uvicorn app.main:app --reload --port 8000 --app-dir backend
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Backend smoke test:

```bash
.venv/bin/python -m pip install -r backend/requirements-dev.txt
.venv/bin/python -m pytest backend/tests
```

API examples:

```bash
curl -X POST http://127.0.0.1:8000/api/notebooks \
  -H 'content-type: application/json' \
  -d '{"title":"Algorithms"}'

curl http://127.0.0.1:8000/api/notebooks
```

After creating a notebook, add a pasted source and chat:

```bash
curl -X POST http://127.0.0.1:8000/api/notebooks/1/sources \
  -H 'content-type: application/json' \
  -d '{"title":"Trees.md","content":"AVL trees rotate to stay balanced."}'

curl -X POST http://127.0.0.1:8000/api/notebooks/1/chat \
  -H 'content-type: application/json' \
  -d '{"question":"How do AVL trees stay balanced?"}'
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Build check:

```bash
cd frontend
npm run build
```

## Project Tracking

- Source of truth: `PROJECT_PLAN.md`
- Design notes: `docs/design.md`
- Roadmap: `docs/project-roadmap.md`
- MVP smoke test checklist: `docs/mvp-smoke-test.md`
- Reports: `reports/`
