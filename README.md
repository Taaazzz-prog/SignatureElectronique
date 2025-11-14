# 📝 Signature Électronique PDF

Application web simple et efficace pour signer des fichiers PDF électroniquement.

## 🚀 Fonctionnalités

- ✅ Upload de fichiers PDF (drag & drop ou sélection)
- ✍️ Création de signature à la souris ou au tactile
- 📍 Positionnement personnalisable de la signature
- 📄 Support multi-pages
- 💾 Téléchargement automatique du PDF signé
- 🎨 Interface moderne et intuitive

## 📋 Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

## 🔧 Installation

1. **Cloner ou naviguer vers le projet**
```powershell
cd "d:\WEB API\SignatureElectronique"
```

2. **Créer un environnement virtuel (recommandé)**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. **Installer les dépendances**
```powershell
pip install -r requirements.txt
```

## ▶️ Lancement

1. **Démarrer le serveur**
```powershell
python app.py
```

2. **Ouvrir votre navigateur**
```
http://localhost:5000
```

## 📖 Utilisation

1. **Charger un PDF**
   - Glissez-déposez votre fichier PDF dans la zone prévue
   - Ou cliquez sur "Choisir un fichier PDF"

2. **Créer votre signature**
   - Dessinez votre signature sur le canvas blanc
   - Utilisez "Effacer" pour recommencer
   - Utilisez "Annuler" pour supprimer le dernier trait

3. **Configurer la position**
   - Sélectionnez la page à signer
   - Ajustez les positions X et Y
   - Modifiez la largeur si nécessaire

4. **Signer**
   - Cliquez sur "Signer le PDF"
   - Le fichier signé se téléchargera automatiquement

## 📁 Structure du projet

```
SignatureElectronique/
├── app.py                 # Serveur Flask (API backend)
├── templates/
│   └── index.html        # Interface utilisateur
├── uploads/              # PDFs uploadés (créé automatiquement)
├── signed/               # PDFs signés (créé automatiquement)
├── signatures/           # Signatures temporaires (créé automatiquement)
├── requirements.txt      # Dépendances Python
└── README.md            # Documentation
```

## 🛠️ Configuration

### Limites de fichiers
Par défaut, la taille maximale des fichiers est de 16 MB. Pour modifier :
```python
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB
```

### Port du serveur
Pour changer le port (par défaut 5000) :
```python
app.run(debug=True, host='0.0.0.0', port=8080)
```

## 🔒 Sécurité

- Les fichiers sont stockés avec des noms UUID uniques
- Validation des types de fichiers (PDF uniquement)
- Limite de taille de fichier configurée
- Nettoyage automatique des fichiers temporaires

## 🐛 Dépannage

### Erreur "Module not found"
```powershell
pip install -r requirements.txt
```

### Port déjà utilisé
Modifiez le port dans `app.py` ou arrêtez l'application utilisant le port 5000

### Problèmes de permissions
Exécutez PowerShell en tant qu'administrateur

## 📝 Notes

- Les fichiers uploadés et signés sont stockés localement
- Pour la production, ajoutez un système de nettoyage automatique des anciens fichiers
- Considérez l'ajout d'une authentification pour un usage professionnel
- Les signatures sont en format PNG transparent

## 🎯 Améliorations futures possibles

- [ ] Authentification utilisateur
- [ ] Base de données pour historique
- [ ] Prévisualisation PDF intégrée
- [ ] Signatures prédéfinies
- [ ] Support de multiples signatures par document
- [ ] Export en différents formats
- [ ] Horodatage des signatures
- [ ] Certificats numériques

## 📄 Licence

Projet libre d'utilisation pour usage personnel et professionnel.

## 👤 Support

Pour toute question ou problème, créez une issue dans le projet.
