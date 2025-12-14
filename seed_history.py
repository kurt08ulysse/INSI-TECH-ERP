# seed_history.py - Injecte un historique de 90 jours pour les prédictions IA
import sqlite3
from datetime import datetime, timedelta
import random

DB_PATH = "stock_manager.db"

def seed_historical_revenue(days=90):
    """Injecte des transactions historiques cohérentes pour l'IA."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Vérifier si on a déjà des données historiques
    c.execute("SELECT COUNT(*) FROM transactions WHERE date_creation < date('now')")
    existing = c.fetchone()[0]
    
    if existing > 50:
        print(f"⚠️ Il y a déjà {existing} transactions historiques. Abandon.")
        conn.close()
        return
    
    print(f"🚀 Injection de {days} jours d'historique...")
    
    taxes = ["TAXE - Patente", "TAXE - Foncière", "TAXE - Résidence"]
    actes = ["ACTE - Naissance", "ACTE - Mariage", "ACTE - Décès", "ACTE - Certificat"]
    
    base_revenue = 12000  # Montant de base journalier
    trend_factor = 100     # Croissance par jour (tendance haussière)
    
    for i in range(days, 0, -1):
        date = datetime.now() - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d %H:%M:%S")
        
        # 3 à 8 transactions par jour
        nb_transactions = random.randint(3, 8)
        
        for _ in range(nb_transactions):
            if random.random() < 0.6:
                type_tx = random.choice(taxes)
                montant = random.choice([5000, 10000, 15000, 20000, 25000])
            else:
                type_tx = random.choice(actes)
                montant = random.choice([2500, 5000, 7500, 10000])
            
            # Ajouter une tendance haussière progressive
            trend_bonus = int((days - i) * trend_factor / days)
            montant += trend_bonus
            
            hashscan = f"https://hashscan.io/testnet/transaction/0.0.{random.randint(10000,99999)}"
            
            c.execute('''
                INSERT INTO transactions (contrat_id, type, montant, transaction_id, hashscan_url, statut, date_creation)
                VALUES (NULL, ?, ?, ?, ?, 'COMPLETE', ?)
            ''', (type_tx, montant, f"HIST_{i}_{_}", hashscan, date_str))
    
    conn.commit()
    conn.close()
    print(f"✅ {days} jours d'historique injectés avec succès !")

if __name__ == "__main__":
    seed_historical_revenue()
