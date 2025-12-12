# 🔄 Guide de migration vers Docker Swarm + Secrets + GHCR

## ✅ Ce qui a changé

### Avant (Docker Compose + Variables ENV)
```bash
# Secrets en clair dans .env ou docker-compose.yml
docker-compose up -d
```

### Maintenant (Docker Swarm + Secrets + GHCR)
```bash
# Secrets chiffrés dans Docker Swarm
# Images versionnées sur GitHub Container Registry
docker stack deploy -c docker-compose.yml signature
```

---

## 🚀 Migration étape par étape

### 1️⃣ Build et push de l'image vers GHCR

#### Option A : Build local + push manuel
```powershell
# Sur votre machine locale
.\build-and-push.ps1

# Première fois : Se connecter à GHCR
# 1. Créer un token: https://github.com/settings/tokens/new?scopes=write:packages
# 2. Se connecter:
echo VOTRE_TOKEN | docker login ghcr.io -u VOTRE_USERNAME --password-stdin
```

#### Option B : Automatique via GitHub Actions
```bash
# Le workflow .github/workflows/docker-build.yml se déclenche automatiquement
# à chaque push sur main
git push origin main

# Voir le build : https://github.com/Taaazzz-prog/SignatureElectronique/actions
```

### 2️⃣ Créer les secrets Docker sur le serveur

```bash
# Se connecter au serveur
ssh user@your-server

# Créer les secrets (UNE SEULE FOIS)
# SECRET_KEY : Générer avec: python -c "import secrets; print(secrets.token_urlsafe(32))"
echo "VOTRE_SECRET_KEY_32_CARACTERES" | docker secret create signature_secret_key -

# RECAPTCHA_SECRET_KEY : Depuis https://www.google.com/recaptcha/admin
echo "VOTRE_RECAPTCHA_KEY" | docker secret create signature_recaptcha_key -

# GOODFLAG_API_TOKEN : Depuis https://goodflag.com
echo "VOTRE_GOODFLAG_TOKEN" | docker secret create signature_goodflag_token -

# Vérifier
docker secret ls
```

**Résultat attendu :**
```
ID                          NAME                          CREATED          UPDATED
abc123def456                signature_secret_key          5 seconds ago    5 seconds ago
ghi789jkl012                signature_recaptcha_key       3 seconds ago    3 seconds ago
mno345pqr678                signature_goodflag_token      1 second ago     1 second ago
```

### 3️⃣ Rendre l'image GHCR publique (optionnel mais recommandé)

Pour éviter de s'authentifier sur le serveur :

1. Aller sur https://github.com/Taaazzz-prog/SignatureElectronique/pkgs/container/signatureelectronique/settings
2. Cliquer sur "Change visibility"
3. Sélectionner "Public"
4. Confirmer

### 4️⃣ Déployer sur le serveur

#### Option A : Script automatique (recommandé)
```powershell
# Sur votre machine locale
.\deploy-swarm.ps1

# Première fois avec création des secrets
.\deploy-swarm.ps1 -CreateSecrets
```

#### Option B : Déploiement manuel
```bash
# Sur le serveur
ssh taaazzz@51.75.55.185

cd /home/taaazzz/SignatureElectronique

# Pull de l'image depuis GHCR
docker pull ghcr.io/taaazzz-prog/signatureelectronique:latest

# Déployer la stack
docker stack deploy -c docker-compose.yml signature

# Vérifier
docker service ls | grep signature
docker service ps signature_signature-app
```

### 5️⃣ Vérification

```bash
# Logs en temps réel
ssh user@your-server 'docker service logs -f signature_signature-app'

# Vérifier que les secrets sont montés
ssh user@your-server 'docker exec $(docker ps -q -f name=signature_signature-app) ls -la /run/secrets/'

# Résultat attendu :
# -r--r--r-- 1 root root  32 Dec 12 10:00 signature_secret_key
# -r--r--r-- 1 root root  40 Dec 12 10:00 signature_recaptcha_key
# -r--r--r-- 1 root root  64 Dec 12 10:00 signature_goodflag_token
```

### 6️⃣ Test de l'application

```bash
# Test HTTP
curl -I https://signatureelectronique.taaazzz-prog.fr

# Test API status
curl https://signatureelectronique.taaazzz-prog.fr/api/goodflag/status
```

---

## 🔒 Sécurité : Secrets vs Variables ENV

| Aspect | Variables ENV (.env) | Docker Secrets (Swarm) |
|--------|---------------------|------------------------|
| **Stockage** | Fichier texte clair | Chiffré AES-256 dans Raft |
| **Visibilité** | `docker inspect` les affiche | Invisibles dans inspect |
| **Logs** | Peuvent fuiter | Jamais dans les logs |
| **Rotation** | Redéploiement complet | `docker secret update` |
| **Audit** | Aucun | Traçabilité complète |
| **Montage** | Variable d'environnement | tmpfs (RAM) en lecture seule |

---

## 📦 Workflow complet de déploiement

