# Configuration de l'application
import os
from pathlib import Path

# Chemin de base de l'application
BASE_DIR = Path(__file__).resolve().parent

# Dossier de données
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Création du dossier data s'il n'existe pas
os.makedirs(DATA_DIR, exist_ok=True)

# Configuration de la base de données
DATABASE = os.path.join(DATA_DIR, 'entreprise.db')

# Clé secrète pour les sessions Flask
SECRET_KEY = os.environ.get('SECRET_KEY', 'votre_cle_secrete')

# Configuration du serveur
HOST = os.environ.get('HOST', '0.0.0.0')
PORT = int(os.environ.get('PORT', 5002))

# Configuration de la base de données
DB_ENGINE = os.environ.get('DB_ENGINE', 'sqlite').lower()  # 'sqlite' ou 'postgres'

# Configuration PostgreSQL
if DB_ENGINE == 'postgres':
    DB_NAME = os.environ.get('DB_NAME', 'entreprise')
    DB_USER = os.environ.get('DB_USER', 'postgres')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'postgres')
    DB_HOST = os.environ.get('DB_HOST', 'postgres')
    DB_PORT = os.environ.get('DB_PORT', '5432')

# Chemin des templates de documents
TEMPLATES_DOCUMENT_DIR = os.path.join(BASE_DIR, 'templates', 'document_templates')
os.makedirs(TEMPLATES_DOCUMENT_DIR, exist_ok=True)

# Configuration des logs
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)