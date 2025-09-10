from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify, session
from models.document import get_document_templates, generate_document_data, get_all_moa, get_all_moe, get_all_cotraitants, get_detailed_enterprise_data, format_dc1_data, format_dc2_data, get_projet_document_templates, get_projet_data_for_document
from models.entreprise import get_enterprises_list, get_chiffres_affaires, add_or_update_chiffre_affaires
from models.projet import create_projet, get_all_projets, get_projet, update_projet, add_moe_cotraitant, get_moe_cotraitants, remove_moe_cotraitant, create_lot, get_lots_by_projet, add_entreprise_to_lot, get_entreprises_by_lot, create_avenant, get_montant_actuel_lot_entreprise, get_historique_montants_lot_entreprise, log_document_generation, delete_projet, update_lot_entreprise, remove_entreprise_from_lot, get_lot_entreprise, get_lot, update_lot, delete_lot, delete_latest_avenant_by_lot_entreprise
import os
import tempfile
from docxtpl import DocxTemplate
import io
import zipfile
import pandas as pd

# Création du blueprint pour les routes de gestion des documents
document = Blueprint('document', __name__)

@document.route('/')
def index():
    """Page d'accueil de gestion des documents"""
    templates = get_document_templates()
    return render_template('document/index.html', templates=templates)

@document.route('/select_enterprise/<int:document_id>', methods=['GET'])
def select_enterprise(document_id):
    """Sélection de l'entreprise pour générer un document"""
    # Récupérer toutes les entreprises pour la sélection
    enterprises = get_enterprises_list()
    templates = get_document_templates()
    selected_template = next((t for t in templates if t["id"] == document_id), None)
    
    return render_template('document/select_enterprise.html', 
                          enterprises=enterprises, 
                          document_id=document_id,
                          template=selected_template)

@document.route('/preview', methods=['POST'])
def preview_document():
    """Aperçu du document avant génération"""
    document_id = int(request.form.get('document_id'))
    enterprise_id = int(request.form.get('enterprise_id'))
    
    # Récupérer les données
    document_data = generate_document_data(enterprise_id, document_id)
    templates = get_document_templates()
    selected_template = next((t for t in templates if t["id"] == document_id), None)
    
    if not document_data:
        flash("Impossible de récupérer les données de l'entreprise.")
        return redirect(url_for('document.index'))
    
    return render_template('document/preview.html', 
                          data=document_data, 
                          document_id=document_id,
                          enterprise_id=enterprise_id,
                          template=selected_template)

