import re
import os
PDF_URL_RE = re.compile(r"\.pdf($|[?#])", re.IGNORECASE)
import re
import re
from typing import List, Tuple
from pathlib import Path
from urllib.parse import urlparse
import requests

def _unique_sources(source_documents) -> List[Tuple[str, str]]:
    seen = set()
    ordered = []
    for d in source_documents or []:
        src = d.metadata.get("source") or d.metadata.get("url") or "unknown"
        page = d.metadata.get("page") or d.metadata.get("pdf_page") or None
        key = (src, page)
        if src and key not in seen:
            ordered.append(key)
            seen.add(key)
    return ordered

def format_citations(source_documents) -> str:
    pairs = _unique_sources(source_documents)
    if not pairs:
        return ""
    lines = ["Sources:"]
    for src, page in pairs:
        suffix = f" (page {page})" if page is not None else ""
        lines.append(f"- {src}{suffix}")
    return "\n".join(lines)

def attach_citations(answer: str, source_documents) -> str:
    tail = format_citations(source_documents)
    if not tail:
        return answer
    return f"{answer}\n\n{tail}"

def download_pdf(url: str, out_dir: str = None, filename: str | None = None, timeout: int = 30) -> str:
    r"""
    Download a PDF to data\raw\ (Windows-friendly).
    - Auto-creates the folder
    - Derives a safe filename from the URL (or use `filename`)
    - Warns if response doesn't look like a PDF
    - De-duplicates by appending _1, _2, ...

    Returns: absolute file path as string
    """
    from config import DATA_RAW_DIR
    if out_dir is None:
        out_dir = str(DATA_RAW_DIR)
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    try:
        # derive filename
        if not filename:
            name = os.path.basename(urlparse(url).path) or "download.pdf"
            if not name.lower().endswith(".pdf"):
                name = (name or "download") + ".pdf"
            name = re.sub(r"[^A-Za-z0-9._-]+", "_", name)  # sanitize
        else:
            name = filename if filename.lower().endswith(".pdf") else filename + ".pdf"

        dest = Path(out_dir) / name
        base, ext = os.path.splitext(dest.name)
        i = 1
        while dest.exists():
            dest = dest.with_name(f"{base}_{i}{ext}")
            i += 1

        headers = {"User-Agent": os.getenv("USER_AGENT", "YEGGardenSuite-RAG/1.0")}
        with requests.get(url, headers=headers, stream=True, timeout=timeout) as r:
            r.raise_for_status()
            ct = r.headers.get("Content-Type", "")
            if ("pdf" not in ct.lower()) and (not PDF_URL_RE.search(url.lower())):
                print(f"[warn] Response may not be a PDF (Content-Type: {ct})")
            with open(dest, "wb") as f:
                for chunk in r.iter_content(chunk_size=65536):
                    if chunk:
                        f.write(chunk)

        return str(dest.resolve())
    except Exception as e:
        print(f"[error] Failed to download PDF from {url}: {e}")
        return None
