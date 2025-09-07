# Edmonton Backyard Housing RAG + Hybrid (Ollama)

Local, privacy-first Q&A over City of Edmonton backyard-housing pages using:
- Ollama (Meta Llama for generation, nomic-embed-text for embeddings)
- LangChain + FAISS
- Pre-ingest (RAG) and Hybrid (RAG + live refresh on demand)

## Quick Start
1) Install dependencies:
   ```bash
   python -m venv myenv
   pip install -r requirements.txt
   pip install --force-reinstall -r requirements.txt
   ```

2) Start Ollama and pull models:
-  Code uses the nomic-embed-text model for generating embeddings with Ollama. 
-  pull nomic-embed-text, because RAG code needs an embedding model to turn text into vectors for FAISS.
-  nomic-embed-text → converts docs & queries into vectors for semantic search.

   ```bash
   ollama serve
   ollama pull llama3.1:8b
   ollama pull nomic-embed-text
   ```

3) Run:
   ```bash
   python main.py
   ```

## Files
- `config.py` — models, URLs, system rules, prompt template.
- `rag_store.py` — load/split pages, build/load FAISS, refresh store.
- `qa_chain.py` — create LLM and RetrievalQA with custom prompt.
- `answer_modes.py` — `answer_pre_ingest` and `answer_hybrid` helpers.
- `main.py` — demo runner showing both modes.

## Notes
- Add or adjust URLs in `config.py` to include more official City pages.
- Hybrid mode refreshes the store if the model replies `NOT_ENOUGH_CONTEXT`.
- For production, schedule periodic refreshes and add robust citations/logging.
- Integrations providers https://python.langchain.com/docs/integrations/providers/
