# Belittle V2 - Application de Gestion d'Entreprises et Projets

Application web Flask permettant la gestion d'une base de données d'entreprises et la gestion complète de projets. Cette application facilite le suivi, la recherche et l'organisation d'informations sur les entreprises partenaires ainsi que la gestion des projets, lots et documents administratifs associés.

## Fonctionnalités principales

- **Gestion des entreprises** : ajout, modification et suppression d'entreprises
- **Gestion des projets** : création et suivi de projets avec MOA/MOE, lots et avenants
- **Gestion des lots** : attribution d'entreprises aux lots avec montants et suivi
- **Recherche avancée** : filtrage par corps de métier, type d'entreprise ou recherche libre
- **Génération de documents** : création automatisée de documents administratifs (DC1, DC2, ATTRI1, Ordre de Service, etc.)
- **Interface responsive** : utilisation sur ordinateur, tablette ou mobile

## Technologies utilisées

- **Back-end** : Python, Flask, SQLite, SQLAlchemy
- **Front-end** : HTML, CSS, JavaScript, Bootstrap
- **Déploiement** : Waitress (WSGI), Docker, Docker Compose
- **Génération de documents** : docxtpl, docxcompose, pandas, xlsxwriter

## Capture d'écran

![Capture d'écran de l'application](https://placeholder.com/screenshot.png)

## Démarrage rapide

Pour démarrer rapidement avec l'application, suivez ces étapes :

```bash
# Cloner le dépôt
git clone <url_du_depot>
cd Projet_Belittle

# Installer les dépendances
pip install -r requirements.txt

# Initialiser la base de données
python utils/init_db.py

# Démarrer l'application
python run.py
```

Pour plus de détails sur l'installation, consultez le [Guide d'installation](INSTALLATION.md).

## Structure de la base de données

L'application utilise SQLite avec le schéma suivant :

### Tables principales
1. **entreprise** : données principales des entreprises
2. **projets** : informations sur les projets (MOA, MOE, mandataire)
3. **lots** : lots des projets avec montants
4. **lot_entreprises** : attribution des entreprises aux lots

### Tables de référence
5. **villes** : stockage des villes
6. **type_entreprise** : types d'entreprises (MOA, MOE, Co-traitant, etc.)
7. **corps_metier** : corps de métier (Électricité, Plomberie, etc.)
8. **code_postal** : codes postaux
9. **cedex** : informations CEDEX
10. **entreprise_corps_metier** : table de liaison N-N
11. **chiffre_affaires** : chiffres d'affaires annuels des entreprises
12. **montants_lot_entreprises** : historique des montants par lot et entreprise

## Architecture du projet

Le projet suit une architecture MVC (Modèle-Vue-Contrôleur) adaptée à Flask :

- **Modèles** (`models/`) : gestion des données et opérations CRUD
  - `entreprise.py` : opérations sur les entreprises, recherche, données financières
  - `document.py` : génération de documents administratifs
  - `projet.py` : gestion des projets, lots et attributions
- **Vues** (`templates/`) : interface utilisateur en HTML/Jinja2
- **Contrôleurs** (`routes/`) : logique métier et points d'entrée de l'API
  - `main.py` : page d'accueil et recherche
  - `entreprise.py` : gestion des entreprises
  - `document.py` : génération de documents et gestion des projets

## Environnements de déploiement

L'application peut être déployée dans différents environnements :

- **Développement** : démarrage avec `FLASK_ENV=development python run.py` (port 5002)
- **Production** : démarrage avec `python run.py` (utilise Waitress, port 5002)
- **Docker** : conteneurisation avec `docker-compose up` (port 5002)

L'application est accessible sur `http://localhost:5002` par défaut.

## Utilitaires

- `utils/init_db.py` : création et initialisation de la base de données
- `utils/import_excel.py` : importation de données depuis un fichier Excel
- `utils/diagnose_ca.py` : diagnostic de la table des chiffres d'affaires

## Évolutions futures

- [ ] Pagination des résultats de recherche
- [ ] Système d'authentification des utilisateurs
- [ ] Export des données en Excel/CSV/PDF
- [ ] API REST complète
- [ ] Tests automatisés
- [ ] Amélioration de l'interface de gestion des projets
- [ ] Gestion avancée des avenants
- [ ] Workflow de validation des documents

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## Auteur

Application développée par [Votre nom](mailto:email@example.com)