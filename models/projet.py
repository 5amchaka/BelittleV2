from database import get_db, close_db

def create_projet(identification_operation, id_moa, nom_affaire=None, reference_projet=None, date_notification=None):
    """Crée un nouveau projet"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO projets (identification_operation, id_moa, nom_affaire, reference_projet, date_notification)
            VALUES (?, ?, ?, ?, ?)
        """, (identification_operation, id_moa, nom_affaire, reference_projet, date_notification))
        
        projet_id = cursor.lastrowid
        conn.commit()
        return projet_id
    finally:
        close_db(conn)

def get_projet(id_projet):
    """Récupère un projet avec ses détails"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT p.*, 
                   moa.nom_entreprise as nom_moa,
                   moe.nom_entreprise as nom_moe,
                   mandataire.nom_entreprise as nom_mandataire
            FROM projets p
            LEFT JOIN entreprise moa ON p.id_moa = moa.id_entreprise
            LEFT JOIN entreprise moe ON p.id_moe = moe.id_entreprise
            LEFT JOIN entreprise mandataire ON p.id_moe_mandataire = mandataire.id_entreprise
            WHERE p.id_projet = ?
        """, (id_projet,))
        
        return cursor.fetchone()
    finally:
        close_db(conn)

def get_all_projets():
    """Récupère tous les projets"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT p.id_projet, p.nom_affaire, p.reference_projet, p.identification_operation,
                   p.date_notification, p.statut, moa.nom_entreprise as nom_moa
            FROM projets p
            LEFT JOIN entreprise moa ON p.id_moa = moa.id_entreprise
            ORDER BY p.date_creation DESC
        """)
        
        return cursor.fetchall()
    finally:
        close_db(conn)

def update_projet(id_projet, **kwargs):
    """Met à jour un projet"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Construction dynamique de la requête de mise à jour
        fields = []
        values = []
        
        for field, value in kwargs.items():
            if field in ['identification_operation', 'id_moa', 'id_moe', 'id_moe_mandataire', 
                        'nom_affaire', 'reference_projet', 'date_notification', 'statut']:
                fields.append(f"{field} = ?")
                values.append(value)
        
        if fields:
            values.append(id_projet)
            query = f"UPDATE projets SET {', '.join(fields)} WHERE id_projet = ?"
            cursor.execute(query, values)
            conn.commit()
            return cursor.rowcount > 0
        
        return False
    finally:
        close_db(conn)

def add_moe_cotraitant(id_projet, id_entreprise, est_mandataire=False):
    """Ajoute un MOE co-traitant au projet"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Si c'est un mandataire, retirer le statut de mandataire des autres
        if est_mandataire:
            cursor.execute("""
                UPDATE projet_moe_cotraitants 
                SET est_mandataire = FALSE 
                WHERE id_projet = ?
            """, (id_projet,))
            
            # Mettre à jour le mandataire au niveau projet
            cursor.execute("""
                UPDATE projets 
                SET id_moe_mandataire = ? 
                WHERE id_projet = ?
            """, (id_entreprise, id_projet))
        
        # Ajouter le co-traitant
        cursor.execute("""
            INSERT OR REPLACE INTO projet_moe_cotraitants 
            (id_projet, id_entreprise, est_mandataire)
            VALUES (?, ?, ?)
        """, (id_projet, id_entreprise, est_mandataire))
        
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Erreur lors de l'ajout du MOE co-traitant: {e}")
        return False
    finally:
        close_db(conn)

def get_moe_cotraitants(id_projet):
    """Récupère les MOE co-traitants d'un projet"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT pmc.*, e.nom_entreprise, e.siret
            FROM projet_moe_cotraitants pmc
            JOIN entreprise e ON pmc.id_entreprise = e.id_entreprise
            WHERE pmc.id_projet = ?
            ORDER BY pmc.est_mandataire DESC, e.nom_entreprise
        """, (id_projet,))
        
        return cursor.fetchall()
    finally:
        close_db(conn)

