# config.py (version étendue avec plus d'options)
import os

class Settings:
    # Configuration Ollama
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://ollama:11434")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "phi3:mini")
    
    # Configuration RAG
    PDF_DIR: str = os.getenv("PDF_DIR", "./data")
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "400"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "50"))
    NUM_RETRIEVAL_DOCS: int = int(os.getenv("NUM_RETRIEVAL_DOCS", "3"))
    
    # Configuration embeddings
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    USE_OLLAMA_EMBEDDINGS: bool = os.getenv("USE_OLLAMA_EMBEDDINGS", "false").lower() == "true"
    OLLAMA_EMBEDDING_MODEL: str = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
    
    # Configuration LLM
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.1"))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "150"))
    
    # Debug
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "true").lower() == "true"

settings = Settings()

# Affichage de la config au démarrage (si debug activé)
if settings.DEBUG_MODE:
    print("🔧 Configuration chargée:")
    print(f"   Ollama: {settings.OLLAMA_HOST}")
    print(f"   Modèle: {settings.MODEL_NAME}")
    print(f"   Chunks: {settings.CHUNK_SIZE} chars, overlap {settings.CHUNK_OVERLAP}")
    print(f"   Embeddings: {settings.EMBEDDING_MODEL}")
    print(f"   Température: {settings.TEMPERATURE}")