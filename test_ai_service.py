#!/usr/bin/env python3
"""
Script de test pour vérifier que le service AI avec RAG fonctionne correctement.
Gère les timeouts longs pour le LLM et la base vectorielle.
"""

import requests
import time

BASE_URL = "http://localhost:5000/api"

def test_ask_endpoint():
    """Test de la route /ask"""
    print("🔍 Test de la route /ask...")
    try:
        response = requests.post(
            f"{BASE_URL}/ask",
            params={"question": "peut tu m'expliquer La démarche « Product Environnement Footprint » (PEF) ?"},
            timeout=900  # timeout plus long pour le LLM
        )
        response.raise_for_status()
        data = response.json()

        print(f"✅ /ask fonctionne !")
        print(f"❓ Question : {data['question']}")
        print(f"🤖 Réponse : {data['answer']}")
        print(f"📚 Sources : {data['source_documents']}\n")
        print(f"🔍 Info debug : {data['debug_info']}\n")
        print(f"⏱️ Temps d'attente : {response.elapsed.total_seconds()} secondes")
        print(f"⏱️ Détails des timings : {data['timings']}")
        print(f"⚠️ Avertissements : {data['warnings']}")
        return True
    except requests.exceptions.Timeout:
        print("❌ /ask a dépassé le timeout (LLM trop lent)")
        return False
    except Exception as e:
        print(f"❌ Erreur lors du test de /ask: {e}")
        return False

def test_evaluate_endpoint():
    """Test de la route /evaluate"""
    print("🔍 Test de la route /evaluate...")
    try:
        response = requests.post(
            f"{BASE_URL}/evaluate",
            params={"product_description": "Barre de céréales bio avec emballage en carton recyclable"},
            timeout=900  # timeout plus long pour RAG
        )
        response.raise_for_status()
        data = response.json()
        print(f"✅ /evaluate fonctionne !")
        print(f"📦 Produit : {data['product']}")
        print(f"📊 Évaluation : {data['evaluation']}")
        print(f"📚 Sources : {data['source_documents']}\n")
        print(f"🔍 Info debug : {data['debug_info']}\n")
        print(f"⏱️ Temps d'attente : {response.elapsed.total_seconds()} secondes")
        return True
    except requests.exceptions.Timeout:
        print("❌ /evaluate a dépassé le timeout (RAG trop lent)")
        return False
    except Exception as e:
        print(f"❌ Erreur lors du test de /evaluate: {e}")
        return False

def test_health_check():
    """Test de la route racine"""
    print("🔍 Test de la route racine...")
    try:
        response = requests.get("http://localhost:5000/api/debug-retrieval", timeout=30)
        response.raise_for_status()
        data = response.json()
        print(f"✅ Health check OK : {data['message']}\n")
        return True
    except Exception as e:
        print(f"❌ Health check a échoué : {e}")
        return False

def run_tests():
    """Exécute tous les tests"""
    print("🚀 Démarrage des tests du service AI...")
    print("="*60)
    
    # Laisser un petit temps pour s'assurer que le service est prêt
    time.sleep(3)
    
    results = []
    results.append(test_health_check())
    results.append(test_ask_endpoint())
    results.append(test_evaluate_endpoint())
    
    print("="*60)
    print("📊 Résultats des tests :")
    print(f"✅ Réussis : {sum(results)} / {len(results)}")
    print(f"❌ Échoués : {len(results) - sum(results)}")
    
    if all(results):
        print("🎉 Tous les tests ont réussi !")
    else:
        print("⚠️  Certains tests ont échoué.")
    
    return all(results)

if __name__ == "__main__":
    run_tests()