@document.route('/generate', methods=['POST'])
def generate_document():
    """Génération et téléchargement du document"""
    document_id = int(request.form.get('document_id'))
    enterprise_id = int(request.form.get('enterprise_id'))
    format_type = request.form.get('format', 'docx')
    
    # Récupérer les données
    document_data = generate_document_data(enterprise_id, document_id)
    
    if not document_data:
        flash("Impossible de récupérer les données de l'entreprise.")
        return redirect(url_for('document.index'))
    
    # Quel document générer?
    templates = get_document_templates()
    selected_template = next((t for t in templates if t["id"] == document_id), None)
    
    if not selected_template:
        flash("Modèle de document non trouvé.")
        return redirect(url_for('document.index'))
    
    # Génération selon le format demandé
    if format_type == 'docx':
        # Chemin du modèle Word
        template_name = f"dc{document_id}_template.docx"
        template_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                   'templates/document_templates', 
                                   template_name)
        
        # Vérifier si le modèle existe
        if not os.path.exists(template_path):
            flash(f"Le modèle {selected_template['nom']} n'existe pas.")
            return redirect(url_for('document.index'))
        
        # Générer le document avec DocxTemplate
        doc = DocxTemplate(template_path)
        doc.render(document_data)
        
        # Sauvegarder dans un buffer
        output = io.BytesIO()
        doc.save(output)
        output.seek(0)
        
        filename = f"{selected_template['nom']}_{document_data['nom_entreprise']}.docx"
        
        # Renvoyer le fichier
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    elif format_type == 'excel':
        # Créer un DataFrame avec les données
        df = pd.DataFrame([document_data])
        
        # Sauvegarder dans un buffer
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Données', index=False)
        output.seek(0)
        
        filename = f"{selected_template['nom']}_{document_data['nom_entreprise']}.xlsx"
        
        # Renvoyer le fichier
        return send_file(
            output, 
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    else:
        flash("Format non supporté.")
        return redirect(url_for('document.index'))
    
@document.route('/dc1', methods=['GET'])
def dc1_form():
    """Formulaire spécifique pour le DC1"""
    # Récupérer les listes d'entreprises pour chaque rôle
    moa_list = get_all_moa()
    moe_list = get_all_moe()
    cotraitants_list = get_all_cotraitants()
    
    return render_template('document/dc1_form.html', 
                          moa_list=moa_list,
                          moe_list=moe_list,
                          cotraitants_list=cotraitants_list)

@document.route('/dc1/preview', methods=['POST'])
def dc1_preview():
    """Aperçu du formulaire DC1 avec possibilité d'édition"""
    # Récupérer les données du formulaire
    projet_data = {
        'nom_affaire': request.form.get('nom_affaire', ''),
        'reference_projet': request.form.get('reference_projet', ''),
        'objet_consultation': request.form.get('objet_consultation', '')
    }
    
    moa_id = request.form.get('moa_id')
    moe_id = request.form.get('moe_id')
    cotraitant_ids = request.form.getlist('cotraitant_ids')
    
    # Journal de débogage
    print(f"MOE ID dans dc1_preview: {moe_id}")
    
    # Récupérer les données détaillées des entreprises
    moa_data = get_detailed_enterprise_data(moa_id) if moa_id else {}
    moe_data = get_detailed_enterprise_data(moe_id) if moe_id else {}
    
    # Récupérer les chiffres d'affaires du mandataire (MOE)
    ca_data = get_chiffres_affaires(moe_id) if moe_id else {'annees': [], 'montants': []}
    
    # Journal de débogage
    print(f"Données CA récupérées: {ca_data}")
    
    cotraitants_data = []
    for cot_id in cotraitant_ids:
        if cot_id:
            cotraitant_data = get_detailed_enterprise_data(cot_id)
            if cotraitant_data:
                cotraitants_data.append(cotraitant_data)
    
    # Formater les données pour le DC1
    dc1_data = format_dc1_data(projet_data, moa_data, moe_data, cotraitants_data)
    
    # Si des CA sont récupérés, les trier par année décroissante
    if ca_data and ca_data['annees'] and len(ca_data['annees']) > 0:
        # Créer des paires (année, montant)
        ca_pairs = list(zip(ca_data['annees'], ca_data['montants']))
        # Trier par année décroissante
        ca_pairs.sort(key=lambda x: int(x[0]), reverse=True)
        # Reconstruire les listes triées
        ca_data['annees'], ca_data['montants'] = zip(*ca_pairs)
    
    # Rendre la page d'aperçu avec possibilité d'édition
    return render_template('document/dc1_preview.html', 
                          data=dc1_data,
                          moa_id=moa_id,
                          moe_id=moe_id,
                          cotraitant_ids=cotraitant_ids,
                          projet_data=projet_data,
                          ca_data=ca_data)

@document.route('/dc1/generate', methods=['POST'])
def dc1_generate():
    """Génération du document DC1 et DC2 final"""
    # Récupérer toutes les données du formulaire d'édition
    edited_data = {
        # Données du projet
        'nom_affaire': request.form.get('nom_affaire', ''),
        'reference_projet': request.form.get('reference_projet', ''),
        'objet_consultation': request.form.get('objet_consultation', ''),
        
        # Données de la MOA
        'nom_moa': request.form.get('nom_moa', ''),
        'adresse_moa': request.form.get('adresse_moa', ''),
        
        # Données du mandataire
        'nom_mandataire': request.form.get('nom_mandataire', ''),
        'forme_juridique_mandataire': request.form.get('forme_juridique_mandataire', ''),
        'adresse_mandataire': request.form.get('adresse_mandataire', ''),
        'email_mandataire': request.form.get('email_mandataire', ''),
        'telephone_mandataire': request.form.get('telephone_mandataire', ''),
        'portable_mandataire': request.form.get('portable_mandataire', ''),
        'siret_mandataire': request.form.get('siret_mandataire', ''),
        'prestation_mandataire': request.form.get('prestation_mandataire', 'Mandataire'),
        
        # Tableau pour les co-traitants (avec le mandataire comme premier élément)
        'cotraitants': []
    }
    
    # Identifiants pour enregistrer les données
    moe_id = request.form.get('moe_id')
    
    # Récupérer les données détaillées des entreprises pour le DC2
    moe_data = get_detailed_enterprise_data(moe_id) if moe_id else {}
    
    # Traitement des chiffres d'affaires du mandataire
    if moe_id:
        try:
            # Convertir en entier
            moe_id = int(moe_id)
            
            ca_enregistres = []
            
            for i in range(3):
                annee_key = f'ca_annee_{i}'
                montant_key = f'ca_montant_{i}'
                
                if annee_key in request.form and montant_key in request.form:
                    annee = request.form.get(annee_key)
                    montant = request.form.get(montant_key)
                    
                    print(f"Valeurs de CA trouvées: année={annee}, montant={montant}")
                    
                    if annee and montant:
                        try:
                            annee = int(annee)
                            montant = float(montant)
                            print(f"Enregistrement CA: {moe_id}, {annee}, {montant}")
                            
                            # Enregistrer le CA
                            add_or_update_chiffre_affaires(moe_id, annee, montant)
                            print(f"CA enregistré avec succès: {annee} - {montant}€")
                            ca_enregistres.append((annee, montant))
                        except (ValueError, TypeError) as e:
                            print(f"Erreur conversion CA: {e}")
                        except Exception as e:
                            print(f"Erreur inattendue: {e}")
            
            if ca_enregistres:
                flash(f"{len(ca_enregistres)} chiffres d'affaires enregistrés avec succès.")
            
        except ValueError:
            print(f"MOE ID n'est pas un entier valide: {moe_id}")
        except Exception as e:
            print(f"Erreur lors du traitement des CA: {e}")
    else:
        print("Aucun MOE ID trouvé dans le formulaire")
    
    # Récupérer le nombre de co-traitants
    cotraitant_count = int(request.form.get('cotraitant_count', 0))
    
    # Récupérer les données de chaque co-traitant
    for i in range(cotraitant_count):
        cotraitant = {
            'numero': i+1,  # Commencer à 1 (le mandataire est inclus)
            'nom': request.form.get(f'cotraitant_nom_{i}', ''),
            'adresse': request.form.get(f'cotraitant_adresse_{i}', ''),
            'email': request.form.get(f'cotraitant_email_{i}', ''),
            'telephone': request.form.get(f'cotraitant_telephone_{i}', ''),
            'portable': request.form.get(f'cotraitant_portable_{i}', ''),
            'siret': request.form.get(f'cotraitant_siret_{i}', ''),
            'prestation': request.form.get(f'cotraitant_prestation_{i}', '')
        }
        edited_data['cotraitants'].append(cotraitant)
    
    # Format de sortie
    format_type = request.form.get('format', 'docx')
    
    # Ajout des chiffres d'affaires du mandataire pour le document
    edited_data['ca_mandataire'] = []
    ca_years = []
    for i in range(3):
        annee = request.form.get(f'ca_annee_{i}')
        montant = request.form.get(f'ca_montant_{i}')
        if annee and montant:
            try:
                annee_int = int(annee)
                ca_years.append(annee_int)
                edited_data['ca_mandataire'].append({
                    'annee': annee,
                    'montant': montant
                })
            except ValueError:
                pass
    
    # Trier les CA par année décroissante
    if edited_data['ca_mandataire']:
        edited_data['ca_mandataire'] = sorted(edited_data['ca_mandataire'], 
                                            key=lambda x: int(x['annee']), 
                                            reverse=True)
    
    # Préparation des données pour le DC2
    dc2_data = format_dc2_data(edited_data, moe_data)
    
    if format_type == 'docx':
        # Créer un fichier ZIP pour stocker les deux documents
        output_zip = io.BytesIO()
        
        with zipfile.ZipFile(output_zip, 'w') as zipf:
            # Générer le document DC1
            template_path_dc1 = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                           'templates/document_templates', 'dc1_template.docx')
            
            if os.path.exists(template_path_dc1):
                doc_dc1 = DocxTemplate(template_path_dc1)
                doc_dc1.render(edited_data)
                
                temp_dc1 = io.BytesIO()
                doc_dc1.save(temp_dc1)
                temp_dc1.seek(0)
                
                zipf.writestr(f"DC1_{edited_data['nom_affaire'].replace(' ', '_')}.docx", temp_dc1.getvalue())
            else:
                flash("Le modèle DC1 n'existe pas.")
            
            print(f"Données DC2 avant génération: {dc2_data}")
            # Générer le document DC2
            template_path_dc2 = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                           'templates/document_templates', 'dc2_template.docx')
            
            if os.path.exists(template_path_dc2):
                doc_dc2 = DocxTemplate(template_path_dc2)
                doc_dc2.render(dc2_data)
                
                temp_dc2 = io.BytesIO()
                doc_dc2.save(temp_dc2)
                temp_dc2.seek(0)
                
                zipf.writestr(f"DC2_{edited_data['nom_affaire'].replace(' ', '_')}.docx", temp_dc2.getvalue())
                # Après avoir écrit le DC2 dans le zip
                if zipf.namelist() and f"DC2_{edited_data['nom_affaire'].replace(' ', '_')}.docx" in zipf.namelist():
                    print("DC2 correctement ajouté au zip")
                else:
                    print("DC2 n'a pas été ajouté au zip")
            else:
                flash("Le modèle DC2 n'existe pas.")
        
        output_zip.seek(0)
        filename = f"DC1_DC2_{edited_data['nom_affaire'].replace(' ', '_')}.zip"
        
        return send_file(
            output_zip,
            as_attachment=True,
            download_name=filename,
            mimetype='application/zip'
        )
        
    elif format_type == 'excel':
        # Pour la version Excel, nous devons aplatir la structure des données
        output_zip = io.BytesIO()
        
        with zipfile.ZipFile(output_zip, 'w') as zipf:
            # Créer le fichier Excel DC1
            flat_data_dc1 = {
                'nom_affaire': edited_data['nom_affaire'],
                'reference_projet': edited_data['reference_projet'],
                'objet_consultation': edited_data['objet_consultation'],
                'nom_moa': edited_data['nom_moa'],
                'adresse_moa': edited_data['adresse_moa'],
                'nom_mandataire': edited_data['nom_mandataire'],
                'forme_juridique_mandataire': edited_data.get('forme_juridique_mandataire', ''),
                'adresse_mandataire': edited_data['adresse_mandataire'],
                'email_mandataire': edited_data['email_mandataire'],
                'telephone_mandataire': edited_data['telephone_mandataire'],
                'portable_mandataire': edited_data['portable_mandataire'],
                'siret_mandataire': edited_data['siret_mandataire'],
            }
            
            # Ajouter les chiffres d'affaires
            for i, ca in enumerate(edited_data['ca_mandataire']):
                flat_data_dc1[f'ca_mandataire_annee_{i+1}'] = ca['annee']
                flat_data_dc1[f'ca_mandataire_montant_{i+1}'] = ca['montant']
            
            # Ajouter les données de chaque co-traitant
            for i, cotraitant in enumerate(edited_data['cotraitants']):
                flat_data_dc1[f'cotraitant_{i+1}_nom'] = cotraitant['nom']
                flat_data_dc1[f'cotraitant_{i+1}_adresse'] = cotraitant['adresse']
                flat_data_dc1[f'cotraitant_{i+1}_email'] = cotraitant['email']
                flat_data_dc1[f'cotraitant_{i+1}_telephone'] = cotraitant['telephone']
                flat_data_dc1[f'cotraitant_{i+1}_portable'] = cotraitant['portable']
                flat_data_dc1[f'cotraitant_{i+1}_siret'] = cotraitant['siret']
            
            # Créer un DataFrame pour DC1
            df_dc1 = pd.DataFrame([flat_data_dc1])
            
            # Sauvegarder dans un buffer temporaire pour DC1
            temp_dc1 = io.BytesIO()
            with pd.ExcelWriter(temp_dc1, engine='xlsxwriter') as writer:
                df_dc1.to_excel(writer, sheet_name='DC1', index=False)
            temp_dc1.seek(0)
            zipf.writestr(f"DC1_{edited_data['nom_affaire'].replace(' ', '_')}.xlsx", temp_dc1.getvalue())
            
            # Créer le fichier Excel DC2
            flat_data_dc2 = {
                'nom_affaire': edited_data['nom_affaire'],
                'reference_projet': edited_data['reference_projet'],
                'objet_consultation': edited_data['objet_consultation'],
                'nom_mandataire': edited_data['nom_mandataire'],
                'forme_juridique_mandataire': edited_data.get('forme_juridique_mandataire', ''),
                'adresse_mandataire': edited_data['adresse_mandataire'],
                'siret_mandataire': edited_data['siret_mandataire'],
            }
            
            # Ajouter les chiffres d'affaires pour DC2
            for i, ca in enumerate(dc2_data['ca_mandataire']):
                flat_data_dc2[f'ca_mandataire_annee_{i+1}'] = ca['annee']
                flat_data_dc2[f'ca_mandataire_montant_{i+1}'] = ca['montant']
            
            # Créer un DataFrame pour DC2
            df_dc2 = pd.DataFrame([flat_data_dc2])
            
            # Sauvegarder dans un buffer temporaire pour DC2
            temp_dc2 = io.BytesIO()
            with pd.ExcelWriter(temp_dc2, engine='xlsxwriter') as writer:
                df_dc2.to_excel(writer, sheet_name='DC2', index=False)
            temp_dc2.seek(0)
            zipf.writestr(f"DC2_{edited_data['nom_affaire'].replace(' ', '_')}.xlsx", temp_dc2.getvalue())
            
        output_zip.seek(0)
        filename = f"DC1_DC2_{edited_data['nom_affaire'].replace(' ', '_')}.zip"
        
        return send_file(
            output_zip,
            as_attachment=True,
            download_name=filename,
            mimetype='application/zip'
        )
    
    flash("Format non supporté.")
    return redirect(url_for('document.index'))

