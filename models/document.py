from database import get_db, close_db
from models.entreprise import get_chiffres_affaires
from models.projet import get_projet, get_lots_by_projet, get_entreprises_by_lot, get_montant_actuel_lot_entreprise, get_historique_montants_lot_entreprise

def get_document_templates():
    """Récupère la liste des modèles de documents disponibles"""
    return [
        {"id": 1, "nom": "Formulaire DC1", "description": "Lettre de candidature avec désignation du mandataire par ses co-traitants"},
        {"id": 2, "nom": "Formulaire DC2", "description": "Déclaration du candidat"},
        {"id": 3, "nom": "Formulaire ATTRI1", "description": "Acte d'engagement"},
        {"id": 4, "nom": "Ordre de Service", "description": "Ordre de service pour démarrage des travaux"},
        {"id": 5, "nom": "Formulaire DC4", "description": "Déclaration de sous-traitance"},
        {"id": 6, "nom": "Formulaire EXE10", "description": "État d'avancement des travaux"},
        {"id": 7, "nom": "Formulaire EXE1T", "description": "Avenant au marché"}
    ]

def get_projet_document_templates():
    """Récupère la liste des modèles de documents disponibles pour les projets"""
    return [
        {"type": "ordre_service", "nom": "Ordre de Service", "description": "Ordre de service par entreprise"},
        {"type": "attri1", "nom": "ATTRI-1", "description": "Acte d'engagement par entreprise"},
        {"type": "dc4", "nom": "DC-4", "description": "Déclaration de sous-traitance"},
        {"type": "exe10", "nom": "EXE-10", "description": "État d'avancement"},
        {"type": "exe1t", "nom": "EXE-1T", "description": "Avenant au marché"},
        {"type": "dc1", "nom": "DC-1", "description": "Lettre de candidature (version projet)"},
        {"type": "dc2", "nom": "DC-2", "description": "Déclaration du candidat (version projet)"}
    ]
def get_enterprise_data_for_document(enterprise_id):
    """Récupère toutes les données nécessaires pour remplir un document"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Requête principale pour obtenir les informations de l'entreprise
        cursor.execute("""
            SELECT 
                e.*, 
                v.nom_ville, 
                cp.code_postal,
                c.nom_cedex,
                t.nom_type_entreprise
            FROM entreprise e
            LEFT JOIN villes v ON e.id_ville = v.id_ville
            LEFT JOIN code_postal cp ON e.id_cp = cp.id_cp
            LEFT JOIN cedex c ON e.id_cedex = c.id_cedex
            LEFT JOIN type_entreprise t ON e.id_type_entreprise = t.id_type_entreprise
            WHERE e.id_entreprise = ?
        """, (enterprise_id,))
        
        enterprise_data = cursor.fetchone()
        
        if not enterprise_data:
            return None
            
        # Récupérer les corps de métier associés
        cursor.execute("""
            SELECT cm.nom_corps_metier
            FROM corps_metier cm
            JOIN entreprise_corps_metier ecm ON cm.id_corps_metier = ecm.id_corps_metier
            WHERE ecm.id_entreprise = ?
        """, (enterprise_id,))
        
        corps_metiers = [row["nom_corps_metier"] for row in cursor.fetchall()]
        
        # Ajouter les corps de métier au dictionnaire
        enterprise_data = dict(enterprise_data)
        enterprise_data["corps_metiers"] = corps_metiers
        
        return enterprise_data
    finally:
        close_db(conn)

def generate_document_data(enterprise_id, document_id):
    """Prépare les données pour un document spécifique"""
    enterprise_data = get_enterprise_data_for_document(enterprise_id)
    
    if not enterprise_data:
        return None
    
    # Selon le type de document, on peut faire des traitements spécifiques
    if document_id == 1:  # DC1
        # Traiter spécifiquement pour DC1
        return {
            "nom_entreprise": enterprise_data["nom_entreprise"],
            "siret": enterprise_data["siret"],
            "adresse_complete": f"{enterprise_data['adresse']}, {enterprise_data['code_postal']} {enterprise_data['nom_ville']}",
            "email": enterprise_data["email_principal"],
            "telephone": enterprise_data["numero_telephone"],
            "portable": enterprise_data["numero_portable"],
            "referent": enterprise_data["referent"],
            "type": enterprise_data["nom_type_entreprise"],
            "prestations": enterprise_data["prestations"],
            "corps_metiers": ", ".join(enterprise_data["corps_metiers"]),
            "forme_juridique": enterprise_data.get("forme_juridique", "")
        }
    
    elif document_id == 2:  # DC2
        # Traiter spécifiquement pour DC2
        # Récupérer les chiffres d'affaires
        ca_data = get_chiffres_affaires(enterprise_id)
        ca_mandataire = []
        
        if ca_data and ca_data['annees'] and len(ca_data['annees']) > 0:
            # Créer des paires (année, montant) et trier par année décroissante
            ca_pairs = list(zip(ca_data['annees'], ca_data['montants']))
            ca_pairs.sort(key=lambda x: int(x[0]), reverse=True)
            
            for annee, montant in ca_pairs:
                ca_mandataire.append({
                    'annee': str(annee),
                    'montant': str(montant)
                })
        
        return {
            "nom_entreprise": enterprise_data["nom_entreprise"],
            "siret": enterprise_data["siret"],
            "forme_juridique": enterprise_data.get("forme_juridique", ""),
            "adresse_complete": f"{enterprise_data['adresse']}, {enterprise_data['code_postal']} {enterprise_data['nom_ville']}",
            "email": enterprise_data["email_principal"],
            "telephone": enterprise_data["numero_telephone"],
            "portable": enterprise_data["numero_portable"],
            "referent": enterprise_data["referent"],
            "type": enterprise_data["nom_type_entreprise"],
            "prestations": enterprise_data["prestations"],
            "corps_metiers": ", ".join(enterprise_data["corps_metiers"]),
            "ca_mandataire": ca_mandataire
        }
    
    # Par défaut, retourner toutes les données
    return enterprise_data
def get_all_moa():
    """Récupère la liste des maîtres d'ouvrage (MOA)"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id_entreprise, nom_entreprise 
            FROM entreprise 
            JOIN type_entreprise ON entreprise.id_type_entreprise = type_entreprise.id_type_entreprise
            WHERE type_entreprise.nom_type_entreprise LIKE '%Maîtrise d%ouvrage%'
            OR type_entreprise.nom_type_entreprise LIKE '%Maitrise d%ouvrage%'
            ORDER BY nom_entreprise
        """)
        return cursor.fetchall()
    finally:
        close_db(conn)
        

def get_all_moe():
    """Récupère la liste des maîtres d'œuvre (MOE) et mandataires potentiels"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Version simplifiée qui retourne toutes les entreprises qui ne sont pas de type MOA
        # Vous pouvez ajuster cette requête selon votre classification
        cursor.execute("""
            SELECT id_entreprise, nom_entreprise, siret
            FROM entreprise 
            WHERE id_type_entreprise IN (
                SELECT id_type_entreprise FROM type_entreprise 
                WHERE nom_type_entreprise LIKE '%Maitrise d%oeuvre%'
                OR nom_type_entreprise LIKE '%Maîtrise d%oeuvre%'       
                OR nom_type_entreprise LIKE '%Maîtrise d%œuvre%'
                OR nom_type_entreprise LIKE '%Maitrise d%œuvre%'       
                OR nom_type_entreprise LIKE '%MOE%'
                OR nom_type_entreprise LIKE '%Mandataire%'
            )
            ORDER BY nom_entreprise
        """)
        return cursor.fetchall()
    finally:
        close_db(conn)

