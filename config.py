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
PORT = int(os.environ.get('PORT', 5000))

# Chemin des templates de documents
TEMPLATES_DOCUMENT_DIR = os.path.join(BASE_DIR, 'templates', 'document_templates')
os.makedirs(TEMPLATES_DOCUMENT_DIR, exist_ok=True)