# Nouvelles routes pour la gestion des projets

@document.route('/projets')
def projets_list():
    """Liste tous les projets"""
    projets = get_all_projets()
    return render_template('document/projets_list.html', projets=projets)

@document.route('/projet/create', methods=['GET', 'POST'])
def create_projet_form():
    """Formulaire de création d'un nouveau projet"""
    if request.method == 'POST':
        # Récupérer les données du formulaire
        identification_operation = request.form.get('identification_operation')
        id_moa = request.form.get('id_moa')
        nom_affaire = request.form.get('nom_affaire')
        reference_projet = request.form.get('reference_projet')
        date_notification = request.form.get('date_notification')
        
        if not identification_operation or not id_moa:
            flash("L'identification de l'opération et le MOA sont obligatoires.")
            return redirect(request.url)
        
        # Créer le projet
        projet_id = create_projet(
            identification_operation=identification_operation,
            id_moa=int(id_moa),
            nom_affaire=nom_affaire,
            reference_projet=reference_projet,
            date_notification=date_notification if date_notification else None
        )
        
        if projet_id:
            flash(f"Projet créé avec succès (ID: {projet_id})")
            return redirect(url_for('document.projet_details', id_projet=projet_id))
        else:
            flash("Erreur lors de la création du projet.")
    
    # GET - Afficher le formulaire
    moa_list = get_all_moa()
    return render_template('document/create_projet.html', moa_list=moa_list)

