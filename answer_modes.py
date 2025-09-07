from qa_chain import make_qa
from rag_store import refresh_store
from config import URLS

def answer_pre_ingest(question: str, qa_chain):
    """Answer using the pre-built store only (no live fetch)."""
    out = qa_chain.invoke({"query": question})
    return out["result"], out.get("source_documents", [])

def answer_hybrid(question: str, vs):
    """
    Try RAG first. If the model says NOT_ENOUGH_CONTEXT,
    live-fetch pages, refresh the store, and retry once.
    """
    qa = make_qa(vs)
    first = qa.invoke({"query": question})
    text = first["result"].strip()
    srcs = first.get("source_documents", [])

    if text == "NOT_ENOUGH_CONTEXT":
        refresh_store(vs, URLS)
        qa = make_qa(vs)
        second = qa.invoke({"query": question})
        return second["result"].strip(), second.get("source_documents", [])

    return text, srcs
