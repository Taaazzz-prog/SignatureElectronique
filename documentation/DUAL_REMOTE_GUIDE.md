# 📚 Guide : Repository Dual-Remote

Ce guide explique comment utiliser le système dual-remote dans ce projet.

## 🎯 Concept

Ce projet utilise **un seul dossier** sur votre PC avec **deux remotes Git** :
- **public** : Repository public (code uniquement)
- **private** : Repository privé (code + configuration + documentation)

## 🔧 Configuration Git

Le projet est configuré avec deux remotes :

```bash
git remote -v
# public  https://github.com/Taaazzz-prog/SignatureElectronique.git
# private https://github.com/Taaazzz-prog/SignatureElectronique-private.git
```

## 📋 Fichiers .gitignore

### .gitignore-public (strict)
Utilisé pour pousser vers le repository public. Ignore :
- Tous les scripts PowerShell (*.ps1)
- docker-compose.yml et variantes
- Toute la documentation sauf README.md
- Dossiers d'infrastructure

### .gitignore-private (permissif)
Utilisé pour pousser vers le repository privé. Ignore seulement :
- Fichiers générés (__pycache__, *.pyc)
- Données utilisateur (uploads/, signed/, signatures/)
- Bases de données (*.db)
- Fichiers IDE (.vscode/, .idea/)

## 🚀 Scripts de Push

### push-public.ps1
Pousse uniquement le code vers le repository public.

**Utilisation :**
```powershell
.\push-public.ps1
```

**Ce qu'il fait :**
1. Sauvegarde le .gitignore actuel
2. Active .gitignore-public (filtre strict)
3. Montre les fichiers qui seront poussés
4. Commit et push vers remote `public`
5. Restaure le .gitignore original

**Ce qui sera poussé :** ✅
- Code Python (app.py, database.py)
- Templates HTML
- Fichiers statiques (CSS, JS)
- Dockerfile
- requirements.txt
- README.md (version publique)

**Ce qui sera filtré :** ❌
- Scripts PowerShell
- docker-compose.yml
- Documentation complète
- Fichiers de configuration sensibles

### push-private.ps1
Pousse tout (code + configuration) vers le repository privé.

**Utilisation :**
```powershell
.\push-private.ps1
```

**Ce qu'il fait :**
1. Sauvegarde le .gitignore actuel
2. Active .gitignore-private (filtre permissif)
3. Montre les fichiers qui seront poussés
4. Commit et push vers remote `private`
5. Restaure le .gitignore original

**Ce qui sera poussé :** ✅
- Tout le code
- Tous les scripts (*.ps1)
- docker-compose.yml
- Toute la documentation
- Fichiers .env (template)

**Ce qui sera filtré :** ❌
- Seulement les fichiers générés et données utilisateur

## 💻 Workflow Recommandé

### Développement Normal

1. Travaillez normalement dans votre dossier
2. Faites vos modifications de code
3. Testez localement

### Push du Code (Public)

Quand vous voulez partager le code publiquement :

```powershell
.\push-public.ps1
```

Le script vous demandera un message de commit.

**Exemple :**
```
Message de commit : Ajout de la fonctionnalité d'export PDF
```

### Push Complet (Privé)

Quand vous voulez sauvegarder tout (code + config) :

```powershell
.\push-private.ps1
```

Le script vous demandera un message de commit.

**Exemple :**
```
Message de commit : Mise à jour de la configuration de production
```

## 📝 Cas d'Usage

### Nouveau Développement de Fonctionnalité

1. Développez votre fonctionnalité
2. Testez localement
3. Push vers public : `.\push-public.ps1`
4. Push vers private : `.\push-private.ps1`

### Modification de Configuration

1. Modifiez docker-compose.yml ou scripts
2. Push uniquement vers private : `.\push-private.ps1`
3. Le public ne verra pas ces changements

### Mise à Jour de Documentation

**Documentation publique (README.md) :**
1. Modifiez README.md
2. Push vers public : `.\push-public.ps1`
3. Push vers private : `.\push-private.ps1`

**Documentation privée (autres .md) :**
1. Modifiez la documentation
2. Push uniquement vers private : `.\push-private.ps1`

## 🔍 Vérification

### Voir ce qui sera poussé vers public

```powershell
# Temporairement activer .gitignore-public
Copy-Item .gitignore-public .gitignore -Force
git status
# Restaurer
Copy-Item .gitignore-private .gitignore -Force
```

### Voir ce qui sera poussé vers private

```powershell
# Temporairement activer .gitignore-private
Copy-Item .gitignore-private .gitignore -Force
git status
# .gitignore-private est déjà actif par défaut
```

## 🛠️ Commandes Git Utiles

### Voir les remotes

```bash
git remote -v
```

### Voir l'historique du public

```bash
git log public/main
```

### Voir l'historique du private

```bash
git log private/main
```

### Pull depuis public

```bash
git pull public main
```

### Pull depuis private

```bash
git pull private main
```

## ⚠️ Important

1. **Ne jamais pusher manuellement** - Utilisez toujours les scripts pour éviter les erreurs
2. **Le .gitignore par défaut** est .gitignore-private (plus permissif)
3. **Toujours vérifier** les fichiers qui seront poussés (les scripts le montrent)
4. **Le private contient tout** - C'est votre backup complet
5. **Le public contient le code** - C'est ce que les autres voient

## 🔒 Sécurité

### Repository Public
- Pas de mots de passe
- Pas de clés secrètes
- Pas d'adresses IP/serveurs
- Pas de noms de domaine réels
- Seulement le code source

### Repository Privé
- Contient les vraies configurations
- Contient les scripts de déploiement
- Contient la documentation complète
- Peut contenir .env (template)

## 🆘 Résolution de Problèmes

### Les scripts ne fonctionnent pas

Vérifiez que vous êtes dans le bon dossier :
```powershell
cd "D:\WEB API\SignatureElectronique"
```

### Conflits Git

Si vous avez des conflits :
```bash
# Voir l'état
git status

# Résoudre manuellement les conflits
# Puis :
git add .
git commit -m "Résolution des conflits"
```

### Mauvais fichiers poussés vers public

1. Vérifiez .gitignore-public
2. Ajoutez les patterns nécessaires
3. Re-push avec le script

### .gitignore corrompu

Si le .gitignore est dans un mauvais état :
```powershell
# Restaurer depuis .gitignore-private (par défaut)
Copy-Item .gitignore-private .gitignore -Force
```

## ✨ Avec ce Système

- Un seul dossier sur votre PC
- Deux repositories GitHub
- Contrôle total de ce qui va où
- Sécurité garantie (filtrage automatique)
- Workflow simple et sûr
