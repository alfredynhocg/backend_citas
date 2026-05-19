from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.mensaje_service import MensajeService

ns = Namespace('mensajes', description='Mensajeria')

mensaje_modelo = ns.model('Mensaje', {
    'grupo_id': fields.Integer,
    'para_usuario_id': fields.Integer,
    'mensaje': fields.String(required=True)
})

def _serializar_mensaje(m):
    return {
        'id': m.id,
        'mensaje': m.mensaje,
        'de_usuario_id': m.de_usuario_id,
        'de_usuario': m.emisor.nombre if m.emisor else None,
        'para_usuario_id': m.para_usuario_id,
        'grupo_id': m.grupo_id,
        'leido': m.leido,
        'fecha': str(m.fecha),
    }

@ns.route('')
class MensajesLista(Resource):
    @jwt_required()
    def get(self):
        usuario_id = get_jwt_identity()
        mensajes = MensajeService.obtener_mensajes_usuario(usuario_id)
        return [_serializar_mensaje(m) for m in mensajes], 200

    @jwt_required()
    @ns.expect(mensaje_modelo)
    def post(self):
        usuario_id = get_jwt_identity()
        data = request.get_json()
        mensaje = MensajeService.enviar_mensaje(usuario_id, data)
        return {'mensaje': 'Mensaje enviado', 'id': mensaje.id}, 201

@ns.route('/grupo/<int:grupo_id>')
class MensajesGrupo(Resource):
    @jwt_required()
    def get(self, grupo_id):
        mensajes = MensajeService.obtener_mensajes_grupo(grupo_id)
        return [_serializar_mensaje(m) for m in mensajes], 200