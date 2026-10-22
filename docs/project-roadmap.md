# Project Roadmap - Mini NotebookLM

Ngay cap nhat: 2026-10-22
Trang thai: Roadmap cho du an moi.

## Phase 0 - Project Docs Baseline

Trang thai: Done.

Muc tieu:

- Tao tai lieu nen dung voi repo moi.
- Dat source of truth truoc khi viet code.

Acceptance:

- Co `README.md`, `docs/design.md`, `docs/project-roadmap.md`,
  `docs/mvp-smoke-test.md`.
- Co report baseline trong `reports/`.
- Khong co docs nao noi app da runnable khi code chua ton tai.

## Phase 1 - Runnable Skeleton

Trang thai: Done.

Muc tieu:

- Backend FastAPI co `/health`.
- Frontend React/Vite app shell.
- Cau truc thu muc dau tien.

Acceptance:

- Backend health endpoint tra OK.
- Frontend dev/build chay duoc.
- README co run instructions that su dung duoc cho skeleton.

## Phase 2 - Backend Core

Trang thai: Done.

Muc tieu:

- SQLite schema va API cho notebook/source/chat mock.

Acceptance:

- Tao notebook -> them pasted source -> chat mock -> doc history thanh cong.
- Co smoke test backend core.

## Phase 3 - Ingestion And Retrieval

Trang thai: Done.

Muc tieu:

- Ingest pasted text; TXT/MD/PDF upload se lam sau khi pasted text on dinh.
- Chunking, embeddings/retrieval local, citation/evidence API.

Acceptance:

- Cau hoi retrieve duoc chunk lien quan.
- Citation tro ve chunk/source/page neu co.
- Disabled source khong duoc retrieve.

## Phase 4 - Frontend MVP

Trang thai: Next.

Muc tieu:

- UI 3 cot cho sources, chat, evidence.

Acceptance:

- Browser flow notebook -> source -> chat -> citation -> evidence chay duoc.
- Co loading/error state co ban.
- Upload UI chi bat khi backend da co endpoint upload.

## Phase 5 - Docker And Gemini

Trang thai: Planned.

Muc tieu:

- Docker/Compose cho app.
- Gemini provider sau khi mock/RAG on dinh.

Acceptance:

- Docker stack healthy voi mock provider.
- Gemini config/dependency duoc verify khi bat Gemini.

## Phase 6 - Evaluation And Demo Release

Trang thai: Planned.

Muc tieu:

- Demo sources, evaluation questions, top-k hit rate script, demo report.

Acceptance:

- Co so lieu evaluation.
- Co checklist demo local/Docker.
