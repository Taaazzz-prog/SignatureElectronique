// ============================================
// PAGE D'ACCUEIL - UPLOAD & SIGN PDF
// ============================================

let currentFileId = null;
let signatureCanvas = null;
let savedSignatures = [];
let selectedSavedSignature = null;

// ============================================
// CALLBACKS FROM COMMON.JS
// ============================================

function onUserLoggedIn() {
    const signatureTabsEl = document.getElementById('signatureTypeTabs');
    const saveSignatureBtnEl = document.getElementById('saveSignatureBtn');
    
    if (signatureTabsEl) signatureTabsEl.classList.remove('hidden');
    if (saveSignatureBtnEl) saveSignatureBtnEl.classList.remove('hidden');
    
    loadSavedSignatures();
}

function onUserLoggedOut() {
    const signatureTabsEl = document.getElementById('signatureTypeTabs');
    const saveSignatureBtnEl = document.getElementById('saveSignatureBtn');
    const savedSignaturesEl = document.getElementById('savedSignaturesSelection');
    
    if (signatureTabsEl) signatureTabsEl.classList.add('hidden');
    if (saveSignatureBtnEl) saveSignatureBtnEl.classList.add('hidden');
    if (savedSignaturesEl) savedSignaturesEl.classList.add('hidden');
    
    savedSignatures = [];
    selectedSavedSignature = null;
}

// ============================================
// INITIALISATION
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    // Initialiser le canvas de signature
    signatureCanvas = setupCanvas('signatureCanvas');
    
    // Event listeners pour l'upload
    const fileInput = document.getElementById('pdfFile');
    const uploadZone = document.getElementById('uploadZone');
    
    if (fileInput) {
        fileInput.addEventListener('change', handleFileSelect);
    }
    
    if (uploadZone) {
        // Drag & Drop
        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.classList.add('dragging');
        });
        
        uploadZone.addEventListener('dragleave', () => {
            uploadZone.classList.remove('dragging');
        });
        
        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('dragging');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFile(files[0]);
            }
        });
    }
});

// ============================================
// UPLOAD DE FICHIER
// ============================================

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
}

