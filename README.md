# Application de Gestion d'Entreprises

Application web Flask permettant la gestion d'une base de données d'entreprises. Cette application facilite le suivi, la recherche et l'organisation d'informations sur les entreprises partenaires.

## Fonctionnalités principales

- **Gestion des entreprises** : ajout, modification et suppression d'entreprises
- **Recherche avancée** : filtrage par corps de métier, type d'entreprise ou recherche libre
- **Génération de documents** : création automatisée de documents administratifs à partir des données (DC1, DC2, etc.)
- **Interface responsive** : utilisation sur ordinateur, tablette ou mobile

## Technologies utilisées

- **Back-end** : Python, Flask, SQLite
- **Front-end** : HTML, CSS, JavaScript
- **Déploiement** : Waitress (WSGI), Docker
- **Génération de documents** : docxtpl, pandas, xlsxwriter

## Capture d'écran

![Capture d'écran de l'application](https://placeholder.com/screenshot.png)

## Démarrage rapide

Pour démarrer rapidement avec l'application, suivez ces étapes :

```bash
# Cloner le dépôt
git clone <url_du_depot>
cd mon_appli_flask

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

1. **villes** : stockage des villes
2. **type_entreprise** : types d'entreprises (MOA, MOE, Co-traitant, etc.)
3. **corps_metier** : corps de métier (Électricité, Plomberie, etc.)
4. **code_postal** : codes postaux
5. **cedex** : informations CEDEX
6. **entreprise** : données principales des entreprises
7. **entreprise_corps_metier** : table de liaison N-N
8. **chiffre_affaires** : chiffres d'affaires annuels des entreprises

## Architecture du projet

Le projet suit une architecture MVC (Modèle-Vue-Contrôleur) adaptée à Flask :

- **Modèles** (`models/`) : gestion des données et opérations CRUD
- **Vues** (`templates/`) : interface utilisateur en HTML/Jinja2
- **Contrôleurs** (`routes/`) : logique métier et points d'entrée de l'API

## Environnements de déploiement

L'application peut être déployée dans différents environnements :

- **Développement** : démarrage avec `FLASK_ENV=development python run.py`
- **Production** : démarrage avec `python run.py` (utilise Waitress)
- **Docker** : conteneurisation avec `docker-compose up`

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

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## Auteur

Application développée par [Votre nom](mailto:email@example.com)