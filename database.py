# database.py - Gestion de la base de données SQLite

import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from logger import get_logger

logger = get_logger(__name__)

# Chemin de la base de données
DB_PATH = os.path.join(os.path.dirname(__file__), "stock_manager.db")


def get_connection():
    """Retourne une connexion à la base de données."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Permet d'accéder aux colonnes par nom
    return conn


def init_database():
    """Initialise le schéma de la base de données."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Table des matières premières / stocks
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code VARCHAR(20) UNIQUE NOT NULL,
            nom VARCHAR(100) NOT NULL,
            quantite INTEGER DEFAULT 0,
            seuil_critique INTEGER DEFAULT 20,
            token_id VARCHAR(50), 
            derniere_mise_a_jour TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table des fournisseurs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fournisseurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom VARCHAR(100) NOT NULL,
            email VARCHAR(255),
            hedera_account_id VARCHAR(50),
            actif BOOLEAN DEFAULT 1,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table des contrats
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contrats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matiere VARCHAR(100) NOT NULL,
            quantite INTEGER NOT NULL,
            prix REAL NOT NULL,
            fournisseur_id INTEGER,
            topic_id VARCHAR(50),
            transaction_id VARCHAR(100),
            hashscan_url VARCHAR(255),
            statut VARCHAR(50) DEFAULT 'EN_ATTENTE',
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_confirmation TIMESTAMP,
            FOREIGN KEY (fournisseur_id) REFERENCES fournisseurs(id)
        )
    ''')
    
    # Table des transactions (paiements)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contrat_id INTEGER,
            type VARCHAR(50) NOT NULL,
            montant REAL,
            transaction_id VARCHAR(100),
            hashscan_url VARCHAR(255),
            statut VARCHAR(50) DEFAULT 'EN_COURS',
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (contrat_id) REFERENCES contrats(id)
        )
    ''')
    
    # Table des alertes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alertes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matiere VARCHAR(100) NOT NULL,
            quantite INTEGER NOT NULL,
            type VARCHAR(50) DEFAULT 'STOCK_CRITIQUE',
            traitee BOOLEAN DEFAULT 0,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_traitement TIMESTAMP
        )
    ''')

    # Table des réservations (NOUVEAU)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ressource VARCHAR(100) NOT NULL,
            demandeur VARCHAR(100),
            date_debut DATE,
            duree_jours INTEGER,
            statut VARCHAR(50) DEFAULT 'CONFIRME',
            transaction_id VARCHAR(100),
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table des taxes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS taxes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_taxe TEXT NOT NULL,
            categorie TEXT NOT NULL,
            montant_fixe REAL,
            unite TEXT
        );
    ''')

    # Table des formulaires
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS formulaires (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_document TEXT NOT NULL UNIQUE,
            cout_standard REAL NOT NULL,
            type_personne TEXT
        );
    ''')
    
    # Table des locations
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type_location TEXT NOT NULL,
            designation TEXT NOT NULL,
            prix_base REAL NOT NULL,
            frequence TEXT
        );
    ''')

    # SEEDING: Insérer les données si les tables sont vides
    
    # 1. TAXES
    cursor.execute("SELECT COUNT(*) FROM taxes")
    if cursor.fetchone()[0] == 0:
        taxes_data = [
            ('Taxe de propreté', 'Personne Morale', 50000.0, 'Annuel'),
            ('Taxe de propreté', 'Personne Physique', 25000.0, 'Annuel'),
            ('Taxe sur la publicité', 'Petit Format', 12000.0, 'Annuel'),
            ('Taxe sur la publicité', 'Grand Format', 15000.0, 'Annuel'),
            ('Taxe sur l\'environnement', 'Général', 0, 'Annuel'),
            ('Taxe sur la pollution', 'Général', 0, 'Annuel'),
            ('Taxe sur la nuisance sonore', 'Général', 0, 'Annuel'),
            ('Taxe sur les loyers', 'Général', 0, 'Annuel'),
            ('Taxe sur les pompes funèbres', 'Service', 0, 'Unitaire'),
            ('Taxe sur le transport', 'Personnes et marchandises', 0, 'Annuel'),
            ('Taxe sur les pylônes de téléphonies', 'Opérateur', 0, 'Annuel'),
            ('Taxe sur les terrassements', 'Projet', 0, 'Unitaire'),
            ('Taxe Box', 'Grand Box (Entreprise)', 150000.0, 'Annuel'),
            ('Taxe Box', 'Grand Box (Commerçant)', 100000.0, 'Annuel'),
            ('Taxe Box', 'Box Moyen', 35000.0, 'Annuel'),
            ('Taxe Box', 'Box Petit', 30000.0, 'Annuel'),
            ('Taxe Box', 'Étal de marché', 6500.0, 'Annuel'),
        ]
        cursor.executemany("INSERT INTO taxes (nom_taxe, categorie, montant_fixe, unite) VALUES (?, ?, ?, ?)", taxes_data)
        logger.info("✅ Taxes par défaut créées")

    # 2. FORMULAIRES
    cursor.execute("SELECT COUNT(*) FROM formulaires")
    if cursor.fetchone()[0] == 0:
        formulaires_data = [
            ('Certificat de résidence', 5000.0, 'Adulte'),
            ('Autorisation parentale de voyager', 5000.0, 'Parentale'),
            ('Autorisation maritale de voyager', 5000.0, 'Maritale'),
            ('Certificat d\'hébergement', 5000.0, 'Général'),
            ('Certificat de transfert de corps', 10000.0, 'Général'),
            ('Certificat de célibat', 5000.0, 'Célibat'),
            ('Certificat de coutume', 5000.0, 'Général'),
            ('Certificat de non remariage', 5000.0, 'Général'),
            ('Procuration', 5000.0, 'Général'),
            ('Certificat de concubinage', 5000.0, 'Général'),
            ('Certificat de fiançailles', 5000.0, 'Général'),
            ('Copie intégrale d\'acte de naissance', 5000.0, 'Général'),
            ('Transcription d\'acte de naissance', 5000.0, 'Général'),
            ('Autorisation provisoire d\'exercer', 15000.0, 'Professionnel'),
            ('Attestation de pouvoirs', 5000.0, 'Général'),
            ('Procès verbal de recherche infructueuse', 5000.0, 'Général'),
            ('Procès verbal de recherche fructueuse', 5000.0, 'Général'),
            ('Certificat de conformité', 5000.0, 'Général'),
            ('Certificat de non conformité', 5000.0, 'Général'),
            ('Certificat de vente (véhicule)', 5000.0, 'Général'),
            ('Attestation de cessation', 5000.0, 'Général'),
            ('Attestation de cession', 5000.0, 'Général'),
        ]
        cursor.executemany("INSERT INTO formulaires (nom_document, cout_standard, type_personne) VALUES (?, ?, ?)", formulaires_data)
        logger.info("✅ Formulaires par défaut créés")
        
    # 3. LOCATIONS
    cursor.execute("SELECT COUNT(*) FROM locations")
    if cursor.fetchone()[0] == 0:
        locations_data = [
            ('Transport', 'Véhicule léger', 10000.0, 'Jour'),
            ('Transport', 'Véhicule lourd', 30000.0, 'Jour'),
            ('Bureaux', 'Petit Bureau', 50000.0, 'Mois'),
            ('Bureaux', 'Grand Bureau', 120000.0, 'Mois'),
            ('Salle de réunion', 'Petite salle (1h)', 15000.0, 'Heure'),
            ('Salle de réunion', 'Grande salle (1/2 journée)', 45000.0, 'Demi-journée'),
        ]
        cursor.executemany("INSERT INTO locations (type_location, designation, prix_base, frequence) VALUES (?, ?, ?, ?)", locations_data)
        logger.info("✅ Locations par défaut créées")
    
    conn.commit()
    conn.close()
    logger.info("✅ Base de données initialisée")