def get_all_cotraitants():
    """Récupère la liste des entreprises pouvant être co-traitants"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Toutes les entreprises peuvent potentiellement être des co-traitants
        cursor.execute("""
            SELECT id_entreprise, nom_entreprise, siret 
            FROM entreprise 
            WHERE id_type_entreprise = (
                SELECT id_type_entreprise FROM type_entreprise 
                WHERE nom_type_entreprise = 'Co-traitant'
            )
            ORDER BY nom_entreprise
        """)
        return cursor.fetchall()
    finally:
        close_db(conn)

def get_detailed_enterprise_data(enterprise_id):
    """Récupère les données détaillées d'une entreprise"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                e.*, 
                v.nom_ville, 
                cp.code_postal,
                c.nom_cedex,
                t.nom_type_entreprise
            FROM entreprise e
            LEFT JOIN villes v ON e.id_ville = v.id_ville
            LEFT JOIN code_postal cp ON e.id_cp = cp.id_cp
            LEFT JOIN cedex c ON e.id_cedex = c.id_cedex
            LEFT JOIN type_entreprise t ON e.id_type_entreprise = t.id_type_entreprise
            WHERE e.id_entreprise = ?
        """, (enterprise_id,))
        
        data = cursor.fetchone()
        if data:
            # Convertir le Row object en dictionnaire pour faciliter la manipulation
            return dict(data)
        return None
    finally:
        close_db(conn)

def format_dc1_data(projet_data, moa_data, moe_data, cotraitants_data=None):
    """Formate les données pour le DC1"""
    # Si cotraitants_data est None, initialiser à une liste vide
    if cotraitants_data is None:
        cotraitants_data = []
    
    # Construction de l'adresse complète pour la MOA
    adresse_moa = moa_data.get('adresse', '')
    if moa_data.get('code_postal'):
        adresse_moa += f", {moa_data['code_postal']}"
    if moa_data.get('nom_ville'):
        adresse_moa += f" {moa_data['nom_ville']}"
    if moa_data.get('id_cedex') and moa_data['id_cedex'] is not None:
        adresse_moa += f" CEDEX {moa_data['id_cedex']}"
    
    # Construction de l'adresse complète pour la MOE/Mandataire
    adresse_moe = moe_data.get('adresse', '')
    if moe_data.get('code_postal'):
        adresse_moe += f", {moe_data['code_postal']}"
    if moe_data.get('nom_ville'):
        adresse_moe += f" {moe_data['nom_ville']}"
    if moe_data.get('id_cedex') and moe_data['id_cedex'] is not None:
        adresse_moe += f" CEDEX {moe_data['id_cedex']}"
    
    # Préparation des données pour le template
    data = {
        # Informations du projet
        "nom_affaire": projet_data.get('nom_affaire', ''),
        "reference_projet": projet_data.get('reference_projet', ''),
        "objet_consultation": projet_data.get('objet_consultation', ''),
        
        # Informations de la MOA
        "nom_moa": moa_data.get('nom_entreprise', ''),
        "adresse_moa": adresse_moa,
        
        # Informations du mandataire (MOE)
        "nom_mandataire": moe_data.get('nom_entreprise', ''),
        "forme_juridique_mandataire": moe_data.get('forme_juridique', ''),
        "adresse_mandataire": adresse_moe,
        "email_mandataire": f"Email: {moe_data.get('email_principal', 'Non spécifié')}",
        "telephone_mandataire": f"Téléphone: {moe_data.get('numero_telephone', 'Non spécifié')}",
        "portable_mandataire": f"Portable: {moe_data.get('numero_portable', 'Non spécifié')}",
        "siret_mandataire": f"SIRET: {moe_data.get('siret', 'Non spécifié')}",
        
        # Tableau des co-traitants (avec le mandataire comme premier élément)
        "cotraitants": [
            {
                "numero": 1,  # Le mandataire est toujours numéro 1
                "nom": moe_data.get('nom_entreprise', ''),
                "adresse": adresse_moe,
                "email": f"Email: {moe_data.get('email_principal', 'Non spécifié')}",
                "telephone": f"Téléphone: {moe_data.get('numero_telephone', 'Non spécifié')}",
                "portable": f"Portable: {moe_data.get('numero_portable', 'Non spécifié')}",
                "siret": f"SIRET: {moe_data.get('siret', 'Non spécifié')}",
                "prestation": moe_data.get('prestations', 'Mandataire')  # Utiliser la prestation ou "Mandataire" par défaut
            }
        ]
    }
    
    # Ajouter chaque co-traitant au tableau (en commençant à partir du numéro 2)
    for i, cotraitant in enumerate(cotraitants_data):
        if not cotraitant:
            continue
            
        # Construction de l'adresse complète pour le co-traitant
        adresse_cotraitant = cotraitant.get('adresse', '')
        if cotraitant.get('code_postal'):
            adresse_cotraitant += f", {cotraitant['code_postal']}"
        if cotraitant.get('nom_ville'):
            adresse_cotraitant += f" {cotraitant['nom_ville']}"
        if cotraitant.get('id_cedex') and cotraitant['id_cedex'] is not None:
            adresse_cotraitant += f" CEDEX {cotraitant['id_cedex']}"
        
        data["cotraitants"].append({
            "numero": i+2,  # Commencer à 2 car le mandataire est déjà numéro 1
            "nom": cotraitant.get('nom_entreprise', ''),
            "adresse": adresse_cotraitant,
            "email": f"Email: {cotraitant.get('email_principal', 'Non spécifié')}",
            "telephone": f"Téléphone: {cotraitant.get('numero_telephone', 'Non spécifié')}",
            "portable": f"Portable: {cotraitant.get('numero_portable', 'Non spécifié')}",
            "siret": f"SIRET: {cotraitant.get('siret', 'Non spécifié')}",
            "prestation": cotraitant.get('prestations', 'Non spécifié')
        })
    
    return data


def format_dc2_data(dc1_data, moe_data):
    """Formate les données pour le DC2 à partir des données du DC1"""
    # Récupérer les informations de base du DC1
    dc2_data = {
        # Informations du projet
        "nom_affaire": dc1_data.get('nom_affaire', ''),
        "reference_projet": dc1_data.get('reference_projet', ''),
        "objet_consultation": dc1_data.get('objet_consultation', ''),
        
        # Informations du mandataire
        "nom_mandataire": dc1_data.get('nom_mandataire', ''),
        "adresse_mandataire": dc1_data.get('adresse_mandataire', ''),
        "email_mandataire": dc1_data.get('email_mandataire', ''),
        "telephone_mandataire": dc1_data.get('telephone_mandataire', ''),
        "portable_mandataire": dc1_data.get('portable_mandataire', ''),
        "siret_mandataire": dc1_data.get('siret_mandataire', ''),
        
        # Forme juridique pour le DC2 - priorité à la valeur saisie dans le formulaire
        "forme_juridique_mandataire": dc1_data.get('forme_juridique_mandataire', moe_data.get('forme_juridique', '')),
    }
    
    # Ajouter les chiffres d'affaires, triés par année décroissante
    if 'ca_mandataire' in dc1_data and dc1_data['ca_mandataire']:
        # Trier les CA par année décroissante
        sorted_ca = sorted(dc1_data['ca_mandataire'], key=lambda x: int(x['annee']), reverse=True)
        dc2_data['ca_mandataire'] = sorted_ca
    
    return dc2_data


# Nouvelles fonctions pour les documents de projet

def format_ordre_service_data(projet_data, lot_data, entreprise_data, montant_data):
    """Formate les données pour l'ordre de service"""
    return {
        # Informations du projet
        "nom_affaire": projet_data.get('nom_affaire', ''),
        "reference_projet": projet_data.get('reference_projet', ''),
        "identification_operation": projet_data.get('identification_operation', ''),
        "date_notification": projet_data.get('date_notification', ''),
        
        # Informations du lot
        "numero_lot": lot_data.get('numero_lot', ''),
        "objet_marche": lot_data.get('objet_marche', ''),
        
        # Informations de l'entreprise
        "nom_entreprise": entreprise_data.get('nom_entreprise', ''),
        "siret": entreprise_data.get('siret', ''),
        "adresse_complete": format_adresse_complete(entreprise_data),
        "email": entreprise_data.get('email_principal', ''),
        "telephone": entreprise_data.get('numero_telephone', ''),
        "portable": entreprise_data.get('numero_portable', ''),
        "referent": entreprise_data.get('referent', ''),
        
        # Informations financières
        "montant_ht": montant_data.get('montant_ht', 0),
        "montant_ttc": montant_data.get('montant_ttc', 0),
        "taux_tva": montant_data.get('taux_tva', 20.0),
        
        # Statut dans le lot
        "est_mandataire": entreprise_data.get('est_mandataire', False)
    }

