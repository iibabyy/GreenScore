AI service - data ingestion and RAG

Requirements
- python3
- pip install -r requirements.txt
- For Playwright (if used): `playwright install`

Steps
1. Populate data/ directories (csv, json, pdf, web)
2. Optionally run the scraper scaffold:
   python rag/scraper/scrape.py
3. Build vectorstore:
   python -c "from rag.loader import load_all_documents; from rag.vectorstore import create_vectorstore; docs=load_all_documents(); create_vectorstore(docs, persist_path='./data/faiss_store')"

Notes
- The loader supports CSV, JSON, PDF, HTML and TXT. Add loaders to `rag/loader.py` if you need other formats.
- The scraper respects robots.txt and will create `.blocked` files when scraping is not allowed.
