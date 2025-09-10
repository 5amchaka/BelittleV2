# Installation de Belittle V2 sur un NAS

Ce guide vous accompagne dans l'installation de l'application Belittle V2 sur votre NAS (Network Attached Storage).

## Prérequis

### NAS Compatible
- NAS avec support Docker (Synology DSM 7.0+, QNAP QTS 4.4+, etc.)
- Au moins 2 GB de RAM disponible
- 5 GB d'espace de stockage libre

### Accès réseau
- Interface web d'administration du NAS
- Accès SSH (optionnel, mais recommandé)
- Port 5002 disponible sur le réseau local

## Méthode 1 : Installation avec Docker Compose (Recommandée)

### Étape 1 : Préparation des fichiers

1. **Créer un dossier sur votre NAS** (via l'interface web ou SSH) :
   ```bash
   # Via SSH
   mkdir -p /volume1/docker/belittle-v2
   cd /volume1/docker/belittle-v2
   ```

2. **Transférer les fichiers du projet** :
   - Copier tous les fichiers du projet dans le dossier créé
   - Ou cloner depuis Git si disponible :
     ```bash
     git clone [URL_REPO] /volume1/docker/belittle-v2
     ```

### Étape 2 : Configuration

1. **Modifier le fichier docker-compose.yaml** si nécessaire :
   ```yaml
   services:
     projet_belittle:
       build: .
       ports:
         - "5002:5002"
       volumes:
         - .:/app
         - ./data:/app/data
       environment:
         - SECRET_KEY=votre_cle_secrete_unique
         - HOST=0.0.0.0
         - PORT=5002
         - FLASK_ENV=production
       restart: unless-stopped
   ```

2. **Créer le dossier data** :
   ```bash
   mkdir -p data
   ```

### Étape 3 : Déploiement

1. **Via interface Docker du NAS** :
   - Ouvrir Docker dans l'interface d'administration
   - Aller dans "Projet" > "Créer"
   - Sélectionner le dossier contenant docker-compose.yaml
   - Cliquer sur "Créer"

2. **Via SSH** :
   ```bash
   cd /volume1/docker/belittle-v2
   docker-compose up -d
   ```

### Étape 4 : Initialisation de la base de données

1. **Accéder au conteneur** :
   ```bash
   docker exec -it belittle-v2_projet_belittle_1 bash
   ```

2. **Initialiser la base** :
   ```bash
   python utils/init_db.py
   ```

3. **Sortir du conteneur** :
   ```bash
   exit
   ```

## Méthode 2 : Installation manuelle avec Python

### Étape 1 : Installation de Python (si non disponible)

**Synology** :
- Installer le paquet Python 3.11 depuis le Centre de paquets

**QNAP** :
- Installer Python via QPKG Center ou Entware

### Étape 2 : Préparation

1. **Créer un dossier** :
   ```bash
   mkdir -p /share/applications/belittle-v2
   cd /share/applications/belittle-v2
   ```

2. **Transférer les fichiers** du projet

3. **Installer les dépendances** :
   ```bash
   pip3 install -r requirements.txt
   ```

### Étape 3 : Configuration

1. **Initialiser la base de données** :
   ```bash
   python3 utils/init_db.py
   ```

2. **Configurer les variables d'environnement** :
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY=votre_cle_secrete_unique
   ```

### Étape 4 : Démarrage

1. **Démarrage manuel** :
   ```bash
   python3 run.py
   ```

2. **Création d'un service système** (optionnel) :
   Créer un script de démarrage automatique selon votre NAS.

## Configuration réseau et accès

### Configuration du pare-feu
- Ouvrir le port 5002 dans les paramètres de pare-feu du NAS
- Ajouter une règle pour autoriser les connexions entrantes sur le port 5002

### Accès à l'application
Une fois installée, l'application sera accessible à :
```
http://[IP_DU_NAS]:5002
```

Exemple : `http://192.168.1.100:5002`

### Configuration du reverse proxy (optionnel)
Pour un accès via sous-domaine, configurer le reverse proxy de votre NAS :

**Synology** :
- Control Panel > Application Portal > Reverse Proxy
- Source : `belittle.monnas.local:80`
- Destination : `localhost:5002`

**QNAP** :
- Via Virtual Host ou Proxy Server dans les paramètres web

## Maintenance et sauvegarde

### Sauvegarde des données
```bash
# Sauvegarder la base de données
cp data/entreprise.db /volume1/backups/belittle-backup-$(date +%Y%m%d).db

# Sauvegarder les templates
tar -czf /volume1/backups/belittle-templates-$(date +%Y%m%d).tar.gz templates/document_templates/
```

### Mise à jour de l'application
```bash
# Arrêter l'application
docker-compose down

# Mettre à jour les fichiers
git pull  # ou remplacer les fichiers manuellement

# Relancer l'application
docker-compose up -d --build
```

### Logs et monitoring
```bash
# Consulter les logs
docker-compose logs -f projet_belittle

# Vérifier le statut
docker-compose ps
```

## Dépannage

### Problèmes courants

**Port déjà utilisé** :
```bash
# Changer le port dans docker-compose.yaml
ports:
  - "5003:5002"  # Utiliser 5003 au lieu de 5002
```

**Permissions insuffisantes** :
```bash
# Corriger les permissions
chmod -R 755 /volume1/docker/belittle-v2
chown -R 1000:1000 /volume1/docker/belittle-v2/data
```

**Base de données corrompue** :
```bash
# Restaurer depuis une sauvegarde
cp /volume1/backups/belittle-backup-YYYYMMDD.db data/entreprise.db
```

**Conteneur qui ne démarre pas** :
```bash
# Vérifier les logs
docker logs belittle-v2_projet_belittle_1

# Reconstruire l'image
docker-compose build --no-cache
```

### Vérification de l'installation

1. **Test de connectivité** :
   ```bash
   curl http://localhost:5002
   ```

2. **Vérification des processus** :
   ```bash
   docker ps | grep belittle
   ```

3. **Test de fonctionnalité** :
   - Accéder à l'interface web
   - Tester la recherche d'entreprises
   - Vérifier la génération de documents

## Optimisations pour NAS

### Performance
- Allouer au moins 2 GB de RAM au conteneur
- Utiliser un disque SSD pour la base de données si disponible
- Configurer des limites de ressources :
  ```yaml
  deploy:
    resources:
      limits:
        memory: 2G
        cpus: '1.0'
  ```

### Sécurité
- Changer la clé secrète par défaut
- Utiliser HTTPS avec un certificat SSL
- Limiter l'accès par adresses IP si nécessaire
- Activer les logs d'audit

### Automatisation
- Configurer des tâches cron pour les sauvegardes automatiques
- Mettre en place une surveillance des logs
- Configurer des alertes en cas de dysfonctionnement

## Support

En cas de problème, vérifiez :
1. Les logs de l'application
2. L'état des conteneurs Docker
3. La disponibilité des ressources (RAM, disque)
4. La connectivité réseau

Pour un support technique, consultez la documentation du projet dans `CLAUDE.md`.