# 🚀 Procédures de Déploiement - PRODUCTION

## 🎯 Vue d'ensemble

Ce document décrit les procédures de déploiement pour l'application SignatureElectronique en production.

---

## 📋 Prérequis

### Sur votre machine locale
- ✅ Git installé
- ✅ PowerShell 5.1+ ou PowerShell Core
- ✅ Accès SSH au serveur : `taaazzz@51.75.55.185`
- ✅ Repositories clonés :
  - Public : `https://github.com/Taaazzz-prog/SignatureElectronique.git`
  - Privé : `https://github.com/Taaazzz-prog/SignatureElectronique-private.git`

### Sur le serveur
- ✅ Docker Swarm initialisé
- ✅ Traefik déployé et configuré
- ✅ Réseau `traefik-public` créé
- ✅ Docker Secrets créés

---

## 🔧 Déploiement Initial (première fois)

### Étape 1️⃣ : Préparer le serveur

```bash
# Se connecter au serveur
ssh taaazzz@51.75.55.185

# Créer le dossier de l'application
mkdir -p /home/taaazzz/SignatureElectronique
cd /home/taaazzz/SignatureElectronique

# Vérifier que Docker Swarm est actif
docker info | grep Swarm
# Devrait afficher: Swarm: active

# Vérifier que le réseau traefik-public existe
docker network ls | grep traefik-public

# Si le réseau n'existe pas, le créer
docker network create --driver overlay traefik-public
```

### Étape 2️⃣ : Créer les Docker Secrets

```powershell
# Sur votre machine locale
cd D:\WEB API\SignatureElectronique-private

# Éditer .env avec vos vraies valeurs
notepad .env

# Créer les secrets sur le serveur
.\secrets\create-secrets.ps1
```

**Vérification** :
```bash
# Sur le serveur
ssh taaazzz@51.75.55.185 "docker secret ls"
```

Devrait afficher :
- `signature_secret_key`
- `signature_recaptcha_key`
- `signature_goodflag_token`

### Étape 3️⃣ : Déployer la stack

```powershell
# Sur votre machine locale
cd D:\WEB API\SignatureElectronique-private

# Déployer
.\deploy-swarm-prod.ps1
```

### Étape 4️⃣ : Vérifier le déploiement

```bash
# Vérifier que le service est démarré
ssh taaazzz@51.75.55.185 "docker service ps signature_signature-app"

# Vérifier les logs
ssh taaazzz@51.75.55.185 "docker service logs signature_signature-app --tail 50"

# Tester l'accès HTTPS
curl -I https://signatureelectronique.taaazzz-prog.fr
```

---

## 🔄 Mise à jour de l'application

### Workflow standard

Le code est automatiquement buildé par GitHub Actions :

1. **Push du code** dans le repository public
   ```bash
   cd D:\WEB API\SignatureElectronique
   git add .
   git commit -m "Description des changements"
   git push origin main
   ```

2. **GitHub Actions** build automatiquement l'image
   - Voir : https://github.com/Taaazzz-prog/SignatureElectronique/actions

3. **Déployer la nouvelle image**
   ```powershell
   cd D:\WEB API\SignatureElectronique-private
   .\deploy-swarm-prod.ps1
   ```

### Mise à jour manuelle (sans rebuild)

Si vous voulez juste redémarrer le service :

```bash
ssh taaazzz@51.75.55.185 "docker service update --force signature_signature-app"
```

---

## 🔐 Gestion des Secrets

### Créer/Recréer les secrets

```powershell
# Sur votre machine locale
cd D:\WEB API\SignatureElectronique-private
.\secrets\create-secrets.ps1
```

### Rotation des secrets

⚠️ **ATTENTION** : La rotation nécessite de recréer les secrets et redémarrer le service.

```bash
# 1. Supprimer les anciens secrets
ssh taaazzz@51.75.55.185 "docker secret rm signature_secret_key signature_recaptcha_key signature_goodflag_token"

# 2. Créer les nouveaux secrets
cd D:\WEB API\SignatureElectronique-private
.\secrets\create-secrets.ps1

# 3. Redéployer
.\deploy-swarm-prod.ps1 -SkipPull
```

---

