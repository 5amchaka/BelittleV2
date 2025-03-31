# Configuration Docker avec PostgreSQL

Ce document explique comment configurer et utiliser l'application avec Docker et PostgreSQL.

## Prérequis

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Configuration

### Paramètres d'environnement

Avant de lancer l'application, vous devez configurer les variables d'environnement. Un fichier `.env.example` est fourni comme modèle.

1. Créez votre fichier `.env` à partir du modèle :

```bash
cp .env.example .env
```

2. Modifiez les valeurs selon vos besoins :

```
# Configuration de l'application
SECRET_KEY=votre_cle_secrete_personnalisee
APP_PORT=5002

# Choix du moteur de base de données (sqlite ou postgres)
DB_ENGINE=postgres

# Configuration PostgreSQL
DB_NAME=entreprise
DB_USER=postgres
DB_PASSWORD=votre_mot_de_passe_securise
```

### Moteurs de base de données disponibles

L'application prend en charge deux moteurs de base de données :

- **SQLite** (par défaut) : Base de données fichier, idéale pour le développement
- **PostgreSQL** : Base de données relationnelle robuste, recommandée pour la production

Pour choisir le moteur, modifiez la variable `DB_ENGINE` dans votre fichier `.env`.

## Démarrage avec Docker Compose

### Premier démarrage

Pour démarrer l'application pour la première fois :

```bash
# Construire et démarrer les services
docker-compose up -d

# Initialiser la base de données PostgreSQL (si DB_ENGINE=postgres)
docker-compose exec app python utils/init_pg_db.py
```

### Utilisation quotidienne

Pour démarrer/arrêter les services :

```bash
# Démarrer
docker-compose up -d

# Arrêter
docker-compose down

# Voir les logs
docker-compose logs -f
```

## Migration des données

Si vous utilisez déjà SQLite et souhaitez migrer vers PostgreSQL :

1. Assurez-vous que votre base de données SQLite contient les données à migrer
2. Configurez PostgreSQL dans le fichier `.env` et définissez `DB_ENGINE=postgres`
3. Exécutez le script de migration :

```bash
# Démarrer les services
docker-compose up -d

# Exécuter la migration
docker-compose exec app python utils/migrate_data.py
```

## Volumes et persistance des données

Le `docker-compose.yml` définit deux volumes principaux :

- `./data:/app/data` : Stocke les fichiers de base de données SQLite
- `postgres_data` : Volume Docker pour les données PostgreSQL

Ces volumes garantissent que vos données persistent même si les conteneurs sont supprimés.

## Ports

Par défaut, l'application est accessible sur le port 5002. Vous pouvez modifier ce port en définissant la variable `APP_PORT` dans votre fichier `.env`.

## Dépannage

### Problèmes de connexion à PostgreSQL

Si l'application ne parvient pas à se connecter à PostgreSQL :

1. Vérifiez que le service PostgreSQL est en cours d'exécution :
   ```bash
   docker-compose ps
   ```

2. Vérifiez les logs de PostgreSQL :
   ```bash
   docker-compose logs postgres
   ```

3. Assurez-vous que les variables d'environnement sont correctement définies dans le fichier `.env`.

### Réinitialisation des données

Pour réinitialiser complètement la base de données PostgreSQL :

```bash
# Arrêter les conteneurs
docker-compose down

# Supprimer le volume PostgreSQL
docker volume rm nom_du_projet_postgres_data

# Redémarrer
docker-compose up -d

# Initialiser la base de données
docker-compose exec app python utils/init_pg_db.py
```

### Accès direct à PostgreSQL

Pour se connecter directement à la base de données PostgreSQL :

```bash
docker-compose exec postgres psql -U postgres -d entreprise
```

## Mises à jour

Lorsque vous mettez à jour l'application :

```bash
# Récupérer les derniers changements
git pull

# Reconstruire les images
docker-compose build

# Redémarrer les services
docker-compose up -d
```