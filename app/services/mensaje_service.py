from ..extensions import db
from ..models import Mensaje


class MensajeService:

    @staticmethod
    def obtener_mensajes_usuario(usuario_id):
        return (
            Mensaje.query
            .filter((Mensaje.de_usuario_id == usuario_id) | (Mensaje.para_usuario_id == usuario_id))
            .order_by(Mensaje.fecha.asc())
            .all()
        )

    @staticmethod
    def obtener_mensajes_grupo(grupo_id):
        return (
            Mensaje.query
            .filter_by(grupo_id=grupo_id)
            .order_by(Mensaje.fecha.asc())
            .all()
        )

    @staticmethod
    def enviar_mensaje(usuario_id, data):
        texto = data.get('mensaje', '').strip()
        if not texto:
            raise ValueError("El mensaje no puede estar vacío")
        mensaje = Mensaje(
            de_usuario_id=usuario_id,
            para_usuario_id=data.get('para_usuario_id'),
            grupo_id=data.get('grupo_id'),
            mensaje=texto,
            leido=False,
        )
        db.session.add(mensaje)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return mensaje

    @staticmethod
    def marcar_leidos(grupo_id, usuario_id):
        Mensaje.query.filter_by(grupo_id=grupo_id, leido=False).filter(
            Mensaje.de_usuario_id != usuario_id
        ).update({'leido': True})
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def contar_no_leidos(usuario_id):
        return Mensaje.query.filter_by(para_usuario_id=usuario_id, leido=False).count()
