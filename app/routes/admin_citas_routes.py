from flask_restx import Namespace, Resource, fields
from flask import request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.admin_cita_service import AdminCitaService
from ..utils.decoradores import admin_requerido
from ..models import User, Cita, FotoCita, db
import os
import secrets
import subprocess
import signal
from werkzeug.utils import secure_filename

# PID del proceso bot
_bot_process = None
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
    def get(self):
        usuario_id = int(get_jwt_identity())
        usuario = User.query.get(usuario_id)
        if not usuario or usuario.rol_id != 1:
            return {'error': 'Acceso denegado'}, 403
        
        negocios = AdminCitaService.obtener_todos_negocios()
        return {'total': len(negocios), 'negocios': negocios}, 200
    
    @jwt_required()
    @ns.expect(negocio_modelo)
    def post(self):
        usuario_id = int(get_jwt_identity())
        usuario = User.query.get(usuario_id)
        if not usuario or usuario.rol_id != 1:
            return {'error': 'Acceso denegado'}, 403
        
        data = request.get_json()
        resultado = AdminCitaService.crear_negocio(data)
        
        # Si resultado es una tupla (dict, status)
        if isinstance(resultado, tuple):
            return resultado[0], resultado[1]
        
        return resultado, 201

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
    def get(self):
        usuario_id = int(get_jwt_identity())
        usuario = User.query.get(usuario_id)
        if not usuario or usuario.rol_id != 1:
            return {'error': 'Acceso denegado'}, 403
        
        citas = AdminCitaService.obtener_todas_citas()
        return {'total': len(citas), 'citas': citas}, 200
    
    @jwt_required()
    @ns.expect(cita_modelo)
    def post(self):
        usuario_id = int(get_jwt_identity())
        usuario = User.query.get(usuario_id)
        if not usuario or usuario.rol_id != 1:
            return {'error': 'Acceso denegado'}, 403
        
        data = request.get_json()
        resultado = AdminCitaService.crear_cita(data)
        return resultado, 201

    @ns.route('/citas/<int:cita_id>')
    class AdminCitaDetail(Resource):
        @jwt_required()
        def get(self, cita_id):
            usuario_id = int(get_jwt_identity())
            usuario = User.query.get(usuario_id)
            if not usuario or usuario.rol_id != 1:
                return {'error': 'Acceso denegado'}, 403
            
            cita = AdminCitaService.obtener_cita_por_id(cita_id)
            if not cita:
                return {'error': 'Cita no encontrada'}, 404
            return cita, 200
        
        @jwt_required()
        @ns.expect(cita_modelo)
        def put(self, cita_id):
            usuario_id = int(get_jwt_identity())
            usuario = User.query.get(usuario_id)
            if not usuario or usuario.rol_id != 1:
                return {'error': 'Acceso denegado'}, 403
            
            data = request.get_json()
            resultado = AdminCitaService.actualizar_cita(cita_id, data)
            return resultado, 200
        
        @jwt_required()
        def delete(self, cita_id):
            usuario_id = int(get_jwt_identity())
            usuario = User.query.get(usuario_id)
            if not usuario or usuario.rol_id != 1:
                return {'error': 'Acceso denegado'}, 403
            
            resultado = AdminCitaService.eliminar_cita(cita_id)
            return resultado, 200


        # ==================== FOTOS CRUD ====================

    @ns.route('/citas/<int:cita_id>/fotos')
    class AdminFotosCita(Resource):
        @jwt_required()
        def get(self, cita_id):
            usuario_id = int(get_jwt_identity())
            usuario = User.query.get(usuario_id)
            if not usuario or usuario.rol_id != 1:
                return {'error': 'Acceso denegado'}, 403
            
            fotos = AdminCitaService.obtener_fotos_cita(cita_id)
            return {'total': len(fotos), 'fotos': fotos}, 200
        
        @jwt_required()
        @ns.expect(foto_modelo)
        def post(self, cita_id):
            usuario_id = int(get_jwt_identity())
            usuario = User.query.get(usuario_id)
            if not usuario or usuario.rol_id != 1:
                return {'error': 'Acceso denegado'}, 403
            
            data = request.get_json()
            resultado = AdminCitaService.agregar_foto_cita(cita_id, data)
            return resultado, 201

    @ns.route('/fotos/<int:foto_id>')
    class AdminFotoDetail(Resource):
        @jwt_required()
        def delete(self, foto_id):
            usuario_id = int(get_jwt_identity())
            usuario = User.query.get(usuario_id)
            if not usuario or usuario.rol_id != 1:
                return {'error': 'Acceso denegado'}, 403
            
            resultado = AdminCitaService.eliminar_foto(foto_id)
            return resultado, 200
    #Crear Cita con imagenes
    @ns.route('/con-fotos')
    class AdminCitaConFotos(Resource):
        @jwt_required()
        def post(self):
            """Crear una cita con imágenes (multipart/form-data)"""
            usuario_id = int(get_jwt_identity())
            usuario = User.query.get(usuario_id)
            if not usuario or usuario.rol_id != 1:
                return {'error': 'Acceso denegado'}, 403
            
            # Obtener datos del formulario
            nombre = request.form.get('nombre')
            descripcion = request.form.get('descripcion')
            categoria_id = request.form.get('categoria_id', type=int)
            departamento_id = request.form.get('departamento_id', type=int)
            negocio_id = request.form.get('negocio_id', type=int)
            latitud = request.form.get('latitud', type=float)
            longitud = request.form.get('longitud', type=float)
            direccion = request.form.get('direccion')
            puntos = request.form.get('puntos', type=int, default=10)
            
            # Validaciones
            if not nombre:
                return {'error': 'El nombre es requerido'}, 400
            if not categoria_id:
                return {'error': 'La categoría es requerida'}, 400
            if not departamento_id:
                return {'error': 'El departamento es requerido'}, 400
            
            # Crear la cita
            cita = Cita(
                nombre=nombre,
                descripcion=descripcion,
                categoria_id=categoria_id,
                departamento_id=departamento_id,
                negocio_id=negocio_id,
                latitud=latitud,
                longitud=longitud,
                direccion=direccion,
                puntos=puntos
            )
            db.session.add(cita)
            db.session.flush()
            
            # Subir fotos
            fotos_subidas = []
            upload_folder = current_app.config.get('IMG_UPLOAD_FOLDER', 'app/static/uploads')
            os.makedirs(upload_folder, exist_ok=True)
            
            archivos = request.files.getlist('fotos')
            for archivo in archivos:
                if archivo and archivo.filename:
                    from werkzeug.utils import secure_filename
                    import secrets
                    
                    ext = archivo.filename.rsplit('.', 1)[1].lower()
                    filename = f"cita_{cita.id}_{secrets.token_hex(8)}.{ext}"
                    filepath = os.path.join(upload_folder, filename)
                    archivo.save(filepath)
                    
                    foto_url = f"/static/uploads/{filename}"
                    
                    foto = FotoCita(cita_id=cita.id, url=foto_url)
                    db.session.add(foto)
                    fotos_subidas.append(foto_url)
            
            db.session.commit()
            
            return {
                'mensaje': 'Cita creada exitosamente',
                'cita': {
                    'id': cita.id,
                    'nombre': cita.nombre
                },
                'fotos_subidas': fotos_subidas,
                'total_fotos': len(fotos_subidas)
            }, 201
    
