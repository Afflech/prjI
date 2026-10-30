# Project Roadmap - Mini NotebookLM

Ngay cap nhat: 2026-10-25
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

- Ingest pasted text va TXT/MD/PDF/PPTX upload.
- PDF citation giu page metadata neu extract duoc.
- OCR la optional fallback cho PDF scan, khong bat buoc cho base MVP.
- Chunking, Unicode retrieval, embedding provider abstraction, citation/evidence
  API.

Acceptance:

- Cau hoi retrieve duoc chunk lien quan.
- Citation tro ve chunk/source/page neu co.
- Disabled source khong duoc retrieve.
- TXT/MD/PDF/PPTX upload retrieve duoc noi dung tieng Viet/Unicode.

## Phase 4 - Frontend MVP

Trang thai: Done.

Muc tieu:

- UI 3 cot cho sources, chat, evidence.

Acceptance:

- Browser flow notebook -> source -> chat -> citation -> evidence chay duoc.
- Co loading/error state co ban.
- Upload UI noi vao TXT/MD/PDF/PPTX endpoint backend.

Tien do:

- UI 3 cot, notebook CRUD, source paste/upload/toggle/delete, chat citation
  chips, evidence panel, va Vite API proxy da duoc implement.
- Audit fixes cho UX no-citation, evidence state, composer layout, va reload
  state da duoc implement.
- Playwright E2E flow da duoc them cho notebook -> pasted source -> chat ->
  citation -> evidence va disabled-source behavior. Dependency da co; chua chay
  suite vi Chromium browser binary chua tai duoc trong moi truong nay.
- Build frontend, backend regression tests, va smoke API pass.
- TXT/MD/PDF/PPTX citation/evidence flow da duoc verify. Retrieval quality van
  la known limitation; Playwright E2E da co nhung chua duoc chay vi thieu
  Chromium browser binary.

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
