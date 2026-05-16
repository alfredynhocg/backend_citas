from ..extensions import bcrypt, db
from ..models import User

VALID_ROLES = {"admin", "couple", "guest"}


def list_users(page: int = 1, per_page: int = 20, role: str | None = None) -> dict:
    q = User.query
    if role:
        q = q.filter_by(role=role)
    pagination = q.order_by(User.created_at.desc()).paginate(
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

    if "name" in data and data["name"]:
        user.name = data["name"].strip()

    if "email" in data and data["email"]:
        email = data["email"].lower().strip()
        conflict = User.query.filter_by(email=email).first()
        if conflict and conflict.id != user_id:
            raise ValueError("El email ya está en uso")
        user.email = email

    if "role" in data:
        if data["role"] not in VALID_ROLES:
            raise ValueError(f"Rol inválido. Opciones: {', '.join(VALID_ROLES)}")
        user.role = data["role"]

    if "is_active" in data:
        user.is_active = bool(data["is_active"])

    if "password" in data and data["password"]:
        if len(data["password"]) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        user.password_hash = bcrypt.generate_password_hash(data["password"]).decode("utf-8")

    db.session.commit()
    return user


def delete_user(user_id: int, requesting_user_id: int) -> None:
    if user_id == requesting_user_id:
        raise ValueError("No puedes eliminar tu propia cuenta")
    user = get_user(user_id)
    db.session.delete(user)
    db.session.commit()


def _user_dict(user: User) -> dict:
    return {
        "id":         user.id,
        "name":       user.name,
        "email":      user.email,
        "role":       user.role,
        "is_active":  user.is_active,
        "created_at": user.created_at.isoformat(),
    }
