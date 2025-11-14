// ============================================
// PAGE DE GESTION DES SIGNATURES
// ============================================

let createCanvas = null;
let savedSignatures = [];
let deleteTargetId = null;

// ============================================
// CALLBACKS FROM COMMON.JS
// ============================================

function onUserLoggedIn() {
    loadSavedSignatures();
}

function onUserLoggedOut() {
    // Rediriger vers la page d'accueil si pas connect\u00e9
    window.location.href = '/';
}

// ============================================
// INITIALISATION
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    // Vérifier si l'utilisateur est connecté
    if (!authToken && !localStorage.getItem('authToken')) {
        showMessage('Veuillez vous connecter pour acc\u00e9der \u00e0 cette page', 'info');
        setTimeout(() => {
            window.location.href = '/';
        }, 1500);
        return;
    }
    
    // Initialiser le canvas de création
    createCanvas = setupCanvas('createSignatureCanvas');
    
    // Masquer le formulaire de sauvegarde au départ
    const saveForm = document.getElementById('saveSignatureForm');
    if (saveForm) saveForm.classList.add('hidden');
});

// ============================================
// GESTION DU CANVAS DE CRÉATION
// ============================================

function clearCreateCanvas() {
    if (createCanvas) {
        createCanvas.clear();
        hideSaveSignatureForm();
    }
}

function undoCreateCanvas() {
    if (createCanvas) {
        createCanvas.undo();
    }
}

function showSaveSignatureForm() {
    if (!createCanvas || createCanvas.isEmpty()) {
        showMessage('Veuillez dessiner une signature d\'abord', 'error');
        return;
    }
    
    const saveBtn = document.getElementById('saveSignatureBtn');
    const saveForm = document.getElementById('saveSignatureForm');
    
    if (saveBtn) saveBtn.classList.add('hidden');
    if (saveForm) saveForm.classList.remove('hidden');
    
    // Focus sur le champ de nom
    document.getElementById('signatureName')?.focus();
}

function hideSaveSignatureForm() {
    const saveBtn = document.getElementById('saveSignatureBtn');
    const saveForm = document.getElementById('saveSignatureForm');
    const nameInput = document.getElementById('signatureName');
    
    if (saveBtn) saveBtn.classList.remove('hidden');
    if (saveForm) saveForm.classList.add('hidden');
    if (nameInput) nameInput.value = '';
}

function cancelSaveSignature() {
    hideSaveSignatureForm();
}

async function saveSignature() {
    const nameInput = document.getElementById('signatureName');
    const name = nameInput?.value.trim();
    
    if (!name) {
        showMessage('Veuillez entrer un nom pour la signature', 'error');
        return;
    }
    
    if (!createCanvas || createCanvas.isEmpty()) {
        showMessage('Veuillez dessiner une signature d\'abord', 'error');
        return;
    }
    
    const signatureData = createCanvas.toDataURL();
    
    try {
        const response = await apiCall('/api/signatures/save', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                name: name,
                signature: signatureData
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMessage('✅ Signature sauvegardée avec succès !', 'success');
            
            // Réinitialiser le canvas et le formulaire
            createCanvas.clear();
            hideSaveSignatureForm();
            
            // Recharger la liste
            loadSavedSignatures();
        } else {
            showMessage(data.error || 'Erreur lors de la sauvegarde', 'error');
        }
    } catch (error) {
        console.error('Save signature error:', error);
        showMessage('Erreur lors de la sauvegarde de la signature', 'error');
    }
}

// ============================================
// CHARGEMENT DES SIGNATURES
// ============================================

async function loadSavedSignatures() {
    if (!authToken) return;
    
    try {
        const response = await apiCall('/api/signatures');
        const data = await response.json();
        
        savedSignatures = data.signatures || [];
        displaySavedSignatures();
    } catch (error) {
        console.error('Error loading signatures:', error);
        showMessage('Erreur lors du chargement des signatures', 'error');
    }
}

function displaySavedSignatures() {
    const noSignaturesMsg = document.getElementById('noSignaturesMessage');
    const signaturesList = document.getElementById('savedSignaturesList');
    
    if (savedSignatures.length === 0) {
        if (noSignaturesMsg) noSignaturesMsg.classList.remove('hidden');
        if (signaturesList) signaturesList.classList.add('hidden');
        return;
    }
    
    if (noSignaturesMsg) noSignaturesMsg.classList.add('hidden');
    if (signaturesList) {
        signaturesList.classList.remove('hidden');
        signaturesList.innerHTML = '';
        
        savedSignatures.forEach(signature => {
            const item = document.createElement('div');
            item.className = 'signature-item';
            item.innerHTML = `
                <img src="${signature.signature_data}" alt="${signature.name}" class="signature-preview">
                <div class="signature-name">${signature.name}</div>
                <button class="signature-delete" onclick="confirmDeleteSignature(${signature.id})" title="Supprimer">
                    ×
                </button>
            `;
            signaturesList.appendChild(item);
        });
    }
}

// ============================================
// SUPPRESSION DE SIGNATURES
// ============================================

function confirmDeleteSignature(id) {
    deleteTargetId = id;
    const modal = document.getElementById('deleteModal');
    if (modal) modal.classList.remove('hidden');
    
    // Attacher l'événement au bouton de confirmation
    const confirmBtn = document.getElementById('confirmDeleteBtn');
    if (confirmBtn) {
        confirmBtn.onclick = deleteSignature;
    }
}

function closeDeleteModal() {
    deleteTargetId = null;
    const modal = document.getElementById('deleteModal');
    if (modal) modal.classList.add('hidden');
}

async function deleteSignature() {
    if (!deleteTargetId) return;
    
    try {
        const response = await apiCall(`/api/signatures/${deleteTargetId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMessage('✅ Signature supprimée', 'success');
            closeDeleteModal();
            loadSavedSignatures();
        } else {
            showMessage(data.error || 'Erreur lors de la suppression', 'error');
        }
    } catch (error) {
        console.error('Delete signature error:', error);
        showMessage('Erreur lors de la suppression de la signature', 'error');
    }
}
