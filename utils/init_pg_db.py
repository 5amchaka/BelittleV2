#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script d'initialisation de la base de données PostgreSQL
"""
import os
import sys
from pathlib import Path
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Ajouter le répertoire parent au chemin d'importation
parent_dir = str(Path(__file__).resolve().parent.parent)
sys.path.append(parent_dir)

def get_pg_connection(dbname=None):
    """Établit une connexion à PostgreSQL"""
    host = os.environ.get('DB_HOST', 'localhost')
    port = os.environ.get('DB_PORT', '5432')
    user = os.environ.get('DB_USER', 'postgres')
    password = os.environ.get('DB_PASSWORD', 'postgres')
    
    # Si dbname est None, se connecter à la base postgres par défaut
    if dbname is None:
        dbname = 'postgres'
    
    return psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password
    )

def create_database():
    """Crée la base de données si elle n'existe pas"""
    db_name = os.environ.get('DB_NAME', 'entreprise')
    
    try:
        # Se connecter à postgres pour vérifier/créer la base de données
        conn = get_pg_connection()
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Vérifier si la base de données existe
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Création de la base de données {db_name}...")
            cursor.execute(f"CREATE DATABASE {db_name}")
            print(f"✅ Base de données {db_name} créée avec succès!")
        else:
            print(f"La base de données {db_name} existe déjà.")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ Erreur lors de la création de la base de données : {e}")
        return False
    
    return True

def init_database():
    """Initialise la base de données avec le schéma de base"""
    db_name = os.environ.get('DB_NAME', 'entreprise')
    
    print(f"Initialisation de la base de données PostgreSQL : {db_name}")
    
    # Créer d'abord la base de données si elle n'existe pas
    if not create_database():
        return
    
    # Connexion à la BDD
    try:
        conn = get_pg_connection(db_name)
        cursor = conn.cursor()
        
        # Créer les tables principales
        # Table des villes
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS villes (
            id_ville SERIAL PRIMARY KEY,
            nom_ville TEXT NOT NULL UNIQUE
        )
        ''')
        
        # Table des types d'entreprise
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS type_entreprise (
            id_type_entreprise SERIAL PRIMARY KEY,
            nom_type_entreprise TEXT NOT NULL UNIQUE
        )
        ''')
        
        # Table des corps de métier
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS corps_metier (
            id_corps_metier SERIAL PRIMARY KEY,
            nom_corps_metier TEXT NOT NULL UNIQUE
        )
        ''')
        
        # Table des codes postaux
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS code_postal (
            id_cp SERIAL PRIMARY KEY,
            code_postal TEXT NOT NULL UNIQUE
        )
        ''')
        
        # Table des cedex
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS cedex (
            id_cedex SERIAL PRIMARY KEY,
            nom_cedex TEXT NOT NULL UNIQUE
        )
        ''')
        
        # Table des entreprises
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS entreprise (
            id_entreprise SERIAL PRIMARY KEY,
            nom_entreprise TEXT NOT NULL,
            siret TEXT,
            forme_juridique TEXT,
            adresse TEXT,
            id_ville INTEGER REFERENCES villes(id_ville),
            id_cp INTEGER REFERENCES code_postal(id_cp),
            id_cedex INTEGER REFERENCES cedex(id_cedex),
            email_principal TEXT,
            email_secondaire TEXT,
            referent TEXT,
            numero_telephone TEXT,
            numero_portable TEXT,
            id_type_entreprise INTEGER REFERENCES type_entreprise(id_type_entreprise),
            prestations TEXT
        )
        ''')
        
        # Table de liaison entreprise-corps de métier
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS entreprise_corps_metier (
            id_entreprise INTEGER,
            id_corps_metier INTEGER,
            PRIMARY KEY (id_entreprise, id_corps_metier),
            FOREIGN KEY (id_entreprise) REFERENCES entreprise(id_entreprise) ON DELETE CASCADE,
            FOREIGN KEY (id_corps_metier) REFERENCES corps_metier(id_corps_metier) ON DELETE CASCADE
        )
        ''')
        
        # Table des chiffres d'affaires
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS chiffre_affaires (
            id_ca SERIAL PRIMARY KEY,
            id_entreprise INTEGER NOT NULL,
            annee INTEGER NOT NULL,
            montant REAL NOT NULL,
            date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_entreprise) REFERENCES entreprise(id_entreprise) ON DELETE CASCADE,
            UNIQUE(id_entreprise, annee)
        )
        ''')
        
        # Insertion de données de base (si non existantes)
        # Type d'entreprise par défaut
        cursor.execute('''
        INSERT INTO type_entreprise (id_type_entreprise, nom_type_entreprise)
        VALUES (1, 'Non spécifié')
        ON CONFLICT (id_type_entreprise) DO NOTHING
        ''')
        
        # Ajouter des types d'entreprise courants
        types_entreprise = [
            'Maîtrise d''ouvrage',
            'Maîtrise d''œuvre',
            'Entrepreneur',
            'Fournisseur',
            'Co-traitant',
            'Sous-traitant'
        ]
        
        for type_ent in types_entreprise:
            cursor.execute('''
            INSERT INTO type_entreprise (nom_type_entreprise) 
            VALUES (%s)
            ON CONFLICT (nom_type_entreprise) DO NOTHING
            ''', (type_ent,))
        
        # Corps de métier par défaut
        cursor.execute('''
        INSERT INTO corps_metier (id_corps_metier, nom_corps_metier)
        VALUES (1, 'Non spécifié')
        ON CONFLICT (id_corps_metier) DO NOTHING
        ''')
        
        # Ajouter des corps de métier courants
        corps_metiers = [
            'Gros œuvre',
            'Électricité',
            'Plomberie',
            'Menuiserie',
            'Peinture',
            'Architecture',
            'Ingénierie'
        ]
        
        for cm in corps_metiers:
            cursor.execute('''
            INSERT INTO corps_metier (nom_corps_metier) 
            VALUES (%s)
            ON CONFLICT (nom_corps_metier) DO NOTHING
            ''', (cm,))
        
        # Valider les modifications
        conn.commit()
        print("✅ Base de données PostgreSQL initialisée avec succès !")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erreur lors de l'initialisation de la base de données : {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    init_database()