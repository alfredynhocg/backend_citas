from flask import session, redirect
from flask_admin.base import MenuLink, BaseView, expose
from flask_admin.contrib.sqla import ModelView

from .extensions import db
from .models import User, Role, Categoria, Cita, Negocio, Departamento


class LoginMenuLink(MenuLink):
    def is_accessible(self):
        return not session.get('admin_logged_in', False)


class LogoutMenuLink(MenuLink):
    def is_accessible(self):
        return session.get('admin_logged_in', False)


class AdminModelView(ModelView):
    def is_accessible(self):
        return session.get('admin_logged_in', False)

    def inaccessible_callback(self, name, **kwargs):
        return redirect('/login')


class ReportesView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/reportes.html')


def register_admin_views(admin):

    admin.add_link(LoginMenuLink(name='Iniciar', url='/login'))
    admin.add_link(LogoutMenuLink(name='Finalizar', url='/logout'))

    admin.add_view(AdminModelView(User, db.session, name='Usuarios'))
    admin.add_view(AdminModelView(Role, db.session, name='Roles'))
    admin.add_view(AdminModelView(Categoria, db.session, name='Categorías'))
    admin.add_view(AdminModelView(Cita, db.session, name='Citas'))
    admin.add_view(AdminModelView(Negocio, db.session, name='Negocios'))
    admin.add_view(AdminModelView(Departamento, db.session, name='Departamentos'))

    admin.add_view(ReportesView(name='Reportes', endpoint='reportes'))