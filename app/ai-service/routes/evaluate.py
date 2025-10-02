# ===== 5. evaluate.py (modifié avec debug) =====
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
import asyncio
import json
from rag.rag_chain import build_rag_chain
from rag.vectorstore_manager import VectorStoreManager
import time
import traceback
from core.ollama_client import ensure_ollama_warm, get_llm
from core.config import settings

MAX_EVAL_RETRIES = 3
RETRY_BACKOFF_BASE = 0.75

router = APIRouter()
vector_store_manager = VectorStoreManager()
vectordb = vector_store_manager.get_vectordb()

async def generate_streaming_response(product_description: str, debug: bool = False):
    print(f"\n🌱 Évaluation demandée pour: {product_description[:100]}...")
    print("⚡ Démarrage du processus d'évaluation...")
    
    print("🔄 Initialisation LLM...")
    start_init = time.time()
    llm = get_llm() if not debug else None
    init_time = time.time() - start_init
    print(f"✅ LLM initialisé en {init_time:.1f}s")
    
    print("🔄 Construction de la chaîne RAG...")
    qa_chain = build_rag_chain(vectordb, llm=llm, k=settings.NUM_RETRIEVAL_DOCS, debug=debug)
    print("✅ Chaîne RAG construite")

    query = (
        "Tu es un expert en analyse environnementale qui doit évaluer l'impact d'un produit. "
        "Commence par une courte introduction narrative qui résume ton analyse de manière conversationnelle. "
        "Ensuite, fournis les détails techniques dans un format structuré.\n\n"
        f"Produit à évaluer: {product_description}"
    )
    print(f"🔍 Query construite: {query[:150]}...")

    if debug:
        print("🔧 Mode debug : récupération des top-k sans appeler le LLM")
        print("🔄 Exécution de la recherche de documents similaires...")
        debug_res = qa_chain.run_with_debug(query)
        print("✅ Recherche terminée")
        response = {
            "product": product_description,
            "debug": debug_res,
        }
        yield json.dumps(response)

    # Warmup Ollama (best-effort)
    warm_ok = ensure_ollama_warm()  # Non-async function
    if not warm_ok:
        print("⚠️ Warmup Ollama non confirmé (continuation quand même)")

    start_time = time.time()
    last_error = None
    result = None
    total_time = 0
    source_docs = []
    
    for attempt in range(1, MAX_EVAL_RETRIES + 1):
        try:
            print(f"🔄 Tentative d'évaluation {attempt}/{MAX_EVAL_RETRIES}...")
            print("📊 Démarrage de la génération...")
            gen_start = time.time()
            result = await qa_chain.ainvoke({"query": query})
            gen_time = time.time() - gen_start
            print(f"✅ Évaluation réussie! (temps: {gen_time:.1f}s)")
            total_time = time.time() - start_time
            if isinstance(result, dict):
                source_docs = result.get("source_documents", [])
                if "result" in result:
                    result = result["result"]
            break
        except Exception as e:
            last_error = e
            delay = round(RETRY_BACKOFF_BASE * attempt, 2)
            print(f"❌ Échec tentative {attempt}/{MAX_EVAL_RETRIES}: {e} (retry in {delay}s)")
            await asyncio.sleep(delay)
    else:
        # All retries failed
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
            "evaluation_length": len(answer)
        }
    }
    
    print(f"⏱️ Évaluation terminée en {total_time:.2f}s")
    print(f"📊 Réponse d'évaluation ({len(answer)} chars): {answer}")
    
    # Stream the response as chunks
    json_str = json.dumps(response)
    chunk_size = 1024
    for i in range(0, len(json_str), chunk_size):
        yield json_str[i:i+chunk_size]

from pydantic import BaseModel

class ProductRequest(BaseModel):
    product_description: str
    debug: bool = False

@router.post("/evaluate")
async def evaluate(request: ProductRequest):
    return StreamingResponse(
        generate_streaming_response(request.product_description, request.debug),
        media_type="application/json"
    )