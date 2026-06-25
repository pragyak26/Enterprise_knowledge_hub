import os
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.deps import get_current_user
from app.models import Document, DocumentVersion, User
from app.schemas import DocumentOut
from app.services import vectorstore
from app.services.chunking import chunk_pages
from app.services.extract import extract_pages, full_text

router = APIRouter(prefix="/documents", tags=["documents"])

SUPPORTED = {"pdf", "docx", "doc", "txt", "md"}


def _save_upload(file: UploadFile) -> tuple[str, str]:
    ext = (file.filename or "").rsplit(".", 1)[-1].lower()
    if ext not in SUPPORTED:
        raise HTTPException(400, f"Unsupported file type '.{ext}'")
    os.makedirs(settings.storage_dir, exist_ok=True)
    stored_path = os.path.join(settings.storage_dir, f"{uuid.uuid4().hex}.{ext}")
    with open(stored_path, "wb") as f:
        f.write(file.file.read())
    return stored_path, ext


def _process_version(version: DocumentVersion, document: Document) -> None:
    """Extract text, chunk, and index into the vector store."""
    pages = extract_pages(version.stored_path, version.file_type)
    chunks = chunk_pages(pages)
    version.extracted_text = full_text(pages)
    version.num_chunks = len(chunks)
    vectorstore.index_chunks(
        document_id=document.id,
        version_id=version.id,
        version_number=version.version_number,
        title=document.title,
        chunks=chunks,
    )


@router.post("", response_model=DocumentOut, status_code=201)
def upload_document(
    file: UploadFile = File(...),
    title: str | None = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new document from an uploaded file (its first version)."""
    stored_path, ext = _save_upload(file)
    document = Document(
        owner_id=current_user.id,
        title=title or (file.filename or "Untitled"),
    )
    db.add(document)
    db.flush()  # assign document.id

    version = DocumentVersion(
        document_id=document.id,
        version_number=1,
        original_filename=file.filename or "upload",
        file_type=ext,
        stored_path=stored_path,
    )
    db.add(version)
    db.flush()  # assign version.id

    _process_version(version, document)
    db.commit()
    db.refresh(document)
    return document


@router.post("/{document_id}/versions", response_model=DocumentOut, status_code=201)
def upload_version(
    document_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a new version of an existing document."""
    document = _get_owned_document(db, document_id, current_user)
    next_number = max((v.version_number for v in document.versions), default=0) + 1
    stored_path, ext = _save_upload(file)

    version = DocumentVersion(
        document_id=document.id,
        version_number=next_number,
        original_filename=file.filename or "upload",
        file_type=ext,
        stored_path=stored_path,
    )
    db.add(version)
    db.flush()

    _process_version(version, document)
    db.commit()
    db.refresh(document)
    return document


@router.get("", response_model=list[DocumentOut])
def list_documents(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return (
        db.query(Document).filter(Document.owner_id == current_user.id).all()
    )


@router.get("/{document_id}", response_model=DocumentOut)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _get_owned_document(db, document_id, current_user)


@router.delete("/{document_id}", status_code=204)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = _get_owned_document(db, document_id, current_user)
    for v in document.versions:
        vectorstore.delete_version(v.id, v.num_chunks)
        if os.path.exists(v.stored_path):
            os.remove(v.stored_path)
    db.delete(document)
    db.commit()


def _get_owned_document(
    db: Session, document_id: int, user: User
) -> Document:
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document or document.owner_id != user.id:
        raise HTTPException(404, "Document not found")
    return document
