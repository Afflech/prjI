# Project Plan - Mini NotebookLM

Ngay cap nhat: 2026-10-28

Tai lieu nay la source of truth cho viec trien khai Mini NotebookLM tu dau.
Truoc moi dot code, update tien do, hoac audit, can doc file nay truoc de nam
scope, phase hien tai, va cac quy uoc da chot.

## 1. Muc tieu

Mini NotebookLM la web app phuc vu hoc tap theo mo hinh source-grounded Q&A:

- User tao notebook theo mon hoc/chu de.
- User them PDF/TXT/MD hoac pasted text sources vao notebook.
- He thong tach tai lieu thanh chunks, lap chi muc retrieval, va chat dua tren
  enabled sources.
- Moi cau tra loi can co citation tro ve source/chunk/page neu co.
- MVP uu tien chay on dinh local truoc, Docker/Gemini/evaluation lam sau theo
  phase.

## 2. Quyet dinh da chot

- Xem repo hien tai la du an moi hoan toan.
- Bat dau bang tai lieu va skeleton nho, khong gia dinh backend/frontend/scripts
  da ton tai.
- LLM phase dau la mock/retrieval-preview provider de demo offline.
- Gemini provider se duoc them sau khi backend, ingestion, retrieval, va UI MVP
  da on dinh.
- Scope MVP gom notebook, source, ingestion co ban, retrieval, chat, citation,
  va evidence panel.
- De ngoai MVP dau: DOCX, URL ingestion, saved notes, study guide tu dong,
  auth, deployment production. OCR chi la optional fallback cho PDF scan khi
  local tool duoc cau hinh.

## 3. README target

Khi tao `README.md`, noi dung can phan anh dung trang thai repo tai thoi diem do.
Khong viet huong dan chay script/path chua duoc tao.

Noi dung README target:

- Ten du an: Mini NotebookLM.
- Mo ta ngan: Project I web app cho source-grounded study Q&A.
- Stack target:
  - Backend: FastAPI, SQLite, local hash embeddings cho MVP, HTTP embedding
    provider abstraction.
  - Frontend: React + Vite.
  - Retrieval: chunking with overlap, FAISS khi co san, NumPy cosine fallback.
- Run target sau khi co code:
  - Manual backend bang virtualenv va `uvicorn app.main:app --reload --port 8000`.
  - Manual frontend bang `npm install` va `npm run dev`.
  - Docker scripts chi dua vao README sau khi cac file trong `scripts/` that su
    ton tai.
- MVP features target:
  - Create, rename, delete notebooks.
  - Upload TXT/MD/PDF/PPTX va paste text sources.
  - Background ingestion voi text extraction, chunking, embeddings, vector
    storage.
  - Enable/disable individual sources truoc khi chat.
  - Chat history per notebook.
  - Citation detail endpoint va UI evidence panel.
  - Source summary/suggested questions chi de dang hook, khong bat buoc trong
    MVP dau.

## 4. Phase plan

### Phase 0 - Project docs baseline

Muc tieu:

- Tao nen tang tai lieu dung voi mot repo moi.

Viec can lam:

- Tao `README.md` ban dau: muc tieu, stack target, trang thai hien tai, cach chay
  khi code chua co.
- Tao `docs/design.md`: kien truc backend/frontend/database/ingestion/retrieval/
  LLM provider.
- Tao `docs/project-roadmap.md`: phase plan va acceptance theo phase.
- Tao `docs/mvp-smoke-test.md`: checklist se dung sau khi co app.
- Tao report baseline trong `reports/`, khong ghi viec chua lam la da xong.

Acceptance:

- Tai lieu nhat quan rang day la du an moi.
- Khong co run command gay hieu nham la app da chay duoc.
- Nguoi doc biet viec tiep theo la Phase 1 skeleton.

### Phase 1 - Runnable skeleton

Trang thai: Done.

Muc tieu:

- Tao app toi thieu co the chay local.

Viec can lam:

- Tao cau truc `backend/`, `frontend/`, `docs/`, `eval/`, `demo_sources/`,
  `scripts/`.
- Backend FastAPI co endpoint `/health`.
- Frontend React/Vite co app shell toi thieu.
- Them huong dan chay manual trong README sau khi skeleton chay duoc.

Acceptance:

- Backend `/health` tra OK.
- Frontend dev/build chay duoc.
- Chua can notebook, ingestion, retrieval, hay chat.

### Phase 2 - Backend core

Trang thai: Done.

Muc tieu:

- Co API va database cho flow notebook/source/chat mock.

Viec can lam:

- SQLite schema cho notebooks, sources, chunks, messages.
- API notebook: create, list, rename, delete.
- API source: paste text, list, enable/disable, delete.
- API chat: nhan cau hoi, tra mock answer, luu history.
- Smoke test backend core.

Acceptance:

- Tao notebook -> them pasted source -> chat mock -> doc history thanh cong.
- Source co status va enabled flag de dung cho phase retrieval.

### Phase 3 - Ingestion va retrieval

Trang thai: Done.

Muc tieu:

- Co retrieval co citation dua tren pasted text va file da ingest.

Viec can lam:

- Ho tro pasted text va TXT/MD/PDF/PPTX upload.
- PDF text extraction voi page metadata neu co.
- PPTX text extraction khong yeu cau slide citation metadata.
- OCR optional fallback cho PDF scan khi `OCR_ENABLED=1` va dependency local co
  san.
- Chunking co overlap va metadata source/page neu co.
- Unicode tokenizer cho tieng Viet va text khong phai ASCII.
- Embedding provider interface: local hash fallback offline va HTTP provider
  that khi duoc cau hinh.
