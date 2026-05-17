from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.progreso_service import ProgresoService

ns = Namespace('progreso', description='Progreso de citas')

completar_modelo = ns.model('Completar', {
    'cita_id': fields.Integer(required=True),
    'grupo_id': fields.Integer(required=False),
    'calificacion': fields.Integer,
    'anecdota': fields.String,
    'fotos': fields.List(fields.String)
})

@ns.route('/completar')
class CompletarCita(Resource):
    @jwt_required()
    @ns.expect(completar_modelo)
    def post(self):
        usuario_id = get_jwt_identity()
        data = request.get_json()
        resultado = ProgresoService.completar_cita(usuario_id, data)
        return resultado, 201

@ns.route('/grupo/<int:grupo_id>')
class ProgresoGrupo(Resource):
    @jwt_required()
    def get(self, grupo_id):
        progreso = ProgresoService.obtener_progreso_grupo(grupo_id)
        return progreso, 200

@ns.route('/usuario/<int:usuario_id>')
class ProgresoUsuario(Resource):
    @jwt_required()
    def get(self, usuario_id):
        progreso = ProgresoService.obtener_progreso_usuario(usuario_id)
        return progreso, 200