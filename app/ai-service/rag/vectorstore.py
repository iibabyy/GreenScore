from langchain.text_splitter import RecursiveCharacterTextSplitter
from core.config import settings
import math
import os
import json
import hashlib
try:
    # Prefer community/huggingface packages when available
    from langchain_huggingface import HuggingFaceEmbeddings
except Exception:
    try:
        from langchain.embeddings import HuggingFaceEmbeddings
    except Exception:
        HuggingFaceEmbeddings = None

try:
    from langchain_community.vectorstores import FAISS
except Exception:
    from langchain.vectorstores import FAISS

def create_vectorstore(docs, persist_path: str = None, batch_size: int = 1024):
    """Create a FAISS vectorstore from a list of LangChain Documents.

    - Uses chunking parameters from `core.config.settings` (CHUNK_SIZE, CHUNK_OVERLAP).
    - Batches embedding and adding to FAISS to handle large datasets without OOM.
    - Optionally persists the index to disk under `persist_path`.
    """
    # Count by declared metadata types when available
    type_counts = {}
    for d in docs:
        try:
            t = d.metadata.get('type')
        except Exception:
            t = None
        type_counts[t or 'unknown'] = type_counts.get(t or 'unknown', 0) + 1

    print(f"📄 Création de la vectorstore à partir de {len(docs)} documents")
    for k, v in type_counts.items():
        print(f"   - {k}: {v}")

    chunk_size = getattr(settings, 'CHUNK_SIZE', 400)
    chunk_overlap = getattr(settings, 'CHUNK_OVERLAP', 50)

    # Configure splitter tuned for small models like Phi3:mini
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""]
    )

    chunks = splitter.split_documents(docs)
    print(f"✂️ Documents découpés en {len(chunks)} chunks (chunk_size={chunk_size}, overlap={chunk_overlap})")

    # Example chunk metadata preview (helpful for debugging multi-source inputs)
    try:
        sample_meta = [getattr(c, 'metadata', {}) for c in (chunks[:10] or [])]
        print(f"   (exemple metadata chunks: {sample_meta[:3]})")
    except Exception:
        pass

    # Multilingual embeddings for French
    print("🔤 Chargement du modèle d'embeddings multilingue...")
    if HuggingFaceEmbeddings is None:
        raise ImportError("HuggingFaceEmbeddings not available. Please install langchain-huggingface or ensure langchain provides HuggingFaceEmbeddings.")

    embeddings = HuggingFaceEmbeddings(
        model_name=getattr(settings, 'EMBEDDING_MODEL', 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'),
        model_kwargs={'device': 'cpu'}
    )
      # Option 2: Si vous avez nomic-embed-text dans Ollama (recommandé)
      # from langchain.embeddings import OllamaEmbeddings
      # embeddings = OllamaEmbeddings(
      #     model="nomic-embed-text",
      #     base_url="http://ollama:11434"
      # )

    print("🗄️ Création de la base vectorielle FAISS (batching pour grande volumétrie)...")

    # If persist_path exists and contains an index, load it to append
    if persist_path:
        os.makedirs(persist_path, exist_ok=True)
        index_path = os.path.join(persist_path, "faiss_index")
    else:
        index_path = None

    # Create an empty FAISS store and add in batches to avoid memory peaks
    # Use from_documents for small datasets, but for large sets, build incrementally
    total = len(chunks)
    if total == 0:
        print("⚠️ Aucun chunk à indexer")
        return None

    # For small datasets, fallback to simple creation
    if total <= batch_size:
        vectordb = FAISS.from_documents(chunks, embeddings)
    else:
        # Create first batch as base
        first_batch = chunks[:batch_size]
        vectordb = FAISS.from_documents(first_batch, embeddings)
        # Add remaining in batches
        for start in range(batch_size, total, batch_size):
            end = min(start + batch_size, total)
            batch = chunks[start:end]
            print(f"Ajout des chunks {start}-{end} / {total}...")
            vectordb.add_documents(batch)

    # Optionally persist the FAISS index to disk (depends on FAISS wrapper implementation)
    if index_path:
        try:
            print(f"💾 Sauvegarde de l'index FAISS dans {index_path}...")
            vectordb.save_local(index_path)
            # Écriture métadonnées index
            meta = {
                "embedding_model": getattr(settings, 'EMBEDDING_MODEL', ''),
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "doc_count": len(docs),
                "chunk_count": len(chunks),
            }
            # Hash simple du nombre de chunks + nom modèle (signature rapide)
            raw_sig = f"{meta['embedding_model']}:{meta['chunk_count']}:{meta['chunk_size']}".encode()
            meta['signature'] = hashlib.sha256(raw_sig).hexdigest()[:16]
            with open(os.path.join(persist_path, 'embedding_meta.json'), 'w', encoding='utf-8') as fh:
                json.dump(meta, fh, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde locale du vectordb: {e}")

    print("✅ Base vectorielle créée avec succès!")
    return vectordb

