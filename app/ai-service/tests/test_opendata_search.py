import os
import sys
import pytest

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


@pytest.mark.integration
def test_opendata_agribalyse_presence():
    """Load the persisted main_index and query for Agribalyse content; expect agribalyse CSV source in results."""
    persist_path = os.path.join(settings.FAISS_DIR, 'main_index', 'faiss_index')
    assert os.path.isdir(persist_path), f"Index not found at {persist_path}"
    assert HuggingFaceEmbeddings is not None, "HuggingFaceEmbeddings not available in environment"
    emb = HuggingFaceEmbeddings(model_name=getattr(settings, 'EMBEDDING_MODEL'))
    vs = FAISS.load_local(persist_path, emb, allow_dangerous_deserialization=True)

    query = 'tableau des ingrédients agribalyse'
    results = vs.similarity_search_with_score(query, k=5)
    # Normalize results to metadata
    found_sources = set()
    if results and isinstance(results[0], tuple):
        for doc, score in results:
            src = doc.metadata.get('source')
            if src:
                found_sources.add(src)
    else:
        for doc in results:
            src = doc.metadata.get('source')
            if src:
                found_sources.add(src)

    # Expect at least one agribalyse CSV or similar in sources
    matches = [s for s in found_sources if 'agribalyse' in s or 'agrifood' in s or 'agribalyse_ingredients' in s]
    assert len(matches) > 0, f"No agribalyse-related source found in top results: {found_sources}"