def format_attri1_data(projet_data, lot_data, entreprise_data, montant_data):
    """Formate les données pour l'ATTRI-1"""
    return {
        # Informations du projet
        "nom_affaire": projet_data.get('nom_affaire', ''),
        "reference_projet": projet_data.get('reference_projet', ''),
        "identification_operation": projet_data.get('identification_operation', ''),
        "nom_moa": projet_data.get('nom_moa', ''),
        "date_notification": projet_data.get('date_notification', ''),
        
        # Informations du lot
        "numero_lot": lot_data.get('numero_lot', ''),
        "objet_marche": lot_data.get('objet_marche', ''),
        
        # Informations de l'entreprise
        "nom_entreprise": entreprise_data.get('nom_entreprise', ''),
        "siret": entreprise_data.get('siret', ''),
        "forme_juridique": entreprise_data.get('forme_juridique', ''),
        "adresse_complete": format_adresse_complete(entreprise_data),
        "email": entreprise_data.get('email_principal', ''),
        "telephone": entreprise_data.get('numero_telephone', ''),
        "portable": entreprise_data.get('numero_portable', ''),
        "referent": entreprise_data.get('referent', ''),
        
        # Informations financières
        "montant_ht": montant_data.get('montant_ht', 0),
        "montant_ttc": montant_data.get('montant_ttc', 0),
        "taux_tva": montant_data.get('taux_tva', 20.0),
        
        # Statut dans le lot
        "est_mandataire": entreprise_data.get('est_mandataire', False)
    }

