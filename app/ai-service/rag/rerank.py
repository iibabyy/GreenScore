"""Lightweight document reranking utilities to reduce hallucinations.

Strategy (MVP):
1. Retrieve an initial candidate set (k_initial) from the vector store.
2. (Optional) Apply a source/type filter driven by user param (e.g. pdf,csv,html).
3. Re-score each candidate with a secondary similarity: cosine(question_embedding, doc_embedding).
   - Uses the same embedding model as the vector index when available.
   - Falls back gracefully to the original order if embeddings not available.
4. Return the top `top_n` documents in descending score order.

This is intentionally simple (single-stage rerank) so we can iterate later:
- Future: cross-encoder / miniLM reranker, LLM-based judge, hybrid sparse + dense fusion.

All heavy resources (embedding model) are lazy-loaded and cached at module level.
"""
from __future__ import annotations

from typing import List, Optional, Tuple
import math

try:  # Prefer community package
    from langchain.schema import Document
except Exception:  # pragma: no cover
    try:
        from langchain.docstore.document import Document  # type: ignore
    except Exception:  # pragma: no cover
        class Document:  # minimal fallback
            def __init__(self, page_content: str, metadata: Optional[dict] = None):
                self.page_content = page_content
                self.metadata = metadata or {}

try:
    from langchain_huggingface import HuggingFaceEmbeddings  # type: ignore
except Exception:  # pragma: no cover
    try:
        from langchain.embeddings import HuggingFaceEmbeddings  # type: ignore
    except Exception:  # pragma: no cover
        HuggingFaceEmbeddings = None  # type: ignore

from core.config import settings

_EMBEDDINGS = None  # lazy singleton


def _get_embeddings():  # pragma: no cover - trivial accessor
    global _EMBEDDINGS
    if _EMBEDDINGS is not None:
        return _EMBEDDINGS
    if HuggingFaceEmbeddings is None:
        return None
    try:
        _EMBEDDINGS = HuggingFaceEmbeddings(
            model_name=getattr(settings, 'EMBEDDING_MODEL', None),
            model_kwargs={"device": "cpu"},
        )
    except Exception as e:  # fallback to None
        print(f"⚠️ Rerank embeddings init failed: {e}")
        _EMBEDDINGS = None
    return _EMBEDDINGS


def _cosine(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    num = 0.0
    da = 0.0
    db = 0.0
    for x, y in zip(a, b):
        num += x * y
        da += x * x
        db += y * y
    if da == 0.0 or db == 0.0:
        return 0.0
    return num / math.sqrt(da * db)


def filter_documents_by_type(docs: List[Document], allowed_types: List[str]) -> List[Document]:
    allowed = set(t.strip().lower() for t in allowed_types if t.strip())
    if not allowed:
        return docs
    filtered = [d for d in docs if d.metadata.get('type', '').lower() in allowed]
    return filtered or docs  # never return empty if original non-empty (fallback)


def rerank_documents(question: str, docs: List[Document], top_n: int = 3) -> Tuple[List[Document], List[Tuple[int, float]]]:
    """Return (top_docs, score_tuples) after similarity rerank.

    score_tuples: list of (original_index, cosine_score) sorted descending.
    Falls back to original order if embeddings unavailable.
    """
    if top_n <= 0:
        return [], []
    embeddings = _get_embeddings()
    if embeddings is None:
        # Fallback: keep original order, assign descending pseudo-scores
        pseudo = list(reversed(range(len(docs))))
        scored = list(zip(range(len(docs)), pseudo))
        top_docs = docs[:top_n]
        return top_docs, scored

    try:
        q_emb = embeddings.embed_query(question)
        # Truncate doc content to reduce embedding cost (long tail often redundant)
        contents = [d.page_content[:1500] for d in docs]
        d_embs = embeddings.embed_documents(contents)
        scored = []
        for idx, emb in enumerate(d_embs):
            score = _cosine(q_emb, emb)
            scored.append((idx, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        ordered_docs = [docs[i] for i, _ in scored]
        return ordered_docs[:top_n], scored
    except Exception as e:  # pragma: no cover - robustness fallback
        print(f"⚠️ Rerank failure, using original order: {e}")
        scored = list((i, 0.0) for i in range(len(docs)))
        return docs[:top_n], scored


__all__ = [
    'rerank_documents',
    'filter_documents_by_type'
]
