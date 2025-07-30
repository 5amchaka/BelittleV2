from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_db, close_db
from models.entreprise import (get_enterprise, get_enterprise_corps_metiers, 
                              get_corps_metiers, get_types_entreprise, get_villes, 
                              get_prestations, get_or_create_ville, get_or_create_type,
                              get_or_create_cp,  # Ajoutez cette ligne
                              add_enterprise as model_add_enterprise, 
                              update_enterprise as model_update_enterprise,
                              delete_enterprise as model_delete_enterprise)
import sqlite3

# Création du blueprint pour les routes de gestion des entreprises
entreprise = Blueprint('entreprise', __name__)

@entreprise.route('/add', methods=['GET', 'POST'])
def add_enterprise():
    """Route pour ajouter une entreprise"""
    if request.method == 'POST':
        nom_entreprise   = request.form.get('nom_entreprise') or "Non spécifié"
        siret            = request.form.get('siret') or "Non spécifié"
        forme_juridique  = request.form.get('forme_juridique', '').strip() or None
        adresse          = request.form.get('adresse') or "Non spécifié"
        ville_input      = request.form.get('ville').strip() or "Non spécifié"
        id_ville         = get_or_create_ville(ville_input) if ville_input else None
        code_postal      = request.form.get('id_cp').strip() or None
        id_cp            = get_or_create_cp(code_postal) if code_postal else None
        id_cedex = request.form.get('id_cedex') or None
        # Par ce code qui vérifie explicitement pour "None" et valeurs vides
        id_cedex_raw = request.form.get('id_cedex', '')
        if not id_cedex_raw or id_cedex_raw.strip() == '' or id_cedex_raw.lower() == 'none':
            id_cedex = None
        else:
            id_cedex = id_cedex_raw
        email_principal  = request.form.get('email_principal').strip() or None
        email_secondaire = request.form.get('email_secondaire').strip() or None
        referent         = request.form.get('referent') or "Non spécifié"
        numero_telephone = request.form.get('numero_telephone') or "Non spécifié"
        numero_portable  = request.form.get('numero_portable') or "Non spécifié"
        new_type         = request.form.get('new_type')
        
        if new_type and new_type.strip() != "":
            id_type_entreprise = get_or_create_type(new_type.strip())
        else:
            id_type_entreprise = request.form.get('id_type_entreprise') or "1"
            
        prestations      = request.form.get('prestations').strip() or None
        selected_cm      = request.form.getlist('corps_metier') or []
        
        # Vérifier si l'email existe déjà
        if email_principal:
            # Vérification à implémenter dans models si nécessaire
            pass
        
        # Préparer les données pour l'ajout
        enterprise_data = {
            'nom_entreprise': nom_entreprise,
            'siret': siret,
            'forme_juridique': forme_juridique,
            'adresse': adresse,
            'id_ville': id_ville,
            'id_cp': id_cp,
            'id_cedex': id_cedex,
            'email_principal': email_principal,
            'email_secondaire': email_secondaire,
            'referent': referent,
            'numero_telephone': numero_telephone,
            'numero_portable': numero_portable,
            'id_type_entreprise': id_type_entreprise,
            'prestations': prestations
        }
        
        try:
            model_add_enterprise(enterprise_data, selected_cm)
            flash('Entreprise ajoutée avec succès!')
        except sqlite3.IntegrityError as e:
            flash("Erreur lors de l'ajout de l'entreprise: " + str(e))
            
        return redirect(url_for('main.index'))
        
    # Récupérer les données pour les formulaires
    villes = get_villes()
    types = get_types_entreprise()
    corps_metiers = get_corps_metiers()
    prestations_list = get_prestations()
    
    return render_template('add_enterprise.html', 
                          villes=villes, 
                          types=types, 
                          corps_metiers=corps_metiers, 
                          prestations_list=prestations_list)