def create_lot(id_projet, numero_lot, objet_marche, montant_initial_ht=0, taux_tva=20.0):
    """Crée un nouveau lot pour un projet"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO lots (id_projet, numero_lot, objet_marche, montant_initial_ht, taux_tva)
            VALUES (?, ?, ?, ?, ?)
        """, (id_projet, numero_lot, objet_marche, montant_initial_ht, taux_tva))
        
        lot_id = cursor.lastrowid
        conn.commit()
        return lot_id
    finally:
        close_db(conn)

def get_lots_by_projet(id_projet):
    """Récupère tous les lots d'un projet"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT * FROM lots 
            WHERE id_projet = ? 
            ORDER BY numero_lot
        """, (id_projet,))
        
        return cursor.fetchall()
    finally:
        close_db(conn)

def get_lot(id_lot):
    """Récupère un lot spécifique"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM lots WHERE id_lot = ?", (id_lot,))
        return cursor.fetchone()
    finally:
        close_db(conn)

def update_lot(id_lot, numero_lot=None, objet_marche=None, montant_initial_ht=None, taux_tva=None):
    """Met à jour un lot"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Construction dynamique de la requête de mise à jour
        fields = []
        values = []
        
        if numero_lot is not None:
            fields.append("numero_lot = ?")
            values.append(numero_lot)
        if objet_marche is not None:
            fields.append("objet_marche = ?")
            values.append(objet_marche)
        if montant_initial_ht is not None:
            fields.append("montant_initial_ht = ?")
            values.append(montant_initial_ht)
        if taux_tva is not None:
            fields.append("taux_tva = ?")
            values.append(taux_tva)
        
        if fields:
            values.append(id_lot)
            query = f"UPDATE lots SET {', '.join(fields)} WHERE id_lot = ?"
            cursor.execute(query, values)
            conn.commit()
            return cursor.rowcount > 0
        
        return False
    finally:
        close_db(conn)

def delete_lot(id_lot):
    """Supprime un lot et toutes ses données associées"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Supprimer le lot (les contraintes CASCADE supprimeront les données liées)
        cursor.execute("DELETE FROM lots WHERE id_lot = ?", (id_lot,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        close_db(conn)

def add_entreprise_to_lot(id_lot, id_entreprise, est_mandataire=False, montant_ht=0, taux_tva=20.0):
    """Ajoute une entreprise à un lot (pour gérer la co-traitance)"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Si c'est un mandataire, retirer le statut de mandataire des autres entreprises du lot
        if est_mandataire:
            cursor.execute("""
                UPDATE lot_entreprises 
                SET est_mandataire = FALSE 
                WHERE id_lot = ?
            """, (id_lot,))
        
        # Ajouter l'entreprise au lot
        cursor.execute("""
            INSERT OR REPLACE INTO lot_entreprises 
            (id_lot, id_entreprise, est_mandataire, montant_ht, taux_tva)
            VALUES (?, ?, ?, ?, ?)
        """, (id_lot, id_entreprise, est_mandataire, montant_ht, taux_tva))
        
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        print(f"Erreur lors de l'ajout de l'entreprise au lot: {e}")
        return None
    finally:
        close_db(conn)

def get_entreprises_by_lot(id_lot):
    """Récupère toutes les entreprises d'un lot"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT le.*, e.nom_entreprise, e.siret, e.adresse, e.email_principal,
                   e.numero_telephone, e.numero_portable, e.referent,
                   v.nom_ville, cp.code_postal, c.nom_cedex, t.nom_type_entreprise
            FROM lot_entreprises le
            JOIN entreprise e ON le.id_entreprise = e.id_entreprise
            LEFT JOIN villes v ON e.id_ville = v.id_ville
            LEFT JOIN code_postal cp ON e.id_cp = cp.id_cp
            LEFT JOIN cedex c ON e.id_cedex = c.id_cedex
            LEFT JOIN type_entreprise t ON e.id_type_entreprise = t.id_type_entreprise
            WHERE le.id_lot = ?
            ORDER BY le.est_mandataire DESC, e.nom_entreprise
        """, (id_lot,))
        
        return cursor.fetchall()
    finally:
        close_db(conn)

