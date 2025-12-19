# services_mairie.py - Logique métier pour les services municipaux
"""
Ce module contient la logique métier RÉELLE pour:
- Calculer les montants des taxes, actes, locations
- Créer les transactions avec blockchain
- Détecter les anomalies financières
"""

import database_mairie as db
from datetime import datetime, timedelta
import random
from logger import get_logger

logger = get_logger(__name__)


def calculer_montant_taxe(taxe_id: int, **params) -> float:
    """
    Calcule le montant d'une taxe selon ses paramètres.

    Args:
        taxe_id: ID de la taxe dans la base
        **params: Paramètres additionnels (ex: montant_loyer pour taxe sur loyers)

    Returns:
        Montant calculé en FCFA
    """
    taxes = db.get_taxes()
    taxe = next((t for t in taxes if t['id'] == taxe_id), None)

    if not taxe:
        raise ValueError(f"Taxe ID {taxe_id} introuvable")

    # Si montant fixe défini
    if taxe['montant_fixe'] and taxe['montant_fixe'] > 0:
        return taxe['montant_fixe']

    # Si taux pourcentage (ex: taxe sur loyers)
    if taxe['taux_pourcentage'] and 'montant_base' in params:
        montant_base = params['montant_base']
        return (montant_base * taxe['taux_pourcentage']) / 100

    # Par défaut, retourner 0 si pas de montant défini
    return 0.0


def calculer_montant_acte(formulaire_id: int) -> float:
    """
    Calcule le montant d'un acte administratif.

    Args:
        formulaire_id: ID du formulaire dans la base

    Returns:
        Montant en FCFA
    """
    formulaires = db.get_formulaires()
    formulaire = next((f for f in formulaires if f['id'] == formulaire_id), None)

    if not formulaire:
        raise ValueError(f"Formulaire ID {formulaire_id} introuvable")

    return formulaire['cout_standard']


def calculer_montant_location(location_id: int, duree: int) -> float:
    """
    Calcule le montant d'une location selon la durée.

    Args:
        location_id: ID de la location
        duree: Durée (en unité correspondant à la fréquence)

    Returns:
        Montant total en FCFA
    """
    locations = db.get_locations()
    location = next((l for l in locations if l['id'] == location_id), None)

    if not location:
        raise ValueError(f"Location ID {location_id} introuvable")

    return location['prix_base'] * duree


def enregistrer_paiement_taxe(taxe_id: int, citoyen_id: int = None, agent_id: int = None,
                                montant_custom: float = None, nom_commercant: str = None,
                                numero_commercant: str = None, mode_paiement: str = 'Espèces',
                                **params) -> int:
    """
    Enregistre un paiement de taxe municipale.

    Args:
        taxe_id: ID de la taxe
        citoyen_id: ID du citoyen (optionnel)
        agent_id: ID de l'agent qui enregistre
        montant_custom: Montant personnalisé (sinon calcul auto)
        nom_commercant: Nom du commerçant/contribuable
        numero_commercant: Numéro du commerçant/contribuable
        mode_paiement: Mode de paiement (Espèces, Airtel Money, MobiCash, etc.)
        **params: Paramètres pour le calcul (ex: montant_base)

    Returns:
        ID de la transaction créée
    """
    # Récupérer infos taxe
    taxes = db.get_taxes()
    taxe = next((t for t in taxes if t['id'] == taxe_id), None)

    if not taxe:
        raise ValueError(f"Taxe ID {taxe_id} introuvable")

    # Calculer montant
    if montant_custom:
        montant = montant_custom
    else:
        montant = calculer_montant_taxe(taxe_id, **params)

    # Créer libellé
    libelle = f"TAXE_{taxe['nom_taxe'].upper().replace(' ', '_')} - {taxe['categorie']}"

    # Enregistrer transaction
    tx_id = db.create_transaction(
        type_tx=f"TAXE_{taxe['nom_taxe'][:20].upper()}",
        libelle=libelle,
        montant=montant,
        citoyen_id=citoyen_id,
        agent_id=agent_id,
        mode_paiement=mode_paiement,
        nom_commercant=nom_commercant,
        numero_commercant=numero_commercant
    )

    logger.info(f"Paiement taxe enregistré: {libelle} - {montant} FCFA")

    # Vérifier anomalies (passer tx_id pour inclure référence dans l'alerte si besoin)
    verifier_anomalie_montant(montant, taxe['montant_fixe'] or 0, libelle, transaction_db_id=tx_id)

    return tx_id


