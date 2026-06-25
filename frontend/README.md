# Knowledge Hub — Frontend

React + Vite UI for the Enterprise Knowledge Hub. Covers login/register,
document upload & versioning, the RAG "Ask" chat with citations, and the
version-compare view.

## Prerequisites

The backend must be running on http://127.0.0.1:8000:

```bash
cd ..                       # project root
source .venv/bin/activate
uvicorn app.main:app --reload
```

## Run the UI

```bash
npm install      # first time only
npm run dev
```

Open **http://localhost:5173**.

In dev, Vite proxies every `/api/*` request to the backend (see
`vite.config.js`), so there are no CORS issues and no base-URL config needed.

## Structure

```
src/
  api.js                 # fetch wrapper; stores the JWT in localStorage
  App.jsx                # auth gate + tab navigation
  components/
    Login.jsx            # login / register
    Documents.jsx        # upload, list, add version, delete
    Chat.jsx             # ask questions, render answer + citations
    Compare.jsx          # diff two versions of a document
  styles.css
```

## Production build

```bash
npm run build            # outputs to dist/
```

Serve `dist/` behind any static host. Point it at the API by replacing the dev
proxy with a real base URL in `src/api.js` (the `BASE` constant).
