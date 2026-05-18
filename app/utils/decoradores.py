# app/utils/decoradores.py
from functools import wraps
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from flask import jsonify
from ..models import User

def admin_requerido(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            usuario_id = get_jwt_identity()
            usuario = User.query.get(usuario_id)
            if not usuario or usuario.rol_id != 1:
                return {'error': 'Acceso denegado. Se requieren permisos de administrador'}, 403
            return f(*args, **kwargs)
        except Exception as e:
            return {'error': 'Token inválido o expirado'}, 401
    return decorated_function