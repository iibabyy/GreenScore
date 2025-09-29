#!/usr/bin/env python3
"""
Script de test pour vérifier que le service AI avec RAG fonctionne correctement.
Gère les timeouts longs pour le LLM et la base vectorielle.
"""

import requests
import time

BASE_URL = "http://localhost:5001/api"

def test_ask_endpoint():
    """Test de la route /ask"""
    print("🔍 Test de la route /ask...")
    try:
        response = requests.post(
            f"{BASE_URL}/ask",
            params={"question": "bonjour"},
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
            params={
            "product_description": (
                "Impact Whey Protein est la protéine en poudre phare de MyProtein, qui a d'ailleurs fortement contribué au succès de la marque sur le marché international. "
                "Elle est composée à 100% de whey concentrée ce qui lui permet d'afficher un prix imbattable sur le format 1000g. Selon la marque, cette formule contient de la whey qui est extraite en intégralité du lait de vache qui est simplement filtrée et séchée par pulvérisation afin de garantir l'intégrité des chaines d'acides aminés.\n\n"
                "Caractéristiques de l'Impact Whey Protein\n"
                "21g de protéines par dose (taux de protéines de 82%)\n"
                "4.5g d'acides aminés ramifiés (BCAA) par prise\n"
                "Faible teneur en sucres\n"
                "Impact Whey Protein de MyProtein vous accompagne pour contribuer à augmenter votre masse musculaire. Cette affirmation a été prouvée scientifiquement et est autorisée par l'autorité européenne de sécurité des aliments. Avec seulement 103 calories par dose, cette whey s'intègre facilement à votre régime alimentaire."
            )
            },
            timeout=900  # timeout plus long pour RAG
        )
        response.raise_for_status()
        data = response.json()
        print(f"✅ /evaluate fonctionne !")
        #print(f"📦 Produit : {data['product']}")
        print(f"📊 Évaluation : {data['evaluation']}")
        #print(f"📚 Sources : {data['source_documents']}\n")
        #print(f"🔍 Info debug : {data['debug_info']}\n")
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
        response = requests.get("http://localhost:5001/api/debug-retrieval", timeout=30)
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
    
    
    results = []
    #results.append(test_ask_endpoint())
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
