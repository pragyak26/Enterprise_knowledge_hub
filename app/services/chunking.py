"""Split page text into overlapping chunks, preserving the source page number."""
from __future__ import annotations

from app.config import settings
from app.services.extract import Page


class Chunk:
    def __init__(self, text: str, page: int, index: int):
        self.text = text
        self.page = page
        self.index = index


def _split_text(text: str, size: int, overlap: int) -> list[str]:
    text = " ".join(text.split())  # normalize whitespace
    if len(text) <= size:
        return [text] if text else []
    chunks: list[str] = []
    start = 0
    step = max(size - overlap, 1)
    while start < len(text):
        chunks.append(text[start : start + size])
        start += step
    return chunks


def chunk_pages(
    pages: list[Page],
    size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    size = size or settings.chunk_size
    overlap = overlap or settings.chunk_overlap
    chunks: list[Chunk] = []
    idx = 0
    for page in pages:
        for piece in _split_text(page.text, size, overlap):
            chunks.append(Chunk(piece, page.number, idx))
            idx += 1
    return chunks
