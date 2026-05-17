# app/routes/usuario_routes.py
from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import date
from ..services.usuario_service import UsuarioService
from ..utils.decoradores import admin_requerido

ns = Namespace('usuarios', description='Gestion de usuarios')

usuario_modelo = ns.model('Usuario', {
    'nombre': fields.String,
    'email': fields.String,
    'departamento_actual': fields.String,
    'activo': fields.Boolean
})

actualizar_modelo = ns.model('ActualizarUsuario', {
    'nombre': fields.String,
    'departamento_actual': fields.String
})

cambiar_password_modelo = ns.model('CambiarPassword', {
    'password_actual': fields.String(required=True),
    'password_nuevo': fields.String(required=True)
})

elegir_pareja_modelo = ns.model('ElegirPareja', {
    'codigo_invitacion': fields.String(required=True)
})

crear_pareja_modelo = ns.model('CrearPareja', {
    'nombre_pareja': fields.String(required=True),
    'email_pareja': fields.String(required=True)
})

suscripcion_modelo = ns.model('Suscripcion', {
    'plan_id': fields.Integer(required=True),
    'tipo': fields.String(required=True),
    'tipo_periodo': fields.String(required=True),
    'grupo_id': fields.Integer
})

pago_modelo = ns.model('Pago', {
    'suscripcion_id': fields.Integer(required=True),
    'metodo_pago': fields.String(required=True),
    'comprobante_url': fields.String
})

verificar_email_modelo = ns.model('VerificarEmail', {
    'codigo': fields.String(required=True)
})

cambiar_departamento_modelo = ns.model('CambiarDepartamento', {
    'departamento': fields.String(required=True)
})

@ns.route('')
class UsuarioLista(Resource):
    @jwt_required()
    def get(self):
        # Verificá manualmente si es admin
        usuario_id = get_jwt_identity()
        usuario = UsuarioService.obtener_por_id(usuario_id)
        if not usuario or usuario.rol_id != 1:
            return {'error': 'Acceso denegado. Se requieren permisos de administrador'}, 403
        
        usuarios = UsuarioService.obtener_todos()
        return [{
            'id': u.id,
            'nombre': u.nombre,
            'email': u.email,
            'departamento_actual': u.departamento_actual,
            'activo': u.activo,
            'fecha_registro': str(u.fecha_registro)
        } for u in usuarios], 200

@ns.route('/perfil')
class MiPerfil(Resource):
    @jwt_required()
    def get(self):
        usuario_id = get_jwt_identity()
        return UsuarioService.obtener_perfil_completo(usuario_id), 200
@ns.route('/<int:usuario_id>')
class UsuarioDetalle(Resource):
    @jwt_required()
    def get(self, usuario_id):
        usuario_actual = get_jwt_identity()
        if usuario_actual != usuario_id:
            return {'error': 'No autorizado'}, 403
        usuario = UsuarioService.obtener_por_id(usuario_id)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        return {
            'id': usuario.id,
            'nombre': usuario.nombre,
            'email': usuario.email,
            'departamento_actual': usuario.departamento_actual,
            'fecha_registro': str(usuario.fecha_registro),
            'activo': usuario.activo
        }, 200
    
    @jwt_required()
    @ns.expect(actualizar_modelo)
    def put(self, usuario_id):
        usuario_actual = get_jwt_identity()
        if usuario_actual != usuario_id:
            return {'error': 'No autorizado'}, 403
        data = request.get_json()
        usuario = UsuarioService.actualizar(usuario_id, data)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        return {
            'id': usuario.id,
            'nombre': usuario.nombre,
            'departamento_actual': usuario.departamento_actual
        }, 200
    
    @jwt_required()
    def delete(self, usuario_id):
        usuario_actual = get_jwt_identity()
        if usuario_actual != usuario_id:
            return {'error': 'No autorizado'}, 403
        UsuarioService.desactivar(usuario_id)
        return {'mensaje': 'Usuario desactivado'}, 200


@ns.route('/cambiar-password')
class CambiarPassword(Resource):
    @jwt_required()
    @ns.expect(cambiar_password_modelo)
    def post(self):
        usuario_id = get_jwt_identity()
        data = request.get_json()
        resultado = UsuarioService.cambiar_password(usuario_id, data)
        if resultado:
            return {'mensaje': 'Password actualizado'}, 200
        return {'error': 'Password actual incorrecto'}, 400


