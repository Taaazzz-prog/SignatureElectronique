// ============================================
// PAGE DE GESTION DU COMPTE
// ============================================

let userStats = {
    totalSignedDocs: 0,
    totalSignatures: 0,
    accountAge: 0
};

let confirmCallback = null;

// ============================================
// CALLBACKS FROM COMMON.JS
// ============================================

function onUserLoggedIn() {
    loadUserInfo();
    loadUserStats();
    loadPreferences();
}

function onUserLoggedOut() {
    // Rediriger vers la page d'accueil si pas connecté
    window.location.href = '/';
}

// ============================================
// INITIALISATION
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    // Attendre que common.js charge l'utilisateur
    const checkUserInterval = setInterval(() => {
        if (typeof currentUser !== 'undefined') {
            clearInterval(checkUserInterval);
            if (currentUser) {
                loadUserInfo();
                loadUserStats();
                loadPreferences();
            } else if (!localStorage.getItem('authToken')) {
                showMessage('Veuillez vous connecter pour accéder à cette page', 'info');
                setTimeout(() => {
                    window.location.href = '/';
                }, 1500);
            }
        }
    }, 100);
    
    // Timeout de sécurité
    setTimeout(() => {
        clearInterval(checkUserInterval);
        if (!currentUser && !localStorage.getItem('authToken')) {
            window.location.href = '/';
        }
    }, 3000);
});

// ============================================
// CHARGEMENT DES INFORMATIONS
// ============================================

function loadUserInfo() {
    if (!currentUser) return;
    
    // Email
    const emailEl = document.getElementById('userEmail');
    if (emailEl) emailEl.textContent = currentUser.email || '-';
    
    // Initiales pour l'avatar
    const initialsEl = document.getElementById('avatarInitials');
    if (initialsEl) {
        const initials = currentUser.email.substring(0, 2).toUpperCase();
        initialsEl.textContent = initials;
    }
    
    // Date de création du compte
    if (currentUser.created_at) {
        const createdDate = new Date(currentUser.created_at);
        const memberSinceEl = document.getElementById('memberSince');
        if (memberSinceEl) {
            memberSinceEl.textContent = formatDate(createdDate);
        }
    }
    
    // Dernière connexion (maintenant)
    const lastLoginEl = document.getElementById('lastLogin');
    if (lastLoginEl) {
        lastLoginEl.textContent = 'Maintenant';
    }
}