# ==================== STOCKS ====================

def get_all_stocks() -> List[Dict]:
    """Récupère tous les stocks."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stocks ORDER BY nom")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_stock_by_name(nom: str) -> Optional[Dict]:
    """Récupère un stock par son nom."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stocks WHERE LOWER(nom) = LOWER(?)", (nom,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_stock_quantity(nom: str, quantite: int):
    """Met à jour la quantité d'un stock."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE stocks 
        SET quantite = ?, derniere_mise_a_jour = ? 
        WHERE LOWER(nom) = LOWER(?)
    ''', (quantite, datetime.now(), nom))
    conn.commit()
    conn.close()
    logger.debug(f"Stock mis à jour: {nom} = {quantite}")


def get_critical_stocks() -> List[Dict]:
    """Récupère les stocks en dessous du seuil critique."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM stocks 
        WHERE quantite < seuil_critique 
        ORDER BY quantite ASC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def add_stock(code: str, nom: str, quantite: int = 0, seuil: int = 20):
    """Ajoute une nouvelle référence de stock."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO stocks (code, nom, quantite, seuil_critique) 
            VALUES (?, ?, ?, ?)
        ''', (code, nom, quantite, seuil))
        conn.commit()
        logger.info(f"✅ Stock ajouté : {nom}")
    except sqlite3.IntegrityError:
        logger.error(f"❌ Erreur : Le code {code} existe déjà.")
    finally:
        conn.close()


def delete_stock(nom: str):
    """Supprime une référence de stock par son nom."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM stocks WHERE nom = ?", (nom,))
    conn.commit()
    conn.close()
    logger.info(f"🗑️ Stock supprimé : {nom}")


