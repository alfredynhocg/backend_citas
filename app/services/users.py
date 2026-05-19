from ..extensions import bcrypt, db
from ..models import User, Role

VALID_ROLES = {1: "administrador", 2: "usuario_normal"}


def list_users(page: int = 1, per_page: int = 20, rol_id: int | None = None) -> dict:
    q = User.query
    if rol_id:
        q = q.filter_by(rol_id=rol_id)
    pagination = q.order_by(User.fecha_registro.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return {
        "items": [_user_dict(u) for u in pagination.items],
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages,
        "per_page": pagination.per_page,
    }


def get_user(user_id: int) -> User:
    user = db.session.get(User, user_id)
    if not user:
        raise LookupError("Usuario no encontrado")
    return user


def update_user(user_id: int, data: dict) -> User:
    user = get_user(user_id)

    if "nombre" in data and data["nombre"]:
        user.nombre = data["nombre"].strip()

    if "email" in data and data["email"]:
        email = data["email"].lower().strip()
        conflict = User.query.filter_by(email=email).first()
        if conflict and conflict.id != user_id:
            raise ValueError("El email ya está en uso")
        user.email = email

    if "rol_id" in data:
        if data["rol_id"] not in VALID_ROLES:
            raise ValueError(f"Rol inválido. Opciones: {list(VALID_ROLES.keys())}")
        user.rol_id = data["rol_id"]

    if "activo" in data:
        user.activo = bool(data["activo"])

    if "password" in data and data["password"]:
        if len(data["password"]) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        user.password_hash = bcrypt.generate_password_hash(data["password"]).decode("utf-8")

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    return user


def delete_user(user_id: int, requesting_user_id: int) -> None:
    if user_id == requesting_user_id:
        raise ValueError("No puedes eliminar tu propia cuenta")
    user = get_user(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


def _user_dict(user: User) -> dict:
    return {
        "id":             user.id,
        "nombre":         user.nombre,
        "email":          user.email,
        "rol_id":         user.rol_id,
        "rol":            user.rol.nombre if user.rol else None,
        "activo":         user.activo,
        "fecha_registro": user.fecha_registro.isoformat() if user.fecha_registro else None,
    }
