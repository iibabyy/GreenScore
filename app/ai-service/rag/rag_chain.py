from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from core.ollama_client import get_llm

def build_rag_chain(vectordb, llm=None, k: int = 8):
    """
    Version ultra-simplifiée pour Phi3:mini avec debug
    """
    if llm is None:
        llm = get_llm()

        retriever = vectordb.as_retriever(search_type="similarity", search_kwargs={"k": k})
        print(f"🔍 Retriever configuré pour récupérer {k} documents")

        # Template amélioré: autorise l'inférence raisonnée si la réponse n'est pas explicitement
        # présente dans les documents, demande d'indiquer les hypothèses et un score de confiance.
        # Toujours citer les sources utilisées.
        template = """
Tu es Mr Green, un assistant expert en impacts environnementaux. Tu disposes uniquement de la
connaissance fournie ci-dessous (extraits de documents).

{context}

Instructions :
- Donne une réponse concise à la question.
- Si l'information demandée est explicitement présente dans les documents, réponds en t'y
    appuyant et cite les documents (nom du fichier et extrait court si pertinent).
- Si l'information n'est PAS explicitement présente, fournis une estimation raisonnée ("best-effort")
    basée sur les documents et connaissances connexes. Indique clairement les hypothèses que tu fais
    (liste numérotée) et fournis une estimation de confiance sur 5 (ex: Confiance: 3/5).
- Ne fabrique pas de sources : indique "Aucune source directe trouvée" si applicable.
- Termine par une courte liste des sources citées.

Question: {question}

Réponse:
"""

    qa_prompt = PromptTemplate.from_template(template)
    print("📝 Template amélioré configuré")

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



