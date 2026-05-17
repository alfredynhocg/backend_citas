from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.admin_cita_service import AdminCitaService
from ..utils.decoradores import admin_requerido

ns = Namespace('admin/citas', description='Administracion de citas, negocios y categorias')

# Modelos para la documentacion
categoria_modelo = ns.model('Categoria', {
    'id': fields.Integer,
    'nombre': fields.String(required=True)
})

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

cita_modelo = ns.model('Cita', {
    'nombre': fields.String(required=True),
    'descripcion': fields.String,
    'categoria_id': fields.Integer(required=True),
    'departamento_id': fields.Integer(required=True),
    'negocio_id': fields.Integer,
    'latitud': fields.Float,
    'longitud': fields.Float,
    'direccion': fields.String,
    'puntos': fields.Integer,
    'portada_url': fields.String,
    'activo': fields.Boolean
})

foto_modelo = ns.model('Foto', {
    'url': fields.String(required=True),
    'descripcion': fields.String
})


# ==================== CATEGORIAS CRUD ====================

@ns.route('/categorias')
class AdminCategorias(Resource):
    @jwt_required()
    @admin_requerido
    def get(self):
        """Obtener todas las categorias"""
        categorias = AdminCitaService.obtener_todas_categorias()
        return {'total': len(categorias), 'categorias': categorias}, 200
    
    @jwt_required()
    @admin_requerido
    @ns.expect(categoria_modelo)
    def post(self):
        """Crear una nueva categoria"""
        data = request.get_json()
        resultado, status = AdminCitaService.crear_categoria(data)
        return resultado, status

@ns.route('/categorias/<int:categoria_id>')
class AdminCategoriaDetail(Resource):
    @jwt_required()
    @admin_requerido
    def get(self, categoria_id):
        """Obtener una categoria por ID"""
        categoria = AdminCitaService.obtener_categoria_por_id(categoria_id)
        if not categoria:
            return {'error': 'Categoria no encontrada'}, 404
        return categoria, 200
    
    @jwt_required()
    @admin_requerido
    @ns.expect(categoria_modelo)
    def put(self, categoria_id):
        """Actualizar una categoria"""
        data = request.get_json()
        resultado, status = AdminCitaService.actualizar_categoria(categoria_id, data)
        return resultado, status
    
    @jwt_required()
    @admin_requerido
    def delete(self, categoria_id):
        """Eliminar una categoria"""
        resultado, status = AdminCitaService.eliminar_categoria(categoria_id)
        return resultado, status


# ==================== NEGOCIOS CRUD ====================

@ns.route('/negocios')
class AdminNegocios(Resource):
    @jwt_required()
    @admin_requerido
    def get(self):
        """Obtener todos los negocios"""
        negocios = AdminCitaService.obtener_todos_negocios()
        return {'total': len(negocios), 'negocios': negocios}, 200
    
    @jwt_required()
    @admin_requerido
    @ns.expect(negocio_modelo)
    def post(self):
        """Crear un nuevo negocio"""
        data = request.get_json()
        resultado, status = AdminCitaService.crear_negocio(data)
        return resultado, status

@ns.route('/negocios/<int:negocio_id>')
class AdminNegocioDetail(Resource):
    @jwt_required()
    @admin_requerido
    def get(self, negocio_id):
        """Obtener un negocio por ID"""
        negocio = AdminCitaService.obtener_negocio_por_id(negocio_id)
        if not negocio:
            return {'error': 'Negocio no encontrado'}, 404
        return negocio, 200
    
    @jwt_required()
    @admin_requerido
    @ns.expect(negocio_modelo)
    def put(self, negocio_id):
        """Actualizar un negocio"""
        data = request.get_json()
        resultado, status = AdminCitaService.actualizar_negocio(negocio_id, data)
        return resultado, status
    
    @jwt_required()
    @admin_requerido
    def delete(self, negocio_id):
        """Eliminar un negocio"""
        resultado, status = AdminCitaService.eliminar_negocio(negocio_id)
        return resultado, status


# ==================== CITAS CRUD ====================

@ns.route('/citas')
class AdminCitas(Resource):
    @jwt_required()
    @admin_requerido
    def get(self):
        """Obtener todas las citas"""
        citas = AdminCitaService.obtener_todas_citas()
        return {'total': len(citas), 'citas': citas}, 200
    
    @jwt_required()
    @admin_requerido
    @ns.expect(cita_modelo)
    def post(self):
        """Crear una nueva cita"""
        data = request.get_json()
        resultado, status = AdminCitaService.crear_cita(data)
        return resultado, status

@ns.route('/citas/<int:cita_id>')
class AdminCitaDetail(Resource):
    @jwt_required()
    @admin_requerido
    def get(self, cita_id):
        """Obtener una cita por ID"""
        cita = AdminCitaService.obtener_cita_por_id(cita_id)
        if not cita:
            return {'error': 'Cita no encontrada'}, 404
        return cita, 200
    
    @jwt_required()
    @admin_requerido
    @ns.expect(cita_modelo)
    def put(self, cita_id):
        """Actualizar una cita"""
        data = request.get_json()
        resultado, status = AdminCitaService.actualizar_cita(cita_id, data)
        return resultado, status
    
    @jwt_required()
    @admin_requerido
    def delete(self, cita_id):
        """Eliminar una cita"""
        resultado, status = AdminCitaService.eliminar_cita(cita_id)
        return resultado, status


# ==================== FOTOS CRUD ====================

@ns.route('/citas/<int:cita_id>/fotos')
class AdminFotosCita(Resource):
    @jwt_required()
    @admin_requerido
    def get(self, cita_id):
        """Obtener todas las fotos de una cita"""
        fotos = AdminCitaService.obtener_fotos_cita(cita_id)
        return {'total': len(fotos), 'fotos': fotos}, 200
    
    @jwt_required()
    @admin_requerido
    @ns.expect(foto_modelo)
    def post(self, cita_id):
        """Agregar una foto a una cita"""
        data = request.get_json()
        resultado, status = AdminCitaService.agregar_foto_cita(cita_id, data)
        return resultado, status

@ns.route('/fotos/<int:foto_id>')
class AdminFotoDetail(Resource):
    @jwt_required()
    @admin_requerido
    def delete(self, foto_id):
        """Eliminar una foto"""
        resultado, status = AdminCitaService.eliminar_foto(foto_id)
        return resultado, status


# ==================== ESTADISTICAS ====================

@ns.route('/estadisticas')
class AdminEstadisticas(Resource):
    @jwt_required()
    @admin_requerido
    def get(self):
        """Obtener estadisticas del sistema"""
        stats = AdminCitaService.obtener_estadisticas()
        return stats, 200