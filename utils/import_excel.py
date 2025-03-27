#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script d'importation d'un fichier Excel dans la base de données
"""
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import text
import os
import sys
from pathlib import Path
import argparse

# Ajouter le répertoire parent au chemin d'importation
parent_dir = str(Path(__file__).resolve().parent.parent)
sys.path.append(parent_dir)

from config import DATABASE, DATA_DIR

def import_excel(excel_file):
    """
    Importe les données d'un fichier Excel dans la base de données
    
    Args:
        excel_file (str): Chemin du fichier Excel à importer
    """
    # Vérifier si le fichier existe
    if not os.path.exists(excel_file):
        print(f"❌ Le fichier {excel_file} n'existe pas.")
        return
    
    # S'assurer que le répertoire de données existe
    os.makedirs(DATA_DIR, exist_ok=True)
    
    print(f"📊 Importation du fichier : {excel_file}")
    
    # Configurer la connexion à SQLite
    sqlite_uri = f"sqlite:///{DATABASE}"
    engine = create_engine(sqlite_uri)
    
    try:
        # Lire le fichier Excel avec pandas
        df = pd.read_excel(excel_file)
        print(f"✓ Fichier chargé avec {len(df)} lignes.")
        
        # Afficher les colonnes pour information
        print(f"📋 Colonnes trouvées : {', '.join(df.columns)}")
        
        # Insérer les données dans une table temporaire "donnees"
        df.to_sql("donnees", con=engine, if_exists="replace", index=False)
        print("✓ Données importées dans la table temporaire 'donnees'.")
        
        # Afficher un échantillon pour vérification
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM donnees LIMIT 5"))
            print("\n📝 Échantillon de données importées :")
            for i, row in enumerate(result):
                print(f"  Ligne {i+1}: {row}")
        
        print(f"\n✅ Importation terminée avec succès dans {DATABASE} !")
        print("⚠️ Note: Les données sont dans la table 'donnees'. Vous devrez maintenant les migrer vers les tables appropriées.")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'importation : {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Importe un fichier Excel dans la base de données")
    parser.add_argument("fichier", help="Chemin du fichier Excel à importer")
    args = parser.parse_args()
    
    import_excel(args.fichier)