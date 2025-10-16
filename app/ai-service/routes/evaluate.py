# ===== 5. evaluate.py (modifié avec query narrative fluide) =====
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from core.ollama_client import get_llm
import asyncio
import json
# NOTE: Pour l'évaluation anti-hallucination nous effectuons une récupération manuelle
# puis (optionnel) un rerank + filtrage pour contrôler précisément le contexte fourni au LLM
from rag.rerank import rerank_documents, filter_documents_by_type
from rag.vectorstore_manager import VectorStoreManager
import time
import traceback
from core.ollama_client import ensure_ollama_warm
from core.config import settings
import os
import re

# --- Anti-hallucination configuration ---
EVAL_MAX_SENTENCES = int(os.getenv("EVAL_MAX_SENTENCES", "6"))
MIN_OVERLAP_REGEN_THRESHOLD = 0.15  # si overlap < 0.15 et patterns suspects -> regen
SUSPECT_PATTERNS = [
    r"create 5 sentences",
    r"write an extensive review",
    r"the document below",
    r"cognitive behavioral therapy",
    r"baby boomers",
    r"leucine-?10",
    r"augmented by a detailed analysis",
    r"instruction:",
    r"canonical",
    r"rewrite",
    r"the answer to",
    r"answer ai:",
    r"what are the answer",
    r"code snippet",
    r"```python",
    r"notebooks?",
    r"question rewrite"
]

SUSPECT_REGEX = re.compile("|".join(SUSPECT_PATTERNS), flags=re.IGNORECASE)

def _split_sentences(text: str):
    # rudimentary sentence splitter
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]

def _truncate_sentences(text: str, max_sentences: int):
    sentences = _split_sentences(text)
    truncated = sentences[:max_sentences]
    return " ".join(truncated), len(sentences) - len(truncated), len(truncated)

def _detect_suspect_patterns(text: str):
    matches = SUSPECT_REGEX.findall(text)
    # return unique lower-cased patterns matched
    return sorted(set(m.strip().lower() for m in matches if m))

def _sanitize_answer(text: str, max_sentences: int):
    # Remove any trailing prompts/instructions starting with quotes or The document below ...
    lines = [l for l in text.splitlines() if l.strip()]
    cleaned_lines = []
    for l in lines:
        if SUSPECT_REGEX.search(l):
            continue
        cleaned_lines.append(l)
    cleaned = " ".join(cleaned_lines)
    truncated_text, removed_count, final_count = _truncate_sentences(cleaned, max_sentences)
    suspects = _detect_suspect_patterns(text)
    return truncated_text.strip(), {
        "removed_sentences": removed_count,
        "final_sentence_count": final_count,
        "suspect_patterns": suspects,
    }

MAX_EVAL_RETRIES = 3
RETRY_BACKOFF_BASE = 0.75
MAX_TOTAL_SECONDS = 45  # coupe après cette durée globale

router = APIRouter()
vector_store_manager = VectorStoreManager()
vectordb = vector_store_manager.get_vectordb()

