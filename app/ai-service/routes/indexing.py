from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from pydantic import BaseModel
from rag.vectorstore_manager import VectorStoreManager
from rag.loader import load_all_documents
from rag.vectorstore import create_vectorstore
from rag.scripts.smoke_check import DEFAULT_QUERIES
from rag.scripts.smoke_check import load_index as smoke_load_index
from core.config import settings
import threading
import os

router = APIRouter()
vsm = VectorStoreManager()


class SearchRequest(BaseModel):
    query: str
    k: int = 3


@router.post('/reindex')
def reindex(background_tasks: BackgroundTasks, sync: bool = Query(False, description="Run reindex synchronously"), verify: bool = Query(False, description="Run smoke-check verification after reindex")):
    """Trigger a reindex. By default runs in background; set sync=true to run inline."""
    sm_result = None

    def _run():
        try:
            docs = load_all_documents()
            create_vectorstore(docs, persist_path=os.path.join(settings.FAISS_DIR, 'main_index'))
            # Reset manager so next get will reload the new index
            vsm._initialized = False
            vsm._vectordb = None
            if verify:
                try:
                    idx = smoke_load_index(os.path.join(settings.FAISS_DIR, 'main_index'))
                    verification = {}
                    for q in DEFAULT_QUERIES:
                        try:
                            res = idx.similarity_search_with_score(q, k=3)
                            rows = []
                            if res and isinstance(res[0], tuple):
                                for doc, score in res:
                                    rows.append({'score': float(score), 'source': doc.metadata.get('source'), 'snippet': (doc.page_content or '')[:300]})
                            else:
                                for doc in res:
                                    rows.append({'score': None, 'source': doc.metadata.get('source'), 'snippet': (doc.page_content or '')[:300]})
                            verification[q] = rows
                        except Exception as e:
                            verification[q] = {'error': str(e)}
                    nonlocal sm_result
                    sm_result = {'verification': verification}
                except Exception as e:
                    sm_result = {'error': str(e)}
        except Exception as e:
            print('Reindex error:', e)

    if sync:
        _run()
        resp = {"status": "reindex_completed"}
        if verify:
            resp['verification'] = sm_result
        return resp
    else:
        background_tasks.add_task(_run)
        return {"status": "reindex_started"}


@router.post('/search')
def search(req: SearchRequest):
    vectordb = vsm.get_vectordb()
    if not vectordb:
        raise HTTPException(status_code=500, detail='Vectorstore not available')
    # Use the vectorstore directly to obtain scores
    try:
        results = vectordb.similarity_search_with_score(req.query, k=req.k)
    except Exception:
        # Fallback to retriever API if direct call not supported
        retriever = vectordb.as_retriever(search_type='similarity', search_kwargs={'k': req.k})
        docs = retriever.get_relevant_documents(req.query)
        results = [(d, None) for d in docs]

    def sanitize_meta(meta: dict):
        if not meta:
            return {}
        safe = {}
        for k, v in meta.items():
            if k in ['source', 'page', 'chunk', 'row']:
                safe[k] = v
            else:
                # keep small primitive values only
                if isinstance(v, (str, int, float, bool)):
                    s = str(v)
                    if len(s) > 200:
                        s = s[:200]
                    safe[k] = s
        return safe

    out = []
    for item in results:
        if isinstance(item, tuple) and len(item) == 2:
            doc, score = item
        else:
            doc = item
            score = None
        snippet = (doc.page_content or '')
        # collapse whitespace and cap length
        snippet = ' '.join(snippet.split())[:300]
        out.append({
            'score': float(score) if score is not None else None,
            'source': doc.metadata.get('source'),
            'page': doc.metadata.get('page'),
            'snippet': snippet,
            'metadata': sanitize_meta(doc.metadata)
        })

    return {'query': req.query, 'k': req.k, 'results': out}
