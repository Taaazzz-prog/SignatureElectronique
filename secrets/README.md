# 🔐 Gestion des Secrets Docker

## 📋 Vue d'ensemble

Les secrets de l'application sont gérés via **Docker Secrets** qui :
- ✅ Chiffre les données avec AES-256
- ✅ Stocke dans le Raft store de Swarm
- ✅ Monte les secrets en lecture seule dans `/run/secrets/`
- ✅ Supporte la rotation

---

## 🔑 Secrets utilisés

| Nom du secret | Variable d'env | Description |
|---------------|----------------|-------------|
| `signature_secret_key` | `SECRET_KEY` | Clé secrète Flask pour sessions |
| `signature_recaptcha_key` | `RECAPTCHA_SECRET_KEY` | Clé secrète Google reCAPTCHA v3 |
| `signature_goodflag_token` | `GOODFLAG_API_TOKEN` | Token API Goodflag (optionnel) |

---

## 🚀 Création des secrets

### Automatique (Recommandé)

```powershell
# Utiliser le script de création
.\create-secrets.ps1
```

Ce script :
1. Lit les valeurs depuis le fichier `.env` parent
2. Valide que les secrets obligatoires sont présents
3. Crée les secrets sur le serveur via SSH

### Manuelle

```bash
# Se connecter au serveur
ssh taaazzz@51.75.55.185

# Créer les secrets
echo "VOTRE_SECRET_KEY" | docker secret create signature_secret_key -
echo "VOTRE_RECAPTCHA_KEY" | docker secret create signature_recaptcha_key -
echo "VOTRE_GOODFLAG_TOKEN" | docker secret create signature_goodflag_token -
```

---

## 🔄 Rotation des secrets

### Pourquoi faire une rotation ?

- 🔐 Conformité sécurité (tous les 90 jours recommandés)
- ⚠️ Compromission suspectée
- 🔄 Changement d'environnement

### Procédure de rotation

⚠️ **ATTENTION** : La rotation nécessite un redémarrage du service.

```bash
# 1. Se connecter au serveur
ssh taaazzz@51.75.55.185

# 2. Arrêter la stack
docker stack rm signature

# 3. Attendre que tous les conteneurs soient arrêtés
docker ps | grep signature

# 4. Supprimer les anciens secrets
docker secret rm signature_secret_key
docker secret rm signature_recaptcha_key
docker secret rm signature_goodflag_token

# 5. Créer les nouveaux secrets
# (utiliser create-secrets.ps1 depuis votre machine locale)

# 6. Redéployer
# (utiliser deploy-swarm-prod.ps1 depuis votre machine locale)
```

---

## ✅ Vérification

### Lister les secrets

```bash
docker secret ls
```

### Inspecter un secret (sans voir le contenu)

```bash
docker secret inspect signature_secret_key
```

### Vérifier qu'un secret est monté dans le conteneur

```bash
# Trouver le conteneur
CONTAINER_ID=$(docker ps -q --filter label=com.docker.swarm.service.name=signature_signature-app)

# Vérifier le montage
docker exec $CONTAINER_ID ls -la /run/secrets/
```

Devrait afficher :
```
-r--r--r-- 1 root root 48 signature_secret_key
-r--r--r-- 1 root root 41 signature_recaptcha_key
-r--r--r-- 1 root root  1 signature_goodflag_token
```

---

## 🔧 Dépannage

### Secret "already exists"

```bash
# Supprimer le secret existant
docker secret rm signature_secret_key

# Recréer
echo "NOUVELLE_VALEUR" | docker secret create signature_secret_key -
```

### Secret non accessible dans le conteneur

1. **Vérifier que le secret existe**
   ```bash
   docker secret ls | grep signature
   ```

2. **Vérifier la configuration du service**
   ```bash
   docker service inspect signature_signature-app | grep -A 10 Secrets
   ```

3. **Redémarrer le service**
   ```bash
   docker service update --force signature_signature-app
   ```

---

## ⚠️ Bonnes pratiques

### ✅ À FAIRE

- ✅ Stocker les valeurs dans le `.env` du repository privé
- ✅ Faire des backups réguliers du `.env`
- ✅ Utiliser des secrets forts (32+ caractères aléatoires)
- ✅ Rotation régulière (tous les 90 jours)
- ✅ Documenter les changements de secrets

### ❌ À NE PAS FAIRE

- ❌ Commit le `.env` dans un repository public
- ❌ Partager les secrets par email/chat
- ❌ Utiliser les mêmes secrets en dev et prod
- ❌ Laisser les secrets par défaut
- ❌ Stocker les secrets en clair dans la base de données

---

## 📊 Génération de secrets sécurisés

### SECRET_KEY (Flask)

```python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Mot de passe aléatoire

```python
python -c "import secrets; import string; chars = string.ascii_letters + string.digits + '!@#$%^&*'; print(''.join(secrets.choice(chars) for _ in range(32)))"
```

### Token hexadécimal

```python
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 🔗 Ressources

- [Docker Secrets Documentation](https://docs.docker.com/engine/swarm/secrets/)
- [Flask Secret Key Best Practices](https://flask.palletsprojects.com/en/2.3.x/config/#SECRET_KEY)
- [OWASP Secret Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)

---

**Dernière mise à jour** : 13 décembre 2025
