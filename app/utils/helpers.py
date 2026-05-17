import os
from flask import current_app

def allowed_file(filename):
    """Verificar si la extensión del archivo está permitida"""
    if not filename:
        return False
    allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif', 'webp'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_uploaded_file(file, subfolder=''):
    """Guardar un archivo subido y devolver la URL"""
    from werkzeug.utils import secure_filename
    import secrets
    
    if not file or not allowed_file(file.filename):
        return None
    
    # Generar nombre único
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{secrets.token_hex(16)}.{ext}"
    
    upload_folder = current_app.config.get('IMG_UPLOAD_FOLDER', 'app/static/uploads')
    if subfolder:
        upload_folder = os.path.join(upload_folder, subfolder)
        os.makedirs(upload_folder, exist_ok=True)
    
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)
    
    # Devolver URL relativa
    return f"/static/uploads/{subfolder}/{filename}" if subfolder else f"/static/uploads/{filename}"