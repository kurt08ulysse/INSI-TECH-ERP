import smtplib
from email.message import EmailMessage
from config import EMAIL_FROM, EMAIL_TO, EMAIL_SUBJECT, SMTP_SERVER, SMTP_PORT, EMAIL_PASSWORD
import agents
from logger import get_logger

logger = get_logger(__name__)

# Active/désactive l’envoi d’email (utile si tu veux juste tester sans spammer)
ENVOYER_EMAILS = True

def envoyer_email(matiere, quantite):
    logger.info(f"🚨 Alerte reçue pour {matiere} ({quantite}). Lancement Négociation Agents...")
    
    # 1. Négociation Automatique (IA Agents)
    winner, proposals = agents.run_negotiation(matiere, 50) # On commande 50 par défaut
    
    if not winner:
        logger.error("❌ Échec de la négociation agents.")
        return

    logger.info(f"🏆 Gagnant de l'enchère : {winner['agent']} avec {winner['price']} FCFA/u")

    # 2. Envoi Email au Gagnant (Simulé ou Réel)
    if not ENVOYER_EMAILS:
        print(f"⚠️ Envoi d’email désactivé. Commande virtuelle passée à {winner['agent']}")
        return

    destinataire = EMAIL_TO # Dans un vrai cas, ce serait l'email du winner['agent']
    
    msg = EmailMessage()
    msg['Subject'] = f"COMMANDE CONFIRMÉE - {matiere.upper()}"
    msg['From'] = EMAIL_FROM
    msg['To'] = destinataire
    msg.set_content(
        f"""Bonjour {winner['agent']},

Suite à votre proposition lors de l'enchère automatique :

- Matière : {matiere}
- Quantité : 50 unités
- Prix unitaire : {winner['price']} FCFA
- Total : {winner['total']} FCFA
- Délai promis : {winner['delay']} jours

Nous confirmons la commande. Veuillez procéder à la livraison.

Cordialement,
Le système IoT de gestion de stock.
(Négociation validée par Agent IA)
"""
    )
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            server.send_message(msg)
            logger.info(f"📧 Commande envoyée à {winner['agent']} ({destinataire}).")
            
            # Pour la simulation, on simule la réponse immédiate pour que le flux continue
            # Dans un vrai système, on attendrait l'email de réponse
            send_price_reply(matiere, winner['price']) 
            
    except Exception as e:
        logger.error(f"❌ Erreur envoi email : {e}")

def send_price_reply(matiere, prix):
    # Simulation de la réponse du fournisseur pour déclencher la suite (Contrat)
    # On écrit directement un fichier qui serait lu par email_reader, 
    # ou on appelle la fonction de suite logique si on veut court-circuiter.
    # Pour garder le flux "Email Reader", on envoie vraiment un email de réponse à soi-même.
    
    if not ENVOYER_EMAILS:
        return

    msg = EmailMessage()
    msg['Subject'] = f"Réponse de prix - {matiere}"
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_FROM # On s'écrit à soi-même pour que email_reader le lise
    msg.set_content(f"Prix pour {matiere}: {prix} FCFA")
    
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_FROM, EMAIL_PASSWORD)
            smtp.send_message(msg)
            logger.info(f"📧 [Auto-Reply] Réponse simulée envoyée pour {matiere} ({prix} FCFA)")
    except Exception as e:
        logger.error(f"❌ Erreur auto-reply : {e}")