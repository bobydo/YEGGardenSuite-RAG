from typing import List
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from config import EMBED_MODEL, INDEX_DIR

def load_pages(urls: List[str]):
    loader = WebBaseLoader(urls)
    docs = loader.load()
    return docs

def split_docs(docs):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=150)
    return splitter.split_documents(docs)

def build_or_load_store(urls: List[str]) -> FAISS:
    embeddings = OllamaEmbeddings(model=EMBED_MODEL)
    if INDEX_DIR.exists():
        vs = FAISS.load_local(str(INDEX_DIR), embeddings, allow_dangerous_deserialization=True)
    else:
        docs = load_pages(urls)
        chunks = split_docs(docs)
        vs = FAISS.from_documents(chunks, embeddings)
        vs.save_local(str(INDEX_DIR))
    return vs

def refresh_store(vs: FAISS, urls: List[str]):
    """Live fetch current pages and update vector store (Hybrid fallback)."""
    docs = load_pages(urls)
    chunks = split_docs(docs)
    vs.add_documents(chunks)
    vs.save_local(str(INDEX_DIR))
    return vs
