from flask import Blueprint, render_template, request, flash
from models.entreprise import get_corps_metiers, get_types_entreprise, search_enterprises as model_search, search_by_text as model_search_by_text, get_filter_names

# Création du blueprint pour les routes principales
main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Page d'accueil : sommaire avec options de recherche"""
    corps_metiers = get_corps_metiers()
    types_entreprise = get_types_entreprise()
    return render_template('index.html', 
                          corps_metiers=corps_metiers, 
                          types_entreprise=types_entreprise)

@main.route('/search')
def search_results():
    """Recherche d'entreprises selon les critères"""
    # Récupérer les paramètres de recherche
    corps_metier_id = request.args.get('corps_metier', '')
    type_entreprise_id = request.args.get('type_entreprise', '')
    direct_search = request.args.get('direct_search', '')
    
    # Rechercher les entreprises selon la méthode choisie
    if direct_search:
        enterprises = model_search_by_text(direct_search)
    else:
        enterprises = model_search(corps_metier_id, type_entreprise_id)
    
    # Récupérer les noms des filtres
    corps_metier_name, type_entreprise_name = get_filter_names(corps_metier_id, type_entreprise_id)
    
    # Récupérer tous les corps de métier et types d'entreprise pour le formulaire de filtre
    corps_metiers = get_corps_metiers()
    types_entreprise = get_types_entreprise()
    
    return render_template('search_results.html', 
                          enterprises=enterprises,
                          corps_metier_name=corps_metier_name, 
                          type_entreprise_name=type_entreprise_name,
                          corps_metiers=corps_metiers,
                          types_entreprise=types_entreprise,
                          corps_metier_id=corps_metier_id,
                          type_entreprise_id=type_entreprise_id)