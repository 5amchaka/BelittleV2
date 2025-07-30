#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script d'exécution de l'application
"""
from app import create_app
from config import HOST, PORT
import os
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Récupérer le mode d'exécution
ENV = os.environ.get('FLASK_ENV', 'development').lower()

if __name__ == '__main__':
    app = create_app()
    
    if ENV == 'development':
        # Mode développement
        print("Démarrage en mode développement...")
        app.run(host=HOST, port=PORT, debug=True)
    else:
        # Mode production avec Waitress
        from waitress import serve
        print(f"Démarrage en mode production sur {HOST}:{PORT}...")
        serve(app, host=HOST, port=PORT)