@document.route('/projet/<int:id_projet>')
def projet_details(id_projet):
    """Détails d'un projet"""
    projet = get_projet(id_projet)
    if not projet:
        flash("Projet non trouvé.")
        return redirect(url_for('document.projets_list'))
    
    lots = get_lots_by_projet(id_projet)
    moe_cotraitants = get_moe_cotraitants(id_projet)
    
    # Récupérer les entreprises pour chaque lot et calculer le montant total
    lots_with_enterprises = []
    for lot in lots:
        lot_dict = dict(lot)
        entreprises = get_entreprises_by_lot(lot['id_lot'])
        lot_dict['entreprises'] = entreprises
        
        # Calculer le montant total du lot (somme des montants des entreprises)
        montant_total = sum(ent['montant_ht'] for ent in entreprises) if entreprises else lot['montant_initial_ht']
        lot_dict['montant_total_ht'] = montant_total
        
        lots_with_enterprises.append(lot_dict)
    
    return render_template('document/projet_details.html', 
                         projet=projet, 
                         lots=lots_with_enterprises, 
                         moe_cotraitants=moe_cotraitants)

@document.route('/projet/<int:id_projet>/edit', methods=['GET', 'POST'])
def edit_projet(id_projet):
    """Modification des données d'un projet"""
    projet = get_projet(id_projet)
    if not projet:
        flash("Projet non trouvé.")
        return redirect(url_for('document.projets_list'))
    
    if request.method == 'POST':
        # Récupérer les données du formulaire
        data = {
            'identification_operation': request.form.get('identification_operation'),
            'nom_affaire': request.form.get('nom_affaire'),
            'reference_projet': request.form.get('reference_projet'),
            'date_notification': request.form.get('date_notification') or None,
            'id_moa': int(request.form.get('id_moa')) if request.form.get('id_moa') else None,
            'id_moe': int(request.form.get('id_moe')) if request.form.get('id_moe') else None,
            'statut': request.form.get('statut')
        }
        
        # Validation
        if not data['identification_operation']:
            flash("L'identification de l'opération est obligatoire.")
            return redirect(request.url)
        
        # Mettre à jour le projet
        if update_projet(id_projet, **data):
            flash("Projet mis à jour avec succès.")
            return redirect(url_for('document.projet_details', id_projet=id_projet))
        else:
            flash("Erreur lors de la mise à jour du projet.")
    
    # GET - Afficher le formulaire
    moa_list = get_all_moa()
    moe_list = get_all_moe()
    
    return render_template('document/edit_projet.html', 
                         projet=projet, 
                         moa_list=moa_list, 
                         moe_list=moe_list)

@document.route('/projet/<int:id_projet>/moe', methods=['GET', 'POST'])
def manage_moe_cotraitants(id_projet):
    """Gestion des MOE co-traitants"""
    projet = get_projet(id_projet)
    if not projet:
        flash("Projet non trouvé.")
        return redirect(url_for('document.projets_list'))
    
    if request.method == 'POST':
        id_entreprise = request.form.get('id_entreprise')
        est_mandataire = request.form.get('est_mandataire') == 'on'
        
        if id_entreprise:
            if add_moe_cotraitant(id_projet, int(id_entreprise), est_mandataire):
                flash("MOE co-traitant ajouté avec succès.")
            else:
                flash("Erreur lors de l'ajout du MOE co-traitant.")
        
        return redirect(url_for('document.projet_details', id_projet=id_projet))
    
    # GET - Afficher le formulaire
    moe_list = get_all_moe()
    moe_cotraitants = get_moe_cotraitants(id_projet)
    
    return render_template('document/manage_moe.html', 
                         projet=projet, 
                         moe_list=moe_list, 
                         moe_cotraitants=moe_cotraitants)

