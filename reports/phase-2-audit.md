# Phase 2 Audit Report - Mini NotebookLM

Ngay cap nhat: 2026-10-21
Phase duoc audit: 2 - Backend core
Ket luan: Pass sau khi bo sung smoke coverage cho rename/delete

## 1. Pham vi audit

Audit doi chieu repo hien tai voi `PROJECT_PLAN.md`, `docs/project-roadmap.md`,
va `reports/phase-2-backend-core.md`.

Pham vi da xem:

- Backend entrypoint va routing: `backend/app/main.py`, `backend/app/api.py`.
- Database/schema: `backend/app/database.py`.
- Validation/contract: `backend/app/schemas.py`.
- Service/repository layers: `backend/app/services.py`,
  `backend/app/repositories.py`.
- Smoke test: `backend/tests/test_phase2_smoke.py`.
- README va tracking docs.

## 2. Ket qua acceptance

Pass:

- SQLite schema co `notebooks`, `sources`, `chunks`, va `messages`.
- Notebook API co create, list, rename, delete.
- Source API co paste text, list, enable/disable/update, delete.
- Chat API nhan cau hoi, tra mock answer, va luu user/assistant messages.
- Source response co `status` va `enabled` de dung cho Phase 3 retrieval.
- Smoke test backend core chay thanh cong.

## 3. Dieu da sua trong audit

- Smoke test ban dau da cover flow chinh nhung chua cover het API da tao.
- Da bo sung coverage cho:
  - list notebooks,
  - rename notebook,
  - delete source,
  - delete notebook,
  - not-found sau khi xoa notebook.

## 4. Architectural notes

- Backend dang theo layering gon: API routes -> services -> repositories ->
  SQLite. Day la fit voi quy mo Phase 2 va de tach them ingestion/retrieval o
  Phase 3.
- API dung resource-oriented endpoints, HTTP method dung ngu nghia REST co ban,
  va response models ro rang.
- Validation da chan title/content/question rong sau khi trim, giam nguy co tao
  entity blank.
- SQLite connection bat `PRAGMA foreign_keys = ON`, nen cascade delete phu hop
  schema hien tai.

## 5. Rui ro con lai

- Chua co pagination/filtering cho list endpoints. Chap nhan duoc o Phase 2,
  nen xem lai khi co nhieu notebook/source/message hon.
- SQLite access dang sync ben trong async route. Chap nhan duoc cho local MVP,
  nhung Phase sau nen can than voi operation nang nhu extraction/embedding.
- API chua versioned (`/api` thay vi `/api/v1`). Chap nhan duoc khi chua co
  public client, nhung nen quyet dinh truoc khi frontend MVP on dinh.

## 6. Verification da chay

- `.venv/bin/python -m pytest backend/tests` -> 1 passed.
- `npm run build` trong `frontend/` -> thanh cong.

## 7. Ket luan

Phase 2 dat acceptance va co the xem la Done. Co the chuyen sang Phase 3:
ingestion va retrieval cho pasted text/TXT/MD, chunk records, va citation/
evidence API.
