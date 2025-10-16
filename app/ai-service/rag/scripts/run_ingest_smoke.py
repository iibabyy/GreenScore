"""Run a quick ingestion: load documents and build a FAISS vectorstore (smoke test).

Usage:
    .venv/bin/python rag/scripts/run_ingest_smoke.py
"""
from pathlib import Path
import os
import sys

# ensure ai-service package path
sys.path.append(os.getcwd())

from rag.loader import load_all_documents
from rag.vectorstore import create_vectorstore
from core.config import settings


def main():
    print('Loading documents...')
    docs = load_all_documents()
    print(f'Loaded {len(docs)} documents total')

    print('Creating vectorstore (persist to data/faiss/test_index)...')
    persist_path = os.path.join(settings.FAISS_DIR, 'test_index')
    vs = create_vectorstore(docs, persist_path=persist_path, batch_size=1024)
    if vs is None:
        print('No vectorstore created (no chunks).')
    else:
        print('Vectorstore created successfully')


if __name__ == '__main__':
    main()
