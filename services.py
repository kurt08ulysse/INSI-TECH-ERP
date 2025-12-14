
import database as db
import random
import datetime
import time

# ==================== SIMULATION RECETTES ====================

def simulate_daily_revenue(nb_transactions: int) -> int:
    """
    Simule une journée d'encaissements (Taxes & Actes).
    Retourne le montant total généré.
    """
    taxes = db.get_taxes()
    docs = db.get_formulaires()
    
    total_gagne = 0
    
    # Si pas de données, on ne peut rien simuler (ou alors fausses données hardcodées ?)
    # On va assumer que database.py a seeded les données.
    
    for _ in range(nb_transactions):
        # Choix aléatoire : 60% Taxe, 40% Acte
        if taxes and random.random() < 0.6:
            item = random.choice(taxes)
            nom = f"TAXE - {item['nom_taxe']}"
            # Logique montant: fixe ou aléatoire si 0
            montant = item['montant_fixe'] or random.choice([5000, 10000, 15000, 25000, 50000])
            detail = f"Contribuable_{random.randint(100,999)}"
        elif docs:
            item = random.choice(docs)
            nom = f"ACTE - {item['nom_document']}"
            montant = item['cout_standard']
            detail = f"Citoyen_{random.randint(100,999)}"
        else:
            continue

        # Simulation Blockchain
        hashscan = f"https://hashscan.io/testnet/transaction/0.0.{random.randint(10000,99999)}@{datetime.datetime.now().timestamp()}"
        
        # Enregistrement DB
        db.create_transaction(
            contrat_id=None,
            type_tx=nom,
            montant=montant,
            transaction_id=detail,
            hashscan_url=hashscan
        )
        
        # 30% de chance d'anomalie
        anomalie_type = None
        if random.random() < 0.3:
            r = random.random()
            if r < 0.33:
                # 1. ANOMALIE_TAXE (Montant suspect)
                montant = montant * 0.1 # Trop faible
                anomalie_type = "ANOMALIE_TAXE"
                detail += " (Montant suspect)"
            elif r < 0.66:
                # 2. RETARD_PAIEMENT (Simulé)
                detail += " (RETARD)"
                anomalie_type = "RETARD_PAIEMENT"
                # On ne change pas le montant mais on flag
            else:
                # 3. CRITIQUE (Fraude ou Erreur Grave)
                anomalie_type = "CRITIQUE_FINANCIER"
                montant = 0 # Echec du paiement
                detail += " (ECHEC CRITIQUE)"

        if montant >= 40000:
            # Création d'une alerte financière (Montant élevé)
            conn = db.get_connection()
            c = conn.cursor()
            c.execute('''
                INSERT INTO alertes (matiere, quantite, type, traitee, date_creation)
                VALUES (?, ?, 'GROS_PAIEMENT', 0, CURRENT_TIMESTAMP)
            ''', (nom, int(montant)))
            conn.commit()
            conn.close()
            
        if anomalie_type:
            conn = db.get_connection()
            c = conn.cursor()
            c.execute('''
                INSERT INTO alertes (matiere, quantite, type, traitee, date_creation)
                VALUES (?, ?, ?, 0, CURRENT_TIMESTAMP)
            ''', (nom, int(montant), anomalie_type))
            conn.commit()
            conn.close()

        total_gagne += montant
        time.sleep(0.05) # Petit délai pour l'effet "traitement"
        
    # Check Tendance Globale (Recette Faible)
    if total_gagne < 10000 and nb_transactions > 2:
         conn = db.get_connection()
         c = conn.cursor()
         c.execute('''
            INSERT INTO alertes (matiere, quantite, type, traitee, date_creation)
            VALUES (?, ?, 'RECETTE_FAIBLE', 0, CURRENT_TIMESTAMP)
        ''', ("Global Journalier", int(total_gagne)))
         conn.commit()
         conn.close()

    return total_gagne

def simulate_stock_consumption(nb_operations: int = 5):
    """
    Simule une consommation de stocks (sorties de matériel).
    Réduit les quantités et crée des transactions 'UTILISATION'.
    """
    stocks = db.get_all_stocks()
    if not stocks:
        return 0

    conn = db.get_connection()
    c = conn.cursor()
    
    count_critique = 0
    
    for _ in range(nb_operations):
        item = random.choice(stocks)
        # Consommation aléatoire entre 1 et 10% du stock actuel
        qty_remove = random.randint(1, max(5, int(item['quantite'] * 0.1)))
        
        new_qty = max(0, item['quantite'] - qty_remove)
        
        # Mise à jour DB
        c.execute("UPDATE stocks SET quantite = ? WHERE id = ?", (new_qty, item['id']))
        
        # Log transaction
        hashscan = f"https://hashscan.io/testnet/transaction/0.0.{random.randint(10000,99999)}"
        c.execute('''
            INSERT INTO transactions (type, montant, transaction_id, hashscan_url, statut)
            VALUES (?, ?, ?, ?, 'COMPLETE')
        ''', (f"SORTIE - {item['nom']}", 0, f"Simu (-{qty_remove})", hashscan))
        
        if new_qty < item['seuil_critique']:
            count_critique += 1
            # Création de l'alerte
            c.execute('''
                INSERT INTO alertes (matiere, quantite, type, traitee, date_creation)
                VALUES (?, ?, 'STOCK_CRITIQUE', 0, CURRENT_TIMESTAMP)
            ''', (item['nom'], new_qty))
            
    conn.commit()
    conn.close()
    return count_critique

# ==================== GUICHET ====================

def process_guichet_payment(type_acte: str, montant: float, demandeur: str, infos_add: str = "") -> str:
    """
    Traite un paiement au guichet (Acte ou Taxe).
    Retourne l'ID de transaction (hashscanUrl ou ID interne).
    """
    timestamp = datetime.datetime.now().timestamp()
    hashscan = f"https://hashscan.io/testnet/transaction/0.0.{random.randint(10000,99999)}@{timestamp}"
    
    transaction_id_str = f"{demandeur} {infos_add}".strip()
    
    db.create_transaction(
        contrat_id=None,
        type_tx=type_acte,
        montant=montant,
        transaction_id=transaction_id_str,
        hashscan_url=hashscan
    )
    
    return hashscan

def process_reservation(ressource: str, demandeur: str, date_debut: str, duree: int, montant: float):
    """
    Gère une réservation de salle/matériel.
    """
    timestamp = datetime.datetime.now().timestamp()
    hashscan = f"https://hashscan.io/testnet/transaction/0.0.{random.randint(10000,99999)}@{timestamp}"
    
    # 1. Transaction Financière
    db.create_transaction(
        contrat_id=None,
        type_tx=f"LOCATION - {ressource}",
        montant=montant,
        transaction_id=f"{demandeur} ({duree}j)",
        hashscan_url=hashscan
    )
    
    # 2. Enregistrement Planning
    db.create_reservation(
        ressource=ressource,
        demandeur=demandeur,
        date_debut=date_debut,
        duree=duree,
        transaction_id=hashscan
    )
    
    return hashscan
