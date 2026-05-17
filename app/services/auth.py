import re

from flask_jwt_extended import create_access_token, create_refresh_token

from ..extensions import bcrypt, db
from ..models import User


def register_user(name: str, email: str, password: str) -> dict:
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        raise ValueError("Email inválido")
    if len(password) < 4:
        raise ValueError("La contraseña debe tener al menos 8 caracteres")
    if User.query.filter_by(email=email).first():
        raise ValueError("El email ya está registrado")

    user = User(
        nombre=name.strip(),
        email=email.lower().strip(),
        password_hash=bcrypt.generate_password_hash(password).decode("utf-8"),
    )
    db.session.add(user)
    db.session.commit()
    return _tokens(user)


def login_user(email: str, password: str) -> dict:
    user = User.query.filter_by(email=email.lower().strip()).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        raise ValueError("Credenciales incorrectas")
    return _tokens(user)


def get_user_by_id(user_id: int) -> User:
    user = db.session.get(User, user_id)
    if not user:
        raise LookupError("Usuario no encontrado")
    return user


def refresh_token(user_id: int) -> str:
    return create_access_token(identity=str(user_id))


def _tokens(user: User) -> dict:
    return {
        "access_token":  create_access_token(identity=str(user.id)),
        "refresh_token": create_refresh_token(identity=str(user.id)),
        "user": _user_dict(user),
    }


def _user_dict(user: User) -> dict:
    return {
        "id": user.id,
        "nombre": user.nombre,
        "email": user.email,
        "rol_id": user.rol_id,
        "activo": user.activo,
        "fecha_registro": user.fecha_registro.isoformat() if user.fecha_registro else None,
    }
