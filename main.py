from config import URLS
from rag_store import build_or_load_store
from qa_chain import make_qa
from answer_modes import answer_pre_ingest, answer_hybrid

def show_sources(srcs):
    seen = set()
    urls = []
    for d in srcs or []:
        u = d.metadata.get("source") or d.metadata.get("url") or "unknown"
        if u and u not in seen:
            urls.append(u)
            seen.add(u)
    if urls:
        print("Sources:")
        for u in urls:
            print(" -", u)

if __name__ == "__main__":
    vs = build_or_load_store(URLS)

    # Example questions
    questions = [
        "What is backyard housing and do I need permits?",
        "What are the height and width limits for backyard housing?",
        "Do I need an alley to build a backyard house?",
    ]

    print("=== PRE-INGEST (RAG) ===")
    qa = make_qa(vs)
    for q in questions:
        ans, srcs = answer_pre_ingest(q, qa)
        print(f"\nQ: {q}\nA: {ans}")
        show_sources(srcs)

    print("\n=== HYBRID (RAG + live refresh fallback) ===")
    for q in questions:
        ans, srcs = answer_hybrid(q, vs)
        print(f"\nQ: {q}\nA: {ans}")
        show_sources(srcs)
