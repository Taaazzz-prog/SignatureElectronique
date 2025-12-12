from flask import Flask, request, jsonify, send_file, render_template, session
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import uuid
from functools import wraps
import requests  # Pour vérifier reCAPTCHA
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

# Import du helper pour secrets Docker
from secrets_helper import read_secret, get_secret_or_default

# Import de la signature électronique
from digital_signature import get_digital_signer

# Import de l'API Goodflag
from goodflag_api import get_goodflag_client

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Lire les secrets Docker Swarm (ou variables d'env en dev)
app.secret_key = get_secret_or_default(
    'signature_secret_key',
    default_value='dev-secret-key-change-in-production-' + str(uuid.uuid4()),
    env_var_name='SECRET_KEY'
)

# Configuration reCAPTCHA depuis secret Docker
RECAPTCHA_SECRET_KEY = get_secret_or_default(
    'signature_recaptcha_key',
    default_value='',
    env_var_name='RECAPTCHA_SECRET_KEY'
)

def verify_recaptcha(token):
    """Vérifie le token reCAPTCHA v3"""
    if not RECAPTCHA_SECRET_KEY:
        # Si pas de clé configurée, on accepte (mode dev)
        return True
    
    try:
        response = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data={
                'secret': RECAPTCHA_SECRET_KEY,
                'response': token
            },
            timeout=5
        )
        result = response.json()
        
        # reCAPTCHA v3 retourne un score de 0.0 à 1.0
        # Score > 0.5 = probablement humain
        # Score < 0.5 = probablement bot
        if result.get('success') and result.get('score', 0) >= 0.5:
            return True
        
        print(f"reCAPTCHA failed: score={result.get('score', 0)}")
        return False
    except Exception as e:
        print(f"Erreur vérification reCAPTCHA: {e}")
        # En cas d'erreur, on accepte pour ne pas bloquer les vrais users
        return True

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
    
    # Vérification reCAPTCHA
    recaptcha_token = data.get('recaptcha_token')
    if not verify_recaptcha(recaptcha_token):
        return jsonify({'error': 'Vérification anti-bot échouée. Veuillez réessayer.'}), 403
    
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
    
    # Vérification reCAPTCHA (optionnelle sur login, mais recommandée)
    recaptcha_token = data.get('recaptcha_token')
    if recaptcha_token and not verify_recaptcha(recaptcha_token):
        return jsonify({'error': 'Vérification anti-bot échouée. Veuillez réessayer.'}), 403
    
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
    """Ajoute une signature électronique certifiée au PDF"""
    data = request.get_json()
    
    file_id = data.get('file_id')
    signature_data = data.get('signature')  # Base64 image data (optionnel, pour apparence visuelle)
    position = data.get('position', {})
    page_num = data.get('page', 0)
    
    if not file_id:
        return jsonify({'error': 'Fichier manquant'}), 400
    
    try:
        # Chemins des fichiers
        input_path = os.path.join(UPLOAD_FOLDER, file_id)
        if not os.path.exists(input_path):
            return jsonify({'error': 'Fichier non trouvé'}), 404
        
        # Préparer le PDF avec signature visuelle d'abord (si fournie)
        temp_visual_path = None
        if signature_data:
            # Sauvegarder la signature visuelle
            signature_filename = f"{uuid.uuid4()}.png"
            signature_path = os.path.join(SIGNATURE_FOLDER, signature_filename)
            
            # Décoder l'image base64
            image_data = signature_data.split(',')[1] if ',' in signature_data else signature_data
            image_bytes = base64.b64decode(image_data)
            
            with open(signature_path, 'wb') as f:
                f.write(image_bytes)
            
            # Créer le PDF avec la signature visuelle
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)
            
            # Position de la signature
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
            
            # Sauvegarder le PDF avec signature visuelle temporaire
            temp_visual_path = os.path.join(UPLOAD_FOLDER, f"temp_visual_{file_id}")
            with open(temp_visual_path, 'wb') as output_file:
                output.write(output_file)
            
            # Nettoyer l'image de signature
            os.remove(signature_path)
            
            # Utiliser ce PDF pour la signature électronique
            input_for_digital = temp_visual_path
        else:
            input_for_digital = input_path
        
        # Maintenant ajouter la signature électronique certifiée
        signed_filename = f"signed_{file_id}"
        signed_path = os.path.join(SIGNED_FOLDER, signed_filename)
        
        # Obtenir le signataire
        digital_signer = get_digital_signer()
        
        # Signer électroniquement le PDF
        success, message = digital_signer.sign_pdf(
            input_path=input_for_digital,
            output_path=signed_path,
            reason="Document signé électroniquement",
            location="France",
            visible=False,  # Signature invisible (la signature visuelle est déjà ajoutée)
            page_num=None,
            position=None
        )
        
        # Nettoyer le fichier temporaire si créé
        if temp_visual_path and os.path.exists(temp_visual_path):
            os.remove(temp_visual_path)
        
        if not success:
            return jsonify({'error': message}), 500
        
        # Ajouter à l'historique si l'utilisateur est connecté
        user_id = None
        if hasattr(request, 'current_user') and request.current_user:
            user_id = request.current_user['id']
        
        original_filename = file_id.split('_', 1)[1] if '_' in file_id else file_id
        db.add_to_history(user_id, original_filename, signed_filename, signed_path, page_num)
        
        return jsonify({
            'success': True,
            'signed_file_id': signed_filename,
            'message': 'PDF signé électroniquement avec succès',
            'signature_type': 'digital_certified'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sign-digital', methods=['POST'])
def sign_pdf_digitally():
    """Ajoute une signature électronique certifiée au PDF"""
    data = request.get_json()
    
    file_id = data.get('file_id')
    signature_data = data.get('signature')  # Image de signature (optionnel pour visible)
    position = data.get('position', {})
    page_num = data.get('page')
    reason = data.get('reason', 'Document signé électroniquement')
    location = data.get('location', 'France')
    visible = data.get('visible', True)
    
    if not file_id:
        return jsonify({'error': 'Fichier manquant'}), 400
    
    try:
        # Chemins des fichiers
        input_path = os.path.join(UPLOAD_FOLDER, file_id)
        if not os.path.exists(input_path):
            return jsonify({'error': 'Fichier non trouvé'}), 404
        
        # Sauvegarder le PDF signé
        signed_filename = f"signed_digital_{file_id}"
        signed_path = os.path.join(SIGNED_FOLDER, signed_filename)
        
        # Obtenir le signataire
        digital_signer = get_digital_signer()
        
        # Préparer la position si signature visible
        position_tuple = None
        if visible and position:
            x = position.get('x', 400)
            y = position.get('y', 50)
            width = position.get('width', 150)
            height = position.get('height', 75)
            position_tuple = (x, y, width, height)
        
        # Signer le PDF
        success, message = digital_signer.sign_pdf(
            input_path=input_path,
            output_path=signed_path,
            reason=reason,
            location=location,
            visible=visible,
            page_num=page_num,
            position=position_tuple
        )
        
        if not success:
            return jsonify({'error': message}), 500
        
        # Ajouter à l'historique si l'utilisateur est connecté
        user_id = None
        if hasattr(request, 'current_user') and request.current_user:
            user_id = request.current_user['id']
        
        original_filename = file_id.split('_', 1)[1] if '_' in file_id else file_id
        db.add_to_history(user_id, original_filename, signed_filename, signed_path, page_num)
        
        return jsonify({
            'success': True,
            'signed_file_id': signed_filename,
            'message': message,
            'signature_type': 'digital'
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

@app.route('/api/verify-signature/<file_id>', methods=['GET'])
def verify_signature(file_id):
    """Vérifie les signatures électroniques d'un PDF"""
    try:
        # Chercher d'abord dans les fichiers signés, puis dans uploads
        filepath = os.path.join(SIGNED_FOLDER, file_id)
        if not os.path.exists(filepath):
            filepath = os.path.join(UPLOAD_FOLDER, file_id)
            if not os.path.exists(filepath):
                return jsonify({'error': 'Fichier non trouvé'}), 404
        
        digital_signer = get_digital_signer()
        success, result = digital_signer.verify_signature(filepath)
        
        if success:
            return jsonify({
                'success': True,
                'signatures': result,
                'count': len(result)
            })
        else:
            return jsonify({'error': result}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sign-goodflag', methods=['POST'])
@login_optional
def sign_with_goodflag():
    """Signe un PDF avec l'API Goodflag (signature qualifiée eIDAS)"""
    data = request.get_json()
    
    file_id = data.get('file_id')
    signature_data = data.get('signature')
    position = data.get('position', {})
    page_num = data.get('page', 0)
    signer_email = data.get('signer_email')
    signer_name = data.get('signer_name', 'Utilisateur')
    
    if not file_id:
        return jsonify({'error': 'Fichier manquant'}), 400
    
    try:
        goodflag = get_goodflag_client()
        if not goodflag.is_configured():
            return jsonify({'error': 'API Goodflag non configurée'}), 503
        
        input_path = os.path.join(UPLOAD_FOLDER, file_id)
        if not os.path.exists(input_path):
            return jsonify({'error': 'Fichier non trouvé'}), 404
        
        # Ajouter signature visuelle si fournie
        temp_visual_path = None
        if signature_data:
            signature_filename = f"{uuid.uuid4()}.png"
            signature_path = os.path.join(SIGNATURE_FOLDER, signature_filename)
            
            image_data = signature_data.split(',')[1] if ',' in signature_data else signature_data
            image_bytes = base64.b64decode(image_data)
            
            with open(signature_path, 'wb') as f:
                f.write(image_bytes)
            
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)
            
            x = position.get('x', 400)
            y = position.get('y', 50)
            width = position.get('width', 150)
            height = position.get('height', 75)
            
            can.drawImage(signature_path, x, y, width=width, height=height, mask='auto')
            can.save()
            
            packet.seek(0)
            signature_pdf = PdfReader(packet)
            existing_pdf = PdfReader(input_path)
            output = PdfWriter()
            
            for i, page in enumerate(existing_pdf.pages):
                if i == page_num:
                    page.merge_page(signature_pdf.pages[0])
                output.add_page(page)
            
            temp_visual_path = os.path.join(UPLOAD_FOLDER, f"temp_visual_{file_id}")
            with open(temp_visual_path, 'wb') as output_file:
                output.write(output_file)
            
            os.remove(signature_path)
            input_for_goodflag = temp_visual_path
        else:
            input_for_goodflag = input_path
        
        # Email du signataire
        if not signer_email and hasattr(request, 'current_user') and request.current_user:
            signer_email = request.current_user.get('email', 'user@example.com')
            signer_name = request.current_user.get('name', signer_name)
        elif not signer_email:
            signer_email = 'user@example.com'
        
        # Signer avec Goodflag
        success, result = goodflag.sign_document_server_side(
            document_path=input_for_goodflag,
            signer_email=signer_email,
            signer_name=signer_name
        )
        
        if temp_visual_path and os.path.exists(temp_visual_path):
            os.remove(temp_visual_path)
        
        if not success:
            return jsonify({'error': result}), 500
        
        # Déplacer vers signed/
        signed_filename = f"signed_goodflag_{file_id}"
        signed_path = os.path.join(SIGNED_FOLDER, signed_filename)
        
        if os.path.exists(result['signed_path']):
            os.rename(result['signed_path'], signed_path)
        
        # Historique
        user_id = None
        if hasattr(request, 'current_user') and request.current_user:
            user_id = request.current_user['id']
        
        original_filename = file_id.split('_', 1)[1] if '_' in file_id else file_id
        db.add_to_history(user_id, original_filename, signed_filename, signed_path, page_num)
        
        return jsonify({
            'success': True,
            'signed_file_id': signed_filename,
            'message': '✅ Signé avec Goodflag (eIDAS qualifié)',
            'signature_type': 'goodflag_qualified'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/goodflag/status', methods=['GET'])
def goodflag_status():
    """Vérifie si l'API Goodflag est configurée"""
    try:
        goodflag = get_goodflag_client()
        
        if not goodflag.is_configured():
            return jsonify({
                'configured': False,
                'available': False,
                'message': 'Non configurée'
            })
        
        success, message = goodflag.test_connection()
        
        return jsonify({
            'configured': True,
            'available': success,
            'message': message
        })
        
    except Exception as e:
        return jsonify({
            'configured': False,
            'available': False,
            'error': str(e)
        })
    
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
