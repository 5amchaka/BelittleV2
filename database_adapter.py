"""
Module d'adaptation pour les différentes bases de données.
Fournit une interface commune pour SQLite et PostgreSQL.
"""
import os
import sqlite3
import psycopg2
from psycopg2.extras import DictCursor

class DatabaseAdapter:
    """Classe abstraite définissant l'interface d'adaptation de base de données"""
    
    def get_connection(self):
        """Retourne une connexion à la base de données"""
        raise NotImplementedError
    
    def close_connection(self, conn):
        """Ferme une connexion à la base de données"""
        if conn:
            conn.close()
    
    def get_cursor(self, conn):
        """Retourne un curseur pour la connexion donnée"""
        raise NotImplementedError
    
    def adapt_query(self, query):
        """Adapte une requête SQL pour la base de données spécifique"""
        return query

class SQLiteAdapter(DatabaseAdapter):
    """Adaptateur pour SQLite"""
    
    def __init__(self, database_path):
        self.database_path = database_path
    
    def get_connection(self):
        """Établit une connexion à la base de données SQLite"""
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row  # Pour accéder aux colonnes par nom
        return conn
    
    def get_cursor(self, conn):
        """Retourne un curseur pour la connexion SQLite"""
        return conn.cursor()
    
    def adapt_query(self, query):
        """Adapte une requête SQL pour SQLite"""
        # SQLite utilise ? comme placeholder
        return query

class PostgreSQLAdapter(DatabaseAdapter):
    """Adaptateur pour PostgreSQL"""
    
    def __init__(self, host, port, dbname, user, password):
        self.host = host
        self.port = port
        self.dbname = dbname
        self.user = user
        self.password = password
    
    def get_connection(self):
        """Établit une connexion à la base de données PostgreSQL"""
        conn = psycopg2.connect(
            host=self.host,
            port=self.port,
            dbname=self.dbname,
            user=self.user,
            password=self.password
        )
        return conn
    
    def get_cursor(self, conn):
        """Retourne un curseur pour la connexion PostgreSQL"""
        return conn.cursor(cursor_factory=DictCursor)
    
    def adapt_query(self, query):
        """Adapte une requête SQL pour PostgreSQL"""
        # PostgreSQL utilise %s comme placeholder au lieu de ?
        return query.replace('?', '%s')

def get_db_adapter():
    """
    Retourne l'adaptateur de base de données approprié selon la configuration.
    """
    db_engine = os.environ.get('DB_ENGINE', 'sqlite').lower()
    
    if db_engine == 'postgres':
        host = os.environ.get('DB_HOST', 'postgres')
        port = os.environ.get('DB_PORT', '5432')
        dbname = os.environ.get('DB_NAME', 'entreprise')
        user = os.environ.get('DB_USER', 'postgres')
        password = os.environ.get('DB_PASSWORD', 'postgres')
        
        return PostgreSQLAdapter(host, port, dbname, user, password)
    else:
        # Par défaut, utiliser SQLite
        from config import DATABASE
        return SQLiteAdapter(DATABASE)