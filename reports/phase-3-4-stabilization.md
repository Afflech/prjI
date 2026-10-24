# Phase 3/4 Stabilization Report - Mini NotebookLM

Ngay: 2026-10-25
Phase: 3 - Ingestion/retrieval; 4 - Frontend MVP
Trang thai: Done for local MVP

## Tom tat

MVP local hien da cover flow chinh: notebook -> source upload/paste -> chat ->
citation -> evidence. Backend ho tro pasted text, TXT/MD, PDF, va PPTX. PDF
giu page metadata khi text extraction lay duoc page; PPTX ingest text nhung
khong gan slide/page metadata theo scope da chot.

## Da co

- Upload va retrieval cho TXT/MD/PDF/PPTX.
- PDF text extraction bang `pypdf` voi citation page metadata.
- PPTX text extraction bang `python-pptx`, citation khong co page metadata.
- OCR optional fallback cho PDF scan khi `OCR_ENABLED=1` va local OCR
  dependencies duoc cai; OCR khong bat buoc cho base MVP.
- Frontend upload UI chap nhan TXT/MD/PDF/PPTX va hien label source type.
- Evidence panel hien page cho PDF va an page khi metadata khong co.
- Regression tests cho PDF/PPTX, `.ppt` unsupported, oversized upload, OCR
  disabled message, extractor smoke, rollback, disabled source, va Unicode.

## Validation

```bash
.venv/bin/python -m pytest backend/tests
cd frontend && npm run build
git diff --check
```

Ket qua:

- Backend tests: 13 passed.
- Frontend build: passed.
- Diff whitespace check: passed.
- API smoke: passed cho TXT, MD, PDF, PPTX upload -> chat -> citation ->
  evidence; PDF page metadata; va `.ppt` rejection.

## Known Limitations

- Retrieval preview van dung local hash embedding va token gate, nen ranking
  chunk con tho.
- OCR la optional fallback, chua phai duong chay mac dinh va can cai Poppler,
  Tesseract, `pdf2image`, `pytesseract` neu muon dung.
- Chua co Playwright/Cypress browser automation.
- Chua co Docker/Compose, Gemini provider, evaluation dataset, hay demo release
  script.

## Ket luan

Phase 3 va Phase 4 dat acceptance cho local MVP. Buoc tiep theo nen la Phase 5:
Docker/Compose de demo de hon, sau do them Gemini provider khi can cau tra loi
tu nhien hon retrieval preview.