@entreprise.route('/edit/<int:enterprise_id>', methods=['GET', 'POST'])
def edit_enterprise(enterprise_id):
    """Route pour modifier une entreprise"""
    if request.method == 'POST':
        nom_entreprise   = request.form.get('nom_entreprise') or "Non spécifié"
        siret            = request.form.get('siret') or "Non spécifié"
        forme_juridique  = request.form.get('forme_juridique', '').strip() or None
        adresse          = request.form.get('adresse') or "Non spécifié"

        ville_input = request.form.get('ville').strip() or "Non spécifié"
        id_ville = get_or_create_ville(ville_input) if ville_input else None

        # Récupérer le code postal saisi et trouver l'ID correspondant
        code_postal = request.form.get('id_cp').strip()
        id_cp = get_or_create_cp(code_postal) or "00000"
        
        id_cedex = request.form.get('id_cedex') or None
        # Par ce code qui vérifie explicitement pour "None" et valeurs vides
        id_cedex_raw = request.form.get('id_cedex', '')
        if not id_cedex_raw or id_cedex_raw.strip() == '' or id_cedex_raw.lower() == 'none':
            id_cedex = None
        else:
            id_cedex = id_cedex_raw
        email_principal  = request.form.get('email_principal').strip() or None
        email_secondaire = request.form.get('email_secondaire').strip() or None
        referent         = request.form.get('referent') or "Non spécifié"
        numero_telephone = request.form.get('numero_telephone') or "Non spécifié"
        numero_portable  = request.form.get('numero_portable') or "Non spécifié"
        id_type_entreprise = request.form.get('id_type_entreprise') or "1"
            
        prestations      = request.form.get('prestations').strip() or None
        selected_cm      = request.form.getlist('corps_metier') or []
        
        # Préparer les données pour la mise à jour
        enterprise_data = {
            'nom_entreprise': nom_entreprise,
            'siret': siret,
            'forme_juridique': forme_juridique,
            'adresse': adresse,
            'id_ville': id_ville,
            'id_cp': id_cp,
            'id_cedex': id_cedex,
            'email_principal': email_principal,
            'email_secondaire': email_secondaire,
            'referent': referent,
            'numero_telephone': numero_telephone,
            'numero_portable': numero_portable,
            'id_type_entreprise': id_type_entreprise,
            'prestations': prestations
        }
        
        try:
            model_update_enterprise(enterprise_id, enterprise_data, selected_cm)
            flash('Entreprise mise à jour avec succès!')
        except Exception as e:
            flash("Erreur lors de la mise à jour de l'entreprise: " + str(e))
            
        return redirect(url_for('main.index'))
    
    # Récupérer les données pour les formulaires
    enterprise = get_enterprise(enterprise_id)
    
    if not enterprise:
        flash("Entreprise non trouvée!")
        return redirect(url_for('main.index'))
    
    # Récupérer le nom de la ville associée à l'entreprise
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT nom_ville FROM villes WHERE id_ville = ?", (enterprise['id_ville'],))
        ville_row = cursor.fetchone()
        if ville_row:
            ville_nom = ville_row['nom_ville']
        else:
            ville_nom = ""
            
        # Récupérer le code postal réel
        cursor.execute("SELECT code_postal FROM code_postal WHERE id_cp = ?", (enterprise['id_cp'],))
        cp_row = cursor.fetchone()
        if cp_row:
            code_postal = cp_row['code_postal']
        else:
            code_postal = ""
    finally:
        close_db(conn)
        
    current_cm = get_enterprise_corps_metiers(enterprise_id)
    villes = get_villes()
    types = get_types_entreprise()
    corps_metiers = get_corps_metiers()
    prestations_list = get_prestations()
    
    return render_template('edit_enterprise.html', 
                          enterprise=enterprise, 
                          villes=villes, 
                          types=types, 
                          corps_metiers=corps_metiers, 
                          prestations_list=prestations_list, 
                          current_cm=current_cm,
                          ville_nom=ville_nom,
                          code_postal=code_postal)

@entreprise.route('/delete', methods=['POST'])
def delete_enterprise():
    """Route pour supprimer une entreprise"""
    enterprise_id = request.form.get('enterprise_id')
    
    # Récupérer les filtres actuels pour rediriger vers la même page de résultats après suppression
    corps_metier_id = request.form.get('corps_metier', '')
    type_entreprise_id = request.form.get('type_entreprise', '')
    
    if not enterprise_id:
        flash("ID d'entreprise manquant!")
        return redirect(url_for('main.index'))
    
    try:
        model_delete_enterprise(enterprise_id)
        flash("Entreprise supprimée avec succès!")
    except Exception as e:
        flash(f"Erreur lors de la suppression de l'entreprise: {str(e)}")
    
    # Rediriger vers la page de résultats avec les mêmes filtres
    return redirect(url_for('main.search_results', 
                           corps_metier=corps_metier_id, 
                           type_entreprise=type_entreprise_id))
# Ajoutez ces fonctions dans models/entreprise.py
