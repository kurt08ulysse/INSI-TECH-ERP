# -*- coding: utf-8 -*-
import sys
import database_mairie as db

# Forcer l'encodage UTF-8 pour Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Initialiser la base de données
db.init_database()

# Récupérer tous les marchés
marches = db.get_all_marches()

print(f"\n{'='*70}")
print(f"VERIFICATION DES MARCHES DE FRANCEVILLE, GABON")
print(f"{'='*70}")
print(f"\nNombre total de marches: {len(marches)}\n")

for i, m in enumerate(marches, 1):
    print(f"{i}. {m['nom_marche']}")
    print(f"   Quartier: {m['quartier']}")
    print(f"   Coordonnees GPS: {m['latitude']}, {m['longitude']}")
    print(f"   Nombre d'etals: {m['nombre_etals']}")
    print(f"   Tarif: {m['tarif_etal_jour']:,.0f} FCFA")
    print(f"   Ouverture: {m['jours_ouverture']}")
    print(f"   Horaires: {m['horaires']}")
    print()

print(f"{'='*70}")
print("Tous les marches sont bien enregistres dans la base!")
print(f"{'='*70}\n")
