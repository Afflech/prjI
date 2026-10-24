# Design - Mini NotebookLM

Ngay cap nhat: 2026-10-25
Trang thai: Phase 3/4 local MVP da Done voi SQLite, pasted/TXT/MD/PDF/PPTX
source ingestion, retrieval-preview chat, citations, chunk evidence API, va
frontend workspace 3 cot.

## 1. Product Goal

Mini NotebookLM giup sinh vien hoi dap tren tai lieu hoc tap cua minh. Moi cau
tra loi can dua tren source da them vao notebook va co citation de kiem chung.

## 2. Architecture Overview

Target app gom cac phan:

- Frontend React/Vite cho thao tac notebook, source, chat, va evidence panel.
  Phase 4 hien co workspace 3 cot cho local MVP.
- Backend FastAPI cung cap REST API. Phase 3 hien co `/health`, notebook,
  pasted source, TXT/MD/PDF/PPTX raw upload, chat, va evidence endpoints.
- SQLite luu notebooks, sources, chunks, messages.
- Ingestion pipeline hien chunk pasted/TXT/MD/PDF/PPTX text voi overlap, embed qua
  provider boundary, va luu metadata.
- Retrieval layer tim chunks lien quan trong enabled ready sources.
- LLM provider abstraction: mock truoc, Gemini sau.

Luon phan biet target design voi trang thai thuc te: Phase 3 co backend
retrieval/citation cho pasted text, TXT/MD, PDF, va PPTX; OCR chi la optional
fallback cho PDF scan khi local tool co san.

## 3. Backend Target

Backend se co cac nhom API chinh:

- Health: kiem tra service song.
- Notebooks: create, list, rename, delete.
- Sources: paste/upload, list, enable/disable, delete.
- Chat: nhan cau hoi theo notebook, retrieve context, tra answer va citations.
- Evidence: lay chunk goc theo citation.

SQLite target tables:

- `notebooks`: metadata notebook.
- `sources`: source title, type, status, enabled flag, error neu failed.
- `chunks`: source id, page neu co, text, embedding/vector id.
- `messages`: notebook id, role, content, citations JSON, created time.

## 4. Ingestion Target

Order trien khai:

1. Pasted text.
2. TXT/MD files.
3. PDF text extraction.
4. PPTX text extraction.

Chunking se co overlap de giam mat ngu canh. PDF citation can giu page number
neu extract duoc. PPTX MVP khong yeu cau slide number trong citation.

## 5. Retrieval Target

MVP dung provider abstraction: local hash embeddings la fallback offline cho
test/demo; HTTP embedding provider co the bat bang env khi can provider that.
Retrieval target:

- Chi retrieve chunks thuoc notebook dang chat.
- Chi retrieve sources co `enabled = true`.
- Bo qua source chua ready hoac failed.
- Dung Unicode tokenizer, token overlap gate va cosine stdlib hien tai;
  FAISS/NumPy co the them sau neu can.

Citation target gom chunk id, source id, source title, page neu co, va quote
ngan de UI hien evidence.

## 6. LLM Target

Phase dau dung mock/retrieval-preview provider:

- Khong can API key.
- Tra loi bang preview tu retrieved chunks.
- Van tra citations de kiem flow end-to-end.

Gemini provider them sau:

- Doc `LLM_PROVIDER`, `GEMINI_API_KEY`, `GEMINI_MODEL` tu env.
- Khong in API key ra log.
- Khong silently fallback ve mock neu user da chon Gemini nhung config sai.

## 7. Frontend Target

UI target gom 3 cot:

- Sources: notebooks va source list.
- Chat: message history, composer, loading/error state.
- Evidence: citation detail va chunk text.

Phase 4 da implement UI day du cho local MVP. Browser automation chua co.

## 8. Non-goals For Early MVP

- OCR mac dinh/bat buoc cho PDF scan; OCR chi optional fallback khi duoc cau hinh.
- DOCX ingestion.
- URL ingestion.
- Auth/user accounts.
- Production deployment.
- Study guide tu dong va saved notes.
