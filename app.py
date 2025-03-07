from flask import Flask
from config import SECRET_KEY, HOST, PORT
from routes.main import main
from routes.entreprise import entreprise
import os
from routes.document import document  # Nouvelle importation

def create_app():
    """Initialise et configure l'application Flask"""
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))
    app.secret_key = SECRET_KEY
    
    # Enregistrement des blueprints
    app.register_blueprint(main)
    app.register_blueprint(entreprise, url_prefix='/entreprise')
    app.register_blueprint(document, url_prefix='/document')  # Nouveau blueprint
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    # En mode développement
    # app.run(debug=True)
    
    # En mode production avec waitress
    from waitress import serve
    serve(app, host=HOST, port=PORT)