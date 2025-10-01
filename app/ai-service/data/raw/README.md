Data directory layout for the ai-service

Structure (under `app/ai-service/data`):

- pdf/        -> PDF files (raw reports, brand PDFs). Use .pdf extension.
- csv/        -> CSV exports (tables, product lists). Use .csv extension.
- json/       -> Cleaned JSON or API dumps (.json).
- web/        -> Raw HTML pages or cleaned text saved from web scraping (.html/.htm).
- raw/        -> Misc text files or sources that don't fit other categories (.txt, .md).
- processed/  -> Normalized/cleaned outputs (for downstream ingestion).
- faiss/      -> Persisted FAISS index files (if you choose to persist locally).
- scrape_index.csv -> Index file produced by the scraper listing sources and statuses.

Usage
1. Quick organization: run the organizer script to move existing files from the data root into the appropriate folders:

   python3 app/ai-service/rag/scripts/organize_data.py

2. Scraping: use `app/ai-service/rag/scraper/scrape.py` with `scrape_config.yaml` to fetch web sources into `web/` or `json/`.

3. Ingestion: use `rag.loader.load_all_documents()` to load documents from the subfolders for chunking and vectorization.

Notes
- Filenames will be kept where possible; the organizer avoids overwriting by adding numeric suffixes when collisions occur.
- The `faiss/` folder is optional — the vectorstore can be configured to persist to `FAISS_DIR` via `core.config`.
- Always respect website `robots.txt` and the legal terms of sources. The scraper scaffold performs basic checks and rate-limits requests.
Data directory layout for multi-source RAG ingestion

Structure:

data/
  csv/      - tabular datasets (Agribalyse, EDGAR, FAO...)
  json/     - JSON exports from APIs/scrapers (CarbonCloud, Eaternity...)
  pdf/      - reports and whitepapers (OECD, ADEME, brand reports...)
  web/      - raw HTML and cleaned text dumps from web scraping
  scrape_index.csv - index of scraping runs (source,id,url,local_path,status,notes)

If a source is blocked by robots.txt or paywall, a .blocked file will be created in data/ with instructions for manual download.

To add data:
- Place CSV files in data/csv/
- Place JSON files in data/json/
- Place PDFs in data/pdf/
- Place cleaned HTML/text in data/web/

Run the scraper scaffold at app/ai-service/rag/scraper/scrape.py (requires requests, beautifulsoup4, pyyaml). For JS-heavy pages, configure Playwright and enable it in the script.
