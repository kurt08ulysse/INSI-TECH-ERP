"""
Configuration pour connexion à un serveur de base de données
PostgreSQL ou MySQL au lieu de SQLite

Pour utiliser ce fichier:
1. Renommer database_mairie.py en database_mairie_sqlite.py
2. Renommer ce fichier en database_mairie.py
3. Configurer les variables dans .env
4. Installer psycopg2-binary OU mysql-connector-python
"""

import os
from typing import List, Dict
from datetime import datetime
from logger import get_logger

logger = get_logger(__name__)

# ==================== CHOIX DU TYPE DE BASE DE DONNEES ====================
DB_TYPE = os.getenv('DB_TYPE', 'postgresql')  # 'postgresql' ou 'mysql' ou 'sqlite'

# ==================== CONFIGURATION ====================

if DB_TYPE == 'postgresql':
    import psycopg2
    from psycopg2.extras import RealDictCursor

    DB_CONFIG = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'database': os.getenv('DB_NAME', 'mairie_db'),
        'user': os.getenv('DB_USER', 'mairie_user'),
        'password': os.getenv('DB_PASSWORD', ''),
        'port': os.getenv('DB_PORT', '5432')
    }

    def get_connection():
        """Retourne une connexion PostgreSQL."""
        conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
        return conn

elif DB_TYPE == 'mysql':
    import mysql.connector

    DB_CONFIG = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'database': os.getenv('DB_NAME', 'mairie_db'),
        'user': os.getenv('DB_USER', 'mairie_user'),
        'password': os.getenv('DB_PASSWORD', ''),
        'port': int(os.getenv('DB_PORT', '3306'))
    }

    def get_connection():
        """Retourne une connexion MySQL."""
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn

else:  # sqlite (par défaut)
    import sqlite3

    DB_PATH = os.path.join(os.path.dirname(__file__), "mairie.db")

    def get_connection():
        """Retourne une connexion SQLite."""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn


# ==================== FONCTIONS UTILITAIRES ====================

def dict_from_row(row):
    """Convertit une ligne en dictionnaire."""
    if DB_TYPE == 'postgresql':
        return dict(row)
    elif DB_TYPE == 'mysql':
        return dict(zip(row.keys(), row))
    else:  # sqlite
        return dict(row)


def test_connection():
    """Test la connexion à la base de données."""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        if DB_TYPE == 'postgresql':
            cursor.execute('SELECT version();')
        elif DB_TYPE == 'mysql':
            cursor.execute('SELECT VERSION();')
        else:
            cursor.execute('SELECT sqlite_version();')

        version = cursor.fetchone()
        conn.close()

        logger.info(f"Connexion reussie a {DB_TYPE}: {version}")
        return True
    except Exception as e:
        logger.error(f"Erreur de connexion a {DB_TYPE}: {e}")
        return False


# ==================== FONCTIONS DE LA BASE DE DONNEES ====================
# Reprendre toutes les fonctions de database_mairie.py ici

def get_taxes() -> List[Dict]:
    """Récupère toutes les taxes."""
    conn = get_connection()
    cursor = conn.cursor()

    if DB_TYPE == 'mysql':
        cursor.execute("SELECT * FROM taxes WHERE actif = 1 ORDER BY nom_taxe, categorie")
        columns = cursor.column_names
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    else:
        cursor.execute("SELECT * FROM taxes WHERE actif = 1 ORDER BY nom_taxe, categorie")
        rows = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return rows


def get_formulaires() -> List[Dict]:
    """Récupère tous les formulaires."""
    conn = get_connection()
    cursor = conn.cursor()

    if DB_TYPE == 'mysql':
        cursor.execute("SELECT * FROM formulaires WHERE actif = 1 ORDER BY nom_document")
        columns = cursor.column_names
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    else:
        cursor.execute("SELECT * FROM formulaires WHERE actif = 1 ORDER BY nom_document")
        rows = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return rows


def get_locations() -> List[Dict]:
    """Récupère toutes les locations."""
    conn = get_connection()
    cursor = conn.cursor()

    if DB_TYPE == 'mysql':
        cursor.execute("SELECT * FROM locations WHERE disponible = 1 ORDER BY type_location, designation")
        columns = cursor.column_names
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    else:
        cursor.execute("SELECT * FROM locations WHERE disponible = 1 ORDER BY type_location, designation")
        rows = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return rows


