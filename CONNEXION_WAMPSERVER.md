# Guide de Connexion à WAMPSERVER

## Configuration Automatique pour WAMPSERVER MySQL

Ce guide vous permet de connecter votre système de gestion municipale à WAMPSERVER.

---

## ÉTAPE 1: Préparer WAMPSERVER

### 1.1 Démarrer WAMPSERVER
1. Lancer WAMPSERVER (icône verte dans la barre des tâches)
2. Vérifier que l'icône est VERTE (tous les services sont démarrés)
3. Si l'icône est orange ou rouge, cliquer dessus et "Start All Services"

### 1.2 Accéder à phpMyAdmin
1. Clic gauche sur l'icône WAMP
2. Cliquer sur "phpMyAdmin"
3. Se connecter avec:
   - **Utilisateur**: `root`
   - **Mot de passe**: *(vide par défaut)*

### 1.3 Créer la Base de Données
Dans phpMyAdmin:

1. Onglet "Bases de données"
2. Nom: `mairie_db`
3. Interclassement: `utf8mb4_general_ci`
4. Cliquer "Créer"

### 1.4 Créer un Utilisateur (Recommandé)
1. Onglet "Comptes d'utilisateurs"
2. Cliquer "Ajouter un compte d'utilisateur"
3. Remplir:
   - **Nom d'utilisateur**: `mairie_user`
   - **Nom d'hôte**: `localhost`
   - **Mot de passe**: `mairie2025` (ou votre choix)
   - Cocher "Re-saisir"
4. Section "Base de données pour le compte utilisateur":
   - Cocher "Accorder tous les privilèges sur la base de données mairie_db"
5. Cliquer "Exécuter"

---

## ÉTAPE 2: Configuration du Projet

### 2.1 Modifier le fichier `.env`

Éditer le fichier `.env` à la racine du projet:

```env
# Type de base de données
DB_TYPE=mysql

# Configuration MySQL WAMPSERVER
DB_HOST=localhost
DB_NAME=mairie_db
DB_USER=mairie_user
DB_PASSWORD=mairie2025
DB_PORT=3306
```

**OU si vous utilisez root (non recommandé):**
```env
DB_TYPE=mysql
DB_HOST=localhost
DB_NAME=mairie_db
DB_USER=root
DB_PASSWORD=
DB_PORT=3306
```

### 2.2 Installer le connecteur MySQL

Ouvrir un terminal et exécuter:

```bash
pip install mysql-connector-python
```

---

## ÉTAPE 3: Migrer les Données

### 3.1 Exécuter le script de migration

```bash
python migrate_to_wampserver.py
```

Ce script va:
1. ✅ Lire les données de SQLite (mairie.db)
2. ✅ Créer les tables dans MySQL
3. ✅ Importer toutes les données
4. ✅ Vérifier l'importation

---

## ÉTAPE 4: Tester la Connexion

```bash
python test_wampserver_connection.py
```

Vous devriez voir:
```
[OK] Connexion a MySQL reussie!
[OK] Base de donnees 'mairie_db' existe
[OK] 10 tables trouvees
[OK] 24 taxes importees
[OK] 25 formulaires importes
[OK] 16 locations importees
```

---

## ÉTAPE 5: Lancer l'Application

```bash
streamlit run dashboard.py
```

L'application utilisera maintenant MySQL au lieu de SQLite!

---

## Vérification dans phpMyAdmin

1. Ouvrir phpMyAdmin
2. Sélectionner la base `mairie_db`
3. Vérifier les tables:
   - `taxes` (24 lignes)
   - `formulaires` (25 lignes)
   - `locations` (16 lignes)
   - `transactions`
   - `citoyens`
   - `agents`
   - `reservations`
   - `alertes`
   - `services_municipaux`
   - `audit_log`

---

## Configuration Réseau (Optionnel)

### Accès depuis d'autres ordinateurs du réseau

#### 1. Autoriser les connexions externes dans WAMP
1. Clic sur icône WAMP
2. "Apache" → "httpd.conf"
3. Chercher "Require local"
4. Remplacer par:
```apache
Require all granted
```
5. Sauvegarder et redémarrer Apache

#### 2. Configurer MySQL pour accepter les connexions externes
1. Clic sur icône WAMP
2. "MySQL" → "my.ini"
3. Chercher `bind-address`
4. Modifier:
```ini
bind-address = 0.0.0.0
```
5. Sauvegarder et redémarrer MySQL

#### 3. Créer un utilisateur pour connexion externe
Dans phpMyAdmin:
```sql
CREATE USER 'mairie_user'@'%' IDENTIFIED BY 'mairie2025';
GRANT ALL PRIVILEGES ON mairie_db.* TO 'mairie_user'@'%';
FLUSH PRIVILEGES;
```

#### 4. Autoriser le port dans le pare-feu Windows
```cmd
netsh advfirewall firewall add rule name="MySQL WAMP" dir=in action=allow protocol=TCP localport=3306
```

---

## Avantages de WAMPSERVER

✅ **Interface graphique** avec phpMyAdmin
✅ **Performances** meilleures que SQLite
✅ **Multi-utilisateurs** simultanés
✅ **Sauvegardes** faciles via phpMyAdmin
✅ **Accès réseau** possible
✅ **Requêtes SQL** directes dans phpMyAdmin

---

## Dépannage

### Problème 1: "Can't connect to MySQL server"
**Solution:**
- Vérifier que WAMP est démarré (icône verte)
- Vérifier que MySQL est actif: Clic WAMP → MySQL → Service

### Problème 2: "Access denied for user"
**Solution:**
- Vérifier le nom d'utilisateur et mot de passe dans `.env`
- Recréer l'utilisateur dans phpMyAdmin

### Problème 3: "Database doesn't exist"
**Solution:**
- Créer la base de données `mairie_db` dans phpMyAdmin
- Relancer le script de migration

### Problème 4: Port 3306 déjà utilisé
**Solution:**
- Arrêter les autres services MySQL
- OU changer le port dans WAMP et `.env`

---

## Sauvegarde et Restauration

### Sauvegarder
Dans phpMyAdmin:
1. Sélectionner `mairie_db`
2. Onglet "Exporter"
3. Méthode: "Rapide"
4. Format: "SQL"
5. Cliquer "Exporter"

### Restaurer
1. Onglet "Importer"
2. Choisir le fichier `.sql`
3. Cliquer "Exécuter"

---

## Performances

### Optimisations MySQL pour WAMP

Éditer `my.ini`:
```ini
# Buffer pool (ajuster selon votre RAM)
innodb_buffer_pool_size = 256M

# Connexions simultanées
max_connections = 100

# Cache de requêtes
query_cache_size = 32M
query_cache_type = 1
```

---

## Monitoring

### Voir les connexions actives
Dans phpMyAdmin → "État" → "Processus"

### Voir les statistiques
phpMyAdmin → "État" → "Surveillance du serveur"

---

**Date:** 17 Décembre 2025
**Version:** 1.0 - Configuration WAMPSERVER
