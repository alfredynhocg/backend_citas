from ..extensions import db
from ..models import Negocio, FotoNegocio


class NegocioService:

    @staticmethod
    def obtener_negocios_activos(departamento_id=None):
        q = Negocio.query.filter_by(activo=True)
        if departamento_id:
            q = q.filter_by(departamento_id=departamento_id)
        return q.all()

    @staticmethod
    def obtener_negocio(negocio_id):
        return Negocio.query.filter_by(id=negocio_id, activo=True).first()

    @staticmethod
    def crear_negocio(usuario_id, data):
        nombre = data.get('nombre', '').strip()
        if not nombre:
            raise ValueError("El nombre del negocio es requerido")
        negocio = Negocio(
            nombre=nombre,
            direccion=data.get('direccion'),
            latitud=data.get('latitud'),
            longitud=data.get('longitud'),
            departamento_id=data.get('departamento_id'),
            telefono=data.get('telefono'),
            categoria_negocio=data.get('categoria_negocio'),
            logo_url=data.get('logo_url'),
            admin_id=usuario_id,
            activo=False,
        )
        db.session.add(negocio)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return negocio

    @staticmethod
    def obtener_fotos(negocio_id):
        return FotoNegocio.query.filter_by(negocio_id=negocio_id).all()
