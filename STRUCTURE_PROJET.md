# Structure du Projet - Système de Gestion Municipale

## Vue d'ensemble

Ce projet est un **système complet de gestion des recettes municipales** avec paiement en ligne via mobile money (Airtel Money et MobiCash).

## Architecture du Système

### Fichiers Principaux

#### 1. Interface Utilisateur
- **`dashboard.py`** (21 KB) - Dashboard principal avec navigation et statistiques
  - Métriques en temps réel
  - Répartition des recettes
  - Historique des transactions
  - Alertes et notifications
  - Navigation entre les différentes pages

- **`guichet_mairie.py`** (16 KB) - Interface pour agents municipaux
  - Enregistrement des paiements de taxes
  - Délivrance d'actes administratifs
  - Gestion des locations
  - Statistiques du jour

- **`paiement_client.py`** (11 KB) - Interface de paiement en ligne pour citoyens
  - Paiement de taxes via mobile money
  - Paiement d'actes administratifs
  - Reçu instantané
  - Validation des paiements

#### 2. Logique Métier et Base de Données
- **`database_mairie.py`** (27 KB) - Gestion de la base de données SQLite
  - Schéma de la base de données
  - 24 taxes municipales
  - 25 formulaires/actes administratifs
  - 16 types de locations
  - Gestion des transactions
  - Système d'alertes

- **`services_mairie.py`** (14 KB) - Logique métier
  - Calcul des montants de taxes
  - Enregistrement des paiements
  - Détection d'anomalies
  - Rapports journaliers
  - Vérification des montants

#### 3. Intelligence Artificielle
- **`ia_surveillance.py`** (19 KB) - Système de surveillance IA
  - Détection des anomalies financières
  - Surveillance des transactions
  - Analyse des patterns de paiement
  - Génération d'alertes

- **`ai_forecast.py`** (6 KB) - Prévisions financières
  - Prévision des recettes
  - Analyse des tendances
  - Régression linéaire
  - Projections à 30 jours

#### 4. Utilitaires
- **`logger.py`** (2.8 KB) - Système de logging
- **`launcher.py`** (1 KB) - Lanceur de l'application
- **`streamlit_app.py`** (183 bytes) - Point d'entrée Streamlit
- **`reset_database.py`** (1.7 KB) - Utilitaire de réinitialisation de la base de données
- **`cleanup_project.py`** - Script de nettoyage du projet

## Base de Données

### `mairie.db` (77 KB)

La base de données contient:

#### Tables Principales
1. **citoyens** - Informations des citoyens/contribuables
2. **agents** - Agents municipaux
3. **taxes** - Catalogue des taxes (24 types)
4. **formulaires** - Actes administratifs (25 types)
5. **locations** - Services de location (16 types)
6. **transactions** - Historique des paiements
7. **reservations** - Réservations de locations
8. **alertes** - Système d'alertes
9. **services_municipaux** - Services de la mairie
10. **audit_log** - Journal d'audit

### Données Chargées

#### Taxes (24 types)
- Taxe de propreté (Personne Morale: 50,000 FCFA, Personne Physique: 25,000 FCFA)
- Taxe sur la publicité (12,000 - 15,000 FCFA)
- Taxe des Box (30,000 - 150,000 FCFA)
- Étal de marché (6,500 FCFA)
- Taxe sur les loyers (10% du loyer)
- Taxes environnementales (20,000 - 100,000 FCFA)
- Taxe pompes funèbres (50,000 FCFA)
- Taxe transport (40,000 - 100,000 FCFA)
- Taxe pylônes téléphonie (500,000 FCFA)
- Taxe terrassements (150,000 - 300,000 FCFA)
- Taxe panneaux lumineux (200,000 FCFA)

#### Formulaires/Actes (25 types)
- Certificats (résidence, hébergement, célibat, etc.)
- Autorisations (parentale, maritale, provisoire d'exercer)
- Actes de naissance (copie, extrait, transcription)
- Procurations et attestations
- Procès verbaux
- Conventions (commerçant, entreprise)

#### Locations (16 types)
- **Transport**: Véhicules légers, minibus, bus, camionnettes (25,000 - 80,000 FCFA/jour)
- **Bureaux**: Petits à premium (50,000 - 200,000 FCFA/mois)
- **Salles de réunion**: Petites à salles de conférence (15,000 - 250,000 FCFA)

## Fonctionnalités Principales

### 1. Paiement en Ligne
- ✅ Paiement via Airtel Money
- ✅ Paiement via MobiCash
- ✅ Reçu instantané
- ✅ Validation en temps réel

### 2. Gestion au Guichet
- ✅ Enregistrement des taxes
- ✅ Délivrance d'actes
- ✅ Gestion des locations
- ✅ Modes de paiement multiples (Espèces, Mobile Money, Virement)

### 3. Surveillance et Alertes
- ✅ Détection d'anomalies de montants (écart > 20%)
- ✅ Détection de recettes faibles
- ✅ Alertes en temps réel
- ✅ Prévisions IA

### 4. Rapports et Statistiques
- ✅ Rapport journalier
- ✅ Statistiques par catégorie
- ✅ Historique complet
- ✅ Répartition des recettes

## Configuration

### Fichiers de Configuration
- **`.env`** - Variables d'environnement (API keys, etc.)
- **`.env.example`** - Template de configuration
- **`requirements.txt`** - Dépendances Python

### Dépendances Principales
- `streamlit` - Framework web
- `sqlite3` - Base de données
- `pandas` - Analyse de données
- `plotly` - Visualisations
- `fpdf` - Génération de PDF

## Installation et Démarrage

### 1. Installation des dépendances
```bash
pip install -r requirements.txt
```

### 2. Initialisation de la base de données
```bash
python reset_database.py
```

### 3. Lancement de l'application
```bash
streamlit run dashboard.py
```

ou

```bash
python launcher.py
```

## Navigation dans l'Application

1. **📊 Dashboard** - Vue d'ensemble avec métriques et statistiques
2. **💳 Paiement en Ligne** - Interface pour les citoyens
3. **🏛️ Guichet Mairie** - Interface pour les agents
4. **Historique Recettes** - Historique des recettes municipales
5. **Historique Transactions** - Toutes les transactions
6. **🚨 Alertes** - Système d'alertes

## Sécurité et Traçabilité

- ✅ Numéro de reçu unique pour chaque transaction
- ✅ Horodatage de toutes les opérations
- ✅ Identification du payeur (nom + numéro)
- ✅ Mode de paiement enregistré
- ✅ Journal d'audit
- ✅ Détection d'anomalies automatique

## Maintenance

### Réinitialisation de la Base de Données
```bash
python reset_database.py
```

### Nettoyage du Projet
```bash
python cleanup_project.py
```

## Support et Documentation

- **README.md** - Documentation générale
- **REFACTORING_MAIRIE.md** - Historique de refactoring
- **SYSTEME_REEL.md** - Documentation système réel
- **STRUCTURE_PROJET.md** - Ce fichier

## Auteur et Licence

Système de Gestion Municipale - Version 2.0
Développé pour la gestion moderne des recettes municipales avec paiement mobile.

---

**Dernière mise à jour:** 17 Décembre 2025
**Version:** 2.0 - Système complet avec paiement en ligne
