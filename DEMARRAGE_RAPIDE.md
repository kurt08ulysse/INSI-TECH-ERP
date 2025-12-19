# Démarrage Rapide - Système de Gestion Municipale

## Installation

### 1. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 2. Initialiser la base de données (optionnel)
Si vous voulez réinitialiser la base de données avec les données par défaut:
```bash
python reset_database.py
```

## Lancement de l'Application

### Méthode 1: Via Streamlit (recommandé)
```bash
streamlit run dashboard.py
```

### Méthode 2: Via le lanceur Python
```bash
python launcher.py
```

### Méthode 3: Via le script batch (Windows)
```bash
start_app.bat
```

## Accès à l'Application

Une fois l'application lancée, ouvrez votre navigateur à l'adresse:
```
http://localhost:8501
```

## Navigation

L'application propose 6 pages principales:

### 1. 📊 Dashboard
- Vue d'ensemble des recettes
- Statistiques en temps réel
- Graphiques de répartition

### 2. 💳 Paiement en Ligne
- **Pour les citoyens**
- Paiement de taxes via Airtel Money ou MobiCash
- Paiement d'actes administratifs
- Reçu instantané

### 3. 🏛️ Guichet Mairie
- **Pour les agents municipaux**
- Enregistrement des paiements
- Délivrance d'actes
- Gestion des locations
- Modes de paiement: Espèces, Airtel Money, MobiCash, Virement

### 4. Historique Recettes
- Liste complète des recettes
- Statistiques par catégorie
- Export PDF

### 5. Historique Transactions
- Toutes les transactions
- Filtres et recherche
- Détails complets

### 6. 🚨 Alertes
- Alertes d'anomalies
- Recettes faibles
- Montants suspects

## Données Disponibles

### Taxes (24 types)
- Taxe de propreté: 50,000 / 25,000 FCFA
- Taxe sur la publicité: 12,000 - 15,000 FCFA
- Taxe des Box: 30,000 - 150,000 FCFA
- Étal de marché: 6,500 FCFA
- Taxe sur les loyers: 10%
- Taxes environnementales: 20,000 - 100,000 FCFA
- Et plus...

### Actes/Certificats (25 types)
- Certificat de résidence: 5,000 FCFA
- Autorisation parentale/maritale: 5,000 FCFA
- Actes de naissance: 3,000 - 10,000 FCFA
- Procurations: 5,000 FCFA
- Conventions: 20,000 - 50,000 FCFA
- Et plus...

### Locations (16 types)
- **Transport**: 25,000 - 80,000 FCFA/jour
- **Bureaux**: 50,000 - 200,000 FCFA/mois
- **Salles**: 15,000 - 250,000 FCFA

## Fonctionnalités Clés

### Paiement Mobile
✅ Airtel Money
✅ MobiCash
✅ Validation instantanée
✅ Reçu automatique

### Gestion des Paiements
✅ Calcul automatique des montants
✅ Validation des données
✅ Numéro de reçu unique
✅ Traçabilité complète

### Intelligence Artificielle
✅ Détection d'anomalies (écart > 20%)
✅ Prévisions de recettes
✅ Alertes automatiques
✅ Analyse des tendances

### Rapports
✅ Rapport journalier
✅ Statistiques par catégorie
✅ Export PDF
✅ Graphiques interactifs

## Exemples d'Utilisation

### Scénario 1: Citoyen paie une taxe en ligne
1. Ouvrir "💳 Paiement en Ligne"
2. Onglet "Payer une Taxe"
3. Sélectionner la taxe (ex: Taxe de propreté - Personne Physique)
4. Renseigner nom et numéro de contribuable
5. Choisir Airtel Money ou MobiCash
6. Saisir le numéro de téléphone
7. Cliquer "PAYER MAINTENANT"
8. Recevoir le reçu instantanément

### Scénario 2: Agent enregistre un paiement au guichet
1. Ouvrir "🏛️ Guichet Mairie"
2. Sélectionner l'agent en service
3. Onglet "Taxes Municipales", "Actes" ou "Locations"
4. Sélectionner le service
5. Renseigner les informations du payeur
6. Choisir le mode de paiement
7. Enregistrer le paiement
8. Imprimer ou envoyer le reçu

### Scénario 3: Consulter les statistiques
1. Ouvrir "📊 Dashboard"
2. Voir les métriques du jour/mois/année
3. Analyser la répartition des recettes
4. Consulter les graphiques

### Scénario 4: Vérifier les alertes
1. Ouvrir "🚨 Alertes"
2. Voir les anomalies détectées
3. Traiter les alertes
4. Marquer comme résolu

## Dépannage

### L'application ne démarre pas
```bash
# Vérifier les dépendances
pip install -r requirements.txt --upgrade

# Vérifier la base de données
python reset_database.py
```

### Erreur de base de données
```bash
# Réinitialiser la base
python reset_database.py
```

### Port déjà utilisé
```bash
# Utiliser un autre port
streamlit run dashboard.py --server.port 8502
```

## Maintenance

### Réinitialiser les données
```bash
python reset_database.py
```

### Nettoyer le projet
```bash
python cleanup_project.py
```

### Consulter les logs
Les logs sont dans le dossier `logs/app.log`

## Support

Pour toute question ou problème:
1. Consulter [STRUCTURE_PROJET.md](STRUCTURE_PROJET.md)
2. Lire [README.md](README.md)
3. Vérifier [NETTOYAGE_RESUME.md](NETTOYAGE_RESUME.md)

---

**Système de Gestion Municipale v2.0**
**Dernière mise à jour:** 17 Décembre 2025
