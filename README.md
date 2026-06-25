# 📚 Enterprise Knowledge Hub

> Ask questions in natural language and get cited answers from your organization's documents — *Google Drive + document versioning + ChatGPT for company docs.*

![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-6-646CFF?logo=vite&logoColor=white)
![Gemini](https://img.shields.io/badge/Google-Gemini-4285F4?logo=google&logoColor=white)
![ChromaDB](https://img.shields.io/badge/Vector_DB-ChromaDB-FF6F61)

Companies have thousands of documents, but finding the right information is painful. Instead of opening PDFs and Word files one by one, users **ask a question** and get an **answer with source citations** — pulled straight from the company's own documents using Retrieval-Augmented Generation (RAG).

It also tracks **document versions**, so you can ask *"what changed between v1 and v2?"* and get an AI-generated diff.

---

## ✨ Features

- 🔐 **Authentication** — register/login with JWT-secured endpoints
- 📤 **Document upload** — PDF, DOCX, TXT, MD; text is extracted, chunked, embedded, and indexed automatically
- 🗂️ **Version management** — upload new versions of a document; each version is tracked and independently searchable
- 💬 **RAG chat with citations** — answers are generated **only** from your documents, every answer traceable to document, version, and page
- 🆕 **Latest-version-only search** — optionally ignore older versions when answering
- 🔀 **Version compare** — AI summary of what changed between any two versions
- 🔍 **Semantic search** — finds answers by meaning, not just keywords
- 🖥️ **React UI** — clean interface for all of the above

---

## 🧱 Tech stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + Vite |
| Backend | FastAPI (Python 3.13) |
| Database (metadata) | SQLAlchemy → SQLite (Postgres-ready) |
| Vector store | ChromaDB (on-disk, cosine) |
| Embeddings + LLM | Google Gemini (`gemini-embedding-001`, `gemini-2.5-flash`) |
| Auth | JWT (PyJWT) + bcrypt |
| File parsing | pypdf, python-docx |

---

## 🏗️ Architecture

```
            React UI (Vite)
                 │  /api/*  (dev proxy)
                 ▼
              FastAPI
        ┌────────┴─────────┐
        ▼                  ▼
  SQLAlchemy DB       File storage
  users, documents,   original PDFs/DOCX
  versions, metadata
        │
   Document Processor:  extract text → chunk → embed (Gemini)
        │
     ChromaDB  ◄── vector search
        │
   RAG: top-k chunks → prompt → Gemini → answer + citations
```

---

## 🚀 Getting started

### Prerequisites
- Python 3.13 (`pydantic-core`/`tokenizers` have no Python 3.14 wheels yet)
- Node.js 18+
- A free Google Gemini API key → https://aistudio.google.com/app/apikey

### 1. Backend

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edit .env: set GEMINI_API_KEY, and a SECRET_KEY:
#   python -c "import secrets; print(secrets.token_hex(32))"

uvicorn app.main:app --reload
```

Backend runs at **http://127.0.0.1:8000** — interactive API docs at **/docs**.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

UI runs at **http://localhost:5173** (it proxies `/api/*` to the backend — no CORS setup needed).

### 3. Try it

Generate sample documents and explore:

```bash
python scripts/make_sample_docs.py   # writes 4 demo docs to sample_docs/
```

Then in the UI: register an account → **Documents** tab to upload → **Ask** a question → **Compare** two versions.

---

## 📡 API reference

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/auth/register` | Create an account |
| POST | `/auth/login` | Get a JWT (OAuth2 form) |
| GET | `/auth/me` | Current user |
| POST | `/documents` | Upload a new document (v1) |
| POST | `/documents/{id}/versions` | Upload a new version |
| GET | `/documents` | List your documents + versions |
| GET | `/documents/{id}` | One document with its versions |
| DELETE | `/documents/{id}` | Delete document, files, and vectors |
| POST | `/ask` | RAG question → answer + citations |
| POST | `/compare` | LLM diff of two versions |
| GET | `/health` | Liveness |

**Ask** request body:
```json
{ "question": "How many maternity leave days are allowed?", "document_id": 1, "latest_only": true }
```
(`document_id` and `latest_only` are optional.)

---

## 🗄️ Switching to PostgreSQL

```bash
# in .env
DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/ekh
pip install "psycopg[binary]"
```
Tables are created automatically on startup.

---

## 🗺️ Roadmap

- ✅ **Phase 1:** auth, upload, view/list, semantic search
- ✅ **Phase 2:** RAG chatbot, citations, version compare, React UI
- ⏭️ **Next:** background/async indexing, streaming answers, org/team sharing, PDF page-accurate citations for DOCX

---

## 📁 Project structure

```
.
├── app/                  # FastAPI backend
│   ├── main.py           # app + routes wiring
│   ├── models.py         # SQLAlchemy ORM (User, Document, DocumentVersion)
│   ├── routers/          # auth, documents, chat
│   └── services/         # extract, chunking, embeddings, vectorstore, rag
├── frontend/             # React + Vite UI
│   └── src/components/    # Login, Documents, Chat, Compare
├── scripts/              # sample-doc generator, smoke test
└── requirements.txt
```

> **Note:** This is a learning/portfolio project. Secrets live in `.env` (gitignored) — never commit your API keys.