async def generate_streaming_response(product_description: str, debug: bool = False,
                                      rerank: bool = False, source_filter: str = "", top_n: int = 3):
    print(f"\n🌱 Évaluation demandée pour: {product_description[:100]}...")
    print("⚡ Démarrage du processus d'évaluation...")
    
    print("🔄 Initialisation LLM (factory)...")
    start_init = time.time()
    llm = get_llm()
    init_time = time.time() - start_init
    print(f"✅ LLM prêt (factory) en {init_time:.1f}s")
    
    # --- 1. Récupération initiale des documents ---
    base_k = max(top_n * 2, settings.NUM_RETRIEVAL_DOCS + 2)
    print(f"� Récupération initiale top-k (k={base_k})")
    try:
        docs_and_scores = vectordb.similarity_search_with_score(product_description, k=base_k)
    except Exception:
        print("⚠️ similarity_search_with_score a échoué, fallback get_relevant_documents")
        retriever = vectordb.as_retriever(search_kwargs={"k": base_k})
        fallback_docs = retriever.get_relevant_documents(product_description)
        docs_and_scores = [(d, None) for d in fallback_docs]

    candidate_docs = [d for d, _ in docs_and_scores]

    # --- Injection / boosting ciblée de documents synthétiques correspondant au produit ---
    import unicodedata as _uc
    def _norm_token(t: str) -> str:
        t = _uc.normalize("NFKD", t).encode("ascii", "ignore").decode("utf-8").lower()
        return re.sub(r"[^a-z0-9]+", "", t)

    # Extra tokens normalisés issus de la description (réutilisés plus bas)
    import re as _re
    raw_tokens = _re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ\-']+", product_description.lower())
    norm_tokens = {_norm_token(t) for t in raw_tokens if t}

    synthetic_docs = [d for d in candidate_docs if d.metadata.get("synthetic")]
    synthetic_by_pid = {}
    for d in synthetic_docs:
        pid_raw = d.metadata.get("product_id")
        if not pid_raw:
            continue
        pid = _norm_token(pid_raw)
        if not pid:
            continue
        synthetic_by_pid.setdefault(pid, []).append(d)

    matched_pid = None
    for pid in synthetic_by_pid.keys():
        if pid in norm_tokens:
            matched_pid = pid
            break
        # fuzzy: pid contained in any token (e.g. "sardine" vs "sardines")
        if any(pid in nt or nt in pid for nt in norm_tokens):
            matched_pid = pid
            break

    injected_docs = []
    forced_injection = False
    if matched_pid:
        # Inject first 2 chunks for this synthetic product at the head
        injected_docs = synthetic_by_pid.get(matched_pid, [])[:2]
        if injected_docs:
            already_ids = {id(d) for d in injected_docs}
            rest = [d for d in candidate_docs if id(d) not in already_ids]
            candidate_docs = injected_docs + rest
            forced_injection = True
            print(f"🧬 Injection forcée: {len(injected_docs)} doc(s) synthétique(s) pour produit '{matched_pid}'")
    else:
        print("ℹ️ Aucun profil synthétique correspondant détecté pour injection")
        # --- Fallback injection (recherche ciblée) ---
        if os.getenv("EVAL_FALLBACK_INJECT", "1") == "1":
            # Essayer quelques tokens longs spécifiques
            anchor_tokens = sorted([t for t in norm_tokens if len(t) > 5], key=len, reverse=True)[:2]
            fallback_docs = []
            tried_terms = []
            for at in anchor_tokens:
                try:
                    tried_terms.append(at)
                    res = vectordb.similarity_search_with_score(at, k=4)
                    for d, _sc in res:
                        if d.metadata.get("synthetic"):
                            pid_raw = d.metadata.get("product_id")
                            if not pid_raw:
                                continue
                            pid_norm = _norm_token(pid_raw)
                            if pid_norm in norm_tokens or any(pid_norm in nt or nt in pid_norm for nt in norm_tokens):
                                fallback_docs.append(d)
                except Exception as fe:
                    print(f"⚠️ Fallback search error term={at}: {fe}")
                if fallback_docs:
                    break
            if fallback_docs:
                # dedupe & prepend
                unique = []
                seen_ids = set()
                for d in fallback_docs:
                    i = id(d)
                    if i not in seen_ids:
                        unique.append(d)
                        seen_ids.add(i)
                injected_docs = unique[:2]
                already_ids = {id(d) for d in injected_docs}
                rest = [d for d in candidate_docs if id(d) not in already_ids]
                candidate_docs = injected_docs + rest
                forced_injection = True
                matched_pid = _norm_token(injected_docs[0].metadata.get("product_id", "")) or matched_pid
                print(f"🔁 Fallback injection: {len(injected_docs)} doc(s) synthétique(s) ajoutés via tokens {anchor_tokens}")
            else:
                print("❔ Fallback injection n'a trouvé aucun document synthétique")
    # --- Filtrage lexicale basique basé sur mots produits (améliore spécificité) ---
    # Extraire mots significatifs (>=5 lettres) du product_description
    product_keywords = sorted({t for t in raw_tokens if len(t) >= 5})[:12]
    filtered_for_product = []
    if product_keywords:
        for d in candidate_docs:
            txt_low = (d.page_content[:5000]).lower()
            if any(k in txt_low for k in product_keywords):
                filtered_for_product.append(d)
        # Only apply if we keep at least 1 doc
        if filtered_for_product:
            candidate_docs = filtered_for_product
            print(f"🔎 Filtrage produit: {len(candidate_docs)} docs correspondent aux mots-clés {product_keywords}")
        else:
            print(f"ℹ️ Aucun doc ne matche les mots-clés {product_keywords}, conservation liste initiale")
    original_candidate_count = len(candidate_docs)
    print(f"📚 {original_candidate_count} candidats avant filtrage/rerank")

    # --- 2. Filtrage par type de source ---
    applied_source_filter = None
    if source_filter.strip():
        types = [t.strip() for t in source_filter.split(',') if t.strip()]
        if types:
            filtered_docs = filter_documents_by_type(candidate_docs, types)
            if filtered_docs is not candidate_docs:
                applied_source_filter = ','.join(types)
            candidate_docs = filtered_docs
            print(f"🔧 Filtrage sources appliqué: {applied_source_filter or 'aucun changement'} -> {len(candidate_docs)} docs")

    # --- 3. Rerank optionnel ---
    rerank_scores = []
    rerank_applied = False
    if rerank and len(candidate_docs) > 1:
        top_docs, scored = rerank_documents(product_description, candidate_docs, top_n=top_n)
        # Boost synthetic matched product docs by slight score increase (post-rerank ordering adjust)
        if matched_pid:
            boosted = []
            for doc, sc in scored:
                if doc.metadata.get("synthetic") and _norm_token(str(doc.metadata.get("product_id"))) == matched_pid:
                    sc *= 1.25  # 25% boost
                boosted.append((doc, sc))
            # re-sort after boost
            boosted.sort(key=lambda x: x[1], reverse=True)
            top_docs = [d for d, _ in boosted[:top_n]]
            scored = boosted
        rerank_applied = True
        rerank_scores = scored[:len(top_docs)]
        selected_docs = top_docs
        print(f"🏅 Rerank appliqué -> {len(selected_docs)} docs")
    else:
        selected_docs = candidate_docs[:top_n]
        print(f"➡️ Pas de rerank -> tronqué à {len(selected_docs)} docs")

    # --- 4. Construction contexte contrôlé ---
    context_fragments = []
    for idx, d in enumerate(selected_docs, 1):
        src = d.metadata.get('source', 'unknown')
        raw_snippet = ' '.join(d.page_content.split())
        snippet = raw_snippet[:900]  # initial cap
        context_fragments.append(f"[DOC {idx} | {src}] {snippet}")
    context_text = "\n\n".join(context_fragments)

    # --- Prompt budgeting (approx token estimate) ---
    approx_tokens = len(context_text.split()) + len(product_description.split()) + 90
    prompt_truncated = False
    MAX_PROMPT_TOKENS = int(os.getenv("EVAL_MAX_PROMPT_TOKENS", "1800"))
    if approx_tokens > MAX_PROMPT_TOKENS:
        # reduce each doc snippet progressively
        reduced_fragments = []
        factor = MAX_PROMPT_TOKENS / float(approx_tokens)
        # minimal floor
        for frag in context_fragments:
            head, body = frag.split('] ', 1)
            target_chars = max(250, int(len(body) * factor * 0.9))
            reduced_fragments.append(f"{head}] {body[:target_chars]}")
        context_text = "\n\n".join(reduced_fragments)
        prompt_truncated = True

    # Query optimisée pour un texte fluide, narratif, avec intégration naturelle des scores
    query = f"""Contexte factuel:
{context_text}

Tâche: Rédige un court paragraphe (≤ {EVAL_MAX_SENTENCES} phrases) expliquant l'impact environnemental du produit: {product_description}.
Contraintes:
- Utilise uniquement le contexte (pas d'invention)
- Intègre production, transport, emballage si présents
- Si une donnée manque: 'Non disponible'
- Ton: pédagogique, concis, naturel
Sortie: texte uniquement, sans listes, sans code, sans 'Instruction', sans 'Rewrite'.
"""
    print(f"🔍 Query construite: {query[:150]}...")

    if debug:
        print("🔧 Mode debug : affichage des documents sélectionnés")
        debug_docs = [
            {
                "source": d.metadata.get('source', 'unknown'),
                "preview": d.page_content[:400]
            } for d in selected_docs
        ]
        response = {
            "product": product_description,
            "debug": {
                "selected_docs": debug_docs,
                "original_candidate_count": original_candidate_count,
                "applied_source_filter": applied_source_filter,
                "rerank_applied": rerank_applied,
                "rerank_scores": rerank_scores[:10]
            },
        }
        yield json.dumps(response)

    # Warmup Ollama (best-effort)
    warm_ok = ensure_ollama_warm()
    if not warm_ok:
        print("⚠️ Warmup Ollama non confirmé (continuation quand même)")

    start_time = time.time()
    last_error = None
    result = None
    total_time = 0
    source_docs = selected_docs  # ceux réellement fournis

    def _generate_answer(prompt: str):
        # Tente différentes interfaces (invoke / __call__ / run)
        try:
            if hasattr(llm, 'invoke'):
                r = llm.invoke(prompt)
                if isinstance(r, dict):
                    return r.get('result') or r.get('text') or str(r)
                return r
            if callable(llm):
                r = llm(prompt)
                if isinstance(r, dict):
                    return r.get('result') or r.get('text') or str(r)
                return r
            if hasattr(llm, 'run'):
                return llm.run(prompt)
        except Exception as e:
            return f"<error: {e}>"
        return "<vide>"

    for attempt in range(1, MAX_EVAL_RETRIES + 1):
        try:
            print(f"🔄 Tentative d'évaluation {attempt}/{MAX_EVAL_RETRIES}...")
            gen_start = time.time()
            # Exécuter génération dans un thread pour ne pas bloquer event loop
            result = await asyncio.to_thread(_generate_answer, query)
            gen_time = time.time() - gen_start
            print(f"✅ Génération réussie! (temps: {gen_time:.1f}s)")
            total_time = time.time() - start_time
            break
        except Exception as e:
            last_error = e
            total_time = time.time() - start_time
            if total_time > MAX_TOTAL_SECONDS:
                print("⏱️ Timeout global atteint, arrêt des retries")
                break
            # jitter exponentiel
            base = RETRY_BACKOFF_BASE * (2 ** (attempt - 1))
            jitter = 0.2 * base
            delay = min(base + (jitter * (0.5)), 8.0)
            print(f"❌ Échec tentative {attempt}/{MAX_EVAL_RETRIES}: {e} (retry in {delay:.2f}s)")
            await asyncio.sleep(delay)
    else:
        tb = traceback.format_exc(limit=3)
        error_response = {
            "error": "Échec de génération après retries",
            "type": last_error.__class__.__name__ if last_error else "Unknown",
            "message": str(last_error),
            "trace": tb.splitlines(),
            "retries": MAX_EVAL_RETRIES,
        }
        yield json.dumps(error_response)

    answer = result or "<vide>"

    # --- 5.a Première passe de sanitation & troncature ---
    sanitized_answer, sanitize_meta = _sanitize_answer(answer, EVAL_MAX_SENTENCES)

    # --- 5.b Heuristique overlap (approximation similarité contenu) ---

    import unicodedata as _uc
    def _norm_token_simple(t: str) -> str:
        t = _uc.normalize("NFKD", t).encode("ascii", "ignore").decode("utf-8").lower()
        return re.sub(r"[^a-z0-9]+", "", t)
    STOP = {"de","la","le","les","un","une","et","en","du","des","au","aux","sur","dans","par","pour","avec","plus","ou"}
    answer_tokens_raw = sanitized_answer.split() if isinstance(sanitized_answer, str) else []
    answer_tokens = [_norm_token_simple(t) for t in answer_tokens_raw]
    answer_tokens = [t for t in answer_tokens if t and len(t) > 2 and t not in STOP]
    source_tokens_set = set()
    for d in source_docs:
        try:
            for tk in d.page_content.split():
                nt = _norm_token_simple(tk)
                if nt and len(nt) > 2 and nt not in STOP:
                    source_tokens_set.add(nt)
        except Exception:
            pass
    overlap_ratio = 0.0
    if answer_tokens:
        common = set(answer_tokens).intersection(source_tokens_set)
        overlap_ratio = round(len(common) / max(1, len(set(answer_tokens))), 4)
    
    # --- 5.c Décision de régénération stricte ---
    regenerated = False
    low_overlap_trigger = overlap_ratio < MIN_OVERLAP_REGEN_THRESHOLD
    if (sanitize_meta["suspect_patterns"] and low_overlap_trigger) or (low_overlap_trigger and injected_docs):
        print("♻️ Régénération stricte déclenchée (patterns suspects & overlap faible)")
        strict_prompt = f"""
Tu es un assistant environnemental factuel.
Ne produis PAS de phrases qui ne sont pas supportées textuellement par le contexte suivant.
Si une information n'est pas présentée, réponds uniquement: "Information non disponible".
Produit au maximum {EVAL_MAX_SENTENCES} phrases concises (<= 22 mots).
Contexte:
{context_text}
Question: Impact environnemental du produit: {product_description}
Réponse:
"""
        try:
            strict_result = await asyncio.to_thread(_generate_answer, strict_prompt)
            strict_sanitized, strict_meta = _sanitize_answer(strict_result, EVAL_MAX_SENTENCES)
            # Recalcule overlap
            answer_tokens = set(strict_sanitized.lower().split()) if strict_sanitized else set()
            source_tokens = set()
            for d in source_docs:
                try:
                    source_tokens.update(d.page_content.lower().split())
                except Exception:
                    pass
            overlap_ratio = round(len(answer_tokens.intersection(source_tokens)) / max(1, len(answer_tokens)), 4) if answer_tokens else 0.0
            sanitized_answer = strict_sanitized
            sanitize_meta = strict_meta
            regenerated = True
        except Exception as regen_e:
            print(f"⚠️ Régénération stricte échouée: {regen_e}")

    # Fallback si tout vidé
    if not sanitized_answer.strip():
        sanitized_answer = "Analyse non disponible sur la base des données fournies."

    # --- 6. Vérification grounding produit (le nom doit apparaître si injection synthétique) ---
    grounding_regen = False
    grounding_missing_tokens = []
    if matched_pid and sanitized_answer:
        norm_answer = {_norm_token(t) for t in sanitized_answer.split()}
        # Construire un set d'ancrage plus souple (découpage du product_description)
        anchor_candidates = {nt for nt in norm_tokens if len(nt) > 4}
        required_hit = anchor_candidates.intersection(norm_answer)
        if not required_hit:
            grounding_missing_tokens.extend(sorted(anchor_candidates))
            print(f"🛠️ Grounding regen: aucune ancre {anchor_candidates} trouvée dans la réponse -> régénération ciblée")
            grounding_regen = True
            regen_prompt = f"""
Contexte:
{context_text}

Produit ciblé: {product_description}

Rédige au maximum {EVAL_MAX_SENTENCES} phrases factuelles, concises, naturelles.
Inclue au moins une fois un terme parmi: {', '.join(sorted(anchor_candidates))} si présent dans le contexte, sinon écris seulement 'Information non disponible'.
"""
            try:
                regen_result = await asyncio.to_thread(_generate_answer, regen_prompt)
                regen_sanitized, regen_meta = _sanitize_answer(regen_result, EVAL_MAX_SENTENCES)
                if regen_sanitized.strip():
                    sanitized_answer = regen_sanitized
                    sanitize_meta.update(regen_meta)
            except Exception as ge:
                print(f"⚠️ Échec grounding regeneration: {ge}")

    response = {
        "product": product_description,
        "evaluation": sanitized_answer,
        "evaluation_time_seconds": round(total_time, 2),
        "source_documents": [
            {
                "source": doc.metadata.get("source", "unknown"),
                "page": doc.metadata.get("page", None),
                "text_snippet": doc.page_content[:400]
            }
            for doc in source_docs
        ],
        "debug_info": {
            "num_source_docs": len(source_docs),
            "evaluation_length": len(sanitized_answer),
            "overlap_ratio": overlap_ratio,
            "rerank_applied": rerank_applied,
            "applied_source_filter": applied_source_filter,
            "original_candidate_count": original_candidate_count,
            "rerank_scores": rerank_scores[:10],
            "removed_sentences": sanitize_meta.get("removed_sentences"),
            "final_sentence_count": sanitize_meta.get("final_sentence_count"),
            "suspect_patterns": sanitize_meta.get("suspect_patterns"),
            "regenerated": regenerated,
            "product_keywords": product_keywords,
            "product_filtered_count": len(candidate_docs),
            "product_synthetic_included": bool(injected_docs),
            "injected_product_id": matched_pid,
            "forced_injection": forced_injection,
            "fallback_injection_enabled": os.getenv("EVAL_FALLBACK_INJECT", "1") == "1",
            "fallback_injection_terms": locals().get('anchor_tokens', []),
            "synthetic_candidate_ids": list(synthetic_by_pid.keys()),
            "grounding_regen": grounding_regen,
            "grounding_missing_tokens": grounding_missing_tokens,
            "prompt_truncated": prompt_truncated,
            "approx_prompt_tokens": approx_tokens,
            "low_overlap_trigger": low_overlap_trigger
        }
    }
    
    print(f"⏱️ Évaluation terminée en {total_time:.2f}s")
    print(f"📊 Réponse d'évaluation finale ({len(sanitized_answer)} chars) sentences={sanitize_meta.get('final_sentence_count')} overlap={overlap_ratio}")

    # Stream the response as chunks
    json_str = json.dumps(response)
    chunk_size = 1024
    for i in range(0, len(json_str), chunk_size):
        yield json_str[i:i+chunk_size]

from pydantic import BaseModel

class ProductRequest(BaseModel):
    product_description: str
    debug: bool = False
    rerank: bool = False
    source_filter: str | None = None
    top_n: int = 3

@router.post("/evaluate")
async def evaluate(request: ProductRequest):
    if len(request.product_description) > 1000:
        raise HTTPException(status_code=400, detail="Description produit trop longue (>1000 caractères)")
    if request.top_n < 1 or request.top_n > 10:
        raise HTTPException(status_code=400, detail="top_n doit être entre 1 et 10")
    return StreamingResponse(
        generate_streaming_response(
            request.product_description,
            request.debug,
            rerank=request.rerank,
            source_filter=request.source_filter or "",
            top_n=request.top_n
        ),
        media_type="application/json"
    )