def create_transaction(type_tx: str, libelle: str, montant: float,
                       citoyen_id: int = None, agent_id: int = None,
                       mode_paiement: str = 'Espèces',
                       transaction_id: str = None, hashscan_url: str = None,
                       nom_commercant: str = None, numero_commercant: str = None) -> int:
    """Crée une transaction de paiement."""
    conn = get_connection()
    cursor = conn.cursor()

    # Générer numéro de reçu unique
    numero_recu = f"REC-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # Construire transaction_id
    if not transaction_id:
        if nom_commercant:
            transaction_id = f"{numero_recu} - {nom_commercant}"
            if numero_commercant:
                transaction_id += f" ({numero_commercant})"
        else:
            transaction_id = numero_recu

    # Adapter la requête selon le type de base de données
    if DB_TYPE == 'postgresql':
        query = '''
            INSERT INTO transactions
            (citoyen_id, agent_id, type, libelle, montant, mode_paiement, numero_recu,
             transaction_id, hashscan_url, statut, nom_commercant, numero_commercant)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'COMPLETE', %s, %s)
            RETURNING id
        '''
        cursor.execute(query, (citoyen_id, agent_id, type_tx, libelle, montant, mode_paiement,
                              numero_recu, transaction_id, hashscan_url, nom_commercant, numero_commercant))
        tx_id = cursor.fetchone()[0]

    elif DB_TYPE == 'mysql':
        query = '''
            INSERT INTO transactions
            (citoyen_id, agent_id, type, libelle, montant, mode_paiement, numero_recu,
             transaction_id, hashscan_url, statut, nom_commercant, numero_commercant)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'COMPLETE', %s, %s)
        '''
        cursor.execute(query, (citoyen_id, agent_id, type_tx, libelle, montant, mode_paiement,
                              numero_recu, transaction_id, hashscan_url, nom_commercant, numero_commercant))
        tx_id = cursor.lastrowid

    else:  # sqlite
        query = '''
            INSERT INTO transactions
            (citoyen_id, agent_id, type, libelle, montant, mode_paiement, numero_recu,
             transaction_id, hashscan_url, statut, nom_commercant, numero_commercant)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'COMPLETE', ?, ?)
        '''
        cursor.execute(query, (citoyen_id, agent_id, type_tx, libelle, montant, mode_paiement,
                              numero_recu, transaction_id, hashscan_url, nom_commercant, numero_commercant))
        tx_id = cursor.lastrowid

    conn.commit()
    conn.close()

    logger.info(f"Transaction creee: {libelle} - {montant} FCFA")
    return tx_id


def get_all_transactions() -> List[Dict]:
    """Récupère toutes les transactions."""
    conn = get_connection()
    cursor = conn.cursor()

    query = 'SELECT * FROM transactions ORDER BY date_creation DESC'

    if DB_TYPE == 'mysql':
        cursor.execute(query)
        columns = cursor.column_names
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    else:
        cursor.execute(query)
        rows = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return rows


def get_statistics() -> Dict:
    """Récupère les statistiques."""
    conn = get_connection()
    cursor = conn.cursor()

    stats = {}

    # Adapter les requêtes selon le type de base de données
    if DB_TYPE in ['postgresql', 'mysql']:
        # Recettes du jour
        cursor.execute("""
            SELECT COALESCE(SUM(montant), 0) as total, COUNT(*) as count
            FROM transactions
            WHERE DATE(date_creation) = CURRENT_DATE AND statut = 'COMPLETE'
        """)
    else:  # sqlite
        cursor.execute("""
            SELECT COALESCE(SUM(montant), 0) as total, COUNT(*) as count
            FROM transactions
            WHERE DATE(date_creation) = DATE('now') AND statut = 'COMPLETE'
        """)

    row = cursor.fetchone()
    stats['recettes_jour'] = float(row[0] if DB_TYPE == 'mysql' else row['total'])
    stats['nb_transactions_jour'] = int(row[1] if DB_TYPE == 'mysql' else row['count'])

    # Recettes du mois
    if DB_TYPE in ['postgresql', 'mysql']:
        cursor.execute("""
            SELECT COALESCE(SUM(montant), 0)
            FROM transactions
            WHERE EXTRACT(MONTH FROM date_creation) = EXTRACT(MONTH FROM CURRENT_DATE)
            AND EXTRACT(YEAR FROM date_creation) = EXTRACT(YEAR FROM CURRENT_DATE)
            AND statut = 'COMPLETE'
        """)
    else:
        cursor.execute("""
            SELECT COALESCE(SUM(montant), 0)
            FROM transactions
            WHERE strftime('%Y-%m', date_creation) = strftime('%Y-%m', 'now')
            AND statut = 'COMPLETE'
        """)

    stats['recettes_mois'] = float(cursor.fetchone()[0])

    # Recettes de l'année
    if DB_TYPE in ['postgresql', 'mysql']:
        cursor.execute("""
            SELECT COALESCE(SUM(montant), 0)
            FROM transactions
            WHERE EXTRACT(YEAR FROM date_creation) = EXTRACT(YEAR FROM CURRENT_DATE)
            AND statut = 'COMPLETE'
        """)
    else:
        cursor.execute("""
            SELECT COALESCE(SUM(montant), 0)
            FROM transactions
            WHERE strftime('%Y', date_creation) = strftime('%Y', 'now')
            AND statut = 'COMPLETE'
        """)

    stats['recettes_annee'] = float(cursor.fetchone()[0])

    # Alertes
    cursor.execute("SELECT COUNT(*) FROM alertes WHERE traitee = 0")
    stats['alertes_pending'] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM alertes WHERE traitee = 0 AND niveau_priorite = 'CRITIQUE'")
    stats['incidents_critiques'] = cursor.fetchone()[0]

    conn.close()
    return stats


# ==================== TEST AU DEMARRAGE ====================

if __name__ == "__main__":
    print(f"Test de connexion a {DB_TYPE}...")
    if test_connection():
        print("Connexion reussie!")

        print("\nTest des requetes:")
        taxes = get_taxes()
        print(f"  - {len(taxes)} taxes trouvees")

        formulaires = get_formulaires()
        print(f"  - {len(formulaires)} formulaires trouves")

        locations = get_locations()
        print(f"  - {len(locations)} locations trouvees")

        stats = get_statistics()
        print(f"  - Recettes du jour: {stats['recettes_jour']:,.0f} FCFA")
    else:
        print("Echec de la connexion!")
