# simulateur_rfid.py - Simulation de capteurs RFID via MQTT

import paho.mqtt.client as mqtt
import json
import random
import time
import config
from logger import get_logger, log_mqtt_message

logger = get_logger(__name__)

# Liste des matières premières
MATIERES = [
    {"code": "MP_A", "nom": "PAPIER A4"},
    {"code": "MP_B", "nom": "ENCRE IMPRIMANTE"},
    {"code": "MP_C", "nom": "AMPOULES PUBLIC"},
    {"code": "MP_D", "nom": "FORMULAIRES ACTES"},
    {"code": "MP_E", "nom": "ROULEAUX TICKETS"},
    {"code": "MP_F", "nom": "KITS SCOLAIRES"},
]


def on_connect(client, userdata, flags, rc, properties=None):
    """Callback de connexion au broker MQTT."""
    if rc == 0:
        logger.info("✅ Connecté au broker MQTT HiveMQ Cloud")
    else:
        logger.error(f"❌ Connexion échouée, code: {rc}")


def on_disconnect(client, userdata, rc, properties=None):
    """Callback de déconnexion."""
    if rc != 0:
        logger.warning(f"⚠️ Déconnexion inattendue, code: {rc}")


def publish_random_stock():
    """Publie des données de stock aléatoires via MQTT."""
    
    # Validation de la configuration
    if not config.validate_config():
        logger.error("❌ Configuration invalide. Arrêt du simulateur.")
        return
    
    client = mqtt.Client(client_id="simulateur_stock", protocol=mqtt.MQTTv311)
    
    # Authentification sécurisée pour HiveMQ Cloud
    client.username_pw_set(config.MQTT_USERNAME, config.MQTT_PASSWORD)
    client.tls_set()  # Active TLS (sécurisé)
    
    # Callbacks
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    try:
        # Connexion au broker
        logger.info(f"🔌 Connexion à {config.MQTT_BROKER}:{config.MQTT_PORT}...")
        client.connect(config.MQTT_BROKER, config.MQTT_PORT)
        client.loop_start()

        while True:
            mp = random.choice(MATIERES)
            quantite = random.randint(0, 100)
            payload = {
                "matiere": mp["nom"],
                "quantite": quantite,
                "code": mp["code"]
            }
            payload_str = json.dumps(payload)
            
            result = client.publish(config.MQTT_TOPIC, payload_str)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"📤 Publié sur {config.MQTT_TOPIC} : {payload_str}")
                log_mqtt_message(config.MQTT_TOPIC, payload_str)
            else:
                logger.error(f"❌ Échec de publication, code: {result.rc}")
            
            time.sleep(5)
            
    except KeyboardInterrupt:
        logger.info("🛑 Arrêt du simulateur par l'utilisateur")
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
    finally:
        client.loop_stop()
        client.disconnect()
        logger.info("🔌 Déconnecté du broker MQTT")


if __name__ == "__main__":
    logger.info("🚀 Démarrage du simulateur RFID MQTT...")
    publish_random_stock()