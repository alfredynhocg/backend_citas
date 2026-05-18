from flask import redirect, session

from flask_appbuilder import ModelView, BaseView, expose
from flask_appbuilder.models.sqla.interface import SQLAInterface

from .extensions import appbuilder
from .models import User, Cita


class UserModelView(ModelView):
    datamodel = SQLAInterface(User)

    list_columns = [
        "id",
        "nombre",
        "email",
        "activo"
    ]


class CitaModelView(ModelView):
    datamodel = SQLAInterface(Cita)

    list_columns = [
        "id",
        "nombre",
        "puntos"
    ]


class LoginButtonView(BaseView):

    route_base = "/"

    @expose("/admin-login/")
    def admin_login(self):
        if session.get("admin_logged_in"):
            return redirect("/admin")

        return redirect("/login")


appbuilder.add_link(
    "Iniciar Sesión",
    href="/login",
    icon="fa-sign-in",
    category=""
)

appbuilder.add_view(
    UserModelView,
    "Usuarios",
    icon="fa-users",
    category="Seguridad"
)

appbuilder.add_view(
    CitaModelView,
    "Citas",
    icon="fa-calendar",
    category="Contenido"
)