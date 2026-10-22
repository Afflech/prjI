# Phase 3 Retrieval Report - Mini NotebookLM

Ngay: 2026-10-22
Phase: 3 - Ingestion va retrieval
Trang thai: Done

## Tom tat

Phase 3 da them ingestion va retrieval offline cho pasted text. Khi tao source,
backend tach noi dung thanh chunks co overlap, tao local hash embedding, luu vao
SQLite, va chat se retrieve chunks tu enabled ready sources de tra citations.
Co endpoint evidence de lay chunk goc theo citation.

## Thay doi chinh

- Them `ChunkRepository` de tao va doc chunks/evidence.
- Them chunking, local hash embedding, cosine retrieval trong service layer.
- Chat response chuyen tu mock answer rong citation sang retrieval-preview answer
  co citations khi tim duoc chunk lien quan.
- Them endpoint `GET /api/chunks/{chunk_id}` cho evidence panel phase sau.
- Them smoke test `backend/tests/test_phase3_retrieval.py`.

## Acceptance Phase 3

- Hoi cau lien quan den source thi retrieve duoc chunk phu hop: Dat.
- Citation co chunk id, source id, source title, page neu co: Dat.
- Disabled source khong duoc retrieve/cite: Dat.

## Validation

Command:

```bash
.venv/bin/python -m pytest backend/tests
```

Ket qua: 2 passed.

## Ghi chu

- Pasted text da duoc ingest; upload TXT/MD file chua co UI/API rieng va co the
  noi vao cung pipeline trong phase sau.
- PDF extraction van de sau khi flow TXT/MD va frontend on dinh.
- Retrieval hien dung stdlib hash embedding de khong them dependency moi.

## Viec tiep theo

1. Bat dau Phase 4: frontend MVP cho notebook, sources, chat, citation chips,
   va evidence panel.
2. Neu can upload file trong UI, them endpoint upload TXT/MD dung chung pipeline
   pasted text truoc khi cham PDF.
