#!/usr/bin/env python3
"""
Script pour nettoyer le projet et supprimer les fichiers inutiles
pour le système de gestion municipale.
"""

import os
import shutil

# Fichiers Python ESSENTIELS pour le système de gestion municipale
ESSENTIAL_FILES = {
    'dashboard.py',              # Interface principale
    'database_mairie.py',        # Base de données municipale
    'services_mairie.py',        # Logique métier municipale
    'guichet_mairie.py',         # Interface guichet
    'paiement_client.py',        # Interface paiement en ligne
    'ia_surveillance.py',        # Surveillance IA
    'ai_forecast.py',            # Prévisions IA
    'logger.py',                 # Système de logging
    'reset_database.py',         # Utilitaire de réinitialisation DB
    'launcher.py',               # Lanceur de l'application
    'streamlit_app.py',          # Point d'entrée Streamlit
}

# Fichiers à SUPPRIMER (anciens fichiers de gestion de stock/RFID/IoT)
FILES_TO_DELETE = {
    # Ancienne base de données et services de stock
    'database.py',               # Ancienne base de données stock
    'services.py',               # Anciens services stock
    'guichet.py',                # Ancien guichet stock

    # Fichiers RFID/IoT non utilisés
    'simulateur_rfid.py',        # Simulateur RFID
    'simulateur_mqtt.py',        # Simulateur MQTT
    'detecteur_seuil.py',        # Détecteur de seuil stock

    # Fichiers Hashgraph/Blockchain non essentiels
    'hedera_publisher.py',       # Publisher Hedera
    'connect_hashgraph.py',      # Connexion Hashgraph
    'connect_testnet.py',        # Connexion testnet
    'create_topic.py',           # Création de topic
    'create_real_topic.py',      # Création topic réel
    'contract_manager.py',       # Gestionnaire de contrats
    'token_manager.py',          # Gestionnaire de tokens
    'run_publish.py',            # Publication

    # Fichiers email non utilisés
    'email_reader.py',           # Lecteur email
    'envoi_email.py',            # Envoi email
    'confirm_reception.py',      # Confirmation réception

    # Fichiers de configuration et utilitaires obsolètes
    'agents.py',                 # Agents (ancien système)
    'payment.py',                # Ancien système de paiement
    'main.py',                   # Ancien main
    'config.py',                 # Ancienne config
    'check_env.py',              # Vérification env
    'check_transactions.py',     # Vérification transactions
    'generate_env.py',           # Génération env
    'diagnose_db.py',            # Diagnostic DB
    'db_seeder.py',              # Seeder DB ancien
    'seed_history.py',           # Seed historique
    'mairie_data.py',            # Données mairie (obsolète)
    'log_stream.py',             # Stream de logs
}

# Fichiers de données à supprimer
DATA_FILES_TO_DELETE = {
    'stock_manager.db',          # Ancienne base de données stock
    'contrat_a_publier.json',    # Contrats à publier
    'paiement_log.json',         # Logs de paiement
    'publication_log.json',      # Logs de publication
    'config_local.json',         # Config locale
    'publish_contract.js',       # Script de publication
}

# Dossiers à supprimer
DIRECTORIES_TO_DELETE = {
    'tests',                     # Tests (anciens)
    'assets',                    # Assets (non utilisés)
}

def cleanup_project():
    """Nettoie le projet en supprimant les fichiers inutiles."""

    deleted_count = 0
    kept_count = 0

    print("=" * 60)
    print("NETTOYAGE DU PROJET - SYSTEME DE GESTION MUNICIPALE")
    print("=" * 60)

    # Supprimer les fichiers Python inutiles
    print("\n[1/3] Suppression des fichiers Python inutiles...")
    for filename in FILES_TO_DELETE:
        if os.path.exists(filename):
            try:
                os.remove(filename)
                print(f"  [DELETED] {filename}")
                deleted_count += 1
            except Exception as e:
                print(f"  [ERROR] Impossible de supprimer {filename}: {e}")
        else:
            print(f"  [SKIP] {filename} (n'existe pas)")

    # Supprimer les fichiers de données inutiles
    print("\n[2/3] Suppression des fichiers de donnees inutiles...")
    for filename in DATA_FILES_TO_DELETE:
        if os.path.exists(filename):
            try:
                os.remove(filename)
                print(f"  [DELETED] {filename}")
                deleted_count += 1
            except Exception as e:
                print(f"  [ERROR] Impossible de supprimer {filename}: {e}")
        else:
            print(f"  [SKIP] {filename} (n'existe pas)")

    # Supprimer les dossiers inutiles
    print("\n[3/3] Suppression des dossiers inutiles...")
    for dirname in DIRECTORIES_TO_DELETE:
        if os.path.exists(dirname) and os.path.isdir(dirname):
            try:
                shutil.rmtree(dirname)
                print(f"  [DELETED] {dirname}/ (dossier)")
                deleted_count += 1
            except Exception as e:
                print(f"  [ERROR] Impossible de supprimer {dirname}: {e}")
        else:
            print(f"  [SKIP] {dirname}/ (n'existe pas)")

    # Afficher les fichiers essentiels conservés
    print("\n" + "=" * 60)
    print("FICHIERS ESSENTIELS CONSERVES:")
    print("=" * 60)
    for filename in sorted(ESSENTIAL_FILES):
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"  [OK] {filename} ({size:,} bytes)")
            kept_count += 1
        else:
            print(f"  [WARNING] {filename} (manquant!)")

    # Fichiers de base de données
    print("\n[BASE DE DONNEES]")
    if os.path.exists('mairie.db'):
        size = os.path.getsize('mairie.db')
        print(f"  [OK] mairie.db ({size:,} bytes)")
        kept_count += 1

    # Fichiers de configuration
    print("\n[CONFIGURATION]")
    for config_file in ['.env', '.env.example', '.gitignore', 'requirements.txt', 'README.md']:
        if os.path.exists(config_file):
            size = os.path.getsize(config_file)
            print(f"  [OK] {config_file} ({size:,} bytes)")
            kept_count += 1

    # Résumé
    print("\n" + "=" * 60)
    print("RESUME DU NETTOYAGE:")
    print("=" * 60)
    print(f"  Fichiers/dossiers supprimes: {deleted_count}")
    print(f"  Fichiers essentiels conserves: {kept_count}")
    print(f"\n[SUCCESS] Nettoyage termine avec succes!")
    print("=" * 60)

if __name__ == "__main__":
    cleanup_project()