- API citation/evidence tra chunk goc.

Acceptance:

- Hoi cau lien quan den source thi retrieve duoc chunk phu hop.
- Citation co chunk id, source id, source title, page neu co.
- Disabled source khong duoc retrieve/cite.
- Upload TXT/MD/PDF/PPTX tao source ready va retrieve duoc noi dung Unicode.

### Phase 4 - Frontend MVP

Trang thai: Done.

Muc tieu:

- Co UI demo flow chinh end-to-end.

Viec can lam:

- Layout 3 cot: sources, chat, evidence.
- Tao/chon/doi ten/xoa notebook.
- Paste/upload source theo kha nang backend da co.
- Enable/disable/delete source.
- Chat voi citation chips va evidence panel.
- Playwright browser automation cho flow notebook -> source -> chat -> citation
  -> evidence va source enable/disable.

Acceptance:

- Browser flow notebook -> source -> chat -> citation -> evidence chay duoc;
  co automated E2E coverage cho flow chinh.
- UI co loading/error state co ban va responsive toi thieu.

Tien do 2026-10-25:

- Da thay placeholder frontend bang UI 3 cot sources/chat/evidence.
- Da noi frontend vao API notebooks, sources, upload TXT/MD/PDF/PPTX, chat,
  messages, va chunk evidence.
- Da them Vite dev proxy `/api` va `/health` sang backend local port 8000.
- Da audit va sua UX/state cho no-citation message, evidence loading/error,
  page metadata TXT/MD, composer layout, va reload khong can thiet.
- `.venv/bin/python -m pytest backend/tests`, `npm run build`, va
  `git diff --check` deu pass.
- Smoke API da pass cho TXT/MD/PDF/PPTX -> chat -> citation -> evidence.
- Chap nhan known limitations: retrieval hash con tho, OCR optional fallback
  ngoai base MVP.

Tien do 2026-10-28:

- Da them Playwright E2E cho tao notebook, paste source, chat, mo citation/evidence,
  va xac nhan source disabled khong con duoc cite.
- Playwright config tu khoi dong backend va Vite tren port rieng, dung SQLite
  file rieng trong system temp, va xoa database sau run.
- Playwright dependency da duoc cai tu cache; chua chay E2E vi Chromium chua co
  san va moi truong khong tai duoc browser binary.

### Phase 5 - Docker va Gemini

Muc tieu:

- Dong goi app de demo de hon va them LLM provider that.

Viec can lam:

- Dockerfile/Compose cho backend/frontend.
- Scripts Docker sau khi Compose on dinh: `scripts/docker-up.sh`,
  `scripts/docker-down.sh`, optional `scripts/docker-desktop-up.sh`.
- Gemini provider doc `LLM_PROVIDER`, `GEMINI_API_KEY`, `GEMINI_MODEL`.
- Khong silently fallback ve mock khi user da chon Gemini nhung config sai.

Acceptance:

- Docker stack len healthy voi mock provider.
- Gemini dependency/config duoc verify khi bat Gemini.
- Chat Gemini that chi test khi duoc phep gui noi dung test ra dich vu ngoai.

### Phase 6 - Evaluation va demo release

Muc tieu:

- Co bang chung chat luong retrieval va demo reproducible.

Viec can lam:

- Tao demo sources.
- Tao bo 20-30 cau hoi evaluation.
- Gan expected source/page/evidence cho tung cau.
- Viet script do top-k hit rate.
- Viet/chup tai lieu demo neu can nop.

Acceptance:

- Co bao cao evaluation co so lieu.
- Co checklist demo local/Docker.
- Co danh sach viec con ton dong truoc release.

## 5. Quy uoc update va audit

Moi lan cap nhat tien do:

- Doc `PROJECT_PLAN.md` truoc.
- Ghi phase dang lam.
- Ghi viec da xong, dang lam, bi chan.
- Ghi acceptance nao da dat/chua dat.
- Neu co bao cao moi, dat trong `reports/`.

Moi lan audit:

- Doi chieu repo hien tai voi phase plan trong file nay.
- Phan biet ro "target trong plan" voi "file/code da ton tai".
- Khong ghi mot tinh nang la Done neu chua co file/code/test tuong ung.
- Neu scope thay doi, cap nhat `PROJECT_PLAN.md` truoc hoac cung luc voi bao
  cao audit.

Quy uoc trang thai:

- Planned: chua bat dau.
- In progress: dang lam, chua dat het acceptance.
- Done: da dat acceptance cua phase.
- Blocked: bi chan boi thong tin, dependency, approval, hoac loi moi truong.

## 6. Test plan tong quat

- Phase 0: doc review, dam bao tai lieu khong gia dinh code da ton tai.
- Phase 1: backend `/health` OK, frontend build/dev OK.
- Phase 2: backend smoke test notebook/source/chat mock.
- Phase 3: retrieval/citation smoke test, TXT/MD/PDF/PPTX upload, Unicode
  retrieval, va regression tests cho failure paths.
- Phase 4: manual browser checklist and Playwright E2E for notebook/source/chat/
  citation/evidence and disabled-source behavior.
- Phase 5: Docker healthcheck va Gemini config check.
- Phase 6: evaluation top-k hit rate va demo checklist.

## 7. Assumptions

- Repo bat dau tu trang thai moi, khong co backend/frontend/scripts/docs that
  ngoai cac file plan hien tai.
- Security co ban: khong commit `.env`, khong log API key, khong in secret trong
  bao cao.
- Uu tien MVP co citation hon tinh nang phu.
