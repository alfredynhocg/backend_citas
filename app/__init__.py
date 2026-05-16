import logging
import os

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended.exceptions import JWTExtendedException
from flask_restx import Api
from jwt.exceptions import PyJWTError
from werkzeug.exceptions import HTTPException

from .extensions import bcrypt, db, jwt


logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object("config")

    os.makedirs(app.config["IMG_UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    CORS(app, origins=app.config["CORS_ORIGINS"], supports_credentials=True)

    _register_error_handlers(app)

    with app.app_context():
        from . import models  # noqa: F401
        db.create_all()

    api = Api(
        app,
        title="100 Citas Románticas en La Paz — API",
        version="1.0",
        description="API REST para la app de citas románticas paceñas",
        doc="/swagger/",
        prefix="/api",
        authorizations={
            "Bearer": {
                "type": "apiKey",
                "in": "header",
                "name": "Authorization",
                "description": "JWT: Bearer <token>",
            }
        },
        security="Bearer",
    )

    from .routes.auth     import ns as auth_ns
    from .routes.couples  import ns as couples_ns
    from .routes.dates    import ns as dates_ns
    from .routes.memories import ns as memories_ns
    from .routes.users    import ns as users_ns

    api.add_namespace(auth_ns,     path="/auth")
    api.add_namespace(couples_ns,  path="/couples")
    api.add_namespace(dates_ns,    path="/dates")
    api.add_namespace(memories_ns, path="/memories")
    api.add_namespace(users_ns,    path="/users")

    return app


def _register_error_handlers(app: Flask) -> None:
    log = logging.getLogger(__name__)

    @app.errorhandler(HTTPException)
    def handle_http(e):
        return jsonify(message=e.description), e.code

    @app.errorhandler(JWTExtendedException)
    @app.errorhandler(PyJWTError)
    def handle_jwt(e):
        return jsonify(message="Token inválido o expirado"), 401

    @app.errorhandler(Exception)
    def handle_generic(e):
        log.exception("Error no controlado: %s", e)
        return jsonify(message="Error interno del servidor"), 500