def create_avenant(id_lot_entreprise, numero_avenant, objet_avenant, montant_precedent_ht, 
                  montant_nouveau_ht, date_avenant, motif=None, taux_tva=20.0):
    """Crée un nouvel avenant"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO avenants 
            (id_lot_entreprise, numero_avenant, objet_avenant, montant_precedent_ht, 
             montant_nouveau_ht, taux_tva, motif, date_avenant)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (id_lot_entreprise, numero_avenant, objet_avenant, montant_precedent_ht, 
              montant_nouveau_ht, taux_tva, motif, date_avenant))
        
        avenant_id = cursor.lastrowid
        
        # Mettre à jour le montant actuel de l'entreprise dans le lot
        cursor.execute("""
            UPDATE lot_entreprises 
            SET montant_ht = ? 
            WHERE id_lot_entreprise = ?
        """, (montant_nouveau_ht, id_lot_entreprise))
        
        conn.commit()
        return avenant_id
    except Exception as e:
        conn.rollback()
        print(f"Erreur lors de la création de l'avenant: {e}")
        return None
    finally:
        close_db(conn)

def get_avenants_by_lot_entreprise(id_lot_entreprise):
    """Récupère tous les avenants d'une entreprise sur un lot"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT * FROM avenants 
            WHERE id_lot_entreprise = ? 
            ORDER BY numero_avenant
        """, (id_lot_entreprise,))
        
        return cursor.fetchall()
    finally:
        close_db(conn)

def get_montant_actuel_lot_entreprise(id_lot_entreprise):
    """Calcule le montant actuel d'une entreprise sur un lot (montant en cours avec avenants)"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Récupérer le montant actuel (qui est mis à jour à chaque avenant)
        cursor.execute("""
            SELECT montant_ht, taux_tva FROM lot_entreprises 
            WHERE id_lot_entreprise = ?
        """, (id_lot_entreprise,))
        
        result = cursor.fetchone()
        if not result:
            return {'montant_ht': 0, 'montant_ttc': 0, 'taux_tva': 20.0}
        
        montant_ht = result['montant_ht']
        taux_tva = result['taux_tva']
        montant_ttc = montant_ht * (1 + taux_tva / 100)
        
        return {
            'montant_ht': montant_ht,
            'montant_ttc': montant_ttc,
            'taux_tva': taux_tva
        }
    finally:
        close_db(conn)

def get_montant_initial_lot_entreprise(id_lot_entreprise):
    """Récupère le montant initial (avant avenants) d'une entreprise sur un lot"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Récupérer le montant initial depuis la table des lots
        cursor.execute("""
            SELECT le.id_lot_entreprise, l.montant_initial_ht, le.taux_tva,
                   le.montant_ht as montant_attribue_initial
            FROM lot_entreprises le
            JOIN lots l ON le.id_lot = l.id_lot
            WHERE le.id_lot_entreprise = ?
        """, (id_lot_entreprise,))
        
        result = cursor.fetchone()
        if not result:
            return {'montant_ht': 0, 'montant_ttc': 0, 'taux_tva': 20.0}
        
        # Le montant initial de l'entreprise est son montant attribué lors de la première attribution
        # Nous devons vérifier s'il y a eu des avenants pour retrouver le montant de départ
        cursor.execute("""
            SELECT MIN(montant_precedent_ht) as montant_initial
            FROM avenants 
            WHERE id_lot_entreprise = ?
        """, (id_lot_entreprise,))
        
        avenant_result = cursor.fetchone()
        
        if avenant_result and avenant_result['montant_initial'] is not None:
            # Il y a eu des avenants, le montant initial est le montant_precedent du premier avenant
            montant_ht = avenant_result['montant_initial']
        else:
            # Pas d'avenants, le montant actuel est le montant initial
            montant_ht = result['montant_attribue_initial']
        
        taux_tva = result['taux_tva']
        montant_ttc = montant_ht * (1 + taux_tva / 100)
        
        return {
            'montant_ht': montant_ht,
            'montant_ttc': montant_ttc,
            'taux_tva': taux_tva
        }
    finally:
        close_db(conn)

def get_historique_montants_lot_entreprise(id_lot_entreprise):
    """Récupère l'historique complet des montants (initial + avenants)"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Récupérer le montant initial
        cursor.execute("""
            SELECT le.montant_ht as montant_initial, le.taux_tva, le.date_attribution,
                   l.montant_initial_ht, l.numero_lot, l.objet_marche,
                   e.nom_entreprise
            FROM lot_entreprises le
            JOIN lots l ON le.id_lot = l.id_lot
            JOIN entreprise e ON le.id_entreprise = e.id_entreprise
            WHERE le.id_lot_entreprise = ?
        """, (id_lot_entreprise,))
        
        lot_info = cursor.fetchone()
        if not lot_info:
            return None
        
        # Récupérer tous les avenants
        cursor.execute("""
            SELECT * FROM avenants 
            WHERE id_lot_entreprise = ? 
            ORDER BY numero_avenant
        """, (id_lot_entreprise,))
        
        avenants = cursor.fetchall()
        
        return {
            'lot_info': dict(lot_info),
            'avenants': [dict(avenant) for avenant in avenants]
        }
    finally:
        close_db(conn)

