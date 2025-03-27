from database import get_db, close_db

def get_or_create_ville(ville_nom):
    """Récupère ou crée une ville et retourne son ID"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id_ville FROM villes WHERE nom_ville = ?", (ville_nom,))
        row = cursor.fetchone()
        
        if row:
            return row["id_ville"]
        else:
            cursor.execute("INSERT INTO villes (nom_ville) VALUES (?)", (ville_nom,))
            conn.commit()
            return cursor.lastrowid
    finally:
        close_db(conn)

def get_or_create_type(type_nom):
    """Récupère ou crée un type d'entreprise et retourne son ID"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id_type_entreprise FROM type_entreprise WHERE nom_type_entreprise = ?", (type_nom,))
        row = cursor.fetchone()
        
        if row:
            return row["id_type_entreprise"]
        else:
            cursor.execute("INSERT INTO type_entreprise (nom_type_entreprise) VALUES (?)", (type_nom,))
            conn.commit()
            return cursor.lastrowid
    finally:
        close_db(conn)

def get_types_entreprise():
    """Récupère tous les types d'entreprise"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id_type_entreprise, nom_type_entreprise FROM type_entreprise ORDER BY nom_type_entreprise")
        return cursor.fetchall()
    finally:
        close_db(conn)

def get_corps_metiers():
    """Récupère tous les corps de métier"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id_corps_metier, nom_corps_metier FROM corps_metier ORDER BY nom_corps_metier")
        return cursor.fetchall()
    finally:
        close_db(conn)

def get_villes():
    """Récupère toutes les villes"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT DISTINCT nom_ville FROM villes ORDER BY nom_ville")
        return [row["nom_ville"] for row in cursor.fetchall()]
    finally:
        close_db(conn)

def get_prestations():
    """Récupère toutes les prestations existantes"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT DISTINCT prestations FROM entreprise WHERE prestations IS NOT NULL AND prestations <> '' ORDER BY prestations")
        return [row["prestations"] for row in cursor.fetchall()]
    finally:
        close_db(conn)

def search_enterprises(corps_metier_id=None, type_entreprise_id=None):
    """Recherche des entreprises selon les critères donnés"""
    conn = get_db()
    cursor = conn.cursor()
    
    query = """
    SELECT DISTINCT
        e.id_entreprise,
        e.nom_entreprise,
        e.siret,
        e.adresse || ', ' || 
            COALESCE(cp.code_postal || ' ', '') || 
            COALESCE(v.nom_ville, '') ||
            CASE WHEN e.id_cedex IS NOT NULL THEN ' ' || c.nom_cedex ELSE '' END AS adresse_complete,
        e.email_principal,
        e.email_secondaire,
        e.referent,
        e.numero_telephone,
        e.numero_portable
    FROM entreprise e
    LEFT JOIN villes v ON e.id_ville = v.id_ville
    LEFT JOIN code_postal cp ON e.id_cp = cp.id_cp
    LEFT JOIN cedex c ON e.id_cedex = c.id_cedex
    """
    
    params = []
    conditions = []
    
    # Si un corps de métier est sélectionné
    if corps_metier_id:
        query += """
        LEFT JOIN entreprise_corps_metier ecm ON e.id_entreprise = ecm.id_entreprise
        """
        conditions.append("ecm.id_corps_metier = ?")
        params.append(corps_metier_id)
    
    # Si un type d'entreprise est sélectionné
    if type_entreprise_id:
        conditions.append("e.id_type_entreprise = ?")
        params.append(type_entreprise_id)
    
    # Ajouter les conditions à la requête
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    try:
        cursor.execute(query, params)
        return cursor.fetchall()
    finally:
        close_db(conn)

def get_filter_names(corps_metier_id=None, type_entreprise_id=None):
    """Récupère les noms des filtres appliqués"""
    conn = get_db()
    cursor = conn.cursor()
    
    corps_metier_name = ""
    type_entreprise_name = ""
    
    try:
        if corps_metier_id:
            cursor.execute("SELECT nom_corps_metier FROM corps_metier WHERE id_corps_metier = ?", (corps_metier_id,))
            result = cursor.fetchone()
            if result:
                corps_metier_name = result["nom_corps_metier"]
        
        if type_entreprise_id:
            cursor.execute("SELECT nom_type_entreprise FROM type_entreprise WHERE id_type_entreprise = ?", (type_entreprise_id,))
            result = cursor.fetchone()
            if result:
                type_entreprise_name = result["nom_type_entreprise"]
                
        return corps_metier_name, type_entreprise_name
    finally:
        close_db(conn)

