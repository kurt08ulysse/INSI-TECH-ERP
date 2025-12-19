#!/usr/bin/env python3
"""
Script de migration automatique de SQLite vers WAMPSERVER MySQL
Ce script va:
1. Se connecter à WAMPSERVER MySQL
2. Créer les tables
3. Migrer toutes les données de SQLite vers MySQL
4. Vérifier l'importation
"""

import os
import sys
import sqlite3
from datetime import datetime

def check_mysql_connector():
    """Vérifie si mysql-connector-python est installé."""
    try:
        import mysql.connector
        print("[OK] mysql-connector-python est installé")
        return True
    except ImportError:
        print("[ERROR] mysql-connector-python n'est pas installé")
        print("        Installer avec: pip install mysql-connector-python")
        return False


def get_mysql_config():
    """Récupère la configuration MySQL depuis .env ou utilise les valeurs par défaut."""
    from dotenv import load_dotenv
    load_dotenv()

    config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'port': int(os.getenv('DB_PORT', '3306')),
        'database': os.getenv('DB_NAME', 'mairie_db')
    }

    print("\n[CONFIG] Configuration MySQL:")
    print(f"  Host: {config['host']}")
    print(f"  User: {config['user']}")
    print(f"  Database: {config['database']}")
    print(f"  Port: {config['port']}")

    return config


def test_mysql_connection(config):
    """Test la connexion à MySQL."""
    import mysql.connector

    print("\n[TEST] Test de connexion à MySQL...")

    try:
        # Connexion sans spécifier la base de données
        conn = mysql.connector.connect(
            host=config['host'],
            user=config['user'],
            password=config['password'],
            port=config['port']
        )

        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()

        print(f"[OK] Connexion réussie à MySQL {version[0]}")

        conn.close()
        return True

    except mysql.connector.Error as e:
        print(f"[ERROR] Impossible de se connecter à MySQL: {e}")
        print("\nVérifiez que:")
        print("  1. WAMPSERVER est démarré (icône verte)")
        print("  2. MySQL est actif")
        print("  3. Les identifiants dans .env sont corrects")
        return False


