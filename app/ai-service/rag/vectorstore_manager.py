import threading
from typing import Optional
from langchain.vectorstores import FAISS
from core.config import settings
from .loader import load_documents
from .vectorstore import create_vectorstore


class VectorStoreManager:
    """
    Gère le chargement lazy et le cache de la base vectorielle.
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._vectordb = None
                    cls._instance._initialized = False
        return cls._instance

    def get_vectordb(self) -> FAISS:
        """
        Retourne la base vectorielle, en la chargeant si nécessaire (lazy loading).
        """
        if not self._initialized:
            with self._lock:
                if not self._initialized:
                    print(f"Chargement des documents depuis le répertoire: {settings.PDF_DIR}")
                    docs = load_documents()
                    print(f"Création de la base vectorielle à partir de {len(docs)} documents...")
                    self._vectordb = create_vectorstore(docs)
                    print("Base vectorielle créée avec succès!")
                    self._initialized = True
        
        return self._vectordb