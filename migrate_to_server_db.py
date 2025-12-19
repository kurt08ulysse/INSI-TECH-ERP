#!/usr/bin/env python3
"""
Script de migration de SQLite vers PostgreSQL/MySQL
Pour déployer la base de données sur un serveur.
"""

import sqlite3
import os
import sys

def check_dependencies():
    """Vérifie les dépendances nécessaires."""
    print("[CHECK] Verification des dependances...")

    try:
        import psycopg2
        print("  [OK] psycopg2 installe (PostgreSQL)")
        has_postgres = True
    except ImportError:
        print("  [WARNING] psycopg2 non installe")
        print("           Installer avec: pip install psycopg2-binary")
        has_postgres = False

    try:
        import mysql.connector
        print("  [OK] mysql-connector-python installe (MySQL)")
        has_mysql = True
    except ImportError:
        print("  [WARNING] mysql-connector-python non installe")
        print("           Installer avec: pip install mysql-connector-python")
        has_mysql = False

    return has_postgres, has_mysql


def export_sqlite_schema():
    """Exporte le schéma SQLite."""
    print("\n[EXPORT] Exportation du schema SQLite...")

    conn = sqlite3.connect('mairie.db')
    cursor = conn.cursor()

    # Récupérer toutes les tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = cursor.fetchall()

    schema = {}
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        create_sql = cursor.fetchone()[0]
        schema[table_name] = create_sql
        print(f"  [OK] Table: {table_name}")

    conn.close()
    return schema


def convert_schema_to_postgresql(sqlite_schema):
    """Convertit le schéma SQLite en PostgreSQL."""
    print("\n[CONVERT] Conversion du schema pour PostgreSQL...")

    pg_schema = {}

    for table_name, create_sql in sqlite_schema.items():
        # Remplacements de base
        pg_sql = create_sql

        # SQLite -> PostgreSQL conversions
        pg_sql = pg_sql.replace('INTEGER PRIMARY KEY AUTOINCREMENT', 'SERIAL PRIMARY KEY')
        pg_sql = pg_sql.replace('AUTOINCREMENT', '')
        pg_sql = pg_sql.replace('DATETIME', 'TIMESTAMP')
        pg_sql = pg_sql.replace('REAL', 'NUMERIC')
        pg_sql = pg_sql.replace('BOOLEAN', 'BOOLEAN')
        pg_sql = pg_sql.replace('VARCHAR', 'VARCHAR')

        pg_schema[table_name] = pg_sql
        print(f"  [OK] Converti: {table_name}")

    return pg_schema


def convert_schema_to_mysql(sqlite_schema):
    """Convertit le schéma SQLite en MySQL."""
    print("\n[CONVERT] Conversion du schema pour MySQL...")

    mysql_schema = {}

    for table_name, create_sql in sqlite_schema.items():
        # Remplacements de base
        mysql_sql = create_sql

        # SQLite -> MySQL conversions
        mysql_sql = mysql_sql.replace('INTEGER PRIMARY KEY AUTOINCREMENT', 'INT PRIMARY KEY AUTO_INCREMENT')
        mysql_sql = mysql_sql.replace('AUTOINCREMENT', 'AUTO_INCREMENT')
        mysql_sql = mysql_sql.replace('DATETIME', 'TIMESTAMP')
        mysql_sql = mysql_sql.replace('REAL', 'DECIMAL(10,2)')
        mysql_sql = mysql_sql.replace('BOOLEAN', 'TINYINT(1)')

        # Ajouter ENGINE=InnoDB
        if not mysql_sql.strip().endswith(';'):
            mysql_sql += ';'
        mysql_sql = mysql_sql.replace(';', ' ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;')

        mysql_schema[table_name] = mysql_sql
        print(f"  [OK] Converti: {table_name}")

    return mysql_schema