def log_document_generation(id_projet, type_document, nom_fichier=None, id_entreprise=None, id_lot=None):
    """Enregistre la génération d'un document"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO projet_documents 
            (id_projet, type_document, nom_fichier, id_entreprise, id_lot)
            VALUES (?, ?, ?, ?, ?)
        """, (id_projet, type_document, nom_fichier, id_entreprise, id_lot))
        
        conn.commit()
        return cursor.lastrowid
    finally:
        close_db(conn)

def get_documents_by_projet(id_projet):
    """Récupère tous les documents générés pour un projet"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT pd.*, e.nom_entreprise, l.numero_lot
            FROM projet_documents pd
            LEFT JOIN entreprise e ON pd.id_entreprise = e.id_entreprise
            LEFT JOIN lots l ON pd.id_lot = l.id_lot
            WHERE pd.id_projet = ?
            ORDER BY pd.date_generation DESC
        """, (id_projet,))
        
        return cursor.fetchall()
    finally:
        close_db(conn)

def delete_projet(id_projet):
    """Supprime un projet et toutes ses données associées"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Grâce aux contraintes CASCADE, supprimer le projet supprimera automatiquement
        # tous les lots, entreprises de lots, avenants, etc.
        cursor.execute("DELETE FROM projets WHERE id_projet = ?", (id_projet,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        close_db(conn)

def get_lot_entreprise(id_lot_entreprise):
    """Récupère les détails d'une association lot-entreprise"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT le.*, e.nom_entreprise, l.numero_lot, l.objet_marche, p.nom_affaire
            FROM lot_entreprises le
            JOIN entreprise e ON le.id_entreprise = e.id_entreprise
            JOIN lots l ON le.id_lot = l.id_lot
            JOIN projets p ON l.id_projet = p.id_projet
            WHERE le.id_lot_entreprise = ?
        """, (id_lot_entreprise,))
        
        return cursor.fetchone()
    finally:
        close_db(conn)

def update_lot_entreprise(id_lot_entreprise, montant_ht, taux_tva, est_mandataire=False):
    """Met à jour les informations d'une entreprise dans un lot"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # D'abord, si on définit cette entreprise comme mandataire, 
        # il faut retirer le statut mandataire des autres entreprises du même lot
        if est_mandataire:
            # Récupérer l'id_lot de cette entreprise
            cursor.execute("SELECT id_lot FROM lot_entreprises WHERE id_lot_entreprise = ?", (id_lot_entreprise,))
            result = cursor.fetchone()
            if result:
                id_lot = result['id_lot']
                # Retirer le statut mandataire des autres entreprises du lot
                cursor.execute("""
                    UPDATE lot_entreprises 
                    SET est_mandataire = FALSE 
                    WHERE id_lot = ? AND id_lot_entreprise != ?
                """, (id_lot, id_lot_entreprise))
        
        # Mettre à jour l'entreprise
        cursor.execute("""
            UPDATE lot_entreprises 
            SET montant_ht = ?, taux_tva = ?, est_mandataire = ?
            WHERE id_lot_entreprise = ?
        """, (montant_ht, taux_tva, est_mandataire, id_lot_entreprise))
        
        conn.commit()
        return cursor.rowcount > 0
    finally:
        close_db(conn)

def remove_entreprise_from_lot(id_lot_entreprise):
    """Supprime une entreprise d'un lot"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM lot_entreprises WHERE id_lot_entreprise = ?", (id_lot_entreprise,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        close_db(conn)