def format_dc4_data(projet_data, lot_data, entreprise_data, sous_traitants_data):
    """Formate les données pour le DC-4 (sous-traitance)"""
    return {
        # Informations du projet
        "nom_affaire": projet_data.get('nom_affaire', ''),
        "reference_projet": projet_data.get('reference_projet', ''),
        "identification_operation": projet_data.get('identification_operation', ''),
        
        # Informations du lot
        "numero_lot": lot_data.get('numero_lot', ''),
        "objet_marche": lot_data.get('objet_marche', ''),
        
        # Informations de l'entreprise principale
        "nom_entreprise": entreprise_data.get('nom_entreprise', ''),
        "siret": entreprise_data.get('siret', ''),
        "adresse_complete": format_adresse_complete(entreprise_data),
        
        # Sous-traitants
        "sous_traitants": sous_traitants_data or []
    }

def format_montant_euro(montant):
    """Formate un montant en euros avec séparateurs de milliers et 2 décimales"""
    if montant is None:
        return "0.00 €"
    # Arrondir à 2 décimales puis formater avec séparateur de milliers
    montant_arrondi = round(float(montant), 2)
    return f"{montant_arrondi:,.2f} €".replace(",", " ")

def format_exe10_data(projet_data, lot_data, entreprise_data, montant_data, avancement_pct=0, avenant_data=None):
    """Formate les données pour l'EXE-10 (état d'avancement)"""
    
    # Récupérer les données MOA depuis le projet
    moa_data = {}
    if projet_data.get('id_moa'):
        moa_data = get_detailed_enterprise_data(projet_data['id_moa'])
    
    # Calculer les montants selon les formules fournies
    montant_initial_ht = 0
    montant_avenant_ht = 0
    prc_ecart_introduit = 0
    montant_final_ht = montant_data.get('montant_ht', 0)
    
    if avenant_data:
        montant_initial_ht = avenant_data.get('montant_precedent_ht', 0)
        montant_nouveau_ht = avenant_data.get('montant_nouveau_ht', 0)
        montant_avenant_ht = montant_nouveau_ht - montant_initial_ht
        if montant_initial_ht > 0:
            prc_ecart_introduit = (montant_avenant_ht / montant_initial_ht) * 100
        montant_final_ht = montant_nouveau_ht
    else:
        # Pas d'avenant, montant initial = montant actuel
        montant_initial_ht = montant_data.get('montant_ht', 0)
        montant_final_ht = montant_initial_ht
    
    # Calculer les montants TTC
    taux_tva = montant_data.get('taux_tva', 20.0)
    montant_initial_ttc = montant_initial_ht * (1 + taux_tva / 100)
    montant_avenant_ttc = montant_avenant_ht * (1 + taux_tva / 100)
    montant_final_ttc = montant_final_ht * (1 + taux_tva / 100)
    
    return {
        # Informations du projet
        "nom_affaire": projet_data.get('nom_affaire', ''),
        "reference_projet": projet_data.get('reference_projet', ''),
        "identification_operation": projet_data.get('identification_operation', ''),
        "date_notification": projet_data.get('date_notification', ''),
        
        # Informations MOA
        "nom_moa": moa_data.get('nom_entreprise', '') if moa_data else projet_data.get('nom_moa', ''),
        "adresse_moa": format_adresse_complete(moa_data) if moa_data else '',
        
        # Informations du lot
        "numero_lot": lot_data.get('numero_lot', ''),
        "objet_marche": lot_data.get('objet_marche', ''),
        "duree_execution_marche": lot_data.get('duree_execution', ''),  # À ajouter via formulaire
        
        # Informations de l'entreprise
        "nom_entreprise": entreprise_data.get('nom_entreprise', ''),
        "siret": entreprise_data.get('siret', ''),
        "adresse_complete": format_adresse_complete(entreprise_data),
        "telephone_entreprise": entreprise_data.get('numero_telephone', ''),
        "email_entreprise": entreprise_data.get('email_principal', ''),
        
        # Informations d'avenant
        "numero_avenant": avenant_data.get('numero_avenant', '') if avenant_data else '',
        "objet_avenant": avenant_data.get('objet_avenant', '') if avenant_data else '',
        
        # Informations financières (formatées pour affichage)
        "montant_initial_ht": format_montant_euro(montant_initial_ht),
        "montant_initial_ttc": format_montant_euro(montant_initial_ttc),
        "montant_avenant_ht": format_montant_euro(montant_avenant_ht),
        "montant_avenant_ttc": format_montant_euro(montant_avenant_ttc),
        "prc_ecart_introduit": f"{round(prc_ecart_introduit, 2):.2f} %",
        "montant_final_ht": format_montant_euro(montant_final_ht),
        "montant_final_ttc": format_montant_euro(montant_final_ttc),
        "taux_tva": f"{taux_tva:.2f} %",
        
        # Informations d'avancement
        "avancement_pct": f"{avancement_pct:.2f} %",
        "montant_realise_ht": format_montant_euro(montant_final_ht * avancement_pct / 100),
        "montant_realise_ttc": format_montant_euro(montant_final_ht * (1 + taux_tva / 100) * avancement_pct / 100)
    }

