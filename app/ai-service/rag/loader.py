import os
import csv
import json
import glob
from typing import List, Callable, Dict, Any
try:
    from bs4 import BeautifulSoup
except Exception:
    BeautifulSoup = None
from core.config import settings

# Prefer community loaders
try:
    from langchain_community.document_loaders import PyPDFLoader
except Exception:
    from langchain.document_loaders import PyPDFLoader

try:
    from langchain.schema import Document
except Exception:
    from langchain.docstore.document import Document


def _flatten_json(obj: Any, parent_key: str = "") -> List[str]:
    parts: List[str] = []
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
                parts = [f"{k}: {v}" for k, v in row.items() if v is not None and v != ""]
                text = ". ".join(parts)
                metadata = {"source": os.path.basename(path), "row": i, "type": "csv"}
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
                # Look for common arrays
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
                metadata = {"source": os.path.basename(path), "index": i, "type": "json"}
                docs.append(Document(page_content=text, metadata=metadata))
    except Exception as e:
        print(f"Error loading JSON {path}: {e}")
    return docs


def load_html(path: str) -> List[Document]:
    docs: List[Document] = []
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            raw = fh.read()
            if BeautifulSoup is not None:
                soup = BeautifulSoup(raw, 'html.parser')
                # remove scripts/styles
                for tag in soup(['script', 'style', 'noscript']):
                    tag.decompose()
                # extract main text - keep headers and paragraphs
                texts = []
                for el in soup.find_all(['h1','h2','h3','h4','p','li']):
                    txt = el.get_text(separator=' ', strip=True)
                    if txt:
                        texts.append(txt)
                # Supprimer doublons consécutifs et lignes très courtes répétitives
                filtered = []
                last = None
                for t in texts:
                    if t == last:
                        continue
                    if len(t) < 3 and any(ch.isalpha() for ch in t) is False:
                        continue
                    filtered.append(t)
                    last = t
                content = '\n\n'.join(filtered)
                # Collapse whitespaces globaux
                content = '\n'.join([' '.join(line.split()) for line in content.splitlines()])
            else:
                # fallback: naive remove tags
                import re
                content = re.sub(r'<[^>]+>', ' ', raw)
                content = ' '.join(content.split())
            metadata = {"source": os.path.basename(path), "type": "html"}
            docs.append(Document(page_content=content, metadata=metadata))
    except Exception as e:
        print(f"Error loading HTML {path}: {e}")
    return docs


# registry
def _load_text_with_tags(path: str) -> List[Document]:
    try:
        content = open(path, 'r', encoding='utf-8').read()
    except Exception as e:
        print(f"Error loading TXT {path}: {e}")
        return []
    fname = os.path.basename(path)
    meta = {"source": fname, "type": "text"}
    if 'synthetic_profiles' in path:
        # derive product_id from filename before extension
        product_id = os.path.splitext(fname)[0]
        meta.update({"synthetic": True, "product_id": product_id})
    return [Document(page_content=content, metadata=meta)]

_LOADERS: Dict[str, Callable[[str], List[Document]]] = {
    '.pdf': load_pdf,
    '.csv': load_csv,
    '.json': load_json,
    '.html': load_html,
    '.htm': load_html,
    '.txt': _load_text_with_tags
}


def _gather_files(data_dir: str) -> List[str]:
    files: List[str] = []
    # Walk standard subfolders
    subdirs = [
        settings.PDF_DIR,
        settings.CSV_DIR,
        settings.JSON_DIR,
        settings.WEB_DIR,
        data_dir or settings.DATA_DIR
    ]
    seen = set()
    for sd in subdirs:
        if not sd:
            continue
        if not os.path.isdir(sd):
            continue
        for root, _, filenames in os.walk(sd):
            for fname in filenames:
                path = os.path.join(root, fname)
                if path in seen:
                    continue
                seen.add(path)
                files.append(path)
    return sorted(files)


def load_all_documents(data_dir: str = None) -> List[Document]:
    files = _gather_files(data_dir)
    all_docs: List[Document] = []
    counts: Dict[str, int] = {}

    for path in files:
        _, ext = os.path.splitext(path)
        ext = ext.lower()
        loader = _LOADERS.get(ext)
        if loader is None:
            print(f"No loader for {path}, skipping")
            continue
        docs = loader(path)
        all_docs.extend(docs)
        counts[ext] = counts.get(ext, 0) + len(docs)
        print(f"Loaded {len(docs)} docs from {os.path.relpath(path, start=settings.DATA_DIR)}")

    # summary
    print("Load summary:")
    for ext, c in counts.items():
        print(f"  {ext}: {c} documents")
    print(f"  Total: {len(all_docs)} documents")

    return all_docs


def load_documents() -> List[Document]:
    return load_all_documents()
