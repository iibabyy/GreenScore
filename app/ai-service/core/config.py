# config.py (version étendue avec plus d'options)
import os

class Settings:
    # Configuration Ollama
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://ollama:11434")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "phi3:mini")
    
    # Configuration RAG / data layout
    DATA_DIR: str = os.getenv("DATA_DIR", "./data")
    PDF_DIR: str = os.getenv("PDF_DIR", "./data/pdf")
    CSV_DIR: str = os.getenv("CSV_DIR", "./data/csv")
    JSON_DIR: str = os.getenv("JSON_DIR", "./data/json")
    WEB_DIR: str = os.getenv("WEB_DIR", "./data/web")
    RAW_DIR: str = os.getenv("RAW_DIR", "./data/raw")
    PROCESSED_DIR: str = os.getenv("PROCESSED_DIR", "./data/processed")
    FAISS_DIR: str = os.getenv("FAISS_DIR", "./data/faiss")
    SCRAPE_INDEX: str = os.getenv("SCRAPE_INDEX", "./data/scrape_index.csv")
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    NUM_RETRIEVAL_DOCS: int = int(os.getenv("NUM_RETRIEVAL_DOCS", "6"))
    
    # Configuration embeddings
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    USE_OLLAMA_EMBEDDINGS: bool = os.getenv("USE_OLLAMA_EMBEDDINGS", "false").lower() == "true"
    OLLAMA_EMBEDDING_MODEL: str = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
    
    # Configuration LLM
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.1"))
    # Reduced to 1000 tokens since responses are typically around 1500 chars
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "500"))
    
    # Debug
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "true").lower() == "true"
    # Scraper defaults
    SCRAPER_USER_AGENT: str = os.getenv("SCRAPER_USER_AGENT", "my-rag-bot/0.1 - contact: you@example.com")
    SCRAPER_RATE_LIMIT: float = float(os.getenv("SCRAPER_RATE_LIMIT", "1.0"))  # req/sec per domain

settings = Settings()

# Affichage de la config au démarrage (si debug activé)
if settings.DEBUG_MODE:
    print("🔧 Configuration chargée:")
    print(f"   Ollama: {settings.OLLAMA_HOST}")
    print(f"   Modèle: {settings.MODEL_NAME}")
    print(f"   Chunks: {settings.CHUNK_SIZE} chars, overlap {settings.CHUNK_OVERLAP}")
    print(f"   Embeddings: {settings.EMBEDDING_MODEL}")
    print(f"   Température: {settings.TEMPERATURE}")
    print(f"   Max tokens (LLM): {settings.MAX_TOKENS}")


# If running inside Docker, avoid using localhost for service discovery — prefer the docker service name.
def _running_in_docker() -> bool:
    try:
        # /.dockerenv is present in many Docker containers
        if os.path.exists('/.dockerenv'):
            return True
        # Fallback: check cgroup for docker/kubernetes identifiers
        with open('/proc/1/cgroup', 'rt') as f:
            content = f.read()
            if 'docker' in content or 'kubepods' in content:
                return True
    except Exception:
        pass
    return False


# Auto-fix common misconfiguration: when running inside container and OLLAMA_HOST points to localhost,
# switch to the docker service hostname `http://ollama:11434` which the compose file exposes.
if _running_in_docker():
    try:
        ll = settings.OLLAMA_HOST.lower()
        if 'localhost' in ll or ll.startswith('127.'):
            old = settings.OLLAMA_HOST
            settings.OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://ollama:11434') or 'http://ollama:11434'
            if settings.DEBUG_MODE:
                print(f"🔁 Running in container: overriding OLLAMA_HOST {old} -> {settings.OLLAMA_HOST}")
    except Exception:
        # best-effort, don't crash on startup
        if settings.DEBUG_MODE:
            print("⚠️ Could not auto-fix OLLAMA_HOST for container environment")

# Ensure data directories exist (safe to call on startup)
_data_dirs = [
    settings.DATA_DIR,
    settings.PDF_DIR,
    settings.CSV_DIR,
    settings.JSON_DIR,
    settings.WEB_DIR,
    settings.RAW_DIR,
    settings.PROCESSED_DIR,
    settings.FAISS_DIR,
]
for _d in _data_dirs:
    try:
        os.makedirs(_d, exist_ok=True)
    except Exception:
        # best-effort; do not fail the service if directory creation is blocked
        if settings.DEBUG_MODE:
            print(f"⚠️ Could not create data dir: {_d}")