def format_exe1t_data(projet_data, lot_data, entreprise_data, avenant_data):
    """Formate les données pour l'EXE-1T (avenant)"""
    return {
        # Informations du projet
        "nom_affaire": projet_data.get('nom_affaire', ''),
        "reference_projet": projet_data.get('reference_projet', ''),
        "identification_operation": projet_data.get('identification_operation', ''),
        
        # Informations du lot
        "numero_lot": lot_data.get('numero_lot', ''),
        "objet_marche": lot_data.get('objet_marche', ''),
        
        # Informations de l'entreprise
        "nom_entreprise": entreprise_data.get('nom_entreprise', ''),
        "siret": entreprise_data.get('siret', ''),
        "adresse_complete": format_adresse_complete(entreprise_data),
        
        # Informations de l'avenant
        "numero_avenant": avenant_data.get('numero_avenant', ''),
        "objet_avenant": avenant_data.get('objet_avenant', ''),
        "date_avenant": avenant_data.get('date_avenant', ''),
        "motif": avenant_data.get('motif', ''),
        
        # Montants
        "montant_precedent_ht": avenant_data.get('montant_precedent_ht', 0),
        "montant_nouveau_ht": avenant_data.get('montant_nouveau_ht', 0),
        "taux_tva": avenant_data.get('taux_tva', 20.0),
        "montant_precedent_ttc": avenant_data.get('montant_precedent_ht', 0) * (1 + avenant_data.get('taux_tva', 20.0) / 100),
        "montant_nouveau_ttc": avenant_data.get('montant_nouveau_ht', 0) * (1 + avenant_data.get('taux_tva', 20.0) / 100),
        "difference_ht": avenant_data.get('montant_nouveau_ht', 0) - avenant_data.get('montant_precedent_ht', 0),
        "difference_ttc": (avenant_data.get('montant_nouveau_ht', 0) - avenant_data.get('montant_precedent_ht', 0)) * (1 + avenant_data.get('taux_tva', 20.0) / 100)
    }

