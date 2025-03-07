import sqlite3
from config import DATABASE

def get_db():
    """Établit une connexion à la base de données et configure le row_factory"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Pour accéder aux colonnes par nom
    return conn

def close_db(conn):
    """Ferme la connexion à la base de données"""
    if conn:
        conn.close()