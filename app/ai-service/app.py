from fastapi import FastAPI
import time
from core.ollama_client import _ping_ollama as _ping, _model_present, ensure_ollama_warm
from routes.ask import router as ask_router
from routes.evaluate import router as evaluate_router
from routes.indexing import router as indexing_router
from rag.vectorstore_manager import VectorStoreManager

app = FastAPI(title="GreenScore AI Service")

# Préchargement du vectordb au démarrage
@app.on_event("startup")
def preload_vectordb():
    print("🔄 Préchargement de la base vectorielle...")
    VectorStoreManager().get_vectordb()
    print("✅ Base vectorielle prête !")

# Routes
app.include_router(ask_router, prefix="/api")
app.include_router(evaluate_router, prefix="/api")
app.include_router(indexing_router, prefix="/api")

@app.get("/")
def root():
    return {"message": "GreenScore AI Service is running"}

_started_at = time.time()

@app.get("/api/health")
def health():
    warmed = ensure_ollama_warm()
    return {
        "status": "ok",
        "uptime_seconds": round(time.time() - _started_at, 2),
        "ollama": {
            "reachable": _ping(),
            "model_present": _model_present(),
            "warmed": warmed,
        },
        # Vector store presence (lazy load may still be in progress if cold start)
        "vector_index_loaded": VectorStoreManager().get_vectordb() is not None,
    }
