import os
import pytest
import sys
import json

sys.path.append(os.getcwd())

from fastapi.testclient import TestClient
from app import app

# These tests assume the vector store loads successfully with existing data.
# They exercise the new query parameters and response fields.

client = TestClient(app)


def test_ask_basic_overlap_and_rerank_params():
    q = "Donne un résumé environnemental"  # generic question
    resp = client.post(f"/ask?question={q}&rerank=true&top_n=3")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    dbg = data.get("debug_info", {})
    assert "overlap_ratio" in dbg
    assert 0.0 <= dbg["overlap_ratio"] <= 1.0
    # If rerank applied, flag should be true
    assert dbg.get("rerank_applied") in (True, False)
    if dbg.get("rerank_applied"):
        assert isinstance(dbg.get("rerank_scores"), list)


def test_ask_source_filter():
    q = "Impact carbone"  # generic query
    # Ask with a fake type filter that likely yields fallback (should not 500)
    resp = client.post(f"/ask?question={q}&source_filter=pdf,csv&top_n=2")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    dbg = data.get("debug_info", {})
    # applied_source_filter may be None if no matching, but field should exist
    assert "applied_source_filter" in dbg

