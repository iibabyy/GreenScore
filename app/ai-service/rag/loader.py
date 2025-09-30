import os
import csv
import json
from typing import List, Callable
from core.config import settings

# Prefer community loaders to reduce langchain deprecation noise
try:
    from langchain_community.document_loaders import PyPDFLoader
except Exception:
    from langchain.document_loaders import PyPDFLoader

try:
    # Document class for wrapping text + metadata
    from langchain.schema import Document
except Exception:
    # Backwards-compatible fallback
    from langchain.docstore.document import Document


def _flatten_json(obj, parent_key: str = "") -> List[str]:
    """Flatten a nested JSON/dict into a list of 'key: value' strings."""
    parts = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            parts.extend(_flatten_json(v, new_key))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            new_key = f"{parent_key}[{i}]"
            parts.extend(_flatten_json(item, new_key))
    else:
        parts.append(f"{parent_key}: {obj}")
    return parts


def load_pdf(path: str) -> List[Document]:
    loader = PyPDFLoader(path)
    return loader.load()


def load_csv(path: str) -> List[Document]:
    docs: List[Document] = []
    try:
        with open(path, newline='', encoding='utf-8') as fh:
            reader = csv.DictReader(fh)
            for i, row in enumerate(reader):
                # Convert row dict into a readable text block
                parts = [f"{k}: {v}" for k, v in row.items() if v is not None and v != ""]
                text = ". ".join(parts)
                metadata = {"source": os.path.basename(path), "row": i}
                docs.append(Document(page_content=text, metadata=metadata))
    except Exception as e:
        print(f"Error loading CSV {path}: {e}")
    return docs


def load_json(path: str) -> List[Document]:
    docs: List[Document] = []
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
            if isinstance(data, list):
                iterable = enumerate(data)
            elif isinstance(data, dict):
                # If dict contains a top-level list under common keys, try to pick it
                # otherwise treat the whole dict as a single object
                found = False
                for key in ("items", "documents", "records", "data"):
                    if key in data and isinstance(data[key], list):
                        iterable = enumerate(data[key])
                        found = True
                        break
                if not found:
                    iterable = [(0, data)]
            else:
                iterable = []

            for i, item in iterable:
                parts = _flatten_json(item)
                text = ". ".join(parts)
                metadata = {"source": os.path.basename(path), "index": i}
                docs.append(Document(page_content=text, metadata=metadata))
    except Exception as e:
        print(f"Error loading JSON {path}: {e}")
    return docs


# Registry of extension -> loader function
_LOADERS: dict[str, Callable[[str], List[Document]]] = {
    ".pdf": load_pdf,
    ".csv": load_csv,
    ".json": load_json,
}


def load_all_documents(data_dir: str = None) -> List[Document]:
    """Load all supported documents from disk and return a list of Documents.

    Supports PDF, CSV and JSON. Easily extensible by adding entries to `_LOADERS`.
    """
    data_dir = data_dir or settings.PDF_DIR
    all_docs: List[Document] = []
    if not os.path.isdir(data_dir):
        print(f"Data directory not found: {data_dir}")
        return all_docs

    for fname in sorted(os.listdir(data_dir)):
        path = os.path.join(data_dir, fname)
        if not os.path.isfile(path):
            continue
        _, ext = os.path.splitext(fname)
        ext = ext.lower()
        loader = _LOADERS.get(ext)
        if loader:
            try:
                docs = loader(path)
                if docs:
                    print(f"Loaded {len(docs)} docs from {fname}")
                all_docs.extend(docs)
            except Exception as e:
                print(f"Failed to load {fname}: {e}")
        else:
            print(f"No loader for extension {ext}, skipping {fname}")

    print(f"Total documents loaded: {len(all_docs)}")
    return all_docs


def load_documents() -> List[Document]:
    """Backward-compatible alias for existing codepaths (keeps default behavior)."""
    return load_all_documents()
