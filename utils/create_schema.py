#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script pour créer le schéma PostgreSQL complet
"""
import os
import psycopg2

def create_schema():
    """Crée le schéma complet dans PostgreSQL"""
    # Connexion à PostgreSQL
    conn = psycopg2.connect(
        host=os.environ.get('DB_HOST', 'postgres'),
        port=os.environ.get('DB_PORT', '5432'),
        dbname=os.environ.get('DB_NAME', 'entreprise'),
        user=os.environ.get('DB_USER', 'postgres'),
        password=os.environ.get('DB_PASSWORD', 'postgres')
    )
    conn.autocommit = True
    cursor = conn.cursor()

    # Création des tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS corps_metier (
        id_corps_metier SERIAL PRIMARY KEY,
        nom_corps_metier TEXT UNIQUE NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS type_entreprise (
        id_type_entreprise SERIAL PRIMARY KEY,
        nom_type_entreprise TEXT UNIQUE NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS villes (
        id_ville SERIAL PRIMARY KEY,
        nom_ville TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS code_postal (
        id_cp SERIAL PRIMARY KEY,
        code_postal TEXT NOT NULL UNIQUE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ville_code_postal (
        id_ville INTEGER NOT NULL,
        id_cp INTEGER NOT NULL,
        PRIMARY KEY (id_ville, id_cp),
        FOREIGN KEY (id_ville) REFERENCES villes(id_ville) ON DELETE CASCADE,
        FOREIGN KEY (id_cp) REFERENCES code_postal(id_cp) ON DELETE CASCADE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cedex (
        id_cedex SERIAL PRIMARY KEY,
        nom_cedex TEXT NOT NULL,
        id_cp INTEGER NOT NULL,
        FOREIGN KEY (id_cp) REFERENCES code_postal(id_cp) ON DELETE CASCADE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS entreprise (
        id_entreprise SERIAL PRIMARY KEY,
        nom_entreprise TEXT NOT NULL,
        siret TEXT NOT NULL UNIQUE,
        adresse TEXT NOT NULL,
        id_ville INTEGER NOT NULL,
        id_cp INTEGER,
        id_cedex INTEGER,
        email_principal TEXT UNIQUE,
        email_secondaire TEXT,
        referent TEXT,
        numero_telephone TEXT,
        numero_portable TEXT,
        id_type_entreprise INTEGER NOT NULL,
        prestations TEXT,
        forme_juridique VARCHAR(50),
        FOREIGN KEY (id_ville) REFERENCES villes(id_ville) ON DELETE CASCADE,
        FOREIGN KEY (id_cp) REFERENCES code_postal(id_cp) ON DELETE CASCADE,
        FOREIGN KEY (id_cedex) REFERENCES cedex(id_cedex) ON DELETE CASCADE,
        FOREIGN KEY (id_type_entreprise) REFERENCES type_entreprise(id_type_entreprise) ON DELETE CASCADE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS entreprise_corps_metier (
        id_entreprise INTEGER NOT NULL,
        id_corps_metier INTEGER NOT NULL,
        PRIMARY KEY (id_entreprise, id_corps_metier),
        FOREIGN KEY (id_entreprise) REFERENCES entreprise(id_entreprise) ON DELETE CASCADE,
        FOREIGN KEY (id_corps_metier) REFERENCES corps_metier(id_corps_metier) ON DELETE CASCADE
    )
    ''')

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

    cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_ca_entreprise ON chiffre_affaires(id_entreprise)
    ''')

    cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_ca_annee ON chiffre_affaires(annee)
    ''')

    cursor.close()
    conn.close()
    print('Schéma PostgreSQL créé avec succès!')

if __name__ == "__main__":
    create_schema()#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script pour créer le schéma PostgreSQL complet
"""
import os
import psycopg2

def create_schema():
    """Crée le schéma complet dans PostgreSQL"""
    # Connexion à PostgreSQL
    conn = psycopg2.connect(
        host=os.environ.get('DB_HOST', 'postgres'),
        port=os.environ.get('DB_PORT', '5432'),
        dbname=os.environ.get('DB_NAME', 'entreprise'),
        user=os.environ.get('DB_USER', 'postgres'),
        password=os.environ.get('DB_PASSWORD', 'postgres')
    )
    conn.autocommit = True
    cursor = conn.cursor()

    # Création des tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS corps_metier (
        id_corps_metier SERIAL PRIMARY KEY,
        nom_corps_metier TEXT UNIQUE NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS type_entreprise (
        id_type_entreprise SERIAL PRIMARY KEY,
        nom_type_entreprise TEXT UNIQUE NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS villes (
        id_ville SERIAL PRIMARY KEY,
        nom_ville TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS code_postal (
        id_cp SERIAL PRIMARY KEY,
        code_postal TEXT NOT NULL UNIQUE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ville_code_postal (
        id_ville INTEGER NOT NULL,
        id_cp INTEGER NOT NULL,
        PRIMARY KEY (id_ville, id_cp),
        FOREIGN KEY (id_ville) REFERENCES villes(id_ville) ON DELETE CASCADE,
        FOREIGN KEY (id_cp) REFERENCES code_postal(id_cp) ON DELETE CASCADE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cedex (
        id_cedex SERIAL PRIMARY KEY,
        nom_cedex TEXT NOT NULL,
        id_cp INTEGER NOT NULL,
        FOREIGN KEY (id_cp) REFERENCES code_postal(id_cp) ON DELETE CASCADE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS entreprise (
        id_entreprise SERIAL PRIMARY KEY,
        nom_entreprise TEXT NOT NULL,
        siret TEXT NOT NULL UNIQUE,
        adresse TEXT NOT NULL,
        id_ville INTEGER NOT NULL,
        id_cp INTEGER,
        id_cedex INTEGER,
        email_principal TEXT UNIQUE,
        email_secondaire TEXT,
        referent TEXT,
        numero_telephone TEXT,
        numero_portable TEXT,
        id_type_entreprise INTEGER NOT NULL,
        prestations TEXT,
        forme_juridique VARCHAR(50),
        FOREIGN KEY (id_ville) REFERENCES villes(id_ville) ON DELETE CASCADE,
        FOREIGN KEY (id_cp) REFERENCES code_postal(id_cp) ON DELETE CASCADE,
        FOREIGN KEY (id_cedex) REFERENCES cedex(id_cedex) ON DELETE CASCADE,
        FOREIGN KEY (id_type_entreprise) REFERENCES type_entreprise(id_type_entreprise) ON DELETE CASCADE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS entreprise_corps_metier (
        id_entreprise INTEGER NOT NULL,
        id_corps_metier INTEGER NOT NULL,
        PRIMARY KEY (id_entreprise, id_corps_metier),
        FOREIGN KEY (id_entreprise) REFERENCES entreprise(id_entreprise) ON DELETE CASCADE,
        FOREIGN KEY (id_corps_metier) REFERENCES corps_metier(id_corps_metier) ON DELETE CASCADE
    )
    ''')

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

    cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_ca_entreprise ON chiffre_affaires(id_entreprise)
    ''')

    cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_ca_annee ON chiffre_affaires(annee)
    ''')

    cursor.close()
    conn.close()
    print('Schéma PostgreSQL créé avec succès!')

if __name__ == "__main__":
    create_schema()
