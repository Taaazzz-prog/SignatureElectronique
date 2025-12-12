# � SignatureElectronique

Application web Flask pour la signature électronique de documents PDF.

## 📋 Fonctionnalités

- ✍️ Signature de documents PDF
- 🖼️ Signature graphique (dessin à la main)
- 📄 Téléchargement des documents signés
- 🔐 Authentification utilisateur
- 📊 Historique des signatures
- 🔒 Sécurité ReCaptcha

## 🚀 Installation

### Prérequis

- Python 3.10+
- Docker (optionnel)

### Installation locale

```bash
# Cloner le repository
git clone https://github.com/Taaazzz-prog/SignatureElectronique.git
cd SignatureElectronique

# Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python src/app.py
```

### Avec Docker

```bash
# Build l'image
docker build -t signatureelectronique .

# Lancer le conteneur
docker run -p 5000:5000 signatureelectronique
```

## 📁 Structure

```
SignatureElectronique/
├── src/                    # Code source
│   ├── app.py             # Application Flask
│   ├── database.py        # Gestion BDD
│   └── digital_signature.py  # Logique de signature
├── templates/             # Templates HTML
├── static/               # CSS et JavaScript
├── requirements.txt      # Dépendances Python
└── Dockerfile           # Configuration Docker
```

## 🛠️ Technologies

- **Backend:** Flask, SQLite
- **Signature PDF:** pyHanko
- **Frontend:** HTML, CSS, JavaScript
- **Sécurité:** Google ReCaptcha

## 📦 Déploiement

L'image Docker est automatiquement buildée via GitHub Actions et disponible sur GHCR.

```bash
docker pull ghcr.io/taaazzz-prog/signatureelectronique:latest
```

## 📄 Licence

Projet personnel.

## 👤 Auteur

**Taaazzz-prog**

---

*Application de signature électronique PDF sécurisée*
