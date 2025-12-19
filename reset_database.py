#!/usr/bin/env python3
"""
Script pour réinitialiser complètement la base de données
avec les nouvelles données municipales.
"""

import os
import database_mairie as db

def reset_database():
    """Supprime et recrée complètement la base de données."""

    # Supprimer l'ancienne base si elle existe
    db_path = 'mairie.db'
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"[OK] Ancienne base de donnees supprimee: {db_path}")
    else:
        print("[INFO] Aucune base de donnees existante")

    # Créer la nouvelle base
    print("\n[CREATE] Creation de la nouvelle base de donnees...")
    db.init_database()

    # Vérifier les données
    print("\n[CHECK] Verification des donnees chargees:")
    taxes = db.get_taxes()
    print(f"  [OK] {len(taxes)} taxes chargees")

    formulaires = db.get_formulaires()
    print(f"  [OK] {len(formulaires)} formulaires/actes charges")

    locations = db.get_locations()
    print(f"  [OK] {len(locations)} locations chargees")

    print("\n[SUCCESS] Base de donnees reinitialisee avec succes!")
    print("\n[EXAMPLES] Exemples de donnees chargees:")
    print("\nTAXES:")
    for i, t in enumerate(taxes[:3], 1):
        print(f"  {i}. {t['nom_taxe']} - {t['categorie']}: {t['montant_fixe'] or str(t['taux_pourcentage'])+'%'}")

    print("\nFORMULAIRES:")
    for i, f in enumerate(formulaires[:3], 1):
        print(f"  {i}. {f['nom_document']}: {f['cout_standard']} FCFA")

    print("\nLOCATIONS:")
    for i, l in enumerate(locations[:3], 1):
        print(f"  {i}. {l['type_location']} - {l['designation']}: {l['prix_base']} FCFA/{l['frequence']}")

if __name__ == "__main__":
    reset_database()
