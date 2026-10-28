# Mini NotebookLM

Mini NotebookLM is a Project I web app for source-grounded study Q&A.
Users will create notebooks, add TXT/MD/PDF/PPTX or pasted text sources, then
chat against enabled sources with citations back to original chunks.

## Current Status

Phase 4 frontend MVP is complete for local demo. The backend exposes notebook,
pasted source, TXT/MD/PDF/PPTX raw upload, chunking, retrieval-preview chat,
citations, and chunk evidence APIs backed by SQLite. The frontend now provides
the main notebook/source/chat/evidence workspace. Docker and Gemini features are
planned for later phases.

Start with:

- `PROJECT_PLAN.md` for the source-of-truth implementation plan.
- `docs/design.md` for the intended architecture.
- `docs/project-roadmap.md` for phase order and acceptance criteria.
- `docs/mvp-smoke-test.md` for future manual verification steps.
- `reports/phase-0-baseline.md` for the initial Phase 0 report.

## Target Stack

- Backend: FastAPI, SQLite, local hash embeddings for offline MVP tests, and
  an HTTP embedding provider abstraction.
- Frontend: React + Vite.
- Retrieval: chunking with overlap, Unicode token gating, and cosine scoring.
- LLM: mock/retrieval-preview provider first, Gemini later.

## Target MVP Features

- Create, rename, and delete notebooks.
- Add TXT/MD/PDF/PPTX files and pasted text sources.
- Ingest sources with text extraction, chunking, embeddings, and vector storage.
- Enable or disable individual sources before chat.
- Keep chat history per notebook.
- Return citations and expose citation details in a UI evidence panel.

## Run

Backend:

```bash
./scripts/backend.sh
```

Lần đầu setup backend:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements.txt
```

Đổi port nếu cần, ví dụ: `PORT=8010 ./scripts/backend.sh`.

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

Upload a source file with a raw body:

```bash
curl -X POST 'http://127.0.0.1:8000/api/notebooks/1/sources/upload?filename=notes.md' \
  -H 'content-type: text/markdown; charset=utf-8' \
  --data-binary @notes.md
```

Supported upload types are `.txt`, `.md`, `.markdown`, `.pdf`, and `.pptx`.
Legacy `.ppt` files are not supported. PDF OCR is optional: set
`OCR_ENABLED=1` and install local OCR dependencies such as Poppler and
Tesseract plus Python packages `pdf2image` and `pytesseract` to attempt OCR when
a PDF has no extractable text.

Embedding configuration:

```bash
# Default, offline and used by tests
EMBEDDING_PROVIDER=hash

# OpenAI-compatible HTTP embeddings
EMBEDDING_PROVIDER=openai
EMBEDDING_API_KEY=...
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_BASE_URL=https://api.openai.com/v1/embeddings
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

During local frontend development, Vite proxies `/api` and `/health` to the
backend on `http://127.0.0.1:8000`.

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
