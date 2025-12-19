# 🚀 Guide de Déploiement sur Streamlit Cloud

## 📋 Prérequis

- Un compte GitHub (gratuit)
- Un compte Streamlit Cloud (gratuit - https://streamlit.io/cloud)
- Vos credentials Hedera, MQTT, etc. (optionnels selon les fonctionnalités)

---

## 🔧 Étape 1: Préparer le Repository GitHub

### 1.1 Créer un repository GitHub

1. Allez sur https://github.com/new
2. Créez un nouveau repository:
   - Nom: `systeme-gestion-municipale` (ou votre choix)
   - Visibilité: Public ou Private
   - **NE PAS** initialiser avec README (le projet en a déjà un)

### 1.2 Pousser le code sur GitHub

Ouvrez un terminal dans le dossier du projet et exécutez:

```bash
# Initialiser Git (si pas déjà fait)
git init

# Ajouter tous les fichiers
git add .

# Créer le premier commit
git commit -m "Initial commit - Système de Gestion Municipale"

# Ajouter le remote GitHub (remplacez USERNAME et REPO)
git remote add origin https://github.com/USERNAME/REPO.git

# Pousser sur GitHub
git branch -M main
git push -u origin main
```

**⚠️ IMPORTANT**: Vérifiez que le fichier `.gitignore` contient:
```
.env
.streamlit/secrets.toml
*.db
__pycache__/
logs/
```

---

## ☁️ Étape 2: Déployer sur Streamlit Cloud

### 2.1 Se connecter à Streamlit Cloud

1. Allez sur https://share.streamlit.io/
2. Cliquez sur **"Sign up"** ou **"Sign in"**
3. Connectez-vous avec votre compte GitHub

### 2.2 Créer une nouvelle application

1. Cliquez sur **"New app"**
2. Remplissez les informations:
   - **Repository**: Sélectionnez votre repository GitHub
   - **Branch**: `main`
   - **Main file path**: `Projet-Blockchain-et-IoT-Suivi-intelligent-des-stocks-avec-RFID-et-Hashgraph-master/dashboard.py`

   ⚠️ **ATTENTION**: Le chemin doit inclure le dossier du projet!

3. Cliquez sur **"Advanced settings"** (optionnel):
   - Python version: 3.11 (recommandé)
   - Secrets: Vous les ajouterez après

4. Cliquez sur **"Deploy!"**

---

## 🔐 Étape 3: Configurer les Secrets

### 3.1 Accéder aux paramètres de l'application

1. Une fois déployée, cliquez sur **"⚙️ Settings"** (en bas à droite)
2. Allez dans l'onglet **"Secrets"**

### 3.2 Ajouter vos secrets

Copiez le contenu du fichier `.streamlit/secrets.toml.example` et modifiez avec vos vraies valeurs:

```toml
[database]
DB_TYPE = "sqlite"
DB_HOST = "localhost"
DB_NAME = "mairie_db"
DB_USER = "root"
DB_PASSWORD = ""
DB_PORT = "3306"

[email]
EMAIL_FROM = "votre_email@gmail.com"
EMAIL_PASSWORD = "votre_mot_de_passe_application"
EMAIL_TO = "destinataire@email.com"

[mqtt]
MQTT_BROKER = "votre_broker.hivemq.cloud"
MQTT_PORT = "8883"
MQTT_USERNAME = "votre_username"
MQTT_PASSWORD = "votre_password"

[hedera]
OPERATOR_ID = "0.0.XXXXXX"
OPERATOR_KEY = "302e020100300506032b6570..."
TOPIC_ID = "0.0.XXXXXX"
SUPPLIER_ACCOUNT_ID = "0.0.XXXXXX"
```

3. Cliquez sur **"Save"**
4. L'application va redémarrer automatiquement

---

## 🎯 Étape 4: Vérifier le Déploiement

### 4.1 Attendre le déploiement

- Le déploiement initial peut prendre **3-5 minutes**
- Vous verrez les logs en temps réel
- Attendez le message: **"Your app is live!"**

### 4.2 Tester l'application

1. Cliquez sur le lien de votre application (ex: `https://username-app-name.streamlit.app`)
2. Vérifiez que:
   - ✅ La page s'affiche correctement
   - ✅ Le dashboard se charge
   - ✅ Les données s'affichent (ou base vide si nouvelle installation)

### 4.3 Problèmes courants

| Problème | Solution |
|----------|----------|
| **ModuleNotFoundError** | Vérifiez que `requirements.txt` contient tous les modules |
| **Base de données vide** | Normal pour une nouvelle installation - la base sera créée automatiquement |
| **Erreur de secrets** | Vérifiez la syntaxe TOML dans les secrets |
| **Chemin de fichier incorrect** | Vérifiez le "Main file path" dans les settings |

---

## 🔄 Étape 5: Mettre à Jour l'Application

### 5.1 Pousser des changements

```bash
# Faire vos modifications localement
git add .
git commit -m "Description des changements"
git push
```

### 5.2 Déploiement automatique

- Streamlit Cloud **détecte automatiquement** les changements
- L'application sera **redéployée automatiquement**
- Attendez 2-3 minutes pour voir les changements

### 5.3 Redémarrage manuel

Si nécessaire:
1. Allez dans **Settings** > **Reboot app**
2. L'application redémarre immédiatement

---

## 📊 Fonctionnalités Limitées en Cloud

### ⚠️ Limitations de Streamlit Cloud

Certaines fonctionnalités peuvent ne pas fonctionner complètement:

1. **Base de données SQLite**:
   - ✅ Fonctionne MAIS les données sont **temporaires**
   - Les données sont **perdues à chaque redémarrage**
   - **Solution**: Utilisez une base externe (PostgreSQL, MySQL)

2. **Envoi d'emails**:
   - ⚠️ Peut être bloqué par le firewall
   - **Solution**: Utilisez un service d'email API (SendGrid, Mailgun)

3. **Communication MQTT**:
   - ✅ Devrait fonctionner avec HiveMQ Cloud
   - ⚠️ Vérifiez les ports autorisés

4. **Blockchain Hedera**:
   - ✅ Devrait fonctionner (API externe)
   - ⚠️ Testez en mode Testnet d'abord

### 💡 Recommandations pour Production

Pour une application de production complète:

1. **Base de données persistante**:
   ```toml
   [database]
   DB_TYPE = "postgresql"
   DB_HOST = "votre-instance.rds.amazonaws.com"
   DB_NAME = "mairie_prod"
   DB_USER = "admin"
   DB_PASSWORD = "votre_mot_de_passe_securise"
   DB_PORT = "5432"
   ```

2. **Services externes recommandés**:
   - **BDD**: [Supabase](https://supabase.com) (PostgreSQL gratuit)
   - **Email**: [SendGrid](https://sendgrid.com) (100 emails/jour gratuit)
   - **Fichiers**: [AWS S3](https://aws.amazon.com/s3/) ou [Cloudinary](https://cloudinary.com)

---

## 🔒 Sécurité

### ✅ Bonnes pratiques

- ✅ **TOUJOURS** utiliser les Secrets pour les credentials
- ✅ **JAMAIS** commiter `.env` ou `secrets.toml`
- ✅ Utiliser des **mots de passe forts**
- ✅ Activer **l'authentification** si l'app contient des données sensibles

### 🔐 Authentification (Optionnelle)

Streamlit Cloud supporte l'authentification:
1. Allez dans **Settings** > **Secrets**
2. Ajoutez:
   ```toml
   [passwords]
   # Liste des utilisateurs autorisés
   admin = "mot_de_passe_securise"
   user1 = "autre_mot_de_passe"
   ```

3. Dans `dashboard.py`, ajoutez en haut:
   ```python
   import streamlit as st

   def check_password():
       if "authenticated" not in st.session_state:
           st.session_state.authenticated = False

       if st.session_state.authenticated:
           return True

       username = st.text_input("Utilisateur")
       password = st.text_input("Mot de passe", type="password")

       if st.button("Se connecter"):
           if username in st.secrets["passwords"]:
               if st.secrets["passwords"][username] == password:
                   st.session_state.authenticated = True
                   st.rerun()
           st.error("Identifiants incorrects")

       return False

   if not check_password():
       st.stop()
   ```

---

## 📈 Monitoring

### Logs de l'application

1. Dans le dashboard Streamlit Cloud
2. Cliquez sur **"Manage app"**
3. Consultez les **logs en temps réel**

### Métriques (Plan payant)

- Nombre de visiteurs
- Temps de réponse
- Utilisation mémoire

---

## 💰 Limites du Plan Gratuit

| Ressource | Limite Gratuite |
|-----------|----------------|
| **Apps** | 1 app publique |
| **RAM** | 1 GB |
| **CPU** | Partagé |
| **Stockage** | 1 GB |
| **Visiteurs** | Illimité |

Pour plus d'apps ou de ressources: https://streamlit.io/cloud/pricing

---

## 🆘 Support et Dépannage

### Documentation officielle

- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [Forum Communautaire](https://discuss.streamlit.io/)

### Problèmes fréquents

**Application très lente**:
- Optimisez les requêtes de base de données
- Utilisez `@st.cache_data` pour les données
- Réduisez les graphiques complexes

**Erreur de mémoire**:
- L'app dépasse 1 GB de RAM
- Optimisez le code
- Passez au plan payant

**Redémarrages fréquents**:
- Normal après 7 jours d'inactivité
- Utilisez un service de "ping" pour maintenir actif

---

## ✅ Checklist de Déploiement

Avant de déployer, vérifiez:

- [ ] ✅ Repository GitHub créé et pushé
- [ ] ✅ `.gitignore` configuré correctement
- [ ] ✅ `requirements.txt` complet
- [ ] ✅ `.streamlit/config.toml` configuré
- [ ] ✅ `.streamlit/secrets.toml.example` créé
- [ ] ✅ Secrets ajoutés sur Streamlit Cloud
- [ ] ✅ Chemin du fichier principal correct
- [ ] ✅ Application testée en local
- [ ] ✅ Base de données initialisée
- [ ] ✅ Credentials Hedera/MQTT valides (si utilisés)

---

## 🎉 Félicitations!

Votre application est maintenant déployée sur Streamlit Cloud!

**URL de votre application**: `https://[username]-[app-name].streamlit.app`

Partagez ce lien avec vos utilisateurs!

---

## 📞 Besoin d'Aide?

- 📧 Email: support@votreprojet.com
- 💬 Discord/Slack: [Lien vers votre communauté]
- 🐛 Issues GitHub: https://github.com/USERNAME/REPO/issues

---

**Date**: Décembre 2025
**Version**: 1.0
**Statut**: ✅ Production Ready
