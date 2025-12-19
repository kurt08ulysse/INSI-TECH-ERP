# Guide de Déploiement sur Serveur

## Options de Déploiement

Votre système de gestion municipale peut être déployé de plusieurs façons selon vos besoins.

---

## Option 1: Serveur Local avec PostgreSQL/MySQL (Recommandé pour Production)

### Avantages
✅ Base de données robuste et performante
✅ Support multi-utilisateurs simultanés
✅ Meilleure gestion des transactions
✅ Sauvegardes automatiques
✅ Scalabilité

### Étape 1: Installer PostgreSQL ou MySQL

#### Pour PostgreSQL:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# Démarrer le service
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### Pour MySQL:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install mysql-server

# Démarrer le service
sudo systemctl start mysql
sudo systemctl enable mysql
```

### Étape 2: Créer la base de données

#### PostgreSQL:
```bash
# Se connecter à PostgreSQL
sudo -u postgres psql

# Créer la base de données
CREATE DATABASE mairie_db;

# Créer un utilisateur
CREATE USER mairie_user WITH PASSWORD 'votre_mot_de_passe_securise';

# Donner les permissions
GRANT ALL PRIVILEGES ON DATABASE mairie_db TO mairie_user;

# Quitter
\q
```

#### MySQL:
```bash
# Se connecter à MySQL
sudo mysql

# Créer la base de données
CREATE DATABASE mairie_db;

# Créer un utilisateur
CREATE USER 'mairie_user'@'localhost' IDENTIFIED BY 'votre_mot_de_passe_securise';

# Donner les permissions
GRANT ALL PRIVILEGES ON mairie_db.* TO 'mairie_user'@'localhost';
FLUSH PRIVILEGES;

# Quitter
EXIT;
```

### Étape 3: Modifier le code pour utiliser PostgreSQL/MySQL

Créer un nouveau fichier `database_server.py`:

```python
import psycopg2  # Pour PostgreSQL
# OU
import mysql.connector  # Pour MySQL
from psycopg2.extras import RealDictCursor
import os

# Configuration de la connexion
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'mairie_db'),
    'user': os.getenv('DB_USER', 'mairie_user'),
    'password': os.getenv('DB_PASSWORD', 'votre_mot_de_passe'),
    'port': os.getenv('DB_PORT', '5432')  # 5432 pour PostgreSQL, 3306 pour MySQL
}

def get_connection():
    """Retourne une connexion à la base de données PostgreSQL."""
    conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
    return conn

# Adapter les requêtes SQL pour PostgreSQL/MySQL
# SQLite: AUTOINCREMENT -> PostgreSQL: SERIAL, MySQL: AUTO_INCREMENT
# etc.
```

### Étape 4: Configurer les variables d'environnement

Modifier `.env`:
```env
# Base de données
DB_HOST=localhost
DB_NAME=mairie_db
DB_USER=mairie_user
DB_PASSWORD=votre_mot_de_passe_securise
DB_PORT=5432

# Application
APP_PORT=8501
APP_HOST=0.0.0.0
```

### Étape 5: Installer les dépendances supplémentaires

```bash
# Pour PostgreSQL
pip install psycopg2-binary

# Pour MySQL
pip install mysql-connector-python
```

---

## Option 2: Déploiement sur Serveur Cloud avec SQLite (Simple)

### Avantages
✅ Configuration simple
✅ Pas de serveur de base de données séparé
✅ Fichier unique facile à sauvegarder
✅ Idéal pour petit volume

### Limitations
⚠️ Pas optimal pour usage multi-utilisateurs intensif
⚠️ Performances limitées avec beaucoup de données

### Étape 1: Préparer le serveur

```bash
# Mettre à jour le système
sudo apt update && sudo apt upgrade -y

# Installer Python 3 et pip
sudo apt install python3 python3-pip -y

# Installer git (si nécessaire)
sudo apt install git -y
```

### Étape 2: Cloner le projet sur le serveur

```bash
# Se connecter au serveur via SSH
ssh votre_utilisateur@adresse_ip_serveur

# Cloner le projet
git clone <url_de_votre_repo>
cd Projet-Blockchain-et-IoT-Suivi-intelligent-des-stocks-avec-RFID-et-Hashgraph-master

# Installer les dépendances
pip3 install -r requirements.txt
```

### Étape 3: Configurer le pare-feu

```bash
# Autoriser le port Streamlit (8501)
sudo ufw allow 8501/tcp

# Activer le pare-feu
sudo ufw enable
```

### Étape 4: Lancer l'application

```bash
# Lancer en arrière-plan avec nohup
nohup streamlit run dashboard.py --server.port 8501 --server.address 0.0.0.0 &

# OU créer un service systemd (voir ci-dessous)
```

---

## Option 3: Déploiement avec Docker (Moderne et Portable)

### Avantages
✅ Environnement isolé et reproductible
✅ Facile à déployer sur n'importe quel serveur
✅ Gestion simple avec Docker Compose
✅ Scalabilité facile

### Étape 1: Créer un Dockerfile

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Créer le dossier logs
RUN mkdir -p logs

# Exposer le port Streamlit
EXPOSE 8501

# Commande de démarrage
CMD ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Étape 2: Créer docker-compose.yml (avec PostgreSQL)

```yaml
version: '3.8'

