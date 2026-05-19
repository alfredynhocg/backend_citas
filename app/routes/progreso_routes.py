from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.progreso_service import ProgresoService

ns = Namespace('progreso', description='Progreso de citas')

completar_modelo = ns.model('Completar', {
    'cita_id': fields.Integer(required=True),
    'tipo': fields.String(default='individual'),
    'grupo_id': fields.Integer(required=False),
    'calificacion': fields.Integer,
    'anecdota': fields.String,
})

def _serializar(p):
    return {
        'id': p.id,
        'cita_id': p.cita_id,
        'cita': p.cita.nombre if p.cita else None,
        'cita_descripcion': p.cita.descripcion if p.cita else None,
        'cita_imagen': p.cita.portada_url if p.cita else None,
        'cita_categoria': p.cita.categoria.nombre if p.cita and p.cita.categoria else None,
        'tipo': p.tipo,
        'completado': p.completado,
        'calificacion': p.calificacion,
        'anecdota': p.anecdota,
        'fecha_completado': str(p.fecha_completado) if p.fecha_completado else None,
    }

@ns.route('/completar')
class CompletarCita(Resource):
    @jwt_required()
    @ns.expect(completar_modelo)
    def post(self):
        usuario_id = get_jwt_identity()
        data = request.get_json()
        try:
            resultado = ProgresoService.completar_cita(usuario_id, data)
            return _serializar(resultado), 201
        except (ValueError, LookupError) as e:
            return {'message': str(e)}, 400

@ns.route('/mis-recuerdos')
class MisRecuerdos(Resource):
    @jwt_required()
    def get(self):
        usuario_id = get_jwt_identity()
        progresos = ProgresoService.obtener_progreso_usuario(usuario_id)
        completados = [p for p in progresos if p.completado]
        return [_serializar(p) for p in completados], 200

@ns.route('/estadisticas')
class Estadisticas(Resource):
    @jwt_required()
    def get(self):
        usuario_id = get_jwt_identity()
        return ProgresoService.obtener_estadisticas(usuario_id), 200

@ns.route('/grupo/<int:grupo_id>')
class ProgresoGrupo(Resource):
    @jwt_required()
    def get(self, grupo_id):
        progreso = ProgresoService.obtener_progreso_grupo(grupo_id)
        completados = [p for p in progreso if p.completado]
        return [_serializar(p) for p in completados], 200