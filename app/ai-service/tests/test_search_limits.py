import os, sys
from fastapi.testclient import TestClient
sys.path.append(os.getcwd())
from app import app  # noqa

client = TestClient(app)

def test_search_k_too_large():
    r = client.post('/api/search', json={'query':'test', 'k': 50})
    assert r.status_code == 400

def test_search_k_valid(monkeypatch):
    # Monkeypatch vectorstore manager to avoid heavy load
    import rag.vectorstore_manager as vsm_module
    class DummyVS:
        def similarity_search_with_score(self, q, k=3):
            class D: metadata={'source':'dummy','page':None}; page_content='dummy content'
            return [(D(), 0.1)]
    class DummyMgr:
        _initialized = True
        def get_vectordb(self):
            return DummyVS()
    monkeypatch.setattr(vsm_module, 'VectorStoreManager', lambda: DummyMgr())
    r = client.post('/api/search', json={'query':'abc', 'k': 2})
    assert r.status_code == 200
    data = r.json()
    assert data['k'] == 2
    assert len(data['results']) == 1
