from fastapi import FastAPI
from routes.ask import router as ask_router
from routes.evaluate import router as evaluate_router
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

@app.get("/")
def root():
    return {"message": "GreenScore AI Service is running"}
