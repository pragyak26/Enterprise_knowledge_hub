from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import init_db
from app.routers import auth, chat, documents
from app.services.embeddings import ProviderNotConfigured


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Enterprise Knowledge Hub", version="0.1.0", lifespan=lifespan)

# Allow a future React dev server to call the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(ProviderNotConfigured)
async def provider_not_configured_handler(request: Request, exc: ProviderNotConfigured):
    return JSONResponse(status_code=503, content={"detail": str(exc)})


app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(chat.router)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
