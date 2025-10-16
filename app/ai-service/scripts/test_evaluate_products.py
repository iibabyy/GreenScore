"""Batch test for /evaluate endpoint across synthetic products.

This script:
- Iterates a list of product descriptions matching synthetic profiles
- Calls the /evaluate FastAPI endpoint (assumes service running on localhost:8000)
- Streams the JSON response (assembled) and extracts key debug metrics
- Computes simple heuristics: contains_product_name, overlap_ratio, grounding flags
- Prints a compact table + detailed anomalies summary at the end

Usage (from ai-service directory):
  python3 scripts/test_evaluate_products.py

Requirements:
  FastAPI service must be running locally (uvicorn app:app --reload)
"""
from __future__ import annotations
import json
import http.client  # kept for potential future fallback
import time
from dataclasses import dataclass
from typing import List, Dict, Any
import re
import sys
import os
from urllib.parse import urlparse

# --- Config flexible via variables d'environnement ---
# Priorité: EVAL_API_URL (ex: http://localhost:5000/api) sinon host+port+prefix
DEFAULT_PORT = 5000  # correspond au port interne du conteneur greenscore_ai
api_url_env = os.getenv("EVAL_API_URL")
if api_url_env:
    parsed = urlparse(api_url_env if '://' in api_url_env else f"http://{api_url_env}")
    HOST = parsed.hostname or 'localhost'
    PORT = parsed.port or DEFAULT_PORT
    # base path sans trailing slash
    base_path = parsed.path.rstrip('/') or ''
else:
    HOST = os.getenv("EVAL_API_HOST", "localhost")
    try:
        PORT = int(os.getenv("EVAL_API_PORT", str(DEFAULT_PORT)))
    except ValueError:
        PORT = DEFAULT_PORT
    base_path = os.getenv("EVAL_API_PREFIX", "/api").rstrip('/')

ENDPOINT = f"{base_path}/evaluate"
TIMEOUT = int(os.getenv("EVAL_TIMEOUT", "90"))
PER_PRODUCT_TIMEOUT = int(os.getenv("EVAL_PER_PRODUCT_TIMEOUT", "75"))
VERBOSE = os.getenv("EVAL_VERBOSE", "0") == "1"

PRODUCTS = [
    "Sardines à l'huile d'olive en conserve",
    "Pizza végétarienne surgelée",
    "Barre protéinée cacao",
    "Poudre protéine vegan chanvre et pois",
    "Complément oméga 3 gélules"
]

NORMALIZE_RE = re.compile(r"[^a-z0-9]+")

def norm(s: str) -> str:
    import unicodedata
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("utf-8")
    s = s.lower()
    return NORMALIZE_RE.sub("", s)

@dataclass
class EvalResult:
    product: str
    ok: bool
    status: int
    evaluation: str
    overlap_ratio: float
    regenerated: bool
    grounding_regen: bool
    product_synthetic_included: bool
    injected_product_id: str | None
    contains_name: bool
    missing_name: bool
    length: int
    suspect_patterns: List[str]
    debug: Dict[str, Any]


def call_evaluate(product: str) -> EvalResult:
    """Call evaluate endpoint with robust streaming handling (requests)."""
    import requests
    url = f"http://{HOST}:{PORT}{ENDPOINT}"
    payload = {
        "product_description": product,
        "debug": False,
        "rerank": True,
        "top_n": 3
    }
    start = time.time()
    try:
        with requests.post(url, json=payload, stream=True, timeout=TIMEOUT) as r:
            status = r.status_code
            parts: list[str] = []
            for chunk in r.iter_content(chunk_size=512):
                if chunk:
                    parts.append(chunk.decode('utf-8', errors='replace'))
                if (time.time() - start) > PER_PRODUCT_TIMEOUT:
                    if VERBOSE:
                        print(f"[TIMEOUT] stop reading product='{product[:30]}' at {int(time.time()-start)}s")
                    break
            raw = ''.join(parts).strip()
            # Parse JSON gracefully
            try:
                data = json.loads(raw)
            except Exception:
                last = raw.rfind('}')
                if last != -1:
                    try:
                        data = json.loads(raw[:last+1])
                    except Exception:
                        data = {"_raw": raw, "error": "json_parse_failed"}
                else:
                    data = {"_raw": raw, "error": "json_parse_failed"}
            debug = data.get("debug_info", {}) or {}
            evaluation = data.get("evaluation", "") or ""
            injected_pid = debug.get("injected_product_id")
            syn_included = bool(debug.get("product_synthetic_included"))
            try:
                ov = float(debug.get("overlap_ratio", 0.0))
            except Exception:
                ov = 0.0
            regenerated = bool(debug.get("regenerated"))
            grounding_regen = bool(debug.get("grounding_regen"))
            suspect = debug.get("suspect_patterns", []) or []
            anchor_first = norm(product.split()[0]) if product.split() else ""
            contains_name = anchor_first in {norm(t) for t in evaluation.split()}
            missing_name = not contains_name and syn_included
            ok = (status == 200 and not data.get("error"))
            return EvalResult(
                product=product,
                ok=ok,
                status=status,
                evaluation=evaluation,
                overlap_ratio=ov,
                regenerated=regenerated,
                grounding_regen=grounding_regen,
                product_synthetic_included=syn_included,
                injected_product_id=injected_pid,
                contains_name=contains_name,
                missing_name=missing_name,
                length=len(evaluation),
                suspect_patterns=suspect,
                debug=debug
            )
    except Exception as e:
        return EvalResult(product, False, 0, f"EXC: {e}", 0.0, False, False, False, None, False, False, 0, [], {})


def main():
    print(f"Testing {ENDPOINT} on {len(PRODUCTS)} products (host={HOST} port={PORT})...\n")
    if VERBOSE:
        print(f"Config: TIMEOUT={TIMEOUT}s PER_PRODUCT_TIMEOUT={PER_PRODUCT_TIMEOUT}s URL=http://{HOST}:{PORT}{ENDPOINT}")
    results: List[EvalResult] = []
    start = time.time()
    for p in PRODUCTS:
        t0 = time.time()
        r = call_evaluate(p)
        dt = time.time() - t0
        results.append(r)
        print(f"→ {p[:34]:34} | status={r.status} ok={r.ok} overlap={r.overlap_ratio:.3f} regen={r.regenerated} ground_regen={r.grounding_regen} syn_inj={r.product_synthetic_included} pid={r.injected_product_id} name_ok={not r.missing_name} ({dt:.1f}s)")
    total = time.time() - start

    # Summary table
    print("\nSUMMARY")
    headers = ["Product", "OK", "Overlap", "SynInj", "PID", "NameOK", "Len", "Suspects"]
    print(" | ".join(headers))
    print("-" * 100)
    for r in results:
        print(f"{r.product[:22]:22} | {int(r.ok)} | {r.overlap_ratio:.3f} | {int(r.product_synthetic_included)} | {r.injected_product_id or '-':8} | {int(not r.missing_name)} | {r.length:4d} | {','.join(r.suspect_patterns) or '-'}")

    # Anomalies
    anomalies = [r for r in results if r.missing_name or not r.ok]
    if anomalies:
        print("\nANOMALIES DETECTED:")
        for a in anomalies:
            print(f" - {a.product}: missing_name={a.missing_name} ok={a.ok} status={a.status} syn_inj={a.product_synthetic_included} pid={a.injected_product_id}")
    else:
        print("\nNo grounding anomalies detected.")

    print(f"\nDone in {total:.1f}s")

if __name__ == "__main__":
    main()
