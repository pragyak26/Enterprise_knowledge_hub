"""Offline smoke test: imports, DB init, extraction, chunking. No API key needed.

Run:  python scripts/smoke_test.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def main() -> int:
    # 1. App + service imports
    from app.main import app  # noqa: F401
    from app.database import init_db
    from app.services.chunking import chunk_pages
    from app.services.extract import Page

    # 2. Tables create cleanly
    init_db()

    # 3. Chunking works on a synthetic 2-page doc
    pages = [Page(1, "leave policy " * 200), Page(2, "maternity " * 200)]
    chunks = chunk_pages(pages, size=300, overlap=50)
    assert chunks, "expected chunks"
    assert all(c.page in (1, 2) for c in chunks)

    print(f"OK: app imports, DB initialized, {len(chunks)} chunks produced.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