@document.route('/projet/<int:id_projet>/moe/<int:id_entreprise>/remove', methods=['POST'])
def remove_moe_cotraitant_route(id_projet, id_entreprise):
    """Supprime un MOE co-traitant d'un projet"""
    projet = get_projet(id_projet)
    if not projet:
        flash("Projet non trouvé.")
        return redirect(url_for('document.projets_list'))
    
    # Récupérer le nom de l'entreprise pour le message
    from models.entreprise import get_enterprise
    try:
        entreprise = get_enterprise(id_entreprise)
        nom_entreprise = entreprise['nom_entreprise'] if entreprise else f"Entreprise {id_entreprise}"
    except:
        nom_entreprise = f"Entreprise {id_entreprise}"
    
    if remove_moe_cotraitant(id_projet, id_entreprise):
        flash(f"MOE co-traitant {nom_entreprise} supprimé avec succès.")
    else:
        flash("Erreur lors de la suppression du MOE co-traitant.")
    
    return redirect(url_for('document.manage_moe_cotraitants', id_projet=id_projet))

@document.route('/projet/<int:id_projet>/lots', methods=['GET', 'POST'])
def manage_lots(id_projet):
    """Gestion des lots d'un projet"""
    projet = get_projet(id_projet)
    if not projet:
        flash("Projet non trouvé.")
        return redirect(url_for('document.projets_list'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'create_lots':
            nombre_lots = int(request.form.get('nombre_lots', 1))
            
            # Récupérer les lots existants pour déterminer le prochain numéro
            existing_lots = get_lots_by_projet(id_projet)
            existing_count = len(existing_lots) if existing_lots else 0
            
            for i in range(1, nombre_lots + 1):
                lot_number = existing_count + i
                numero_lot = f"LOT{lot_number:02d}"
                objet_marche = f"Lot {lot_number}"
                create_lot(id_projet, numero_lot, objet_marche)
            
            flash(f"{nombre_lots} lot(s) créé(s) avec succès.")
            return redirect(url_for('document.manage_lots', id_projet=id_projet))
    
    lots = get_lots_by_projet(id_projet)
    
    # Récupérer les entreprises attribuées pour chaque lot
    lots_with_enterprises = []
    for lot in lots:
        lot_dict = dict(lot)
        lot_dict['entreprises'] = get_entreprises_by_lot(lot['id_lot'])
        lots_with_enterprises.append(lot_dict)
    
    return render_template('document/manage_lots.html', projet=projet, lots=lots_with_enterprises)

@document.route('/lot-entreprise/<int:id_lot_entreprise>/delete', methods=['POST'])
def delete_lot_entreprise(id_lot_entreprise):
    """Supprime une entreprise d'un lot"""
    lot_entreprise = get_lot_entreprise(id_lot_entreprise)
    if not lot_entreprise:
        flash("Attribution entreprise-lot non trouvée.")
        return redirect(url_for('document.projets_list'))
    
    id_projet = None
    # Récupérer l'ID du projet pour la redirection
    try:
        from database import get_db, close_db
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.id_projet 
            FROM lot_entreprises le
            JOIN lots l ON le.id_lot = l.id_lot
            JOIN projets p ON l.id_projet = p.id_projet
            WHERE le.id_lot_entreprise = ?
        """, (id_lot_entreprise,))
        result = cursor.fetchone()
        if result:
            id_projet = result['id_projet']
    finally:
        close_db(conn)
    
    if remove_entreprise_from_lot(id_lot_entreprise):
        flash(f"Entreprise {lot_entreprise['nom_entreprise']} supprimée du lot {lot_entreprise['numero_lot']}.")
    else:
        flash("Erreur lors de la suppression.")
    
    if id_projet:
        return redirect(url_for('document.manage_lots', id_projet=id_projet))
    else:
        return redirect(url_for('document.projets_list'))

@document.route('/lot-entreprise/<int:id_lot_entreprise>/edit', methods=['GET', 'POST'])
def edit_lot_entreprise(id_lot_entreprise):
    """Édite les informations d'une entreprise dans un lot"""
    lot_entreprise = get_lot_entreprise(id_lot_entreprise)
    if not lot_entreprise:
        flash("Attribution entreprise-lot non trouvée.")
        return redirect(url_for('document.projets_list'))
    
    if request.method == 'POST':
        montant_ht = float(request.form.get('montant_ht', 0))
        taux_tva = float(request.form.get('taux_tva', 20.0))
        est_mandataire = request.form.get('est_mandataire') == 'on'
        
        if update_lot_entreprise(id_lot_entreprise, montant_ht, taux_tva, est_mandataire):
            flash(f"Informations de {lot_entreprise['nom_entreprise']} mises à jour.")
        else:
            flash("Erreur lors de la mise à jour.")
        
        # Récupérer l'ID du projet pour la redirection
        id_projet = None
        try:
            from database import get_db, close_db
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.id_projet 
                FROM lot_entreprises le
                JOIN lots l ON le.id_lot = l.id_lot
                JOIN projets p ON l.id_projet = p.id_projet
                WHERE le.id_lot_entreprise = ?
            """, (id_lot_entreprise,))
            result = cursor.fetchone()
            if result:
                id_projet = result['id_projet']
        finally:
            close_db(conn)
        
        if id_projet:
            return redirect(url_for('document.manage_lots', id_projet=id_projet))
        else:
            return redirect(url_for('document.projets_list'))
    
    # GET - Afficher le formulaire d'édition
    # Récupérer l'ID du projet pour le template
    id_projet = None
    try:
        from database import get_db, close_db
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.id_projet 
            FROM lot_entreprises le
            JOIN lots l ON le.id_lot = l.id_lot
            JOIN projets p ON l.id_projet = p.id_projet
            WHERE le.id_lot_entreprise = ?
        """, (id_lot_entreprise,))
        result = cursor.fetchone()
        if result:
            id_projet = result['id_projet']
    finally:
        close_db(conn)
    
    return render_template('document/edit_lot_entreprise.html', 
                         lot_entreprise=lot_entreprise, 
                         id_projet=id_projet)

@document.route('/lot/<int:id_lot>/edit', methods=['GET', 'POST'])
def edit_lot(id_lot):
    """Édite les informations d'un lot"""
    lot = get_lot(id_lot)
    if not lot:
        flash("Lot non trouvé.")
        return redirect(url_for('document.projets_list'))
    
    if request.method == 'POST':
        numero_lot = request.form.get('numero_lot')
        objet_marche = request.form.get('objet_marche')
        montant_initial_ht = float(request.form.get('montant_initial_ht', 0))
        taux_tva = float(request.form.get('taux_tva', 20.0))
        
        if update_lot(id_lot, numero_lot, objet_marche, montant_initial_ht, taux_tva):
            flash(f"Lot {numero_lot} mis à jour avec succès.")
        else:
            flash("Erreur lors de la mise à jour du lot.")
        
        # Récupérer l'ID du projet pour la redirection
        updated_lot = get_lot(id_lot)
        if updated_lot:
            return redirect(url_for('document.manage_lots', id_projet=updated_lot['id_projet']))
        else:
            return redirect(url_for('document.projets_list'))
    
    # GET - Afficher le formulaire d'édition
    return render_template('document/edit_lot.html', lot=lot)

@document.route('/lot/<int:id_lot>/delete', methods=['POST'])
def delete_lot_route(id_lot):
    """Supprime un lot"""
    lot = get_lot(id_lot)
    if not lot:
        flash("Lot non trouvé.")
        return redirect(url_for('document.projets_list'))
    
    id_projet = lot['id_projet']
    numero_lot = lot['numero_lot']
    
    if delete_lot(id_lot):
        flash(f"Lot {numero_lot} supprimé avec succès.")
    else:
        flash("Erreur lors de la suppression du lot.")
    
    return redirect(url_for('document.manage_lots', id_projet=id_projet))

@document.route('/projet/<int:id_projet>/lots/assignment')
def lots_assignment(id_projet):
    """Interface d'attribution des entreprises aux lots"""
    projet = get_projet(id_projet)
    if not projet:
        flash("Projet non trouvé.")
        return redirect(url_for('document.projets_list'))
    
    lots = get_lots_by_projet(id_projet)
    enterprises = get_enterprises_list()
    
    # Récupérer les attributions existantes pour chaque lot
    lots_with_enterprises = []
    for lot in lots:
        lot_dict = dict(lot)
        lot_dict['entreprises'] = get_entreprises_by_lot(lot['id_lot'])
        lots_with_enterprises.append(lot_dict)
    
    return render_template('document/lots_assignment.html', 
                         projet=projet, 
                         lots=lots_with_enterprises, 
                         enterprises=enterprises)

@document.route('/projet/<int:id_projet>/lot/<int:id_lot>/add_entreprise', methods=['POST'])
def add_entreprise_to_lot_route(id_projet, id_lot):
    """Ajoute une entreprise à un lot"""
    id_entreprise = request.form.get('id_entreprise')
    est_mandataire = request.form.get('est_mandataire') == 'on'
    montant_ht = float(request.form.get('montant_ht', 0))
    taux_tva = float(request.form.get('taux_tva', 20.0))
    
    if id_entreprise:
        result = add_entreprise_to_lot(int(id_lot), int(id_entreprise), est_mandataire, montant_ht, taux_tva)
        if result:
            flash("Entreprise ajoutée au lot avec succès.")
        else:
            flash("Erreur lors de l'ajout de l'entreprise au lot.")
    
    return redirect(url_for('document.lots_assignment', id_projet=id_projet))

@document.route('/projet/<int:id_projet>/generate')
def generate_projet_documents(id_projet):
    """Interface de génération des documents de projet"""
    projet = get_projet(id_projet)
    if not projet:
        flash("Projet non trouvé.")
        return redirect(url_for('document.projets_list'))
    
    lots = get_lots_by_projet(id_projet)
    templates = get_projet_document_templates()
    
    # Récupérer toutes les entreprises par lot
    lots_with_enterprises = []
    for lot in lots:
        lot_dict = dict(lot)
        entreprises = get_entreprises_by_lot(lot['id_lot'])
        lot_dict['entreprises'] = [dict(entreprise) for entreprise in entreprises]
        lots_with_enterprises.append(lot_dict)
    
    return render_template('document/generate_projet_documents.html', 
                         projet=projet, 
                         lots=lots_with_enterprises, 
                         templates=templates)

@document.route('/projet/<int:id_projet>/prepare_documents', methods=['POST'])
def prepare_documents(id_projet):
    """Prépare la génération de plusieurs documents"""
    from models.document import analyze_missing_data
    
    document_types = request.form.getlist('document_types')
    lot_ids = request.form.getlist('lot_ids')
    
    if not document_types:
        flash('Veuillez sélectionner au moins un type de document.', 'error')
        return redirect(url_for('document.generate_projet_documents', id_projet=id_projet))
    
    if not lot_ids:
        flash('Veuillez sélectionner au moins un lot.', 'error')
        return redirect(url_for('document.generate_projet_documents', id_projet=id_projet))
    
    # Convertir les IDs en entiers
    lot_ids = [int(id) for id in lot_ids]
    
    # Analyser les données manquantes
    missing_data = analyze_missing_data(id_projet, document_types, lot_ids)
    
    # Stocker les sélections en session
    session['document_generation'] = {
        'id_projet': id_projet,
        'document_types': document_types,
        'lot_ids': lot_ids,
        'missing_data': missing_data
    }
    
    return redirect(url_for('document.complete_documents', id_projet=id_projet))

@document.route('/projet/<int:id_projet>/complete_documents', methods=['GET', 'POST'])
def complete_documents(id_projet):
    """Formulaire de completion des données manquantes"""
    if 'document_generation' not in session:
        flash('Session expirée. Veuillez recommencer.', 'error')
        return redirect(url_for('document.generate_projet_documents', id_projet=id_projet))
    
    generation_data = session['document_generation']
    
    if request.method == 'GET':
        # Afficher le formulaire de completion
        projet = get_projet(id_projet)
        if not projet:
            flash('Projet non trouvé.', 'error')
            return redirect(url_for('document.projets'))
        
        return render_template('document/complete_documents_data.html',
                             projet=projet,
                             generation_data=generation_data)
    
    # POST: traiter la soumission du formulaire et générer les documents
    return generate_multiple_documents(id_projet, generation_data, request.form)

@document.route('/projet/<int:id_projet>/generate_document', methods=['POST'])
def generate_single_projet_document(id_projet):
    """Génère un document spécifique pour un projet"""
    type_document = request.form.get('type_document')
    id_lot = request.form.get('id_lot')
    id_entreprise = request.form.get('id_entreprise')
    format_type = request.form.get('format', 'docx')
    
    # Paramètres spécifiques selon le type de document
    kwargs = {}
    if type_document == 'exe10':
        kwargs['avancement_pct'] = float(request.form.get('avancement_pct', 0))
    elif type_document == 'exe1t':
        kwargs['avenant_data'] = {
            'numero_avenant': request.form.get('numero_avenant', ''),
            'objet_avenant': request.form.get('objet_avenant', ''),
            'date_avenant': request.form.get('date_avenant', ''),
            'motif': request.form.get('motif', ''),
            'montant_precedent_ht': float(request.form.get('montant_precedent_ht', 0)),
            'montant_nouveau_ht': float(request.form.get('montant_nouveau_ht', 0)),
            'taux_tva': float(request.form.get('taux_tva', 20.0))
        }
    
    # Récupérer les données formatées
    document_data = get_projet_data_for_document(
        id_projet, 
        type_document, 
        id_lot=int(id_lot) if id_lot else None,
        id_entreprise=int(id_entreprise) if id_entreprise else None,
        **kwargs
    )
    
    if not document_data:
        flash("Impossible de récupérer les données pour le document.")
        return redirect(url_for('document.generate_projet_documents', id_projet=id_projet))
    
    if format_type == 'docx':
        # Générer le document Word
        template_name = f"{type_document}_template.docx"
        template_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                   'templates/document_templates', 
                                   template_name)
        
        if not os.path.exists(template_path):
            flash(f"Le modèle {type_document} n'existe pas.")
            return redirect(url_for('document.generate_projet_documents', id_projet=id_projet))
        
        # Générer le document avec DocxTemplate
        doc = DocxTemplate(template_path)
        doc.render(document_data)
        
        # Sauvegarder dans un buffer
        output = io.BytesIO()
        doc.save(output)
        output.seek(0)
        
        # Construire le nom du fichier
        entreprise_name = document_data.get('nom_entreprise', 'entreprise')
        lot_name = document_data.get('numero_lot', 'lot')
        filename = f"{type_document.upper()}_{entreprise_name}_{lot_name}.docx"
        
        # Enregistrer la génération dans la base
        log_document_generation(
            id_projet, 
            type_document, 
            filename,
            int(id_entreprise) if id_entreprise else None,
            int(id_lot) if id_lot else None
        )
        
        # Renvoyer le fichier
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
    
    else:
        flash("Format non supporté pour les documents de projet.")
        return redirect(url_for('document.generate_projet_documents', id_projet=id_projet))

