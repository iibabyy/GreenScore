import os
from pathlib import Path
import json
import csv

import pytest

import sys
sys.path.append(os.getcwd())

from rag.loader import load_all_documents
import rag.vectorstore as vectorstore_module
from core.config import settings

try:
    from langchain.schema import Document
except Exception:
    # fallback simple Document-like object
    class Document:
        def __init__(self, page_content, metadata=None):
            self.page_content = page_content
            self.metadata = metadata or {}


def test_loader_basic(tmp_path):
    # create sample files
    d = tmp_path
    # csv
    csv_file = d / "sample.csv"
    with open(csv_file, 'w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=["col1", "col2"])
        w.writeheader()
        w.writerow({"col1": "a", "col2": "1"})
        w.writerow({"col1": "b", "col2": "2"})

    # json
    json_file = d / "sample.json"
    with open(json_file, 'w', encoding='utf-8') as fh:
        json.dump([{"k": "v1"}, {"k": "v2"}], fh)

    # txt
    txt_file = d / "sample.txt"
    txt_file.write_text("Hello world", encoding='utf-8')

    # Ensure the loader looks only in our temp folder by overriding settings paths
    orig_pdf = settings.PDF_DIR
    orig_csv = settings.CSV_DIR
    orig_json = settings.JSON_DIR
    orig_web = settings.WEB_DIR
    try:
        settings.PDF_DIR = str(d)
        settings.CSV_DIR = str(d)
        settings.JSON_DIR = str(d)
        settings.WEB_DIR = str(d)
        docs = load_all_documents(str(d))
    finally:
        settings.PDF_DIR = orig_pdf
        settings.CSV_DIR = orig_csv
        settings.JSON_DIR = orig_json
        settings.WEB_DIR = orig_web
    # expect 2 rows from csv -> 2 docs, json -> 2 docs, txt -> 1 doc => total 5
    assert len(docs) == 5


def test_vectorstore_with_dummy_embeddings(tmp_path, monkeypatch):
    # Prepare small documents
    docs = [Document(page_content=f"doc {i}", metadata={"source": f"s{i}"}) for i in range(3)]

    # Dummy embeddings that return small fixed vectors
    class DummyEmbeddings:
        def __init__(self, model_name=None, model_kwargs=None):
            self.dim = 8

        def embed_documents(self, texts):
            return [[float(len(t) % 10) for _ in range(self.dim)] for t in texts]

        def embed_query(self, text):
            return [float(len(text) % 10) for _ in range(self.dim)]
        
        # Make the object callable as some FAISS wrappers expect a callable embedding function
        def __call__(self, text):
            return [float(len(text) % 10) for _ in range(self.dim)]

    # Patch the HuggingFaceEmbeddings in the module
    monkeypatch.setattr(vectorstore_module, 'HuggingFaceEmbeddings', DummyEmbeddings)

    persist = tmp_path / "faiss_index"
    vs = vectorstore_module.create_vectorstore(docs, persist_path=str(persist), batch_size=2)
    assert vs is not None
    # If persisted, expect the index folder exists
    idx_dir = Path(str(persist)) / 'faiss_index'
    # The implementation may save into persist_path/faiss_index
    assert idx_dir.exists() or (Path(str(persist))).exists()