services:
  # Base de données PostgreSQL
  db:
    image: postgres:14
    environment:
      POSTGRES_DB: mairie_db
      POSTGRES_USER: mairie_user
      POSTGRES_PASSWORD: votre_mot_de_passe_securise
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: always

  # Application Streamlit
  app:
    build: .
    ports:
      - "8501:8501"
    environment:
      DB_HOST: db
      DB_NAME: mairie_db
      DB_USER: mairie_user
      DB_PASSWORD: votre_mot_de_passe_securise
      DB_PORT: 5432
    depends_on:
      - db
    volumes:
      - ./logs:/app/logs
      - ./mairie.db:/app/mairie.db  # Si vous utilisez SQLite
    restart: always

volumes:
  postgres_data:
```

### Étape 3: Déployer avec Docker

```bash
# Construire et lancer
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Arrêter
docker-compose down

# Mettre à jour
docker-compose pull
docker-compose up -d
```

---

## Option 4: Créer un Service Systemd (Linux)

Pour que l'application démarre automatiquement au démarrage du serveur.

### Créer le fichier service

```bash
sudo nano /etc/systemd/system/mairie.service
```

### Contenu du fichier:

```ini
[Unit]
Description=Systeme de Gestion Municipale
After=network.target

[Service]
Type=simple
User=votre_utilisateur
WorkingDirectory=/chemin/vers/votre/projet
ExecStart=/usr/local/bin/streamlit run dashboard.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Activer le service

```bash
# Recharger systemd
sudo systemctl daemon-reload

# Activer le service au démarrage
sudo systemctl enable mairie.service

# Démarrer le service
sudo systemctl start mairie.service

# Vérifier le statut
sudo systemctl status mairie.service

# Voir les logs
sudo journalctl -u mairie.service -f
```

---

## Option 5: Utiliser Nginx comme Reverse Proxy

Pour avoir un nom de domaine et HTTPS.

### Étape 1: Installer Nginx

```bash
sudo apt install nginx
```

### Étape 2: Configurer Nginx

```bash
sudo nano /etc/nginx/sites-available/mairie
```

### Contenu:

```nginx
server {
    listen 80;
    server_name votre-domaine.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Étape 3: Activer le site

```bash
sudo ln -s /etc/nginx/sites-available/mairie /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Étape 4: Installer SSL avec Let's Encrypt (HTTPS)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d votre-domaine.com
```

---

## Recommandations de Sécurité

### 1. Sauvegardes Automatiques

```bash
# Créer un script de sauvegarde
sudo nano /usr/local/bin/backup-mairie.sh
```

```bash
#!/bin/bash
# Script de sauvegarde

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/mairie"
DB_FILE="/chemin/vers/mairie.db"

mkdir -p $BACKUP_DIR

# Sauvegarder SQLite
cp $DB_FILE $BACKUP_DIR/mairie_$DATE.db

# OU sauvegarder PostgreSQL
# pg_dump -U mairie_user mairie_db > $BACKUP_DIR/mairie_$DATE.sql

# Garder seulement les 30 dernières sauvegardes
find $BACKUP_DIR -name "mairie_*.db" -mtime +30 -delete

echo "Sauvegarde terminée: $BACKUP_DIR/mairie_$DATE.db"
```

```bash
# Rendre exécutable
sudo chmod +x /usr/local/bin/backup-mairie.sh

# Ajouter à crontab (tous les jours à 2h du matin)
sudo crontab -e
0 2 * * * /usr/local/bin/backup-mairie.sh
```

### 2. Sécuriser les accès

- Utiliser des mots de passe forts
- Configurer un pare-feu (ufw, iptables)
- Utiliser HTTPS (SSL/TLS)
- Limiter les accès par IP si possible
- Activer l'authentification dans Streamlit

### 3. Monitoring

```bash
# Installer htop pour surveiller les ressources
sudo apt install htop

# Surveiller les logs
tail -f logs/app.log
```

---

## Accès à Distance

Une fois déployé sur serveur:

### Accès local:
```
http://localhost:8501
```

### Accès depuis internet:
```
http://adresse_ip_serveur:8501
# OU avec nom de domaine
https://votre-domaine.com
```

---

## Résumé des Options

| Option | Complexité | Performance | Scalabilité | Coût |
|--------|-----------|-------------|-------------|------|
| SQLite sur serveur | ⭐ Facile | ⭐⭐ Moyenne | ⭐ Limitée | 💰 Gratuit |
| PostgreSQL local | ⭐⭐ Moyenne | ⭐⭐⭐ Bonne | ⭐⭐⭐ Excellente | 💰 Gratuit |
| Docker + PostgreSQL | ⭐⭐⭐ Avancée | ⭐⭐⭐ Excellente | ⭐⭐⭐ Excellente | 💰 Gratuit |
| Cloud (AWS/Azure) | ⭐⭐⭐ Avancée | ⭐⭐⭐⭐ Excellente | ⭐⭐⭐⭐ Illimitée | 💰💰 Payant |

---

## Support et Aide

Pour toute question sur le déploiement:
1. Consultez la documentation de votre hébergeur
2. Vérifiez les logs: `logs/app.log`
3. Testez d'abord en local avant de déployer

---

**Date de création:** 17 Décembre 2025
**Version:** 1.0
