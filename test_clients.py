# -*- coding: utf-8 -*-
import sys
import database_mairie as db

# Forcer l'encodage UTF-8 pour Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Initialiser la base de données
db.init_database()

print(f"\n{'='*70}")
print(f"VERIFICATION DES CLIENTS DES MARCHES")
print(f"{'='*70}\n")

# Statistiques globales
stats = db.get_clients_stats()
print(f"Total clients actifs: {stats['total_clients']}")
print(f"Total categories: {stats['total_categories']}")
print(f"Marches avec clients: {stats['marches_avec_clients']}")

print(f"\n{'='*70}")
print(f"DETAILS PAR MARCHE")
print(f"{'='*70}\n")

# Récupérer tous les marchés
marches = db.get_all_marches()

for marche in marches:
    print(f"\n{marche['nom_marche']}")
    print(f"{'-'*70}")

    # Récupérer les catégories
    categories = db.get_categories_by_marche(marche['id'])

    if not categories:
        print(f"  Aucun client enregistre")
    else:
        for cat in categories:
            print(f"\n  {cat['categorie_etal']}: {cat['nombre_clients']} client(s)")

            # Récupérer les clients de cette catégorie
            clients = db.get_clients_by_categorie(marche['id'], cat['categorie_etal'])

            for client in clients:
                print(f"    - {client['nom_complet']} (Etal {client['numero_etal'] or 'N/A'}) - {client['type_produits']}")

print(f"\n{'='*70}")
print("Verification terminee!")
print(f"{'='*70}\n")
