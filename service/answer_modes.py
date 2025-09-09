from langchain.prompts import PromptTemplate
from langchain_ollama import ChatOllama  # pip install -U langchain-ollama
from config import GEN_MODEL
from service.qa_chain import make_qa

# --- Normalizer protects retrieval from user typos before embeddings/reranker run.---
_QN_PROMPT = PromptTemplate.from_template(
    "Fix spelling and grammar in the question without changing meaning. "
    "Return ONLY the corrected question.\n\nQuestion: {q}"
)
_qn_llm = ChatOllama(model=GEN_MODEL, temperature=0)

def normalize_question(q: str) -> str:
    try:
        result = _qn_llm.invoke(_QN_PROMPT.format(q=q))
        # If result is a list, get the first string or dict's 'content'
        if isinstance(result, list):
            if result and isinstance(result[0], dict) and "content" in result[0]:
                return result[0]["content"].strip()
            elif result and isinstance(result[0], str):
                return result[0].strip()
            else:
                return str(result).strip()
        elif hasattr(result, "content"):
            content = result.content
            if isinstance(content, str):
                return content.strip()
            elif isinstance(content, list):
                # If it's a list, join string elements or extract 'content' from dicts
                items = []
                for item in content:
                    if isinstance(item, str):
                        items.append(item.strip())
                    elif isinstance(item, dict) and "content" in item:
                        items.append(str(item["content"]).strip())
                return " ".join(items)
            else:
                return str(content).strip()
        elif isinstance(result, str):
            return result.strip()
        else:
            return str(result).strip()
    except Exception:
        return q  # safest fallback

# Then use it inside your answer functions:

def answer_pre_ingest(question: str, qa_chain):
    q_norm = normalize_question(question)
    out = qa_chain.invoke({"query": q_norm})
    # If normalization hurt recall, fall back to original once
    if out["result"].strip() == "NOT_ENOUGH_CONTEXT" and q_norm != question:
        out = qa_chain.invoke({"query": question})
    return out["result"], out.get("source_documents", [])

def answer_hybrid(question: str, vs):
    q_norm = normalize_question(question)
    qa = make_qa(vs)
    first = qa.invoke({"query": q_norm})
    text = first["result"].strip()
    srcs = first.get("source_documents", [])

    if text == "NOT_ENOUGH_CONTEXT" and q_norm != question:
        first = qa.invoke({"query": question})
        text = first["result"].strip()
        srcs = first.get("source_documents", [])

    if text == "NOT_ENOUGH_CONTEXT":
        from service.rag_store import refresh_store
        from config import URLS, PDF_URLS, LOCAL_PDF_PATHS
        refresh_store(vs, URLS, PDF_URLS, LOCAL_PDF_PATHS)
        qa = make_qa(vs)
        second = qa.invoke({"query": q_norm})
        text = second["result"].strip()
        srcs = second.get("source_documents", [])
    return text, srcs
