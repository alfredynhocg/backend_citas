from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.negocio_service import NegocioService

ns = Namespace('negocios', description='Gestion de negocios')

negocio_modelo = ns.model('Negocio', {
    'nombre': fields.String(required=True),
    'direccion': fields.String,
    'latitud': fields.Float,
    'longitud': fields.Float,
    'departamento_id': fields.Integer,
    'telefono': fields.String,
    'categoria_negocio': fields.String,
    'logo_url': fields.String
})

@ns.route('')
class NegocioLista(Resource):
    def get(self):
        departamento = request.args.get('departamento')
        negocios = NegocioService.obtener_negocios_activos(departamento)
        return [{
            'id': n.id,
            'nombre': n.nombre,
            'direccion': n.direccion,
            'categoria_negocio': n.categoria_negocio,
            'logo_url': n.logo_url
        } for n in negocios], 200
    
    @jwt_required()
    @ns.expect(negocio_modelo)
    def post(self):
        usuario_id = int(get_jwt_identity())
        data = request.get_json()
        negocio = NegocioService.crear_negocio(usuario_id, data)
        return {'id': negocio.id, 'nombre': negocio.nombre, 'mensaje': 'Negocio registrado pendiente de aprobacion'}, 201