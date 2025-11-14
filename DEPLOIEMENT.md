# 🚀 Déploiement Signature Électronique sur OVH

## ✅ Déploiement réussi !

L'application de signature électronique est maintenant déployée et accessible sur :

### 🌐 URL de production
**https://signatureelectronique.taaazzz-prog.fr**

---

## 📋 Configuration du serveur

### Emplacement
- **Serveur** : OVH (51.75.55.185)
- **Dossier** : `/home/taaazzz/SignatureElectronique`
- **Utilisateur** : `taaazzz`

### Architecture Docker
- **Conteneur** : `signature_electronique_app`
- **Image** : `signatureelectronique-signature-app`
- **Réseau** : `faildaily_faildaily-ssl-network` (partagé avec Traefik)
- **Port interne** : 5000
- **Workers** : 4 Gunicorn workers

### Reverse Proxy (Traefik)
- **Conteneur Traefik** : `faildaily-traefik-ssl`
- **Domaine** : `signatureelectronique.taaazzz-prog.fr`
- **SSL** : Let's Encrypt (automatique)
- **Redirection HTTP → HTTPS** : Activée

---

## 🔧 Commandes de gestion

### Se connecter au serveur
```powershell
ssh taaazzz@51.75.55.185
```

### Accéder au dossier
```bash
cd /home/taaazzz/SignatureElectronique
```

### Voir les logs en temps réel
```bash
docker logs -f signature_electronique_app
```

### Redémarrer l'application
```bash
docker-compose restart
```

### Arrêter l'application
```bash
docker-compose down
```

### Démarrer l'application
```bash
docker-compose up -d
```

### Reconstruire après modification
```bash
docker-compose down
docker-compose build
docker-compose up -d
```

### Voir le statut du conteneur
```bash
docker ps | grep signature
```

---

## 📦 Volumes Docker

Les données persistantes sont stockées dans des volumes Docker :

- `signatureelectronique_signature_uploads` : Fichiers PDF uploadés
- `signatureelectronique_signature_signed` : PDFs signés
- `signatureelectronique_signature_signatures` : Signatures temporaires

### Sauvegarder les données
```bash
docker run --rm -v signatureelectronique_signature_uploads:/data -v $(pwd):/backup alpine tar czf /backup/uploads_backup.tar.gz /data
docker run --rm -v signatureelectronique_signature_signed:/data -v $(pwd):/backup alpine tar czf /backup/signed_backup.tar.gz /data
```

---

## 🔄 Mise à jour de l'application

### Depuis Windows (local)

1. **Modifier le code localement**
2. **Transférer les fichiers**
   ```powershell
   scp -r "d:\WEB API\SignatureElectronique\*" taaazzz@51.75.55.185:/home/taaazzz/SignatureElectronique/
   ```
3. **Redéployer**
   ```powershell
   ssh taaazzz@51.75.55.185 "cd /home/taaazzz/SignatureElectronique && docker-compose down && docker-compose build && docker-compose up -d"
   ```

### Depuis le serveur

1. **Se connecter**
   ```bash
   ssh taaazzz@51.75.55.185
   cd /home/taaazzz/SignatureElectronique
   ```

2. **Modifier les fichiers** (avec nano, vim, etc.)

3. **Redéployer**
   ```bash
   docker-compose down
   docker-compose build
   docker-compose up -d
   ```

---

## 🔒 Sécurité

### Headers de sécurité configurés
- ✅ X-Frame-Deny (protection contre clickjacking)
- ✅ X-Content-Type-Options: nosniff
- ✅ X-XSS-Protection
- ✅ Referrer-Policy: same-origin
- ✅ HSTS (HTTP Strict Transport Security)
- ✅ Force HTTPS

### Limites
- Taille maximale des fichiers : 20 MB (configurable dans docker-compose.yml)
- Utilisateur non-root dans le conteneur (appuser:1000)

---

## 📊 Monitoring

### Vérifier la santé de l'application
```bash
# Statut du conteneur
docker ps | grep signature

# Logs récents
docker logs --tail 100 signature_electronique_app

# Utilisation des ressources
docker stats signature_electronique_app

# Vérifier le réseau Traefik
docker network inspect faildaily_faildaily-ssl-network | grep signature -A 5
```

### Test de connectivité
```bash
# Depuis le serveur
curl http://172.18.0.21:5000

# Via le domaine
curl -I https://signatureelectronique.taaazzz-prog.fr
```

---

## 🐛 Dépannage

### L'application ne démarre pas
```bash
# Voir les logs d'erreur
docker logs signature_electronique_app

# Vérifier le réseau
docker network ls | grep faildaily
```

### Certificat SSL non généré
- Attendre quelques minutes (Let's Encrypt peut prendre du temps)
- Vérifier les logs Traefik : `docker logs faildaily-traefik-ssl`

### Erreur 502 Bad Gateway
```bash
# Redémarrer le conteneur
docker-compose restart

# Si le problème persiste, reconstruire
docker-compose down
docker-compose build
docker-compose up -d
```

### Accès refusé
- Vérifier que le réseau Traefik existe : `docker network ls`
- Vérifier que Traefik tourne : `docker ps | grep traefik`

---

## 📝 Configuration Traefik

Les labels Traefik configurés dans `docker-compose.yml` :

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.signature.rule=Host(`signatureelectronique.taaazzz-prog.fr`)"
  - "traefik.http.routers.signature.tls=true"
  - "traefik.http.routers.signature.tls.certresolver=letsencrypt"
  - "traefik.http.services.signature.loadbalancer.server.port=5000"
```

---

## 🎯 Prochaines étapes possibles

- [ ] Configurer des sauvegardes automatiques
- [ ] Ajouter un système de monitoring (Prometheus/Grafana)
- [ ] Implémenter un nettoyage automatique des anciens fichiers
- [ ] Ajouter une authentification utilisateur
- [ ] Configurer des alertes en cas de problème

---

## 📞 Support

Pour toute question ou problème :
1. Consulter les logs : `docker logs signature_electronique_app`
2. Vérifier le statut : `docker ps`
3. Tester l'accès : `curl https://signatureelectronique.taaazzz-prog.fr`

---

**✅ Déploiement effectué le : 14 novembre 2025**
**🌐 URL : https://signatureelectronique.taaazzz-prog.fr**
