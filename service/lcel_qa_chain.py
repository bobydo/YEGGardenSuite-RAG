"""LCEL-based QA chains.

Why this file:
- Gives you a lower-level, fully explicit chain built with LangChain Expression Language (LCEL)
- Easier to customize (context truncation, reranking, filters, streaming, logging)
- Lives alongside the classic RetrievalQA wrapper (see qa_chain.py). Keep both until you're happy.

Exports:
- make_lcel_chain(vs, k=4): returns a runnable that outputs ONLY the answer string.
- make_lcel_chain_with_sources(vs, k=4): returns a runnable that outputs dict {"answer", "sources"}.

Usage examples:

    from service.lcel_qa_chain import make_lcel_chain, make_lcel_chain_with_sources
    chain = make_lcel_chain(vs)
    answer = chain.invoke("What are height limits?")

    chain_sources = make_lcel_chain_with_sources(vs)
    out = chain_sources.invoke("Do I need an alley?")
    print(out["answer"])
    print(out["sources"])  # list of (source, page?) strings

Streaming tokens (answer only):

    for token in chain.stream("Setback requirements?"):
        print(token, end="", flush=True)

Notes:
- You can plug additional steps between retriever and LLM (e.g., a reranker) by editing pipeline.
- History support: format CHAT_PROMPT manually with a list for "history" if needed.
"""
from typing import Iterable, List, Dict, Any
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.schema import Document

from service.prompts import CHAT_PROMPT
from service.qa_chain import make_llm  # reuse Ollama LLM factory

# ------------ Helpers ------------

def _format_docs_plain(docs: List[Document]) -> str:
    return "\n\n".join(d.page_content for d in docs)

def _format_docs_with_ids(docs: List[Document]) -> str:
    lines = []
    for i, d in enumerate(docs):
        lines.append(f"[{i}] {d.page_content}")
    return "\n\n".join(lines)

def _extract_sources(docs: List[Document]) -> List[str]:
    out = []
    for d in docs:
        src = d.metadata.get("source") or "unknown"
        page = d.metadata.get("page") or d.metadata.get("pdf_page")
        out.append(f"{src}{' (page '+str(page)+')' if page is not None else ''}")
    # keep order, remove dupes while preserving first occurrence
    seen = set(); uniq = []
    for s in out:
        if s not in seen:
            uniq.append(s); seen.add(s)
    return uniq

# ------------ Public factories ------------

def make_lcel_chain(vs, k: int = 4):
    """Return a runnable: str question -> str answer.

    Simpler substitute for RetrievalQA when you only want the answer and
    might later insert custom logic.
    """
    retriever = vs.as_retriever(search_kwargs={"k": k})
    llm = make_llm()

    chain = (
        {
            "question": RunnablePassthrough(),
            "context": (lambda q: q) | retriever | _format_docs_plain,
        }
        | CHAT_PROMPT
        | llm
        | StrOutputParser()
    )
    return chain

def make_lcel_chain_with_sources(vs, k: int = 4):
    """Return a runnable producing dict with answer + sources list.

    Output shape: {"answer": str, "sources": [str, ...]}
    """
    retriever = vs.as_retriever(search_kwargs={"k": k})
    llm = make_llm()

    def _build_context(x: Dict[str, Any]):
        return _format_docs_with_ids(x["docs"])  # x["docs"] inserted earlier

    pipeline = (
        {
            "question": RunnablePassthrough(),
            "docs": (lambda q: q) | retriever,
        }
        | {
            "question": lambda x: x["question"],
            "context": _build_context,
            "docs": lambda x: x["docs"],  # pass through for later source extraction
        }
        | CHAT_PROMPT
        | llm
    )

    def _invoke(question: str):
        intermediate = pipeline.invoke(question)
        # intermediate is an LLM message/string depending on llm; ensure str
        answer = getattr(intermediate, "content", intermediate)
        docs = (
            ({"question": question} | pipeline) if False else None  # placeholder to show structure
        )
        # We need docs: rerun retriever only (cheaper)
        retrieved = retriever.get_relevant_documents(question)
        sources = _extract_sources(retrieved)
        return {"answer": answer, "sources": sources}

    class _Runnable:
        def invoke(self, question: str):
            return _invoke(question)
        def stream(self, question: str):  # stream answer tokens only
            # Stream via llm.stream over formatted prompt messages
            formatted = CHAT_PROMPT.format_messages(question=question, context=_format_docs_plain(retriever.get_relevant_documents(question)))
            for part in llm.stream(formatted):
                yield getattr(part, "content", part)
        def batch(self, questions: List[str]):
            return [self.invoke(q) for q in questions]

    return _Runnable()

__all__ = [
    "make_lcel_chain",
    "make_lcel_chain_with_sources",
]
