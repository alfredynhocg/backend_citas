import os
import secrets
from flask_restx import Namespace, Resource, fields
from flask import request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
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
        usuario_id = int(get_jwt_identity())
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
        usuario_id = int(get_jwt_identity())
        suscripciones = SuscripcionService.obtener_suscripciones_usuario(usuario_id)
        return [{
            'id': s.id,
            'plan': s.plan.nombre,
            'fecha_inicio': str(s.fecha_inicio),
            'fecha_expiracion': str(s.fecha_expiracion),
            'activo': s.activo
        } for s in suscripciones], 200

ALLOWED = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'}

@ns.route('/upload-comprobante')
class SubirComprobante(Resource):
    @jwt_required()
    def post(self):
        if 'file' not in request.files:
            return {'error': 'No se envió ningún archivo'}, 400
        file = request.files['file']
        if not file.filename:
            return {'error': 'Archivo sin nombre'}, 400
        ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
        if ext not in ALLOWED:
            return {'error': f'Extensión no permitida. Usa: {", ".join(ALLOWED)}'}, 400
        filename = f"comprobante_{secrets.token_hex(10)}.{ext}"
        upload_folder = current_app.config.get('IMG_UPLOAD_FOLDER', 'app/static/uploads')
        os.makedirs(upload_folder, exist_ok=True)
        file.save(os.path.join(upload_folder, filename))
        url = f"/static/uploads/{filename}"
        return {'url': url}, 201