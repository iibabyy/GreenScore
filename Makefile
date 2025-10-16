# Makefile pour l'application GreenBook

# Variables
DOCKER_COMPOSE = docker compose -f docker-compose.yml

# Cible par défaut
.PHONY: help
help:
	@echo "GreenScore - Application d'évaluation des compléments alimentaires"
	@echo ""
	@echo "Commandes disponibles :"
	@echo "  make start          - Démarrer l'application "
	@echo "  make stop         - Arrêter tous les services "
	@echo "  make down         - Arrêter et supprimer tous les services et volumes "
	@echo "  make logs         - Afficher les logs des services "
	@echo "  make build        - Construire les images Docker "
	@echo "  make clean        - Nettoyer les fichiers de build et node_modules"
	@echo "  make help         - Afficher cette aide"


# tout premier lancement
.PHONY: init
init: start pull-model
	@echo "Attente de 10 secondes pour que le service Ollama soit prêt..."
	@sleep 10

#installer le modele ollama
.PHONY: pull-model
pull-model:
	docker exec ollama_service ollama pull phi3:mini
	
# Démarrer en mode développement
.PHONY: start
start:
	$(DOCKER_COMPOSE) up -d

#
# Arrêter les services en mode développement
.PHONY: stop
stop:
	$(DOCKER_COMPOSE) stop


.PHONY: down
down:
	$(DOCKER_COMPOSE) down --remove-orphans

# Si tu veux tout supprimer (⚠️ y compris modèles et BDD)
.PHONY: down-full
down-full:
	$(DOCKER_COMPOSE) down -v --remove-orphans

# Afficher les logs en mode développement
.PHONY: logs
logs:
	$(DOCKER_COMPOSE) logs -f


# Construire les images en mode développement
.PHONY: build
build-dev:
	$(DOCKER_COMPOSE) build

# Construire les images en mode production

# Nettoyer les fichiers de build et node_modules
.PHONY: clean
clean:
	@echo "Nettoyage des fichiers de build et node_modules..."
	@if [ -d "app/frontend/node_modules" ]; then rm -rf app/frontend/node_modules; fi
	@if [ -d "app/backend/node_modules" ]; then rm -rf app/backend/node_modules; fi
	@if [ -d "app/frontend/dist" ]; then rm -rf app/frontend/dist; fi
	@if [ -f "app/frontend/package-lock.json" ]; then rm app/frontend/package-lock.json; fi
	@if [ -f "app/backend/package-lock.json" ]; then rm app/backend/package-lock.json; fi
	@echo "Nettoyage terminé."

# Afficher l'état des services
.PHONY: ps
ps:
	$(DOCKER_COMPOSE) ps
