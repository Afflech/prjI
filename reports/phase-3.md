# Phase 3 Status Report - Mini NotebookLM

Ngay: 2026-10-22
Phase: 3 - Ingestion va retrieval
Trang thai: In progress

## Tom tat

Phase 3 hien co backend retrieval cho pasted text va TXT/MD raw upload. Backend
chunk source text, tao embeddings qua provider boundary, retrieve tren enabled
ready sources, tra citations, va co evidence endpoint de lay chunk goc.

## Da co

- Pasted text va TXT/MD upload endpoint dung chung ingestion pipeline.
- Unicode tokenizer ho tro tieng Viet co dau va text khong phai ASCII.
- Embedding interface voi local hash provider mac dinh cho offline tests va
  OpenAI-compatible HTTP provider khi cau hinh env.
- Transaction cho source + chunks, backfill source cu chua co chunks, va chat
  turn atomic.
- Input limits cho pasted content, upload bytes, va chat question.
- Regression tests cho upgrade/backfill, ingestion rollback, short-query false
  positive, chat rollback, TXT/MD upload, va Unicode retrieval.

## Con lai

- PDF extraction chua lam va duoc de sau TXT/MD.
- Route van la async va goi service sync truc tiep. Da thu sync route va
  `run_in_threadpool`, nhung anyio threadpool bi treo trong ASGI test
  environment; se doi lai khi runtime/test harness on dinh.
- HTTP embedding provider chua duoc goi trong test tu dong vi can network/API
  key; default hash provider van la duong test offline.
- Can audit lai Phase 3 truoc khi nang trang thai len Done.

## Validation

```bash
.venv/bin/python -m pytest backend/tests
```

Ket qua: 7 passed.
