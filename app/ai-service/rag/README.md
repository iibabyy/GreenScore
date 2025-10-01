RAG data ingestion

This folder contains utilities to load multi-format data and build a FAISS vectorstore.

Loader: `loader.py`
- `load_all_documents(data_dir=None)` finds files under the configured data directories and returns a list of `langchain.Document` objects.
- Supports CSV, JSON, PDF, HTML and TXT.

Scraper scaffold: `scraper/scrape.py`
- Uses `scrape_config.yaml` to list sources. Respects robots.txt and rate limits.
- Saves raw_html, cleaned text, and metadata JSON under `data/web` or `data/json`.

Vectorstore: `vectorstore.py`
- `create_vectorstore(docs, persist_path=None)` creates a FAISS index using HuggingFace embeddings.
- Chunking settings are taken from `core.config.settings` (CHUNK_SIZE, CHUNK_OVERLAP).

Quick start
1. Populate `app/ai-service/rag/scraper/scrape_config.yaml` with sources.
2. Run the scraper (optional): `python app/ai-service/rag/scraper/scrape.py`
3. Load documents and build vectorstore from Python:

```python
from rag.loader import load_all_documents
from rag.vectorstore import create_vectorstore

docs = load_all_documents()
vs = create_vectorstore(docs, persist_path='./data/faiss_store')
```

Notes
- Ensure `beautifulsoup4`, `requests`, `pyyaml` are installed if you want to use the scraper.
- The loader tries to handle UTF-8 and common JSON structures; add more parsers to `_LOADERS` for other filetypes.
