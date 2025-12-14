# test_contract_manager.py - Tests unitaires pour le module contract_manager

import pytest
import os
import sys
from datetime import datetime

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from contract_manager import finalize_contract


class TestContractManager:
    """Tests pour la génération de contrats."""
    
    def test_finalize_contract_basic(self):
        """Vérifie la création d'un contrat basique."""
        contrat = finalize_contract("fer", 50, 100.0)
        
        assert contrat is not None
        assert contrat['matiere'] == 'fer'
        assert contrat['quantite'] == 50
        assert contrat['prix'] == 100.0
    
    def test_finalize_contract_has_date(self):
        """Vérifie que le contrat contient une date."""
        contrat = finalize_contract("cuivre", 30, 75.0)
        
        assert 'date' in contrat
        # Vérifier que c'est un format ISO valide
        try:
            datetime.fromisoformat(contrat['date'])
            valid_date = True
        except ValueError:
            valid_date = False
        
        assert valid_date
    
    def test_finalize_contract_has_topic_id(self):
        """Vérifie que le contrat contient un topic_id."""
        contrat = finalize_contract("zinc", 20, 50.0)
        
        assert 'topic_id' in contrat
        assert contrat['topic_id'] is not None
    
    def test_finalize_contract_different_materials(self):
        """Vérifie la création pour différentes matières."""
        matieres = ["fer", "cuivre", "aluminium", "nickel", "zinc", "plomb"]
        
        for matiere in matieres:
            contrat = finalize_contract(matiere, 10, 50.0)
            assert contrat['matiere'] == matiere
    
    def test_finalize_contract_zero_quantity(self):
        """Vérifie le comportement avec quantité zéro."""
        contrat = finalize_contract("fer", 0, 100.0)
        assert contrat['quantite'] == 0
    
    def test_finalize_contract_float_price(self):
        """Vérifie le comportement avec prix décimal."""
        contrat = finalize_contract("nickel", 25, 90.5)
        assert contrat['prix'] == 90.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
