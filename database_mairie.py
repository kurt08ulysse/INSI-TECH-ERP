# database_mairie.py - Gestion de la base de données pour la MAIRIE
# Application: Système de Gestion des Recettes Municipales avec Blockchain

import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from logger import get_logger

logger = get_logger(__name__)

# Chemin de la base de données
DB_PATH = os.path.join(os.path.dirname(__file__), "mairie.db")


def get_connection():
    """Retourne une connexion à la base de données."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def migrate_database():
    """Applique les migrations nécessaires à la base de données."""
    conn = get_connection()
    cursor = conn.cursor()

    # Migration: Ajouter les colonnes nom_commercant et numero_commercant si elles n'existent pas
    try:
        cursor.execute("SELECT nom_commercant FROM transactions LIMIT 1")
    except sqlite3.OperationalError:
        logger.info("Migration: Ajout des colonnes nom_commercant et numero_commercant")
        cursor.execute("ALTER TABLE transactions ADD COLUMN nom_commercant VARCHAR(200)")
        cursor.execute("ALTER TABLE transactions ADD COLUMN numero_commercant VARCHAR(50)")
        conn.commit()
        logger.info("✅ Migration terminée: colonnes merchant ajoutées")

    conn.close()


def init_database():
    """Initialise le schéma de la base de données pour la MAIRIE."""
    conn = get_connection()
    cursor = conn.cursor()

    # ==================== TABLES PRINCIPALES ====================

    # 1. CITOYENS / CONTRIBUABLES
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS citoyens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_contribuable VARCHAR(20) UNIQUE,
            nom VARCHAR(100) NOT NULL,
            prenom VARCHAR(100) NOT NULL,
            telephone VARCHAR(20),
            email VARCHAR(255),
            adresse TEXT,
            type_personne VARCHAR(20) DEFAULT 'Physique',
            date_inscription TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 2. AGENTS MUNICIPAUX
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matricule VARCHAR(20) UNIQUE NOT NULL,
            nom VARCHAR(100) NOT NULL,
            prenom VARCHAR(100) NOT NULL,
            service VARCHAR(100),
            fonction VARCHAR(100),
            actif BOOLEAN DEFAULT 1,
            date_embauche TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 3. TAXES MUNICIPALES
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS taxes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_taxe TEXT NOT NULL,
            categorie TEXT NOT NULL,
            montant_fixe REAL,
            taux_pourcentage REAL,
            unite TEXT,
            description TEXT,
            actif BOOLEAN DEFAULT 1
        )
    ''')

    # 4. FORMULAIRES / ACTES ADMINISTRATIFS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS formulaires (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_document TEXT NOT NULL UNIQUE,
            cout_standard REAL NOT NULL,
            type_personne TEXT,
            delai_traitement_jours INTEGER DEFAULT 3,
            description TEXT,
            actif BOOLEAN DEFAULT 1
        )
    ''')

    # 5. LOCATIONS MUNICIPALES
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type_location TEXT NOT NULL,
            designation TEXT NOT NULL,
            prix_base REAL NOT NULL,
            frequence TEXT,
            description TEXT,
            capacite INTEGER,
            disponible BOOLEAN DEFAULT 1
        )
    ''')

    # 6. TRANSACTIONS / PAIEMENTS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            citoyen_id INTEGER,
            agent_id INTEGER,
            type VARCHAR(50) NOT NULL,
            libelle TEXT NOT NULL,
            montant REAL NOT NULL,
            mode_paiement VARCHAR(50) DEFAULT 'Espèces',
            numero_recu VARCHAR(50) UNIQUE,
            transaction_id VARCHAR(100),
            hashscan_url VARCHAR(255),
            statut VARCHAR(50) DEFAULT 'COMPLETE',
            nom_commercant VARCHAR(200),
            numero_commercant VARCHAR(50),
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (citoyen_id) REFERENCES citoyens(id),
            FOREIGN KEY (agent_id) REFERENCES agents(id)
        )
    ''')

    # 7. RÉSERVATIONS (Salles, véhicules, etc.)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_id INTEGER NOT NULL,
            citoyen_id INTEGER,
            demandeur VARCHAR(100) NOT NULL,
            date_debut DATE NOT NULL,
            date_fin DATE NOT NULL,
            duree_jours INTEGER,
            montant_total REAL,
            statut VARCHAR(50) DEFAULT 'CONFIRMEE',
            transaction_id VARCHAR(100),
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (location_id) REFERENCES locations(id),
            FOREIGN KEY (citoyen_id) REFERENCES citoyens(id)
        )
    ''')

    # 8. ALERTES FINANCIÈRES
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alertes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre VARCHAR(200) NOT NULL,
            description TEXT,
            type VARCHAR(50) DEFAULT 'FINANCIERE',
            montant REAL,
            niveau_priorite VARCHAR(20) DEFAULT 'NORMAL',
            traitee BOOLEAN DEFAULT 0,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_traitement TIMESTAMP
        )
    ''')

    # 9. SERVICES MUNICIPAUX
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS services_municipaux (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_service VARCHAR(100) NOT NULL UNIQUE,
            responsable_id INTEGER,
            budget_annuel REAL,
            description TEXT,
            actif BOOLEAN DEFAULT 1,
            FOREIGN KEY (responsable_id) REFERENCES agents(id)
        )
    ''')

    # 10. HISTORIQUE / AUDIT
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id INTEGER,
            action VARCHAR(100) NOT NULL,
            table_concernee VARCHAR(50),
            details TEXT,
            date_action TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (agent_id) REFERENCES agents(id)
        )
    ''')

    # ==================== SEEDING DES DONNÉES ====================

    # 1. TAXES
    cursor.execute("SELECT COUNT(*) FROM taxes")
    if cursor.fetchone()[0] == 0:
        taxes_data = [
            # Taxe de propreté
            ('Taxe de propreté', 'Personne Morale', 50000.0, None, 'Annuel', 'Taxe annuelle pour les entreprises', 1),
            ('Taxe de propreté', 'Personne Physique', 25000.0, None, 'Annuel', 'Taxe annuelle pour les particuliers', 1),

            # Taxe sur la publicité
            ('Taxe sur la publicité', 'Petit Format', 12000.0, None, 'Annuel', 'Panneau publicitaire petit format', 1),
            ('Taxe sur la publicité', 'Grand Format', 15000.0, None, 'Annuel', 'Panneau publicitaire grand format', 1),

            # Taxe des box
            ('Taxe des Box', 'Grand Box - Entreprise', 150000.0, None, 'Annuel', 'Box commercial grand format entreprise', 1),
            ('Taxe des Box', 'Grand Box - Commerçant', 100000.0, None, 'Annuel', 'Box commercial grand format commerçant', 1),
            ('Taxe des Box', 'Moyen Box', 35000.0, None, 'Annuel', 'Box commercial moyen', 1),
            ('Taxe des Box', 'Petit Box', 30000.0, None, 'Annuel', 'Box commercial petit', 1),

            # Étal de marché
            ('Étal de marché', 'Quotidien', 6500.0, None, 'Journalier', 'Étal sur le marché municipal', 1),

            # Taxe sur les loyers
            ('Taxe sur les loyers', 'Général', None, 10.0, 'Mensuel', '10% du montant du loyer', 1),

            # Taxes environnementales
            ('Taxe sur l\'environnement', 'Standard', 20000.0, None, 'Annuel', 'Taxe pour la protection de l\'environnement', 1),
            ('Taxe sur la pollution', 'Entreprise', 100000.0, None, 'Annuel', 'Taxe anti-pollution pour entreprises', 1),
            ('Taxe sur la pollution', 'Commerce', 50000.0, None, 'Annuel', 'Taxe anti-pollution pour commerces', 1),
            ('Taxe sur la nuisance sonore', 'Bars/Restaurants', 75000.0, None, 'Annuel', 'Taxe pour nuisances sonores', 1),
            ('Taxe sur l\'insalubrité', 'Standard', 30000.0, None, 'Annuel', 'Taxe sur les lieux insalubres', 1),

            # Taxe sur les pompes funèbres
            ('Taxe sur les pompes funèbres', 'Standard', 50000.0, None, 'Annuel', 'Taxe pour services funéraires', 1),

            # Taxe sur le transport
            ('Taxe sur le transport', 'Personnes - Taxi', 40000.0, None, 'Annuel', 'Taxe transport de personnes (taxi)', 1),
            ('Taxe sur le transport', 'Personnes - Bus', 80000.0, None, 'Annuel', 'Taxe transport de personnes (bus)', 1),
            ('Taxe sur le transport', 'Marchandises - Léger', 50000.0, None, 'Annuel', 'Taxe transport marchandises véhicule léger', 1),
            ('Taxe sur le transport', 'Marchandises - Lourd', 100000.0, None, 'Annuel', 'Taxe transport marchandises véhicule lourd', 1),

            # Taxe sur les pylônes
            ('Taxe sur les pylônes de téléphonie', 'Standard', 500000.0, None, 'Annuel', 'Taxe pour installation pylône télécom', 1),

            # Taxe sur les terrassements
            ('Taxe sur les terrassements', 'Petit chantier', 150000.0, None, 'Par projet', 'Terrassement < 100m²', 1),
            ('Taxe sur les terrassements', 'Grand chantier', 300000.0, None, 'Par projet', 'Terrassement > 100m²', 1),

            # Taxe sur les grands panneaux lumineux
            ('Taxe sur les grands panneaux lumineux', 'Standard', 200000.0, None, 'Annuel', 'Panneau publicitaire lumineux grand format', 1),
        ]
        cursor.executemany(
            "INSERT INTO taxes (nom_taxe, categorie, montant_fixe, taux_pourcentage, unite, description, actif) VALUES (?, ?, ?, ?, ?, ?, ?)",
            taxes_data
        )
        logger.info("✅ Taxes par défaut créées")

    # 2. FORMULAIRES (Attestations/Certificats)
    cursor.execute("SELECT COUNT(*) FROM formulaires")
    if cursor.fetchone()[0] == 0:
        formulaires_data = [
            # Certificats de résidence et voyage
            ('Certificat de résidence', 5000.0, 'Adulte', 1, 'Atteste du domicile actuel', 1),
            ('Autorisation parentale de voyager', 5000.0, 'Mineur', 1, 'Autorisation pour voyage de mineur', 1),
            ('Autorisation maritale de voyager', 5000.0, 'Marié(e)', 1, 'Autorisation du conjoint pour voyager', 1),

            # Certificats d'hébergement et état civil
            ('Certificat d\'hébergement', 5000.0, 'Général', 2, 'Atteste qu\'une personne est hébergée', 1),
            ('Certificat de transfert de corps', 10000.0, 'Général', 1, 'Autorisation de transfert de corps défunt', 1),
            ('Certificat de célibat', 5000.0, 'Célibataire', 2, 'Atteste du statut de célibataire', 1),
            ('Certificat de coutume', 5000.0, 'Général', 2, 'Certificat selon coutumes locales', 1),
            ('Certificat de non remariage', 5000.0, 'Général', 2, 'Atteste qu\'une personne ne s\'est pas remariée', 1),
            ('Certificat de concubinage', 5000.0, 'Couple', 2, 'Atteste de la vie en concubinage', 1),
            ('Certificat de fiançailles', 5000.0, 'Couple', 1, 'Atteste de l\'engagement de fiançailles', 1),

            # Actes de naissance
            ('Copie intégrale d\'acte de naissance', 5000.0, 'Général', 1, 'Copie complète acte de naissance', 1),
            ('Extrait d\'acte de naissance', 3000.0, 'Général', 1, 'Extrait acte de naissance', 1),
            ('Transcription d\'acte de naissance', 10000.0, 'Général', 3, 'Transcription acte étranger', 1),

            # Procurations et autorisations
            ('Procuration', 5000.0, 'Général', 1, 'Donne pouvoir à une tierce personne', 1),
            ('Attestation de pouvoirs', 8000.0, 'Professionnel', 2, 'Atteste des pouvoirs d\'un représentant', 1),
            ('Autorisation provisoire d\'exercer', 15000.0, 'Professionnel', 5, 'Autorisation temporaire activité pro', 1),

            # Procès verbaux
            ('Procès verbal de recherche infructueuse', 10000.0, 'Général', 3, 'PV attestant d\'une recherche sans résultat', 1),
            ('Procès verbal de recherche fructueuse', 10000.0, 'Général', 3, 'PV attestant d\'une recherche réussie', 1),

            # Certificats de conformité
            ('Certificat de conformité', 5000.0, 'Général', 3, 'Atteste de la conformité d\'un bien', 1),
            ('Certificat de non conformité', 5000.0, 'Général', 3, 'Atteste de la non conformité', 1),

            # Certificats véhicules et cessions
            ('Certificat de vente (véhicule)', 8000.0, 'Automobile', 2, 'Certificat pour vente de véhicule', 1),
            ('Attestation de cessation', 5000.0, 'Professionnel', 2, 'Atteste de la cessation d\'activité', 1),
            ('Attestation de cession', 5000.0, 'Professionnel', 2, 'Atteste d\'une cession d\'activité/bien', 1),

            # Conventions
            ('Convention commerçant', 20000.0, 'Commerçant', 5, 'Convention avec la mairie pour commerçant', 1),
            ('Convention entreprise', 50000.0, 'Entreprise', 7, 'Convention avec la mairie pour entreprise', 1),
        ]
        cursor.executemany(
            "INSERT INTO formulaires (nom_document, cout_standard, type_personne, delai_traitement_jours, description, actif) VALUES (?, ?, ?, ?, ?, ?)",
            formulaires_data
        )
        logger.info("✅ Formulaires par défaut créés")

    # 3. LOCATIONS
    cursor.execute("SELECT COUNT(*) FROM locations")
    if cursor.fetchone()[0] == 0:
        locations_data = [
            # Location transport
            ('Transport', 'Véhicule léger (4 places)', 25000.0, 'Jour', 'Voiture municipale légère pour déplacements', 4, 1),
            ('Transport', 'Véhicule moyen (7 places)', 35000.0, 'Jour', 'Véhicule familial 7 places', 7, 1),
            ('Transport', 'Minibus (15 places)', 50000.0, 'Jour', 'Minibus pour groupes', 15, 1),
            ('Transport', 'Bus (30 places)', 80000.0, 'Jour', 'Grand bus pour événements', 30, 1),
            ('Transport', 'Camionnette marchandises', 40000.0, 'Jour', 'Camionnette pour transport marchandises', 3, 1),

            # Location bureaux
            ('Bureau', 'Petit Bureau (10m²)', 50000.0, 'Mois', 'Bureau individuel ou association', 2, 1),
            ('Bureau', 'Bureau Moyen (20m²)', 80000.0, 'Mois', 'Bureau pour petite équipe', 4, 1),
            ('Bureau', 'Grand Bureau (30m²)', 120000.0, 'Mois', 'Bureau spacieux pour équipe', 6, 1),
            ('Bureau', 'Bureau Premium (50m²)', 200000.0, 'Mois', 'Grand bureau tout équipé', 10, 1),

            # Location salles de réunion
            ('Salle de réunion', 'Petite salle (1 heure)', 15000.0, 'Heure', 'Salle 10 personnes max', 10, 1),
            ('Salle de réunion', 'Salle moyenne (1 heure)', 25000.0, 'Heure', 'Salle 20 personnes', 20, 1),
            ('Salle de réunion', 'Grande salle (1 heure)', 40000.0, 'Heure', 'Salle 50 personnes', 50, 1),
            ('Salle de réunion', 'Salle réunion (demi-journée)', 80000.0, 'Demi-journée', 'Salle équipée demi-journée', 30, 1),
            ('Salle de réunion', 'Salle réunion (journée complète)', 150000.0, 'Jour', 'Salle équipée journée complète', 30, 1),
            ('Salle de réunion', 'Salle des fêtes (journée)', 200000.0, 'Jour', 'Grande salle événements 200 personnes', 200, 1),
            ('Salle de réunion', 'Salle de conférence (journée)', 250000.0, 'Jour', 'Salle de conférence équipée 100 personnes', 100, 1),
        ]
        cursor.executemany(
            "INSERT INTO locations (type_location, designation, prix_base, frequence, description, capacite, disponible) VALUES (?, ?, ?, ?, ?, ?, ?)",
            locations_data
        )
        logger.info("✅ Locations par défaut créées")

    # 4. AGENTS (Exemples)
    cursor.execute("SELECT COUNT(*) FROM agents")
    if cursor.fetchone()[0] == 0:
        agents_data = [
            ('AG001', 'KOUADIO', 'Jean', 'Finances', 'Trésorier Municipal', 1),
            ('AG002', 'TRAORE', 'Aminata', 'État Civil', 'Chef Service État Civil', 1),
            ('AG003', 'YAO', 'Kouassi', 'Guichet', 'Agent Guichet', 1),
        ]
        cursor.executemany(
            "INSERT INTO agents (matricule, nom, prenom, service, fonction, actif) VALUES (?, ?, ?, ?, ?, ?)",
            agents_data
        )
        logger.info("✅ Agents par défaut créés")

    # 5. SERVICES MUNICIPAUX
    cursor.execute("SELECT COUNT(*) FROM services_municipaux")
    if cursor.fetchone()[0] == 0:
        services_data = [
            ('Finances et Trésorerie', None, 50000000.0, 'Gestion des recettes et dépenses', 1),
            ('État Civil', None, 10000000.0, 'Actes et certificats', 1),
            ('Urbanisme', None, 30000000.0, 'Permis et autorisations', 1),
            ('Services Techniques', None, 40000000.0, 'Entretien et travaux', 1),
        ]
        cursor.executemany(
            "INSERT INTO services_municipaux (nom_service, responsable_id, budget_annuel, description, actif) VALUES (?, ?, ?, ?, ?)",
            services_data
        )
        logger.info("✅ Services municipaux créés")

    conn.commit()
    conn.close()
    logger.info("✅ Base de données MAIRIE initialisée")

    # Appliquer les migrations
    migrate_database()


# ==================== FONCTIONS MÉTIER ====================

def get_all_transactions() -> List[Dict]:
    """Récupère toutes les transactions."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT
            t.*,
            c.nom || ' ' || c.prenom as nom_citoyen,
            a.nom || ' ' || a.prenom as nom_agent
        FROM transactions t
        LEFT JOIN citoyens c ON t.citoyen_id = c.id
        LEFT JOIN agents a ON t.agent_id = a.id
        ORDER BY t.date_creation DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


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

    # Si aucune transaction_id explicite fournie, construire une référence lisible
    # combinant le numéro de reçu et, si disponible, le nom du commerçant/demandeur
    transaction_id_value = transaction_id
    if not transaction_id_value:
        if nom_commercant:
            transaction_id_value = f"{numero_recu} - {nom_commercant}{' (' + str(numero_commercant) + ')' if numero_commercant else ''}"
        else:
            transaction_id_value = numero_recu

    cursor.execute('''
        INSERT INTO transactions
        (citoyen_id, agent_id, type, libelle, montant, mode_paiement, numero_recu, transaction_id, hashscan_url, statut, nom_commercant, numero_commercant)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'COMPLETE', ?, ?)
    ''', (citoyen_id, agent_id, type_tx, libelle, montant, mode_paiement, numero_recu, transaction_id_value, hashscan_url, nom_commercant, numero_commercant))

    tx_id = cursor.lastrowid
    conn.commit()
    conn.close()
    logger.info(f"💰 Transaction créée: {libelle} - {montant} FCFA")
    return tx_id


