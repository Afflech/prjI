# Phase 4 Status Report - Mini NotebookLM

Ngay: 2026-10-23
Phase: 4 - Frontend MVP
Trang thai: In progress

## Tom tat

Frontend MVP da thay placeholder shell bang workspace 3 cot cho sources, chat,
va evidence. UI da noi vao cac API backend hien co de demo flow notebook ->
source -> chat -> citation -> evidence voi pasted text va TXT/MD upload.

## Da co

- Notebook create/select/rename/delete.
- Pasted source create va TXT/MD upload qua endpoint raw body.
- Source status, enable/disable, va delete.
- Chat history per notebook, question composer, assistant messages, citation
  chips.
- Evidence panel goi `/api/chunks/{chunk_id}` khi click citation.
- Loading/disabled states theo tung khu vuc va error banner.
- Message assistant khong co citation hien note rieng de tranh hieu nham
  evidence panel bi loi.
- Evidence panel co state loading/error rieng va an page khi TXT/MD khong co
  metadata page.
- Rename notebook khong reload/clear chat va evidence khong can thiet.
- Them/xoa/upload source chi refresh source list, khong reset chat history.
- Composer duoc gioi han chieu cao de khong day lech vung chat.
- Vite dev proxy cho `/api` va `/health` sang backend local port 8000.
- Responsive layout stack thanh mot cot tren viewport nho.

## Con lai

- Chua them browser automation vi repo hien chua co Playwright/Cypress setup.
- PDF upload van ngoai scope Phase 4, dung theo backend Phase 3 hien tai.
- Retrieval preview dung hash embedding va token gate con tho; cau hoi co the
  tra chunk dung source nhung chua phai chunk giai thich tot nhat.
- Source trung title duoc phep trong MVP; UI da hien source id de phan biet.

## Validation

```bash
cd frontend && npm run build
.venv/bin/python -m pytest backend/tests
```

Ket qua:

- Frontend build passed sau audit fixes.
- Backend regression: 7 passed.
- Manual browser smoke: pass cho pasted/TXT-MD source -> matching question ->
  citation chips -> evidence panel. No-citation path cung hien note huong dan.