def enregistrer_paiement_acte(formulaire_id: int, citoyen_id: int = None, agent_id: int = None,
                                nom_commercant: str = None, numero_commercant: str = None,
                                mode_paiement: str = 'Espèces') -> int:
    """
    Enregistre un paiement pour un acte administratif.

    Args:
        formulaire_id: ID du formulaire/acte
        citoyen_id: ID du citoyen (optionnel)
        agent_id: ID de l'agent
        nom_commercant: Nom du demandeur
        numero_commercant: Numéro d'identification du demandeur
        mode_paiement: Mode de paiement (Espèces, Airtel Money, MobiCash, etc.)

    Returns:
        ID de la transaction créée
    """
    # Récupérer infos formulaire
    formulaires = db.get_formulaires()
    formulaire = next((f for f in formulaires if f['id'] == formulaire_id), None)

    if not formulaire:
        raise ValueError(f"Formulaire ID {formulaire_id} introuvable")

    montant = formulaire['cout_standard']
    libelle = f"ACTE_{formulaire['nom_document'].upper()}"

    # Enregistrer transaction
    tx_id = db.create_transaction(
        type_tx=f"ACTE_{formulaire['nom_document'][:20].upper()}",
        libelle=libelle,
        montant=montant,
        citoyen_id=citoyen_id,
        agent_id=agent_id,
        mode_paiement=mode_paiement,
        nom_commercant=nom_commercant,
        numero_commercant=numero_commercant
    )

    logger.info(f"Paiement acte enregistré: {libelle} - {montant} FCFA")

    # Vérifier anomalies et inclure référence si besoin
    verifier_anomalie_montant(montant, formulaire.get('cout_standard', 0), libelle, transaction_db_id=tx_id)

    return tx_id


def enregistrer_paiement_location(location_id: int, duree: int, date_debut: str,
                                    demandeur: str, citoyen_id: int = None, agent_id: int = None,
                                    nom_commercant: str = None, numero_commercant: str = None,
                                    mode_paiement: str = 'Espèces') -> int:
    """
    Enregistre un paiement de location et crée la réservation.

    Args:
        location_id: ID de la location
        duree: Durée de la location
        date_debut: Date de début (format YYYY-MM-DD)
        demandeur: Nom du demandeur
        citoyen_id: ID du citoyen (optionnel)
        agent_id: ID de l'agent
        nom_commercant: Nom du demandeur
        numero_commercant: Numéro d'identification du demandeur
        mode_paiement: Mode de paiement (Espèces, Airtel Money, MobiCash, etc.)

    Returns:
        ID de la transaction créée
    """
    # Récupérer infos location
    locations = db.get_locations()
    location = next((l for l in locations if l['id'] == location_id), None)

    if not location:
        raise ValueError(f"Location ID {location_id} introuvable")

    # Calculer montant total
    montant_total = calculer_montant_location(location_id, duree)

    libelle = f"LOCATION_{location['type_location'].upper()} - {location['designation']}"

    # Enregistrer transaction
    tx_id = db.create_transaction(
        type_tx=f"LOCATION_{location['type_location'].upper()}",
        libelle=libelle,
        montant=montant_total,
        citoyen_id=citoyen_id,
        agent_id=agent_id,
        mode_paiement=mode_paiement,
        nom_commercant=nom_commercant,
        numero_commercant=numero_commercant
    )

    # Créer réservation
    date_debut_obj = datetime.strptime(date_debut, '%Y-%m-%d')
    date_fin = date_debut_obj + timedelta(days=duree if 'Jour' in location['frequence'] else duree * 30)

    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO reservations
        (location_id, citoyen_id, demandeur, date_debut, date_fin, duree_jours, montant_total, transaction_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (location_id, citoyen_id, demandeur, date_debut, date_fin.strftime('%Y-%m-%d'), duree, montant_total, f"TX-{tx_id}"))
    conn.commit()
    conn.close()

    logger.info(f"Location enregistrée: {libelle} - {montant_total} FCFA")

    return tx_id


