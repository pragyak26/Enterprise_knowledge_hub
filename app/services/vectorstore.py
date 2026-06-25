"""ChromaDB wrapper. Stores chunk vectors with document/version metadata."""
from __future__ import annotations

import chromadb

from app.config import settings
from app.services.chunking import Chunk
from app.services.embeddings import embed_query, embed_texts

_client: chromadb.ClientAPI | None = None
COLLECTION = "documents"


def _collection():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(
            path=settings.chroma_dir,
            settings=chromadb.Settings(anonymized_telemetry=False),
        )
    return _client.get_or_create_collection(
        name=COLLECTION, metadata={"hnsw:space": "cosine"}
    )


def _chunk_id(version_id: int, index: int) -> str:
    return f"v{version_id}_c{index}"


def index_chunks(
    *, document_id: int, version_id: int, version_number: int, title: str, chunks: list[Chunk]
) -> None:
    if not chunks:
        return
    col = _collection()
    embeddings = embed_texts([c.text for c in chunks])
    col.add(
        ids=[_chunk_id(version_id, c.index) for c in chunks],
        embeddings=embeddings,
        documents=[c.text for c in chunks],
        metadatas=[
            {
                "document_id": document_id,
                "version_id": version_id,
                "version_number": version_number,
                "title": title,
                "page": c.page,
            }
            for c in chunks
        ],
    )


def delete_version(version_id: int, num_chunks: int) -> None:
    col = _collection()
    ids = [_chunk_id(version_id, i) for i in range(num_chunks)]
    if ids:
        col.delete(ids=ids)


def search(
    query: str,
    top_k: int,
    document_id: int | None = None,
    version_ids: list[int] | None = None,
) -> list[dict]:
    col = _collection()
    clauses: list[dict] = []
    if document_id is not None:
        clauses.append({"document_id": document_id})
    if version_ids is not None:
        clauses.append({"version_id": {"$in": version_ids}})
    if not clauses:
        where = None
    elif len(clauses) == 1:
        where = clauses[0]
    else:
        where = {"$and": clauses}
    results = col.query(
        query_embeddings=[embed_query(query)],
        n_results=top_k,
        where=where,
    )
    hits: list[dict] = []
    docs = results.get("documents") or [[]]
    metas = results.get("metadatas") or [[]]
    for text, meta in zip(docs[0], metas[0]):
        hits.append({"text": text, "metadata": meta})
    return hits
