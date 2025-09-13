import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import URLS, PDF_URLS, LOCAL_PDF_PATHS, INDEX_DIR
from service.logging_helper import configure_logging
from service.rag_store import (
    build_or_load_store,
    refresh_store,
    load_pages,
    load_pdf_urls,
    load_local_pdfs,
    split_docs,
)

# -------------------------------
# Helpers
# -------------------------------
def index_size(vs) -> int:
    try:
        return int(vs.index.ntotal)  # type: ignore[attr-defined]
    except Exception:
        return -1

# -------------------------------
# Main
# -------------------------------
def main():
    parser = argparse.ArgumentParser(description="Refresh FAISS vector store with latest City of Edmonton pages & PDFs.")
    parser.add_argument("--dry-run", action="store_true", help="Load and count sources, but do NOT write to FAISS")
    parser.add_argument("--rebuild", action="store_true", help="Delete existing index and rebuild from scratch")
    args = parser.parse_args()

    # Configure logging via helper (logs/refresh.log inferred from script name)
    logger = configure_logging(level=logging.INFO)
    start_ts = time.time()
    logger.info("=== refresh start ===")
    logger.info(f"rebuild={args.rebuild} dry_run={args.dry_run}")
    logger.info(f"urls={len(URLS)} pdf_urls={len(PDF_URLS)} local_pdf_paths={len(LOCAL_PDF_PATHS)}")

    # Optionally rebuild index from scratch
    if args.rebuild and INDEX_DIR.exists():
        logger.warning(f"Deleting existing index at {INDEX_DIR.resolve()}")
        for p in INDEX_DIR.iterdir():
            try:
                if p.is_file():
                    p.unlink()
                else:
                    import shutil
                    shutil.rmtree(p, ignore_errors=True)
            except Exception as e:
                logger.error(f"Failed to remove {p}: {e}")
        try:
            INDEX_DIR.rmdir()
        except Exception:
            pass

    # Build/load store
    vs = build_or_load_store(URLS, PDF_URLS, LOCAL_PDF_PATHS)
    before_size = index_size(vs)
    logger.info(f"index size (before): {before_size}")

    # Pre-load sources to compute counts
    try:
        web_docs = load_pages(URLS or [])
    except Exception as e:
        logger.exception(f"load_pages failed: {e}")
        web_docs = []
    try:
        pdf_web_docs = load_pdf_urls(PDF_URLS or [])
    except Exception as e:
        logger.exception(f"load_pdf_urls failed: {e}")
        pdf_web_docs = []
    try:
        pdf_local_docs = load_local_pdfs(LOCAL_PDF_PATHS or [])
    except Exception as e:
        logger.exception(f"load_local_pdfs failed: {e}")
        pdf_local_docs = []

    all_docs = (web_docs or []) + (pdf_web_docs or []) + (pdf_local_docs or [])
    try:
        chunks = split_docs(all_docs)
        chunk_count = len(chunks)
    except Exception as e:
        logger.exception(f"split_docs failed: {e}")
        chunk_count = -1

    logger.info(f"fetched docs: web={len(web_docs)} pdf_web={len(pdf_web_docs)} pdf_local={len(pdf_local_docs)} total={len(all_docs)}")
    logger.info(f"chunk_count (pre-split estimate): {chunk_count}")

    # Write to FAISS (unless dry-run)
    if not args.dry_run:
        vs = refresh_store(vs, URLS, PDF_URLS, LOCAL_PDF_PATHS)

    after_size = index_size(vs)
    elapsed = round(time.time() - start_ts, 3)
    logger.info(f"index size (after): {after_size}")
    logger.info(f"elapsed_s: {elapsed}")
    logger.info("=== refresh end ===")

    # JSON summary for cron-friendly scraping
    summary = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "rebuild": args.rebuild,
        "dry_run": args.dry_run,
        "urls": len(URLS),
        "pdf_urls": len(PDF_URLS),
        "local_pdf_paths": len(LOCAL_PDF_PATHS),
        "docs_web": len(web_docs),
        "docs_pdf_web": len(pdf_web_docs),
        "docs_pdf_local": len(pdf_local_docs),
        "docs_total": len(all_docs),
        "chunks_estimated": chunk_count,
        "index_size_before": before_size,
        "index_size_after": after_size,
        "elapsed_s": elapsed,
    }
    print(json.dumps(summary))

if __name__ == "__main__":
    main()