### Développement local
```bash
# 1. Modifier le code
# 2. Tester en local avec .env (variables d'environnement classiques)
python app.py

# 3. Commit et push
git add .
git commit -m "feat: nouvelle fonctionnalité"
git push origin main
```

### Build automatique (GitHub Actions)
```bash
# GitHub Actions construit automatiquement l'image
# et la pousse sur ghcr.io/taaazzz-prog/signatureelectronique:latest
```

### Déploiement production
```powershell
# Sur votre machine locale
.\deploy-swarm.ps1

# L'image est automatiquement récupérée depuis GHCR
# Les secrets sont lus depuis Docker Swarm
# Le service est mis à jour sans downtime
```

---

## 🔄 Rotation des secrets

### Méthode recommandée (sans downtime)
```bash
ssh user@your-server

# 1. Créer un nouveau secret avec suffixe _v2
echo "NOUVEAU_SECRET" | docker secret create signature_secret_key_v2 -

# 2. Mettre à jour le service
docker service update \
  --secret-rm signature_secret_key \
  --secret-add source=signature_secret_key_v2,target=signature_secret_key \
  signature_signature-app

# 3. Supprimer l'ancien secret
docker secret rm signature_secret_key

# 4. Renommer le nouveau (optionnel, pour propreté)
# Note: Pas de commande directe, garder _v2 ou refaire la procédure
```

### Méthode simple (avec redémarrage)
```bash
# 1. Supprimer la stack
docker stack rm signature

# 2. Supprimer les secrets
docker secret rm signature_secret_key signature_recaptcha_key signature_goodflag_token

# 3. Recréer les secrets
echo "NOUVEAU_SECRET" | docker secret create signature_secret_key -
echo "NOUVEAU_RECAPTCHA" | docker secret create signature_recaptcha_key -
echo "NOUVEAU_GOODFLAG" | docker secret create signature_goodflag_token -

# 4. Redéployer
docker stack deploy -c docker-compose.yml signature
```

---

## 🛠️ Commandes utiles

### Gestion des secrets
```bash
# Lister
docker secret ls

# Inspecter (ne montre PAS le contenu)
docker secret inspect signature_secret_key

# Supprimer (impossible si utilisé par un service)
docker secret rm signature_secret_key
```

### Gestion de la stack
```bash
# Voir les services
docker service ls

# Voir les tâches (réplicas)
docker service ps signature_signature-app

# Logs
docker service logs -f signature_signature-app

# Mettre à jour l'image seulement
docker service update --image ghcr.io/taaazzz-prog/signatureelectronique:latest signature_signature-app

# Scaler (augmenter le nombre de réplicas)
docker service scale signature_signature-app=3

# Supprimer
docker stack rm signature
```

### Débug
```bash
# Entrer dans un conteneur
docker exec -it $(docker ps -q -f name=signature_signature-app) bash

# Vérifier les secrets montés
ls -la /run/secrets/

# Lire un secret (attention, sensible!)
cat /run/secrets/signature_secret_key
```

---

## ⚠️ Importantes notes

### 1. Ne JAMAIS commiter les secrets
```bash
# Le .gitignore contient déjà :
.env
*.key
secrets/
```

### 2. Backup des secrets
Les secrets Docker Swarm sont dans `/var/lib/docker/swarm/raft/`  
**Backup recommandé** :
```bash
# Sur le serveur
sudo tar -czf swarm-secrets-backup-$(date +%Y%m%d).tar.gz /var/lib/docker/swarm/raft/
```

### 3. GHCR Rate Limiting
GitHub Container Registry :
- Images **publiques** : Illimité
- Images **privées** : 5000 pulls/mois (compte gratuit)

### 4. Compatibilité dev local
Le code supporte **les deux modes** :
- **Production (Swarm)** : Lit depuis `/run/secrets/`
- **Dev local** : Lit depuis variables d'environnement

Donc votre `.env` local continue de fonctionner !

---

## 📚 Ressources

- Docker Secrets : https://docs.docker.com/engine/swarm/secrets/
- GitHub Container Registry : https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry
- Docker Swarm : https://docs.docker.com/engine/swarm/

---

## ✅ Checklist de migration

- [ ] Image buildée et poussée vers GHCR
- [ ] Image GHCR rendue publique (ou authentification configurée)
- [ ] Secrets créés sur le serveur Docker Swarm
- [ ] `docker-compose.yml` mis à jour avec `secrets:` et image GHCR
- [ ] Code mis à jour pour lire depuis `/run/secrets/`
- [ ] Déploiement testé avec `docker stack deploy`
- [ ] Vérification que les secrets sont montés (`ls /run/secrets/`)
- [ ] Application fonctionnelle (test HTTP + API)
- [ ] Ancien fichier `.env` sauvegardé localement mais jamais commité
- [ ] Documentation mise à jour

**C'est fait ! 🎉 Votre application utilise maintenant Docker Swarm + Secrets + GHCR !**
