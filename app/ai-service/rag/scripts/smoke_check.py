#!/usr/bin/env python3
"""Simple smoke-check CLI for FAISS index.

Usage:
  .venv/bin/python rag/scripts/smoke_check.py --persist-dir ./data/faiss/main_index --k 3

Exits with code 0 if all queries returned at least one result, 2 otherwise.
"""
import os
import sys
import json
import argparse

sys.path.append(os.getcwd())
from core.config import settings
try:
    from langchain_community.vectorstores import FAISS
except Exception:
    from langchain.vectorstores import FAISS

try:
    from langchain_huggingface import HuggingFaceEmbeddings
except Exception:
    try:
        from langchain.embeddings import HuggingFaceEmbeddings
    except Exception:
        HuggingFaceEmbeddings = None


DEFAULT_QUERIES = [
    'impact environnemental du packaging',
    'empreinte carbone d\'un produit alimentaire',
    'tableau des ingrédients agribalyse'
]


def load_index(persist_dir):
    index_path = os.path.join(persist_dir, 'faiss_index')
    if not os.path.isdir(index_path):
        print('Index path not found:', index_path)
        return None
    if HuggingFaceEmbeddings is None:
        print('HuggingFaceEmbeddings not available; cannot load FAISS index')
        return None
    embeddings = HuggingFaceEmbeddings(
        model_name=getattr(settings, 'EMBEDDING_MODEL', 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'),
        model_kwargs={'device': 'cpu'}
    )
    vectordb = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
    return vectordb


def run_smoke(persist_dir, queries, k=3):
    vs = load_index(persist_dir)
    if vs is None:
        return 2
    results_summary = {}
    overall_ok = True
    for q in queries:
        try:
            res = vs.similarity_search_with_score(q, k=k)
            rows = []
            if res and isinstance(res[0], tuple):
                for doc, score in res:
                    rows.append({'score': float(score), 'source': doc.metadata.get('source'), 'snippet': (doc.page_content or '')[:300]})
            else:
                for doc in res:
                    rows.append({'score': None, 'source': doc.metadata.get('source'), 'snippet': (doc.page_content or '')[:300]})
            results_summary[q] = rows
            if len(rows) == 0:
                overall_ok = False
        except Exception as e:
            results_summary[q] = {'error': str(e)}
            overall_ok = False

    print(json.dumps({'persist_dir': persist_dir, 'k': k, 'results': results_summary}, ensure_ascii=False, indent=2))
    return 0 if overall_ok else 2


def main():
    p = os.path.join(settings.FAISS_DIR, 'main_index')
    parser = argparse.ArgumentParser()
    parser.add_argument('--persist-dir', default=p)
    parser.add_argument('--k', type=int, default=3)
    parser.add_argument('--queries-file', default=None, help='Path to a newline-separated file with queries')
    args = parser.parse_args()

    if args.queries_file:
        if not os.path.isfile(args.queries_file):
            print('queries file not found:', args.queries_file)
            sys.exit(2)
        with open(args.queries_file, 'r', encoding='utf-8') as fh:
            queries = [l.strip() for l in fh if l.strip()]
    else:
        queries = DEFAULT_QUERIES

    code = run_smoke(args.persist_dir, queries, k=args.k)
    sys.exit(code)


if __name__ == '__main__':
    main()
