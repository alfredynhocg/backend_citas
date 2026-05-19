import secrets
from ..extensions import db
from ..models import Grupo, GrupoMiembro, User


class GrupoService:

    @staticmethod
    def obtener_grupos_usuario(usuario_id):
        memberships = GrupoMiembro.query.filter_by(usuario_id=usuario_id).all()
        return [m.grupo for m in memberships if m.grupo and m.grupo.activo]

    @staticmethod
    def crear_grupo(usuario_id, data):
        nombre = data.get('nombre', '').strip()
        tipo = data.get('tipo', 'pareja')
        if not nombre:
            raise ValueError("El nombre del grupo es requerido")

        codigo = secrets.token_hex(4).upper()
        while Grupo.query.filter_by(codigo_invitacion=codigo).first():
            codigo = secrets.token_hex(4).upper()

        grupo = Grupo(
            nombre=nombre,
            tipo=tipo,
            codigo_invitacion=codigo,
            creado_por=usuario_id,
            activo=True,
        )
        db.session.add(grupo)
        db.session.flush()

        miembro = GrupoMiembro(grupo_id=grupo.id, usuario_id=usuario_id, es_admin=True)
        db.session.add(miembro)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return grupo

    @staticmethod
    def obtener_grupo(grupo_id):
        return Grupo.query.filter_by(id=grupo_id, activo=True).first()

    @staticmethod
    def obtener_miembros(grupo_id):
        miembros = GrupoMiembro.query.filter_by(grupo_id=grupo_id).all()
        return [m.usuario for m in miembros if m.usuario]

    @staticmethod
    def unir_grupo(codigo, usuario_id):
        grupo = Grupo.query.filter_by(codigo_invitacion=codigo, activo=True).first()
        if not grupo:
            return None
        ya_miembro = GrupoMiembro.query.filter_by(grupo_id=grupo.id, usuario_id=usuario_id).first()
        if ya_miembro:
            return grupo
        miembro = GrupoMiembro(grupo_id=grupo.id, usuario_id=usuario_id, es_admin=False)
        db.session.add(miembro)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return grupo

    @staticmethod
    def invitar_miembro(grupo_id, email):
        usuario = User.query.filter_by(email=email).first()
        if not usuario:
            return {'error': 'Usuario no encontrado con ese email'}
        ya_miembro = GrupoMiembro.query.filter_by(grupo_id=grupo_id, usuario_id=usuario.id).first()
        if ya_miembro:
            return {'mensaje': 'El usuario ya es miembro del grupo'}
        miembro = GrupoMiembro(grupo_id=grupo_id, usuario_id=usuario.id, es_admin=False)
        db.session.add(miembro)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return {'mensaje': f'{usuario.nombre} agregado al grupo'}

    @staticmethod
    def eliminar_grupo(grupo_id):
        grupo = Grupo.query.get(grupo_id)
        if not grupo:
            raise LookupError("Grupo no encontrado")
        grupo.activo = False
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