@document.route('/projet/<int:id_projet>/avenants')
def manage_avenants(id_projet):
    """Gestion des avenants d'un projet"""
    projet = get_projet(id_projet)
    if not projet:
        flash("Projet non trouvé.")
        return redirect(url_for('document.projets_list'))
    
    lots = get_lots_by_projet(id_projet)
    
    # Récupérer les entreprises de chaque lot avec leurs montants actuels et historique
    lots_with_data = []
    for lot in lots:
        lot_dict = dict(lot)
        entreprises = get_entreprises_by_lot(lot['id_lot'])
        
        entreprises_with_montants = []
        for ent in entreprises:
            ent_dict = dict(ent)
            montant_data = get_montant_actuel_lot_entreprise(ent['id_lot_entreprise'])
            ent_dict['montant_actuel'] = montant_data
            
            # Récupérer l'historique des avenants
            historique = get_historique_montants_lot_entreprise(ent['id_lot_entreprise'])
            ent_dict['historique'] = historique
            
            entreprises_with_montants.append(ent_dict)
        
        lot_dict['entreprises'] = entreprises_with_montants
        lots_with_data.append(lot_dict)
    
    return render_template('document/manage_avenants.html', 
                         projet=projet, 
                         lots=lots_with_data)

@document.route('/projet/<int:id_projet>/create_avenant', methods=['POST'])
def create_avenant_route(id_projet):
    """Crée un nouvel avenant"""
    id_lot_entreprise = request.form.get('id_lot_entreprise')
    numero_avenant = request.form.get('numero_avenant')
    objet_avenant = request.form.get('objet_avenant')
    montant_precedent_ht = float(request.form.get('montant_precedent_ht', 0))
    montant_nouveau_ht = float(request.form.get('montant_nouveau_ht', 0))
    date_avenant = request.form.get('date_avenant')
    motif = request.form.get('motif', '')
    taux_tva = float(request.form.get('taux_tva', 20.0))
    
    if not all([id_lot_entreprise, numero_avenant, objet_avenant, date_avenant]):
        flash("Tous les champs obligatoires doivent être remplis.")
        return redirect(url_for('document.manage_avenants', id_projet=id_projet))
    
    avenant_id = create_avenant(
        int(id_lot_entreprise),
        int(numero_avenant),
        objet_avenant,
        montant_precedent_ht,
        montant_nouveau_ht,
        date_avenant,
        motif,
        taux_tva
    )
    
    if avenant_id:
        flash("Avenant créé avec succès.")
    else:
        flash("Erreur lors de la création de l'avenant.")
    
    return redirect(url_for('document.manage_avenants', id_projet=id_projet))

