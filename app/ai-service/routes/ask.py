# ===== 4. ask.py (modifié avec debug complet) =====
from fastapi import APIRouter, Query, HTTPException
from core.ollama_client import get_llm
from core.cache import cached_answer
from rag.rag_chain import build_rag_chain
from rag.rerank import rerank_documents, filter_documents_by_type
from rag.vectorstore_manager import VectorStoreManager
import re
import time

router = APIRouter()
vector_store_manager = VectorStoreManager()
vectordb = vector_store_manager.get_vectordb()

def extract_quoted_blocks(text: str):
    """Extrait les blocs formatés [SOURCE] ```...``` du texte retourné par le LLM."""
    pattern = r"\[([^\]]+)\]\s*```(.*?)```"
    return re.findall(pattern, text, flags=re.S)

def verify_blocks_in_sources(blocks, source_docs):
    """Vérifie que chaque bloc de texte extrait figure bien dans au moins un source_doc."""
    results = []
    for source_label, extrait in blocks:
        extrait_clean = extrait.strip()
        found = any(extrait_clean in doc.page_content for doc in source_docs)
        results.append((source_label, extrait_clean, found))
    return results

@router.post("/debug-retrieval")
def debug_retrieval(question: str = Query(..., description="Question pour tester la récupération")):
    """Route de debug pour vérifier la qualité de la récupération des documents"""
    print(f"🔍 DEBUG RETRIEVAL - Question: {question}")
    
    retriever = vectordb.as_retriever(search_type="similarity", search_kwargs={"k": 5})
    start_time = time.time()
    retrieved_docs = retriever.get_relevant_documents(question)
    retrieval_time = time.time() - start_time
    
    print(f"⏱️ Temps de récupération: {retrieval_time:.2f}s")
    print(f"📚 Documents récupérés: {len(retrieved_docs)}")
    
    for i, doc in enumerate(retrieved_docs):
        print(f"📄 Doc {i+1}: {doc.metadata.get('source', 'unknown')} - Page {doc.metadata.get('page', '?')}")
        print(f"   Contenu (100 premiers chars): {doc.page_content[:100]}...")
    
    return {
        "question": question,
        "retrieval_time_seconds": round(retrieval_time, 2),
        "num_documents_found": len(retrieved_docs),
        "retrieved_documents": [
            {
                "source": doc.metadata.get("source", "unknown"),
                "page": doc.metadata.get("page", "unknown"),
                "content_preview": doc.page_content[:400],
                "content_length": len(doc.page_content)
            }
            for doc in retrieved_docs
        ]
    }

MAX_QUESTION_LEN = 500

PROMPT_VERSION = "analysis_v1"

