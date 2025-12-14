# db_seeder.py - Remplissage de la DB avec des fausses données

import database as db
import random
from datetime import datetime, timedelta

def seed_data():
    """Remplit la base de données avec des transactions et contrats fictifs."""
    conn = db.get_connection()
    c = conn.cursor()
    
    print("🌱 Seeding de la database en cours...")
    
    matieres = ["PAPIER A4", "ENCRE IMPRIMANTE", "AMPOULES PUBLIC", "CIMENT", "GAZOLE", "KITS SCOLAIRES"]
    fournisseurs_noms = ["Bureautique Pro", "BTP Services", "Energie Locale", "Librairie Centrale"]
    fournisseur_ids = []

    # 1. Insérer Fournisseurs
    for nom in fournisseurs_noms:
        # Vérifier si existe déjà
        c.execute("SELECT id FROM fournisseurs WHERE nom = ?", (nom,))
        row = c.fetchone()
        if row:
            fournisseur_ids.append(row[0])
        else:
            c.execute("INSERT INTO fournisseurs (nom, email, actif) VALUES (?, ?, 1)", (nom, f"contact@{nom.lower().replace(' ', '')}.com"))
            fournisseur_ids.append(c.lastrowid)

    # 1.bis MISE A JOUR STOCKS CRITIQUES (POUR DEMO)
    # On met PAPIER A4 (MP_A) et GAZOLE (MP_E) en dessous du seuil
    # Note: MP_A correspondra au premier item inséré si on repart de zéro, mais ici on update les codes existants s'ils sont déjà là.
    # Pour être propre, on devrait peut-être vider la table stocks ou faire un update intelligent.
    # Simplification : On update par NOM.
    c.execute("UPDATE stocks SET quantite = 10 WHERE nom = 'PAPIER A4'") 
    c.execute("UPDATE stocks SET quantite = 50 WHERE nom = 'GAZOLE'") # Seuil critique gazole peut-être plus haut
    print("📉 Stocks 'PAPIER A4' et 'GAZOLE' mis à niveau critique pour la démo.")

    # 2. Générer des Contrats passés
    for _ in range(12):
        matiere = random.choice(matieres)
        fournisseur_id = random.choice(fournisseur_ids)
        quantite = random.randint(50, 200)
        prix = random.randint(2500, 7500) # Prix en FCFA (approx)
        # total n'est pas stocké en DB, on stocke juste prix unitaire 'prix'
        
        date_contrat = datetime.now() - timedelta(days=random.randint(1, 60))
        date_str = date_contrat.isoformat()
        
        # Statut aléatoire
        statut = random.choice(["LIVRE", "PAYE", "EN_ATTENTE_LIVRAISON"])
        hashscan = f"https://hashscan.io/testnet/transaction/0.0.{random.randint(10000,99999)}@{random.randint(1000000000,9999999999)}"
        
        c.execute('''
            INSERT INTO contrats (matiere, quantite, prix, fournisseur_id, date_creation, statut, hashscan_url, transaction_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (matiere, quantite, prix, fournisseur_id, date_str, statut, hashscan, f"0.0.{random.randint(1000,9999)}@{random.randint(1000,9999)}"))
        
        contrat_id = c.lastrowid
        
        # 3. Si PAYE, générer transaction
        if statut == "PAYE":
            tx_id = f"0.0.{random.randint(10000,90000)}@{date_str}"
            montant_total = quantite * prix / 10 # Simulation conversion HBAR
            
            c.execute('''
                INSERT INTO transactions (contrat_id, type, montant, transaction_id, hashscan_url, statut, date_creation)
                VALUES (?, ?, ?, ?, ?, 'COMPLETE', ?)
            ''', (contrat_id, "PAIEMENT", montant_total, tx_id, hashscan, date_str))
            
    conn.commit()
    conn.close()
    print("✅ Database peuplée !")

if __name__ == "__main__":
    seed_data()