## 📊 Monitoring et Logs

### Logs en temps réel
```bash
ssh taaazzz@51.75.55.185 "docker service logs -f signature_signature-app"
```

### Logs des 100 dernières lignes
```bash
ssh taaazzz@51.75.55.185 "docker service logs signature_signature-app --tail 100"
```

### Filtrer les erreurs
```bash
ssh taaazzz@51.75.55.185 "docker service logs signature_signature-app | grep -i error"
```

### État du service
```bash
ssh taaazzz@51.75.55.185 "docker service ps signature_signature-app --no-trunc"
```

---

## 🆘 Rollback (retour arrière)

### Revenir à la version précédente

```bash
# 1. Trouver l'ID de l'image précédente
ssh taaazzz@51.75.55.185 "docker images | grep signatureelectronique"

# 2. Mettre à jour avec l'ancienne image
ssh taaazzz@51.75.55.185 "docker service update --image ghcr.io/taaazzz-prog/signatureelectronique:SHA_PRECEDENT signature_signature-app"
```

### Revenir à la dernière version stable

```bash
ssh taaazzz@51.75.55.185 "docker service update --image ghcr.io/taaazzz-prog/signatureelectronique:latest signature_signature-app"
```

---

## 🔧 Dépannage

### Le service ne démarre pas

1. **Vérifier les logs**
   ```bash
   ssh taaazzz@51.75.55.185 "docker service logs signature_signature-app --tail 50"
   ```

2. **Vérifier les secrets**
   ```bash
   ssh taaazzz@51.75.55.185 "docker secret ls"
   ```

3. **Vérifier que l'image existe**
   ```bash
   ssh taaazzz@51.75.55.185 "docker images | grep signatureelectronique"
   ```

### Certificat SSL ne fonctionne pas

1. **Vérifier les logs Traefik**
   ```bash
   ssh taaazzz@51.75.55.185 "docker logs faildaily-traefik-ssl --tail 100 | grep -i 'error\|certificate'"
   ```

2. **Vérifier la configuration du domaine**
   ```bash
   nslookup signatureelectronique.taaazzz-prog.fr
   ```

### L'application ne répond pas

1. **Vérifier que le service tourne**
   ```bash
   ssh taaazzz@51.75.55.185 "docker service ps signature_signature-app"
   ```

2. **Tester depuis le serveur**
   ```bash
   ssh taaazzz@51.75.55.185 "curl -I http://localhost:5000"
   ```

3. **Vérifier le réseau Traefik**
   ```bash
   ssh taaazzz@51.75.55.185 "docker network inspect traefik-public"
   ```

---

## 📦 Backup et Restauration

### Backup de la base de données

```bash
# Se connecter au serveur
ssh taaazzz@51.75.55.185

# Trouver le volume de la base de données
docker volume inspect signature_signature_database

# Copier la base de données
docker run --rm -v signature_signature_database:/data -v /tmp:/backup alpine \
  tar czf /backup/signature-db-$(date +%Y%m%d-%H%M%S).tar.gz /data

# Télécharger le backup
scp taaazzz@51.75.55.185:/tmp/signature-db-*.tar.gz ./backups/
```

### Restauration

```bash
# Uploader le backup
scp ./backups/signature-db-20231213.tar.gz taaazzz@51.75.55.185:/tmp/

# Restaurer
ssh taaazzz@51.75.55.185 "docker run --rm -v signature_signature_database:/data -v /tmp:/backup alpine \
  tar xzf /backup/signature-db-20231213.tar.gz -C /"
```

---

## 🔄 Checklist de déploiement

- [ ] Code testé localement
- [ ] Commit et push sur GitHub
- [ ] GitHub Actions build réussi
- [ ] `.env` du repo privé à jour
- [ ] Backup de la base de données effectué
- [ ] Déploiement avec `deploy-swarm-prod.ps1`
- [ ] Vérification des logs
- [ ] Test de l'application en production
- [ ] Monitoring actif

---

## 📞 Support

En cas de problème critique :
1. Vérifier les logs
2. Consulter la documentation `infrastructure/server-setup.md`
3. Rollback si nécessaire

---

**Dernière mise à jour** : 13 décembre 2025
