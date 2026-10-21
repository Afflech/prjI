# Phase 2 Backend Core Report - Mini NotebookLM

Ngay cap nhat: 2026-10-21
Phase: 2 - Backend core
Trang thai: Done

## Summary

Da them backend core cho flow notebook -> pasted source -> mock chat -> history.
Backend dung FastAPI va SQLite, co schema target cho `notebooks`, `sources`,
`chunks`, va `messages`.

## Da lam

- Tao SQLite schema va connection helper trong `backend/app/database.py`.
- Tach backend thanh API, schemas, services, repositories.
- Them notebook API: create, list, rename, delete.
- Them source API: paste text, list, enable/disable/title update, delete.
- Them chat API: nhan cau hoi, tra mock answer, luu user/assistant messages.
- Them message history API theo notebook.
- Them `backend/requirements-dev.txt` voi `httpx` va `pytest`.
- Them smoke test `backend/tests/test_phase2_smoke.py`.
- Pin frontend dependencies theo version dang lock de giam drift.

## Acceptance Phase 2

- Tao notebook -> them pasted source -> chat mock -> doc history thanh cong: Dat.
- Source co status va enabled flag de dung cho phase retrieval: Dat.
- Co smoke test backend core: Dat.

## API hien co

- `POST /api/notebooks`
- `GET /api/notebooks`
- `PATCH /api/notebooks/{notebook_id}`
- `DELETE /api/notebooks/{notebook_id}`
- `POST /api/notebooks/{notebook_id}/sources`
- `GET /api/notebooks/{notebook_id}/sources`
- `PATCH /api/sources/{source_id}`
- `DELETE /api/sources/{source_id}`
- `POST /api/notebooks/{notebook_id}/chat`
- `GET /api/notebooks/{notebook_id}/messages`

## Verification da chay

- `.venv/bin/python -m pytest backend/tests` -> 1 passed.
- Uvicorn smoke: `GET /health` -> `{"status":"ok"}`.
- Uvicorn smoke: `POST /api/notebooks` -> tao notebook thanh cong.

## Chua lam

- Chua chunk pasted source thanh `chunks`.
- Chua co embeddings/retrieval/citation evidence.
- Chua co frontend UI goi backend core.
- Chua co Docker/Gemini/evaluation.

## Viec tiep theo

1. Bat dau Phase 3: ingestion va retrieval cho pasted text/TXT/MD.
2. Tao chunk records tu source content va citation/evidence API.
3. Dam bao disabled source khong duoc retrieve/cite.
