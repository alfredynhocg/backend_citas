from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.suscripcion_service import SuscripcionService

ns = Namespace('suscripciones', description='Suscripciones y pagos')

pago_modelo = ns.model('Pago', {
    'plan_id': fields.Integer(required=True),
    'grupo_id': fields.Integer,
    'tipo_periodo': fields.String(required=True),
    'comprobante_url': fields.String
})

@ns.route('/planes')
class PlanesLista(Resource):
    def get(self):
        planes = SuscripcionService.obtener_planes()
        return [{
            'id': p.id,
            'nombre': p.nombre,
            'precio_mensual': float(p.precio_mensual),
            'precio_anual': float(p.precio_anual),
            'max_integrantes': p.max_integrantes,
            'permite_grupo': p.permite_grupo,
            'departamentos_desbloquea': p.departamentos_desbloquea
        } for p in planes], 200

@ns.route('/pago')
class CrearPago(Resource):
    @jwt_required()
    @ns.expect(pago_modelo)
    def post(self):
        usuario_id = get_jwt_identity()
        data = request.get_json()
        pago = SuscripcionService.crear_pago(usuario_id, data)
        return {
            'id': pago.id,
            'monto': float(pago.monto),
            'estado': pago.estado,
            'mensaje': 'Pago registrado, esperando aprobacion'
        }, 201

@ns.route('/mis-suscripciones')
class MisSuscripciones(Resource):
    @jwt_required()
    def get(self):
        usuario_id = get_jwt_identity()
        suscripciones = SuscripcionService.obtener_suscripciones_usuario(usuario_id)
        return [{
            'id': s.id,
            'plan': s.plan.nombre,
            'fecha_inicio': str(s.fecha_inicio),
            'fecha_expiracion': str(s.fecha_expiracion),
            'activo': s.activo
        } for s in suscripciones], 200