async function loadUserStats() {
    if (!authToken) return;
    
    try {
        // Charger l'historique
        const historyResponse = await apiCall('/api/history?limit=1000');
        const historyData = await historyResponse.json();
        userStats.totalSignedDocs = historyData.history?.length || 0;
        
        // Charger les signatures
        const signaturesResponse = await apiCall('/api/signatures');
        const signaturesData = await signaturesResponse.json();
        userStats.totalSignatures = signaturesData.signatures?.length || 0;
        
        // Calculer l'âge du compte
        if (currentUser && currentUser.created_at) {
            const createdDate = new Date(currentUser.created_at);
            const now = new Date();
            const diffTime = Math.abs(now - createdDate);
            userStats.accountAge = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        }
        
        displayStats();
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

function displayStats() {
    document.getElementById('totalSignedDocs').textContent = userStats.totalSignedDocs;
    document.getElementById('totalSignatures').textContent = userStats.totalSignatures;
    document.getElementById('accountAge').textContent = userStats.accountAge;
}

function formatDate(date) {
    const options = {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    };
    return date.toLocaleDateString('fr-FR', options);
}

// ============================================
// PRÉFÉRENCES
// ============================================

function loadPreferences() {
    // Charger les préférences depuis localStorage
    const darkMode = localStorage.getItem('darkMode') === 'true';
    const notifications = localStorage.getItem('notifications') === 'true';
    const autoSave = localStorage.getItem('autoSave') === 'true';
    const touchMode = localStorage.getItem('touchMode') === 'true';
    
    document.getElementById('darkModeToggle').checked = darkMode;
    document.getElementById('notificationsToggle').checked = notifications;
    document.getElementById('autoSaveToggle').checked = autoSave;
    document.getElementById('touchModeToggle').checked = touchMode;
    
    // Charger les paramètres de signature par défaut
    document.getElementById('defaultX').value = localStorage.getItem('defaultX') || '400';
    document.getElementById('defaultY').value = localStorage.getItem('defaultY') || '50';
    document.getElementById('defaultWidth').value = localStorage.getItem('defaultWidth') || '150';
    document.getElementById('defaultPage').value = localStorage.getItem('defaultPage') || '0';
    
    // Appliquer le mode sombre si activé
    if (darkMode) {
        document.body.classList.add('dark-mode');
    }
}

function toggleDarkMode() {
    const enabled = document.getElementById('darkModeToggle').checked;
    localStorage.setItem('darkMode', enabled);
    
    if (enabled) {
        document.body.classList.add('dark-mode');
        showMessage('Mode sombre activé', 'success');
    } else {
        document.body.classList.remove('dark-mode');
        showMessage('Mode sombre désactivé', 'success');
    }
}

function toggleNotifications() {
    const enabled = document.getElementById('notificationsToggle').checked;
    localStorage.setItem('notifications', enabled);
    showMessage(enabled ? 'Notifications activées' : 'Notifications désactivées', 'success');
}

function toggleAutoSave() {
    const enabled = document.getElementById('autoSaveToggle').checked;
    localStorage.setItem('autoSave', enabled);
    showMessage(enabled ? 'Sauvegarde automatique activée' : 'Sauvegarde automatique désactivée', 'success');
}

function toggleTouchMode() {
    const enabled = document.getElementById('touchModeToggle').checked;
    localStorage.setItem('touchMode', enabled);
    showMessage(enabled ? 'Mode tactile activé' : 'Mode tactile désactivé', 'success');
}

function saveDefaultSettings() {
    const defaultX = document.getElementById('defaultX').value;
    const defaultY = document.getElementById('defaultY').value;
    const defaultWidth = document.getElementById('defaultWidth').value;
    const defaultPage = document.getElementById('defaultPage').value;
    
    localStorage.setItem('defaultX', defaultX);
    localStorage.setItem('defaultY', defaultY);
    localStorage.setItem('defaultWidth', defaultWidth);
    localStorage.setItem('defaultPage', defaultPage);
    
    showMessage('✅ Paramètres par défaut sauvegardés', 'success');
}

// ============================================
// ACTIONS DANGEREUSES
// ============================================

function confirmDeleteAllSignatures() {
    showConfirmModal(
        '🗑️ Supprimer toutes les signatures',
        'Voulez-vous vraiment supprimer toutes vos signatures sauvegardées ? Cette action est irréversible.',
        deleteAllSignatures
    );
}

function confirmDeleteHistory() {
    showConfirmModal(
        '🗑️ Effacer l\'historique',
        'Voulez-vous vraiment effacer tout votre historique de signatures ? Cette action est irréversible.',
        deleteHistory
    );
}

function confirmDeleteAccount() {
    showConfirmModal(
        '⚠️ Supprimer le compte',
        'Voulez-vous vraiment supprimer votre compte et toutes vos données ? Cette action est DÉFINITIVE et IRRÉVERSIBLE.',
        deleteAccount
    );
}

function showConfirmModal(title, message, callback) {
    document.getElementById('confirmModalTitle').textContent = title;
    document.getElementById('confirmModalMessage').textContent = message;
    confirmCallback = callback;
    
    const confirmBtn = document.getElementById('confirmActionBtn');
    confirmBtn.onclick = () => {
        if (confirmCallback) confirmCallback();
        closeConfirmModal();
    };
    
    document.getElementById('confirmModal').classList.remove('hidden');
}

function closeConfirmModal() {
    document.getElementById('confirmModal').classList.add('hidden');
    confirmCallback = null;
}

async function deleteAllSignatures() {
    try {
        // Charger toutes les signatures
        const response = await apiCall('/api/signatures');
        const data = await response.json();
        const signatures = data.signatures || [];
        
        // Supprimer chaque signature
        for (const sig of signatures) {
            await apiCall(`/api/signatures/${sig.id}`, { method: 'DELETE' });
        }
        
        showMessage('✅ Toutes les signatures ont été supprimées', 'success');
        loadUserStats();
    } catch (error) {
        console.error('Error deleting signatures:', error);
        showMessage('Erreur lors de la suppression des signatures', 'error');
    }
}

async function deleteHistory() {
    try {
        const response = await apiCall('/api/history', { method: 'DELETE' });
        if (response.ok) {
            showMessage('✅ Historique supprimé avec succès', 'success');
            loadUserStats();
        } else {
            showMessage('Erreur lors de la suppression de l\'historique', 'error');
        }
    } catch (error) {
        console.error('Error deleting history:', error);
        showMessage('Erreur lors de la suppression de l\'historique', 'error');
    }
}

async function deleteAccount() {
    try {
        const response = await apiCall('/api/account', { method: 'DELETE' });
        if (response.ok) {
            showMessage('✅ Compte supprimé. Vous allez être déconnecté...', 'success');
            setTimeout(() => {
                logout();
            }, 2000);
        } else {
            showMessage('Erreur lors de la suppression du compte', 'error');
        }
    } catch (error) {
        console.error('Error deleting account:', error);
        showMessage('Erreur lors de la suppression du compte', 'error');
    }
}