# ==================== UPLOAD IMAGEN ====================

@ns.route('/upload-imagen')
class UploadImagen(Resource):
    @jwt_required()
    def post(self):
        usuario_id = int(get_jwt_identity())
        usuario = User.query.get(usuario_id)
        if not usuario or usuario.rol_id != 1:
            return {'error': 'Acceso denegado'}, 403

        if 'imagen' not in request.files:
            return {'error': 'No se envió ninguna imagen'}, 400

        archivo = request.files['imagen']
        if not archivo or not archivo.filename:
            return {'error': 'Archivo inválido'}, 400

        allowed = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
        ext = archivo.filename.rsplit('.', 1)[-1].lower() if '.' in archivo.filename else ''
        if ext not in allowed:
            return {'error': f'Formato no permitido. Usa: {", ".join(allowed)}'}, 400

        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'citas')
        os.makedirs(upload_folder, exist_ok=True)

        filename = f"portada_{secrets.token_hex(10)}.{ext}"
        filepath = os.path.join(upload_folder, filename)
        archivo.save(filepath)

        url = f"/static/uploads/citas/{filename}"
        return {'url': url, 'mensaje': 'Imagen subida correctamente'}, 200


# ==================== ESTADISTICAS ====================

@ns.route('/estadisticas')
class AdminEstadisticas(Resource):
    @jwt_required()
    @admin_requerido
    def get(self):
        stats = AdminCitaService.obtener_estadisticas()
        return stats, 200


