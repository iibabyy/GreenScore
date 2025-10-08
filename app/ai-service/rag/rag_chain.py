from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from core.ollama_client import get_llm
from typing import Any, Dict
import os

PROMPTS_DIR = os.path.join(os.path.dirname(__file__), 'prompts')

def _load_prompt(name: str = 'analysis_v1.txt') -> str:
    path = os.path.join(PROMPTS_DIR, name)
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            return fh.read()
    except Exception as e:
        # Fallback minimal prompt
        return f"Réponds à la question en utilisant uniquement le contexte.\nContexte: {{context}}\nQuestion: {{question}}\n(Erreur chargement prompt: {e})"


def build_rag_chain(vectordb, llm=None, k: int = 8, debug: bool = False):
    """
    Version ultra-simplifiée pour Phi3:mini avec un mode debug optionnel.

    - vectordb: vectordb object (must implement similarity_search_with_score)
    - llm: optional LLM instance
    - k: number of documents to retrieve
    - debug: if True, attach `run_with_debug(query)` on the returned chain which
      returns the QA result plus top-k retrieved chunks (score, source, snippet).
    """
    if llm is None:
        if debug:
            # Provide a harmless dummy LLM when in debug mode so we don't make network calls
            class _DummyLLM:
                def __call__(self, *args, **kwargs):
                    return {"result": "DEBUG_LLM"}

                def run(self, *args, **kwargs):
                    return "DEBUG_LLM"

                def invoke(self, *args, **kwargs):
                    return {"result": "DEBUG_LLM"}

            llm = _DummyLLM()
        else:
            llm = get_llm()

    # Always create the retriever irrespective of llm presence
    retriever = vectordb.as_retriever(search_type="similarity", search_kwargs={"k": k})
    print(f"🔍 Retriever configuré pour récupérer {k} documents")

    # Chargement du template externe (externalisé Sprint 1)
    template = _load_prompt('analysis_v1.txt')

    qa_prompt = PromptTemplate.from_template(template)
    print("📝 Template amélioré configuré")

    qa_chain = None
    if not debug:
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            chain_type="stuff",
            chain_type_kwargs={
                "prompt": qa_prompt,
                "document_variable_name": "context"
            },
            return_source_documents=True,
        )

    class QAWithDebug:
        def __init__(self, inner_chain, vectordb, retriever, k, debug):
            self._inner = inner_chain
            self._vectordb = vectordb
            self._retriever = retriever
            self._k = k
            self._debug = debug

        def run_with_debug(self, query: str) -> Dict[str, Any]:
            debug_list = []
            try:
                docs_and_scores = self._vectordb.similarity_search_with_score(query, k=self._k)
            except Exception:
                try:
                    docs = self._retriever.get_relevant_documents(query)
                    docs_and_scores = [(d, None) for d in docs]
                except Exception:
                    docs_and_scores = []

            for doc, score in docs_and_scores:
                snippet = (doc.page_content or '')
                snippet = ' '.join(snippet.split())[:800]
                debug_list.append({
                    'score': float(score) if score is not None else None,
                    'source': doc.metadata.get('source') if hasattr(doc, 'metadata') else None,
                    'snippet': snippet,
                })

            if self._debug:
                print(f"🧪 Debug retrieved ({len(debug_list)} items):")
                for i, d in enumerate(debug_list[:self._k]):
                    print(f"  {i+1}. score={d['score']} source={d['source']} snippet={d['snippet'][:120]}...")

                return {
                    'answer': None,
                    'result': None,
                    'debug_retrieved': debug_list,
                    'truncated': False,
                    'truncation_hints': [],
                }

            # Run the QA chain (keep same interface used elsewhere).
            # Support multiple LangChain versions/objects: prefer `invoke`, then callable (chain.__call__), then `run`.
            result = None
            answer = None
            try:
                if hasattr(self._inner, "invoke"):
                    result = self._inner.invoke({"query": query})
                elif callable(self._inner):
                    result = self._inner({"query": query})
                elif hasattr(self._inner, "run"):
                    answer = self._inner.run(query)
                    result = {"result": answer}
                else:
                    try:
                        answer = getattr(self._inner, "run")(query)
                        result = {"result": answer}
                    except Exception as ex_inner:
                        raise ex_inner

                # Normalize answer extraction
                if isinstance(result, dict):
                    answer = result.get('result') or result.get('answer') or next((v for v in result.values() if isinstance(v, str)), None)
                else:
                    answer = result
            except Exception as e2:
                answer = str(e2)
                result = {'error': answer}

            # Heuristic truncation detection
            truncated = False
            truncation_hints = []
            if isinstance(answer, str):
                a = answer.strip()
                if a.endswith("...") or a.endswith(".."):
                    truncated = True
                    truncation_hints.append("ends_with_ellipsis")
                if len(a) > 0 and a[-1] not in (".", "!", "?", "»", '"', "'"):
                    truncated = True
                    truncation_hints.append("no_final_punctuation")

            return {
                'answer': answer,
                'result': result,
                'debug_retrieved': debug_list,
                'truncated': truncated,
                'truncation_hints': truncation_hints,
            }

        def __getattr__(self, name):
            # Delegate attribute access to the underlying chain
            return getattr(self._inner, name)

    return QAWithDebug(qa_chain, vectordb, retriever, k, debug)



