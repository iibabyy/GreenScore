"""Reindex CLI: load documents and create/persist FAISS index.

Usage:
    .venv/bin/python rag/scripts/reindex.py [--persist-dir ./data/faiss/main_index]
"""
import argparse
import os
import sys
sys.path.append(os.getcwd())

from core.config import settings
from rag.loader import load_all_documents
from rag.vectorstore import create_vectorstore


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--persist-dir', default=os.path.join(settings.FAISS_DIR, 'main_index'))
    p.add_argument('--batch-size', type=int, default=1024)
    args = p.parse_args()

    print('Loading documents...')
    docs = load_all_documents()
    print(f'Loaded {len(docs)} documents')

    print('Creating vectorstore...')
    vs = create_vectorstore(docs, persist_path=args.persist_dir, batch_size=args.batch_size)
    if vs:
        print('Index created at', args.persist_dir)
    else:
        print('No index created')


if __name__ == '__main__':
    main()
