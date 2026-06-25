from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Document, DocumentVersion, User
from app.schemas import (
    AskRequest,
    AskResponse,
    CompareRequest,
    CompareResponse,
)
from app.services import rag

router = APIRouter(tags=["chat"])


@router.post("/ask", response_model=AskResponse)
def ask(
    payload: AskRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.document_id is not None:
        _assert_owned(db, payload.document_id, current_user)

    version_ids = None
    if payload.latest_only:
        version_ids = _latest_version_ids(db, current_user, payload.document_id)

    answer, citations = rag.answer_question(
        payload.question,
        top_k=payload.top_k,
        document_id=payload.document_id,
        version_ids=version_ids,
    )
    return AskResponse(answer=answer, citations=citations)


def _latest_version_ids(
    db: Session, user: User, document_id: int | None
) -> list[int]:
    """The version id of each document's highest version_number (scoped to one
    document if document_id is given)."""
    query = db.query(Document).filter(Document.owner_id == user.id)
    if document_id is not None:
        query = query.filter(Document.id == document_id)
    ids: list[int] = []
    for doc in query.all():
        if doc.versions:
            latest = max(doc.versions, key=lambda v: v.version_number)
            ids.append(latest.id)
    return ids


@router.post("/compare", response_model=CompareResponse)
def compare(
    payload: CompareRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = _assert_owned(db, payload.document_id, current_user)
    va = _get_version(db, document.id, payload.version_a)
    vb = _get_version(db, document.id, payload.version_b)
    summary = rag.compare_versions(
        title=document.title,
        version_a=va.version_number,
        text_a=va.extracted_text,
        version_b=vb.version_number,
        text_b=vb.extracted_text,
    )
    return CompareResponse(
        document_title=document.title,
        version_a=va.version_number,
        version_b=vb.version_number,
        summary=summary,
    )


def _assert_owned(db: Session, document_id: int, user: User) -> Document:
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document or document.owner_id != user.id:
        raise HTTPException(404, "Document not found")
    return document


def _get_version(db: Session, document_id: int, number: int) -> DocumentVersion:
    version = (
        db.query(DocumentVersion)
        .filter(
            DocumentVersion.document_id == document_id,
            DocumentVersion.version_number == number,
        )
        .first()
    )
    if not version:
        raise HTTPException(404, f"Version {number} not found")
    return version
