#!/usr/bin/env python3
"""
Script de test de connexion à WAMPSERVER MySQL
Vérifie que la connexion fonctionne et que les données sont présentes
"""

import os
import sys

def test_wampserver_connection():
    """Test complet de la connexion WAMPSERVER."""

    print("=" * 70)
    print("TEST DE CONNEXION A WAMPSERVER MYSQL")
    print("=" * 70)

    # Vérifier mysql-connector-python
    print("\n[1/6] Vérification du module mysql-connector-python...")
    try:
        import mysql.connector
        print("  [OK] Module installé")
    except ImportError:
        print("  [ERROR] Module non installé")
        print("         Installer avec: pip install mysql-connector-python")
        return False

    # Charger la configuration
    print("\n[2/6] Chargement de la configuration...")
    try:
        from dotenv import load_dotenv
        load_dotenv()

        config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_NAME', 'mairie_db'),
            'port': int(os.getenv('DB_PORT', '3306'))
        }

        print(f"  [OK] Host: {config['host']}")
        print(f"  [OK] User: {config['user']}")
        print(f"  [OK] Database: {config['database']}")
        print(f"  [OK] Port: {config['port']}")

    except Exception as e:
        print(f"  [ERROR] Erreur de configuration: {e}")
        return False

    # Tester la connexion MySQL
    print("\n[3/6] Test de connexion à MySQL...")
    try:
        conn = mysql.connector.connect(
            host=config['host'],
            user=config['user'],
            password=config['password'],
            port=config['port']
        )

        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()[0]

        print(f"  [OK] Connexion réussie à MySQL {version}")
        conn.close()

    except mysql.connector.Error as e:
        print(f"  [ERROR] Impossible de se connecter: {e}")
        print("\n  Vérifiez que:")
        print("    1. WAMPSERVER est démarré (icône verte)")
        print("    2. MySQL est actif")
        print("    3. Les identifiants sont corrects")
        return False

    # Vérifier que la base de données existe
    print("\n[4/6] Vérification de la base de données...")
    try:
        conn = mysql.connector.connect(**config)
        print(f"  [OK] Base de données '{config['database']}' existe")
        conn.close()

    except mysql.connector.Error as e:
        print(f"  [ERROR] Base de données introuvable: {e}")
        print(f"\n  Créez la base de données avec:")
        print(f"    CREATE DATABASE {config['database']};")
        return False

    # Vérifier les tables
    print("\n[5/6] Vérification des tables...")
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]

        if tables:
            print(f"  [OK] {len(tables)} tables trouvées:")
            for table in tables:
                print(f"       - {table}")
        else:
            print("  [WARNING] Aucune table trouvée")
            print("           Exécutez: python migrate_to_wampserver.py")

        conn.close()

    except mysql.connector.Error as e:
        print(f"  [ERROR] Erreur lors de la vérification: {e}")
        return False

    # Vérifier les données
    print("\n[6/6] Vérification des données...")
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        # Tables importantes
        important_tables = [
            ('taxes', 24),
            ('formulaires', 25),
            ('locations', 16),
            ('transactions', 0),
            ('citoyens', 0),
            ('agents', 0)
        ]

        all_ok = True

        for table, expected_min in important_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]

                if count >= expected_min:
                    print(f"  [OK] {table}: {count} lignes")
                elif expected_min == 0:
                    print(f"  [INFO] {table}: {count} lignes (table vide normale)")
                else:
                    print(f"  [WARNING] {table}: {count} lignes (attendu: >= {expected_min})")
                    all_ok = False

            except mysql.connector.Error:
                print(f"  [WARNING] Table {table} non trouvée")

        conn.close()

        if not all_ok:
            print("\n  [WARNING] Certaines tables semblent incomplètes")
            print("           Exécutez: python migrate_to_wampserver.py")

    except mysql.connector.Error as e:
        print(f"  [ERROR] Erreur lors de la vérification: {e}")
        return False

    # Résumé
    print("\n" + "=" * 70)
    print("TEST TERMINE AVEC SUCCES!")
    print("=" * 70)
    print("\nStatut: Connexion à WAMPSERVER MySQL fonctionnelle")
    print("\nVous pouvez maintenant:")
    print("  1. Lancer l'application: streamlit run dashboard.py")
    print("  2. Gérer la base via phpMyAdmin")
    print("  3. Consulter les logs dans logs/app.log")
    print("=" * 70)

    return True


def quick_test():
    """Test rapide de connexion."""
    try:
        import mysql.connector
        from dotenv import load_dotenv
        load_dotenv()

        config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_NAME', 'mairie_db'),
            'port': int(os.getenv('DB_PORT', '3306'))
        }

        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM taxes")
        taxes_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM formulaires")
        formulaires_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM locations")
        locations_count = cursor.fetchone()[0]

        conn.close()

        print(f"\n[QUICK TEST]")
        print(f"  Taxes: {taxes_count}")
        print(f"  Formulaires: {formulaires_count}")
        print(f"  Locations: {locations_count}")

        return True

    except Exception as e:
        print(f"\n[QUICK TEST] Erreur: {e}")
        return False


if __name__ == "__main__":
    # Test complet par défaut
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        quick_test()
    else:
        test_wampserver_connection()