@ns.route('/crear-pareja')
class CrearPareja(Resource):
    @jwt_required()
    @ns.expect(crear_pareja_modelo)
    def post(self):
        usuario_id = get_jwt_identity()
        data = request.get_json()
        resultado = UsuarioService.crear_invitar_pareja(usuario_id, data)
        return resultado


@ns.route('/unir-pareja')
class UnirPareja(Resource):
    @jwt_required()
    @ns.expect(elegir_pareja_modelo)
    def post(self):
        usuario_id = get_jwt_identity()
        data = request.get_json()
        resultado = UsuarioService.unir_pareja(usuario_id, data['codigo_invitacion'])
        if resultado:
            return {'mensaje': 'Te has unido a la pareja', 'grupo_id': resultado.id}, 200
        return {'error': 'Codigo invalido'}, 404


@ns.route('/mi-pareja')
class MiPareja(Resource):
    @jwt_required()
    def get(self):
        usuario_id = get_jwt_identity()
        pareja = UsuarioService.obtener_pareja(usuario_id)
        if not pareja:
            return {'mensaje': 'No tienes pareja vinculada'}, 404
        progreso_pareja = UsuarioService.obtener_progreso_pareja(usuario_id)
        return {
            'pareja': {
                'id': pareja.id,
                'nombre': pareja.nombre,
                'email': pareja.email
            },
            'progreso_pareja': {
                'citas_completadas': progreso_pareja['completadas'],
                'puntos_totales': progreso_pareja['puntos'],
                'racha_actual': progreso_pareja['racha']
            }
        }, 200


@ns.route('/desvincular-pareja')
class DesvincularPareja(Resource):
    @jwt_required()
    def post(self):
        usuario_id = get_jwt_identity()
        resultado = UsuarioService.desvincular_pareja(usuario_id)
        if resultado:
            return {'mensaje': 'Pareja desvinculada'}, 200
        return {'error': 'No se pudo desvincular'}, 400


@ns.route('/suscripciones')
class MisSuscripciones(Resource):
    @jwt_required()
    def get(self):
        usuario_id = get_jwt_identity()
        suscripciones = UsuarioService.obtener_suscripciones(usuario_id)
        suscripcion_activa = UsuarioService.obtener_suscripcion_activa(usuario_id)
        return {
            'suscripcion_activa': {
                'id': s.id,
                'plan': s.plan.nombre if s.plan else 'N/A',
                'fecha_inicio': str(s.fecha_inicio),
                'fecha_expiracion': str(s.fecha_expiracion),
                'dias_restantes': (s.fecha_expiracion - date.today()).days if s.fecha_expiracion else 0
            } if suscripcion_activa else None,
            'historial': [{
                'id': s.id,
                'plan': s.plan.nombre if s.plan else 'N/A',
                'fecha_inicio': str(s.fecha_inicio),
                'fecha_expiracion': str(s.fecha_expiracion),
                'activo': s.activo
            } for s in suscripciones]
        }, 200


@ns.route('/contratar-suscripcion')
class ContratarSuscripcion(Resource):
    @jwt_required()
    @ns.expect(suscripcion_modelo)
    def post(self):
        usuario_id = get_jwt_identity()
        data = request.get_json()
        resultado = UsuarioService.contratar_suscripcion(usuario_id, data)
        return resultado


@ns.route('/realizar-pago')
class RealizarPago(Resource):
    @jwt_required()
    @ns.expect(pago_modelo)
    def post(self):
        usuario_id = get_jwt_identity()
        data = request.get_json()
        pago = UsuarioService.realizar_pago(usuario_id, data)
        if not pago:
            return {'error': 'Error al procesar pago'}, 400
        return {
            'id': pago.id,
            'monto': float(pago.monto),
            'estado': pago.estado,
            'mensaje': 'Pago registrado. Esperando aprobacion del administrador.'
        }, 201


