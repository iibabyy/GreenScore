# GreenScore

Application d'évaluation des compléments alimentaires selon leur impact environnemental.

## Structure du projet

- `app/frontend/` - Application React avec TypeScript
- `app/backend/` - API Node.js/Express
- `app/ai-service/` - Services d'intelligence artificielle
- `app/database/` - Scripts et configurations de base de données

## Prérequis

- Docker et Docker Compose
- Node.js (pour le développement local)
- Python 3.8+ (pour le développement local)
- Make (pour utiliser les commandes simplifiées)

## Configuration

1. Copier le fichier `.env.example` vers `.env` dans chaque service :
   ```bash
   cp .env.example ./app/frontend/.env
   cp .env.example ./app/backend/.env
   cp .env.example ./app/ai-service/.env
   ```

2. Mettre à jour les variables d'environnement dans les fichiers `.env` avec vos valeurs.

## Démarrage rapide avec Makefile (recommandé)

```bash
# Démarrer l'application en mode développement (rechargement automatique)
make start

# Arrêter tous les services
make stop

# Arrêter et supprimer tous les services et volumes
make down

# Afficher les logs
make logs
```

## Démarrage rapide avec Docker Compose

### Avec Docker en mode développement (avec rechargement automatique)

```bash
# Démarrer tous les services en mode développement
docker-compose -f docker-compose.yml up -d

# Arrêter tous les services
docker-compose -f docker-compose.yml down
```

### Développement local

#### Frontend
```bash
cd app/frontend
npm install
npm run dev
```

#### Backend
```bash
cd app/backend
npm install
npm run dev
```

#### AI Service
```bash
cd app/ai-service
pip install -r requirements.txt
python app.py
```

## Commandes Makefile disponibles

- `make start` - Démarrer l'application en mode développement
- `make stop` - Arrêter tous les services en mode développement
- `make down` - Arrêter et supprimer tous les services et volumes (développement)
- `make logs` - Afficher les logs des services (développement)
- `make build` - Construire les images Docker en mode développement
- `make clean` - Nettoyer les fichiers de build et node_modules
- `make help` - Afficher l'aide

## Services

- Frontend : http://localhost:3000
- Backend API : http://localhost:3001
- AI Service : http://localhost:5000
- Base de données : postgresql://localhost:5433