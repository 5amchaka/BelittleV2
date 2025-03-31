"""
Gestionnaire de base de données unifié pour l'application.
Fournit des méthodes communes pour interagir avec la base de données,
indépendamment du moteur sous-jacent (SQLite ou PostgreSQL).
"""
from database_adapter import get_db_adapter

class DatabaseManager:
    """
    Gestionnaire de base de données unifié pour l'application.
    """
    
    def __init__(self):
        self.adapter = get_db_adapter()
    
    def get_db(self):
        """
        Établit une connexion à la base de données et retourne la connexion.
        """
        return self.adapter.get_connection()
    
    def close_db(self, conn):
        """
        Ferme la connexion à la base de données.
        """
        self.adapter.close_connection(conn)
    
    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False, commit=False):
        """
        Exécute une requête SQL et retourne le résultat approprié.
        
        Args:
            query (str): Requête SQL à exécuter
            params (tuple, optional): Paramètres de la requête. Defaults to None.
            fetch_one (bool, optional): Si True, retourne un seul résultat. Defaults to False.
            fetch_all (bool, optional): Si True, retourne tous les résultats. Defaults to False.
            commit (bool, optional): Si True, effectue un commit après l'exécution. Defaults to False.
            
        Returns:
            dict, list, or None: Résultat de la requête selon les paramètres
        """
        conn = None
        try:
            conn = self.get_db()
            cursor = self.adapter.get_cursor(conn)
            
            # Adapter la requête au moteur de base de données
            adapted_query = self.adapter.adapt_query(query)
            
            # Exécuter la requête avec les paramètres
            if params:
                cursor.execute(adapted_query, params)
            else:
                cursor.execute(adapted_query)
            
            # Récupérer les résultats selon les flags
            result = None
            if fetch_one:
                result = cursor.fetchone()
            elif fetch_all:
                result = cursor.fetchall()
            
            # Commit si demandé
            if commit:
                conn.commit()
            
            return result
        except Exception as e:
            if conn and commit:
                conn.rollback()
            raise e
        finally:
            if conn:
                self.close_db(conn)
    
    def insert(self, table, data, returning=None):
        """
        Insère des données dans une table et retourne l'ID généré.
        
        Args:
            table (str): Nom de la table
            data (dict): Données à insérer (clé=nom de colonne, valeur=valeur)
            returning (str, optional): Colonne à retourner après insertion. Defaults to None.
            
        Returns:
            int: ID de la ligne insérée ou autre valeur retournée
        """
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        values = tuple(data.values())
        
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        if returning:
            # Pour PostgreSQL
            query += f" RETURNING {returning}"
        
        conn = None
        try:
            conn = self.get_db()
            cursor = self.adapter.get_cursor(conn)
            
            # Adapter la requête au moteur de base de données
            adapted_query = self.adapter.adapt_query(query)
            
            cursor.execute(adapted_query, values)
            
            if returning:
                result = cursor.fetchone()[0]
            else:
                result = cursor.lastrowid
            
            conn.commit()
            return result
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                self.close_db(conn)
    
    def update(self, table, data, condition, condition_params):
        """
        Met à jour des données dans une table.
        
        Args:
            table (str): Nom de la table
            data (dict): Données à mettre à jour (clé=nom de colonne, valeur=valeur)
            condition (str): Condition WHERE (ex: "id = ?")
            condition_params (tuple): Paramètres de la condition
            
        Returns:
            bool: True si succès, False sinon
        """
        set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
        values = tuple(data.values()) + condition_params
        
        query = f"UPDATE {table} SET {set_clause} WHERE {condition}"
        
        return self.execute_query(query, values, commit=True) is not None
    
    def delete(self, table, condition, condition_params):
        """
        Supprime des données d'une table.
        
        Args:
            table (str): Nom de la table
            condition (str): Condition WHERE (ex: "id = ?")
            condition_params (tuple): Paramètres de la condition
            
        Returns:
            bool: True si succès, False sinon
        """
        query = f"DELETE FROM {table} WHERE {condition}"
        
        return self.execute_query(query, condition_params, commit=True) is not None