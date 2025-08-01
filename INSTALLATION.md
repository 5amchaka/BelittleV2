# Guide d'installation

Ce document explique comment installer et configurer Belittle V2 - l'application de gestion d'entreprises et projets.

## Prérequis

- Python 3.9 ou supérieur
- pip (gestionnaire de paquets Python)
- Virtualenv (recommandé)

## Installation manuelle

### 1. Cloner le dépôt

```bash
git clone <url_du_depot>
cd Projet_Belittle
```

### 2. Créer et activer un environnement virtuel

```bash
# Sur Windows
python -m venv venv
venv\Scripts\activate

# Sur MacOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Initialiser la base de données

```bash
python utils/init_db.py
```

### 5. Exécuter l'application

```bash
# En mode développement
FLASK_ENV=development python run.py

# En mode production
python run.py
```

L'application sera accessible à l'adresse http://localhost:5002

## Installation avec Docker

### 1. Construire l'image Docker

```bash
docker build -t projet_belittle .
```

### Installation alternative avec Docker Compose

```bash
# Démarrer l'application avec Docker Compose
docker-compose up --build

# En arrière-plan
docker-compose up -d --build
```

### 2. Exécuter le conteneur

```bash
docker run -p 5002:5002 -v $(pwd)/data:/app/data projet_belittle
```

L'application sera accessible à l'adresse http://localhost:5002

## Configuration

Vous pouvez configurer l'application en modifiant le fichier `config.py` ou en définissant des variables d'environnement :

- `SECRET_KEY` : Clé secrète pour les sessions Flask
- `HOST` : Adresse IP d'écoute (par défaut: 0.0.0.0)
- `PORT` : Port d'écoute (par défaut: 5002)
- `FLASK_ENV` : Mode d'exécution (`development` ou `production`)

## Importation de données

Pour importer des données depuis un fichier Excel :

```bash
python utils/import_excel.py chemin/vers/votre_fichier.xlsx
```

## Structure des répertoires

```
Projet_Belittle/
├── app.py                  # Point d'entrée de l'application
├── config.py               # Configuration (DB, clés secrètes, serveur)
├── database.py             # Utilitaires de connexion à la base de données
├── requirements.txt        # Dépendances Python
├── run.py                  # Script d'exécution
├── Dockerfile              # Configuration Docker
├── docker-compose.yaml     # Configuration Docker Compose
├── CLAUDE.md               # Documentation pour Claude Code
├── models/                 # Modèles de données
│   ├── __init__.py
│   ├── entreprise.py       # Opérations CRUD pour les entreprises
│   ├── document.py         # Opérations pour les documents
│   └── projet.py           # Opérations pour les projets et lots
├── routes/                 # Contrôleurs / Routes
│   ├── __init__.py
│   ├── entreprise.py       # Routes pour la gestion des entreprises
│   ├── document.py         # Routes documents et projets
│   └── main.py             # Routes principales et recherche
├── templates/              # Templates HTML
│   ├── base.html
│   ├── index.html
│   ├── document/           # Templates pour les documents et projets
│   │   ├── dc1_form.html
│   │   ├── projets_list.html
│   │   └── ...
│   └── document_templates/ # Modèles de documents Word
│       ├── dc1_template.docx
│       └── dc2_template.docx
├── static/                 # Fichiers statiques
│   ├── css/
│   │   └── main.css
│   └── js/
│       ├── document.js
│       └── search.js
├── data/                   # Données
│   └── entreprise.db       # Base de données SQLite
└── utils/                  # Utilitaires
    ├── init_db.py          # Script d'initialisation de la BDD
    ├── import_excel.py     # Script d'importation Excel
    └── diagnose_ca.py      # Script de diagnostic des CA
```

## Résolution des problèmes courants

### La base de données n'est pas créée ou est inaccessible

- Vérifiez que le dossier `data` existe et est accessible en écriture
- Exécutez le script d'initialisation : `python utils/init_db.py`

### Problèmes d'importation Excel

- Vérifiez que le fichier existe et est accessible
- Assurez-vous que le format des colonnes correspond aux attentes de l'application

### L'application ne démarre pas

- Vérifiez les logs pour plus de détails
- Assurez-vous que le port n'est pas déjà utilisé par un autre service

## Sauvegarde et restauration

### Sauvegarde de la base de données

```bash
cp data/entreprise.db data/entreprise_backup_$(date +%Y%m%d).db
```

### Restauration de la base de données

```bash
cp data/entreprise_backup_YYYYMMDD.db data/entreprise.db
```