from pathlib import Path

# Ollama model names
GEN_MODEL = "llama3.1:8b"          # Meta Llama via Ollama (chat model)
EMBED_MODEL = "nomic-embed-text"   # Embedding model via Ollama

# Local FAISS index directory
INDEX_DIR = Path("./edmonton_backyard_faiss")

# Source pages (add more official City of Edmonton pages if needed)
URLS = [
    "https://www.edmonton.ca/city_government/bylaws/zoning-bylaw",
    "https://www.edmonton.ca/residential_neighbourhoods/backyard-housing",
    "https://zoningbylaw.edmonton.ca/570-measuring-height-and-grade",
    "https://zoningbylaw.edmonton.ca/backyard-housing",
    "https://zoningbylaw.edmonton.ca/bylaw-pdf-print",
    "https://zoningbylaw.edmonton.ca/part-6-specific-development-regulations",
    "https://zoningbylaw.edmonton.ca/part-6-specific-development-regulations/610-backyard-housing",
]

# Optional: online PDF sources (processed with OnlinePDFLoader)
PDF_URLS = [
    # Example: City "How-To Guide" PDF
    # "https://www.edmonton.ca/sites/default/files/public-files/Backyard-Housing-How-To-Guide.pdf?cb=1737052351",
]

# Optional: local PDF paths (if you download PDFs manually)
LOCAL_PDF_PATHS = [
    "./data/raw/Backyard-Housing-How-To-Guide.pdf"
] 

# System-style rules baked into the prompt
SYSTEM_RULES = (
    "You are an assistant for Edmonton backyard housing. "
    "Answer ONLY from the provided context (official City sources). "
    "If the answer is not in the context, reply exactly with: NOT_ENOUGH_CONTEXT. "
    "Be concise and non-legal."
)

# Prompt template for RetrievalQA
QA_TEMPLATE = """{system}

Question: {question}

Context:
{context}

Answer:
"""

# ---------- Ollama generation parameters (tunable) ----------
# These map to Ollama's /generate options.
# See: https://github.com/ollama/ollama/blob/main/docs/modelfile.md#parameters
LLM_KWARGS = {
    # Decoding
    "temperature": 0.2,        # lower for factual QA
    "top_k": 40,               # shortlist of candidates
    "top_p": 0.9,              # nucleus sampling
    "tfs_z": 1.0,              # tail-free sampling

    # Length & context
    "num_predict": 384,        # max new tokens to generate
    "num_ctx": 8192,           # context window tokens (depends on model)

    # Repetition control
    "repeat_last_n": 64,
    "repeat_penalty": 1.1,

    # Mirostat (advanced, keeps perplexity steady). 0 = off, 1 or 2 = on.
    "mirostat": 0,
    "mirostat_tau": 5.0,
    "mirostat_eta": 0.1,

    # Optional: set a stop sequence (example shown, usually not needed here)
    # "stop": ["\nSources:", "\nContext:"],

    # Connectivity (uncomment if your Ollama is remote)
    # "base_url": "http://localhost:11434",
}