@document.route('/projet/<int:id_projet>/delete_latest_avenant', methods=['POST'])
def delete_latest_avenant_route(id_projet):
    """Supprime le dernier avenant d'une entreprise sur un lot"""
    id_lot_entreprise = request.form.get('id_lot_entreprise')
    
    if not id_lot_entreprise:
        flash("ID lot-entreprise manquant.")
        return redirect(url_for('document.manage_avenants', id_projet=id_projet))
    
    # Supprimer le dernier avenant
    success, message = delete_latest_avenant_by_lot_entreprise(int(id_lot_entreprise))
    
    if success:
        flash(message)
    else:
        flash(message, 'error')
    
    return redirect(url_for('document.manage_avenants', id_projet=id_projet))

@document.route('/projet/<int:id_projet>/delete', methods=['POST'])
def delete_projet_route(id_projet):
    """Supprime un projet et toutes ses données associées"""
    projet = get_projet(id_projet)
    if not projet:
        flash("Projet non trouvé.")
        return redirect(url_for('document.projets_list'))
    
    projet_nom = projet['nom_affaire'] or f'Projet {id_projet}'
    
    # Supprimer le projet (cascade supprimera automatiquement tous les éléments liés)
    if delete_projet(id_projet):
        flash(f"Le projet '{projet_nom}' a été supprimé avec succès.")
    else:
        flash("Erreur lors de la suppression du projet.")
    
    return redirect(url_for('document.projets_list'))

