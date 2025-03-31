#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de migration des données de SQLite vers PostgreSQL
"""
import os
import sys
import sqlite3
import psycopg2
import psycopg2.extras
from pathlib import Path
import logging

# Ajouter le répertoire parent au chemin d'importation
parent_dir = str(Path(__file__).resolve().parent.parent)
sys.path.append(parent_dir)

from config import DATABASE

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('migration')

def get_sqlite_connection():
    """Établit une connexion à la base de données SQLite"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def get_pg_connection():
    """Établit une connexion à la base de données PostgreSQL"""
    host = os.environ.get('DB_HOST', 'localhost')
    port = os.environ.get('DB_PORT', '5432')
    dbname = os.environ.get('DB_NAME', 'entreprise')
    user = os.environ.get('DB_USER', 'postgres')
    password = os.environ.get('DB_PASSWORD', 'postgres')
    
    return psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password
    )

def get_sqlite_tables():
    """Récupère la liste des tables dans SQLite"""
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    return tables

def get_table_columns(table, sqlite_conn):
    """Récupère les colonnes d'une table SQLite"""
    cursor = sqlite_conn.cursor()
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [row['name'] for row in cursor.fetchall()]
    cursor.close()
    return columns

def migrate_table(table, sqlite_conn, pg_conn):
    """Migre les données d'une table de SQLite vers PostgreSQL"""
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    # Récupérer les colonnes de la table
    columns = get_table_columns(table, sqlite_conn)
    columns_str = ', '.join(columns)
    
    # Récupérer les données de SQLite
    sqlite_cursor.execute(f"SELECT {columns_str} FROM {table}")
    rows = sqlite_cursor.fetchall()
    
    # Si aucune donnée, passer à la table suivante
    if not rows:
        logger.info(f"Table {table} : aucune donnée à migrer")
        return 0
    
    # Préparer la requête d'insertion pour PostgreSQL
    placeholders = ', '.join(['%s'] * len(columns))
    
    # Éviter les conflits d'ID pour les tables avec des séquences
    if 'id_' + table in columns or table.startswith('id_'):
        # Réinitialiser la séquence pour être sûr
        if table == 'corps_metier':
            sequence_name = 'corps_metier_id_corps_metier_seq'
        else:
            sequence_name = f"{table}_id_{table[:-1] if table.endswith('s') else table}_seq"
        
        try:
            pg_cursor.execute(f"SELECT setval('{sequence_name}', GREATEST((SELECT COALESCE(MAX(id_{table[:-1] if table.endswith('s') else table}), 1) FROM {table}), 1))")
        except Exception as e:
            logger.warning(f"Impossible de réinitialiser la séquence {sequence_name}: {e}")
    
    # Migrer les données
    count = 0
    for row in rows:
        row_dict = dict(row)
        values = [row_dict[col] for col in columns]
        
        try:
            pg_cursor.execute(
                f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders}) ON CONFLICT DO NOTHING",
                values
            )
            count += 1
        except Exception as e:
            logger.error(f"Erreur lors de l'insertion dans {table} : {e}")
            pg_conn.rollback()
            break
    
    # Commit les changements
    pg_conn.commit()
    return count

def migrate_data():
    """Migre toutes les données de SQLite vers PostgreSQL"""
    try:
        # Vérifier si le fichier SQLite existe
        if not os.path.exists(DATABASE):
            logger.error(f"La base de données SQLite {DATABASE} n'existe pas")
            return
        
        # Obtenir les connexions
        sqlite_conn = get_sqlite_connection()
        pg_conn = get_pg_connection()
        
        # Obtenir la liste des tables
        tables = get_sqlite_tables()
        
        # Migrer chaque table
        total_count = 0
        for table in tables:
            logger.info(f"Migration de la table : {table}")
            count = migrate_table(table, sqlite_conn, pg_conn)
            logger.info(f"Table {table} : {count} lignes migrées")
            total_count += count
        
        logger.info(f"Migration terminée : {total_count} lignes migrées au total")
    
    except Exception as e:
        logger.error(f"Erreur lors de la migration : {e}")
    finally:
        # Fermer les connexions
        if 'sqlite_conn' in locals():
            sqlite_conn.close()
        if 'pg_conn' in locals():
            pg_conn.close()

def confirm_migration():
    """Demande une confirmation avant de lancer la migration"""
    print("⚠️ Vous êtes sur le point de migrer les données de SQLite vers PostgreSQL.")
    print("Cette opération va transférer toutes les données de la base SQLite vers PostgreSQL.")
    print("Assurez-vous que la base PostgreSQL est vide ou que vous êtes prêt à fusionner les données.")
    
    response = input("Voulez-vous continuer ? (o/n): ")
    return response.lower() in ['o', 'oui', 'y', 'yes']

if __name__ == "__main__":
    # Vérifier les variables d'environnement nécessaires
    required_vars = ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        logger.error(f"Variables d'environnement manquantes : {', '.join(missing_vars)}")
        logger.error("Définissez-les avant de lancer la migration.")
        sys.exit(1)
    
    # Demander confirmation
    if confirm_migration():
        logger.info("Démarrage de la migration...")
        migrate_data()
    else:
        logger.info("Migration annulée.")
