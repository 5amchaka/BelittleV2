from database import get_db, close_db

def get_document_templates():
    """Récupère la liste des modèles de documents disponibles"""
    return [
        {"id": 1, "nom": "Formulaire DC1", "description": "Lettre de candidature avec désignation du mandataire par ses co-traitants"},
        {"id": 2, "nom": "Formulaire DC2", "description": "Déclaration du candidat"},
        {"id": 3, "nom": "Formulaire ATTRI1", "description": "Acte d'engagement"}
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
            "corps_metiers": ", ".join(enterprise_data["corps_metiers"])
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