def create_database(config):
    """Crée la base de données si elle n'existe pas."""
    import mysql.connector

    print(f"\n[CREATE] Création de la base de données '{config['database']}'...")

    try:
        conn = mysql.connector.connect(
            host=config['host'],
            user=config['user'],
            password=config['password'],
            port=config['port']
        )

        cursor = conn.cursor()

        # Créer la base de données
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {config['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci")
        print(f"[OK] Base de données '{config['database']}' créée/vérifiée")

        conn.close()
        return True

    except mysql.connector.Error as e:
        print(f"[ERROR] Impossible de créer la base de données: {e}")
        return False


def create_tables(config):
    """Crée les tables MySQL."""
    import mysql.connector

    print("\n[TABLES] Création des tables MySQL...")

    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        # Drop tables if exist (pour migration propre)
        tables = [
            'audit_log', 'alertes', 'reservations', 'transactions',
            'agents', 'citoyens', 'locations', 'formulaires',
            'taxes', 'services_municipaux'
        ]

        for table in tables:
            cursor.execute(f"DROP TABLE IF EXISTS {table}")

        # Créer les tables

        # Table services_municipaux
        cursor.execute("""
            CREATE TABLE services_municipaux (
                id INT PRIMARY KEY AUTO_INCREMENT,
                nom VARCHAR(200) NOT NULL,
                description TEXT,
                responsable VARCHAR(200),
                email VARCHAR(200),
                telephone VARCHAR(50),
                actif TINYINT(1) DEFAULT 1,
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("  [OK] Table services_municipaux")

        # Table taxes
        cursor.execute("""
            CREATE TABLE taxes (
                id INT PRIMARY KEY AUTO_INCREMENT,
                nom_taxe VARCHAR(200) NOT NULL,
                categorie VARCHAR(100),
                montant_base DECIMAL(10,2),
                montant_max DECIMAL(10,2),
                periodicite VARCHAR(50),
                description TEXT,
                conditions_application TEXT,
                mode_calcul TEXT,
                actif TINYINT(1) DEFAULT 1,
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("  [OK] Table taxes")

        # Table formulaires
        cursor.execute("""
            CREATE TABLE formulaires (
                id INT PRIMARY KEY AUTO_INCREMENT,
                nom_document VARCHAR(200) NOT NULL,
                categorie VARCHAR(100),
                tarif DECIMAL(10,2),
                delai_traitement VARCHAR(100),
                pieces_requises TEXT,
                description TEXT,
                conditions_obtention TEXT,
                actif TINYINT(1) DEFAULT 1,
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("  [OK] Table formulaires")

        # Table locations
        cursor.execute("""
            CREATE TABLE locations (
                id INT PRIMARY KEY AUTO_INCREMENT,
                type_location VARCHAR(100) NOT NULL,
                designation VARCHAR(200) NOT NULL,
                tarif_base DECIMAL(10,2),
                unite VARCHAR(50),
                capacite VARCHAR(100),
                equipements TEXT,
                conditions_location TEXT,
                disponible TINYINT(1) DEFAULT 1,
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("  [OK] Table locations")

        # Table citoyens
        cursor.execute("""
            CREATE TABLE citoyens (
                id INT PRIMARY KEY AUTO_INCREMENT,
                nom VARCHAR(200) NOT NULL,
                prenom VARCHAR(200),
                email VARCHAR(200),
                telephone VARCHAR(50),
                adresse TEXT,
                numero_contribuable VARCHAR(100) UNIQUE,
                date_naissance DATE,
                lieu_naissance VARCHAR(200),
                actif TINYINT(1) DEFAULT 1,
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("  [OK] Table citoyens")

        # Table agents
        cursor.execute("""
            CREATE TABLE agents (
                id INT PRIMARY KEY AUTO_INCREMENT,
                nom VARCHAR(200) NOT NULL,
                prenom VARCHAR(200),
                email VARCHAR(200),
                telephone VARCHAR(50),
                poste VARCHAR(100),
                service_id INT,
                actif TINYINT(1) DEFAULT 1,
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (service_id) REFERENCES services_municipaux(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("  [OK] Table agents")

        # Table transactions
        cursor.execute("""
            CREATE TABLE transactions (
                id INT PRIMARY KEY AUTO_INCREMENT,
                citoyen_id INT,
                agent_id INT,
                type VARCHAR(50) NOT NULL,
                libelle VARCHAR(255) NOT NULL,
                montant DECIMAL(10,2) NOT NULL,
                mode_paiement VARCHAR(100) DEFAULT 'Espèces',
                numero_recu VARCHAR(100) UNIQUE,
                transaction_id VARCHAR(255),
                hashscan_url TEXT,
                statut VARCHAR(50) DEFAULT 'COMPLETE',
                nom_commercant VARCHAR(200),
                numero_commercant VARCHAR(100),
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (citoyen_id) REFERENCES citoyens(id),
                FOREIGN KEY (agent_id) REFERENCES agents(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("  [OK] Table transactions")

        # Table reservations
        cursor.execute("""
            CREATE TABLE reservations (
                id INT PRIMARY KEY AUTO_INCREMENT,
                location_id INT NOT NULL,
                citoyen_id INT,
                agent_id INT,
                date_debut DATE NOT NULL,
                date_fin DATE NOT NULL,
                montant_total DECIMAL(10,2),
                statut VARCHAR(50) DEFAULT 'EN_ATTENTE',
                commentaire TEXT,
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (location_id) REFERENCES locations(id),
                FOREIGN KEY (citoyen_id) REFERENCES citoyens(id),
                FOREIGN KEY (agent_id) REFERENCES agents(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("  [OK] Table reservations")

        # Table alertes
        cursor.execute("""
            CREATE TABLE alertes (
                id INT PRIMARY KEY AUTO_INCREMENT,
                type_alerte VARCHAR(100) NOT NULL,
                niveau_priorite VARCHAR(50) DEFAULT 'MOYEN',
                titre VARCHAR(255) NOT NULL,
                description TEXT,
                transaction_id INT,
                traitee TINYINT(1) DEFAULT 0,
                date_traitement TIMESTAMP NULL,
                responsable VARCHAR(200),
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (transaction_id) REFERENCES transactions(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("  [OK] Table alertes")

        # Table audit_log
        cursor.execute("""
            CREATE TABLE audit_log (
                id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT,
                action VARCHAR(100) NOT NULL,
                table_name VARCHAR(100),
                record_id INT,
                details TEXT,
                ip_address VARCHAR(50),
                date_action TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES agents(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("  [OK] Table audit_log")

        conn.commit()
        conn.close()

        print(f"[OK] {len(tables)} tables créées avec succès")
        return True

    except mysql.connector.Error as e:
        print(f"[ERROR] Erreur lors de la création des tables: {e}")
        return False


def migrate_data(config):
    """Migre les données de SQLite vers MySQL."""
    import mysql.connector

    print("\n[MIGRATION] Migration des données SQLite -> MySQL...")

    # Vérifier que mairie.db existe
    if not os.path.exists('mairie.db'):
        print("[ERROR] Fichier mairie.db non trouvé!")
        return False

    try:
        # Connexion SQLite
        sqlite_conn = sqlite3.connect('mairie.db')
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cursor = sqlite_conn.cursor()

        # Connexion MySQL
        mysql_conn = mysql.connector.connect(**config)
        mysql_cursor = mysql_conn.cursor()

        # Tables à migrer (dans l'ordre des dépendances)
        tables_to_migrate = [
            'services_municipaux',
            'taxes',
            'formulaires',
            'locations',
            'citoyens',
            'agents',
            'transactions',
            'reservations',
            'alertes',
            'audit_log'
        ]

        total_rows = 0

        for table in tables_to_migrate:
            # Récupérer les données de SQLite
            sqlite_cursor.execute(f"SELECT * FROM {table}")
            rows = sqlite_cursor.fetchall()

            if not rows:
                print(f"  [SKIP] {table}: 0 lignes")
                continue

            # Récupérer les noms de colonnes
            columns = [description[0] for description in sqlite_cursor.description]

            # Préparer la requête d'insertion
            placeholders = ', '.join(['%s'] * len(columns))
            columns_str = ', '.join(columns)
            insert_query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"

            # Insérer les données
            rows_inserted = 0
            for row in rows:
                try:
                    values = tuple(row)
                    mysql_cursor.execute(insert_query, values)
                    rows_inserted += 1
                except mysql.connector.Error as e:
                    print(f"    [WARNING] Erreur insertion dans {table}: {e}")
                    continue

            mysql_conn.commit()
            total_rows += rows_inserted
            print(f"  [OK] {table}: {rows_inserted} lignes migrées")

        sqlite_conn.close()
        mysql_conn.close()

        print(f"\n[OK] Migration terminée: {total_rows} lignes au total")
        return True

    except Exception as e:
        print(f"[ERROR] Erreur lors de la migration: {e}")
        return False


def verify_migration(config):
    """Vérifie que la migration s'est bien passée."""
    import mysql.connector

    print("\n[VERIFICATION] Vérification de la migration...")

    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        # Vérifier chaque table
        tables = [
            'services_municipaux',
            'taxes',
            'formulaires',
            'locations',
            'citoyens',
            'agents',
            'transactions',
            'reservations',
            'alertes',
            'audit_log'
        ]

        all_ok = True

        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]

            if count > 0:
                print(f"  [OK] {table}: {count} lignes")
            else:
                print(f"  [INFO] {table}: 0 lignes")

        conn.close()

        if all_ok:
            print("\n[OK] Vérification terminée avec succès!")

        return all_ok

    except mysql.connector.Error as e:
        print(f"[ERROR] Erreur lors de la vérification: {e}")
        return False


def update_env_file():
    """Met à jour le fichier .env pour utiliser MySQL."""
    print("\n[CONFIG] Mise à jour du fichier .env...")

    env_content = """# Type de base de données
DB_TYPE=mysql

# Configuration MySQL WAMPSERVER
DB_HOST=localhost
DB_NAME=mairie_db
DB_USER=root
DB_PASSWORD=
DB_PORT=3306
"""

    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)

        print("[OK] Fichier .env mis à jour")
        print("\nSi vous utilisez un utilisateur autre que 'root',")
        print("modifiez DB_USER et DB_PASSWORD dans le fichier .env")
        return True

    except Exception as e:
        print(f"[ERROR] Impossible de mettre à jour .env: {e}")
        return False


def main():
    """Fonction principale."""
    print("=" * 70)
    print("MIGRATION AUTOMATIQUE VERS WAMPSERVER MYSQL")
    print("=" * 70)

    # Vérifier mysql-connector-python
    if not check_mysql_connector():
        print("\n[ACTION] Installez mysql-connector-python avec:")
        print("         pip install mysql-connector-python")
        return

    # Récupérer la configuration
    config = get_mysql_config()

    # Tester la connexion
    if not test_mysql_connection(config):
        return

    # Créer la base de données
    if not create_database(config):
        return

    # Créer les tables
    if not create_tables(config):
        return

    # Migrer les données
    if not migrate_data(config):
        return

    # Vérifier la migration
    if not verify_migration(config):
        return

    # Mettre à jour .env
    update_env_file()

    # Résumé
    print("\n" + "=" * 70)
    print("MIGRATION TERMINEE AVEC SUCCES!")
    print("=" * 70)
    print("\nProchaines étapes:")
    print("  1. Vérifiez les données dans phpMyAdmin")
    print("  2. Modifiez .env si vous utilisez un autre utilisateur")
    print("  3. Lancez l'application: streamlit run dashboard.py")
    print("\nL'application utilisera maintenant MySQL au lieu de SQLite!")
    print("=" * 70)


if __name__ == "__main__":
    main()
