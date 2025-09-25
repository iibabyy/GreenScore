from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from core.ollama_client import get_llm

def build_rag_chain(vectordb, llm=None, k: int = 3):
    """
    Version ultra-simplifiée pour Phi3:mini avec debug
    """
    if llm is None:
        llm = get_llm()

    retriever = vectordb.as_retriever(search_type="similarity", search_kwargs={"k": k})
    print(f"🔍 Retriever configuré pour récupérer {k} documents")

    # Template ULTRA-SIMPLE pour Phi3:mini
    template = """Réponds en utilisant UNIQUEMENT ces informations:

{context}

Question: {question}

Réponse (uniquement basée sur les informations ci-dessus):"""

    qa_prompt = PromptTemplate.from_template(template)
    print("📝 Template de prompt ultra-simplifié configuré")

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        chain_type_kwargs={
            "prompt": qa_prompt,
            "document_variable_name": "context"
        },
        return_source_documents=True
    )
    return qa_chain



