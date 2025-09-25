# ===== 5. evaluate.py (modifié avec debug) =====
from fastapi import APIRouter, Query
from rag.rag_chain import build_rag_chain
from rag.vectorstore_manager import VectorStoreManager
import time

router = APIRouter()
vector_store_manager = VectorStoreManager()
vectordb = vector_store_manager.get_vectordb()

@router.post("/evaluate")
def evaluate(product_description: str = Query(..., description="Description produit + emballage")):
    print(f"\n🌱 Évaluation demandée pour: {product_description[:100]}...")
    
    llm = None  # build_rag_chain appellera get_llm
    qa_chain = build_rag_chain(vectordb, llm=llm, k=3)

    query = (
        f"Évalue l'impact environnemental de ce produit: {product_description}\n"
        "Utilise uniquement les informations des documents fournis."
    )
    
    print(f"🔍 Query construite: {query[:150]}...")
    
    start_time = time.time()
    result = qa_chain.invoke({"query": query})
    total_time = time.time() - start_time
    
    answer = result.get("result", "")
    source_docs = result.get("source_documents", [])
    
    print(f"⏱️ Évaluation terminée en {total_time:.2f}s")
    print(f"📊 Réponse d'évaluation ({len(answer)} chars): {answer[:150]}...")

    return {
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