def get_enterprise(enterprise_id):
    """Récupère les détails d'une entreprise par son ID"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM entreprise WHERE id_entreprise = ?", (enterprise_id,))
        return cursor.fetchone()
    finally:
        close_db(conn)

def get_enterprise_corps_metiers(enterprise_id):
    """Récupère les corps de métier associés à une entreprise"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id_corps_metier FROM entreprise_corps_metier WHERE id_entreprise = ?", (enterprise_id,))
        return [str(row["id_corps_metier"]) for row in cursor.fetchall()]
    finally:
        close_db(conn)

def add_enterprise(enterprise_data, corps_metiers):
    """Ajoute une nouvelle entreprise et ses corps de métier associés"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO entreprise 
            (nom_entreprise, siret, forme_juridique, adresse, id_ville, id_cp, id_cedex, 
             email_principal, email_secondaire, referent, numero_telephone, 
             numero_portable, id_type_entreprise, prestations)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            enterprise_data['nom_entreprise'], 
            enterprise_data['siret'],
            enterprise_data['forme_juridique'],
            enterprise_data['adresse'], 
            enterprise_data['id_ville'], 
            enterprise_data['id_cp'], 
            enterprise_data['id_cedex'],
            enterprise_data['email_principal'], 
            enterprise_data['email_secondaire'], 
            enterprise_data['referent'], 
            enterprise_data['numero_telephone'],
            enterprise_data['numero_portable'], 
            enterprise_data['id_type_entreprise'], 
            enterprise_data['prestations']
        ))
        
        enterprise_id = cursor.lastrowid
        
        for cm_id in corps_metiers:
            cursor.execute("INSERT INTO entreprise_corps_metier (id_entreprise, id_corps_metier) VALUES (?, ?)", 
                          (enterprise_id, cm_id))
        
        conn.commit()
        return enterprise_id
    except:
        conn.rollback()
        raise
    finally:
        close_db(conn)

def update_enterprise(enterprise_id, enterprise_data, corps_metiers):
    """Met à jour une entreprise existante et ses corps de métier associés"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE entreprise
            SET nom_entreprise = ?, siret = ?, forme_juridique = ?, adresse = ?, id_ville = ?, id_cp = ?, id_cedex = ?,
                email_principal = ?, email_secondaire = ?, referent = ?, numero_telephone = ?, numero_portable = ?,
                id_type_entreprise = ?, prestations = ?
            WHERE id_entreprise = ?
        """, (
            enterprise_data['nom_entreprise'], 
            enterprise_data['siret'],
            enterprise_data['forme_juridique'],
            enterprise_data['adresse'], 
            enterprise_data['id_ville'], 
            enterprise_data['id_cp'], 
            enterprise_data['id_cedex'],
            enterprise_data['email_principal'], 
            enterprise_data['email_secondaire'], 
            enterprise_data['referent'], 
            enterprise_data['numero_telephone'],
            enterprise_data['numero_portable'], 
            enterprise_data['id_type_entreprise'], 
            enterprise_data['prestations'],
            enterprise_id
        ))
        
        # Supprimer les associations actuelles et les recréer
        cursor.execute("DELETE FROM entreprise_corps_metier WHERE id_entreprise = ?", (enterprise_id,))
        for cm_id in corps_metiers:
            cursor.execute("INSERT INTO entreprise_corps_metier (id_entreprise, id_corps_metier) VALUES (?, ?)", 
                          (enterprise_id, cm_id))
        
        conn.commit()
        return True
    except:
        conn.rollback()
        raise
    finally:
        close_db(conn)

def delete_enterprise(enterprise_id):
    """Supprime une entreprise et ses associations"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # D'abord supprimer les associations avec les corps de métier
        cursor.execute("DELETE FROM entreprise_corps_metier WHERE id_entreprise = ?", (enterprise_id,))
        
        # Ensuite supprimer l'entreprise elle-même
        cursor.execute("DELETE FROM entreprise WHERE id_entreprise = ?", (enterprise_id,))
        
        conn.commit()
        return True
    except:
        conn.rollback()
        raise
    finally:
        close_db(conn)

