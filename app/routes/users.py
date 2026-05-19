from functools import wraps

from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Namespace, Resource, fields

from ..services import users as users_service

ns = Namespace("users", description="Gestión de usuarios (solo admin)")

user_model = ns.model("UserDetail", {
    "id":         fields.Integer(),
    "name":       fields.String(),
    "email":      fields.String(),
    "role":       fields.String(),
    "rol_id":     fields.Integer(),
    "is_active":  fields.Boolean(),
    "created_at": fields.String(),
})
user_list_model = ns.model("UserList", {
    "items":    fields.List(fields.Nested(user_model)),
    "total":    fields.Integer(),
    "page":     fields.Integer(),
    "pages":    fields.Integer(),
    "per_page": fields.Integer(),
})
update_model = ns.model("UpdateUser", {
    "name":      fields.String(),
    "email":     fields.String(),
    "role":      fields.String(description="admin | couple | guest"),
    "rol_id":    fields.Integer(description="1=admin, 2=usuario"),
    "is_active": fields.Boolean(),
    "password":  fields.String(description="Nueva contraseña (opcional, mín. 8 caracteres)"),
})

def _to_frontend(d: dict) -> dict:
    """Convierte dict del servicio (campos ES) al formato que espera el frontend."""
    rol_id = d.get("rol_id")
    return {
        "id":         d.get("id"),
        "name":       d.get("nombre"),
        "email":      d.get("email"),
        "role":       "admin" if rol_id == 1 else "user",
        "rol_id":     rol_id,
        "rol_nombre": d.get("rol"),
        "is_active":  d.get("activo", True),
        "created_at": d.get("fecha_registro"),
    }


def _to_service(payload: dict) -> dict:
    """Convierte payload del frontend a campos que acepta el servicio."""
    data: dict = {}
    if "name" in payload:
        data["nombre"] = payload["name"]
    if "email" in payload:
        data["email"] = payload["email"]
    if "is_active" in payload:
        data["activo"] = payload["is_active"]
    if "password" in payload:
        data["password"] = payload["password"]
    if "rol_id" in payload:
        data["rol_id"] = int(payload["rol_id"])
    elif "role" in payload:
        data["rol_id"] = 1 if payload["role"] == "admin" else 2
    return data


def admin_required(fn):
    """Decorator: exige JWT válido + rol admin (rol_id == 1)."""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = int(get_jwt_identity())
        try:
            user = users_service.get_user(user_id)
        except LookupError:
            ns.abort(401, "Token inválido")
        if user.rol_id != 1:
            ns.abort(403, "Acceso restringido a administradores")
        return fn(*args, **kwargs)
    return wrapper


@ns.route("/")
class UserList(Resource):
    @admin_required
    @ns.param("page", "Número de página", type=int, default=1)
    @ns.param("per_page", "Resultados por página", type=int, default=20)
    @ns.param("role", "Filtrar por rol (admin|couple|guest)")
    def get(self):
        """Listar todos los usuarios (admin)"""
        page     = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        role     = request.args.get("role")
        rol_id   = ROL_TO_ID.get(role) if role else None
        result   = users_service.list_users(page=page, per_page=per_page, rol_id=rol_id)
        result["items"] = [_to_frontend(u) for u in result["items"]]
        return result, 200


@ns.route("/<int:user_id>")
class UserDetail(Resource):
    @admin_required
    def get(self, user_id):
        """Obtener un usuario por ID (admin)"""
        try:
            user = users_service.get_user(user_id)
        except LookupError as e:
            return {"message": str(e)}, 404
        return _to_frontend(users_service._user_dict(user)), 200

    @admin_required
    @ns.expect(update_model, validate=False)
    def patch(self, user_id):
        """Actualizar nombre, email, rol, estado o contraseña (admin)"""
        try:
            payload = _to_service(request.json or {})
            user = users_service.update_user(user_id, payload)
        except (ValueError, LookupError) as e:
            return {"message": str(e)}, 400
        return _to_frontend(users_service._user_dict(user)), 200

    @admin_required
    def delete(self, user_id):
        """Eliminar usuario (admin, no puede eliminarse a sí mismo)"""
        requesting_id = int(get_jwt_identity())
        try:
            users_service.delete_user(user_id, requesting_id)
        except (ValueError, LookupError) as e:
            return {"message": str(e)}, 400
        return {"message": "Usuario eliminado"}, 200


@ns.route("/me/profile")
class MyProfile(Resource):
    @jwt_required()
    def patch(self):
        """Actualizar nombre o contraseña del usuario autenticado"""
        user_id = int(get_jwt_identity())
        raw = {k: v for k, v in (request.json or {}).items() if k in ("name", "password")}
        payload = _to_service(raw)
        try:
            user = users_service.update_user(user_id, payload)
        except (ValueError, LookupError) as e:
            return {"message": str(e)}, 400
        return _to_frontend(users_service._user_dict(user)), 200
