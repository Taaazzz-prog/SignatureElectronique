# 📝 Signature Électronique PDF

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![Security](https://img.shields.io/badge/Security-reCAPTCHA_v3-red)

Application web pour signer des fichiers PDF électroniquement avec gestion de comptes utilisateurs.

---

## 🚀 Fonctionnalités

- ✍️ Signature de documents PDF avec canvas interactif
- 📍 Positionnement personnalisable de la signature
- 👤 Gestion de comptes utilisateurs (inscription/connexion)
- 💾 Sauvegarde et réutilisation de signatures
- 📜 Historique des documents signés
- 🛡️ Protection anti-bot avec reCAPTCHA v3
- 🔐 Sécurité : hashing bcrypt, secrets chiffrés
- 🐳 Déploiement avec Docker Swarm

---

## 🛠️ Stack Technique

- **Backend** : Python 3.11, Flask 3.0
- **Base de données** : SQLite
- **Signature PDF** : pyHanko, reportlab
- **Sécurité** : bcrypt, reCAPTCHA v3
- **Frontend** : HTML5, CSS3, JavaScript (Vanilla)
- **Conteneurisation** : Docker, Docker Swarm
- **CI/CD** : GitHub Actions → GHCR

---

## 📦 Installation locale

### Prérequis
- Python 3.11+
- pip

### Installation

```bash
# Cloner le repository
git clone https://github.com/Taaazzz-prog/SignatureElectronique.git
cd SignatureElectronique

# Créer un environnement virtuel
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Installer les dépendances
pip install -r requirements.txt

# Créer le fichier .env
cp .env.example .env
# Éditer .env et configurer vos secrets

# Lancer l'application
python app.py
```

L'application sera accessible sur http://localhost:5000

---

## 🔐 Configuration

Créer un fichier `.env` à la racine :

```env
SECRET_KEY=votre-cle-secrete-unique
RECAPTCHA_SECRET_KEY=votre-cle-recaptcha
GOODFLAG_API_TOKEN=optionnel
DATABASE_PATH=signature_app.db
FLASK_ENV=development
DEBUG=True
```

**Générer une SECRET_KEY** :
```python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Obtenir une clé reCAPTCHA** : https://www.google.com/recaptcha/admin/create

---

## 🐳 Docker

### Build local

```bash
docker build -t signature-app .
docker run -p 5000:5000 signature-app
```

### Image publiée

L'image est automatiquement buildée par GitHub Actions et publiée sur GitHub Container Registry :

```bash
docker pull ghcr.io/taaazzz-prog/signatureelectronique:latest
```

---

## 🏗️ Structure du projet

```
SignatureElectronique/
├── app.py                    # Application Flask principale
├── database.py               # Gestion de la base de données
├── digital_signature.py      # Signature PDF avec pyHanko
├── goodflag_api.py          # API Goodflag pour signatures qualifiées
├── secrets_helper.py        # Gestion des secrets (Docker Secrets / env vars)
├── templates/               # Templates HTML
│   ├── index_new.html
│   ├── signatures.html
│   ├── history.html
│   └── account.html
├── static/                  # CSS et JavaScript
│   ├── css/
│   └── js/
├── Dockerfile
├── requirements.txt
└── .env.example
```

---

## 🔒 Sécurité

- ✅ Hashing des mots de passe avec bcrypt (12 rounds)
- ✅ Protection CSRF avec Flask
- ✅ Secrets chiffrés avec Docker Secrets en production
- ✅ Validation des uploads (types MIME)
- ✅ Protection anti-bot avec reCAPTCHA v3
- ✅ Headers de sécurité HTTP
- ✅ HTTPS avec Let's Encrypt

---

## 📄 Licence

MIT License - Voir le fichier LICENSE pour plus de détails.

---

## 👨‍💻 Auteur

**Taaazzz**
- GitHub: [@Taaazzz-prog](https://github.com/Taaazzz-prog)

---

## 🙏 Remerciements

- [pyHanko](https://github.com/MatthiasValvekens/pyHanko) - Signature PDF
- [Flask](https://flask.palletsprojects.com/) - Framework web
- [ReportLab](https://www.reportlab.com/) - Génération PDF
