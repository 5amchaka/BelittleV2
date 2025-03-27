from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify
from models.document import get_document_templates, generate_document_data, get_all_moa, get_all_moe, get_all_cotraitants, get_detailed_enterprise_data, format_dc1_data, format_dc2_data
from models.entreprise import get_enterprises_list, get_chiffres_affaires, add_or_update_chiffre_affaires
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
        template_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                   'templates/document_templates', 
                                   f"template_doc{document_id}.docx")
        
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
            
            # Générer le document DC2
            template_path_dc2 = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                           'templates/document_templates', 'DC2_template.docx')
            
            if os.path.exists(template_path_dc2):
                doc_dc2 = DocxTemplate(template_path_dc2)
                doc_dc2.render(dc2_data)
                
                temp_dc2 = io.BytesIO()
                doc_dc2.save(temp_dc2)
                temp_dc2.seek(0)
                
                zipf.writestr(f"DC2_{edited_data['nom_affaire'].replace(' ', '_')}.docx", temp_dc2.getvalue())
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