def format_adresse_complete(entreprise_data):
    """Formate l'adresse complète d'une entreprise"""
    adresse = entreprise_data.get('adresse', '')
    if entreprise_data.get('code_postal'):
        adresse += f", {entreprise_data['code_postal']}"
    if entreprise_data.get('nom_ville'):
        adresse += f" {entreprise_data['nom_ville']}"
    if entreprise_data.get('nom_cedex'):
        adresse += f" CEDEX {entreprise_data['nom_cedex']}"
    return adresse

def get_projet_data_for_document(id_projet, type_document, id_lot=None, id_entreprise=None, **kwargs):
    """Récupère et formate les données pour un document de projet"""
    projet_data = get_projet(id_projet)
    if not projet_data:
        return None
    
    projet_data = dict(projet_data)
    
    # Si un lot spécifique est demandé
    lot_data = None
    if id_lot:
        from models.projet import get_lot
        lot_data = get_lot(id_lot)
        if lot_data:
            lot_data = dict(lot_data)
    
    # Si une entreprise spécifique est demandée
    entreprise_data = None
    montant_data = None
    if id_entreprise:
        if id_lot:
            # Récupérer les données de l'entreprise dans le contexte du lot
            entreprises_lot = get_entreprises_by_lot(id_lot)
            for ent in entreprises_lot:
                if ent['id_entreprise'] == id_entreprise:
                    entreprise_data = dict(ent)
                    montant_data = get_montant_actuel_lot_entreprise(ent['id_lot_entreprise'])
                    break
        else:
            # Récupérer les données de base de l'entreprise
            entreprise_data = get_detailed_enterprise_data(id_entreprise)
    
    # Formater selon le type de document
    if type_document == "ordre_service":
        return format_ordre_service_data(projet_data, lot_data, entreprise_data, montant_data)
    
    elif type_document == "attri1":
        return format_attri1_data(projet_data, lot_data, entreprise_data, montant_data)
    
    elif type_document == "dc4":
        sous_traitants = kwargs.get('sous_traitants', [])
        return format_dc4_data(projet_data, lot_data, entreprise_data, sous_traitants)
    
    elif type_document == "exe10":
        avancement_pct = kwargs.get('avancement_pct', 0)
        return format_exe10_data(projet_data, lot_data, entreprise_data, montant_data, avancement_pct)
    
    elif type_document == "exe1t":
        avenant_data = kwargs.get('avenant_data', {})
        return format_exe1t_data(projet_data, lot_data, entreprise_data, avenant_data)
    
    elif type_document == "dc1":
        # Version projet du DC1
        return format_projet_dc1_data(projet_data)
    
    elif type_document == "dc2":
        # Version projet du DC2
        return format_projet_dc2_data(projet_data, entreprise_data)
    
    return None

def format_projet_dc1_data(projet_data):
    """Formate les données pour un DC1 basé sur un projet"""
    from models.projet import get_moe_cotraitants
    
    moe_cotraitants = get_moe_cotraitants(projet_data['id_projet'])
    
    cotraitants_list = []
    mandataire_data = None
    
    for i, moe in enumerate(moe_cotraitants):
        moe_dict = dict(moe)
        cotraitant_info = {
            "numero": i + 1,
            "nom": moe_dict.get('nom_entreprise', ''),
            "siret": f"SIRET: {moe_dict.get('siret', 'Non spécifié')}",
            "prestation": "MOE" if moe_dict.get('est_mandataire') else "Co-traitant MOE"
        }
        
        if moe_dict.get('est_mandataire'):
            mandataire_data = cotraitant_info
        else:
            cotraitants_list.append(cotraitant_info)
    
    return {
        "nom_affaire": projet_data.get('nom_affaire', ''),
        "reference_projet": projet_data.get('reference_projet', ''),
        "objet_consultation": projet_data.get('identification_operation', ''),
        "nom_moa": projet_data.get('nom_moa', ''),
        "nom_mandataire": mandataire_data.get('nom') if mandataire_data else '',
        "cotraitants": [mandataire_data] + cotraitants_list if mandataire_data else cotraitants_list
    }

def format_projet_dc2_data(projet_data, entreprise_data):
    """Formate les données pour un DC2 basé sur un projet"""
    if not entreprise_data:
        return None
    
    # Récupérer les chiffres d'affaires de l'entreprise
    ca_data = get_chiffres_affaires(entreprise_data['id_entreprise'])
    ca_mandataire = []
    
    if ca_data and ca_data.get('annees'):
        ca_pairs = list(zip(ca_data['annees'], ca_data['montants']))
        ca_pairs.sort(key=lambda x: int(x[0]), reverse=True)
        
        for annee, montant in ca_pairs:
            ca_mandataire.append({
                'annee': str(annee),
                'montant': str(montant)
            })
    
    return {
        "nom_affaire": projet_data.get('nom_affaire', ''),
        "reference_projet": projet_data.get('reference_projet', ''),
        "objet_consultation": projet_data.get('identification_operation', ''),
        "nom_mandataire": entreprise_data.get('nom_entreprise', ''),
        "forme_juridique_mandataire": entreprise_data.get('forme_juridique', ''),
        "adresse_mandataire": format_adresse_complete(entreprise_data),
        "siret_mandataire": f"SIRET: {entreprise_data.get('siret', 'Non spécifié')}",
        "ca_mandataire": ca_mandataire
    }