@ns.route('/mis-pagos')
class MisPagos(Resource):
    @jwt_required()
    def get(self):
        usuario_id = get_jwt_identity()
        pagos = UsuarioService.obtener_pagos_usuario(usuario_id)
        return [{
            'id': p.id,
            'monto': float(p.monto),
            'metodo_pago': p.metodo_pago,
            'estado': p.estado,
            'fecha_pago': str(p.fecha_pago),
            'comprobante_url': p.comprobante_url
        } for p in pagos], 200


@ns.route('/progreso')
class MiProgreso(Resource):
    @jwt_required()
    def get(self):
        usuario_id = get_jwt_identity()
        progreso = UsuarioService.obtener_progreso_completo(usuario_id)
        return {
            'estadisticas': {
                'total_citas': progreso['total'],
                'completadas': progreso['completadas'],
                'pendientes': progreso['total'] - progreso['completadas'],
                'porcentaje': round((progreso['completadas'] / progreso['total']) * 100, 2) if progreso['total'] > 0 else 0,
                'puntos_totales': progreso['puntos'],
                'racha_actual': progreso['racha'],
                'racha_maxima': progreso['racha_maxima']
            },
            'ultimas_citas': [{
                'cita': p.get('cita'),
                'calificacion': p.get('calificacion'),
                'fecha': str(p.get('fecha_completado')) if p.get('fecha_completado') else None
            } for p in progreso['ultimas']],
            'categorias_progreso': progreso['por_categoria']
        }, 200


@ns.route('/certificados')
class MisCertificados(Resource):
    @jwt_required()
    def get(self):
        usuario_id = get_jwt_identity()
        certificados = UsuarioService.obtener_certificados(usuario_id)
        return [{
            'id': c.id,
            'nivel': c.nivel,
            'fecha': str(c.fecha),
            'pdf_url': c.pdf_url
        } for c in certificados], 200


@ns.route('/verificar-email')
class VerificarEmail(Resource):
    @jwt_required()
    def post(self):
        usuario_id = get_jwt_identity()
        resultado = UsuarioService.enviar_codigo_verificacion(usuario_id)
        if resultado:
            return {'mensaje': 'Codigo enviado a tu email'}, 200
        return {'error': 'Error al enviar codigo'}, 500


@ns.route('/verificar-email/codigo')
class ConfirmarEmail(Resource):
    @jwt_required()
    @ns.expect(verificar_email_modelo)
    def post(self):
        usuario_id = get_jwt_identity()
        data = request.get_json()
        resultado = UsuarioService.verificar_email(usuario_id, data['codigo'])
        if resultado:
            return {'mensaje': 'Email verificado correctamente'}, 200
        return {'error': 'Codigo invalido'}, 400


@ns.route('/departamentos-disponibles')
class DepartamentosDisponibles(Resource):
    @jwt_required()
    def get(self):
        usuario_id = get_jwt_identity()
        departamentos = UsuarioService.obtener_departamentos_desbloqueados(usuario_id)
        return {
            'departamento_actual': UsuarioService.obtener_departamento_actual(usuario_id),
            'departamentos_gratis': [{'id': d.id, 'nombre': d.nombre} for d in departamentos['gratis']],
            'departamentos_premium': [{'id': d.id, 'nombre': d.nombre} for d in departamentos['premium']]
        }, 200


@ns.route('/cambiar-departamento')
class CambiarDepartamento(Resource):
    @jwt_required()
    @ns.expect(cambiar_departamento_modelo)
    def post(self):
        usuario_id = get_jwt_identity()
        data = request.get_json()
        resultado = UsuarioService.cambiar_departamento_actual(usuario_id, data['departamento'])
        if resultado:
            return {'mensaje': f'Departamento cambiado a {data["departamento"]}'}, 200
        return {'error': 'No tienes acceso a ese departamento'}, 403


@ns.route('/estadisticas')
class EstadisticasGlobales(Resource):
    @jwt_required()
    @admin_requerido
    def get(self):
        stats = UsuarioService.obtener_estadisticas_globales()
        return {
            'total_usuarios': stats['total_usuarios'],
            'usuarios_activos': stats['usuarios_activos'],
            'usuarios_premium': stats['usuarios_premium'],
            'total_parejas': stats['total_parejas'],
            'citas_completadas_total': stats['citas_completadas'],
            'ingresos_totales': float(stats['ingresos']),
            'top_usuarios': stats['top']
        }, 200