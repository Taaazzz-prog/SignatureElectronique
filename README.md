# 📝 Signature Électronique PDF

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![Security](https://img.shields.io/badge/Security-reCAPTCHA_v3-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

Application web sécurisée pour signer des fichiers PDF électroniquement avec gestion de comptes utilisateurs.

## 🌐 Demo en ligne

**URL de production** : [https://signatureelectronique.taaazzz-prog.fr](https://signatureelectronique.taaazzz-prog.fr)

---

## 🚀 Fonctionnalités

### Signature de documents
- ✅ Upload de fichiers PDF (drag & drop ou sélection)
- ✍️ Création de signature à la souris ou au tactile
- 📍 Positionnement personnalisable de la signature
- 📄 Support multi-pages
- 💾 Téléchargement automatique du PDF signé
- 🎨 Interface moderne et intuitive avec mode sombre

### Gestion de compte
- 👤 Inscription et connexion sécurisées
- 📧 Validation d'email avec regex
- 🔐 Hashing bcrypt pour les mots de passe
- 📊 Historique des signatures
- 📈 Statistiques personnalisées
- ⚙️ Préférences personnalisables (mode sombre, notifications, auto-save)

### Sécurité
- 🛡️ Protection anti-bot avec Google reCAPTCHA v3
- 🔒 Hashing bcrypt (12 rounds) pour tous les mots de passe
- 🔄 Migration automatique des anciens mots de passe SHA-256
- 🔑 SECRET_KEY pour la sécurité des sessions
- ✅ Validation stricte des emails

## 📋 Prérequis

- Python 3.11 ou supérieur
- pip (gestionnaire de paquets Python)
- Docker (optionnel, pour le déploiement)
- Compte Google reCAPTCHA v3 (pour la protection anti-bot)

## 🔧 Installation

1. **Cloner ou naviguer vers le projet**
```powershell
cd "d:\WEB API\SignatureElectronique"
```

2. **Créer un environnement virtuel (recommandé)**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. **Installer les dépendances**
```powershell
pip install -r requirements.txt
```

4. **Configurer les variables d'environnement**
```powershell
# Copier le fichier d'exemple
Copy-Item .env.example .env

# Éditer .env et configurer :
# - SECRET_KEY (générer avec: python -c "import secrets; print(secrets.token_urlsafe(32))")
# - RECAPTCHA_SECRET_KEY (obtenir sur https://www.google.com/recaptcha/admin/create)
```

## ▶️ Lancement

1. **Démarrer le serveur**
```powershell
python app.py
```

2. **Ouvrir votre navigateur**
```
http://localhost:5000
```

## 📖 Utilisation

### Création de compte
1. Cliquez sur "Inscription" dans la navigation
2. Remplissez le formulaire (nom, email, mot de passe)
3. La protection reCAPTCHA v3 vérifie automatiquement que vous n'êtes pas un bot
4. Connectez-vous avec vos identifiants

### Signature de documents
1. **Charger un PDF**
   - Glissez-déposez votre fichier PDF dans la zone prévue
   - Ou cliquez sur "Choisir un fichier PDF"

2. **Créer votre signature**
   - Dessinez votre signature sur le canvas blanc
   - Utilisez "Effacer" pour recommencer
   - Utilisez "Annuler" pour supprimer le dernier trait

3. **Configurer la position**
   - Sélectionnez la page à signer
   - Ajustez les positions X et Y
   - Modifiez la largeur si nécessaire

4. **Signer**
   - Cliquez sur "Signer le PDF"
   - Le fichier signé se téléchargera automatiquement

### Gestion de compte
- **Historique** : Consultez toutes vos signatures passées
- **Statistiques** : Visualisez vos statistiques de signature
- **Compte** : Gérez vos informations et préférences
  - Mode sombre/clair
  - Notifications
  - Auto-save des signatures
  - Mode tactile optimisé

## 📁 Structure du projet

```
SignatureElectronique/
├── app.py                      # Serveur Flask (API backend)
├── database.py                 # Gestion base de données SQLite
├── templates/
│   ├── index.html             # Page d'accueil
│   ├── base.html              # Template de base
│   ├── account.html           # Page compte utilisateur
│   ├── history.html           # Historique des signatures
│   └── stats.html             # Statistiques
├── static/
│   ├── css/                   # Feuilles de style (+ mode sombre)
│   └── js/                    # Scripts JavaScript
├── uploads/                   # PDFs uploadés (auto, ignoré git)
├── signed/                    # PDFs signés (auto, ignoré git)
├── signatures/                # Signatures temporaires (auto, ignoré git)
├── .env                       # Variables d'environnement (SECRET!)
├── .env.example               # Template de configuration
├── docker-compose.yml         # Configuration Docker
├── Dockerfile                 # Image Docker
├── requirements.txt           # Dépendances Python
└── README.md                  # Documentation
```

## 🛠️ Configuration

### Variables d'environnement (.env)

```bash
# Clé secrète Flask (OBLIGATOIRE EN PRODUCTION)
SECRET_KEY=votre-cle-secrete-unique-32-caracteres

# Clé secrète reCAPTCHA v3 (RECOMMANDÉ)
RECAPTCHA_SECRET_KEY=votre-cle-secrete-recaptcha

# Chemin de la base de données
DATABASE_PATH=/app/data/signature_app.db
```

### Configuration reCAPTCHA v3

1. Créez un compte sur [Google reCAPTCHA Admin](https://www.google.com/recaptcha/admin/create)
2. Choisissez **reCAPTCHA v3**
3. Ajoutez vos domaines (localhost pour dev, votre domaine pour prod)
4. Récupérez :
   - **Site Key** (publique) → À mettre dans `static/js/common.js`
   - **Secret Key** (privée) → À mettre dans `.env`

### Limites de fichiers
Par défaut, la taille maximale des fichiers est de 16 MB. Pour modifier :
```python
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB
```

### Déploiement Docker Swarm (Production)

L'application utilise **Docker Swarm** pour un déploiement production robuste avec résilience et haute disponibilité :

```bash
# Sur le serveur : Construire l'image
docker build -t signature-app:latest .

# Déployer la stack Swarm
docker stack deploy -c docker-compose.yml signature

# Voir les services
docker service ls | grep signature

# Logs en temps réel
docker service logs -f signature_signature-app

# Mettre à jour le service
docker service update --image signature-app:latest signature_signature-app

# Supprimer la stack
docker stack rm signature
```

#### Script de déploiement automatique (Windows)

```powershell
# Déploie automatiquement sur le serveur
.\deploy.ps1

# Surveille l'état du service
.\monitor.ps1

# Régénère le certificat SSL si nécessaire
.\regenerate-ssl.ps1
```

#### Configuration Traefik (Swarm)
- Reverse proxy avec SSL automatique (Let's Encrypt)
- Réseau : `traefik-public` (overlay swarm)
- Domaine : `signatureelectronique.taaazzz-prog.fr`
- Port interne : 5000 (Gunicorn)

## 🔒 Sécurité

### Protection des comptes
- **Bcrypt** : Hashing des mots de passe avec 12 rounds
- **Migration automatique** : Anciens mots de passe SHA-256 convertis en bcrypt
- **Validation email** : Regex stricte pour les emails
- **SECRET_KEY** : Protection des sessions Flask

### Protection anti-bot
- **reCAPTCHA v3** : Détection intelligente des bots sans CAPTCHA visible
- **Score adaptatif** : Seuil de 0.5 pour bloquer les bots suspects
- Pas de limite de requêtes pour les utilisateurs légitimes

### Protection des données
- Fichiers stockés avec des noms UUID uniques
- Validation stricte des types de fichiers (PDF uniquement)
- Limite de taille de fichier configurée (16 MB par défaut)
- `.env` dans `.gitignore` (secrets jamais commités)
- Base de données SQLite avec transactions sécurisées

## 🐛 Dépannage

### Erreur "Module not found"
```powershell
pip install -r requirements.txt
```

### Port déjà utilisé
Modifiez le port dans `app.py` ou arrêtez l'application utilisant le port 5000

### Problèmes de permissions
Exécutez PowerShell en tant qu'administrateur

### 🔒 Erreur SSL "ERR_CERT_AUTHORITY_INVALID" en production

Si vous rencontrez l'erreur `net::ERR_CERT_AUTHORITY_INVALID` en accédant à l'application, suivez ces étapes :

#### 1️⃣ Diagnostic automatique
Exécutez le script de diagnostic :
```powershell
.\fix-ssl.ps1
```

#### 2️⃣ Vérifications manuelles sur le serveur

**a) Vérifier que Traefik est actif :**
```bash
ssh taaazzz@51.75.55.185
docker ps | grep traefik
```

**b) Vérifier les logs Traefik :**
```bash
docker logs faildaily-traefik-ssl --tail 100 | grep -i "error\|certificate"
```

**c) Vérifier le réseau Docker :**
```bash
docker network ls | grep faildaily-ssl-network
```

**d) Vérifier les certificats Let's Encrypt :**
```bash
docker exec faildaily-traefik-ssl cat /letsencrypt/acme.json | grep signatureelectronique
```