def search_by_text(search_text):
    """Recherche des entreprises par texte dans différents champs"""
    conn = get_db()
    cursor = conn.cursor()
    
    search_term = f"%{search_text}%"
    
    query = """
    SELECT DISTINCT
        e.id_entreprise,
        e.nom_entreprise,
        e.siret,
        e.adresse || ', ' || 
            COALESCE(cp.code_postal || ' ', '') || 
            COALESCE(v.nom_ville, '') ||
            CASE WHEN e.id_cedex IS NOT NULL THEN ' ' || c.nom_cedex ELSE '' END AS adresse_complete,
        e.email_principal,
        e.email_secondaire,
        e.referent,
        e.numero_telephone,
        e.numero_portable
    FROM entreprise e
    LEFT JOIN villes v ON e.id_ville = v.id_ville
    LEFT JOIN code_postal cp ON e.id_cp = cp.id_cp
    LEFT JOIN cedex c ON e.id_cedex = c.id_cedex
    WHERE e.nom_entreprise LIKE ?
       OR e.siret LIKE ?
       OR e.adresse LIKE ?
       OR v.nom_ville LIKE ?
       OR e.email_principal LIKE ?
       OR e.email_secondaire LIKE ?
       OR e.referent LIKE ?
       OR e.numero_telephone LIKE ?
       OR e.numero_portable LIKE ?
    ORDER BY e.nom_entreprise
    """
 
    try:
        cursor.execute(query, (search_term, search_term, search_term, search_term, search_term, 
                               search_term, search_term, search_term, search_term))
        return cursor.fetchall()
    finally:
        close_db(conn)

def get_or_create_cp(code_postal):
    """Récupère ou crée un code postal et retourne son ID"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id_cp FROM code_postal WHERE code_postal = ?", (code_postal,))
        row = cursor.fetchone()
        
        if row:
            return row["id_cp"]
        else:
            cursor.execute("INSERT INTO code_postal (code_postal) VALUES (?)", (code_postal,))
            conn.commit()
            return cursor.lastrowid
    finally:
        close_db(conn)

def get_enterprises_list():
    """Récupère la liste de toutes les entreprises pour la sélection"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id_entreprise, nom_entreprise, siret
            FROM entreprise
            ORDER BY nom_entreprise
        """)
        return cursor.fetchall()
    finally:
        close_db(conn)

# Nouvelles fonctions à ajouter dans models/entreprise.py

def update_forme_juridique(enterprise_id, forme_juridique):
    """Met à jour la forme juridique d'une entreprise"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE entreprise
            SET forme_juridique = ?
            WHERE id_entreprise = ?
        """, (forme_juridique, enterprise_id))
        conn.commit()
        return True
    except:
        conn.rollback()
        raise
    finally:
        close_db(conn)

def get_chiffres_affaires(enterprise_id):
    """Récupère les chiffres d'affaires d'une entreprise, triés par année décroissante"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Journal de débogage
        print(f"Récupération des CA pour l'entreprise ID: {enterprise_id}")
        
        # Vérifier que enterprise_id est valide
        if not enterprise_id:
            print("ID d'entreprise invalide")
            return {'annees': [], 'montants': []}
            
        try:
            # Convertir en entier si nécessaire
            enterprise_id = int(enterprise_id)
        except (ValueError, TypeError):
            print(f"Impossible de convertir l'ID d'entreprise en entier: {enterprise_id}")
            return {'annees': [], 'montants': []}
        
        cursor.execute("""
            SELECT annee, montant
            FROM chiffre_affaires
            WHERE id_entreprise = ?
            ORDER BY annee DESC
        """, (enterprise_id,))
        
        ca_data = {
            'annees': [],
            'montants': []
        }
        
        rows = cursor.fetchall()
        print(f"Nombre de CA trouvés: {len(rows)}")
        
        for row in rows:
            ca_data['annees'].append(row['annee'])
            ca_data['montants'].append(row['montant'])
        
        # Déjà trié par année décroissante grâce à la requête SQL
        return ca_data
    except Exception as e:
        print(f"Erreur lors de la récupération des CA: {e}")
        return {'annees': [], 'montants': []}
    finally:
        close_db(conn)

def add_or_update_chiffre_affaires(enterprise_id, annee, montant):
    """Ajoute ou met à jour un chiffre d'affaires pour une entreprise et une année donnée"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Vérifier si l'entrée existe déjà
        cursor.execute("""
            SELECT id_ca FROM chiffre_affaires 
            WHERE id_entreprise = ? AND annee = ?
        """, (enterprise_id, annee))
        
        existing = cursor.fetchone()
        
        if existing:
            # Mise à jour - ne pas modifier date_ajout
            cursor.execute("""
                UPDATE chiffre_affaires 
                SET montant = ? 
                WHERE id_entreprise = ? AND annee = ?
            """, (montant, enterprise_id, annee))
        else:
            # Ajout - date_ajout sera automatiquement définie par le CURRENT_TIMESTAMP
            cursor.execute("""
                INSERT INTO chiffre_affaires (id_entreprise, annee, montant, date_ajout)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (enterprise_id, annee, montant))
            
        conn.commit()
        return True
    except Exception as e:
        print(f"Erreur lors de l'enregistrement du CA: {e}")
        conn.rollback()
        raise
    finally:
        close_db(conn)