def get_statistics() -> Dict:
    """Récupère les statistiques de la mairie."""
    conn = get_connection()
    cursor = conn.cursor()

    # Total recettes du jour
    cursor.execute('''
        SELECT COALESCE(SUM(montant), 0) FROM transactions
        WHERE DATE(date_creation) = DATE('now') AND statut = 'COMPLETE'
    ''')
    recettes_jour = cursor.fetchone()[0]

    # Total recettes du mois
    cursor.execute('''
        SELECT COALESCE(SUM(montant), 0) FROM transactions
        WHERE strftime('%Y-%m', date_creation) = strftime('%Y-%m', 'now') AND statut = 'COMPLETE'
    ''')
    recettes_mois = cursor.fetchone()[0]

    # Total recettes année
    cursor.execute('''
        SELECT COALESCE(SUM(montant), 0) FROM transactions
        WHERE strftime('%Y', date_creation) = strftime('%Y', 'now') AND statut = 'COMPLETE'
    ''')
    recettes_annee = cursor.fetchone()[0]

    # Alertes non traitées
    cursor.execute("SELECT COUNT(*) FROM alertes WHERE traitee = 0")
    alertes_pending = cursor.fetchone()[0]

    # Anomalies critiques
    cursor.execute('''
        SELECT COUNT(*) FROM alertes
        WHERE niveau_priorite = 'CRITIQUE' AND traitee = 0
    ''')
    incidents_critiques = cursor.fetchone()[0]

    # Nombre de transactions aujourd'hui
    cursor.execute('''
        SELECT COUNT(*) FROM transactions
        WHERE DATE(date_creation) = DATE('now')
    ''')
    nb_transactions_jour = cursor.fetchone()[0]

    conn.close()

    return {
        "recettes_jour": recettes_jour,
        "recettes_mois": recettes_mois,
        "recettes_annee": recettes_annee,
        "alertes_pending": alertes_pending,
        "incidents_critiques": incidents_critiques,
        "nb_transactions_jour": nb_transactions_jour
    }