async function handleFile(file) {
    if (!file.type.match('application/pdf')) {
        showMessage('Veuillez sélectionner un fichier PDF', 'error');
        return;
    }
    
    if (file.size > 16 * 1024 * 1024) {
        showMessage('Le fichier est trop volumineux (maximum 16 MB)', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        showMessage('Chargement du fichier...', 'info');
        
        const response = await fetch('/api/upload', {
            method: 'POST',
            headers: authToken ? {'Authorization': `Bearer ${authToken}`} : {},
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentFileId = data.file_id;
            showMessage(`✅ ${data.filename} chargé (${data.num_pages} page${data.num_pages > 1 ? 's' : ''})`, 'success');
            
            // Afficher les infos du fichier
            const pdfInfoEl = document.getElementById('pdfInfo');
            if (pdfInfoEl) {
                pdfInfoEl.innerHTML = `
                    <div style="padding: 1rem; background: var(--bg-light); border-radius: 12px;">
                        <strong>📄 ${data.filename}</strong><br>
                        <small style="color: var(--text-light);">${data.num_pages} page${data.num_pages > 1 ? 's' : ''}</small>
                    </div>
                `;
                pdfInfoEl.classList.remove('hidden');
            }
            
            // Afficher la section signature
            document.getElementById('signatureSection')?.classList.remove('hidden');
            
            // Remplir le sélecteur de pages
            populatePageSelect(data.num_pages);
        } else {
            showMessage(data.error || 'Erreur lors du chargement', 'error');
        }
    } catch (error) {
        console.error('Upload error:', error);
        showMessage('Erreur lors du chargement du fichier', 'error');
    }
}

function populatePageSelect(numPages) {
    const select = document.getElementById('pageSelect');
    if (!select) return;
    
    select.innerHTML = '';
    for (let i = 0; i < numPages; i++) {
        const option = document.createElement('option');
        option.value = i;
        option.textContent = `Page ${i + 1}`;
        select.appendChild(option);
    }
}

// ============================================
// GESTION DES SIGNATURES
// ============================================

function clearCanvas() {
    if (signatureCanvas) {
        signatureCanvas.clear();
    }
}

function undoLast() {
    if (signatureCanvas) {
        signatureCanvas.undo();
    }
}

function switchSignatureType(type) {
    // Mettre à jour les onglets
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    event.target.classList.add('active');
    
    // Afficher la bonne section
    if (type === 'draw') {
        document.getElementById('drawSignature')?.classList.remove('hidden');
        document.getElementById('savedSignaturesSelection')?.classList.add('hidden');
        selectedSavedSignature = null;
    } else if (type === 'saved') {
        document.getElementById('drawSignature')?.classList.add('hidden');
        document.getElementById('savedSignaturesSelection')?.classList.remove('hidden');
    }
}

async function loadSavedSignatures() {
    if (!authToken) return;
    
    try {
        const response = await apiCall('/api/signatures');
        const data = await response.json();
        
        savedSignatures = data.signatures || [];
        displaySavedSignaturesForSelection();
    } catch (error) {
        console.error('Error loading signatures:', error);
    }
}

function displaySavedSignaturesForSelection() {
    const container = document.getElementById('savedSignaturesSelect');
    if (!container) return;
    
    if (savedSignatures.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 2rem; color: var(--text-light);">
                <p>Aucune signature sauvegardée.</p>
                <p style="margin-top: 0.5rem;">
                    <a href="/signatures" style="color: var(--primary);">Créer une signature</a>
                </p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = '';
    savedSignatures.forEach(sig => {
        const item = document.createElement('div');
        item.className = 'signature-item';
        item.onclick = () => selectSavedSignature(sig.id);
        item.innerHTML = `
            <img src="${sig.signature_data}" alt="${sig.name}" class="signature-preview">
            <div class="signature-name">${sig.name}</div>
        `;
        container.appendChild(item);
    });
}

function selectSavedSignature(id) {
    selectedSavedSignature = savedSignatures.find(s => s.id === id);
    
    // Mettre à jour la sélection visuelle
    document.querySelectorAll('#savedSignaturesSelect .signature-item').forEach(item => {
        item.classList.remove('selected');
    });
    event.currentTarget.classList.add('selected');
}

function showSaveSignatureDialog() {
    if (!authToken) {
        showMessage('Connectez-vous pour sauvegarder des signatures', 'info');
        showAuthModal();
        return;
    }
    
    if (signatureCanvas && signatureCanvas.isEmpty()) {
        showMessage('Veuillez créer une signature d\'abord', 'error');
        return;
    }
    
    const name = prompt('Nom de la signature :');
    if (!name) return;
    
    saveSignatureToServer(name, signatureCanvas.toDataURL());
}

async function saveSignatureToServer(name, signatureData) {
    try {
        const response = await apiCall('/api/signatures/save', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({name, signature: signatureData})
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMessage('✅ Signature sauvegardée !', 'success');
            loadSavedSignatures();
        } else {
            showMessage(data.error || 'Erreur lors de la sauvegarde', 'error');
        }
    } catch (error) {
        console.error('Save signature error:', error);
        showMessage('Erreur lors de la sauvegarde', 'error');
    }
}

// ============================================
// SIGNATURE DU PDF
// ============================================

async function signPDF() {
    if (!currentFileId) {
        showMessage('Veuillez d\'abord charger un fichier PDF', 'error');
        return;
    }
    
    let signatureData;
    
    // Vérifier si on utilise une signature sauvegardée ou dessinée
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
        
        const response = await fetch('/api/sign', {
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
            showMessage('✅ PDF signé avec succès !', 'success');
            
            // Télécharger le fichier signé
            window.location.href = `/api/download/${data.signed_file_id}`;
            
            // Réinitialiser l'interface
            setTimeout(() => {
                currentFileId = null;
                if (signatureCanvas) signatureCanvas.clear();
                document.getElementById('signatureSection')?.classList.add('hidden');
                document.getElementById('pdfInfo')?.classList.add('hidden');
                document.getElementById('pdfFile').value = '';
            }, 1000);
        } else {
            showMessage(data.error || 'Erreur lors de la signature', 'error');
        }
    } catch (error) {
        console.error('Sign PDF error:', error);
        showMessage('Erreur lors de la signature du PDF', 'error');
    }
}
