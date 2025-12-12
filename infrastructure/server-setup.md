# 🖥️ Configuration Serveur OVH - PRODUCTION

## 📋 Informations générales

- **Fournisseur** : OVH
- **Type** : Serveur dédié
- **IP Publique** : `51.75.55.185`
- **Domaine** : `signatureelectronique.taaazzz-prog.fr`
- **OS** : Ubuntu 22.04 LTS
- **Node Swarm** : Taaazzz-Dedie

---

## 🔐 Accès SSH

### Connexion
```bash
ssh taaazzz@51.75.55.185
```

### Configuration SSH locale
Ajouter dans `~/.ssh/config` :

```
Host signatureelectronique
    HostName 51.75.55.185
    User taaazzz
    Port 22
    IdentityFile ~/.ssh/id_rsa
```

Puis connexion simplifiée :
```bash
ssh signatureelectronique
```

---

## 🐳 Docker Swarm

### État du Swarm
```bash
docker info | grep Swarm
# Swarm: active
```

### Nœuds
```bash
docker node ls
# ID: Taaazzz-Dedie (Manager)
```

### Réseaux
```bash
docker network ls
# traefik-public (overlay)
```

---

## 🌐 Traefik

### Service Traefik
```bash
docker ps | grep traefik
# faildaily-traefik-ssl
```

### Configuration
- **Réseau** : `traefik-public`
- **Let's Encrypt** : Actif
- **Certificats** : Auto-renouvellement
- **Ports** :
  - 80 (HTTP → redirect HTTPS)
  - 443 (HTTPS)

### Logs Traefik
```bash
docker logs faildaily-traefik-ssl --tail 100
```

---

## 🔥 Firewall / Ports

### Ports ouverts
- **22** : SSH
- **80** : HTTP (Traefik)
- **443** : HTTPS (Traefik)
- **2377** : Docker Swarm management (interne)

### Vérification
```bash
sudo ufw status
```

---

## 📁 Structure des dossiers

### Application
```bash
/home/taaazzz/SignatureElectronique/
├── docker-compose.yml         # Configuration de la stack
└── (autres fichiers temporaires)
```

### Volumes Docker
```bash
docker volume ls | grep signature
# signature_signature_uploads
# signature_signature_signed
# signature_signature_signatures
# signature_signature_database
```

---

## 🔍 Commandes utiles

### Vérifier l'application
```bash
# État de la stack
docker stack ls

# Services
docker service ls

# Logs
docker service logs signature_signature-app --tail 100

# Tâches
docker service ps signature_signature-app
```

### Vérifier les secrets
```bash
# Lister
docker secret ls

# Inspecter (sans voir le contenu)
docker secret inspect signature_secret_key
```

### Vérifier les volumes
```bash
# Lister
docker volume ls | grep signature

# Inspecter
docker volume inspect signature_signature_database
```

### Accès au conteneur
```bash
# Trouver le conteneur
docker ps | grep signature

# Shell dans le conteneur
docker exec -it <container_id> /bin/bash
```

---

## 🔄 Procédures de maintenance

### Redémarrer le service
```bash
docker service update --force signature_signature-app
```

### Mettre à jour l'image
```bash
# Pull de la nouvelle image
docker pull ghcr.io/taaazzz-prog/signatureelectronique:latest

# Mettre à jour le service
docker service update --image ghcr.io/taaazzz-prog/signatureelectronique:latest signature_signature-app
```

### Nettoyer le système
```bash
# Supprimer les images inutilisées
docker image prune -a

# Supprimer les conteneurs arrêtés
docker container prune

# Nettoyer les volumes non utilisés (ATTENTION: backup avant!)
docker volume prune
```

---

## 🆘 Dépannage

### Service ne démarre pas
```bash
# Vérifier les logs
docker service logs signature_signature-app --tail 100

# Vérifier les tâches échouées
docker service ps signature_signature-app --no-trunc

# Vérifier les secrets
docker secret ls
```

### Problème de certificat SSL
```bash
# Vérifier les logs Traefik
docker logs faildaily-traefik-ssl | grep -i "error\|certificate"

# Forcer le renouvellement
# (voir documentation Traefik)
```

### Problème de réseau
```bash
# Vérifier le réseau overlay
docker network inspect traefik-public

# Vérifier la connectivité
curl -I https://signatureelectronique.taaazzz-prog.fr
```

---

## 📊 Monitoring

### Ressources système
```bash
# CPU/Mémoire
htop

# Espace disque
df -h

# Docker stats
docker stats
```

### Application
```bash
# Santé du service
docker service ps signature_signature-app

# Logs en temps réel
docker service logs -f signature_signature-app
```

---

## 🔐 Sécurité

### Mises à jour système
```bash
sudo apt update && sudo apt upgrade -y
```

### Audit des secrets
```bash
# Vérifier que les secrets existent
docker secret ls | grep signature

# Les secrets ne doivent JAMAIS être visibles en clair
```

### Backup des secrets
⚠️ Les secrets Docker ne peuvent pas être exportés une fois créés.  
**Conservez les valeurs dans le .env du repository privé !**

---

## 📞 Informations de contact

- **Admin** : Taaazzz
- **Email** : contact@taaazzz-prog.fr
- **GitHub** : Taaazzz-prog

---

**Dernière mise à jour** : 13 décembre 2025
