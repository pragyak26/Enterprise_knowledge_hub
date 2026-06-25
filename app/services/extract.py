"""Extract text from uploaded files, keeping page numbers where available."""
from __future__ import annotations

from docx import Document as DocxDocument
from pypdf import PdfReader


class Page:
    def __init__(self, number: int, text: str):
        self.number = number
        self.text = text


def extract_pages(path: str, file_type: str) -> list[Page]:
    file_type = file_type.lower()
    if file_type == "pdf":
        return _extract_pdf(path)
    if file_type in ("docx", "doc"):
        return _extract_docx(path)
    if file_type in ("txt", "md"):
        return _extract_txt(path)
    raise ValueError(f"Unsupported file type: {file_type}")


def _extract_pdf(path: str) -> list[Page]:
    reader = PdfReader(path)
    pages: list[Page] = []
    for i, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            pages.append(Page(i, text))
    return pages


def _extract_docx(path: str) -> list[Page]:
    doc = DocxDocument(path)
    text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    # python-docx has no page concept; treat the whole doc as one page.
    return [Page(1, text)] if text.strip() else []


def _extract_txt(path: str) -> list[Page]:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    return [Page(1, text)] if text.strip() else []


def full_text(pages: list[Page]) -> str:
    return "\n\n".join(p.text for p in pages)
