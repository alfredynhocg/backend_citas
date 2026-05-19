from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.cita_service import CitaService

ns = Namespace('citas', description='Gestion de citas romanticas')

cita_modelo = ns.model('Cita', {
    'id': fields.Integer,
    'nombre': fields.String,
    'descripcion': fields.String,
    'categoria_id': fields.Integer,
    'categoria_nombre': fields.String,
    'departamento_id': fields.Integer,
    'departamento_nombre': fields.String,
    'negocio_id': fields.Integer,
    'negocio_nombre': fields.String,
    'latitud': fields.Float,
    'longitud': fields.Float,
    'direccion': fields.String,
    'puntos': fields.Integer,
    'portada_url': fields.String,
    'requiere_premium': fields.Boolean
})

completar_modelo = ns.model('CompletarCita', {
    'cita_id': fields.Integer(required=True),
    'grupo_id': fields.Integer,
    'calificacion': fields.Integer(min=1, max=5),
    'anecdota': fields.String,
    'fotos': fields.List(fields.String)
})

calificar_modelo = ns.model('CalificarCita', {
    'calificacion': fields.Integer(required=True, min=1, max=5),
    'anecdota': fields.String
})

@ns.route('')
class CitaLista(Resource):
    @jwt_required()
    def get(self):
        """Obtener todas las citas disponibles para el usuario"""
        usuario_id = int(get_jwt_identity())
        departamento = request.args.get('departamento')
        categoria = request.args.get('categoria_id', type=int)
        citas = CitaService.obtener_citas_disponibles(usuario_id, departamento, categoria)
        return {
            'total': len(citas),
            'citas': citas
        }, 200

@ns.route('/<int:cita_id>')
class CitaDetalle(Resource):
    @jwt_required()
    def get(self, cita_id):
        """Obtener detalle de una cita especifica"""
        usuario_id = int(get_jwt_identity())
        cita = CitaService.obtener_detalle_cita(usuario_id, cita_id)
        if not cita:
            return {'error': 'Cita no encontrada'}, 404
        
        # Verificar si el usuario tiene acceso
        tiene_acceso = CitaService.verificar_acceso_cita(usuario_id, cita_id)
        if not tiene_acceso:
            return {'error': 'No tienes acceso a esta cita. Actualiza tu suscripcion.'}, 403
        
        return cita, 200

@ns.route('/categorias')
class CategoriaLista(Resource):
    def get(self):
        """Obtener todas las categorias de citas"""
        categorias = CitaService.obtener_categorias()
        return {
            'total': len(categorias),
            'categorias': categorias
        }, 200

@ns.route('/departamentos')
class DepartamentoLista(Resource):
    def get(self):
        """Obtener todos los departamentos"""
        departamentos = CitaService.obtener_departamentos()
        return {
            'total': len(departamentos),
            'departamentos': departamentos
        }, 200

@ns.route('/completar')
class CompletarCita(Resource):
    @jwt_required()
    @ns.expect(completar_modelo)
    def post(self):
        """Marcar una cita como completada"""
        usuario_id = int(get_jwt_identity())
        data = request.get_json()
        
        resultado, status = CitaService.completar_cita(usuario_id, data)
        return resultado, status

@ns.route('/<int:cita_id>/calificar')
class CalificarCita(Resource):
    @jwt_required()
    @ns.expect(calificar_modelo)
    def post(self, cita_id):
        """Calificar una cita ya completada"""
        usuario_id = int(get_jwt_identity())
        data = request.get_json()
        
        resultado, status = CitaService.calificar_cita(usuario_id, cita_id, data)
        return resultado, status

@ns.route('/<int:cita_id>/fotos')
class SubirFotosCita(Resource):
    @jwt_required()
    def post(self, cita_id):
        """Subir fotos de una cita completada"""
        usuario_id = int(get_jwt_identity())
        
        if 'fotos' not in request.files:
            return {'error': 'No se enviaron fotos'}, 400
        
        fotos = request.files.getlist('fotos')
        resultado, status = CitaService.subir_fotos(usuario_id, cita_id, fotos)
        return resultado, status

@ns.route('/aleatoria')
class CitaAleatoria(Resource):
    @jwt_required()
    def get(self):
        """Obtener una cita aleatoria disponible"""
        usuario_id = int(get_jwt_identity())
        departamento = request.args.get('departamento')
        
        cita = CitaService.obtener_cita_aleatoria(usuario_id, departamento)
        if not cita:
            return {'error': 'No hay citas disponibles'}, 404
        
        return cita, 200

@ns.route('/recomendadas')
class CitasRecomendadas(Resource):
    @jwt_required()
    def get(self):
        """Obtener citas recomendadas basadas en el progreso"""
        usuario_id = int(get_jwt_identity())
        limit = request.args.get('limit', 5, type=int)
        
        citas = CitaService.obtener_citas_recomendadas(usuario_id, limit)
        return {
            'total': len(citas),
            'citas': citas
        }, 200

@ns.route('/progreso')
class MiProgresoCitas(Resource):
    @jwt_required()
    def get(self):
        """Obtener progreso de citas del usuario"""
        usuario_id = int(get_jwt_identity())
        
        progreso = CitaService.obtener_progreso_usuario(usuario_id)
        return progreso, 200

@ns.route('/grupo/<int:grupo_id>/progreso')
class GrupoProgresoCitas(Resource):
    @jwt_required()
    def get(self, grupo_id):
        """Obtener progreso de citas de un grupo"""
        usuario_id = int(get_jwt_identity())
        
        progreso = CitaService.obtener_progreso_grupo(usuario_id, grupo_id)
        if not progreso:
            return {'error': 'No tienes acceso a este grupo'}, 403
        
        return progreso, 200