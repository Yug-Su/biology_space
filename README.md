# 🚀 SpaceBio AI Intelligence Platform

AI-powered research platform for NASA space biology publications. Built for NASA Space Apps Challenge 2025.

## ✨ Features

- **🔍 Semantic Search**: AI-powered search using OpenAI embeddings
- **💬 AI Chat Assistant**: Conversational AI for research questions
- **✍️ Article Generator**: Generate comprehensive scientific articles
- **📊 Analytics Dashboard**: Track searches and generations
- **572 Research Articles** indexed from NASA PMC database

## 🏗️ Tech Stack

- **Backend**: Django 5.0 + SQLite
- **Frontend**: TailwindCSS + Alpine.js + HTMX
- **AI**: OpenRouter + Grok APIs
- **Embeddings**: OpenAI text-embedding-3-small

## 🚀 Quick Start

### 1. Configuration des clés API

Créer un fichier `.env` à la racine :

```bash
cp .env.example .env
```

Modifier `.env` avec vos clés API :

```env
# OpenRouter API (https://openrouter.ai/)
OPENROUTER_API_KEY=sk-or-v1-xxxxx

# Grok API (https://console.x.ai/)
GROK_API_KEY=xai-xxxxx
```

**Où obtenir les clés ?**

- **OpenRouter**: https://openrouter.ai/keys (gratuit avec crédits de départ)
- **Grok**: https://console.x.ai/ (nécessite compte X.ai)

### 2. Installation

```bash
# Activer l'environnement virtuel
source venv/Scripts/activate   # Windows Git Bash
# ou
.\venv\Scripts\activate         # Windows PowerShell

# Installer les dépendances
pip install -r requirements.txt

# Appliquer les migrations (déjà fait)
# python manage.py migrate

# Charger les articles (déjà fait - 572 articles)
# python manage.py load_articles
```

### 3. Générer les embeddings (OPTIONNEL)

⚠️ **Coût**: ~$0.50 pour 572 articles avec OpenAI embeddings

```bash
# Générer les embeddings pour la recherche sémantique
python manage.py generate_embeddings
```

**Note**: La recherche sémantique ne fonctionnera qu'après avoir généré les embeddings. Sinon, le système utilise la recherche simple par texte.

### 4. Lancer le serveur

```bash
python manage.py runserver
```

Ouvrir http://localhost:8000

## 📁 Structure du Projet

```
007/
├── core/                       # App principale Django
│   ├── models.py              # Models (Article, Embedding, Chat)
│   ├── views.py               # Vues (search, chat, generate)
│   ├── services/
│   │   ├── ai_providers.py    # OpenRouter + Grok
│   │   └── embeddings.py      # Service embeddings
│   ├── management/commands/
│   │   ├── load_articles.py   # Charger CSV
│   │   └── generate_embeddings.py
│   └── templates/core/        # Templates HTML
├── Data/
│   └── SB_publication_PMC.csv # 608 articles NASA
├── db.sqlite3                 # Base de données
└── manage.py
```

## 🎯 Fonctionnalités Principales

### 1. Recherche

- **Simple Search**: Recherche textuelle classique (GRATUIT)
- **Semantic Search**: Recherche sémantique IA (nécessite embeddings)

### 2. Chat AI

- Conversation avec assistant IA spécialisé en biologie spatiale
- Maintient le contexte de la conversation
- Powered by OpenRouter (GPT-4) avec fallback Grok

### 3. Générateur d'Articles

Génère des articles scientifiques complets :
- **Types**: Review, Research, Protocol
- **Longueur**: Short (500w), Medium (1000w), Long (2000w)
- **Style**: Academic, Executive, Technical

### 4. Admin Django

Accéder à http://localhost:8000/admin

Créer un superuser :
```bash
python manage.py createsuperuser
```

## 💰 Estimation des Coûts API

**Embeddings (une seule fois)** :
- 572 articles × $0.00001/1K tokens ≈ **$0.50**

**Usage normal** :
- Recherche sémantique : $0.00001 par recherche
- Chat : $0.01-0.05 par conversation
- Génération article : $0.05-0.20 par article

**Astuce** : Utiliser la recherche simple (gratuite) quand possible !

## 🔧 Commandes Utiles

```bash
# Recharger les articles
python manage.py load_articles

# Générer embeddings
python manage.py generate_embeddings

# Shell Django
python manage.py shell

# Créer superuser
python manage.py createsuperuser
```

## 📊 Base de Données

**Articles actuels** : 572 (36 duplicatas ignorés)

Structure :
- `Article` : Articles scientifiques
- `ArticleEmbedding` : Vecteurs sémantiques (1536 dim)
- `ChatSession` : Historique conversations
- `SearchQuery` : Tracking recherches
- `GeneratedArticle` : Articles générés par IA

## 🐛 Troubleshooting

**Erreur "No module named 'httpx'"** :
```bash
pip install httpx
```

**Erreur API "Invalid key"** :
- Vérifier que `.env` est à la racine
- Vérifier les clés API dans `.env`

**Recherche sémantique ne fonctionne pas** :
- Générer les embeddings : `python manage.py generate_embeddings`
- Vérifier que `OPENROUTER_API_KEY` est configuré

**Chat AI ne répond pas** :
- Vérifier les clés API
- Voir les logs console pour détails erreur

## 🚀 Déploiement

Pour le hackathon, utiliser :
- **Vercel** : Frontend + Django (via serverless)
- **Railway** : Backend Django
- **PythonAnywhere** : Solution complète gratuite

## 📝 License

MIT License - NASA Space Apps Challenge 2025

## 👥 Équipe

Hackathon NASA Space Apps Challenge 2025 - Team SpaceBio

---

**🎯 Next Steps**:
1. Configurer vos clés API dans `.env`
2. Générer les embeddings (optionnel)
3. Tester l'interface !