# Nouvelles fonctions pour la génération multiple de documents

def get_data_for_ordre_service(lot, entreprise, form_data):
    """Génère les données pour un ordre de service"""
    # Convertir les Row objects en dictionnaires
    lot_dict = dict(lot) if lot else {}
    entreprise_dict = dict(entreprise) if entreprise else {}
    base_key = f"{lot_dict['id_lot']}_{entreprise_dict['id_entreprise']}"
    
    # Récupérer les données du projet
    from models.projet import get_projet
    projet_data = get_projet(lot_dict.get('id_projet'))
    if projet_data:
        projet_data = dict(projet_data)
    
    # Récupérer les données détaillées de l'entreprise
    entreprise_data = get_detailed_enterprise_data(entreprise_dict.get('id_entreprise'))
    
    # Récupérer le montant actuel
    from models.projet import get_montant_actuel_lot_entreprise
    montant_data = get_montant_actuel_lot_entreprise(entreprise_dict.get('id_lot_entreprise'))
    if montant_data:
        montant_data = dict(montant_data)
    
    return format_ordre_service_data(projet_data, lot_dict, entreprise_data, montant_data)

def get_data_for_attri1(lot, entreprise, form_data):
    """Génère les données pour un ATTRI1"""
    # Convertir les Row objects en dictionnaires
    lot_dict = dict(lot) if lot else {}
    entreprise_dict = dict(entreprise) if entreprise else {}
    base_key = f"{lot_dict['id_lot']}_{entreprise_dict['id_entreprise']}"
    
    # Récupérer les données du projet
    from models.projet import get_projet
    projet_data = get_projet(lot_dict.get('id_projet'))
    if projet_data:
        projet_data = dict(projet_data)
    
    # Récupérer les données détaillées de l'entreprise
    entreprise_data = get_detailed_enterprise_data(entreprise_dict.get('id_entreprise'))
    
    # Récupérer le montant actuel
    from models.projet import get_montant_actuel_lot_entreprise
    montant_data = get_montant_actuel_lot_entreprise(entreprise_dict.get('id_lot_entreprise'))
    if montant_data:
        montant_data = dict(montant_data)
    
    return format_attri1_data(projet_data, lot_dict, entreprise_data, montant_data)

def get_data_for_dc4(lot, entreprise, form_data):
    """Génère les données pour un DC4"""
    # Convertir les Row objects en dictionnaires
    lot_dict = dict(lot) if lot else {}
    entreprise_dict = dict(entreprise) if entreprise else {}
    base_key = f"{lot_dict['id_lot']}_{entreprise_dict['id_entreprise']}"
    
    # Récupérer les données du projet
    from models.projet import get_projet
    projet_data = get_projet(lot_dict.get('id_projet'))
    if projet_data:
        projet_data = dict(projet_data)
    
    # Récupérer les données détaillées de l'entreprise
    entreprise_data = get_detailed_enterprise_data(entreprise_dict.get('id_entreprise'))
    
    # Pour le DC4, on peut avoir des sous-traitants (à implémenter si nécessaire)
    sous_traitants_data = []
    
    return format_dc4_data(projet_data, lot_dict, entreprise_data, sous_traitants_data)

def get_data_for_exe10(lot, entreprise, form_data):
    """Génère les données pour un EXE10"""
    # Convertir les Row objects en dictionnaires
    lot_dict = dict(lot) if lot else {}
    entreprise_dict = dict(entreprise) if entreprise else {}
    base_key = f"{lot_dict['id_lot']}_{entreprise_dict['id_entreprise']}"
    
    # Récupérer les données du projet
    from models.projet import get_projet, get_latest_avenant_by_lot_entreprise
    projet_data = get_projet(lot_dict.get('id_projet'))
    if projet_data:
        projet_data = dict(projet_data)
    
    # Récupérer les données détaillées de l'entreprise
    entreprise_data = get_detailed_enterprise_data(entreprise_dict.get('id_entreprise'))
    
    # Récupérer le montant actuel
    from models.projet import get_montant_actuel_lot_entreprise
    montant_data = get_montant_actuel_lot_entreprise(entreprise_dict.get('id_lot_entreprise'))
    if montant_data:
        montant_data = dict(montant_data)
    
    # Récupérer le dernier avenant
    avenant_data = None
    id_lot_entreprise = entreprise_dict.get('id_lot_entreprise')
    if id_lot_entreprise:
        latest_avenant = get_latest_avenant_by_lot_entreprise(id_lot_entreprise)
        if latest_avenant:
            avenant_data = dict(latest_avenant)
    
    # Récupérer la durée d'exécution depuis le formulaire
    duree_execution = form_data.get(f'duree_execution_marche_{base_key}', '')
    lot_dict['duree_execution'] = duree_execution
    
    return format_exe10_data(projet_data, lot_dict, entreprise_data, montant_data, 0, avenant_data)

