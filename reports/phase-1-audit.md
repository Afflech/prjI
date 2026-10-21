# Phase 1 Audit Report - Mini NotebookLM

Ngay cap nhat: 2026-10-21
Phase duoc audit: 1 - Runnable skeleton
Ket luan: Pass, co khuyen nghi nho truoc Phase 2

## 1. Pham vi audit

Audit doi chieu repo hien tai voi `PROJECT_PLAN.md`, `docs/project-roadmap.md`,
va `reports/phase-1-skeleton.md`.

Pham vi da xem:

- Backend skeleton: `backend/app/main.py`, `backend/requirements.txt`.
- Frontend skeleton: `frontend/package.json`, `frontend/src/main.jsx`,
  `frontend/src/styles.css`.
- Tai lieu tracking: `README.md`, `PROJECT_PLAN.md`,
  `docs/project-roadmap.md`, `docs/design.md`.
- Ignore/build hygiene: `.gitignore`.

## 2. Ket qua acceptance

Pass:

- Co cau truc `backend/`, `frontend/`, `docs/`, `eval/`, `demo_sources/`,
  `scripts/`.
- Backend FastAPI co endpoint `GET /health`.
- Backend `/health` tra `{"status":"ok"}` khi chay local.
- Frontend React/Vite app shell build thanh cong bang `npm run build`.
- Frontend dev server tra HTTP 200.
- README co lenh chay backend/frontend dung voi file da tao.
- Chua vuot scope sang notebook, ingestion, retrieval, hay chat.

## 3. Findings

### Low - Frontend dependencies dung `latest`

`frontend/package.json` dung `latest` cho Vite, React, React DOM, va
`@vitejs/plugin-react`. Hien tai `package-lock.json` giup `npm install` lap lai
duoc trong repo, nhung neu lockfile bi regenerate hoac dependency duoc update
trong Phase 2, behavior co the drift kho kiem soat.

Khuyen nghi:

- Pin version trong `package.json` theo version da lock khi bat dau Phase 2.
- Chi update dependency co chu dich va chay lai build/smoke test.

### Info - Backend smoke test can dependency test rieng neu dung `TestClient`

Thu `fastapi.testclient.TestClient` hien loi vi thieu `httpx`. Dieu nay khong
lam fail Phase 1 vi acceptance chi can app chay va `/health` OK, nhung Phase 2
co muc tieu smoke test backend core nen can chot cach test.

Khuyen nghi:

- Them test dependencies rieng, vi du `backend/requirements-dev.txt` co `httpx`
  va `pytest`, neu dung FastAPI `TestClient`.
- Hoac viet smoke test dang process/curl neu muon giu requirements toi gian.

## 4. Architectural notes

- Skeleton backend dung mot FastAPI app don gian, phu hop Phase 1 va de tach
  router/service/database trong Phase 2.
- UI shell co ba vung sources/chat/evidence dung voi huong Phase 4, nhung van
  khong gia lap tinh nang chua co.
- `.gitignore` da che `.venv`, `node_modules`, `dist`, `__pycache__`, va env
  files, phu hop baseline hygiene.

## 5. Verification da chay

- `curl -s http://127.0.0.1:8000/health` -> `{"status":"ok"}`.
- `curl -s -I http://127.0.0.1:5173/` -> HTTP 200.
- `npm run build` trong `frontend/` -> thanh cong.
- `git check-ignore` xac nhan `.venv`, `frontend/node_modules`,
  `frontend/dist`, va `backend/app/__pycache__` duoc ignore.

## 6. Ket luan

Phase 1 dat acceptance va co the xem la Done. Nen xu ly hai khuyen nghi nho
ve dependency pinning va backend test dependencies khi bat dau Phase 2.
