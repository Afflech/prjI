# Phase 3 Audit Report - Mini NotebookLM

Ngay: 2026-10-22
Phase duoc audit: 3 - Ingestion va retrieval
Ket luan: Pass, co the chuyen sang Phase 4

## Skills da dung

- `architect-review`: doi chieu tac dong kien truc, layer boundaries, va tinh
  maintainable cua retrieval MVP.
- `backend-dev-guidelines`: doi chieu API/service/repository separation, input
  validation, test coverage, va anti-patterns backend.

## Pham vi audit

- Backend ingestion/retrieval: `backend/app/services.py`,
  `backend/app/repositories.py`, `backend/app/api.py`, `backend/app/schemas.py`.
- Tests: `backend/tests/test_phase2_smoke.py`,
  `backend/tests/test_phase3_retrieval.py`.
- Tai lieu phase: `PROJECT_PLAN.md`, `docs/project-roadmap.md`,
  `docs/design.md`, `README.md`, `reports/phase-3-retrieval.md`.

## Findings

Khong co issue blocker.

Da sua trong audit:

- Route evidence ban dau tao `ChunkRepository` truc tiep. Da chuyen sang
  `RetrievalService(db)` de giu API layer mong va repository nam sau service.

Residual risks:

- Retrieval hien dung local hash embedding va token overlap gate, du cho smoke
  test va demo offline nhung chua phai semantic retrieval that.
- Ingestion moi co pasted text. Upload TXT/MD va PDF extraction van la viec sau.
- Source status failed chi co schema/field tu Phase 2; pipeline hien tai chua co
  failure-path rieng ngoai loi runtime cua request.

## Acceptance Phase 3

- Cau hoi retrieve duoc chunk lien quan: Pass.
- Citation co chunk id, source id, source title, page neu co: Pass.
- Disabled source khong duoc retrieve/cite: Pass.
- Evidence endpoint tra chunk goc cho citation: Pass.

## Validation

Command:

```bash
.venv/bin/python -m pytest backend/tests
git diff --check
```

Ket qua:

- Backend tests: 2 passed.
- Whitespace check: clean.

## Kien nghi Phase 4

- Noi UI chat vao citation chips va evidence endpoint truoc khi them upload/PDF.
- Neu them upload TXT/MD, dung chung ingestion service hien co de tranh rework.
