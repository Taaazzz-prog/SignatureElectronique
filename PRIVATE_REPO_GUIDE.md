# 🔐 Guide : Repository Privé pour SignatureElectronique

## 🎯 Pourquoi deux repositories ?

### Repository PUBLIC (`SignatureElectronique`)
- **Objectif** : Code source, documentation générique, portfolio
- **Contenu** : Code applicatif sans secrets
- **Visibilité** : Tout le monde

### Repository PRIVÉ (`SignatureElectronique-private` ou `-deploy`)
- **Objectif** : Configuration de production, secrets, infrastructure
- **Contenu** : Vraies valeurs, adresses réelles, procédures internes
- **Visibilité** : Vous uniquement (ou votre équipe)

---

## 📁 Structure recommandée du Repository PRIVÉ

```
SignatureElectronique-private/
├── .env                              # 🔴 SECRETS RÉELS
├── docker-compose.prod.yml           # 🔴 Configuration avec VRAI domaine
├── deploy-swarm-prod.ps1             # 🔴 Script avec VRAIE adresse SSH
├── build-and-push-prod.ps1           # 🔴 Configuration réelle
│
├── infrastructure/
│   ├── traefik-config.yml            # Configuration Traefik complète
│   ├── server-setup.md               # Procédure de setup du serveur OVH
│   └── ssh-config                    # Configuration SSH
│
├── secrets/
│   ├── create-secrets.ps1            # Script de création des secrets Docker
│   ├── rotate-secrets.ps1            # Script de rotation des secrets
│   └── backup-secrets.ps1            # Backup des secrets
│
├── monitoring/
│   ├── monitor-prod.ps1              # Monitoring avec vraies adresses
│   └── alerting-config.yml           # Configuration des alertes
│
├── backups/
│   ├── backup-db.ps1                 # Scripts de backup DB
│   └── restore-db.ps1                # Scripts de restauration
│
├── docs/
│   ├── DEPLOYMENT_PROD.md            # Procédures avec vraies valeurs
│   ├── TROUBLESHOOTING.md            # Résolution de problèmes
│   ├── RUNBOOK.md                    # Documentation opérationnelle
│   └── INCIDENTS.md                  # Log des incidents
│
└── README.md                         # Documentation du repo privé
```

---

## 🔴 Fichiers à DÉPLACER du repo public au privé

### 1️⃣ **Fichiers de configuration avec vraies valeurs**

| Fichier actuel | Action | Nouveau fichier privé |
|----------------|--------|----------------------|
| `.env` (local) | ✅ Déjà exclu | `.env` |
| `docker-compose.yml` | ⚠️ Créer version prod | `docker-compose.prod.yml` |
| `deploy-swarm.ps1` | ⚠️ Créer version prod | `deploy-swarm-prod.ps1` |
| `build-and-push.ps1` | ⚠️ Créer version prod | `build-and-push-prod.ps1` |

### 2️⃣ **Documentation avec informations sensibles**

| Contenu | Fichier public (actuel) | Nouveau fichier privé |
|---------|------------------------|----------------------|
| Procédures de déploiement | `README.md` | `docs/DEPLOYMENT_PROD.md` |
| Guide de migration | `MIGRATION_SWARM.md` | `docs/MIGRATION_PROD.md` |
| IP serveur, domaine réel | Anonymisé ✅ | `infrastructure/server-setup.md` |

### 3️⃣ **Scripts avec credentials réels**

Créer des versions "prod" dans le repo privé :
- `deploy-swarm-prod.ps1` avec `taaazzz@51.75.55.185`
- `monitor-prod.ps1` avec vraie IP
- `fix-ssl-prod.ps1` avec vraie configuration

---

## 🚀 Plan de migration vers 2 repositories

### Étape 1️⃣ : Créer le repository privé sur GitHub

```bash
# Sur GitHub, créer : SignatureElectronique-private (PRIVATE)
```

### Étape 2️⃣ : Initialiser le repo privé localement

```powershell
# Dans un nouveau dossier
cd "D:\WEB API\"
mkdir SignatureElectronique-private
cd SignatureElectronique-private

git init
git branch -M main
git remote add origin https://github.com/Taaazzz-prog/SignatureElectronique-private.git
```

### Étape 3️⃣ : Créer les fichiers de production

#### `.env` (SECRETS RÉELS)
```env
SECRET_KEY=VOTRE_VRAIE_CLE_ICI
RECAPTCHA_SECRET_KEY=VOTRE_VRAIE_CLE_RECAPTCHA
GOODFLAG_API_TOKEN=VOTRE_TOKEN_GOODFLAG
DATABASE_PATH=/app/data/signature_app.db
FLASK_ENV=production
DEBUG=False
```

#### `docker-compose.prod.yml` (VRAI DOMAINE)
```yaml
version: '3.8'
services:
  signature-app:
    image: ghcr.io/taaazzz-prog/signatureelectronique:latest
    # ... reste de la config ...
    deploy:
      labels:
        - "traefik.http.routers.signature.rule=Host(`signatureelectronique.taaazzz-prog.fr`)"
        # Autres labels avec vraie config
```

#### `deploy-swarm-prod.ps1` (VRAIE ADRESSE SSH)
```powershell
$SERVER = "taaazzz@51.75.55.185"
$REMOTE_PATH = "/home/taaazzz/SignatureElectronique"
$STACK_NAME = "signature"

# Script complet avec vraies valeurs
```

