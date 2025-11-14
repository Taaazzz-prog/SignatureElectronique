from flask import Flask, request, jsonify, send_file, render_template, session
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import uuid
from functools import wraps
try:
    from PyPDF2 import PdfReader, PdfWriter
except ImportError:
    from PyPDF2 import PdfFileReader as PdfReader, PdfFileWriter as PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image
import io
import base64

# Import de la gestion de base de données
import database as db

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production-' + str(uuid.uuid4()))

# Configuration
UPLOAD_FOLDER = 'uploads'
SIGNED_FOLDER = 'signed'
SIGNATURE_FOLDER = 'signatures'
ALLOWED_EXTENSIONS = {'pdf'}

for folder in [UPLOAD_FOLDER, SIGNED_FOLDER, SIGNATURE_FOLDER]:
    os.makedirs(folder, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Initialiser la base de données
db.init_db()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_current_user():
    """Récupère l'utilisateur actuel depuis le token dans les headers"""
    token = request.headers.get('Authorization')
    if token and token.startswith('Bearer '):
        token = token[7:]  # Remove 'Bearer ' prefix
        return db.get_user_by_token(token)
    return None

def login_optional(f):
    """Décorateur pour les routes où la connexion est optionnelle"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        request.current_user = get_current_user()
        return f(*args, **kwargs)
    return decorated_function

def login_required(f):
    """Décorateur pour les routes nécessitant une authentification"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentification requise'}), 401
        request.current_user = user
        return f(*args, **kwargs)
    return decorated_function

# ============================================
# ROUTES D'AUTHENTIFICATION
# ============================================

@app.route('/api/register', methods=['POST'])
def register():
    """Inscription d'un nouvel utilisateur"""
    data = request.get_json()
    
    email = data.get('email', '').strip()
    password = data.get('password', '')
    name = data.get('name', '').strip() if data.get('name') else None
    
    if not email or not password:
        return jsonify({'error': 'Email et mot de passe requis'}), 400
    
    try:
        user_id = db.create_user(email, password, name)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    
    if not user_id:
        return jsonify({'error': 'Cet email est déjà utilisé'}), 409
    
    # Créer une session automatiquement
    token = db.create_session(user_id)
    
    return jsonify({
        'success': True,
        'token': token,
        'message': 'Compte créé avec succès'
    })

@app.route('/api/login', methods=['POST'])
def login():
    """Connexion d'un utilisateur"""
    data = request.get_json()
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email et mot de passe requis'}), 400
    
    user = db.authenticate_user(email, password)
    
    if not user:
        return jsonify({'error': 'Email ou mot de passe incorrect'}), 401
    
    # Créer une session
    token = db.create_session(user['id'])
    
    return jsonify({
        'success': True,
        'token': token,
        'user': {
            'id': user['id'],
            'email': user['email'],
            'name': user['name']
        }
    })

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    """Déconnexion d'un utilisateur"""
    token = request.headers.get('Authorization', '')[7:]
    db.delete_session(token)
    
    return jsonify({'success': True, 'message': 'Déconnecté avec succès'})

@app.route('/api/me', methods=['GET'])
@login_required
def get_current_user_info():
    """Récupère les informations de l'utilisateur connecté"""
    user = request.current_user
    
    return jsonify({
        'id': user['id'],
        'email': user['email'],
        'name': user['name'],
        'created_at': user['created_at']
    })

# ============================================
# ROUTES PRINCIPALES (accessibles sans compte)
# ============================================

@app.route('/')
def index():
    """Page d'accueil - Upload et signature de PDF"""
    return render_template('index_new.html')

@app.route('/signatures')
def signatures_page():
    """Page de gestion des signatures"""
    return render_template('signatures.html')

@app.route('/history')
def history_page():
    """Page d'historique des documents signés"""
    return render_template('history.html')

@app.route('/account')
def account_page():
    """Page de gestion du compte utilisateur"""
    return render_template('account.html')

@app.route('/api/upload', methods=['POST'])
@login_optional
def upload_file():
    """Upload un fichier PDF"""
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier fourni'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nom de fichier vide'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        # Obtenir le nombre de pages
        pdf_reader = PdfReader(filepath)
        num_pages = len(pdf_reader.pages)
        
        return jsonify({
            'success': True,
            'file_id': unique_filename,
            'filename': filename,
            'num_pages': num_pages
        })
    
    return jsonify({'error': 'Type de fichier non autorisé'}), 400

@app.route('/api/sign', methods=['POST'])
@login_optional
def sign_pdf():
    """Ajoute une signature au PDF"""
    data = request.get_json()
    
    file_id = data.get('file_id')
    signature_data = data.get('signature')  # Base64 image data
    position = data.get('position', {})
    page_num = data.get('page', 0)
    
    if not file_id or not signature_data:
        return jsonify({'error': 'Données manquantes'}), 400
    
    try:
        # Chemins des fichiers
        input_path = os.path.join(UPLOAD_FOLDER, file_id)
        if not os.path.exists(input_path):
            return jsonify({'error': 'Fichier non trouvé'}), 404
        
        # Sauvegarder la signature
        signature_filename = f"{uuid.uuid4()}.png"
        signature_path = os.path.join(SIGNATURE_FOLDER, signature_filename)
        
        # Décoder l'image base64
        image_data = signature_data.split(',')[1] if ',' in signature_data else signature_data
        image_bytes = base64.b64decode(image_data)
        
        with open(signature_path, 'wb') as f:
            f.write(image_bytes)
        
        # Créer le PDF avec la signature
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        
        # Position de la signature (par défaut en bas à droite)
        x = position.get('x', 400)
        y = position.get('y', 50)
        width = position.get('width', 150)
        height = position.get('height', 75)
        
        can.drawImage(signature_path, x, y, width=width, height=height, mask='auto')
        can.save()
        
        # Fusionner avec le PDF original
        packet.seek(0)
        signature_pdf = PdfReader(packet)
        existing_pdf = PdfReader(input_path)
        output = PdfWriter()
        
        for i, page in enumerate(existing_pdf.pages):
            if i == page_num:
                page.merge_page(signature_pdf.pages[0])
            output.add_page(page)
        
        # Sauvegarder le PDF signé
        signed_filename = f"signed_{file_id}"
        signed_path = os.path.join(SIGNED_FOLDER, signed_filename)
        
        with open(signed_path, 'wb') as output_file:
            output.write(output_file)
        
        # Nettoyer
        os.remove(signature_path)
        
        # Ajouter à l'historique si l'utilisateur est connecté
        user_id = None
        if hasattr(request, 'current_user') and request.current_user:
            user_id = request.current_user['id']
        
        original_filename = file_id.split('_', 1)[1] if '_' in file_id else file_id
        db.add_to_history(user_id, original_filename, signed_filename, signed_path, page_num)
        
        return jsonify({
            'success': True,
            'signed_file_id': signed_filename,
            'message': 'PDF signé avec succès'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<file_id>')
def download_file(file_id):
    """Télécharge le PDF signé"""
    filepath = os.path.join(SIGNED_FOLDER, file_id)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'Fichier non trouvé'}), 404
    
    original_name = file_id.replace('signed_', '').split('_', 1)[1]
    download_name = f"signed_{original_name}"
    
    return send_file(filepath, as_attachment=True, download_name=download_name)

@app.route('/api/preview/<file_id>/<int:page>')
def preview_page(file_id, page):
    """Génère une prévisualisation d'une page du PDF"""
    try:
        filepath = os.path.join(UPLOAD_FOLDER, file_id)
        if not os.path.exists(filepath):
            return jsonify({'error': 'Fichier non trouvé'}), 404
        
        # Note: Pour une vraie prévisualisation, il faudrait pdf2image
        # Cette version retourne juste un message de succès
        return jsonify({'success': True, 'message': 'Prévisualisation disponible'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# ROUTES POUR UTILISATEURS CONNECTÉS
# ============================================

@app.route('/api/signatures/save', methods=['POST'])
@login_required
def save_signature_route():
    """Sauvegarde une signature pour réutilisation"""
    data = request.get_json()
    
    name = data.get('name')
    signature_data = data.get('signature')
    
    if not name or not signature_data:
        return jsonify({'error': 'Nom et signature requis'}), 400
    
    user_id = request.current_user['id']
    signature_id = db.save_signature(user_id, name, signature_data)
    
    return jsonify({
        'success': True,
        'signature_id': signature_id,
        'message': 'Signature sauvegardée avec succès'
    })

@app.route('/api/signatures', methods=['GET'])
@login_required
def get_signatures():
    """Récupère toutes les signatures sauvegardées de l'utilisateur"""
    user_id = request.current_user['id']
    signatures = db.get_user_signatures(user_id)
    
    return jsonify({'signatures': signatures})

@app.route('/api/signatures/<int:signature_id>', methods=['DELETE'])
@login_required
def delete_signature_route(signature_id):
    """Supprime une signature sauvegardée"""
    user_id = request.current_user['id']
    success = db.delete_signature(signature_id, user_id)
    
    if success:
        return jsonify({'success': True, 'message': 'Signature supprimée'})
    return jsonify({'error': 'Signature non trouvée'}), 404

@app.route('/api/history', methods=['GET'])
@login_required
def get_history():
    """Récupère l'historique des signatures de l'utilisateur"""
    user_id = request.current_user['id']
    limit = request.args.get('limit', 50, type=int)
    
    history = db.get_user_history(user_id, limit)
    
    return jsonify({'history': history})

@app.route('/api/history/<int:history_id>/download', methods=['GET'])
@login_required
def download_from_history(history_id):
    """Télécharge un PDF depuis l'historique"""
    user_id = request.current_user['id']
    
    # Récupérer l'entrée de l'historique
    history = db.get_user_history(user_id, limit=1000)
    entry = next((h for h in history if h['id'] == history_id), None)
    
    if not entry:
        return jsonify({'error': 'Fichier non trouvé'}), 404
    
    filepath = entry['file_path']
    if not os.path.exists(filepath):
        return jsonify({'error': 'Fichier non trouvé sur le serveur'}), 404
    
    return send_file(filepath, as_attachment=True, download_name=entry['signed_filename'])

@app.route('/api/history', methods=['DELETE'])
@login_required
def delete_all_history():
    """Supprime tout l'historique de l'utilisateur"""
    user_id = request.current_user['id']
    
    success = db.delete_user_history(user_id)
    if success:
        return jsonify({'success': True, 'message': 'Historique supprimé'})
    return jsonify({'error': 'Erreur lors de la suppression'}), 500

@app.route('/api/account', methods=['DELETE'])
@login_required
def delete_account():
    """Supprime le compte utilisateur et toutes ses données"""
    user_id = request.current_user['id']
    
    # Supprimer toutes les données de l'utilisateur
    success = db.delete_user(user_id)
    if success:
        return jsonify({'success': True, 'message': 'Compte supprimé'})
    return jsonify({'error': 'Erreur lors de la suppression'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
