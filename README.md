# 🔒 SignatureElectronique - Configuration Privée

⚠️ **REPOSITORY PRIVÉ** - Ne jamais rendre public

## 📦 À propos

Ce repository contient la **configuration de production** et les **secrets** pour l'application SignatureElectronique.

**Code source public** : https://github.com/Taaazzz-prog/SignatureElectronique

---

## 📁 Structure

```
SignatureElectronique-private/
├── .env                           # Secrets de production (SECRET_KEY, RECAPTCHA, GOODFLAG)
├── docker-compose.prod.yml        # Configuration Swarm avec VRAI domaine
├── deploy-swarm-prod.ps1          # Script de déploiement avec VRAIE adresse SSH
├── build-and-push-prod.ps1        # Build et push avec config réelle
│
├── infrastructure/
│   ├── server-setup.md            # Configuration serveur OVH (IP, SSH, domaine)
│   └── traefik-config.md          # Configuration Traefik détaillée
│
├── secrets/
│   ├── create-secrets.ps1         # Création des Docker Secrets
│   ├── rotate-secrets.ps1         # Rotation des secrets
│   └── README.md                  # Documentation gestion des secrets
│
├── monitoring/
│   ├── monitor-prod.ps1           # Monitoring avec vraies adresses
│   └── alerting.md                # Configuration des alertes
│
├── backups/
│   ├── backup-db.ps1              # Scripts de backup
│   └── restore-db.ps1             # Scripts de restauration
│
└── docs/
    ├── DEPLOYMENT_PROD.md         # Procédures de déploiement
    ├── TROUBLESHOOTING.md         # Résolution de problèmes
    └── RUNBOOK.md                 # Documentation opérationnelle
```

---

## 🚀 Utilisation

### Déploiement initial

```powershell
# 1. Créer les secrets Docker sur le serveur
.\secrets\create-secrets.ps1

# 2. Déployer la stack
.\deploy-swarm-prod.ps1
```

### Mise à jour

```powershell
# Le code est automatiquement buildé par GitHub Actions
# Il suffit de mettre à jour le service
.\deploy-swarm-prod.ps1 -SkipPull
```

### Monitoring

```powershell
# Surveiller les logs et services
.\monitoring\monitor-prod.ps1
```

---

## 🔐 Sécurité

- ✅ Repository **PRIVÉ** sur GitHub
- ✅ Secrets chiffrés avec Docker Secrets
- ✅ Accès SSH sécurisé (mot de passe fort)
- ✅ HTTPS avec Let's Encrypt

⚠️ **Ne jamais commit** :
- Fichiers de backup de base de données (*.db, *.sql)
- Logs avec données sensibles
- Clés SSL/TLS locales

---

## 📞 Contact

- **Serveur** : OVH Dédié
- **Domaine** : signatureelectronique.taaazzz-prog.fr
- **IP** : 51.75.55.185

---

**Dernière mise à jour** : 13 décembre 2025
