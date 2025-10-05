# 🚀 Quick Start Guide - SpaceBio AI

## ✅ Status Actuel

- ✅ **572 articles chargés** dans la base de données
- ✅ **Serveur Django lancé** sur http://localhost:8000
- ⚠️ **Clés API à configurer** pour les fonctionnalités IA

## 🔑 Étape 1 : Configurer les Clés API

### Obtenir les clés :

1. **OpenRouter** (recommandé - gratuit au départ)
   - Aller sur https://openrouter.ai/keys
   - Créer un compte
   - Générer une clé API
   - Copier `sk-or-v1-xxxxx...`

2. **Grok** (optionnel - fallback)
   - Aller sur https://console.x.ai/
   - Créer un compte X.ai
   - Générer une clé API
   - Copier `xai-xxxxx...`

### Configurer le fichier .env :

```bash
# Ouvrir .env et modifier :
OPENROUTER_API_KEY=sk-or-v1-VOTRE_CLE_ICI
GROK_API_KEY=xai-VOTRE_CLE_ICI  # optionnel
```

## 🚀 Étape 2 : Accéder à l'Application

Le serveur tourne déjà sur : **http://localhost:8000**

### Pages disponibles :

- 🏠 **Accueil** : http://localhost:8000
- 🔍 **Recherche** : http://localhost:8000/search
- 💬 **Chat AI** : http://localhost:8000/chat
- ✍️ **Générateur** : http://localhost:8000/generate
- 📊 **Analytics** : http://localhost:8000/analytics
- 🔧 **Admin** : http://localhost:8000/admin

## 🎯 Étape 3 : Tester les Fonctionnalités

### Test 1 : Recherche Simple (GRATUIT - fonctionne déjà)

1. Aller sur http://localhost:8000/search
2. Chercher : "microgravity bone"
3. Sélectionner "Simple Search"
4. ✅ Résultats affichés sans besoin d'API !

### Test 2 : Chat AI (nécessite clé API)

1. Aller sur http://localhost:8000/chat
2. Poser une question : "What are the effects of microgravity?"
3. ✅ L'IA répond si la clé API est configurée
4. ❌ Erreur si pas de clé → configurer `.env`

### Test 3 : Recherche Sémantique (nécessite embeddings)

```bash
# Générer les embeddings (coût ~$0.50)
source venv/Scripts/activate
python manage.py generate_embeddings
```

Puis tester sur http://localhost:8000/search avec "Semantic Search"

## 🛠️ Commandes Utiles

```bash
# Activer l'environnement virtuel
source venv/Scripts/activate   # Git Bash
.\venv\Scripts\activate         # PowerShell

# Lancer le serveur
python manage.py runserver

# Générer embeddings (optionnel)
python manage.py generate_embeddings

# Créer admin
python manage.py createsuperuser
```

## ❓ Troubleshooting

**❌ "AI Provider Error"** :
→ Vérifier que `.env` contient `OPENROUTER_API_KEY`

**❌ "Semantic search not working"** :
→ Lancer `python manage.py generate_embeddings`

**❌ "Server not starting"** :
→ Vérifier que port 8000 est libre
→ Ou lancer sur autre port : `python manage.py runserver 8001`

## 📊 Fonctionnalités par Coût

| Fonctionnalité | Coût | Status |
|---|---|---|
| Recherche simple | GRATUIT | ✅ Fonctionne |
| Liste articles | GRATUIT | ✅ Fonctionne |
| Admin Django | GRATUIT | ✅ Fonctionne |
| Chat AI | $0.01-0.05/conv | ⚠️ Besoin clé API |
| Résumé AI | $0.005/résumé | ⚠️ Besoin clé API |
| Génération article | $0.05-0.20/article | ⚠️ Besoin clé API |
| Recherche sémantique | $0.00001/recherche | ⚠️ Besoin embeddings |

## 🎯 Workflow Recommandé pour le Hackathon

1. **Démo sans frais** :
   - Utiliser recherche simple
   - Montrer l'interface
   - Expliquer la vision IA

2. **Démo avec IA** (budget $5) :
   - Configurer OpenRouter
   - Générer ~50 embeddings ($0.05)
   - Tester chat et génération

3. **Production complète** (budget $20) :
   - Générer tous les embeddings ($0.50)
   - Crédit OpenRouter ($10)
   - Buffer pour tests ($9.50)

## 🚀 Next Steps

1. ✅ Configurer `.env` avec vos clés API
2. 🧪 Tester le chat AI
3. 🔬 (Optionnel) Générer les embeddings
4. 🎨 Personnaliser les templates si besoin
5. 🚢 Déployer sur Vercel/Railway

---

**🎉 Bon hackathon !**
