# 🐙 Guide GitHub - Partager le Projet SpaceBio AI

## Étape 1 : Créer le Dépôt sur GitHub

1. Aller sur **https://github.com/new**
2. Remplir :
   - **Repository name** : `spacebio-ai-platform`
   - **Description** : `🚀 AI-powered research platform for NASA space biology - Space Apps Challenge 2025`
   - **Visibilité** : Public ✅
   - **NE PAS** cocher "Add README" (on a déjà le nôtre)
3. Cliquer **Create repository**

## Étape 2 : Initialiser Git Localement

```bash
# Aller dans le dossier du projet
cd C:\Users\iamfe\thebox\007

# Initialiser git
git init

# Ajouter tous les fichiers (sauf ceux dans .gitignore)
git add .

# Premier commit
git commit -m "🚀 Initial commit - SpaceBio AI Platform for NASA Space Apps 2025"
```

## Étape 3 : Lier au Dépôt GitHub

Remplacer `VOTRE_USERNAME` par votre nom d'utilisateur GitHub :

```bash
# Ajouter le remote GitHub
git remote add origin https://github.com/VOTRE_USERNAME/spacebio-ai-platform.git

# Vérifier
git remote -v

# Pousser sur GitHub
git branch -M main
git push -u origin main
```

## Étape 4 : Vérifier sur GitHub

Aller sur **https://github.com/VOTRE_USERNAME/spacebio-ai-platform**

Vous devriez voir :
- ✅ Tous les fichiers
- ✅ README.md affiché
- ✅ 572 articles dans Data/

## ⚠️ Fichiers Exclus (via .gitignore)

Ces fichiers ne seront PAS poussés (c'est normal) :
- `.env` (contient vos clés API secrètes)
- `venv/` (environnement virtuel Python)
- `__pycache__/` (fichiers Python compilés)
- `db.sqlite3` (base de données locale)

## 🔐 Sécurité des Clés API

**IMPORTANT** : Ne JAMAIS pousser `.env` avec vos clés API !

Le fichier `.gitignore` protège automatiquement :
```
.env
.env.local
db.sqlite3
```

## 📝 Ajouter un Badge au README

Optionnel - Ajouter en haut du README.md :

```markdown
![NASA](https://img.shields.io/badge/NASA-Space%20Apps%20Challenge-red)
![Django](https://img.shields.io/badge/Django-5.0-green)
![Python](https://img.shields.io/badge/Python-3.13-blue)
![Articles](https://img.shields.io/badge/Articles-572-orange)
```

## 🚀 Commandes Git Utiles

```bash
# Voir le status
git status

# Ajouter des modifications
git add .
git commit -m "✨ Add new feature"
git push

# Voir l'historique
git log --oneline

# Créer une branche
git checkout -b feature/nouvelle-feature
```

## 🌟 Améliorer la Visibilité du Repo

### 1. Ajouter des Topics sur GitHub

Dans votre repo GitHub :
1. Cliquer sur ⚙️ (Settings) à droite
2. Dans "Topics", ajouter :
   - `nasa-space-apps`
   - `space-biology`
   - `artificial-intelligence`
   - `django`
   - `python`
   - `openai`
   - `hackathon`

### 2. Ajouter une Image de Preview

Créer un dossier `screenshots/` :
```bash
mkdir screenshots
# Ajouter des captures d'écran de l'interface
```

Puis mettre dans README.md :
```markdown
![SpaceBio AI Preview](screenshots/homepage.png)
```

### 3. Ajouter LICENSE

```bash
# Créer LICENSE MIT
echo "MIT License

Copyright (c) 2025 SpaceBio AI Team

Permission is hereby granted..." > LICENSE
```

## 📤 Partager le Projet

Votre lien GitHub sera :
```
https://github.com/VOTRE_USERNAME/spacebio-ai-platform
```

Partager sur :
- 🐦 Twitter/X : "Built AI platform for @NASA Space Apps Challenge"
- 💼 LinkedIn : Post avec lien GitHub
- 📧 Email jury NASA
- 🌐 README du hackathon

## 🔄 Mettre à Jour le Repo

```bash
# Après modifications
git add .
git commit -m "✨ Description des changements"
git push
```

## ❓ Troubleshooting

**Erreur "remote origin already exists"** :
```bash
git remote remove origin
git remote add origin https://github.com/VOTRE_USERNAME/spacebio-ai-platform.git
```

**Erreur "permission denied"** :
```bash
# Utiliser token GitHub au lieu de password
# Créer token sur https://github.com/settings/tokens
```

**Fichiers trop gros** :
```bash
# Vérifier la taille
du -sh *
# GitHub limite à 100MB par fichier
```

---

**🎉 Votre projet sera visible publiquement sur GitHub !**
