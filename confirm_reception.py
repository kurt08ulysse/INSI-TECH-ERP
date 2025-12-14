# confirm_reception.py - Confirmation de réception des matières premières

import paho.mqtt.client as mqtt
from hedera import Client, AccountId, PrivateKey, TopicMessageSubmitTransaction, TopicId
from datetime import datetime
import json
import config
from logger import get_logger, log_hedera_publish, log_mqtt_message, log_error
import token_manager
import database as db

logger = get_logger(__name__)

# Initialisation Hedera Client
hedera_client = None


def init_hedera_client():
    """Initialise le client Hedera."""
    global hedera_client
    try:
        hedera_client = Client.forTestnet()
        hedera_client.setOperator(
            AccountId.fromString(config.OPERATOR_ID),
            PrivateKey.fromString(config.OPERATOR_KEY)
        )
        logger.info("✅ Client Hedera initialisé")
        return True
    except Exception as e:
        log_error("Initialisation Hedera", e)
        return False


def on_connect(client, userdata, flags, rc, properties=None):
    """Callback de connexion au broker MQTT."""
    if rc == 0:
        logger.info("✅ Connecté au broker MQTT HiveMQ Cloud")
        client.subscribe(config.MQTT_TOPIC)
        logger.info(f"📡 Abonné au topic : {config.MQTT_TOPIC}")
    else:
        logger.error(f"❌ Connexion échouée, code: {rc}")


def on_message(client_mqtt, userdata, msg):
    """Callback quand un message est reçu."""
    try:
        payload = msg.payload.decode()
        logger.debug(f"📥 Message reçu sur '{msg.topic}': {payload}")
        log_mqtt_message(msg.topic, payload)

        data = json.loads(payload)
        matiere = data.get("matiere")
        quantite = data.get("quantite", 0)

        if not matiere or quantite <= 0:
            logger.warning(f"⚠️ Message incomplet ou invalide : {data}")
            return

        # Créer la confirmation
        confirmation = {
            "type": "reception_confirmation",
            "matiere": matiere,
            "quantite": quantite,
            "date": datetime.now().isoformat()
        }

        message_json = json.dumps(confirmation, ensure_ascii=False)

        # Publier sur Hedera
        if hedera_client:
            topic_id = TopicId.fromString(config.TOPIC_ID)
            transaction = TopicMessageSubmitTransaction() \
                .setTopicId(topic_id) \
                .setMessage(message_json) \
                .execute(hedera_client)

            receipt = transaction.getReceipt(hedera_client)
            transaction_id = transaction.transactionId.toString()

            logger.info(f"✅ Réception confirmée pour {matiere} ({quantite} unités)")
            logger.info(f"🔗 HashScan : https://hashscan.io/testnet/transaction/{transaction_id}")
            log_hedera_publish(config.TOPIC_ID, transaction_id)
            
            # MINT du Token (Nouveau)
            conn = db.get_connection()
            cursor = conn.cursor()
            row = cursor.execute("SELECT token_id FROM stocks WHERE LOWER(nom)=?", (matiere.lower(),)).fetchone()
            token_id = row['token_id'] if row else None
            conn.close()
            
            if token_id:
                token_manager.mint_stock(token_id, quantite)
                logger.info(f"💎 {quantite} tokens mintés pour {matiere} (ID: {token_id})")
            else:
                logger.warning(f"⚠️ Pas de Token ID pour {matiere}, impossible de mint.")

            # Retourner le résultat pour le pipeline
            print(f"Réception confirmée pour {matiere}")
            return True

    except json.JSONDecodeError:
        logger.error(f"❌ Payload JSON invalide : {msg.payload}")
    except Exception as e:
        log_error("Publication sur Hedera", e)
    
    return False


def main():
    """Point d'entrée principal."""
    # Validation de la configuration
    if not config.validate_config():
        logger.error("❌ Configuration invalide. Arrêt.")
        return
    
    # Initialiser Hedera
    if not init_hedera_client():
        logger.error("❌ Impossible d'initialiser Hedera. Arrêt.")
        return
    
    # Configurer MQTT
    client_mqtt = mqtt.Client(client_id="confirm_reception", protocol=mqtt.MQTTv311)
    client_mqtt.username_pw_set(config.MQTT_USERNAME, config.MQTT_PASSWORD)
    client_mqtt.tls_set()
    
    client_mqtt.on_connect = on_connect
    client_mqtt.on_message = on_message

    try:
        logger.info(f"📡 Connexion au broker MQTT {config.MQTT_BROKER}:{config.MQTT_PORT}...")
        client_mqtt.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
        logger.info(f"📶 Surveillance des réceptions RFID sur '{config.MQTT_TOPIC}'...")
        client_mqtt.loop_forever()
        
    except KeyboardInterrupt:
        logger.info("🛑 Arrêt par l'utilisateur")
    except Exception as e:
        log_error("Connexion MQTT", e)
    finally:
        client_mqtt.disconnect()


if __name__ == "__main__":
    main()