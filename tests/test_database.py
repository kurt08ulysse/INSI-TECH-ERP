# test_database.py - Tests unitaires pour le module database

import pytest
import os
import sys

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database as db


@pytest.fixture(autouse=True)
def setup_test_db(tmp_path, monkeypatch):
    """Configure une base de données de test temporaire."""
    test_db = str(tmp_path / "test_stock.db")
    monkeypatch.setattr(db, "DB_PATH", test_db)
    db.init_database()
    yield
    # Nettoyage automatique avec tmp_path


class TestStocks:
    """Tests pour les opérations sur les stocks."""
    
    def test_get_all_stocks(self):
        """Vérifie que les stocks par défaut sont créés."""
        stocks = db.get_all_stocks()
        assert len(stocks) == 6
        noms = [s['nom'] for s in stocks]
        assert 'fer' in noms
        assert 'cuivre' in noms
    
    def test_get_stock_by_name(self):
        """Vérifie la récupération d'un stock par nom."""
        stock = db.get_stock_by_name("fer")
        assert stock is not None
        assert stock['nom'] == 'fer'
        assert stock['code'] == 'MP_A'
    
    def test_get_stock_by_name_case_insensitive(self):
        """Vérifie que la recherche est insensible à la casse."""
        stock = db.get_stock_by_name("FER")
        assert stock is not None
        assert stock['nom'] == 'fer'
    
    def test_get_stock_not_found(self):
        """Vérifie le retour None pour un stock inexistant."""
        stock = db.get_stock_by_name("uranium")
        assert stock is None
    
    def test_update_stock_quantity(self):
        """Vérifie la mise à jour de quantité."""
        db.update_stock_quantity("fer", 100)
        stock = db.get_stock_by_name("fer")
        assert stock['quantite'] == 100
    
    def test_get_critical_stocks(self):
        """Vérifie la détection des stocks critiques."""
        db.update_stock_quantity("fer", 10)
        db.update_stock_quantity("cuivre", 5)
        
        critical = db.get_critical_stocks()
        assert len(critical) >= 2
        
        noms = [s['nom'] for s in critical]
        assert 'fer' in noms
        assert 'cuivre' in noms


class TestContrats:
    """Tests pour les opérations sur les contrats."""
    
    def test_create_contrat(self):
        """Vérifie la création d'un contrat."""
        contrat_id = db.create_contrat(
            matiere="fer",
            quantite=50,
            prix=100.0,
            topic_id="0.0.123456",
            transaction_id="tx_001",
            hashscan_url="https://hashscan.io/testnet/tx/001"
        )
        assert contrat_id > 0
    
    def test_get_all_contrats(self):
        """Vérifie la récupération des contrats."""
        db.create_contrat("fer", 50, 100.0)
        db.create_contrat("cuivre", 30, 75.0)
        
        contrats = db.get_all_contrats()
        assert len(contrats) >= 2
    
    def test_update_contrat_status(self):
        """Vérifie la mise à jour du statut."""
        contrat_id = db.create_contrat("zinc", 20, 50.0)
        db.update_contrat_status(contrat_id, "CONFIRME", "tx_123")
        
        contrats = db.get_all_contrats()
        contrat = next((c for c in contrats if c['id'] == contrat_id), None)
        assert contrat is not None
        assert contrat['statut'] == "CONFIRME"


class TestTransactions:
    """Tests pour les opérations sur les transactions."""
    
    def test_create_transaction(self):
        """Vérifie la création d'une transaction."""
        contrat_id = db.create_contrat("nickel", 25, 90.0)
        tx_id = db.create_transaction(
            contrat_id=contrat_id,
            type_tx="PAIEMENT",
            montant=2250.0,
            transaction_id="tx_pay_001",
            hashscan_url="https://hashscan.io/testnet/tx/pay_001"
        )
        assert tx_id > 0
    
    def test_get_all_transactions(self):
        """Vérifie la récupération des transactions."""
        contrat_id = db.create_contrat("plomb", 15, 40.0)
        db.create_transaction(contrat_id, "PAIEMENT", 600.0, "tx_1", "url_1")
        db.create_transaction(contrat_id, "PAIEMENT", 400.0, "tx_2", "url_2")
        
        transactions = db.get_all_transactions()
        assert len(transactions) >= 2


class TestAlertes:
    """Tests pour les opérations sur les alertes."""
    
    def test_create_alerte(self):
        """Vérifie la création d'une alerte."""
        alerte_id = db.create_alerte("fer", 15, "STOCK_CRITIQUE")
        assert alerte_id > 0
    
    def test_get_pending_alertes(self):
        """Vérifie la récupération des alertes non traitées."""
        db.create_alerte("cuivre", 10)
        db.create_alerte("zinc", 5)
        
        alertes = db.get_pending_alertes()
        assert len(alertes) >= 2
    
    def test_mark_alerte_treated(self):
        """Vérifie le marquage d'une alerte comme traitée."""
        alerte_id = db.create_alerte("aluminium", 8)
        db.mark_alerte_treated(alerte_id)
        
        # L'alerte ne doit plus apparaître dans les pending
        alertes = db.get_pending_alertes()
        ids = [a['id'] for a in alertes]
        assert alerte_id not in ids


class TestStatistics:
    """Tests pour les statistiques."""
    
    def test_get_statistics(self):
        """Vérifie le calcul des statistiques."""
        # Créer des données de test
        db.update_stock_quantity("fer", 10)  # Critique
        db.create_contrat("fer", 50, 100.0)
        db.create_alerte("fer", 10)
        
        stats = db.get_statistics()
        
        assert 'stocks_critiques' in stats
        assert 'total_contrats' in stats
        assert 'alertes_pending' in stats
        assert stats['stocks_critiques'] >= 1
        assert stats['total_contrats'] >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
