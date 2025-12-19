# ia_surveillance.py - Intelligence Artificielle de Surveillance des Recettes
"""
Système IA qui surveille en temps réel les recettes municipales pour détecter:
- Fraudes et tentatives de détournement
- Anomalies de paiement
- Patterns suspects
- Fuites de données
- Écarts anormaux
"""

import database_mairie as db
from datetime import datetime, timedelta
from logger import get_logger
import statistics

logger = get_logger(__name__)


class SurveillanceIA:
    """Intelligence Artificielle de surveillance des recettes municipales."""

    def __init__(self):
        self.seuil_ecart_normal = 20  # % d'écart acceptable
        self.seuil_recette_faible = 50  # % de baisse par rapport à la moyenne
        self.seuil_transaction_suspecte = 100000  # FCFA - montant suspect

    def analyser_transaction_en_temps_reel(self, transaction_id: int) -> dict:
        """
        Analyse une transaction dès qu'elle est créée.

        Returns:
            dict: {
                'status': 'OK' | 'ALERTE' | 'CRITIQUE',
                'anomalies': [],
                'score_confiance': 0-100,
                'recommandations': []
            }
        """
        conn = db.get_connection()
        cursor = conn.cursor()

        # Récupérer la transaction
        cursor.execute('SELECT * FROM transactions WHERE id = ?', (transaction_id,))
        transaction = cursor.fetchone()

        if not transaction:
            conn.close()
            return {'status': 'ERREUR', 'message': 'Transaction introuvable'}

        anomalies = []
        score_confiance = 100  # On commence à 100% de confiance
        recommandations = []

        tx_type = transaction[2]  # type
        montant = transaction[4]  # montant
        agent_id = transaction[6]  # agent_id
        date_creation = transaction[9]  # date_creation

        # 1. VÉRIFICATION MONTANT ANORMAL
        if "TAXE" in tx_type:
            # Vérifier si le montant correspond aux tarifs standards
            cursor.execute('''
                SELECT AVG(montant) as moy, MIN(montant) as min, MAX(montant) as max
                FROM transactions
                WHERE type LIKE ? AND statut = 'COMPLETE'
            ''', (f'{tx_type[:10]}%',))
            stats = cursor.fetchone()

            if stats and stats[0]:
                moyenne = stats[0]
                ecart = abs(montant - moyenne) / moyenne * 100

                if ecart > self.seuil_ecart_normal:
                    anomalies.append({
                        'type': 'MONTANT_ANORMAL',
                        'severite': 'CRITIQUE' if ecart > 50 else 'MOYENNE',
                        'details': f'Écart de {ecart:.1f}% par rapport à la moyenne ({moyenne:.0f} FCFA)',
                        'montant_attendu': moyenne,
                        'montant_reel': montant
                    })
                    score_confiance -= min(30, int(ecart))
                    recommandations.append("Vérifier la justification de cet écart avec l'agent")

        # 2. MONTANT TROP ÉLEVÉ (Possible fraude)
        if montant > self.seuil_transaction_suspecte:
            anomalies.append({
                'type': 'MONTANT_ELEVE_SUSPECT',
                'severite': 'CRITIQUE',
                'details': f'Montant inhabituellement élevé: {montant:,.0f} FCFA',
                'montant_reel': montant
            })
            score_confiance -= 25
            recommandations.append("⚠️ VALIDATION MANAGERIALE REQUISE")
            recommandations.append("Demander justificatifs et pièces comptables")

        # 3. AGENT AVEC ACTIVITÉ SUSPECTE
        cursor.execute('''
            SELECT COUNT(*), SUM(montant), AVG(montant)
            FROM transactions
            WHERE agent_id = ?
            AND DATE(date_creation) = DATE('now')
            AND statut = 'COMPLETE'
        ''', (agent_id,))

        agent_stats = cursor.fetchone()
        if agent_stats:
            nb_tx_agent = agent_stats[0]
            total_agent = agent_stats[1] or 0

            # Plus de 20 transactions par jour = suspect
            if nb_tx_agent > 20:
                anomalies.append({
                    'type': 'ACTIVITE_AGENT_SUSPECTE',
                    'severite': 'MOYENNE',
                    'details': f'Agent a effectué {nb_tx_agent} transactions aujourd\'hui',
                    'agent_id': agent_id
                })
                score_confiance -= 15
                recommandations.append(f"Auditer les transactions de l'agent #{agent_id}")

            # Montant total journalier agent > 500k = suspect
            if total_agent > 500000:
                anomalies.append({
                    'type': 'RECETTES_AGENT_ELEVEES',
                    'severite': 'MOYENNE',
                    'details': f'Agent a encaissé {total_agent:,.0f} FCFA aujourd\'hui',
                    'agent_id': agent_id,
                    'montant_total': total_agent
                })
                score_confiance -= 10
                recommandations.append("Vérifier l'intégrité du registre de l'agent")

        # 4. HORAIRES SUSPECTS
        heure_tx = datetime.fromisoformat(date_creation).hour

        # Transaction hors heures ouvrables (avant 7h ou après 19h)
        if heure_tx < 7 or heure_tx > 19:
            anomalies.append({
                'type': 'HORAIRE_SUSPECT',
                'severite': 'CRITIQUE',
                'details': f'Transaction enregistrée à {heure_tx}h (hors heures ouvrables)',
                'heure': heure_tx
            })
            score_confiance -= 30
            recommandations.append("🚨 TRANSACTION HORS HEURES - Vérification urgente requise")

        # 5. TRANSACTIONS RÉPÉTÉES RAPIDES (Possible doublon frauduleux)
        cursor.execute('''
            SELECT COUNT(*)
            FROM transactions
            WHERE agent_id = ?
            AND type = ?
            AND montant = ?
            AND datetime(date_creation) > datetime('now', '-5 minutes')
            AND id != ?
        ''', (agent_id, tx_type, montant, transaction_id))

        tx_similaires = cursor.fetchone()[0]
        if tx_similaires > 0:
            anomalies.append({
                'type': 'DOUBLON_SUSPECT',
                'severite': 'CRITIQUE',
                'details': f'{tx_similaires + 1} transaction(s) identique(s) en moins de 5 minutes',
                'nb_doublons': tx_similaires + 1
            })
            score_confiance -= 40
            recommandations.append("🚨 DOUBLON DÉTECTÉ - Annuler si nécessaire")

        conn.close()

        # Déterminer le statut final
        if score_confiance < 50:
            status = 'CRITIQUE'
        elif score_confiance < 75:
            status = 'ALERTE'
        else:
            status = 'OK'

        # Logger l'analyse
        if status != 'OK':
            logger.warning(f"IA: Transaction #{transaction_id} - Status {status} - Score {score_confiance}%")

            # Créer une alerte automatique
            if anomalies:
                titre_alerte = f"🤖 IA: {anomalies[0]['type']}"
                details_alerte = f"Transaction #{transaction_id}: " + ", ".join([a['details'] for a in anomalies[:2]])

                db.create_alerte(
                    titre=titre_alerte,
                    description=details_alerte,
                    type_alerte=anomalies[0]['type'],
                    montant=montant,
                    niveau='CRITIQUE' if status == 'CRITIQUE' else 'NORMAL'
                )

        return {
            'status': status,
            'anomalies': anomalies,
            'score_confiance': score_confiance,
            'recommandations': recommandations,
            'transaction_id': transaction_id
        }


    def surveillance_recettes_journalieres(self) -> dict:
        """
        Surveille les recettes de la journée et détecte les anomalies globales.

        Returns:
            dict: Rapport de surveillance
        """
        conn = db.get_connection()
        cursor = conn.cursor()

        # Recettes du jour
        cursor.execute('''
            SELECT COALESCE(SUM(montant), 0), COUNT(*)
            FROM transactions
            WHERE DATE(date_creation) = DATE('now') AND statut = 'COMPLETE'
        ''')
        recettes_jour, nb_tx_jour = cursor.fetchone()

        # Moyenne des 7 derniers jours (hors aujourd'hui)
        cursor.execute('''
            SELECT COALESCE(AVG(daily_total), 0), COALESCE(AVG(daily_count), 0)
            FROM (
                SELECT DATE(date_creation) as day, SUM(montant) as daily_total, COUNT(*) as daily_count
                FROM transactions
                WHERE date_creation >= DATE('now', '-7 days')
                AND date_creation < DATE('now')
                AND statut = 'COMPLETE'
                GROUP BY DATE(date_creation)
            )
        ''')
        moyenne_semaine, moyenne_tx = cursor.fetchone()

        anomalies_globales = []

        # ALERTE 1: Baisse anormale des recettes
        if moyenne_semaine > 0:
            baisse_pct = ((moyenne_semaine - recettes_jour) / moyenne_semaine) * 100

            if recettes_jour < (moyenne_semaine * (self.seuil_recette_faible / 100)):
                anomalies_globales.append({
                    'type': 'RECETTES_ANORMALEMENT_FAIBLES',
                    'severite': 'MOYENNE',
                    'details': f'Recettes du jour: {recettes_jour:,.0f} FCFA ({baisse_pct:.1f}% sous la moyenne)',
                    'recettes_jour': recettes_jour,
                    'moyenne_attendue': moyenne_semaine
                })

                # Créer alerte
                db.create_alerte(
                    titre="🤖 IA: Recettes anormalement faibles",
                    description=f"Recettes du jour ({recettes_jour:,.0f} FCFA) inférieures de {baisse_pct:.1f}% à la moyenne hebdomadaire",
                    type_alerte="RECETTE_FAIBLE_IA",
                    montant=recettes_jour,
                    niveau="NORMAL"
                )

        # ALERTE 2: Nombre de transactions anormalement bas
        if moyenne_tx > 0 and nb_tx_jour < (moyenne_tx * 0.5):
            anomalies_globales.append({
                'type': 'ACTIVITE_FAIBLE',
                'severite': 'MOYENNE',
                'details': f'Seulement {nb_tx_jour} transactions vs {moyenne_tx:.0f} en moyenne',
                'nb_tx_jour': nb_tx_jour,
                'moyenne_tx': moyenne_tx
            })

        # ALERTE 3: Pic anormal de recettes (possible fraude ou erreur)
        if moyenne_semaine > 0 and recettes_jour > (moyenne_semaine * 2):
            hausse_pct = ((recettes_jour - moyenne_semaine) / moyenne_semaine) * 100
            anomalies_globales.append({
                'type': 'RECETTES_ANORMALEMENT_ELEVEES',
                'severite': 'CRITIQUE',
                'details': f'Recettes du jour: {recettes_jour:,.0f} FCFA (+{hausse_pct:.1f}% vs moyenne)',
                'recettes_jour': recettes_jour,
                'moyenne_attendue': moyenne_semaine
            })

            db.create_alerte(
                titre="🤖 IA: Pic anormal de recettes",
                description=f"Recettes du jour ({recettes_jour:,.0f} FCFA) supérieures de {hausse_pct:.1f}% à la moyenne - Vérifier l'intégrité",
                type_alerte="RECETTE_ELEVEE_SUSPECTE",
                montant=recettes_jour,
                niveau="CRITIQUE"
            )

        conn.close()

        return {
            'recettes_jour': recettes_jour,
            'moyenne_semaine': moyenne_semaine,
            'nb_transactions': nb_tx_jour,
            'anomalies': anomalies_globales,
            'status': 'CRITIQUE' if any(a['severite'] == 'CRITIQUE' for a in anomalies_globales) else 'OK'
        }


    def detecter_patterns_frauduleux(self, jours: int = 7) -> list:
        """
        Détecte les patterns de fraude sur une période donnée.

        Args:
            jours: Nombre de jours à analyser

        Returns:
            list: Liste des patterns suspects détectés
        """
        conn = db.get_connection()
        cursor = conn.cursor()

        patterns_suspects = []

        # PATTERN 1: Agent avec trop de transactions de montants ronds
        cursor.execute('''
            SELECT agent_id, COUNT(*) as nb_ronds, SUM(montant) as total
            FROM transactions
            WHERE date_creation >= DATE('now', ?)
            AND montant % 10000 = 0
            AND statut = 'COMPLETE'
            GROUP BY agent_id
            HAVING nb_ronds > 10
        ''', (f'-{jours} days',))

        for row in cursor.fetchall():
            patterns_suspects.append({
                'type': 'MONTANTS_RONDS_SUSPECTS',
                'agent_id': row[0],
                'nb_transactions': row[1],
                'total': row[2],
                'details': f'Agent #{row[0]}: {row[1]} transactions avec montants ronds ({row[2]:,.0f} FCFA)'
            })

        # PATTERN 2: Mêmes montants répétés (possible fraude systématique)
        cursor.execute('''
            SELECT agent_id, montant, COUNT(*) as repetitions
            FROM transactions
            WHERE date_creation >= DATE('now', ?)
            AND statut = 'COMPLETE'
            GROUP BY agent_id, montant
            HAVING repetitions > 5
        ''', (f'-{jours} days',))

        for row in cursor.fetchall():
            patterns_suspects.append({
                'type': 'REPETITION_SUSPECTE',
                'agent_id': row[0],
                'montant': row[1],
                'repetitions': row[2],
                'details': f'Agent #{row[0]}: Montant {row[1]:,.0f} FCFA répété {row[2]} fois'
            })

        # PATTERN 3: Augmentation soudaine d'activité d'un agent
        cursor.execute('''
            SELECT agent_id,
                   COUNT(*) as nb_recent,
                   (SELECT COUNT(*) FROM transactions t2
                    WHERE t2.agent_id = t1.agent_id
                    AND date_creation < DATE('now', '-7 days')
                    AND date_creation >= DATE('now', '-14 days')) as nb_avant
            FROM transactions t1
            WHERE date_creation >= DATE('now', '-7 days')
            AND statut = 'COMPLETE'
            GROUP BY agent_id
        ''')

        for row in cursor.fetchall():
            nb_recent = row[1]
            nb_avant = row[2]

            if nb_avant > 0 and nb_recent > (nb_avant * 3):
                patterns_suspects.append({
                    'type': 'AUGMENTATION_ACTIVITE',
                    'agent_id': row[0],
                    'nb_recent': nb_recent,
                    'nb_avant': nb_avant,
                    'details': f'Agent #{row[0]}: Activité x{nb_recent/nb_avant:.1f} en 7 jours'
                })

        conn.close()

        # Créer des alertes pour les patterns détectés
        for pattern in patterns_suspects:
            db.create_alerte(
                titre=f"🤖 IA: Pattern suspect - {pattern['type']}",
                description=pattern['details'],
                type_alerte=f"PATTERN_{pattern['type']}",
                montant=pattern.get('total', 0),
                niveau="CRITIQUE"
            )

        return patterns_suspects


    def get_score_integrite_global(self) -> dict:
        """
        Calcule un score d'intégrité global du système (0-100).

        Returns:
            dict: {
                'score': 0-100,
                'niveau': 'EXCELLENT' | 'BON' | 'MOYEN' | 'FAIBLE' | 'CRITIQUE',
                'facteurs': []
            }
        """
        score = 100
        facteurs = []

        conn = db.get_connection()
        cursor = conn.cursor()

        # Facteur 1: Nombre d'alertes critiques non résolues
        cursor.execute('''
            SELECT COUNT(*) FROM alertes
            WHERE traitee = 0 AND niveau_priorite = 'CRITIQUE'
        ''')
        alertes_critiques = cursor.fetchone()[0]

        if alertes_critiques > 5:
            score -= 30
            facteurs.append(f"❌ {alertes_critiques} alertes critiques non résolues")
        elif alertes_critiques > 0:
            score -= 10
            facteurs.append(f"⚠️ {alertes_critiques} alertes critiques")
        else:
            facteurs.append("✅ Aucune alerte critique")

        # Facteur 2: Régularité des recettes
        cursor.execute('''
            SELECT date_creation, montant
            FROM transactions
            WHERE date_creation >= DATE('now', '-7 days')
            AND statut = 'COMPLETE'
            ORDER BY date_creation DESC
        ''')

        recettes = [row[1] for row in cursor.fetchall()]

        if len(recettes) > 5:
            try:
                ecart_type = statistics.stdev(recettes)
                moyenne = statistics.mean(recettes)
                coefficient_variation = (ecart_type / moyenne) * 100 if moyenne > 0 else 0

                if coefficient_variation > 50:
                    score -= 15
                    facteurs.append(f"⚠️ Forte variabilité des transactions ({coefficient_variation:.1f}%)")
                else:
                    facteurs.append("✅ Transactions régulières")
            except:
                pass

        # Facteur 3: Transactions hors heures
        cursor.execute('''
            SELECT COUNT(*)
            FROM transactions
            WHERE date_creation >= DATE('now', '-7 days')
            AND (CAST(strftime('%H', date_creation) AS INTEGER) < 7
                 OR CAST(strftime('%H', date_creation) AS INTEGER) > 19)
        ''')
        tx_hors_heures = cursor.fetchone()[0]

        if tx_hors_heures > 5:
            score -= 25
            facteurs.append(f"❌ {tx_hors_heures} transactions hors heures")
        elif tx_hors_heures > 0:
            score -= 10
            facteurs.append(f"⚠️ {tx_hors_heures} transactions hors heures")
        else:
            facteurs.append("✅ Toutes transactions en heures ouvrables")

        conn.close()

        # Déterminer le niveau
        if score >= 90:
            niveau = "EXCELLENT"
        elif score >= 75:
            niveau = "BON"
        elif score >= 60:
            niveau = "MOYEN"
        elif score >= 40:
            niveau = "FAIBLE"
        else:
            niveau = "CRITIQUE"

        return {
            'score': max(0, score),
            'niveau': niveau,
            'facteurs': facteurs,
            'timestamp': datetime.now().isoformat()
        }


# Instance globale de l'IA
ia_surveillance = SurveillanceIA()


def analyser_nouvelle_transaction(transaction_id: int):
    """
    Fonction appelée automatiquement après chaque transaction.

    Args:
        transaction_id: ID de la transaction à analyser
    """
    return ia_surveillance.analyser_transaction_en_temps_reel(transaction_id)


def lancer_surveillance_quotidienne():
    """Lance la surveillance quotidienne des recettes."""
    rapport = ia_surveillance.surveillance_recettes_journalieres()
    patterns = ia_surveillance.detecter_patterns_frauduleux(jours=7)

    logger.info(f"IA Surveillance: {len(rapport.get('anomalies', []))} anomalies détectées")
    logger.info(f"IA Surveillance: {len(patterns)} patterns suspects détectés")

    return {
        'rapport_quotidien': rapport,
        'patterns_frauduleux': patterns
    }
