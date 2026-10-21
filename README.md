# Mini NotebookLM

Mini NotebookLM is a Project I web app for source-grounded study Q&A.
Users will create notebooks, add PDF/TXT/MD or pasted text sources, then chat
against enabled sources with citations back to original chunks.

## Current Status

This is a new project. The repository currently contains planning and baseline
documentation only; the backend, frontend, ingestion pipeline, retrieval system,
and Docker setup have not been implemented yet.

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

There is no runnable app yet. Run instructions will be added after Phase 1
creates the backend and frontend skeletons.

## Project Tracking

- Source of truth: `PROJECT_PLAN.md`
- Design notes: `docs/design.md`
- Roadmap: `docs/project-roadmap.md`
- MVP smoke test checklist: `docs/mvp-smoke-test.md`
- Reports: `reports/`
