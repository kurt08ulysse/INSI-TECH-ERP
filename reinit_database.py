# -*- coding: utf-8 -*-
"""
Script de réinitialisation complète de la base de données
Supprime l'ancienne base et en crée une nouvelle avec toutes les données
"""
import sys
import os
import database_mairie as db

# Forcer l'encodage UTF-8 pour Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("\n" + "="*70)
print("REINITIALISATION DE LA BASE DE DONNEES")
print("="*70 + "\n")

# Supprimer l'ancienne base de données
db_path = "mairie.db"
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"✅ Ancienne base de données supprimée: {db_path}")
else:
    print(f"ℹ️ Aucune base de données existante trouvée")

# Recréer la base de données avec toutes les données
print("\n🔄 Création de la nouvelle base de données...")
db.init_database()

# Vérifier que tout est bien créé
print("\n📊 Vérification des données créées:")

# Marchés
marches = db.get_all_marches()
print(f"  • Marchés: {len(marches)}")

# Clients
stats = db.get_clients_stats()
print(f"  • Clients actifs: {stats['total_clients']}")
print(f"  • Catégories d'étals: {stats['total_categories']}")
print(f"  • Marchés avec clients: {stats['marches_avec_clients']}")

print("\n" + "="*70)
print("✅ REINITIALISATION TERMINEE AVEC SUCCES!")
print("="*70)
print("\n💡 Vous pouvez maintenant lancer l'application:")
print("   streamlit run dashboard.py\n")
