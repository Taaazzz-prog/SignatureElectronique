from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import uuid
try:
    from PyPDF2 import PdfReader, PdfWriter
except ImportError:
    from PyPDF2 import PdfFileReader as PdfReader, PdfFileWriter as PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image
import io
import base64

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
SIGNED_FOLDER = 'signed'
SIGNATURE_FOLDER = 'signatures'
ALLOWED_EXTENSIONS = {'pdf'}

for folder in [UPLOAD_FOLDER, SIGNED_FOLDER, SIGNATURE_FOLDER]:
    os.makedirs(folder, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
