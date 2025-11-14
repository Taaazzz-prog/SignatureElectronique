// ============================================
// PAGE D'HISTORIQUE DES SIGNATURES
// ============================================

let allHistory = [];
let filteredHistory = [];

// ============================================
// CALLBACKS FROM COMMON.JS
// ============================================

function onUserLoggedIn() {
    loadHistory();
}

function onUserLoggedOut() {
    // Rediriger vers la page d'accueil si pas connecté
    window.location.href = '/';
}

// ============================================
// INITIALISATION
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    // Vérifier si l'utilisateur est connecté
    if (!authToken && !localStorage.getItem('authToken')) {
        showMessage('Veuillez vous connecter pour accéder à cette page', 'info');
        setTimeout(() => {
            window.location.href = '/';
        }, 1500);
        return;
    }
});

// ============================================
// CHARGEMENT DE L'HISTORIQUE
// ============================================

async function loadHistory() {
    if (!authToken) return;
    
    try {
        const response = await apiCall('/api/history?limit=100');
        const data = await response.json();
        
        allHistory = data.history || [];
        filteredHistory = [...allHistory];
        
        displayHistory();
        updateStatistics();
    } catch (error) {
        console.error('Error loading history:', error);
        showMessage('Erreur lors du chargement de l\'historique', 'error');
    }
}

function displayHistory() {
    const noHistoryMsg = document.getElementById('noHistoryMessage');
    const historyList = document.getElementById('historyList');
    
    if (filteredHistory.length === 0) {
        if (noHistoryMsg) noHistoryMsg.classList.remove('hidden');
        if (historyList) historyList.classList.add('hidden');
        return;
    }
    
    if (noHistoryMsg) noHistoryMsg.classList.add('hidden');
    if (historyList) {
        historyList.classList.remove('hidden');
        historyList.innerHTML = '';
        
        filteredHistory.forEach(item => {
            const historyItem = document.createElement('div');
            historyItem.className = 'history-item';
            
            const date = new Date(item.created_at);
            const formattedDate = formatDate(date);
            
            historyItem.innerHTML = `
                <div class="history-info">
                    <div class="history-filename">📄 ${item.original_filename}</div>
                    <div class="history-date">Signé le ${formattedDate}</div>
                </div>
                <button class="btn btn-primary btn-small" onclick="downloadHistoryItem(${item.id})">
                    📥 Télécharger
                </button>
            `;
            
            historyList.appendChild(historyItem);
        });
    }
}

function formatDate(date) {
    const options = {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return date.toLocaleDateString('fr-FR', options);
}

async function downloadHistoryItem(id) {
    try {
        window.location.href = `/api/history/${id}/download`;
        showMessage('Téléchargement en cours...', 'info');
    } catch (error) {
        console.error('Download error:', error);
        showMessage('Erreur lors du téléchargement', 'error');
    }
}

// ============================================
// FILTRAGE ET TRI
// ============================================

function filterHistory() {
    const searchTerm = document.getElementById('searchInput')?.value.toLowerCase() || '';
    const periodFilter = document.getElementById('periodFilter')?.value || 'all';
    
    filteredHistory = allHistory.filter(item => {
        // Filtre de recherche
        const matchesSearch = item.original_filename.toLowerCase().includes(searchTerm);
        
        // Filtre de période
        let matchesPeriod = true;
        if (periodFilter !== 'all') {
            const itemDate = new Date(item.created_at);
            const now = new Date();
            
            switch (periodFilter) {
                case 'today':
                    matchesPeriod = isSameDay(itemDate, now);
                    break;
                case 'week':
                    matchesPeriod = isWithinDays(itemDate, 7);
                    break;
                case 'month':
                    matchesPeriod = isWithinDays(itemDate, 30);
                    break;
                case 'year':
                    matchesPeriod = isWithinDays(itemDate, 365);
                    break;
            }
        }
        
        return matchesSearch && matchesPeriod;
    });
    
    displayHistory();
    updateStatistics();
}

function sortHistory() {
    const sortOrder = document.getElementById('sortOrder')?.value || 'desc';
    
    filteredHistory.sort((a, b) => {
        const dateA = new Date(a.created_at);
        const dateB = new Date(b.created_at);
        
        return sortOrder === 'desc' ? dateB - dateA : dateA - dateB;
    });
    
    displayHistory();
}

// ============================================
// STATISTIQUES
// ============================================

function updateStatistics() {
    const now = new Date();
    
    const total = allHistory.length;
    const today = allHistory.filter(item => isSameDay(new Date(item.created_at), now)).length;
    const thisWeek = allHistory.filter(item => isWithinDays(new Date(item.created_at), 7)).length;
    const thisMonth = allHistory.filter(item => isWithinDays(new Date(item.created_at), 30)).length;
    
    document.getElementById('statTotal').textContent = total;
    document.getElementById('statToday').textContent = today;
    document.getElementById('statThisWeek').textContent = thisWeek;
    document.getElementById('statThisMonth').textContent = thisMonth;
}

// ============================================
// UTILITAIRES DE DATE
// ============================================

function isSameDay(date1, date2) {
    return date1.getDate() === date2.getDate() &&
           date1.getMonth() === date2.getMonth() &&
           date1.getFullYear() === date2.getFullYear();
}

function isWithinDays(date, days) {
    const now = new Date();
    const diffTime = now - date; // En millisecondes
    const diffDays = diffTime / (1000 * 60 * 60 * 24); // Convertir en jours
    return diffDays >= 0 && diffDays < days; // Entre 0 et days jours
}
