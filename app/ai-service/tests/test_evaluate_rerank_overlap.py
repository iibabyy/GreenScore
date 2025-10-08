import os
import sys
import json

sys.path.append(os.getcwd())

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_evaluate_with_rerank_and_filter():
    payload = {
        "product_description": "Barre énergétique à base de soja et avoine biologique",
        "rerank": True,
        "source_filter": "pdf,csv",
        "top_n": 3,
        "debug": False
    }
    resp = client.post("/evaluate", json=payload)
    assert resp.status_code == 200
    # Collect full streamed body
    body = b"".join(resp.iter_bytes())
    data = json.loads(body.decode("utf-8"))
    dbg = data.get("debug_info", {})
    assert "overlap_ratio" in dbg
    assert 0.0 <= dbg["overlap_ratio"] <= 1.0
    assert "rerank_applied" in dbg
    assert "applied_source_filter" in dbg
    assert "original_candidate_count" in dbg


def test_evaluate_top_n_bounds():
    bad = {"product_description": "x", "top_n": 0}
    r = client.post("/evaluate", json=bad)
    assert r.status_code == 400
    bad2 = {"product_description": "x", "top_n": 99}
    r2 = client.post("/evaluate", json=bad2)
    assert r2.status_code == 400