#### 3️⃣ Solutions courantes

**Problème : Traefik non démarré**
```bash
cd /path/to/faildaily
docker-compose up -d
```

**Problème : Certificat non généré**
```bash
cd /home/taaazzz/SignatureElectronique
docker-compose down
docker-compose up -d
# Attendre 2-3 minutes pour la génération Let's Encrypt
docker logs faildaily-traefik-ssl -f
```

**Problème : DNS mal configuré**
- Vérifier que `votre-domaine.com` pointe vers l'IP de votre serveur
- Attendre la propagation DNS (jusqu'à 24h)
- Tester avec : `nslookup votre-domaine.com`

**Problème : Ports 80/443 non accessibles**
```bash
# Vérifier que les ports sont ouverts
sudo ufw status
sudo netstat -tulpn | grep ':80\|:443'
```

#### 4️⃣ Forcer la régénération du certificat

Si rien ne fonctionne :
```bash
# Sur le serveur
docker stack rm signature

# Redémarrer Traefik si nécessaire puis redéployer
docker stack deploy -c docker-compose.yml signature
```

#### 5️⃣ Contourner temporairement (DEV uniquement)

Pour tester localement sans SSL :
- Dans Chrome : taper `thisisunsafe` sur la page d'erreur
- Ou accéder via `http://` au lieu de `https://` (si configuré)

## 📝 Notes

- Les fichiers uploadés et signés sont stockés localement
- Pour la production, ajoutez un système de nettoyage automatique des anciens fichiers
- Considérez l'ajout d'une authentification pour un usage professionnel
- Les signatures sont en format PNG transparent

## 🎯 Améliorations futures possibles

- [x] Authentification utilisateur
- [x] Base de données pour historique
- [x] Statistiques personnalisées
- [x] Mode sombre
- [x] Protection anti-bot (reCAPTCHA v3)
- [x] Hashing sécurisé des mots de passe (bcrypt)
- [ ] Prévisualisation PDF intégrée
- [ ] Signatures prédéfinies sauvegardées
- [ ] Support de multiples signatures par document
- [ ] Export en différents formats
- [ ] Certificats numériques (PKI)
- [ ] API REST documentée
- [ ] Notifications email
- [ ] Partage de documents signés

## 📄 Licence

Projet libre d'utilisation pour usage personnel et professionnel.

## 👤 Support

Pour toute question ou problème, créez une issue dans le projet.
