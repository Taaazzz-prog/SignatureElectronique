# 📚 Guide : Repository Dual-Remote

## 🎯 Architecture

Ce dossier utilise **un seul repository Git** avec **deux remotes** :

- **`public`** → https://github.com/Taaazzz-prog/SignatureElectronique
- **`private`** → https://github.com/Taaazzz-prog/SignatureElectronique-private

```
SignatureElectronique/
├── .git/
│   └── remotes: public + private
├── .gitignore-public          ← Ignore fichiers sensibles
├── .gitignore-private         ← Ignore presque rien
├── push-public.ps1            ← Script pour push public
├── push-private.ps1           ← Script pour push privé
├── app.py                     ← CODE (dans les 2 repos)
├── docker-compose.yml         ← CONFIG (privé uniquement)
└── ...
```

---

## 🚀 Utilisation

### Push vers le PUBLIC (code uniquement)

```powershell
.\push-public.ps1 -Message "Ajout nouvelle fonctionnalité"
```

**Ce qui sera pushé** :
- ✅ Code source (*.py)
- ✅ Templates et static
- ✅ Dockerfile, requirements.txt
- ✅ README.md
- ❌ Scripts PowerShell
- ❌ docker-compose.yml
- ❌ Documentation opérationnelle

### Push vers le PRIVÉ (code + config)

```powershell
.\push-private.ps1 -Message "Mise à jour configuration serveur"
```

**Ce qui sera pushé** :
- ✅ Tout le code
- ✅ Tous les scripts PowerShell
- ✅ docker-compose.yml
- ✅ Toute la documentation
- ✅ Configuration infrastructure

---

## 📝 Workflow recommandé

### Développement de code

```powershell
# 1. Modifier le code
notepad app.py

# 2. Tester localement
python app.py

# 3. Push vers les DEUX repos
.\push-public.ps1 -Message "Nouvelle feature"
.\push-private.ps1 -Message "Nouvelle feature"
```

### Modification de configuration

```powershell
# 1. Modifier la config
notepad docker-compose.yml

# 2. Push UNIQUEMENT vers privé
.\push-private.ps1 -Message "Update docker-compose"
```

---

## 🔍 Vérifier avant push

### Voir ce qui sera pushé vers PUBLIC

```powershell
# Activer temporairement le .gitignore public
Copy-Item .gitignore-public .gitignore -Force
git status
# Restaurer
Copy-Item .gitignore-private .gitignore -Force
```

### Voir ce qui sera pushé vers PRIVÉ

```powershell
git status
```

---

## 🛠️ Commandes Git utiles

### Lister les remotes

```powershell
git remote -v
```

### Pull depuis public ou privé

```powershell
git pull public main
# ou
git pull private main
```

### Push manuel

```powershell
# Vers public (attention au .gitignore !)
git push public main

# Vers privé
git push private main
```

---

## ⚠️ IMPORTANT

### .gitignore actif

Par défaut, le `.gitignore-private` est actif (copié vers `.gitignore`).

**Avant un push vers PUBLIC**, le script `push-public.ps1` :
1. Sauvegarde `.gitignore`
2. Active `.gitignore-public` (ignore les fichiers sensibles)
3. Fait le push
4. Restaure `.gitignore`

### Fichiers sensibles

Ces fichiers sont **TOUJOURS ignorés** (même en privé) :
- `.env` (secrets locaux)
- `uploads/`, `signed/`, `signatures/` (données utilisateurs)
- `*.db` (base de données)
- `.venv/` (environnement virtuel)

---

## 📊 Résumé

| Action | Commande | Destination |
|--------|----------|-------------|
| Push code | `.\push-public.ps1` | Repository PUBLIC |
| Push config | `.\push-private.ps1` | Repository PRIVÉ |
| Push tout | Exécuter les 2 scripts | Les 2 repositories |

---

## 🆘 Dépannage

### Conflit de .gitignore

Si vous avez des conflits, réinitialisez :

```powershell
Copy-Item .gitignore-private .gitignore -Force
```

### Vérifier les remotes

```powershell
git remote -v
```

Si un remote manque :

```powershell
# Ajouter public
git remote add public https://github.com/Taaazzz-prog/SignatureElectronique.git

# Ajouter private
git remote add private https://github.com/Taaazzz-prog/SignatureElectronique-private.git
```

---

**✨ Avec ce système, vous avez un seul dossier et vous contrôlez ce qui va dans chaque repository !**