def generate_multiple_documents(id_projet, generation_data, form_data):
    """Génère plusieurs documents et les retourne dans un ZIP"""
    import zipfile
    import tempfile
    import os
    from io import BytesIO
    from models.document import (
        get_data_for_ordre_service, get_data_for_attri1, get_data_for_dc4,
        get_data_for_exe10, get_data_for_exe1t, get_data_for_dc1, get_data_for_dc2
    )
    
    # Dictionnaire des fonctions de génération par type de document
    generation_functions = {
        'ordre_service': get_data_for_ordre_service,
        'attri1': get_data_for_attri1,
        'dc4': get_data_for_dc4,
        'exe10': get_data_for_exe10,
        'exe1t': get_data_for_exe1t,
        'dc1': get_data_for_dc1,
        'dc2': get_data_for_dc2
    }
    
    generated_documents = []
    errors = []
    
    try:
        # Créer un dossier temporaire
        with tempfile.TemporaryDirectory() as temp_dir:
            # Pour chaque lot et entreprise, générer les documents sélectionnés
            for lot_data in generation_data['missing_data']['lots_data']:
                lot = lot_data['lot']
                
                for enterprise_data in lot_data['enterprises']:
                    entreprise = enterprise_data['entreprise']
                    
                    # Pour chaque type de document sélectionné
                    for doc_type in generation_data['document_types']:
                        try:
                            if doc_type in generation_functions:
                                # Générer les données pour le document
                                doc_data = generation_functions[doc_type](lot, entreprise, form_data)
                                
                                if doc_data:
                                    # Définir le chemin du template
                                    template_name = f"{doc_type}_template.docx"
                                    template_path = os.path.join(
                                        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                        'templates/document_templates', 
                                        template_name
                                    )
                                    
                                    # Vérifier si le template existe
                                    if os.path.exists(template_path):
                                        # Générer le document avec DocxTemplate
                                        doc = DocxTemplate(template_path)
                                        doc.render(doc_data)
                                        
                                        # Sauvegarder le document dans le dossier temporaire
                                        filename = f"{doc_type.upper()}_{lot['numero_lot']}_{entreprise['nom_entreprise'].replace(' ', '_')}.docx"
                                        filepath = os.path.join(temp_dir, filename)
                                        doc.save(filepath)
                                        
                                        generated_documents.append({
                                            'filename': filename,
                                            'filepath': filepath,
                                            'doc_type': doc_type,
                                            'lot': lot['numero_lot'],
                                            'enterprise': entreprise['nom_entreprise']
                                        })
                                        
                                        # Log de la génération
                                        log_document_generation(
                                            generation_data['id_projet'],
                                            doc_type,
                                            filename,
                                            entreprise['id_entreprise'],
                                            lot['id_lot']
                                        )
                                    else:
                                        error_msg = f"Template {template_name} non trouvé pour {doc_type}"
                                        errors.append(error_msg)
                                else:
                                    error_msg = f"Impossible de générer les données pour {doc_type}"
                                    errors.append(error_msg)
                                
                        except Exception as e:
                            error_msg = f"Erreur lors de la génération de {doc_type} pour {entreprise['nom_entreprise']} (Lot {lot['numero_lot']}): {str(e)}"
                            errors.append(error_msg)
            
            if generated_documents:
                # Créer le fichier ZIP
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for doc in generated_documents:
                        zip_file.write(doc['filepath'], doc['filename'])
                
                zip_buffer.seek(0)
                
                # Nettoyer la session
                session.pop('document_generation', None)
                
                # Afficher les erreurs s'il y en a
                if errors:
                    for error in errors:
                        flash(error, 'warning')
                
                # Retourner le fichier ZIP
                projet = get_projet(id_projet)
                projet_name = projet['nom_affaire'] if projet and projet['nom_affaire'] else f'Projet_{id_projet}'
                zip_filename = f"Documents_{projet_name}_{len(generated_documents)}_docs.zip"
                
                return send_file(
                    zip_buffer,
                    as_attachment=True,
                    download_name=zip_filename,
                    mimetype='application/zip'
                )
            else:
                flash('Aucun document n\'a pu être généré.', 'error')
                if errors:
                    for error in errors:
                        flash(error, 'error')
                
                return redirect(url_for('document.generate_projet_documents', id_projet=id_projet))
                
    except Exception as e:
        flash(f'Erreur lors de la génération des documents: {str(e)}', 'error')
        return redirect(url_for('document.generate_projet_documents', id_projet=id_projet))

