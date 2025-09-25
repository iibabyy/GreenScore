from langchain.llms import Ollama
from .config import settings

def get_llm():
    """Retourne une instance du client Ollama avec paramètres optimisés pour RAG."""
    return Ollama(
        model=settings.MODEL_NAME, 
        base_url=settings.OLLAMA_HOST,
        # Paramètres pour limiter les hallucinations
        temperature=0.1,  # Très bas pour plus de consistance
        top_p=0.9,
        repeat_penalty=1.1,
        # Limite la longueur pour forcer la concision
        num_predict=200,  # Maximum 200 tokens de réponse
    )