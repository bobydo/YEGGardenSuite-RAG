from typing import List, Tuple

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