def export_data_from_sqlite():
    """Exporte toutes les données de SQLite."""
    print("\n[EXPORT] Exportation des donnees SQLite...")

    conn = sqlite3.connect('mairie.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Récupérer toutes les tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [t[0] for t in cursor.fetchall()]

    data = {}
    total_rows = 0

    for table in tables:
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        data[table] = [dict(row) for row in rows]
        total_rows += len(rows)
        print(f"  [OK] {table}: {len(rows)} lignes")

    conn.close()
    print(f"\n  [TOTAL] {total_rows} lignes exportees")
    return data


def generate_sql_export_file(schema, data, db_type='postgresql'):
    """Génère un fichier SQL d'export."""
    print(f"\n[GENERATE] Generation du fichier SQL pour {db_type}...")

    filename = f'export_{db_type}.sql'

    with open(filename, 'w', encoding='utf-8') as f:
        # Header
        f.write(f"-- Export de la base de donnees mairie vers {db_type.upper()}\n")
        f.write(f"-- Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # Schema
        f.write("-- SCHEMA\n\n")
        for table_name, create_sql in schema.items():
            f.write(f"DROP TABLE IF EXISTS {table_name} CASCADE;\n")
            f.write(f"{create_sql}\n\n")

        # Data
        f.write("\n-- DATA\n\n")
        for table_name, rows in data.items():
            if not rows:
                continue

            f.write(f"-- Table: {table_name}\n")

            for row in rows:
                columns = ', '.join(row.keys())
                values = []

                for value in row.values():
                    if value is None:
                        values.append('NULL')
                    elif isinstance(value, str):
                        # Échapper les apostrophes
                        escaped = value.replace("'", "''")
                        values.append(f"'{escaped}'")
                    elif isinstance(value, (int, float)):
                        values.append(str(value))
                    else:
                        values.append(f"'{str(value)}'")

                values_str = ', '.join(values)
                f.write(f"INSERT INTO {table_name} ({columns}) VALUES ({values_str});\n")

            f.write("\n")

    print(f"  [OK] Fichier genere: {filename}")
    return filename


def create_migration_guide():
    """Crée un guide de migration."""
    guide = """
=================================================================
GUIDE DE MIGRATION - BASE DE DONNEES MAIRIE
=================================================================

ETAPE 1: PREPARER LE SERVEUR DE BASE DE DONNEES
-----------------------------------------------

Pour PostgreSQL:
    1. Installer PostgreSQL sur votre serveur
    2. Créer la base de données:
       CREATE DATABASE mairie_db;
    3. Créer un utilisateur:
       CREATE USER mairie_user WITH PASSWORD 'votre_mot_de_passe';
    4. Donner les permissions:
       GRANT ALL PRIVILEGES ON DATABASE mairie_db TO mairie_user;

Pour MySQL:
    1. Installer MySQL sur votre serveur
    2. Créer la base de données:
       CREATE DATABASE mairie_db;
    3. Créer un utilisateur:
       CREATE USER 'mairie_user'@'localhost' IDENTIFIED BY 'votre_mot_de_passe';
    4. Donner les permissions:
       GRANT ALL PRIVILEGES ON mairie_db.* TO 'mairie_user'@'localhost';
       FLUSH PRIVILEGES;

ETAPE 2: IMPORTER LES DONNEES
-----------------------------

Pour PostgreSQL:
    psql -U mairie_user -d mairie_db -f export_postgresql.sql

Pour MySQL:
    mysql -u mairie_user -p mairie_db < export_mysql.sql

ETAPE 3: MODIFIER L'APPLICATION
-------------------------------

1. Installer les dépendances:
   - Pour PostgreSQL: pip install psycopg2-binary
   - Pour MySQL: pip install mysql-connector-python

2. Configurer les variables d'environnement dans .env:
   DB_HOST=localhost
   DB_NAME=mairie_db
   DB_USER=mairie_user
   DB_PASSWORD=votre_mot_de_passe
   DB_PORT=5432  # ou 3306 pour MySQL

3. Modifier database_mairie.py pour utiliser le nouveau connecteur

ETAPE 4: TESTER LA CONNEXION
----------------------------

1. Tester la connexion au serveur de base de données
2. Vérifier que toutes les tables sont créées
3. Vérifier que toutes les données sont importées
4. Lancer l'application et tester

=================================================================
"""

    with open('GUIDE_MIGRATION.txt', 'w', encoding='utf-8') as f:
        f.write(guide)

    print("\n[OK] Guide de migration cree: GUIDE_MIGRATION.txt")


def main():
    """Fonction principale."""
    from datetime import datetime

    print("=" * 60)
    print("MIGRATION DE LA BASE DE DONNEES MAIRIE")
    print("SQLite -> PostgreSQL/MySQL")
    print("=" * 60)

    # Vérifier les dépendances
    has_postgres, has_mysql = check_dependencies()

    if not has_postgres and not has_mysql:
        print("\n[ERROR] Aucun connecteur de base de donnees installe!")
        print("        Installer au moins un des deux:")
        print("        - pip install psycopg2-binary")
        print("        - pip install mysql-connector-python")
        return

    # Vérifier que mairie.db existe
    if not os.path.exists('mairie.db'):
        print("\n[ERROR] Fichier mairie.db non trouve!")
        print("        Verifiez que vous etes dans le bon repertoire.")
        return

    # Exporter le schéma SQLite
    sqlite_schema = export_sqlite_schema()

    # Exporter les données
    data = export_data_from_sqlite()

    # Générer les fichiers SQL
    if has_postgres:
        pg_schema = convert_schema_to_postgresql(sqlite_schema)
        generate_sql_export_file(pg_schema, data, 'postgresql')

    if has_mysql:
        mysql_schema = convert_schema_to_mysql(sqlite_schema)
        generate_sql_export_file(mysql_schema, data, 'mysql')

    # Créer le guide de migration
    create_migration_guide()

    # Résumé
    print("\n" + "=" * 60)
    print("MIGRATION TERMINEE AVEC SUCCES!")
    print("=" * 60)
    print("\nFichiers generes:")
    if has_postgres:
        print("  - export_postgresql.sql")
    if has_mysql:
        print("  - export_mysql.sql")
    print("  - GUIDE_MIGRATION.txt")
    print("\nConsultez GUIDE_MIGRATION.txt pour les etapes suivantes.")
    print("=" * 60)


if __name__ == "__main__":
    main()
