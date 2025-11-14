"""
Gestion de la base de données SQLite pour l'application
"""
import sqlite3
import hashlib
import secrets
from datetime import datetime
from contextlib import contextmanager

DATABASE_PATH = 'signature_app.db'

@contextmanager
def get_db():
    """Context manager pour la connexion à la base de données"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_db():
    """Initialise la base de données avec les tables nécessaires"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Table des utilisateurs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Table des signatures sauvegardées
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS saved_signatures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                signature_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        # Table de l'historique des signatures
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signature_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                original_filename TEXT NOT NULL,
                signed_filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                signature_page INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
            )
        ''')
        
        # Table des sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        print("Base de donnees initialisee avec succes")

def hash_password(password):
    """Hash un mot de passe avec SHA-256 et un salt"""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${pwd_hash}"

def verify_password(password, password_hash):
    """Vérifie un mot de passe contre son hash"""
    try:
        salt, pwd_hash = password_hash.split('$')
        new_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return new_hash == pwd_hash
    except:
        return False

def create_user(email, password, name=None):
    """Crée un nouvel utilisateur"""
    with get_db() as conn:
        cursor = conn.cursor()
        password_hash = hash_password(password)
        
        try:
            cursor.execute(
                'INSERT INTO users (email, password_hash, name) VALUES (?, ?, ?)',
                (email, password_hash, name)
            )
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

def authenticate_user(email, password):
    """Authentifie un utilisateur et retourne ses informations"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        
        if user and verify_password(password, user['password_hash']):
            # Mise à jour du last_login
            cursor.execute(
                'UPDATE users SET last_login = ? WHERE id = ?',
                (datetime.now(), user['id'])
            )
            return dict(user)
        return None

def create_session(user_id):
    """Crée une session pour un utilisateur"""
    from datetime import timedelta
    
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(days=7)  # Session de 7 jours
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, ?)',
            (user_id, token, expires_at)
        )
    
    return token

def get_user_by_token(token):
    """Récupère un utilisateur par son token de session"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.* FROM users u
            JOIN sessions s ON u.id = s.user_id
            WHERE s.token = ? AND s.expires_at > ?
        ''', (token, datetime.now()))
        
        user = cursor.fetchone()
        return dict(user) if user else None

def delete_session(token):
    """Supprime une session (déconnexion)"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM sessions WHERE token = ?', (token,))

def save_signature(user_id, name, signature_data):
    """Sauvegarde une signature pour un utilisateur"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO saved_signatures (user_id, name, signature_data) VALUES (?, ?, ?)',
            (user_id, name, signature_data)
        )
        return cursor.lastrowid

def get_user_signatures(user_id):
    """Récupère toutes les signatures sauvegardées d'un utilisateur"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM saved_signatures WHERE user_id = ? ORDER BY created_at DESC',
            (user_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

def delete_signature(signature_id, user_id):
    """Supprime une signature sauvegardée"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'DELETE FROM saved_signatures WHERE id = ? AND user_id = ?',
            (signature_id, user_id)
        )
        return cursor.rowcount > 0

def add_to_history(user_id, original_filename, signed_filename, file_path, signature_page):
    """Ajoute une entrée à l'historique des signatures"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO signature_history 
               (user_id, original_filename, signed_filename, file_path, signature_page) 
               VALUES (?, ?, ?, ?, ?)''',
            (user_id, original_filename, signed_filename, file_path, signature_page)
        )
        return cursor.lastrowid

def get_user_history(user_id, limit=50):
    """Récupère l'historique des signatures d'un utilisateur"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT * FROM signature_history 
               WHERE user_id = ? 
               ORDER BY created_at DESC 
               LIMIT ?''',
            (user_id, limit)
        )
        return [dict(row) for row in cursor.fetchall()]

def clean_old_files():
    """Nettoie les fichiers non associés à un utilisateur de plus de 24h"""
    from datetime import timedelta
    
    with get_db() as conn:
        cursor = conn.cursor()
        cutoff_date = datetime.now() - timedelta(hours=24)
        
        # Récupère les fichiers à supprimer
        cursor.execute(
            '''SELECT file_path FROM signature_history 
               WHERE user_id IS NULL AND created_at < ?''',
            (cutoff_date,)
        )
        
        files_to_delete = [row['file_path'] for row in cursor.fetchall()]
        
        # Supprime les entrées de l'historique
        cursor.execute(
            'DELETE FROM signature_history WHERE user_id IS NULL AND created_at < ?',
            (cutoff_date,)
        )
        
        return files_to_delete

if __name__ == '__main__':
    # Initialise la base de données si exécuté directement
    init_db()
