"""RAG orchestration: answer questions and compare document versions."""
from __future__ import annotations

from app.config import settings
from app.schemas import Citation
from app.services import embeddings, vectorstore

NO_ANSWER = "NO_ANSWER"
NO_ANSWER_MESSAGE = "I couldn't find that in the documents."

ANSWER_PROMPT = """You are an assistant for an enterprise knowledge base.
Use ONLY the context below to answer. Each context block is labeled with its
source document and version, e.g. [Leave Policy v2, page 1].

Rules:
- Be concise and factual.
- The SAME fact may appear with different values across versions. If the
  versions differ, report each version's value and name the version
  (e.g. "120 days in v1, 180 days in v2").
- Cite the source document and version in your answer.
- Only if the answer is genuinely absent from every context block, reply with
  exactly: {no_answer}

Context:
{context}

Question: {question}

Answer:"""

COMPARE_PROMPT = """You are comparing two versions of the same company document
titled "{title}".

--- VERSION {va} ---
{text_a}

--- VERSION {vb} ---
{text_b}

List the meaningful changes from version {va} to version {vb} as concise bullet
points (additions, removals, and modifications). Ignore formatting-only changes."""


def answer_question(
    question: str,
    top_k: int | None = None,
    document_id: int | None = None,
    version_ids: list[int] | None = None,
) -> tuple[str, list[Citation]]:
    top_k = top_k or settings.top_k
    # An explicit empty version filter means "nothing to search".
    if version_ids is not None and len(version_ids) == 0:
        return NO_ANSWER_MESSAGE, []
    hits = vectorstore.search(
        question, top_k=top_k, document_id=document_id, version_ids=version_ids
    )
    if not hits:
        return NO_ANSWER_MESSAGE, []

    context_blocks = []
    citations: list[Citation] = []
    for hit in hits:
        meta = hit["metadata"]
        page = meta.get("page")
        label = f"[{meta.get('title')} v{meta.get('version_number')}, page {page}]"
        context_blocks.append(f"{label}\n{hit['text']}")
        citations.append(
            Citation(
                document_id=int(meta["document_id"]),
                document_title=str(meta.get("title")),
                version_number=int(meta.get("version_number")),
                page=int(page) if page is not None else None,
                snippet=hit["text"][:240],
            )
        )

    prompt = ANSWER_PROMPT.format(
        context="\n\n".join(context_blocks),
        question=question,
        no_answer=NO_ANSWER,
    )
    answer = embeddings.generate(prompt)
    if answer.strip().upper().startswith(NO_ANSWER):
        return NO_ANSWER_MESSAGE, []
    return answer, citations


def compare_versions(
    title: str, version_a: int, text_a: str, version_b: int, text_b: str
) -> str:
    # Cap text to keep the prompt within model limits.
    cap = 12000
    prompt = COMPARE_PROMPT.format(
        title=title,
        va=version_a,
        vb=version_b,
        text_a=text_a[:cap],
        text_b=text_b[:cap],
    )
    return embeddings.generate(prompt)
