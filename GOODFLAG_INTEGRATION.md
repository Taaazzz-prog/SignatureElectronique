# 🚀 Guide d'intégration Goodflag

## ✅ Ce qui a été fait

### 1. Modules créés
- **goodflag_api.py** : Client API Goodflag pour signature qualifiée
- **Routes API ajoutées dans app.py** :
  - `/api/sign-goodflag` : Signer avec Goodflag
  - `/api/goodflag/status` : Vérifier la configuration

### 2. Double système disponible
Votre application propose maintenant **2 modes de signature** :

#### Mode 1 : Signature Standard (pyHanko)
- Route : `/api/sign` 
- Certificat auto-signé gratuit
- Pour usage personnel
- ❌ Non accepté par l'INPI

#### Mode 2 : Signature Qualifiée (Goodflag)
- Route : `/api/sign-goodflag`
- Certificat eIDAS qualifié
- ✅ Accepté par l'INPI
- 💰 Requiert un abonnement Goodflag

## 📝 Configuration requise

### 1. Obtenir un compte Goodflag
1. Aller sur https://goodflag.com/tarifs-signature-electronique
2. S'inscrire pour un essai gratuit ou un abonnement
3. Récupérer votre **token API** depuis le portail

### 2. Configurer les variables d'environnement
Ajoutez ces lignes dans votre fichier `.env` ou dans les variables d'environnement du serveur :

```bash
GOODFLAG_API_TOKEN=votre_token_ici
GOODFLAG_API_URL=https://api.goodflag.com/v1
```

### 3. Sur le serveur OVH
```bash
# Se connecter au serveur
ssh user@votre-serveur

# Éditer le fichier docker-compose.yml
cd /home/VOTRE_USER/SignatureElectronique
nano docker-compose.yml

# Ajouter dans la section environment:
environment:
  - GOODFLAG_API_TOKEN=votre_token_ici
  - GOODFLAG_API_URL=https://api.goodflag.com/v1

# Redéployer la stack Swarm
docker stack deploy -c docker-compose.yml signature
```

## 🎨 Modification de l'interface (TODO)

Pour ajouter le choix dans l'interface web, modifiez `templates/index_new.html` :

Ajoutez AVANT le bouton "Signer le PDF" (ligne 88) :

```html
<!-- Choix du mode de signature -->
<div style="margin: 1.5rem 0; padding: 1rem; background: #f8f9fa; border-radius: 8px;">
    <h3 style="margin: 0 0 1rem 0; font-size: 1rem;">🔐 Mode de signature</h3>
    <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
        <label style="display: flex; align-items: center; gap: 0.5rem; cursor: pointer;">
            <input type="radio" name="signatureMode" value="pyhanko" checked>
            <div>
                <strong>🔓 Standard</strong><br>
                <small style="color: #6c757d;">Gratuit (usage personnel)</small>
            </div>
        </label>
        <label style="display: flex; align-items: center; gap: 0.5rem; cursor: pointer;">
            <input type="radio" name="signatureMode" value="goodflag">
            <div>
                <strong>✅ Qualifiée</strong><br>
                <small style="color: #6c757d;" id="goodflagStatus">Goodflag (INPI)</small>
            </div>
        </label>
    </div>
    <div id="goodflagWarning" class="hidden" style="margin-top: 0.5rem; padding: 0.5rem; background: #fff3cd;">
        ⚠️ API Goodflag non configurée
    </div>
</div>
```

Puis modifiez `static/js/index.js`, dans la fonction `signPDF()` :

```javascript
async function signPDF() {
    if (!currentFileId) {
        showMessage('Veuillez d\'abord charger un fichier PDF', 'error');
        return;
    }
    
    // Récupérer le mode de signature sélectionné
    const signatureMode = document.querySelector('input[name="signatureMode"]:checked')?.value || 'pyhanko';
    
    let signatureData;
    if (selectedSavedSignature) {
        signatureData = selectedSavedSignature.signature_data;
    } else {
        if (!signatureCanvas || signatureCanvas.isEmpty()) {
            showMessage('Veuillez créer une signature', 'error');
            return;
        }
        signatureData = signatureCanvas.toDataURL();
    }
    
    const position = {
        x: parseInt(document.getElementById('xPosition')?.value || 400),
        y: parseInt(document.getElementById('yPosition')?.value || 50),
        width: parseInt(document.getElementById('signWidth')?.value || 150),
        height: 75
    };
    const page = parseInt(document.getElementById('pageSelect')?.value || 0);
    
    try {
        showMessage('Signature en cours...', 'info');
        
        const headers = {'Content-Type': 'application/json'};
        if (authToken) {
            headers['Authorization'] = `Bearer ${authToken}`;
        }
        
        // Choisir l'endpoint selon le mode
        const endpoint = signatureMode === 'goodflag' ? '/api/sign-goodflag' : '/api/sign';
        
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({
                file_id: currentFileId,
                signature: signatureData,
                position: position,
                page: page
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            const modeText = signatureMode === 'goodflag' ? 'signature qualifiée Goodflag' : 'signature standard';
            showMessage(`✅ PDF signé avec ${modeText} !`, 'success');
            
            // Télécharger le fichier signé
            window.location.href = `/api/download/${data.signed_file_id}`;
            
            // Réinitialiser l'interface
            setTimeout(() => {
                currentFileId = null;
                if (signatureCanvas) signatureCanvas.clear();
                document.getElementById('signatureSection').classList.add('hidden');
                document.getElementById('pdfInfo').innerHTML = '';
                document.getElementById('pdfInfo').classList.add('hidden');
                document.getElementById('pdfFile').value = '';
            }, 2000);
        } else {
            showMessage(`❌ ${data.error || 'Erreur lors de la signature'}`, 'error');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showMessage('❌ Erreur réseau', 'error');
    }
}

// Vérifier le statut Goodflag au chargement
async function checkGoodflagStatus() {
    try {
        const response = await fetch('/api/goodflag/status');
        const data = await response.json();
        
        if (!data.configured || !data.available) {
            document.getElementById('goodflagWarning')?.classList.remove('hidden');
            document.getElementById('goodflagStatus').textContent = 'Non disponible';
        }
    } catch (error) {
        console.error('Erreur vérification Goodflag:', error);
    }
}

// Appeler au chargement de la page
document.addEventListener('DOMContentLoaded', () => {
    checkGoodflagStatus();
    // ... reste du code
});
```

## 🧪 Test

### Tester l'API (sans interface)
```bash
# En local
curl http://localhost:5000/api/goodflag/status

# En production (Docker Swarm)
curl https://votre-domaine.com/api/goodflag/status
```

Si configuré, vous devriez voir :
```json
{
  "configured": true,
  "available": true,
  "message": "Connecté: VotreCompteGoodflag"
}
```

## 📚 Documentation API Goodflag officielle

https://sgs-demo-test01.sunnystamp.com/wm-docs/api.html

## 💡 Résumé

- ✅ Backend prêt : 2 systèmes de signature fonctionnels
- ⚙️ Configuration : Ajouter GOODFLAG_API_TOKEN
- 🎨 Interface : Modifier index_new.html et index.js (code fourni ci-dessus)
- 💰 Coût : Goodflag payant (~quelques euros par signature)

Pour l'INPI, vous **devez** utiliser le mode Goodflag.
