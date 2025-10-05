# 🚀 SpaceBio AI Intelligence Platform

AI-powered research platform for NASA space biology publications. Built for NASA Space Apps Challenge 2025.

## ✨ Features

- **🔍 Enhanced Search**: Advanced search across titles, abstracts, and authors with year filtering
- **💬 AI Chat Assistant**: Conversational AI for research questions
- **✍️ Article Generator**: Generate comprehensive scientific articles
- **📊 Analytics Dashboard**: Track searches and generations
- **572 Research Articles** indexed from NASA PMC database

## 🏗️ Tech Stack

- **Backend**: Django 5.0 + SQLite
- **Frontend**: TailwindCSS + Alpine.js + HTMX
- **AI**: OpenRouter + Groq APIs
- **Search**: Multi-field text search with intelligent ranking

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

# Groq API (https://console.groq.com/)
GROQ_API_KEY=gsk_xxxxx
```

**Où obtenir les clés ?**

- **OpenRouter**: https://openrouter.ai/keys (gratuit avec crédits de départ)
- **Groq**: https://console.groq.com/ (gratuit avec crédits de départ)

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

### 3. Lancer le serveur

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
│   │   ├── ai_providers.py    # OpenRouter + Groq
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

### 1. Enhanced Search

- **Multi-field Search**: Recherche dans les titres, abstracts et auteurs
- **Smart Filtering**: Filtrage par année de publication
- **Intelligent Ranking**: Résultats triés par popularité et pertinence

### 2. Chat AI

- Conversation avec assistant IA spécialisé en biologie spatiale
- Maintient le contexte de la conversation
- Powered by OpenRouter (GPT-4) avec fallback Groq

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

**100% GRATUIT** :
- ✅ Recherche avancée : **GRATUIT** (aucune API payante)
- ✅ Navigation articles : **GRATUIT**
- ✅ Admin Django : **GRATUIT**

**Avec clés API** :
- Chat AI : $0.01-0.05 par conversation (OpenRouter/Groq)
- Génération article : $0.05-0.20 par article (OpenRouter/Groq)

**Budget recommandé pour le hackathon** : $5-10 pour tester les features AI

## 🔧 Commandes Utiles

```bash
# Recharger les articles
python manage.py load_articles

# Shell Django
python manage.py shell

# Créer superuser
python manage.py createsuperuser
```

## 📊 Base de Données

**Articles actuels** : 572 (36 duplicatas ignorés)

Structure :
- `Article` : 572 articles scientifiques NASA
- `ChatSession` : Historique conversations AI
- `SearchQuery` : Tracking recherches
- `GeneratedArticle` : Articles générés par IA

## 🐛 Troubleshooting

**Erreur "No module named 'httpx'"** :
```bash
pip install httpx
```

**Erreur API "Invalid key"** :
- Vérifier que `.env` est à la racine
- Vérifier les clés API OpenRouter/Groq dans `.env`

**Chat AI ne répond pas** :
- Vérifier que `OPENROUTER_API_KEY` ou `GROQ_API_KEY` est configuré
- Voir les logs console pour détails erreur

**Recherche ne retourne pas de résultats** :
- Vérifier l'orthographe
- Essayer des termes plus généraux (ex: "microgravity" au lieu de "microgravity effects")

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
1. Configurer vos clés API OpenRouter/Groq dans `.env` (pour Chat & Génération)
2. Tester la recherche avancée (100% gratuite !)
3. Essayer le Chat AI et le générateur d'articles
4. Préparer votre présentation pour le hackathon !
