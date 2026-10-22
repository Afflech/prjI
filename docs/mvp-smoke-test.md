# MVP Smoke Test Checklist - Mini NotebookLM

Ngay cap nhat: 2026-10-22
Trang thai: Checklist target, dung sau khi co implementation.

## Phase 1 Skeleton

- Backend starts without error.
- `GET /health` returns OK.
- Frontend dev server starts.
- Frontend build succeeds.
- README run commands match real files.

## Phase 2 Backend Core

- Create notebook.
- List notebooks.
- Rename notebook.
- Delete notebook.
- Add pasted text source.
- List sources in a notebook.
- Enable/disable source.
- Send chat question and receive mock answer.
- Read chat history.

## Phase 3 Retrieval

- Ingest TXT/MD or pasted text.
- Chunk records are created.
- Unicode/Vietnamese query retrieves relevant chunk.
- Query retrieves relevant chunk.
- Citation includes chunk id and source id.
- Disabled source is excluded from retrieval.
- Ingestion failure does not leave a ready source without chunks.

## Phase 4 Frontend MVP

- User can create/select notebook.
- User can add source.
- Source status is visible.
- User can disable and re-enable source.
- User can ask a question.
- Answer displays citation chips.
- Clicking citation opens evidence panel.
- UI shows loading and error states.

## Phase 5 Docker/Gemini

- Docker stack starts with mock provider.
- Backend healthcheck passes in Docker.
- Frontend can reach backend from browser.
- Gemini mode refuses to start without required key.
- Gemini mode does not log secret values.

## Phase 6 Evaluation

- Evaluation set has 20-30 questions.
- Each question has expected source/evidence.
- Top-k hit rate script runs.
- Report records results and known limitations.