# ==================== CONTRATS ====================

def create_contrat(matiere: str, quantite: int, prix: float, 
                   topic_id: str = None, transaction_id: str = None,
                   hashscan_url: str = None) -> int:
    """Crée un nouveau contrat."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO contrats (matiere, quantite, prix, topic_id, transaction_id, hashscan_url)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (matiere, quantite, prix, topic_id, transaction_id, hashscan_url))
    contrat_id = cursor.lastrowid
    conn.commit()
    conn.close()
    logger.info(f"📄 Contrat créé: ID={contrat_id}, Matière={matiere}")
    return contrat_id


def update_all_taxes(df_taxes):
    """Met à jour toute la table taxes à partir d'un DataFrame."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # On vide la table (attention aux IDs si on veut les garder, mais ici c'est plus simple de remplacer)
        # Mais pour garder l'intégrité, on va plutôt faire des UPDATE ou INSERT
        # Option simple : Truncate + Insert (Reset IDs) ou Replace row by row.
        # Pour une config simple, on remplace tout.
        cursor.execute("DELETE FROM taxes") 
        
        for index, row in df_taxes.iterrows():
            cursor.execute('''
                INSERT INTO taxes (nom_taxe, categorie, montant_fixe, unite)
                VALUES (?, ?, ?, ?)
            ''', (row['nom_taxe'], row['categorie'], row['montant_fixe'], row['unite']))
            
        conn.commit()
    except Exception as e:
        print(f"Erreur update taxes: {e}")
        conn.rollback()
    finally:
        conn.close()

def update_all_formulaires(df_docs):
    """Met à jour toute la table formulaires à partir d'un DataFrame."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM formulaires")
        
        for index, row in df_docs.iterrows():
            cursor.execute('''
                INSERT INTO formulaires (nom_document, cout_standard, type_personne)
                VALUES (?, ?, ?)
            ''', (row['nom_document'], row['cout_standard'], row['type_personne']))
            
        conn.commit()
    except Exception as e:
        print(f"Erreur update formulaires: {e}")
        conn.rollback()
    finally:
        conn.close()

def get_all_contrats() -> List[Dict]:
    """Récupère tous les contrats."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contrats ORDER BY date_creation DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def update_contrat_status(contrat_id: int, statut: str, transaction_id: str = None):
    """Met à jour le statut d'un contrat."""
    conn = get_connection()
    cursor = conn.cursor()
    if transaction_id:
        cursor.execute('''
            UPDATE contrats 
            SET statut = ?, transaction_id = ?, date_confirmation = ?
            WHERE id = ?
        ''', (statut, transaction_id, datetime.now(), contrat_id))
    else:
        cursor.execute("UPDATE contrats SET statut = ? WHERE id = ?", (statut, contrat_id))
    conn.commit()
    conn.close()


# ==================== TRANSACTIONS ====================

def create_transaction(contrat_id: int, type_tx: str, montant: float,
                       transaction_id: str, hashscan_url: str) -> int:
    """Enregistre une transaction (paiement)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO transactions (contrat_id, type, montant, transaction_id, hashscan_url, statut)
        VALUES (?, ?, ?, ?, ?, 'COMPLETE')
    ''', (contrat_id, type_tx, montant, transaction_id, hashscan_url))
    tx_id = cursor.lastrowid
    conn.commit()
    conn.close()
    logger.info(f"💰 Transaction enregistrée: ID={tx_id}, Montant={montant}")
    return tx_id


def get_all_transactions() -> List[Dict]:
    """Récupère toutes les transactions."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT t.*, c.matiere 
        FROM transactions t
        LEFT JOIN contrats c ON t.contrat_id = c.id
        ORDER BY t.date_creation DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# ==================== ALERTES ====================

