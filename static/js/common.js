// ============================================
// VARIABLES GLOBALES
// ============================================
let currentUser = null;
let authToken = null;

// ============================================
// RECAPTCHA
// ============================================

// Configuration reCAPTCHA (clé publique)
const RECAPTCHA_SITE_KEY = '6LdP6AwsAAAAAMDKl4Qo9u3C0dK1qhTWjJMvEmDq';

async function getRecaptchaToken(action) {
    try {
        // Si grecaptcha n'est pas chargé, retourner null
        if (typeof grecaptcha === 'undefined') {
            console.warn('reCAPTCHA not loaded');
            return null;
        }
        
        // Attendre que grecaptcha soit prêt et obtenir le token
        return await new Promise((resolve, reject) => {
            grecaptcha.ready(async () => {
                try {
                    const token = await grecaptcha.execute(RECAPTCHA_SITE_KEY, { action });
                    resolve(token);
                } catch (error) {
                    reject(error);
                }
            });
        });
    } catch (error) {
        console.error('Erreur reCAPTCHA:', error);
        return null;
    }
}

// ============================================
// AUTHENTIFICATION
// ============================================

function checkAuth() {
    authToken = localStorage.getItem('authToken');
    if (authToken) {
        fetch('/api/me', {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        })
        .then(r => r.json())
        .then(data => {
            if (data.id) {
                currentUser = data;
                updateUIForLoggedInUser();
                
                // Appeler le callback de la page si défini
                if (typeof onUserLoggedIn === 'function') {
                    onUserLoggedIn();
                }
            } else {
                logout();
            }
        })
        .catch(() => logout());
    } else {
        updateUIForLoggedOutUser();
        
        // Appeler le callback de la page si défini
        if (typeof onUserLoggedOut === 'function') {
            onUserLoggedOut();
        }
    }
}

function updateUIForLoggedInUser() {
    const userNameEl = document.getElementById('userName');
    const headerUserEmailEl = document.getElementById('headerUserEmail');
    const userInfoEl = document.getElementById('userInfo');
    const authBtnEl = document.getElementById('authBtn');
    
    if (userNameEl) userNameEl.textContent = currentUser.name || 'Utilisateur';
    if (headerUserEmailEl) headerUserEmailEl.textContent = currentUser.email;
    if (userInfoEl) userInfoEl.classList.remove('hidden');
    if (authBtnEl) {
        authBtnEl.textContent = 'Déconnexion';
        authBtnEl.onclick = logout;
    }
    
    // Afficher les liens de navigation réservés aux utilisateurs connectés
    document.querySelectorAll('.nav-auth-required').forEach(link => {
        link.classList.remove('hidden');
    });
    
    // Callback pour les pages spécifiques
    if (typeof onUserLoggedIn === 'function') {
        onUserLoggedIn();
    }
}

function updateUIForLoggedOutUser() {
    const userInfoEl = document.getElementById('userInfo');
    const authBtnEl = document.getElementById('authBtn');
    
    if (userInfoEl) userInfoEl.classList.add('hidden');
    if (authBtnEl) {
        authBtnEl.textContent = 'Connexion';
        authBtnEl.onclick = showAuthModal;
    }
    
    // Masquer les liens de navigation réservés aux utilisateurs connectés
    document.querySelectorAll('.nav-auth-required').forEach(link => {
        link.classList.add('hidden');
    });
    
    // Callback pour les pages spécifiques
    if (typeof onUserLoggedOut === 'function') {
        onUserLoggedOut();
    }
}

function showAuthModal() {
    const modal = document.getElementById('authModal');
    if (modal) modal.classList.add('active');
}

function closeAuthModal() {
    const modal = document.getElementById('authModal');
    if (modal) modal.classList.remove('active');
}

function showLoginForm() {
    document.getElementById('registerForm')?.classList.add('hidden');
    document.getElementById('loginForm')?.classList.remove('hidden');
}

function showRegisterForm() {
    document.getElementById('loginForm')?.classList.add('hidden');
    document.getElementById('registerForm')?.classList.remove('hidden');
}

async function login() {
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;

    if (!email || !password) {
        showMessage('Veuillez remplir tous les champs', 'error');
        return;
    }

    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email, password})
        });

        const data = await response.json();

        if (response.ok && data.success) {
            authToken = data.token;
            localStorage.setItem('authToken', authToken);
            currentUser = data.user;
            updateUIForLoggedInUser();
            closeAuthModal();
            showMessage('Connexion réussie !', 'success');
        } else {
            showMessage(data.error || 'Email ou mot de passe incorrect', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showMessage('Erreur de connexion au serveur', 'error');
    }
}

async function register() {
    const name = document.getElementById('registerName').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;

    if (!email || !password) {
        showMessage('Email et mot de passe requis', 'error');
        return;
    }

    try {
        // Obtenir le token reCAPTCHA
        const recaptchaToken = await getRecaptchaToken('register');
        
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                name, 
                email, 
                password,
                recaptcha_token: recaptchaToken
            })
        });

        const data = await response.json();

        if (data.success) {
            authToken = data.token;
            localStorage.setItem('authToken', authToken);
            await checkAuth();
            closeAuthModal();
            showMessage('Compte créé avec succès !', 'success');
        } else {
            showMessage(data.error, 'error');
        }
    } catch (error) {
        showMessage('Erreur lors de l\'inscription', 'error');
    }
}

function logout() {
    if (authToken) {
        fetch('/api/logout', {
            method: 'POST',
            headers: {'Authorization': `Bearer ${authToken}`}
        });
    }
    
    localStorage.removeItem('authToken');
    authToken = null;
    currentUser = null;
    
    updateUIForLoggedOutUser();
    showMessage('Déconnexion réussie', 'info');
    
    // Rediriger vers la page d'accueil après 1 seconde
    setTimeout(() => {
        window.location.href = '/';
    }, 1000);
}

