import os
from langchain.document_loaders import PyPDFLoader
from core.config import settings

def load_documents():
    docs = []
    for file_name in os.listdir(settings.PDF_DIR):
        if file_name.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(settings.PDF_DIR, file_name))
            docs.extend(loader.load())
    return docs
