from ..extensions import db
from ..models import Pago


class PagoService:

    @staticmethod
    def obtener_historial_usuario(usuario_id):
        return Pago.query.filter_by(usuario_id=usuario_id).order_by(Pago.fecha_pago.desc()).all()

    @staticmethod
    def obtener_pago(pago_id, usuario_id):
        return Pago.query.filter_by(id=pago_id, usuario_id=usuario_id).first()
