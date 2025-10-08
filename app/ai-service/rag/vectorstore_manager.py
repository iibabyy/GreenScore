import threading
import os
import json
from typing import Optional
from core.config import settings
from .loader import load_documents
from .vectorstore import create_vectorstore

try:
    from langchain_community.vectorstores import FAISS
except Exception:
    from langchain.vectorstores import FAISS
    
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except Exception:
    try:
        from langchain.embeddings import HuggingFaceEmbeddings
    except Exception:
        HuggingFaceEmbeddings = None


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
                    # If a persisted FAISS index exists, load it (preferred)
                    persist_dir = os.path.join(settings.FAISS_DIR, 'main_index', 'faiss_index')
                    meta_path = os.path.join(settings.FAISS_DIR, 'main_index', 'embedding_meta.json')
                    if os.path.isdir(persist_dir):
                        print(f"Chargement de l'index FAISS persistant depuis: {persist_dir}")
                        try:
                            if HuggingFaceEmbeddings is None:
                                raise ImportError("HuggingFaceEmbeddings not available to load persisted index")
                            embeddings = HuggingFaceEmbeddings(
                                model_name=getattr(settings, 'EMBEDDING_MODEL', None),
                                model_kwargs={'device': 'cpu'}
                            )
                            # allow_dangerous_deserialization True because index is local/trusted
                            self._vectordb = FAISS.load_local(persist_dir, embeddings, allow_dangerous_deserialization=True)
                            # Vérification meta si présent
                            if os.path.isfile(meta_path):
                                try:
                                    with open(meta_path, 'r', encoding='utf-8') as fh:
                                        meta = json.load(fh)
                                    expected = getattr(settings, 'EMBEDDING_MODEL', '')
                                    if meta.get('embedding_model') != expected:
                                        print(f"⚠️ Mismatch embedding_model meta={meta.get('embedding_model')} != runtime={expected}")
                                except Exception as me:
                                    print(f"⚠️ Lecture meta échouée: {me}")
                            print("Index FAISS chargé avec succès depuis le disque.")
                            self._initialized = True
                            return self._vectordb
                        except Exception as e:
                            print(f"Erreur lors du chargement de l'index persistant: {e}")

                    # Fallback: build from documents
                    print(f"Chargement des documents depuis le répertoire: {settings.PDF_DIR}")
                    docs = load_documents()
                    print(f"Création de la base vectorielle à partir de {len(docs)} documents...")
                    self._vectordb = create_vectorstore(docs)
                    print("Base vectorielle créée avec succès!")
                    self._initialized = True
        
        return self._vectordb