# Migration Automatique vers WAMPSERVER - Guide Rapide

## 📋 Ce qui a été préparé pour vous

J'ai créé 3 scripts automatiques pour connecter votre système à WAMPSERVER MySQL:

1. **`migrate_to_wampserver.py`** - Migration automatique complète
2. **`test_wampserver_connection.py`** - Test de connexion
3. **`.env`** - Configuration MySQL prête à l'emploi

---

## 🚀 MIGRATION EN 3 ÉTAPES

### ÉTAPE 1: Préparer WAMPSERVER (5 minutes)

1. **Démarrer WAMPSERVER**
   - Lancer WAMPSERVER
   - Vérifier que l'icône est **VERTE** dans la barre des tâches
   - Si elle est orange/rouge: clic droit → "Start All Services"

2. **Ouvrir phpMyAdmin**
   - Clic gauche sur l'icône WAMP
   - Cliquer sur "phpMyAdmin"
   - Connexion automatique (pas de mot de passe par défaut)

**C'est tout pour la préparation!** Le script va créer automatiquement la base de données.

---

### ÉTAPE 2: Lancer la Migration Automatique (2 minutes)

Ouvrir un terminal dans le dossier du projet et exécuter:

```bash
python migrate_to_wampserver.py
```

**Le script va automatiquement:**
- ✅ Vérifier la connexion à MySQL
- ✅ Créer la base de données `mairie_db`
- ✅ Créer toutes les tables (10 tables)
- ✅ Migrer toutes les données de SQLite vers MySQL
- ✅ Vérifier que tout a bien été importé
- ✅ Configurer le fichier .env

**Sortie attendue:**
```
======================================================================
MIGRATION AUTOMATIQUE VERS WAMPSERVER MYSQL
======================================================================

[OK] mysql-connector-python est installé

[CONFIG] Configuration MySQL:
  Host: localhost
  User: root
  Database: mairie_db
  Port: 3306

[TEST] Test de connexion à MySQL...
[OK] Connexion réussie à MySQL 8.x.x

[CREATE] Création de la base de données 'mairie_db'...
[OK] Base de données 'mairie_db' créée/vérifiée

[TABLES] Création des tables MySQL...
  [OK] Table services_municipaux
  [OK] Table taxes
  [OK] Table formulaires
  [OK] Table locations
  [OK] Table citoyens
  [OK] Table agents
  [OK] Table transactions
  [OK] Table reservations
  [OK] Table alertes
  [OK] Table audit_log
[OK] 10 tables créées avec succès

[MIGRATION] Migration des données SQLite -> MySQL...
  [OK] taxes: 24 lignes migrées
  [OK] formulaires: 25 lignes migrées
  [OK] locations: 16 lignes migrées
  [OK] services_municipaux: X lignes migrées
  [OK] citoyens: X lignes migrées
  [OK] agents: X lignes migrées

[OK] Migration terminée: XXX lignes au total

[VERIFICATION] Vérification de la migration...
  [OK] taxes: 24 lignes
  [OK] formulaires: 25 lignes
  [OK] locations: 16 lignes
  ...

[OK] Vérification terminée avec succès!

[CONFIG] Mise à jour du fichier .env...
[OK] Fichier .env mis à jour

======================================================================
MIGRATION TERMINEE AVEC SUCCES!
======================================================================

Prochaines étapes:
  1. Vérifiez les données dans phpMyAdmin
  2. Modifiez .env si vous utilisez un autre utilisateur
  3. Lancez l'application: streamlit run dashboard.py

L'application utilisera maintenant MySQL au lieu de SQLite!
======================================================================
```

---

### ÉTAPE 3: Vérifier et Tester (1 minute)

1. **Tester la connexion**

```bash
python test_wampserver_connection.py
```

Vous verrez:
```
======================================================================
TEST DE CONNEXION A WAMPSERVER MYSQL
======================================================================

[1/6] Vérification du module mysql-connector-python...
  [OK] Module installé

[2/6] Chargement de la configuration...
  [OK] Host: localhost
  [OK] User: root
  [OK] Database: mairie_db
  [OK] Port: 3306

[3/6] Test de connexion à MySQL...
  [OK] Connexion réussie à MySQL 8.x.x

[4/6] Vérification de la base de données...
  [OK] Base de données 'mairie_db' existe

[5/6] Vérification des tables...
  [OK] 10 tables trouvées:
       - services_municipaux
       - taxes
       - formulaires
       - locations
       - citoyens
       - agents
       - transactions
       - reservations
       - alertes
       - audit_log

[6/6] Vérification des données...
  [OK] taxes: 24 lignes
  [OK] formulaires: 25 lignes
  [OK] locations: 16 lignes
  [INFO] transactions: 0 lignes (table vide normale)
  [INFO] citoyens: 0 lignes (table vide normale)
  [INFO] agents: 0 lignes (table vide normale)

======================================================================
TEST TERMINE AVEC SUCCES!
======================================================================

Statut: Connexion à WAMPSERVER MySQL fonctionnelle

Vous pouvez maintenant:
  1. Lancer l'application: streamlit run dashboard.py
  2. Gérer la base via phpMyAdmin
  3. Consulter les logs dans logs/app.log
======================================================================
```

2. **Vérifier dans phpMyAdmin**
   - Ouvrir phpMyAdmin
   - Sélectionner la base `mairie_db` (dans la colonne de gauche)
   - Cliquer sur chaque table pour voir les données

