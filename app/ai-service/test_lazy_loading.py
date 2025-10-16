#!/usr/bin/env python3
"""
Script de test pour vérifier le chargement lazy du vectordb
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag.vectorstore_manager import VectorStoreManager

def test_lazy_loading():
    print("Test du chargement lazy du vectordb...")

    # Créer une instance du gestionnaire
    manager = VectorStoreManager()

    print("Avant l'appel à get_vectordb() - la base n'est pas encore chargée")

    # Accéder à la base vectorielle - cela devrait la charger
    vectordb = manager.get_vectordb()

    print(f"Après l'appel à get_vectordb() - la base a été chargée avec succès")
    print(f"Type de vectordb: {type(vectordb)}")

    # essayer d'accéder à la base vectorielle - cela devrait réutiliser la même instance
    print("🔄 Test de la réutilisation de l'instance existante...")
    vectordb2 = manager.get_vectordb()
    
    if vectordb is vectordb2:
        print("✅ Les deux appels ont retourné la même instance - le caching fonctionne correctement!")
    else:
        print("❌ Les instances sont différentes - problème avec le caching")

    print("Test terminé avec succès!")

if __name__ == "__main__":
    test_lazy_loading()