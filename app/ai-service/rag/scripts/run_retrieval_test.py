"""Load a persisted FAISS index and run a few queries to verify retrieval.

Usage:
    .venv/bin/python rag/scripts/run_retrieval_test.py
"""
import os
import sys
sys.path.append(os.getcwd())

from core.config import settings
try:
    from langchain_community.vectorstores import FAISS
except Exception:
    from langchain.vectorstores import FAISS
# embeddings provider
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except Exception:
    try:
        from langchain.embeddings import HuggingFaceEmbeddings
    except Exception:
        HuggingFaceEmbeddings = None


def load_index(persist_dir):
    index_path = os.path.join(persist_dir, 'faiss_index')
    if not os.path.isdir(index_path):
        print('Index path not found:', index_path)
        return None
    try:
        # Build the embeddings object same as during index creation
        if HuggingFaceEmbeddings is None:
            raise ImportError('HuggingFaceEmbeddings not available; cannot load FAISS index without embeddings instance')
        embeddings = HuggingFaceEmbeddings(
            model_name=getattr(settings, 'EMBEDDING_MODEL', 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'),
            model_kwargs={'device': 'cpu'}
        )
        # We created this index locally in a previous step; allow local deserialization.
        vectordb = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
        return vectordb
    except Exception as e:
        print('Error loading FAISS index:', e)
        return None


def pretty_print_result(res, top_k=3):
    for i, r in enumerate(res[:top_k], start=1):
        txt = getattr(r, 'page_content', None) or r.get('text', '')
        meta = getattr(r, 'metadata', None) or r.get('metadata', {})
        snippet = (txt[:300] + '...') if txt and len(txt) > 300 else txt
        print(f"{i}. score={meta.get('score', 'n/a')} source={meta.get('source')}")
        print('   ', snippet.replace('\n', ' ') if snippet else '(no text)')


def main():
    persist_path = os.path.join(settings.FAISS_DIR, 'test_index')
    print('Loading index from', persist_path)
    vs = load_index(persist_path)
    if vs is None:
        print('No index loaded')
        return

    queries = [
        'impact environnemental du packaging',
        'tableau des ingrédients agribalyse',
        'émissions liées à la production alimentaire'
    ]

    for q in queries:
        print('\n=== Query:', q)
        try:
            results = vs.similarity_search_with_score(q, k=5)
            # results is list[(doc, score)] or list[doc] depending on wrapper
            if results and isinstance(results[0], tuple):
                docs = []
                for doc, score in results:
                    doc.metadata['score'] = score
                    docs.append(doc)
                pretty_print_result(docs, top_k=5)
            else:
                pretty_print_result(results, top_k=5)
        except Exception as e:
            print('Error during search:', e)


if __name__ == '__main__':
    main()
