FROM python:3.9-slim

WORKDIR /app

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers requirements et les installer avant le reste du code
# pour tirer parti du cache des couches Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code de l'application
COPY . .

# Créer le dossier data s'il n'existe pas
RUN mkdir -p data

# Exposer le port sur lequel l'application s'exécutera
EXPOSE 5000

# Commande par défaut pour exécuter l'application
CMD ["python", "run.py"]