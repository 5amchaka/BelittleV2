#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de test des connexions aux bases de données
"""
import os
import sys
import sqlite3
import psycopg2
from pathlib import Path
import logging

# Ajouter le répertoire parent au chemin d'importation
parent_dir = str(Path(__file__).resolve().parent.parent)
sys.path.append(parent_dir)

from config import DATABASE, DB_ENGINE
from database_adapter import SQLiteAdapter, PostgreSQLAdapter
from database_manager import DatabaseManager

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('db_test')

def test_sqlite_connection():
    """Teste la connexion à SQLite"""
    logger.info("Test de connexion à SQLite...")
    try:
        # Test direct
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT sqlite_version()")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        logger.info(f"✅ Connexion SQLite réussie (version: {version})")
        
        # Test via l'adaptateur
        adapter = SQLiteAdapter(DATABASE)
        conn = adapter.get_connection()
        cursor = adapter.get_cursor(conn)
        cursor.execute("SELECT sqlite_version()")
        version = cursor.fetchone()[0]
        adapter.close_connection(conn)
        logger.info(f"✅ Connexion via SQLiteAdapter réussie (version: {version})")
        
        return True
    except Exception as e:
        logger.error(f"❌ Erreur de connexion SQLite: {e}")
        return False

def test_postgres_connection():
    """Teste la connexion à PostgreSQL"""
    logger.info("Test de connexion à PostgreSQL...")
    try:
        # Récupérer les paramètres de connexion
        host = os.environ.get('DB_HOST', 'localhost')
        port = os.environ.get('DB_PORT', '5432')
        dbname = os.environ.get('DB_NAME', 'entreprise')
        user = os.environ.get('DB_USER', 'postgres')
        password = os.environ.get('DB_PASSWORD', 'postgres')
        
        # Test direct
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        logger.info(f"✅ Connexion PostgreSQL réussie (version: {version})")
        
        # Test via l'adaptateur
        adapter = PostgreSQLAdapter(host, port, dbname, user, password)
        conn = adapter.get_connection()
        cursor = adapter.get_cursor(conn)
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        adapter.close_connection(conn)
        logger.info(f"✅ Connexion via PostgreSQLAdapter réussie")
        
        return True
    except Exception as e:
        logger.error(f"❌ Erreur de connexion PostgreSQL: {e}")
        return False

def test_db_manager():
    """Teste le gestionnaire de base de données unifié"""
    logger.info("Test du gestionnaire de base de données...")
    try:
        manager = DatabaseManager()
        
        # Test simple de connexion
        conn = manager.get_db()
        manager.close_db(conn)
        logger.info(f"✅ Connexion via DatabaseManager réussie")
        
        # Test d'exécution de requête
        engine_name = "SQLite" if DB_ENGINE == "sqlite" else "PostgreSQL"
        result = manager.execute_query("SELECT 1 as test", fetch_one=True)
        logger.info(f"✅ Exécution de requête réussie ({engine_name})")
        
        return True
    except Exception as e:
        logger.error(f"❌ Erreur avec DatabaseManager: {e}")
        return False

def test_all_connections():
    """Teste toutes les connexions disponibles"""
    logger.info("=== Démarrage des tests de connexion aux bases de données ===")
    
    # Afficher la configuration actuelle
    logger.info(f"Configuration actuelle: DB_ENGINE={DB_ENGINE}")
    
    # Tester SQLite
    sqlite_ok = test_sqlite_connection()
    
    # Tester PostgreSQL si les variables d'environnement sont définies
    pg_vars_defined = all(var in os.environ for var in ['DB_HOST', 'DB_USER', 'DB_PASSWORD'])
    if pg_vars_defined:
        postgres_ok = test_postgres_connection()
    else:
        logger.warning("Variables d'environnement PostgreSQL non définies, test ignoré")
        postgres_ok = False
    
    # Tester le gestionnaire de base de données
    manager_ok = test_db_manager()
    
    # Résumé
    logger.info("=== Résumé des tests ===")
    logger.info(f"SQLite: {'✅ OK' if sqlite_ok else '❌ Échec'}")
    
    if pg_vars_defined:
        logger.info(f"PostgreSQL: {'✅ OK' if postgres_ok else '❌ Échec'}")
    else:
        logger.info("PostgreSQL: ⚠️ Non testé (variables d'environnement manquantes)")
    
    logger.info(f"Gestionnaire de base de données: {'✅ OK' if manager_ok else '❌ Échec'}")
    logger.info("=======================")
    
    # Retourner le statut global
    return (sqlite_ok and (postgres_ok if pg_vars_defined else True) and manager_ok)

if __name__ == "__main__":
    success = test_all_connections()
    sys.exit(0 if success else 1)