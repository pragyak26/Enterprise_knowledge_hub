# Enterprise Knowledge Hub

Ask questions in natural language and get answers from your organization's
documents — *Google Drive + document versioning + ChatGPT for company docs.*

This repo is the **Phase 1 + RAG-core backend**: a FastAPI service with auth,
document upload & versioning, text extraction, chunking, Gemini embeddings,
ChromaDB vector search, a `/ask` RAG endpoint with citations, and a `/compare`
endpoint that diffs two document versions with the LLM.

## Architecture

```
HTTP client (curl / Swagger / future React UI)
        |
     FastAPI  ──────────────┐
        |                    |
  SQLAlchemy (SQLite/PG)   File storage (./storage)
   users, documents,         original PDFs/DOCX
   versions, metadata
        |
  Document Processor:  extract text -> chunk -> embed (Gemini)
        |
     ChromaDB (./data/chroma)  <-- vector search
        |
   RAG: top-k chunks -> prompt -> Gemini -> answer + citations
```

## Setup

```bash
cd "Enterprise Knowledge Hub"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edit .env: set GEMINI_API_KEY and a random SECRET_KEY
```

Get a Gemini API key at https://aistudio.google.com/app/apikey (free tier works).

## Run

```bash
uvicorn app.main:app --reload
```

Open the interactive docs at http://127.0.0.1:8000/docs

## Quick walkthrough (curl)

```bash
BASE=http://127.0.0.1:8000

# 1. Register + log in
curl -s -X POST $BASE/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"me@corp.com","password":"secret123"}'

TOKEN=$(curl -s -X POST $BASE/auth/login \
  -d 'username=me@corp.com&password=secret123' | python3 -c 'import sys,json;print(json.load(sys.stdin)["access_token"])')

# 2. Upload a document (its first version)
curl -s -X POST $BASE/documents \
  -H "Authorization: Bearer $TOKEN" \
  -F 'file=@LeavePolicy_v1.pdf' -F 'title=Leave Policy'

# 3. Upload a newer version of document #1
curl -s -X POST $BASE/documents/1/versions \
  -H "Authorization: Bearer $TOKEN" \
  -F 'file=@LeavePolicy_v2.pdf'

# 4. Ask a question (RAG + citations)
curl -s -X POST $BASE/ask \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"question":"How many maternity leave days are allowed?"}'

# 5. Compare two versions
curl -s -X POST $BASE/compare \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"document_id":1,"version_a":1,"version_b":2}'
```

## API summary

| Method | Path                          | Purpose                              |
|--------|-------------------------------|--------------------------------------|
| POST   | `/auth/register`              | Create an account                    |
| POST   | `/auth/login`                 | Get a JWT (OAuth2 form)              |
| GET    | `/auth/me`                    | Current user                         |
| POST   | `/documents`                  | Upload a new document (v1)            |
| POST   | `/documents/{id}/versions`    | Upload a new version                 |
| GET    | `/documents`                  | List your documents + versions       |
| GET    | `/documents/{id}`             | One document with its versions        |
| DELETE | `/documents/{id}`             | Delete document, files, and vectors  |
| POST   | `/ask`                        | RAG question -> answer + citations   |
| POST   | `/compare`                    | LLM diff of two versions             |
| GET    | `/health`                     | Liveness                             |

Supported file types: PDF, DOCX, TXT, MD.

## Switching to PostgreSQL

Set in `.env`:
```
DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/ekh
```
and `pip install "psycopg[binary]"`. Tables are created automatically on startup.

## Roadmap

- **Phase 1 (done):** auth, upload, view/list, semantic search
- **Phase 2 (done):** RAG chatbot, citations, version compare
- **Next:** React UI, latest-version-only filtering, async/background indexing,
  org/team sharing, streaming answers.
```