def create_alerte(matiere: str, quantite: int, type_alerte: str = "STOCK_CRITIQUE") -> int:
    """Crée une nouvelle alerte."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO alertes (matiere, quantite, type)
        VALUES (?, ?, ?)
    ''', (matiere, quantite, type_alerte))
    alerte_id = cursor.lastrowid
    conn.commit()
    conn.close()
    logger.warning(f"🚨 Alerte créée: {type_alerte} - {matiere} ({quantite})")
    return alerte_id


def get_pending_alertes() -> List[Dict]:
    """Récupère les alertes non traitées."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM alertes 
        WHERE traitee = 0 
        ORDER BY date_creation DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def mark_alerte_treated(alerte_id: int):
    """Marque une alerte comme traitée."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE alertes 
        SET traitee = 1, date_traitement = ? 
        WHERE id = ?
    ''', (datetime.now(), alerte_id))
    conn.commit()
    conn.close()

def mark_all_alertes_treated():
    """Marque TOUTES les alertes comme traitées."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE alertes SET traitee = 1, date_traitement = CURRENT_TIMESTAMP WHERE traitee = 0")
    conn.commit()
    conn.close()


# ==================== STATISTIQUES ====================

def get_statistics() -> Dict:
    """Récupère des statistiques globales."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Nombre d'anomalies financières (EXCLUT les stocks)
    cursor.execute('''
        SELECT COUNT(*) FROM alertes 
        WHERE (type = 'CRITIQUE_FINANCIER' OR type = 'ANOMALIE_TAXE' OR type = 'RECETTE_FAIBLE' OR type = 'RETARD_PAIEMENT')
        AND traitee = 0
    ''')
    incidents_critiques = cursor.fetchone()[0]
    
    # On garde aussi les stocks purs pour debug
    cursor.execute("SELECT COUNT(*) FROM stocks WHERE quantite < seuil_critique")
    stocks_critiques = cursor.fetchone()[0]
    
    # Total des contrats
    cursor.execute("SELECT COUNT(*) FROM contrats")
    total_contrats = cursor.fetchone()[0]
    
    # Contrats du jour
    cursor.execute('''
        SELECT COUNT(*) FROM contrats 
        WHERE DATE(date_creation) = DATE('now')
    ''')
    contrats_jour = cursor.fetchone()[0]
    
    # Total des transactions
    cursor.execute("SELECT SUM(montant) FROM transactions WHERE statut = 'COMPLETE'")
    total_paiements = cursor.fetchone()[0] or 0
    
    # Alertes non traitées
    cursor.execute("SELECT COUNT(*) FROM alertes WHERE traitee = 0")
    alertes_pending = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "stocks_critiques": stocks_critiques,
        "incidents_critiques": incidents_critiques,
        "total_contrats": total_contrats,
        "contrats_jour": contrats_jour,
        "total_paiements": total_paiements,
        "alertes_pending": alertes_pending
    }


# ==================== SERVICES MUNICIPAUX (Refactoring) ====================

def get_taxes() -> List[Dict]:
    """Récupère toutes les taxes."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM taxes")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_formulaires() -> List[Dict]:
    """Récupère tous les formulaires/actes."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM formulaires")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_locations() -> List[Dict]:
    """Récupère toutes les locations disponibles."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM locations")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def create_reservation(ressource: str, demandeur: str, date_debut: str, duree: int, transaction_id: str):
    """Crée une réservation."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO reservations (ressource, demandeur, date_debut, duree_jours, transaction_id)
        VALUES (?, ?, ?, ?, ?)
    ''', (ressource, demandeur, date_debut, duree, transaction_id))
    conn.commit()
    conn.close()

def get_reservations() -> List[Dict]:
    """Récupère les réservations."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reservations ORDER BY date_creation DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# Initialiser la base au chargement du module
if __name__ == "__main__":
    init_database()
    print("✅ Base de données initialisée avec succès!")
    print(f"📁 Chemin: {DB_PATH}")
