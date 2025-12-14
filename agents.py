# agents.py - Simulation de Négociation Multi-Agents

import random
import time
from logger import get_logger, log_transaction
import json

logger = get_logger(__name__)

class SupplierAgent:
    """Agent simulant un fournisseur."""
    def __init__(self, name, quality_score, aggressiveness):
        self.name = name
        self.quality_score = quality_score # 0.0 à 1.0
        self.aggressiveness = aggressiveness # 0.0 à 1.0 (propension à baisser le prix)
        
    def propose_price(self, base_price):
        """Propose un prix basé sur une stratégie."""
        # Variation aléatoire autour du prix de base
        variance = random.uniform(-0.1, 0.2) 
        
        # Les fournisseurs agressifs sont moins chers
        discount = self.aggressiveness * 0.15
        
        # La qualité premium est plus chère
        premium = self.quality_score * 0.2
        
        final_price = base_price * (1 + variance - discount + premium)
        return round(final_price, 2)


class Market:
    """Environnement de marché pour les enchères."""
    def __init__(self):
        self.suppliers = [
            SupplierAgent("MegaCorps Ind.", 0.8, 0.2),  # Cher, bonne qualité
            SupplierAgent("Discount Metal", 0.4, 0.9),  # Pas cher, qualité moyenne
            SupplierAgent("FastSupply Co.", 0.6, 0.5),  # Equilibré
            SupplierAgent("Premium Materials", 0.95, 0.1) # Très cher, top qualité
        ]
        
    def request_quotes(self, matiere, quantite):
        """Lance un appel d'offre et récupère les propositions."""
        logger.info(f"🤖 Lancement Appel d'Offre Multi-Agents pour {quantite}x {matiere}")
        
        # Prix de base estimé pour la matière en FCFA
        base_prices = {
            "papier a4": 3500.0, "encre imprimante": 15000.0, "ampoules public": 5000.0,
            "formulaires actes": 2000.0, "rouleaux tickets": 1500.0, "kits scolaires": 2500.0
        }
        ref_price = base_prices.get(matiere.lower(), 3000.0)
        
        proposals = []
        for agent in self.suppliers:
            price = agent.propose_price(ref_price)
            delay = random.randint(1, 5) # Jours de livraison
            proposals.append({
                "agent": agent.name,
                "price": price,
                "total": price * quantite,
                "delay": delay,
                "score": agent.quality_score
            })
            time.sleep(0.1) # Simulation délai réseau
            
        return proposals

    def select_best_offer(self, proposals):
        """Choisit la meilleure offre (stratégie mixte prix/délai/qualité)."""
        logger.info("🤖 Analyse des offres par l'Agent Acheteur...")
        
        best_offer = None
        best_score = -1
        
        for p in proposals:
            # Score composite : 
            # - Plus le prix est bas, mieux c'est
            # - Plus la qualité est haute, mieux c'est
            # - Moins de délai est mieux
            
            # Normalisation (simplifiée)
            price_factor = 1000 / p['total']  
            delay_factor = 1 / p['delay']
            
            score = (price_factor * 0.6) + (p['score'] * 20) + (delay_factor * 2)
            
            p['ai_score'] = round(score, 2)
            
            if score > best_score:
                best_score = score
                best_offer = p
                
        logger.info(f"🏆 Meilleure offre sélectionnée : {best_offer['agent']} ({best_offer['total']:.2f} MAD)")
        return best_offer

def run_negotiation(matiere, quantite):
    """Exécute une négociation complète."""
    market = Market()
    proposals = market.request_quotes(matiere, quantite)
    
    # Log les détails
    for p in proposals:
        logger.debug(f"   - Offre {p['agent']}: {p['price']} FCFA/u (Total: {p['total']}) - {p['delay']}j")
        
    winner = market.select_best_offer(proposals)
    
    log_transaction("AGENT_NEGOTIATION", {
        "matiere": matiere,
        "quantite": quantite,
        "winner": winner['agent'],
        "price": winner['price'],
        "savings": "N/A" # Pourrait être calculé vs prix moyen
    })
    
    return winner, proposals

if __name__ == "__main__":
    # Test
    run_negotiation("fer", 100)