@router.post("/ask")
def ask(
    question: str = Query(..., description="Question à poser au modèle"),
    rerank: bool = Query(False, description="Activer le reranking secondaire (embedding cosine)"),
    source_filter: str = Query("", description="Filtrer types sources ex: csv,pdf,html"),
    top_n: int = Query(3, ge=1, le=10, description="Nombre final de documents après rerank"),
):
    if len(question) > MAX_QUESTION_LEN:
        raise HTTPException(status_code=400, detail=f"Question trop longue (>{MAX_QUESTION_LEN} caractères)")
    print(f"\n🤔 Question reçue: {question}")
    
    # 1. Récupération des documents (une seule fois)
    base_k = max(top_n, 5)  # récupérer un peu plus pour permettre un rerank utile
    retriever = vectordb.as_retriever(search_type="similarity", search_kwargs={"k": base_k})
    start_retrieval = time.time()
    retrieved_docs = retriever.get_relevant_documents(question)

    original_docs = list(retrieved_docs)  # copy for debug

    # 2.a Filtrage des sources (type) si demandé
    applied_filter = None
    if source_filter.strip():
        types = [t.strip() for t in source_filter.split(',') if t.strip()]
        if types:
            filtered_docs = filter_documents_by_type(retrieved_docs, types)
            if filtered_docs is not retrieved_docs:
                applied_filter = ','.join(types)
            retrieved_docs = filtered_docs

    # 2.b Rerank si demandé
    rerank_scores = []
    rerank_applied = False
    if rerank and len(retrieved_docs) > 1:
        top_docs, scored = rerank_documents(question, retrieved_docs, top_n=top_n)
        rerank_applied = True
        rerank_scores = scored[:len(top_docs)]
        retrieved_docs = top_docs
    else:
        # Tronquer à top_n si pas de rerank
        retrieved_docs = retrieved_docs[:top_n]
    retrieval_time = time.time() - start_retrieval

    # 2. Construction de la chaîne RAG (LLM + prompt) après avoir les docs
    llm = get_llm()
    qa_chain = build_rag_chain(vectordb, llm=llm, k=base_k)
    
    print(f"🔍 Récupération terminée en {retrieval_time:.2f}s")
    print(f"📚 {len(retrieved_docs)} documents récupérés:")
    for i, doc in enumerate(retrieved_docs):
        source = doc.metadata.get("source", "unknown")
        page = doc.metadata.get("page", "?")
        print(f"   📄 Doc {i+1}: {source} (page {page}) - {len(doc.page_content)} chars")
    
    # 3. Génération de la réponse (avec cache)
    print(f"🤖 Génération de la réponse avec {llm.model} (cache support)...")
    def _gen():
        return qa_chain.invoke({"query": question})
    start_generation = time.time()
    result, from_cache = cached_answer(question, PROMPT_VERSION, _gen)
    generation_time = time.time() - start_generation
    answer = result.get("result", "") if isinstance(result, dict) else str(result)
    source_docs = (result.get("source_documents", []) if isinstance(result, dict) else []) or retrieved_docs

    # 3.b Heuristique overlap réponse / sources (approximate anti-hallucination metric)
    answer_tokens = set(answer.lower().split()) if isinstance(answer, str) else set()
    source_tokens = set()
    for d in source_docs:
        try:
            source_tokens.update(d.page_content.lower().split())
        except Exception:
            pass
    overlap_ratio = 0.0
    if answer_tokens:
        common = answer_tokens.intersection(source_tokens)
        overlap_ratio = round(len(common) / max(1, len(answer_tokens)), 4)
    
    print(f"⏱️ Génération terminée en {generation_time:.2f}s")
    print(f"📝 Réponse générée ({len(answer)} caractères):")
    print(f"   {answer[:200]}{'...' if len(answer) > 200 else ''}")
    
    # 4. Vérification des citations (optionnel)
    blocks = extract_quoted_blocks(answer)
    verification = verify_blocks_in_sources(blocks, source_docs)
    
    warnings = []
    for (src_label, extrait, found) in verification:
        if not found:
            warnings.append({
                "source_label": src_label,
                "excerpt": extrait,
                "status": "NOT_FOUND_IN_DOCS"
            })
    
    if warnings:
        print(f"⚠️ {len(warnings)} citations non vérifiées détectées")
    
    return {
        "question": question,
        "answer": answer,
        "timings": {
            "retrieval_seconds": round(retrieval_time, 2),
            "generation_seconds": round(generation_time, 2),
            "total_seconds": round(retrieval_time + generation_time, 2)
        },
        "source_documents": [
            {
                "source": doc.metadata.get("source", "unknown"), 
                "page": doc.metadata.get("page", None), 
                "text_snippet": doc.page_content[:300]
            }
            for doc in source_docs
        ],
        "debug_info": {
            "num_retrieved_docs": len(retrieved_docs),
            "answer_length": len(answer),
            "warnings_count": len(warnings),
            "cache_hit": from_cache,
            "rerank_applied": rerank_applied,
            "applied_source_filter": applied_filter,
            "rerank_scores": rerank_scores[:10],
            "original_candidate_count": len(original_docs),
            "overlap_ratio": overlap_ratio
        },
        "warnings": warnings
    }
# Note: Les warnings contiennent les extraits non trouvés dans les documents récupérés