#### `infrastructure/server-setup.md`
```markdown
# Configuration Serveur OVH

- **IP** : 51.75.55.185
- **SSH** : taaazzz@51.75.55.185
- **Domaine** : signatureelectronique.taaazzz-prog.fr
- **OS** : Ubuntu 22.04 LTS
- **Node Swarm** : Taaazzz-Dedie

## Accès

```bash
ssh taaazzz@51.75.55.185
```

## Ports ouverts
- 80 (HTTP)
- 443 (HTTPS)
- 22 (SSH)
```

#### `.gitignore` (pour le repo privé)
```gitignore
# Même si c'est privé, on exclut quand même certains fichiers
__pycache__/
*.pyc
.vscode/
.DS_Store
*.log

# Backups de base de données (trop gros)
backups/*.db
backups/*.sql

# Fichiers temporaires
*.tmp
*.bak
```

### Étape 4️⃣ : Structure recommandée

Créer ces dossiers et fichiers :

```powershell
# Dans SignatureElectronique-private/
New-Item -ItemType Directory -Path infrastructure, secrets, monitoring, backups, docs

# Créer les fichiers
@'
# Repository Privé - SignatureElectronique

Configuration de production, secrets et documentation opérationnelle.

⚠️ **REPOSITORY PRIVÉ** - Ne jamais rendre public

## Contenu

- `docker-compose.prod.yml` : Configuration Swarm avec vrai domaine
- `deploy-swarm-prod.ps1` : Script de déploiement avec vraie adresse SSH
- `.env` : Secrets de production
- `infrastructure/` : Configuration serveur
- `docs/` : Documentation opérationnelle

## Référence

Code source public : https://github.com/Taaazzz-prog/SignatureElectronique
'@ | Out-File README.md -Encoding utf8
```

### Étape 5️⃣ : Commit et push

```powershell
git add .
git commit -m "🔒 Initial commit - Configuration de production et secrets"
git push -u origin main
```

---

## 🔗 Lien entre les deux repositories

### Dans le repo PUBLIC (`SignatureElectronique`)

Ajouter dans `README.md` :

```markdown
## 🔒 Configuration de production

La configuration de production (avec secrets et adresses réelles) se trouve dans un repository privé séparé.

Pour déployer en production :
1. Cloner le repository de configuration privée
2. Configurer les secrets Docker sur le serveur
3. Utiliser les scripts de déploiement du repo privé
```

### Dans le repo PRIVÉ

Ajouter dans `README.md` :

```markdown
## 📦 Code source

Code source public : https://github.com/Taaazzz-prog/SignatureElectronique

Ce repository contient uniquement la configuration de production.
```

---

## 🔄 Workflow de développement

### Développement local
```bash
# 1. Cloner le repo public
git clone https://github.com/Taaazzz-prog/SignatureElectronique.git
cd SignatureElectronique

# 2. Copier .env depuis le repo privé
cp ../SignatureElectronique-private/.env .

# 3. Développer normalement
```

### Déploiement
```bash
# 1. Push le code dans le repo public
cd SignatureElectronique
git push origin main

# 2. GitHub Actions build automatiquement l'image

# 3. Déployer avec les scripts du repo privé
cd ../SignatureElectronique-private
.\deploy-swarm-prod.ps1
```

---

## ✅ Avantages de cette approche

### 🌐 Repository PUBLIC
- ✅ Portfolio professionnel
- ✅ Partage de code open-source
- ✅ Contributions de la communauté
- ✅ Documentation technique

### 🔒 Repository PRIVÉ
- ✅ Secrets protégés
- ✅ Configuration d'infrastructure
- ✅ Documentation opérationnelle
- ✅ Procédures internes
- ✅ Historique des incidents

---

## 📋 Checklist de migration

- [ ] Créer le repository privé sur GitHub
- [ ] Initialiser le repo localement
- [ ] Créer `.env` avec les vrais secrets
- [ ] Créer `docker-compose.prod.yml` avec vrai domaine
- [ ] Créer `deploy-swarm-prod.ps1` avec vraie adresse SSH
- [ ] Créer la structure de dossiers (`infrastructure/`, `secrets/`, etc.)
- [ ] Documenter la configuration serveur avec vraies valeurs
- [ ] Ajouter les scripts de backup/monitoring
- [ ] Créer `DEPLOYMENT_PROD.md` avec procédures complètes
- [ ] Commit et push vers le repo privé
- [ ] Mettre à jour le README du repo public avec référence au privé
- [ ] Tester le workflow de déploiement

---

## 🆘 Si vous devez partager avec un collègue

```bash
# Ajouter le collègue au repo privé
# Sur GitHub : Settings > Collaborators > Add people
```

**Inviter uniquement les personnes de confiance !**

---

## 🔐 Sécurité du repository privé

### À FAIRE
- ✅ Activer "Private" sur GitHub
- ✅ Activer l'authentification 2FA sur votre compte GitHub
- ✅ Utiliser des tokens d'accès personnels (PAT) au lieu de mot de passe
- ✅ Restreindre l'accès aux collaborateurs de confiance
- ✅ Faire des backups réguliers

### À NE PAS FAIRE
- ❌ Ne jamais rendre public accidentellement
- ❌ Ne pas partager le lien de clone avec des non-autorisés
- ❌ Ne pas commit de fichiers de backup de DB (trop gros + données sensibles)

---

**🎯 Résultat final** :
- **Repository PUBLIC** : Code propre, documenté, sans secrets
- **Repository PRIVÉ** : Configuration réelle, secrets, infrastructure

Cette séparation est la **meilleure pratique** professionnelle ! 🚀
