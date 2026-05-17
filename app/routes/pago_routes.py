from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.pago_service import PagoService

ns = Namespace('pagos', description='Gestion de pagos')

@ns.route('/historial')
class HistorialPagos(Resource):
    @jwt_required()
    def get(self):
        usuario_id = get_jwt_identity()
        pagos = PagoService.obtener_historial_usuario(usuario_id)
        return [{
            'id': p.id,
            'monto': float(p.monto),
            'plan': p.plan.nombre,
            'estado': p.estado,
            'fecha_pago': str(p.fecha_pago)
        } for p in pagos], 200