# Phases 1-3 Re-audit - Mini NotebookLM

Ngay: 2026-10-22
Baseline: bbd4c2e (Complete phase 3 retrieval backend)
Ket luan: Phase 1 pass; Phase 2 happy path pass voi failure-path gap;
Phase 3 can sua loi va doi chieu lai scope truoc khi xem la hoan tat.

## Pham vi va skills

- Hieu "3 phase dau tien" la Phase 1, 2, 3 theo ngu canh trien khai truoc do.
- Dung `code-reviewer` de kiem tra correctness, validation, persistence, tests.
- Dung `architect-review` de kiem tra layer boundaries, transaction ownership,
  upgrade path, va su nhat quan voi plan.
- Doi chieu `PROJECT_PLAN.md`, roadmap, design, README, va cac report Phase 1-3.
- Doc toan bo backend, hai backend tests, frontend skeleton va build config.
- Working tree co thay doi tu truoc trong `frontend/src/main.jsx`; da doc va
  build trang thai hien tai, khong sua hoac stage thay doi nay.
- Day la review/audit; khong sua code nghiep vu, khong commit.

## Findings

### F1 - P1: Source tu Phase 2 khong duoc index khi nang cap Phase 3

Vi tri: `backend/app/database.py:77`, `backend/app/services.py:125`.

Phase 2 luu source content va status ready nhung chua tao chunks. Startup hien
chi chay CREATE TABLE IF NOT EXISTS; chunking chi chay trong create_pasted cho
source moi. Tai lieu cu van xuat hien ready nhung khong bao gio duoc retrieve.
Khong co API reindex de phuc hoi tai lieu cu.

Tai hien: tao source bang SourceRepository (duong ghi cua Phase 2), chay lai
SCHEMA nhu startup, tim "AVL trees" tren content "AVL trees rotate to stay
balanced.". Ket qua: status=ready, chunks=0, hits=0.

De xuat: migration/backfill hoac reindex idempotent cho source cu. Giu nguyen
source ID va content; bao dam chay lai khong tao chunks trung. Can test upgrade
tu database Phase 2 that su, khong chi test database moi.

### F2 - P2: Ingestion loi nhung source van duoc commit la ready

Vi tri: `backend/app/repositories.py:78`, `backend/app/services.py:125`.

SourceRepository commit source voi status ready truoc khi service embed va
ghi chunks. Neu embedding hoac chunk insert loi, source da commit khong rollback
cung request va khong co failed/error update. Retry POST co the tao ban sao.

Tai hien: inject RuntimeError vao embed_text, goi create_pasted, doc lai source.
Ket qua: source van ton tai voi status="ready", error=null, khong co chunks.

De xuat: service so huu transaction cho source va chunks; chi danh dau ready
sau khi ingest thanh cong. Neu chu dong giu record that bai, can status failed
va error co y nghia, kem luong retry ro rang.

### F3 - P2: Cau hoi ngan bo qua lexical gate va cite tai lieu khong lien quan

Vi tri: `backend/app/services.py:28`, `backend/app/services.py:234`.

searchable_tokens bo token dai <=2. Khi query_tokens rong, dieu kien overlap
khong duoc ap dung, nhung embedding van dung nhung token do. Hash 64 chieu co
the collision voi tu bat ky va tao cosine score duong, duoc xem la evidence.

Tai hien: source="We study art in an old museum.", query="AI".
Ket qua: query_tokens=[], source khong lien quan van duoc retrieve voi
score=0.3779644730092272 va tro thanh citation khi chat.

De xuat: xu ly keyword ngan nhu AI/ML va query khong co searchable token mot
cach nhat quan; khong coi hash collision la bang chung lien quan. Them negative
retrieval test cho query ngan va nhieu source khac chu de.

### F4 - P2: Chat loi de lai user message thieu assistant response

Vi tri: `backend/app/services.py:176`, `backend/app/repositories.py:222`.

