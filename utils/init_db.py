#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script d'initialisation de la base de données SQLite
"""
import sqlite3
import os
from pathlib import Path
import sys

# Ajouter le répertoire parent au chemin d'importation
parent_dir = str(Path(__file__).resolve().parent.parent)
sys.path.append(parent_dir)

from config import DATABASE

def init_database():
    """Initialise la base de données avec le schéma de base"""
    # S'assurer que le répertoire parent existe
    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
    
    print(f"Initialisation de la base de données : {DATABASE}")
    
    # Connexion à la BDD (va la créer si elle n'existe pas)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Activer les contraintes de clé étrangère
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Créer les tables principales
    try:
        # Table des villes
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS villes (
            id_ville INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_ville TEXT NOT NULL UNIQUE
        )
        ''')
        
        # Table des types d'entreprise
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS type_entreprise (
            id_type_entreprise INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_type_entreprise TEXT NOT NULL UNIQUE
        )
        ''')
        
        # Table des corps de métier
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS corps_metier (
            id_corps_metier INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_corps_metier TEXT NOT NULL UNIQUE
        )
        ''')
        
        # Table des codes postaux
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS code_postal (
            id_cp INTEGER PRIMARY KEY AUTOINCREMENT,
            code_postal TEXT NOT NULL UNIQUE
        )
        ''')
        
        # Table des cedex
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS cedex (
            id_cedex INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_cedex TEXT NOT NULL UNIQUE
        )
        ''')
        
        # Table des entreprises
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS entreprise (
            id_entreprise INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_entreprise TEXT NOT NULL,
            siret TEXT,
            forme_juridique TEXT,
            adresse TEXT,
            id_ville INTEGER,
            id_cp INTEGER,
            id_cedex INTEGER,
            email_principal TEXT,
            email_secondaire TEXT,
            referent TEXT,
            numero_telephone TEXT,
            numero_portable TEXT,
            id_type_entreprise INTEGER,
            prestations TEXT,
            FOREIGN KEY (id_ville) REFERENCES villes(id_ville),
            FOREIGN KEY (id_cp) REFERENCES code_postal(id_cp),
            FOREIGN KEY (id_cedex) REFERENCES cedex(id_cedex),
            FOREIGN KEY (id_type_entreprise) REFERENCES type_entreprise(id_type_entreprise)
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
            id_ca INTEGER PRIMARY KEY AUTOINCREMENT,
            id_entreprise INTEGER NOT NULL,
            annee INTEGER NOT NULL,
            montant REAL NOT NULL,
            date_ajout TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_entreprise) REFERENCES entreprise(id_entreprise) ON DELETE CASCADE,
            UNIQUE(id_entreprise, annee)
        )
        ''')
        
        # Insertion de données de base (si non existantes)
        # Type d'entreprise par défaut
        cursor.execute('''
        INSERT OR IGNORE INTO type_entreprise (id_type_entreprise, nom_type_entreprise)
        VALUES (1, 'Non spécifié')
        ''')
        
        # Ajouter des types d'entreprise courants
        types_entreprise = [
            'Maîtrise d\'ouvrage',
            'Maîtrise d\'œuvre',
            'Entrepreneur',
            'Fournisseur',
            'Co-traitant',
            'Sous-traitant'
        ]
        
        for type_ent in types_entreprise:
            cursor.execute('INSERT OR IGNORE INTO type_entreprise (nom_type_entreprise) VALUES (?)', (type_ent,))
        
        # Corps de métier par défaut
        cursor.execute('''
        INSERT OR IGNORE INTO corps_metier (id_corps_metier, nom_corps_metier)
        VALUES (1, 'Non spécifié')
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
            cursor.execute('INSERT OR IGNORE INTO corps_metier (nom_corps_metier) VALUES (?)', (cm,))
        
        # Valider les modifications
        conn.commit()
        print("✅ Base de données initialisée avec succès !")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erreur lors de l'initialisation de la base de données : {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    init_database()