"""Reindex only synthetic product profiles.

Usage:
    python -m rag.scripts.reindex_synthetic --persist-dir ./data/faiss/main_index_synth

This loads only TXT files under data/raw/synthetic_profiles and builds a FAISS index.
"""
import argparse
import os
import sys
sys.path.append(os.getcwd())

from core.config import settings
from rag.vectorstore import create_vectorstore
from rag.loader import _load_text_with_tags  # type: ignore

def _gather_synthetic_profiles(base_dir: str):
    target = os.path.join(base_dir, 'raw', 'synthetic_profiles')
    files = []
    if os.path.isdir(target):
        for fname in os.listdir(target):
            if fname.endswith('.txt'):
                files.append(os.path.join(target, fname))
    return sorted(files)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--persist-dir', default=os.path.join(settings.FAISS_DIR, 'synthetic_index'))
    p.add_argument('--batch-size', type=int, default=256)
    args = p.parse_args()

    profiles = _gather_synthetic_profiles(settings.DATA_DIR)
    if not profiles:
        print('No synthetic profiles found.')
        return
    print(f'Found {len(profiles)} synthetic profiles')
    docs = []
    for pth in profiles:
        docs.extend(_load_text_with_tags(pth))
    print(f'Loaded {len(docs)} synthetic documents')
    vs = create_vectorstore(docs, persist_path=args.persist_dir, batch_size=args.batch_size)
    if vs:
        print('Synthetic index created at', args.persist_dir)
    else:
        print('Failed to build synthetic index')

if __name__ == '__main__':
    main()