def get_data_for_exe1t(lot, entreprise, form_data):
    """Génère les données pour un EXE1T"""
    # Convertir les Row objects en dictionnaires
    lot_dict = dict(lot) if lot else {}
    entreprise_dict = dict(entreprise) if entreprise else {}
    base_key = f"{lot_dict['id_lot']}_{entreprise_dict['id_entreprise']}"
    
    # Récupérer les données du projet
    from models.projet import get_projet
    projet_data = get_projet(lot_dict.get('id_projet'))
    if projet_data:
        projet_data = dict(projet_data)
    
    # Récupérer les données détaillées de l'entreprise
    entreprise_data = get_detailed_enterprise_data(entreprise_dict.get('id_entreprise'))
    
    # Récupérer les données d'avenant depuis le formulaire
    avenant_data = {
        'numero_avenant': form_data.get(f'numero_avenant_{base_key}', ''),
        'date_avenant': form_data.get(f'date_avenant_{base_key}', ''),
        'objet_avenant': form_data.get(f'objet_avenant_{base_key}', ''),
        'montant_precedent_ht': float(form_data.get(f'montant_precedent_ht_{base_key}', 0)),
        'montant_nouveau_ht': float(form_data.get(f'montant_nouveau_ht_{base_key}', 0)),
        'motif': form_data.get(f'motif_{base_key}', ''),
        'taux_tva': 20.0  # TVA par défaut
    }
    
    return format_exe1t_data(projet_data, lot_dict, entreprise_data, avenant_data)

def get_data_for_dc1(lot, entreprise, form_data):
    """Génère les données pour un DC1 (version projet)"""
    # Convertir les Row objects en dictionnaires
    lot_dict = dict(lot) if lot else {}
    
    # Récupérer les données du projet
    from models.projet import get_projet
    projet_data = get_projet(lot_dict.get('id_projet'))
    if projet_data:
        projet_data = dict(projet_data)
    
    return format_projet_dc1_data(projet_data)

def get_data_for_dc2(lot, entreprise, form_data):
    """Génère les données pour un DC2 (version projet)"""
    # Convertir les Row objects en dictionnaires
    lot_dict = dict(lot) if lot else {}
    entreprise_dict = dict(entreprise) if entreprise else {}
    
    # Récupérer les données du projet
    from models.projet import get_projet
    projet_data = get_projet(lot_dict.get('id_projet'))
    if projet_data:
        projet_data = dict(projet_data)
    
    # Récupérer les données détaillées de l'entreprise
    entreprise_data = get_detailed_enterprise_data(entreprise_dict.get('id_entreprise'))
    
    return format_projet_dc2_data(projet_data, entreprise_data)

def analyze_missing_data(id_projet, document_types, lot_ids):
    """Analyse les données manquantes pour la génération de documents multiples"""
    from models.projet import get_projet, get_lot, get_entreprises_by_lot
    
    # Récupérer les données du projet
    projet = get_projet(id_projet)
    missing_data = {
        'documents': [],
        'global_missing': [],
        'lots_data': []
    }
    
    # Définir les champs requis par type de document
    required_fields = {
        'ordre_service': ['date_demarrage', 'delai_execution'],
        'attri1': [],
        'dc4': [],
        'exe10': ['duree_execution_marche'],
        'exe1t': ['numero_avenant', 'date_avenant', 'objet_avenant', 'montant_precedent_ht', 'montant_nouveau_ht'],
        'dc1': [],
        'dc2': []
    }
    
    # Analyser chaque lot sélectionné
    for lot_id in lot_ids:
        lot = get_lot(lot_id)
        if not lot:
            continue
            
        lot_data = {
            'lot': dict(lot),
            'enterprises': [],
            'missing_fields': []
        }
        
        # Récupérer les entreprises du lot
        entreprises = get_entreprises_by_lot(lot_id)
        
        for entreprise in entreprises:
            entreprise_data = {
                'entreprise': dict(entreprise),
                'documents': {}
            }
            
            # Pour chaque type de document sélectionné
            for doc_type in document_types:
                doc_missing = []
                
                # Vérifier les champs requis pour ce type de document
                if doc_type in required_fields:
                    for field in required_fields[doc_type]:
                        # Logique pour vérifier si le champ est disponible
                        # Pour le moment, on considère qu'ils sont tous manquants
                        doc_missing.append(field)
                
                entreprise_data['documents'][doc_type] = {
                    'missing_fields': doc_missing,
                    'can_generate': len(doc_missing) == 0
                }
            
            lot_data['enterprises'].append(entreprise_data)
        
        missing_data['lots_data'].append(lot_data)
    
    # Identifier les données globales manquantes au niveau projet
    if not projet:
        missing_data['global_missing'].append('projet_introuvable')
    
    # Créer la liste des documents à générer
    for doc_type in document_types:
        doc_info = next((t for t in get_projet_document_templates() if t['type'] == doc_type), None)
        if doc_info:
            missing_data['documents'].append({
                'type': doc_type,
                'nom': doc_info['nom'],
                'description': doc_info['description']
            })
    
    return missing_data
