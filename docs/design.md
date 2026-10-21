# Design - Mini NotebookLM

Ngay cap nhat: 2026-10-21
Trang thai: Phase 2 da co backend core voi SQLite va mock chat; ingestion,
retrieval citation, va frontend MVP van la target design cho phase sau.

## 1. Product Goal

Mini NotebookLM giup sinh vien hoi dap tren tai lieu hoc tap cua minh. Moi cau
tra loi can dua tren source da them vao notebook va co citation de kiem chung.

## 2. Architecture Overview

Target app gom cac phan:

- Frontend React/Vite cho thao tac notebook, source, chat, va evidence panel.
  Phase 1 hien co app shell toi thieu.
- Backend FastAPI cung cap REST API. Phase 2 hien co `/health`, notebook,
  pasted source, va mock chat endpoints.
- SQLite luu notebooks, sources, chunks, messages. Phase 2 da tao schema.
- Ingestion pipeline extract text, chunk, embed, va luu metadata.
- Retrieval layer tim chunks lien quan trong enabled sources.
- LLM provider abstraction: mock truoc, Gemini sau.

Luon phan biet target design voi trang thai thuc te: Phase 2 co backend
notebook/source/chat mock, chua co ingestion/retrieval citation that.

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

Chunking se co overlap de giam mat ngu canh. PDF citation can giu page number
neu extract duoc.

## 5. Retrieval Target

MVP dung local hash embeddings de co demo offline. Retrieval target:

- Chi retrieve chunks thuoc notebook dang chat.
- Chi retrieve sources co `enabled = true`.
- Bo qua source chua ready hoac failed.
- Dung FAISS neu co san, fallback NumPy cosine.

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

Phase 4 moi implement UI day du. Phase 1 chi can app shell toi thieu.

## 8. Non-goals For Early MVP

- OCR cho PDF scan.
- DOCX ingestion.
- URL ingestion.
- Auth/user accounts.
- Production deployment.
- Study guide tu dong va saved notes.
