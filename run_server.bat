@echo off
REM Script pour démarrer le serveur Django sur Windows

echo Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

echo Demarrage du serveur Django...
echo Ouvrir http://localhost:8000 dans votre navigateur
echo Appuyer sur Ctrl+C pour arreter

python manage.py runserver 0.0.0.0:8000
