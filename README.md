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
   Ask one question:
   python main.py -q "What are the height and area limits for backyard housing?"
   Interactive chat:
   python main.py -i
   Pick mode explicitly:
   python main.py --mode rag      # pre-ingest only
   python main.py --mode hybrid   # RAG + live refresh
   ```
4) Jobs
   ```bash
   python jobs/search_first.py # get urls
   python jobs/refresh.py # rebuild index from scratch, write logs to custom path
   ```
5) Static type checker for Python
```bash
   (.venv) PS D:\YEGGardenSuite-RAG> npx pyright
   0 errors, 0 warnings, 0 informations
```

## Notes
- Add or adjust URLs in `config.py` to include more official City pages.
- Hybrid mode refreshes the store if the model replies `NOT_ENOUGH_CONTEXT`.
- For production, schedule periodic refreshes and add robust citations/logging.
- Integrations providers https://python.langchain.com/docs/integrations/providers/
- refresh.py took long 53 mins to complete index
```
2025-09-07 08:30:12,039 INFO index size (before): 112
2025-09-07 08:30:34,663 INFO fetched docs: web=7 pdf_web=0 pdf_local=34 total=41
2025-09-07 08:30:34,664 INFO chunk_count (pre-split estimate): 1469
2025-09-07 09:23:08,670 INFO index size (after): 1581
2025-09-07 09:23:08,670 INFO elapsed_s: 3176.661
2025-09-07 09:23:08,670 INFO === refresh end ===
```
- seach_first.py tuning process 
```
a) You don’t need to “know all terms” first. Start with a small glossary and intent paraphrases → auto-generate many queries.
b) The mining step (--mine) scrapes the top results and surfaces phrases like “abutting lane”, “Pathway (0.9 m)”, “Vehicle Access”. Add any good ones back to GLOSSARY and re-run.
c) Keep the allowlist so results stay authoritative.
python jobs\search_first.py -k 25 --mine
```
- Optional (future try): LCEL chains available in `service/lcel_qa_chain.py` (more control, streaming, custom context formatting).
