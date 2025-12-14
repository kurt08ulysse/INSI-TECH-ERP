# config.py - Configuration centralisée
# Les valeurs sensibles sont chargées depuis le fichier .env

import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

# ==============================================
# CONFIGURATION EMAIL
# ==============================================
EMAIL_FROM = os.getenv("EMAIL_FROM", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_TO = os.getenv("EMAIL_TO", "")
EMAIL_SUBJECT = "Demande de prix"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# ==============================================
# CONFIGURATION MQTT (HiveMQ Cloud)
# ==============================================
MQTT_BROKER = os.getenv("MQTT_BROKER", "")
MQTT_PORT = int(os.getenv("MQTT_PORT", "8883"))
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")
MQTT_TOPIC = "stock/matiere_premiere/MP_A"
MQTT_TOPIC_RECEPTION = "stock/reception"

# ==============================================
# CONFIGURATION HEDERA HASHGRAPH
# ==============================================
OPERATOR_ID = os.getenv("OPERATOR_ID", "")
OPERATOR_KEY = os.getenv("OPERATOR_KEY", "")
TOPIC_ID = os.getenv("TOPIC_ID", "")

# ==============================================
# PARAMÈTRES MÉTIER
# ==============================================
SEUIL_CRITIQUE = 20

# ID du compte fournisseur pour les paiements
SUPPLIER_ACCOUNT_ID = os.getenv("SUPPLIER_ACCOUNT_ID", "0.0.6180961")

# ==============================================
# VALIDATION DE LA CONFIGURATION
# ==============================================
def validate_config():
    """Vérifie que toutes les variables critiques sont configurées."""
    missing = []
    
    if not EMAIL_FROM:
        missing.append("EMAIL_FROM")
    if not EMAIL_PASSWORD:
        missing.append("EMAIL_PASSWORD")
    if not MQTT_BROKER:
        missing.append("MQTT_BROKER")
    if not MQTT_USERNAME:
        missing.append("MQTT_USERNAME")
    if not MQTT_PASSWORD:
        missing.append("MQTT_PASSWORD")
    if not OPERATOR_ID:
        missing.append("OPERATOR_ID")
    if not OPERATOR_KEY:
        missing.append("OPERATOR_KEY")
    if not TOPIC_ID:
        missing.append("TOPIC_ID")
    
    if missing:
        print(f"⚠️ Variables manquantes dans .env : {', '.join(missing)}")
        print("📝 Copiez .env.example vers .env et remplissez les valeurs.")
        return False
    return True