User message duoc commit truoc retrieval va assistant message. Neu retrieval
hoac assistant insert that bai, request loi nhung history van giu message le.
Schema hien tai khong co trang thai failed/pending de client phan biet; retry
request co the ghi lap cau hoi.

Tai hien: inject RuntimeError vao RetrievalService.search, goi ChatService.answer,
doc history. Ket qua: chi mot message role=user, khong co assistant message.

De xuat: voi API chat dong bo hien tai, persist ca cap messages trong mot
transaction sau khi co answer, hoac thiet ke explicit failed-turn state neu can
giu cau hoi that bai. Them failure-path test.

### F5 - P2: Phase 3 Done chua phan anh du scope ingestion trong plan

Vi tri: `PROJECT_PLAN.md:133`, `PROJECT_PLAN.md:141`, `backend/app/api.py:76`.

Plan yeu cau "Ho tro pasted text/TXT/MD truoc". API hien chi nhan JSON title va
content, va source type luon la pasted_text; khong co file ingestion endpoint
hay extraction. Dat title Trees.md khong kiem chung ho tro upload MD. Report
Phase 3 co ghi viec nay de sau, nhung source-of-truth plan chua doi scope.

De xuat: hoan tat ingestion TXT/MD va cac tests tuong ung, hoac cap nhat plan
va roadmap de chot scope pasted-text-only va chi ro phase nhan phan con lai.
Ba acceptance bullets hien tai pass voi pasted text; dieu do chua chung minh
toan bo danh sach cong viec Phase 3 da hoan tat.

## Verification

- `.venv/bin/python -m pytest backend/tests`: 2 passed.
- `npm run build` trong frontend: pass.
- `.venv/bin/python -m pip check`: no broken requirements.
- `git diff --check`: pass truoc khi ghi bao cao.
- Uvicorn startup voi database tam, GET /health: HTTP 200, {"status":"ok"}.
- Vite dev server startup tren port tam, GET /: HTTP 200 va HTML tham chieu
  /src/main.jsx. Ca hai server da duoc dung sau khi kiem tra.
- ASGI probes voi database in-memory: blank title/question va empty source PATCH
  tra 422; missing notebook/chunk tra 404; notebook isolation pass; delete
  notebook cascade sources/chunks/messages va evidence sau delete tra 404.
- Fault injection va targeted probes da tai hien F1-F4. Khong dung database
  nguoi dung, khong goi dich vu ngoai.

## Gioi han va rui ro con lai

- Hai smoke tests hien co chua bao phu upgrade, rollback, ranking giua nhieu
  chunks, overlap boundary, source rename trong citations, va false positives.
- Tokenizer `[a-z0-9]+` tach mat chu co dau/non-Latin. Vi du searchable_tokens
  cua "Do thi" co dau (U+0110 U+1ED3 / th U+1ECB) tra set rong. Can chot yeu cau
  ngon ngu va test Unicode; khong xem hash embedding hien tai la semantic search.
- SQLite va retrieval dong bo chay trong async routes. Input content/question
  chua co upper bound; can xem lai truoc khi tang kich thuoc tai lieu hoac tai.
- Khong chay browser automation cho UI Phase 4, benchmark retrieval, hay kiem
  tra CVE qua registry. Pip check chi kiem tra dependency compatibility.

## Danh gia theo phase

- Phase 1: dat acceptance skeleton, health, dev/build trong moi truong hien tai.
- Phase 2: CRUD/source/chat/history happy path dat; F4 can khac phuc cho failure
  consistency khi ket hop retrieval Phase 3.
- Phase 3: pasted-text happy path, citation/evidence va disabled-source filter
  pass, nhung F1-F3 va scope F5 chua cho phep ket luan audit sach.
- Bao cao nay bo sung va dieu chinh ket luan "Pass, co the chuyen sang Phase 4"
  trong reports/phase-3-audit.md; bao cao cu giu lai nhu lich su.
