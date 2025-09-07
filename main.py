import argparse
from config import URLS, PDF_URLS, LOCAL_PDF_PATHS
from service.rag_store import build_or_load_store
from service.qa_chain import make_qa
from service.answer_modes import answer_pre_ingest, answer_hybrid
from service.utils import attach_citations

EXAMPLE_QUESTIONS = [
    "What is backyard housing and do I need permits?",
    "What are the height and area limits for backyard housing?",
    "Do I need an alley to build a backyard house?",
]

def ask_once(vs, question: str, mode: str):
    if mode == "rag":
        qa = make_qa(vs)
        ans, srcs = answer_pre_ingest(question, qa)
    elif mode == "hybrid":
        ans, srcs = answer_hybrid(question, vs)
    else:
        raise ValueError("mode must be 'rag' or 'hybrid'")
    print(attach_citations(ans, srcs))

def interactive(vs, mode: str):
    print(f"Backyard Housing QA ({mode}) — type 'exit' to quit.")
    qa = make_qa(vs) if mode == "rag" else None
    while True:
        try:
            q = input("\nQ: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not q or q.lower() in {"exit", "quit"}:
            break
        if mode == "rag":
            ans, srcs = answer_pre_ingest(q, qa)
        else:
            ans, srcs = answer_hybrid(q, vs)
        print("\nA:", attach_citations(ans, srcs))

def main():
    parser = argparse.ArgumentParser(description="YEG Garden Suite — RAG/Hybrid QA with citations")
    parser.add_argument("--mode", choices=["rag", "hybrid"], default="hybrid", help="Use pre-ingested RAG or Hybrid (RAG + live refresh)")
    parser.add_argument("--question", "-q", help="Ask a single question and exit")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive Q&A loop")
    parser.add_argument("--examples", "-e", action="store_true", help="Run example questions")
    args = parser.parse_args()

    vs = build_or_load_store(URLS, PDF_URLS, LOCAL_PDF_PATHS)

    if args.question:
        return ask_once(vs, args.question, args.mode)

    if args.interactive:
        return interactive(vs, args.mode)

    if args.examples or True:  # default: run examples
        print(f"=== {args.mode.upper()} MODE ===")
        for q in EXAMPLE_QUESTIONS:
            print(f"\nQ: {q}")
            if args.mode == "rag":
                qa = make_qa(vs)
                ans, srcs = answer_pre_ingest(q, qa)
            else:
                ans, srcs = answer_hybrid(q, vs)
            print("A:", attach_citations(ans, srcs))

if __name__ == "__main__":
    main()
