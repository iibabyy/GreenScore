import os
import sys
from fastapi.testclient import TestClient

sys.path.append(os.getcwd())
from app import app  # noqa

client = TestClient(app)

def test_ask_rejects_long_question():
    long_q = 'a' * 600
    r = client.post('/api/ask', params={'question': long_q})
    assert r.status_code == 400
    assert 'trop longue' in r.text

def test_ask_accepts_short_question(monkeypatch):
    # Monkeypatch get_llm to avoid real model call
    import core.ollama_client as oc
    class Dummy:
        model = 'dummy'
        def __call__(self, *args, **kwargs):
            return {'result': 'ok'}
        def invoke(self, *args, **kwargs):
            return {'result': 'Réponse test', 'source_documents': []}
    monkeypatch.setattr(oc, 'get_llm', lambda: Dummy())
    r = client.post('/api/ask', params={'question': 'Impact carbone du packaging ?'})
    assert r.status_code == 200
    data = r.json()
    assert 'answer' in data


def test_evaluate_rejects_long_description():
    long_desc = 'b' * 1500
    r = client.post('/api/evaluate', json={'product_description': long_desc, 'debug': True})
    assert r.status_code == 400