// ============================================
// MESSAGES UTILISATEUR
// ============================================

function showMessage(message, type = 'info') {
    // Chercher la zone de message dans la page
    let messageArea = document.getElementById('messageArea');
    
    // Si pas de zone de message, en créer une temporaire
    if (!messageArea) {
        messageArea = document.createElement('div');
        messageArea.id = 'messageArea';
        messageArea.style.position = 'fixed';
        messageArea.style.top = '20px';
        messageArea.style.right = '20px';
        messageArea.style.zIndex = '10000';
        messageArea.style.maxWidth = '400px';
        document.body.appendChild(messageArea);
    }
    
    const alertClass = type === 'error' ? 'alert-error' : (type === 'info' ? 'alert-info' : 'alert-success');
    const icon = type === 'error' ? '❌' : (type === 'info' ? 'ℹ️' : '✅');
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert ${alertClass}`;
    alertDiv.innerHTML = `${icon} ${message}`;
    alertDiv.style.marginBottom = '10px';
    alertDiv.style.animation = 'slideIn 0.3s ease-out';
    
    messageArea.appendChild(alertDiv);
    
    // Supprimer le message après 5 secondes
    setTimeout(() => {
        alertDiv.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => {
            alertDiv.remove();
        }, 300);
    }, 5000);
}

// ============================================
// UTILITAIRES API
// ============================================

async function apiCall(url, options = {}) {
    const headers = options.headers || {};
    
    if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }
    
    const response = await fetch(url, {
        ...options,
        headers
    });
    
    // Si 401, déconnecter l'utilisateur
    if (response.status === 401) {
        logout();
        throw new Error('Non authentifié');
    }
    
    return response;
}

// ============================================
// UTILITAIRES CANVAS
// ============================================

function setupCanvas(canvasId) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;
    
    const ctx = canvas.getContext('2d');
    let isDrawing = false;
    let paths = [];
    let currentPath = [];
    
    // Configuration du style
    ctx.strokeStyle = '#000000';
    ctx.lineWidth = 2;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    
    // Redimensionner le canvas
    function resize() {
        const container = canvas.parentElement;
        const width = Math.min(container.clientWidth - 32, 600);
        const height = Math.min(window.innerHeight * 0.3, 300);
        
        const savedPaths = [...paths];
        canvas.width = width;
        canvas.height = height;
        
        ctx.strokeStyle = '#000000';
        ctx.lineWidth = 2;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        
        paths = savedPaths;
        redraw();
    }
    
    // Redessiner tous les chemins
    function redraw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        paths.forEach(path => {
            if (path.length > 0) {
                ctx.beginPath();
                ctx.moveTo(path[0].x, path[0].y);
                for (let i = 1; i < path.length; i++) {
                    ctx.lineTo(path[i].x, path[i].y);
                }
                ctx.stroke();
            }
        });
    }
    
    // Obtenir les coordonnées
    function getCoordinates(e) {
        const rect = canvas.getBoundingClientRect();
        const scaleX = canvas.width / rect.width;
        const scaleY = canvas.height / rect.height;
        
        if (e.touches) {
            return {
                x: (e.touches[0].clientX - rect.left) * scaleX,
                y: (e.touches[0].clientY - rect.top) * scaleY
            };
        }
        return {
            x: (e.clientX - rect.left) * scaleX,
            y: (e.clientY - rect.top) * scaleY
        };
    }
    
    // Événements de dessin
    function startDrawing(e) {
        e.preventDefault();
        isDrawing = true;
        currentPath = [];
        const coords = getCoordinates(e);
        currentPath.push(coords);
        ctx.beginPath();
        ctx.moveTo(coords.x, coords.y);
    }
    
    function draw(e) {
        if (!isDrawing) return;
        e.preventDefault();
        const coords = getCoordinates(e);
        currentPath.push(coords);
        ctx.lineTo(coords.x, coords.y);
        ctx.stroke();
    }
    
    function stopDrawing() {
        if (isDrawing) {
            isDrawing = false;
            if (currentPath.length > 0) {
                paths.push([...currentPath]);
            }
        }
    }
    
    // Attacher les événements
    canvas.addEventListener('mousedown', startDrawing);
    canvas.addEventListener('mousemove', draw);
    canvas.addEventListener('mouseup', stopDrawing);
    canvas.addEventListener('mouseout', stopDrawing);
    
    canvas.addEventListener('touchstart', startDrawing);
    canvas.addEventListener('touchmove', draw);
    canvas.addEventListener('touchend', stopDrawing);
    
    resize();
    window.addEventListener('resize', resize);
    
    // Retourner l'API du canvas
    return {
        canvas,
        ctx,
        getPaths: () => paths,
        setPaths: (newPaths) => { paths = newPaths; redraw(); },
        clear: () => { paths = []; currentPath = []; ctx.clearRect(0, 0, canvas.width, canvas.height); },
        undo: () => { paths.pop(); redraw(); },
        isEmpty: () => paths.length === 0,
        toDataURL: () => canvas.toDataURL('image/png')
    };
}

// ============================================
// INITIALISATION
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    // Appliquer le mode sombre si activé
    if (localStorage.getItem('darkMode') === 'true') {
        document.body.classList.add('dark-mode');
    }
    
    // Appliquer le mode tactile si activé
    if (localStorage.getItem('touchMode') === 'true') {
        document.body.classList.add('touch-mode');
    }
    
    checkAuth();
});
