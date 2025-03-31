"""
Module de gestion de la base de données.
Fournit les fonctions get_db et close_db compatibles avec le code existant,
mais utilise le nouveau DatabaseManager en arrière-plan.
"""
from database_manager import DatabaseManager

# Instance globale du gestionnaire de base de données
_db_manager = DatabaseManager()

def get_db():
    """Établit une connexion à la base de données et configure le row_factory"""
    return _db_manager.get_db()

def close_db(conn):
    """Ferme la connexion à la base de données"""
    _db_manager.close_db(conn)

def execute_query(query, params=None, fetch_one=False, fetch_all=False, commit=False):
    """
    Exécute une requête SQL et retourne le résultat approprié.
    
    Cette fonction est un wrapper pratique pour utiliser le gestionnaire de base de données
    sans avoir à gérer manuellement les connexions.
    """
    return _db_manager.execute_query(query, params, fetch_one, fetch_all, commit)