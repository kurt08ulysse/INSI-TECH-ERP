# logger.py - Système de logging centralisé

import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Créer le dossier logs s'il n'existe pas
LOGS_DIR = os.path.join(os.path.dirname(__file__), "logs")

# Configuration
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def get_logger(name):
    """Récupère un logger configuré."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        # 1. Console Handler
        c_handler = logging.StreamHandler()
        c_handler.setLevel(logging.INFO)
        c_format = logging.Formatter('%(asctime)s | %(levelname)-8s | %(name)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        c_handler.setFormatter(c_format)
        logger.addHandler(c_handler)

        # 2. File Handler
        f_handler = RotatingFileHandler(os.path.join(LOG_DIR, 'app.log'), maxBytes=1000000, backupCount=5)
        f_handler.setLevel(logging.DEBUG)
        f_format = logging.Formatter('%(asctime)s | %(levelname)-8s | %(name)s | %(message)s')
        f_handler.setFormatter(f_format)
        logger.addHandler(f_handler)# 
#
    return logger


# Logger principal pour les messages généraux
main_logger = get_logger("iot_blockchain")


def log_transaction(tx_type: str, details: dict):
    """Log une transaction avec ses détails."""
    main_logger.info(f"[TRANSACTION] Type: {tx_type} | Détails: {details}")


def log_alert(matiere: str, quantite: int):
    """Log une alerte de stock critique."""
    main_logger.warning(f"[ALERTE] Stock critique - Matière: {matiere}, Quantité: {quantite}")


def log_mqtt_message(topic: str, payload: str):
    """Log un message MQTT reçu."""
    main_logger.debug(f"[MQTT] Topic: {topic} | Payload: {payload}")


def log_hedera_publish(topic_id: str, tx_id: str):
    """Log une publication Hedera."""
    main_logger.info(f"[HEDERA] Topic: {topic_id} | Transaction: {tx_id}")


def log_error(context: str, error: Exception):
    """Log une erreur avec le contexte."""
    main_logger.error(f"[ERREUR] {context}: {str(error)}", exc_info=True)