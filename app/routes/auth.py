from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Namespace, Resource, fields

from ..services import auth as auth_service

ns = Namespace("auth", description="Registro, login y perfil")


# =========================
# MODELOS SWAGGER
# =========================

register_model = ns.model("Register", {
    "name": fields.String(required=True),
    "email": fields.String(required=True),
    "password": fields.String(required=True),
})

login_model = ns.model("Login", {
    "email": fields.String(required=True),
    "password": fields.String(required=True),
})

user_model = ns.model("User", {
    "id": fields.Integer(),
    "nombre": fields.String(),
    "email": fields.String(),
    "rol_id": fields.Integer(),
    "activo": fields.Boolean(),
    "fecha_registro": fields.String(),
})

tokens_model = ns.model("Tokens", {
    "access_token": fields.String(),
    "refresh_token": fields.String(),
    "user": fields.Nested(user_model),
})

access_model = ns.model("AccessToken", {
    "access_token": fields.String(),
})


# =========================
# REGISTER
# =========================

@ns.route("/register")
class Register(Resource):

    @ns.expect(register_model, validate=True)
    @ns.marshal_with(tokens_model, code=201)
    def post(self):
        """Registrar nuevo usuario"""

        body = request.json

        try:
            result = auth_service.register_user(
                body["name"],
                body["email"],
                body["password"]
            )

        except ValueError as e:
            ns.abort(400, str(e))

        return result, 201


# =========================
# LOGIN
# =========================

@ns.route("/login")
class Login(Resource):

    @ns.expect(login_model, validate=True)
    @ns.marshal_with(tokens_model)
    def post(self):
        """Iniciar sesión"""

        body = request.json

        try:
            result = auth_service.login_user(
                body["email"],
                body["password"]
            )

        except ValueError as e:
            ns.abort(401, str(e))

        return result


# =========================
# PERFIL
# =========================

@ns.route("/me")
class Me(Resource):

    @jwt_required()
    @ns.marshal_with(user_model)
    def get(self):
        """Perfil del usuario autenticado"""

        user_id = int(get_jwt_identity())

        try:
            user = auth_service.get_user_by_id(user_id)

        except LookupError as e:
            ns.abort(404, str(e))

        return {
            "id": user.id,
            "nombre": user.nombre,
            "email": user.email,
            "rol_id": user.rol_id,
            "activo": user.activo,
            "fecha_registro": user.fecha_registro.isoformat() if user.fecha_registro else None,
        }


# =========================
# REFRESH TOKEN
# =========================

@ns.route("/refresh")
class Refresh(Resource):

    @jwt_required(refresh=True)
    @ns.marshal_with(access_model)
    def post(self):
        """Renovar access token"""

        user_id = int(get_jwt_identity())

        return {
            "access_token": auth_service.refresh_token(user_id)
        }