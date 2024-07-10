from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from cryptography.fernet import Fernet, InvalidToken
from . import db
from .models import File
import os
import io
import logging

views = Blueprint('views', __name__)

# Use an absolute path for the upload folder
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

# Load or generate the encryption key
key_path = os.path.join(BASE_DIR, 'secret.key')
if os.path.exists(key_path):
    with open(key_path, 'rb') as key_file:
        key = key_file.read()
else:
    key = Fernet.generate_key()
    with open(key_path, 'wb') as key_file:
        key_file.write(key)
cipher = Fernet(key)

def allowed_file(filename):
    logging.debug(f"Checking if file allowed: {filename}")
    return True

@views.route('/')
def home():
    return render_template("home.html")

@views.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        logging.debug("POST request received for file upload")

        if 'file' not in request.files:
            flash('No file part')
            logging.debug("No file part in request")
            return redirect(request.url)
        
        file = request.files['file']
        logging.debug(f"File received: {file.filename}")

        if file.filename == '':
            flash('No selected file')
            logging.debug("No selected file")
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            logging.debug(f"Secure filename: {filename}")

            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
                logging.debug(f"Created upload folder at {UPLOAD_FOLDER}")
            
            file_data = file.read()
            encrypted_data = cipher.encrypt(file_data)
            logging.debug("File encrypted")

            with open(os.path.join(UPLOAD_FOLDER, filename), 'wb') as f:
                f.write(encrypted_data)
                logging.debug(f"File written to {os.path.join(UPLOAD_FOLDER, filename)}")
            
            new_file = File(filename=filename, user_id=current_user.id)
            db.session.add(new_file)
            db.session.commit()
            logging.debug(f"File {filename} added to database")

            flash(f'File {filename} successfully uploaded')
            return redirect(url_for('views.upload_file'))
        else:
            flash('File type not allowed')
            logging.debug(f"File type not allowed for file: {file.filename}")
            return redirect(request.url)
    
    uploaded_files = File.query.filter_by(user_id=current_user.id).all()
    return render_template('upload.html', files=uploaded_files)

@views.route('/download/<int:file_id>')
@login_required
def download_file(file_id):
    file = File.query.get_or_404(file_id)
    if file.user_id != current_user.id:
        flash('You do not have permission to access this file')
        return redirect(url_for('views.upload_file'))

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    if os.path.exists(file_path):
        try:
            with open(file_path, 'rb') as f:
                encrypted_data = f.read()
            decrypted_data = cipher.decrypt(encrypted_data)
            
            return send_file(
                io.BytesIO(decrypted_data),
                mimetype='application/octet-stream',
                as_attachment=True,
                download_name=file.filename
            )
        except InvalidToken:
            flash('Decryption failed. Invalid token.')
            return redirect(url_for('views.upload_file'))
    else:
        flash('File not found')
        return redirect(url_for('views.upload_file'))

@views.route('/delete/<int:file_id>', methods=['POST'])
@login_required
def delete_file(file_id):
    file = File.query.get_or_404(file_id)
    if file.user_id != current_user.id:
        flash('You do not have permission to delete this file')
        return redirect(url_for('views.upload_file'))
    
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    db.session.delete(file)
    db.session.commit()
    flash(f'File {file.filename} successfully deleted')
    return redirect(url_for('views.upload_file'))
