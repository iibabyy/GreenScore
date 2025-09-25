from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings

def create_vectorstore(docs):
    print(f"📄 Création de la vectorstore à partir de {len(docs)} documents")
    
    # Chunks plus petits pour Phi3:mini
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,  # Réduit de 750 à 400
        chunk_overlap=50,  # Réduit de 100 à 50
        separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""]
    )
    chunks = splitter.split_documents(docs)
    print(f"✂️ Documents découpés en {len(chunks)} chunks")

    # Modèle multilingue plus performant pour le français
    print("🔤 Chargement du modèle d'embeddings multilingue...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        model_kwargs={'device': 'cpu'}  # Forcé sur CPU
    )
      # Option 2: Si vous avez nomic-embed-text dans Ollama (recommandé)
      # from langchain.embeddings import OllamaEmbeddings
      # embeddings = OllamaEmbeddings(
      #     model="nomic-embed-text",
      #     base_url="http://ollama:11434"
      # )

    print("🗄️ Création de la base vectorielle FAISS...")
    vectordb = FAISS.from_documents(chunks, embeddings)
    print("✅ Base vectorielle créée avec succès!")
    return vectordb

