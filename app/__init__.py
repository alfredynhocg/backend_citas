import logging
import os
from flask import Flask, jsonify, redirect, request, flash, session
from flask_cors import CORS
from flask_jwt_extended.exceptions import JWTExtendedException
from flask_restx import Api
from jwt.exceptions import PyJWTError
from werkzeug.exceptions import HTTPException

from flask_admin import Admin, BaseView, expose

from flask_admin.contrib.sqla import ModelView

from .extensions import bcrypt, db, jwt

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

def create_app() -> Flask:
    app = Flask(__name__)
    
    app.config.from_object("config")
    app.config['SECRET_KEY'] = 'clave-secreta-para-sesion-12345'
    
    os.makedirs(app.config["IMG_UPLOAD_FOLDER"], exist_ok=True)
    
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    CORS(app, origins=app.config["CORS_ORIGINS"], supports_credentials=True)
    from flask_babel import Babel
    app.config['BABEL_DEFAULT_LOCALE'] = 'es'
    babel = Babel(app)

    _register_error_handlers(app)
    
    with app.app_context():
        from . import models
        db.create_all()
        from .models import crear_roles_por_defecto
        crear_roles_por_defecto()
    
    # ============ FLASK-ADMIN ============
    admin = Admin(app, name='Panel Admin Citas')
    from flask_admin.base import MenuLink

    class LoginMenuLink(MenuLink):
        def is_accessible(self):
            return not session.get('admin_logged_in', False)


    class LogoutMenuLink(MenuLink):
        def is_accessible(self):
            return session.get('admin_logged_in', False)


    admin.add_link(
        LoginMenuLink(
            name='Iniciar',
            url='/login'
        )
    )
    # Importar modelos después de crear tablas
    from .models import User, Role, Categoria, Cita, Negocio, Departamento


    class AdminModelView(ModelView):
        def is_accessible(self):
            return session.get('admin_logged_in', False)

        def inaccessible_callback(self, name, **kwargs):
            return redirect('/login')
    
    # Agregar vistas al admin
    admin.add_view(AdminModelView(User, db.session, name='Usuarios'))
    admin.add_view(AdminModelView(Role, db.session, name='Roles'))
    admin.add_view(AdminModelView(Categoria, db.session, name='Categorías'))
    admin.add_view(AdminModelView(Cita, db.session, name='Citas'))
    admin.add_view(AdminModelView(Negocio, db.session, name='Negocios'))
    admin.add_view(AdminModelView(Departamento, db.session, name='Departamentos'))
    
    # ============ RUTAS LOGIN/LOGOUT ============
    @app.route('/login', methods=['GET', 'POST'])
    def login_page():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            # 🔥 USUARIO Y PASSWORD HARDCODEADO (puedes cambiar luego a BD)
            if username == 'admin' and password == 'admin123':
                session['admin_logged_in'] = True
                session['admin_user'] = username
                return redirect('/admin')
            else:
                return '''
                <script>
                    alert("Usuario o contraseña incorrectos");
                    window.location.href = "/login";
                </script>
                '''

        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Login Admin</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">

            <style>
                body {
                    background: linear-gradient(135deg, #0f172a, #1e293b);
                    height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    font-family: Arial, sans-serif;
                }

                .login-box {
                    background: #ffffff;
                    border-radius: 16px;
                    padding: 35px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.25);
                    width: 100%;
                    max-width: 420px;
                    transition: transform 0.2s ease;
                }

                .login-box:hover {
                    transform: translateY(-3px);
                }

                .btn-login {
                    background: linear-gradient(135deg, #22c55e, #16a34a);
                    border: none;
                    width: 100%;
                    padding: 10px;
                    font-weight: bold;
                }

                .btn-login:hover {
                    opacity: 0.9;
                    transform: scale(1.02);
                }

                input.form-control {
                    border-radius: 10px;
                    padding: 10px;
                }

                h3 {
                    font-weight: bold;
                    color: #0f172a;
                }
                </style>
        </head>

        <body>

            <div class="login-box">
                <h3 class="text-center mb-3">Panel Administrativo</h3>
                <p class="text-center text-muted">Sistema de Citas</p>

                <form method="POST">

                    <div class="mb-3">
                        <label>Usuario</label>
                        <input type="text" name="username" class="form-control" placeholder="admin" required>
                    </div>

                    <div class="mb-3">
                        <label>Contraseña</label>
                        <input type="password" name="password" class="form-control" placeholder="admin123" required>
                    </div>

                    <button type="submit" class="btn btn-primary btn-login">
                        Ingresar
                    </button>

                </form>

                <hr>
                <small class="text-muted">Usuario: admin | Password: admin123</small>
            </div>

        </body>
        </html>
        '''
    
    @app.route('/logout')
    def logout_page():
        session.pop('admin_logged_in', None)
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Sesión Cerrada</title>
            <meta http-equiv="refresh" content="2;url=/login">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container text-center" style="margin-top:200px">
                <div class="alert alert-success">
                    <h4>¡Sesión cerrada correctamente!</h4>
                    <p>Redirigiendo al login...</p>
                </div>
            </div>
        </body>
        </html>
        '''
    
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
    
    from .routes.auth import ns as auth_ns
    from .routes.couples import ns as couples_ns
    from .routes.dates import ns as dates_ns
    from .routes.memories import ns as memories_ns
    from .routes.users import ns as users_ns
    from .routes.test import ns as test_ns
    from .routes.usuario_routes import ns as usuario_ns
    from .routes.cita_routes import ns as citas_ns
    from .routes.admin_citas_routes import ns as admin_citas_ns
    from .routes.ia_routes import ns as ia_ns
    from .routes.grupo_routes import ns as grupo_ns
    from .routes.suscripcion_routes import ns as suscripcion_ns
    from .routes.pago_routes import ns as pago_ns
    from .routes.mensaje_routes import ns as mensaje_ns
    from .routes.negocio_routes import ns as negocio_ns
    from .routes.admin_routes import ns as admin_ns
    from .routes.progreso_routes import ns as progreso_ns
    from .routes.rol_routes import ns as rol_ns
    from .routes.dashboard_routes import ns as dashboard_ns
    from .routes.bot_routes import ns as bot_ns
    from .routes.whatsapp_routes import ns as whatsapp_ns

    api.add_namespace(auth_ns, path="/auth")
    api.add_namespace(couples_ns, path="/couples")
    api.add_namespace(dates_ns, path="/dates")
    api.add_namespace(memories_ns, path="/memories")
    api.add_namespace(test_ns, path="/dev")
    api.add_namespace(users_ns, path="/users")
    api.add_namespace(usuario_ns, path="/usuarios")
    api.add_namespace(citas_ns, path="/citas")
    api.add_namespace(admin_citas_ns, path="/admin/citas")
    api.add_namespace(ia_ns, path="/ia")
    api.add_namespace(grupo_ns, path="/grupos")
    api.add_namespace(suscripcion_ns, path="/suscripciones")
    api.add_namespace(pago_ns, path="/pagos")
    api.add_namespace(mensaje_ns, path="/mensajes")
    api.add_namespace(negocio_ns, path="/negocios")
    api.add_namespace(admin_ns, path="/admin")
    api.add_namespace(progreso_ns, path="/progreso")
    api.add_namespace(rol_ns, path="/roles")
    api.add_namespace(dashboard_ns, path="/dashboard")
    api.add_namespace(bot_ns, path="/bot")
    api.add_namespace(whatsapp_ns, path="/whatsapp")

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