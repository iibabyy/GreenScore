from fastapi import FastAPI, Request
import time
import json
import os
from core.ollama_client import _ping_ollama as _ping, _model_present, ensure_ollama_warm
from routes.ask import router as ask_router
from routes.evaluate import router as evaluate_router
from routes.indexing import router as indexing_router
from rag.vectorstore_manager import VectorStoreManager

app = FastAPI(title="GreenScore AI Service")

# Metrics basiques en mémoire (non thread-safe perfection mais suffisant)
METRICS = {"http_requests": 0, "cache_hits": 0, "cache_miss": 0}


def log_event(event: str, **fields):
    rec = {"event": event, **fields, "ts": round(time.time(), 3)}
    print(json.dumps(rec, ensure_ascii=False))

# Préchargement du vectordb au démarrage
@app.on_event("startup")
def preload_vectordb():
    if os.getenv("PRELOAD_VECTORSTORE", "true").lower() == "true":
        log_event("vectordb_preload_start")
        VectorStoreManager().get_vectordb()
        log_event("vectordb_preload_done")
    else:
        log_event("vectordb_preload_skipped")


@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    dur_ms = (time.perf_counter() - start) * 1000
    METRICS["http_requests"] += 1
    log_event("http_request", path=request.url.path, method=request.method, status=response.status_code, ms=round(dur_ms,2))
    return response

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
    # Soft check vectordb: ne force pas chargement complet si désactivé
    vs_loaded = VectorStoreManager()._initialized  # type: ignore
    return {
        "status": "ok",
        "uptime_seconds": round(time.time() - _started_at, 2),
        "ollama": {
            "reachable": _ping(),
            "model_present": _model_present(),
            "warmed": warmed,
        },
        "vector_index_loaded": vs_loaded,
    }

@app.get('/api/metrics')
def metrics():
    return METRICS