def get_taxes() -> List[Dict]:
    """Récupère toutes les taxes actives."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM taxes WHERE actif = 1 ORDER BY nom_taxe, categorie")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_formulaires() -> List[Dict]:
    """Récupère tous les formulaires actifs."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM formulaires WHERE actif = 1 ORDER BY nom_document")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_locations() -> List[Dict]:
    """Récupère toutes les locations disponibles."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM locations WHERE disponible = 1 ORDER BY type_location, designation")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def create_alerte(titre: str, description: str = None, type_alerte: str = "FINANCIERE",
                  montant: float = None, niveau: str = "NORMAL", reference: str = None) -> int:
    """Crée une alerte."""
    conn = get_connection()
    cursor = conn.cursor()
    # Si une référence fournie, l'ajouter à la description pour traçabilité
    full_description = description or ''
    if reference:
        if full_description:
            full_description = f"{full_description}\nRef: {reference}"
        else:
            full_description = f"Ref: {reference}"

    cursor.execute('''
        INSERT INTO alertes (titre, description, type, montant, niveau_priorite)
        VALUES (?, ?, ?, ?, ?)
    ''', (titre, full_description, type_alerte, montant, niveau))
    alerte_id = cursor.lastrowid
    conn.commit()
    conn.close()
    logger.warning(f"🚨 Alerte créée: {titre}")
    return alerte_id


def get_pending_alertes() -> List[Dict]:
    """Récupère les alertes non traitées."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM alertes
        WHERE traitee = 0
        ORDER BY niveau_priorite DESC, date_creation DESC
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
    """Marque toutes les alertes comme traitées."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE alertes SET traitee = 1, date_traitement = CURRENT_TIMESTAMP WHERE traitee = 0")
    conn.commit()
    conn.close()


def update_all_taxes(df_taxes):
    """Met à jour toutes les taxes."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM taxes")
        for _, row in df_taxes.iterrows():
            cursor.execute('''
                INSERT INTO taxes (nom_taxe, categorie, montant_fixe, taux_pourcentage, unite, description, actif)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (row['nom_taxe'], row['categorie'], row.get('montant_fixe'),
                  row.get('taux_pourcentage'), row['unite'], row.get('description', ''), 1))
        conn.commit()
    except Exception as e:
        logger.error(f"Erreur update taxes: {e}")
        conn.rollback()
    finally:
        conn.close()


def update_all_formulaires(df_docs):
    """Met à jour tous les formulaires."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM formulaires")
        for _, row in df_docs.iterrows():
            cursor.execute('''
                INSERT INTO formulaires (nom_document, cout_standard, type_personne, delai_traitement_jours, description, actif)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (row['nom_document'], row['cout_standard'], row.get('type_personne'),
                  row.get('delai_traitement_jours', 3), row.get('description', ''), 1))
        conn.commit()
    except Exception as e:
        logger.error(f"Erreur update formulaires: {e}")
        conn.rollback()
    finally:
        conn.close()


# Initialiser la base au chargement du module
if __name__ == "__main__":
    init_database()
    print("✅ Base de données MAIRIE initialisée avec succès!")
    print(f"📁 Chemin: {DB_PATH}")
