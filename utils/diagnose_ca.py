#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de diagnostic de la table chiffre_affaires
"""
import sqlite3
import datetime
import sys
from pathlib import Path

# Ajouter le répertoire parent au chemin d'importation
parent_dir = str(Path(__file__).resolve().parent.parent)
sys.path.append(parent_dir)

from config import DATABASE

def diagnose_chiffre_affaires_table():
    """Diagnostique la table chiffre_affaires et teste son fonctionnement"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print(f"📊 Diagnostic de la table chiffre_affaires dans {DATABASE}")
    print("-" * 60)
    
    try:
        # 1. Vérifier si la table existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chiffre_affaires'")
        if not cursor.fetchone():
            print("❌ La table chiffre_affaires n'existe pas!")
            return
        
        print("✅ La table chiffre_affaires existe")
        
        # 2. Examiner la structure de la table
        cursor.execute("PRAGMA table_info(chiffre_affaires)")
        columns = cursor.fetchall()
        print("\n📋 Structure de la table:")
        for col in columns:
            print(f"  - {col['name']} ({col['type']})")
        
        # 3. Vérifier les index
        cursor.execute("PRAGMA index_list(chiffre_affaires)")
        indexes = cursor.fetchall()
        print("\n🔍 Index de la table:")
        for idx in indexes:
            print(f"  - {idx['name']}")
            cursor.execute(f"PRAGMA index_info({idx['name']})")
            index_columns = cursor.fetchall()
            for col in index_columns:
                print(f"    - Colonne: {col['name'] if 'name' in col else col}")
        
        # 4. Afficher quelques données existantes
        cursor.execute("SELECT * FROM chiffre_affaires LIMIT 5")
        rows = cursor.fetchall()
        print("\n📝 Exemples de données existantes:")
        if not rows:
            print("  (Aucune donnée)")
        else:
            for row in rows:
                print(f"  - Entreprise {row['id_entreprise']}, {row['annee']}: {row['montant']}€")
        
        # 5. Tester l'insertion et la mise à jour
        # Utiliser un ID d'entreprise fictif pour le test
        test_enterprise_id = 9999
        test_year = datetime.datetime.now().year
        test_amount = 123456.78
        
        print(f"\n🧪 Test d'insertion pour entreprise ID {test_enterprise_id}, année {test_year}:")
        try:
            # D'abord, supprimer tout enregistrement de test existant
            cursor.execute("DELETE FROM chiffre_affaires WHERE id_entreprise = ? AND annee = ?", 
                         (test_enterprise_id, test_year))
            
            # Ensuite, insérer un nouvel enregistrement
            cursor.execute("""
                INSERT INTO chiffre_affaires (id_entreprise, annee, montant, date_ajout)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (test_enterprise_id, test_year, test_amount))
            
            print(f"✅ Insertion réussie")
            
            # Vérifier que l'insertion a fonctionné
            cursor.execute("SELECT * FROM chiffre_affaires WHERE id_entreprise = ? AND annee = ?",
                         (test_enterprise_id, test_year))
            test_row = cursor.fetchone()
            if test_row:
                print(f"  - Données insérées: Entreprise {test_row['id_entreprise']}, {test_row['annee']}: {test_row['montant']}€ (ajouté le {test_row['date_ajout']})")
            else:
                print("❌ Échec de la vérification des données insérées")
            
            # Mettre à jour les données de test
            updated_amount = test_amount + 10000
            cursor.execute("""
                UPDATE chiffre_affaires 
                SET montant = ? 
                WHERE id_entreprise = ? AND annee = ?
            """, (updated_amount, test_enterprise_id, test_year))
            
            print(f"✅ Mise à jour réussie")
            
            # Vérifier que la mise à jour a fonctionné
            cursor.execute("SELECT * FROM chiffre_affaires WHERE id_entreprise = ? AND annee = ?",
                         (test_enterprise_id, test_year))
            test_row = cursor.fetchone()
            if test_row:
                print(f"  - Données mises à jour: Entreprise {test_row['id_entreprise']}, {test_row['annee']}: {test_row['montant']}€ (ajouté le {test_row['date_ajout']})")
            else:
                print("❌ Échec de la vérification des données mises à jour")
                
            # Nettoyer après le test
            cursor.execute("DELETE FROM chiffre_affaires WHERE id_entreprise = ? AND annee = ?", 
                         (test_enterprise_id, test_year))
            print("✓ Nettoyage des données de test effectué")
            
        except Exception as e:
            print(f"❌ Erreur lors du test: {e}")
        
        print("\n🔒 Vérification des contraintes de colonne:")
        try:
            # Tester si date_ajout accepte NULL
            cursor.execute("""
                INSERT INTO chiffre_affaires (id_entreprise, annee, montant, date_ajout)
                VALUES (?, ?, ?, NULL)
            """, (test_enterprise_id, test_year + 1, test_amount))
            print("  - date_ajout peut être NULL")
            # Nettoyer
            cursor.execute("DELETE FROM chiffre_affaires WHERE id_entreprise = ? AND annee = ?", 
                         (test_enterprise_id, test_year + 1))
        except Exception as e:
            print(f"  - date_ajout ne peut pas être NULL: {e}")
        
        conn.commit()
        
    except Exception as e:
        print(f"\n❌ Erreur durant le diagnostic: {e}")
        conn.rollback()
    finally:
        conn.close()
        
    print("\n✨ Diagnostic terminé.")

if __name__ == "__main__":
    diagnose_chiffre_affaires_table()