---

## 🎯 Lancer l'Application

Maintenant que MySQL est configuré:

```bash
streamlit run dashboard.py
```

L'application utilisera automatiquement MySQL au lieu de SQLite!

---

## 📊 Vérifications dans phpMyAdmin

### Tables et Données Attendues

| Table | Nombre de lignes attendu | Description |
|-------|-------------------------|-------------|
| `taxes` | 24 | Tous les types de taxes municipales |
| `formulaires` | 25 | Actes et certificats administratifs |
| `locations` | 16 | Véhicules, bureaux, salles |
| `services_municipaux` | Variable | Services de la mairie |
| `citoyens` | 0 au départ | Rempli au fur et à mesure |
| `agents` | Variable | Agents municipaux |
| `transactions` | 0 au départ | Historique des paiements |
| `reservations` | 0 au départ | Réservations de locations |
| `alertes` | 0 au départ | Alertes système |
| `audit_log` | 0 au départ | Journal d'audit |

---

## 🔧 Dépannage

### Problème 1: "Can't connect to MySQL server"

**Cause:** WAMPSERVER n'est pas démarré ou MySQL n'est pas actif

**Solution:**
1. Vérifier l'icône WAMP (doit être VERTE)
2. Clic droit sur WAMP → "Restart All Services"
3. Relancer `python migrate_to_wampserver.py`

---

### Problème 2: "Access denied for user 'root'"

**Cause:** Mot de passe root MySQL configuré

**Solution:**
Modifier le fichier `.env`:
```env
DB_PASSWORD=votre_mot_de_passe_mysql
```

---

### Problème 3: Port 3306 déjà utilisé

**Cause:** Un autre MySQL est actif

**Solution:**
1. Arrêter les autres services MySQL
2. OU changer le port dans WAMP et `.env`

---

### Problème 4: "Module 'mysql.connector' not found"

**Cause:** Module non installé

**Solution:**
```bash
pip install mysql-connector-python
```

---

## ⚙️ Configuration Avancée

### Créer un Utilisateur Dédié (Recommandé pour Production)

1. Dans phpMyAdmin, onglet "Comptes d'utilisateurs"
2. "Ajouter un compte d'utilisateur"
3. Remplir:
   - Nom: `mairie_user`
   - Mot de passe: `mairie2025`
   - Privilèges: Cocher "Accorder tous les privilèges sur mairie_db"

4. Modifier `.env`:
```env
DB_USER=mairie_user
DB_PASSWORD=mairie2025
```

5. Relancer l'application

---

## 🌐 Accès Réseau (Optionnel)

Pour permettre l'accès depuis d'autres ordinateurs du réseau local:

### 1. Autoriser les connexions externes dans MySQL

Dans phpMyAdmin, onglet SQL:
```sql
CREATE USER 'root'@'%' IDENTIFIED BY '';
GRANT ALL PRIVILEGES ON mairie_db.* TO 'root'@'%';
FLUSH PRIVILEGES;
```

### 2. Configurer le pare-feu Windows

```cmd
netsh advfirewall firewall add rule name="MySQL WAMP" dir=in action=allow protocol=TCP localport=3306
```

### 3. Modifier `.env` sur les autres machines

```env
DB_HOST=192.168.x.x  # IP du serveur WAMP
```

---

## 💾 Sauvegardes

### Sauvegarder la base de données

Dans phpMyAdmin:
1. Sélectionner `mairie_db`
2. Onglet "Exporter"
3. Méthode: "Rapide"
4. Format: "SQL"
5. Cliquer "Exporter"

Fichier sauvegardé: `mairie_db.sql`

### Restaurer la base de données

1. Onglet "Importer"
2. Choisir le fichier `mairie_db.sql`
3. Cliquer "Exécuter"

---

## 📈 Avantages de MySQL vs SQLite

| Critère | SQLite | MySQL (WAMPSERVER) |
|---------|--------|-------------------|
| **Performance** | ⭐⭐ Moyenne | ⭐⭐⭐⭐ Excellente |
| **Multi-utilisateurs** | ⚠️ Limité | ✅ Illimité |
| **Interface graphique** | ❌ Non | ✅ phpMyAdmin |
| **Sauvegardes** | Manuel | ✅ Facile (phpMyAdmin) |
| **Requêtes SQL** | Terminal | ✅ Interface web |
| **Accès réseau** | ❌ Non | ✅ Oui |
| **Taille max** | ~140 TB | Illimitée |

---

## 📝 Résumé

**Ce qui a été fait automatiquement:**
- ✅ Configuration MySQL dans `.env`
- ✅ Installation de `mysql-connector-python`
- ✅ Scripts de migration et test créés

**Ce que vous devez faire:**
1. Démarrer WAMPSERVER (icône verte)
2. Exécuter: `python migrate_to_wampserver.py`
3. Vérifier: `python test_wampserver_connection.py`
4. Lancer: `streamlit run dashboard.py`

**Temps total estimé:** 10 minutes

---

## 🆘 Support

Si vous rencontrez des problèmes:

1. Consulter ce guide
2. Vérifier [CONNEXION_WAMPSERVER.md](CONNEXION_WAMPSERVER.md) pour plus de détails
3. Consulter les logs: `logs/app.log`
4. Vérifier l'état de WAMPSERVER (icône verte)

---

**Date:** 17 Décembre 2025
**Version:** 1.0 - Migration Automatique WAMPSERVER
