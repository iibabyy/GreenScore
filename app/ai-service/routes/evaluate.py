# ===== 5. evaluate.py (modifié avec query narrative fluide) =====
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from core.ollama_client import get_llm
import asyncio
import json
# NOTE: Pour l'évaluation anti-hallucination nous effectuons une récupération manuelle
# puis (optionnel) un rerank + filtrage pour contrôler précisément le contexte fourni au LLM
from rag.rerank import rerank_documents, filter_documents_by_type
from rag.vectorstore_manager import VectorStoreManager
import time
import traceback
from core.ollama_client import ensure_ollama_warm
from core.config import settings
import os

MAX_EVAL_RETRIES = 3
RETRY_BACKOFF_BASE = 0.75
MAX_TOTAL_SECONDS = 45  # coupe après cette durée globale

router = APIRouter()
vector_store_manager = VectorStoreManager()
vectordb = vector_store_manager.get_vectordb()

async def generate_streaming_response(product_description: str, debug: bool = False,
                                      rerank: bool = False, source_filter: str = "", top_n: int = 3):
    print(f"\n🌱 Évaluation demandée pour: {product_description[:100]}...")
    print("⚡ Démarrage du processus d'évaluation...")
    
    print("🔄 Initialisation LLM (factory)...")
    start_init = time.time()
    llm = get_llm()
    init_time = time.time() - start_init
    print(f"✅ LLM prêt (factory) en {init_time:.1f}s")
    
    # --- 1. Récupération initiale des documents ---
    base_k = max(top_n, settings.NUM_RETRIEVAL_DOCS)
    print(f"� Récupération initiale top-k (k={base_k})")
    try:
        docs_and_scores = vectordb.similarity_search_with_score(product_description, k=base_k)
    except Exception:
        print("⚠️ similarity_search_with_score a échoué, fallback get_relevant_documents")
        retriever = vectordb.as_retriever(search_kwargs={"k": base_k})
        fallback_docs = retriever.get_relevant_documents(product_description)
        docs_and_scores = [(d, None) for d in fallback_docs]

    candidate_docs = [d for d, _ in docs_and_scores]
    original_candidate_count = len(candidate_docs)
    print(f"📚 {original_candidate_count} candidats avant filtrage/rerank")

    # --- 2. Filtrage par type de source ---
    applied_source_filter = None
    if source_filter.strip():
        types = [t.strip() for t in source_filter.split(',') if t.strip()]
        if types:
            filtered_docs = filter_documents_by_type(candidate_docs, types)
            if filtered_docs is not candidate_docs:
                applied_source_filter = ','.join(types)
            candidate_docs = filtered_docs
            print(f"🔧 Filtrage sources appliqué: {applied_source_filter or 'aucun changement'} -> {len(candidate_docs)} docs")

    # --- 3. Rerank optionnel ---
    rerank_scores = []
    rerank_applied = False
    if rerank and len(candidate_docs) > 1:
        top_docs, scored = rerank_documents(product_description, candidate_docs, top_n=top_n)
        rerank_applied = True
        rerank_scores = scored[:len(top_docs)]
        selected_docs = top_docs
        print(f"🏅 Rerank appliqué -> {len(selected_docs)} docs")
    else:
        selected_docs = candidate_docs[:top_n]
        print(f"➡️ Pas de rerank -> tronqué à {len(selected_docs)} docs")

    # --- 4. Construction contexte contrôlé ---
    context_fragments = []
    for idx, d in enumerate(selected_docs, 1):
        src = d.metadata.get('source', 'unknown')
        snippet = ' '.join(d.page_content.split())[:1500]
        context_fragments.append(f"[DOC {idx} | {src}] {snippet}")
    context_text = "\n\n".join(context_fragments)

    # Query optimisée pour un texte fluide, narratif, avec intégration naturelle des scores
    query = f"""
Tu es un expert en analyse environnementale, mais tu t'adresses à quelqu'un de curieux, pas à un spécialiste.
Ton objectif est d'expliquer de manière claire, engageante et naturelle l'impact écologique du produit suivant : {product_description}.

Utilise UNIQUEMENT les informations factuelles suivantes (ne pas inventer de faits absents) :\n\n{context_text}\n\n---\n
Rédige le texte de manière fluide et humaine, en intégrant les données dans les phrases (pas de listes brutes).
- Décris chaque étape du cycle (production, transport, emballage)
- Ajoute des recommandations concrètes à la fin intégrées dans le récit
- Si une donnée manque écris "Non disponible"
- Style: naturel, accessible, conversationnel
"""
    print(f"🔍 Query construite: {query[:150]}...")

    if debug:
        print("🔧 Mode debug : affichage des documents sélectionnés")
        debug_docs = [
            {
                "source": d.metadata.get('source', 'unknown'),
                "preview": d.page_content[:400]
            } for d in selected_docs
        ]
        response = {
            "product": product_description,
            "debug": {
                "selected_docs": debug_docs,
                "original_candidate_count": original_candidate_count,
                "applied_source_filter": applied_source_filter,
                "rerank_applied": rerank_applied,
                "rerank_scores": rerank_scores[:10]
            },
        }
        yield json.dumps(response)

    # Warmup Ollama (best-effort)
    warm_ok = ensure_ollama_warm()
    if not warm_ok:
        print("⚠️ Warmup Ollama non confirmé (continuation quand même)")

    start_time = time.time()
    last_error = None
    result = None
    total_time = 0
    source_docs = selected_docs  # ceux réellement fournis

    def _generate_answer(prompt: str):
        # Tente différentes interfaces (invoke / __call__ / run)
        try:
            if hasattr(llm, 'invoke'):
                r = llm.invoke(prompt)
                if isinstance(r, dict):
                    return r.get('result') or r.get('text') or str(r)
                return r
            if callable(llm):
                r = llm(prompt)
                if isinstance(r, dict):
                    return r.get('result') or r.get('text') or str(r)
                return r
            if hasattr(llm, 'run'):
                return llm.run(prompt)
        except Exception as e:
            return f"<error: {e}>"
        return "<vide>"

    for attempt in range(1, MAX_EVAL_RETRIES + 1):
        try:
            print(f"🔄 Tentative d'évaluation {attempt}/{MAX_EVAL_RETRIES}...")
            gen_start = time.time()
            # Exécuter génération dans un thread pour ne pas bloquer event loop
            result = await asyncio.to_thread(_generate_answer, query)
            gen_time = time.time() - gen_start
            print(f"✅ Génération réussie! (temps: {gen_time:.1f}s)")
            total_time = time.time() - start_time
            break
        except Exception as e:
            last_error = e
            total_time = time.time() - start_time
            if total_time > MAX_TOTAL_SECONDS:
                print("⏱️ Timeout global atteint, arrêt des retries")
                break
            # jitter exponentiel
            base = RETRY_BACKOFF_BASE * (2 ** (attempt - 1))
            jitter = 0.2 * base
            delay = min(base + (jitter * (0.5)), 8.0)
            print(f"❌ Échec tentative {attempt}/{MAX_EVAL_RETRIES}: {e} (retry in {delay:.2f}s)")
            await asyncio.sleep(delay)
    else:
        tb = traceback.format_exc(limit=3)
        error_response = {
            "error": "Échec de génération après retries",
            "type": last_error.__class__.__name__ if last_error else "Unknown",
            "message": str(last_error),
            "trace": tb.splitlines(),
            "retries": MAX_EVAL_RETRIES,
        }
        yield json.dumps(error_response)

    answer = result or "<vide>"

    # --- 5. Heuristique overlap (approximation similarité contenu) ---
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
    
    response = {
        "product": product_description,
        "evaluation": answer,
        "evaluation_time_seconds": round(total_time, 2),
        "source_documents": [
            {
                "source": doc.metadata.get("source", "unknown"),
                "page": doc.metadata.get("page", None),
                "text_snippet": doc.page_content[:400]
            }
            for doc in source_docs
        ],
        "debug_info": {
            "num_source_docs": len(source_docs),
            "evaluation_length": len(answer),
            "overlap_ratio": overlap_ratio,
            "rerank_applied": rerank_applied,
            "applied_source_filter": applied_source_filter,
            "original_candidate_count": original_candidate_count,
            "rerank_scores": rerank_scores[:10]
        }
    }
    
    print(f"⏱️ Évaluation terminée en {total_time:.2f}s")
    print(f"📊 Réponse d'évaluation ({len(answer)} chars)")

    # Stream the response as chunks
    json_str = json.dumps(response)
    chunk_size = 1024
    for i in range(0, len(json_str), chunk_size):
        yield json_str[i:i+chunk_size]

from pydantic import BaseModel

class ProductRequest(BaseModel):
    product_description: str
    debug: bool = False
    rerank: bool = False
    source_filter: str | None = None
    top_n: int = 3

@router.post("/evaluate")
async def evaluate(request: ProductRequest):
    if len(request.product_description) > 1000:
        raise HTTPException(status_code=400, detail="Description produit trop longue (>1000 caractères)")
    if request.top_n < 1 or request.top_n > 10:
        raise HTTPException(status_code=400, detail="top_n doit être entre 1 et 10")
    return StreamingResponse(
        generate_streaming_response(
            request.product_description,
            request.debug,
            rerank=request.rerank,
            source_filter=request.source_filter or "",
            top_n=request.top_n
        ),
        media_type="application/json"
    )