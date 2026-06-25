from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


# ---- Auth ----
class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---- Documents ----
class VersionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    version_number: int
    original_filename: str
    file_type: str
    num_chunks: int
    created_at: datetime


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    created_at: datetime
    versions: list[VersionOut] = []


# ---- Chat / RAG ----
class AskRequest(BaseModel):
    question: str
    top_k: int | None = None
    document_id: int | None = None  # restrict search to one document
    latest_only: bool = False  # only search each document's newest version


class Citation(BaseModel):
    document_id: int
    document_title: str
    version_number: int
    page: int | None = None
    snippet: str


class AskResponse(BaseModel):
    answer: str
    citations: list[Citation]


class CompareRequest(BaseModel):
    document_id: int
    version_a: int
    version_b: int


class CompareResponse(BaseModel):
    document_title: str
    version_a: int
    version_b: int
    summary: str
