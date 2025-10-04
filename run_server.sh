#!/bin/bash
# Script pour démarrer le serveur Django

# Activer l'environnement virtuel
source venv/Scripts/activate

# Vérifier que les dépendances sont installées
echo "Checking dependencies..."
pip list | grep -q "Django" || pip install -r requirements.txt

# Lancer le serveur
echo "Starting Django server on http://localhost:8000"
echo "Press Ctrl+C to stop"
python manage.py runserver 0.0.0.0:8000