def verifier_anomalie_montant(montant_paye: float, montant_attendu: float, libelle: str, transaction_db_id: int = None):
    """
    Vérifie si un montant payé est anormal et crée une alerte si nécessaire.

    Args:
        montant_paye: Montant réellement payé
        montant_attendu: Montant normalement attendu
        libelle: Description de la transaction
    """
    if montant_attendu == 0:
        return  # Pas de montant de référence

    # Calcul écart en pourcentage
    ecart_pct = abs(montant_paye - montant_attendu) / montant_attendu * 100

    # Si écart > 20%, créer alerte
    if ecart_pct > 20:
        # Construire description
        desc = f"{libelle}: Montant payé {montant_paye} FCFA vs attendu {montant_attendu} FCFA (écart {ecart_pct:.1f}%)"

        # Si on a l'ID de la transaction en base, récupérer la référence complète
        reference = None
        try:
            if transaction_db_id:
                conn = db.get_connection()
                cursor = conn.cursor()
                cursor.execute('SELECT numero_recu, nom_commercant, numero_commercant FROM transactions WHERE id = ?', (transaction_db_id,))
                row = cursor.fetchone()
                conn.close()
                if row:
                    nr = row['numero_recu'] or ''
                    nom = row['nom_commercant'] or ''
                    num = row['numero_commercant'] or ''
                    if nom:
                        reference = f"{nr} - {nom}{' ('+str(num)+')' if num else ''}"
                    else:
                        reference = nr
        except Exception:
            reference = None

        db.create_alerte(
            titre=f"Anomalie montant détectée",
            description=desc,
            type_alerte="ANOMALIE_TAXE",
            montant=montant_paye,
            niveau="CRITIQUE" if ecart_pct > 50 else "NORMAL",
            reference=reference
        )
        logger.warning(f"Anomalie détectée: {libelle} - Écart de {ecart_pct:.1f}%")


def detecter_recettes_faibles():
    """
    Détecte si les recettes du jour sont anormalement faibles.
    Compare avec la moyenne des 7 derniers jours.
    """
    conn = db.get_connection()
    cursor = conn.cursor()

    # Recettes du jour
    cursor.execute('''
        SELECT COALESCE(SUM(montant), 0) FROM transactions
        WHERE DATE(date_creation) = DATE('now') AND statut = 'COMPLETE'
    ''')
    recettes_jour = cursor.fetchone()[0]

    # Moyenne des 7 derniers jours
    cursor.execute('''
        SELECT COALESCE(AVG(daily_total), 0) FROM (
            SELECT DATE(date_creation) as day, SUM(montant) as daily_total
            FROM transactions
            WHERE date_creation >= DATE('now', '-7 days')
            AND date_creation < DATE('now')
            AND statut = 'COMPLETE'
            GROUP BY DATE(date_creation)
        )
    ''')
    moyenne_semaine = cursor.fetchone()[0]

    conn.close()

    # Si recettes < 50% de la moyenne, alerte
    if moyenne_semaine > 0 and recettes_jour < (moyenne_semaine * 0.5):
        db.create_alerte(
            titre="Recettes journalières faibles",
            description=f"Recettes du jour: {recettes_jour:,.0f} FCFA vs moyenne: {moyenne_semaine:,.0f} FCFA",
            type_alerte="RECETTE_FAIBLE",
            montant=recettes_jour,
            niveau="NORMAL"
        )
        logger.warning(f"Recettes faibles détectées: {recettes_jour} vs {moyenne_semaine}")


def get_rapport_journalier() -> dict:
    """
    Génère un rapport des activités de la journée.

    Returns:
        Dictionnaire avec les statistiques du jour
    """
    conn = db.get_connection()
    cursor = conn.cursor()

    # Recettes par type
    cursor.execute('''
        SELECT
            CASE
                WHEN type LIKE 'TAXE%' THEN 'Taxes'
                WHEN type LIKE 'ACTE%' THEN 'Actes'
                WHEN type LIKE 'LOCATION%' THEN 'Locations'
                ELSE 'Divers'
            END as categorie,
            COUNT(*) as nombre,
            SUM(montant) as total
        FROM transactions
        WHERE DATE(date_creation) = DATE('now')
        AND statut = 'COMPLETE'
        GROUP BY categorie
    ''')

    recettes_par_type = {}
    for row in cursor.fetchall():
        recettes_par_type[row[0]] = {
            'nombre': row[1],
            'total': row[2]
        }

    # Total général
    cursor.execute('''
        SELECT COUNT(*), COALESCE(SUM(montant), 0)
        FROM transactions
        WHERE DATE(date_creation) = DATE('now')
        AND statut = 'COMPLETE'
    ''')
    total_tx, total_montant = cursor.fetchone()

    conn.close()

    return {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'total_transactions': total_tx,
        'total_recettes': total_montant,
        'par_categorie': recettes_par_type
    }


# Pour compatibilité avec l'ancien code (à supprimer après migration)
def simulate_daily_revenue(nb_transactions: int = 10):
    """
    DEPRECATED: Fonction de simulation à supprimer.
    Utiliser les fonctions réelles d'enregistrement de paiements.
    """
    logger.warning("simulate_daily_revenue est deprecated - Utilisez les fonctions réelles")
    return 0
