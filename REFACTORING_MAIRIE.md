# 🏛️ REFACTORISATION - APPLICATION MAIRIE

## ✅ ÉTAPE 1 TERMINÉE: Nouveau schéma de base de données

### Fichier créé: `database_mairie.py`
Base de données propre et cohérente pour une mairie municipale.

---

## 📊 NOUVEAU SCHÉMA - TABLES PRINCIPALES

### 1. **citoyens** - Registre des contribuables
- `numero_contribuable` (unique)
- Nom, prénom, contact
- Type de personne (Physique/Morale)
- Historique

### 2. **agents** - Personnel municipal
- Matricule (unique)
- Service, fonction
- Statut actif/inactif

### 3. **taxes** - Taxes municipales
- Nom, catégorie
- Montant fixe OU taux pourcentage
- Description, unité
- Statut actif

### 4. **formulaires** - Actes administratifs
- Certificats (résidence, célibat, etc.)
- Autorisations (voyager, exercer, etc.)
- Coût standard
- Délai de traitement

### 5. **locations** - Locations municipales
- Véhicules, bureaux, salles
- Prix selon fréquence
- Capacité, disponibilité

### 6. **transactions** - Paiements
- Type (TAXE, ACTE, LOCATION)
- Montant, mode de paiement
- Numéro de reçu (unique)
- Lien blockchain (transaction_id, hashscan_url)
- Référence citoyen et agent

### 7. **reservations** - Réservations
- Salles, véhicules municipaux
- Dates, durée
- Montant total

### 8. **alertes** - Alertes financières
- Anomalies de recettes
- Paiements suspects
- Niveaux de priorité

### 9. **services_municipaux** - Organigramme
- Finances, État Civil, Urbanisme, etc.
- Budget annuel
- Responsable

### 10. **audit_log** - Traçabilité
- Actions des agents
- Horodatage
- Détails des opérations

---

## 🎯 DONNÉES PRÉ-CHARGÉES

### Taxes (10 types)
- Taxe de propreté (Personne Morale: 50k, Physique: 25k)
- Taxe publicité (Petit: 12k, Grand: 15k)
- Taxe Box (Grand/Moyen/Petit: 150k à 30k)
- Étal de marché (6,5k)
- Taxe sur loyers (10%)

### Formulaires (10 types)
- Certificats (résidence, célibat, hébergement)
- Autorisations (voyager, exercer)
- Copies actes (naissance, etc.)
- Prix: 3k à 15k FCFA

### Locations (7 types)
- Véhicules (léger: 10k/jour, lourd: 30k/jour)
- Bureaux (petit: 50k/mois, grand: 120k/mois)
- Salles (15k/heure à 100k/jour)

### Agents (3 exemples)
- Trésorier Municipal
- Chef Service État Civil
- Agent Guichet

### Services (4 services)
- Finances (Budget: 50M)
- État Civil (Budget: 10M)
- Urbanisme (Budget: 30M)
- Services Techniques (Budget: 40M)

---

## 🔧 ÉTAPES SUIVANTES

### ÉTAPE 2: Créer nouveau fichier `services_mairie.py`
Logique métier propre à la mairie:
- [ ] Calcul automatique des taxes
- [ ] Génération de reçus
- [ ] Validation des paiements
- [ ] Envoi sur blockchain Hedera
- [ ] Détection d'anomalies financières

### ÉTAPE 3: Créer `guichet_mairie.py`
Interface guichet municipal:
- [ ] Page accueil guichet
- [ ] Sélection type de service (Taxe/Acte/Location)
- [ ] Calcul montant automatique
- [ ] Paiement et reçu
- [ ] Publication blockchain

### ÉTAPE 4: Adapter `dashboard.py`
- [ ] Renommer en "Système de Gestion Municipale"
- [ ] Remplacer imports `database` par `database_mairie`
- [ ] Adapter métriques (recettes jour/mois/année)
- [ ] Graphiques recettes par source
- [ ] Historique des encaissements

### ÉTAPE 5: Créer `ai_forecast_mairie.py`
Prédictions spécifiques mairie:
- [ ] Prévision recettes mensuelles
- [ ] Détection périodes creuses
- [ ] Alertes baisse anormale

### ÉTAPE 6: Nettoyer anciens fichiers
- [ ] Supprimer/Archiver `database.py` (stocks)
- [ ] Supprimer `simulateur_mqtt.py` (RFID)
- [ ] Supprimer `detecteur_seuil.py` (stocks)

### ÉTAPE 7: Tests et migration données
- [ ] Tester création transactions
- [ ] Tester calculs taxes
- [ ] Vérifier blockchain
- [ ] Migrer données existantes si besoin

---

## 📈 AVANTAGES DU NOUVEAU SCHÉMA

### ✅ Cohérence métier
- Tables clairement définies pour une MAIRIE
- Pas de mélange stocks/mairie
- Terminologie adaptée

### ✅ Traçabilité complète
- Chaque transaction liée à un citoyen et un agent
- Numéro de reçu unique
- Lien blockchain pour transparence
- Audit log de toutes les actions

### ✅ Gestion complète
- Taxes, actes, locations
- Réservations
- Alertes financières automatiques
- Statistiques en temps réel

### ✅ Extensibilité
- Facile d'ajouter nouveaux services
- Structure modulaire
- Possibilité ajout modules (permis, urbanisme, etc.)

---

## 📝 UTILISATION

### Initialiser la base
```python
python database_mairie.py
```

### Importer dans votre code
```python
import database_mairie as db

# Créer une transaction
db.create_transaction(
    type_tx="TAXE_PROPRETE",
    libelle="Taxe de propreté - Personne Physique",
    montant=25000,
    citoyen_id=1,
    agent_id=1
)

# Récupérer statistiques
stats = db.get_statistics()
print(f"Recettes du jour: {stats['recettes_jour']} FCFA")
```

---

## 🎯 PROCHAINE ÉTAPE

**Voulez-vous que je continue avec l'ÉTAPE 2** (créer services_mairie.py)
ou préférez-vous d'abord **adapter le dashboard** pour utiliser la nouvelle base?

Dites-moi quelle étape vous voulez faire en premier!
