# pip install playwright
# python -m playwright install

from typing import List, Sequence
from urllib.parse import urlparse
from langchain_community.document_loaders import WebBaseLoader, OnlinePDFLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from langchain.schema import Document
from playwright.sync_api import sync_playwright   # NEW
from config import EMBED_MODEL, INDEX_DIR

ALLOWED = {"zoningbylaw.edmonton.ca", "www.edmonton.ca"}

def _is_allowed(url):
    try:
        host = url.split("//", 1)[-1].split("/", 1)[0].lower()
        return host in ALLOWED
    except Exception:
        return False

def _load_html_basic(urls):
    try:
        loader = WebBaseLoader(
            urls,
            header_template={"User-Agent": "Mozilla/5.0"},
        )
        return loader.load()
    except Exception:
        return []

def _expand_and_extract_with_playwright(urls):
    docs = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            user_agent="Mozilla/5.0",
            ignore_https_errors=True,
            service_workers="block",  # avoid “networkidle” hangs
        )

        # speed up: block heavy assets
        ctx.route(
            "**/*",
            lambda route: route.abort()
            if any(route.request.url.endswith(ext) for ext in (
                ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".css", ".woff", ".woff2"
            ))
            else route.continue_(),
        )

        page = ctx.new_page()
        for url in urls:
            if not _is_allowed(url):
                continue
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=15000)

                # dismiss cookie banners (best-effort)
                for txt in ("Accept", "I agree", "Got it"):
                    try:
                        page.get_by_role("button", name=txt, exact=False).click(timeout=1500)
                        break
                    except Exception:
                        pass

                # click “Open All” if present (bylaw pages)
                try:
                    page.get_by_text("Open All", exact=False).click(timeout=2500)
                except Exception:
                    pass

                # expand accordions
                for b in page.locator("button[aria-controls]").all():
                    try:
                        if b.get_attribute("aria-expanded") == "false":
                            b.click()
                    except Exception:
                        pass

                # extract text
                try:
                    page.wait_for_selector("main", timeout=4000)
                    text = page.locator("main").inner_text(timeout=4000)
                except Exception:
                    text = page.inner_text("body", timeout=4000)

                text = (text or "").strip()

                # hard fallback: use the page's “Create PDF” link, parse as PDF
                if len(text) < 600:
                    try:
                        link = page.get_by_role("link", name="Create PDF", exact=False).first
                        href = link.get_attribute("href")
                        if href and href.startswith("http") and _is_allowed(href):
                            pdf_docs = OnlinePDFLoader(href).load()
                            docs.extend(pdf_docs)
                            continue
                    except Exception:
                        pass

                if text:
                    docs.append(Document(page_content=text, metadata={"source": url}))
            except Exception as e:
                print(f"[warn] Playwright load failed: {url} -> {e}")

        ctx.close()
        browser.close()
    return docs

def load_pages(urls):
    # try cheap loader first; if thin, render & expand with Playwright
    docs = _load_html_basic(urls)
    if sum(len(d.page_content) for d in docs) >= 600:
        return docs
    return _expand_and_extract_with_playwright(urls)

def split_docs(docs):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=150)
    return splitter.split_documents(docs)

def build_or_load_store(urls: List[str], pdf_urls: Sequence[str] = (), local_pdf_paths: Sequence[str] = ()):
    embeddings = OllamaEmbeddings(model=EMBED_MODEL)
    if INDEX_DIR.exists():
        vs = FAISS.load_local(str(INDEX_DIR), embeddings, allow_dangerous_deserialization=True)
    else:
        web_docs = load_pages(urls or [])
        pdf_web_docs = load_pdf_urls(list(pdf_urls) if pdf_urls else [])
        pdf_local_docs = load_local_pdfs(list(local_pdf_paths) if local_pdf_paths else [])
        all_docs = web_docs + pdf_web_docs + pdf_local_docs
        chunks = split_docs(all_docs)
        vs = FAISS.from_documents(chunks, embeddings)
        vs.save_local(str(INDEX_DIR))
    return vs

def refresh_store(vs: FAISS, urls: List[str], pdf_urls: Sequence[str] = (), local_pdf_paths: Sequence[str] = ()):
    web_docs = load_pages(urls or [])
    pdf_web_docs = load_pdf_urls(list(pdf_urls) if pdf_urls else [])
    pdf_local_docs = load_local_pdfs(list(local_pdf_paths) if local_pdf_paths else [])
    all_docs = web_docs + pdf_web_docs + pdf_local_docs
    chunks = split_docs(all_docs)
    vs.add_documents(chunks)
    vs.save_local(str(INDEX_DIR))
    return vs
