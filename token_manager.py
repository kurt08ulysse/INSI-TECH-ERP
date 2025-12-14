# token_manager.py - Gestion des Tokens Hedera (HTS)
# Mode hybride : Réel si Java/SDK dispo, sinon Simulation

import config
from logger import get_logger, log_transaction, log_error
import database as db
import uuid

logger = get_logger(__name__)

# État du client Hedera
client = None
IS_SIMULATION = False

try:
    from hedera import (
        Client, AccountId, PrivateKey, 
        TokenCreateTransaction, TokenSupplyType, TokenType,
        TokenMintTransaction
    )
    
    # Tentative d'initialisation du vrai client
    try:
        client = Client.forTestnet()
        client.setOperator(
            AccountId.fromString(config.OPERATOR_ID),
            PrivateKey.fromString(config.OPERATOR_KEY)
        )
        logger.info("✅ Client Hedera HTS initialisé (Mode Réel)")
    except Exception as e:
        logger.warning(f"⚠️ Erreur init client Hedera: {e}. Passage en mode SIMULATION.")
        IS_SIMULATION = True

except ImportError:
    logger.warning("⚠️ Module 'hedera' non trouvé. Passage en mode SIMULATION.")
    IS_SIMULATION = True
except Exception as e:
    logger.warning(f"⚠️ Erreur chargement SDK (probablement Java manquant): {e}. Passage en mode SIMULATION.")
    IS_SIMULATION = True


def create_stock_token(matiere_nom, matiere_code):
    """
    Crée un Token Fungible sur Hedera (ou simule).
    Retourne le TokenId.
    """
    token_id = None
    
    if not IS_SIMULATION and client:
        try:
            logger.info(f"💎 Création du token RÉEL pour {matiere_nom} ({matiere_code})...")
            transaction = TokenCreateTransaction() \
                .setTokenName(f"Stock {matiere_nom.capitalize()}") \
                .setTokenSymbol(matiere_code.upper()) \
                .setTokenType(TokenType.FUNGIBLE_COMMON) \
                .setDecimals(0) \
                .setInitialSupply(0) \
                .setTreasuryAccountId(AccountId.fromString(config.OPERATOR_ID)) \
                .setSupplyType(TokenSupplyType.INFINITE) \
                .setSupplyKey(PrivateKey.fromString(config.OPERATOR_KEY)) \
                .setAdminKey(PrivateKey.fromString(config.OPERATOR_KEY)) \
                .freezeWith(client)

            transaction.sign(PrivateKey.fromString(config.OPERATOR_KEY))
            response = transaction.execute(client)
            receipt = response.getReceipt(client)
            token_id = receipt.tokenId.toString()
            logger.info(f"✅ Token créé sur Hedera ! ID: {token_id}")

        except Exception as e:
            log_error(f"Création Token Réel {matiere_nom}", e)
            logger.info("bascule vers token simulé...")
            token_id = f"0.0.{uuid.uuid4().int.__str__()[:6]} (SIM)"
    else:
        # Simulation
        logger.info(f"💎 [SIMULATION] Création token pour {matiere_nom}...")
        token_id = f"0.0.{uuid.uuid4().int.__str__()[:6]} (SIM)"
        
    if token_id:
        log_transaction("TOKEN_CREATION", {"matiere": matiere_nom, "token_id": token_id, "simulated": IS_SIMULATION})
        
        # Mettre à jour la DB
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE stocks SET token_id = ? WHERE code = ?", (token_id, matiere_code))
        conn.commit()
        conn.close()
        
    return token_id


def mint_stock(token_id, amount):
    """
    Mint des tokens (Réel ou Simulé).
    """
    if not token_id:
        return False
        
    if not IS_SIMULATION and client and "(SIM)" not in token_id:
        try:
            logger.info(f"🔨 Minting RÉEL de {amount} tokens pour {token_id}...")
            transaction = TokenMintTransaction() \
                .setTokenId(token_id) \
                .setAmount(int(amount)) \
                .freezeWith(client)
                
            transaction.sign(PrivateKey.fromString(config.OPERATOR_KEY))
            response = transaction.execute(client)
            response.getReceipt(client) # Wait for confirmation
            
            logger.info(f"✅ Mint réel confirmé.")
            log_transaction("TOKEN_MINT", {"token_id": token_id, "amount": amount, "simulated": False})
            return True
            
        except Exception as e:
            log_error(f"Mint Token Réel {token_id}", e)
            return False
    else:
        # Simulation
        logger.info(f"🔨 [SIMULATION] Mint de {amount} tokens pour {token_id}")
        log_transaction("TOKEN_MINT", {"token_id": token_id, "amount": amount, "simulated": True})
        return True


def init_all_tokens():
    """Crée les tokens manquants au démarrage."""
    logger.info("🚀 Initialisation des tokens (Vérification)...")
    stocks = db.get_all_stocks()
    count = 0
    for stock in stocks:
        if not stock['token_id']:
            create_stock_token(stock['nom'], stock['code'])
            count += 1
    if count > 0:
        logger.info(f"✅ {count} nouveaux tokens créés.")
    else:
        logger.info("✅ Tous les tokens existent déjà.")

            
if __name__ == "__main__":
    init_all_tokens()