# ==================== BOT WHATSAPP ====================

BOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'bot_whatsapp'))
BOT_LOG_FILE = os.path.join(BOT_DIR, 'bot.log')

@ns.route('/bot/process-status')
class BotProcessStatus(Resource):
    @jwt_required()
    def get(self):
        usuario_id = int(get_jwt_identity())
        usuario = User.query.get(usuario_id)
        if not usuario or usuario.rol_id != 1:
            return {'error': 'Acceso denegado'}, 403
        global _bot_process
        pid = None
        running = False
        if _bot_process and _bot_process.poll() is None:
            pid = _bot_process.pid
            running = True
        return {'running': running, 'pid': str(pid) if pid else None}, 200

@ns.route('/bot/start')
class BotStart(Resource):
    @jwt_required()
    def post(self):
        usuario_id = int(get_jwt_identity())
        usuario = User.query.get(usuario_id)
        if not usuario or usuario.rol_id != 1:
            return {'error': 'Acceso denegado'}, 403
        global _bot_process
        if _bot_process and _bot_process.poll() is None:
            return {'mensaje': 'Bot ya está corriendo', 'pid': _bot_process.pid}, 200
        if not os.path.isdir(BOT_DIR):
            return {'error': f'Directorio del bot no encontrado: {BOT_DIR}'}, 500
        log_f = open(BOT_LOG_FILE, 'a')
        _bot_process = subprocess.Popen(
            ['node', 'server.js'],
            cwd=BOT_DIR,
            stdout=log_f,
            stderr=log_f,
        )
        return {'mensaje': 'Bot iniciado', 'pid': _bot_process.pid}, 200

@ns.route('/bot/stop')
class BotStop(Resource):
    @jwt_required()
    def post(self):
        usuario_id = int(get_jwt_identity())
        usuario = User.query.get(usuario_id)
        if not usuario or usuario.rol_id != 1:
            return {'error': 'Acceso denegado'}, 403
        global _bot_process
        if _bot_process and _bot_process.poll() is None:
            _bot_process.terminate()
            try:
                _bot_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                _bot_process.kill()
            _bot_process = None
            return {'mensaje': 'Bot detenido'}, 200
        return {'mensaje': 'Bot no estaba corriendo'}, 200

@ns.route('/bot/logs')
class BotLogs(Resource):
    @jwt_required()
    def get(self):
        usuario_id = int(get_jwt_identity())
        usuario = User.query.get(usuario_id)
        if not usuario or usuario.rol_id != 1:
            return {'error': 'Acceso denegado'}, 403
        if not os.path.isfile(BOT_LOG_FILE):
            return {'logs': 'Sin logs disponibles aún.'}, 200
        with open(BOT_LOG_FILE, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
        return {'logs': ''.join(lines[-100:])}, 200