from functools import wraps

from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Namespace, Resource, fields

from ..services import auth as auth_service
from ..services import users as users_service

ns = Namespace("users", description="Gestión de usuarios (solo admin)")

user_model = ns.model("UserDetail", {
    "id":         fields.Integer(),
    "name":       fields.String(),
    "email":      fields.String(),
    "role":       fields.String(),
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
    "is_active": fields.Boolean(),
    "password":  fields.String(description="Nueva contraseña (opcional, mín. 8 caracteres)"),
})


def admin_required(fn):
    """Decorator: exige JWT válido + rol admin."""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = int(get_jwt_identity())
        try:
            user = auth_service.get_user_by_id(user_id)
        except LookupError:
            ns.abort(401, "Token inválido")
        if user.role != "admin":
            ns.abort(403, "Acceso restringido a administradores")
        return fn(*args, **kwargs)
    return wrapper


@ns.route("/")
class UserList(Resource):
    @admin_required
    @ns.marshal_with(user_list_model)
    @ns.param("page", "Número de página", type=int, default=1)
    @ns.param("per_page", "Resultados por página", type=int, default=20)
    @ns.param("role", "Filtrar por rol (admin|couple|guest)")
    def get(self):
        """Listar todos los usuarios (admin)"""
        page     = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        role     = request.args.get("role")
        return users_service.list_users(page=page, per_page=per_page, role=role)


@ns.route("/<int:user_id>")
class UserDetail(Resource):
    @admin_required
    @ns.marshal_with(user_model)
    def get(self, user_id):
        """Obtener un usuario por ID (admin)"""
        try:
            user = users_service.get_user(user_id)
        except LookupError as e:
            ns.abort(404, str(e))
        return users_service._user_dict(user)

    @admin_required
    @ns.expect(update_model, validate=False)
    @ns.marshal_with(user_model)
    def patch(self, user_id):
        """Actualizar nombre, email, rol, estado o contraseña (admin)"""
        try:
            user = users_service.update_user(user_id, request.json or {})
        except (ValueError, LookupError) as e:
            ns.abort(400, str(e))
        return users_service._user_dict(user)

    @admin_required
    def delete(self, user_id):
        """Eliminar usuario (admin, no puede eliminarse a sí mismo)"""
        requesting_id = int(get_jwt_identity())
        try:
            users_service.delete_user(user_id, requesting_id)
        except (ValueError, LookupError) as e:
            ns.abort(400, str(e))
        return {"message": "Usuario eliminado"}, 200


@ns.route("/me/profile")
class MyProfile(Resource):
    @jwt_required()
    @ns.expect(ns.model("UpdateProfile", {
        "name":     fields.String(),
        "password": fields.String(description="Mín. 8 caracteres"),
    }), validate=False)
    @ns.marshal_with(user_model)
    def patch(self):
        """Actualizar nombre o contraseña del usuario autenticado"""
        user_id = int(get_jwt_identity())
        allowed = {k: v for k, v in (request.json or {}).items() if k in ("name", "password")}
        try:
            user = users_service.update_user(user_id, allowed)
        except (ValueError, LookupError) as e:
            ns.abort(400, str(e))
        return users_service._user_dict(user)
