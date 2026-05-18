from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.grupo_service import GrupoService

ns = Namespace('grupos', description='Gestion de grupos y parejas')

grupo_modelo = ns.model('Grupo', {
    'nombre': fields.String(required=True),
    'tipo': fields.String(required=True)
})

invitar_modelo = ns.model('Invitar', {
    'email': fields.String(required=True)
})

@ns.route('')
class GrupoLista(Resource):
    @jwt_required()
    def get(self):
        usuario_id = get_jwt_identity()
        grupos = GrupoService.obtener_grupos_usuario(usuario_id)
        return [{
            'id': g.id,
            'nombre': g.nombre,
            'tipo': g.tipo,
            'codigo_invitacion': g.codigo_invitacion
        } for g in grupos], 200
    
    @jwt_required()
    @ns.expect(grupo_modelo)
    def post(self):
        usuario_id = get_jwt_identity()
        data = request.get_json()
        grupo = GrupoService.crear_grupo(usuario_id, data)
        return {
            'id': grupo.id,
            'nombre': grupo.nombre,
            'tipo': grupo.tipo,
            'codigo_invitacion': grupo.codigo_invitacion
        }, 201

@ns.route('/<int:grupo_id>')
class GrupoDetalle(Resource):
    @jwt_required()
    def get(self, grupo_id):
        grupo = GrupoService.obtener_grupo(grupo_id)
        if not grupo:
            return {'error': 'Grupo no encontrado'}, 404
        miembros = GrupoService.obtener_miembros(grupo_id)
        return {
            'id': grupo.id,
            'nombre': grupo.nombre,
            'tipo': grupo.tipo,
            'codigo_invitacion': grupo.codigo_invitacion,
            'miembros': [{'id': m.id, 'nombre': m.nombre} for m in miembros]
        }, 200
    
    @jwt_required()
    def delete(self, grupo_id):
        GrupoService.eliminar_grupo(grupo_id)
        return {'mensaje': 'Grupo eliminado'}, 200

@ns.route('/<int:grupo_id>/invitar')
class InvitarMiembro(Resource):
    @jwt_required()
    @ns.expect(invitar_modelo)
    def post(self, grupo_id):
        data = request.get_json()
        resultado = GrupoService.invitar_miembro(grupo_id, data['email'])
        return resultado, 200

@ns.route('/unir/<codigo>')
class UnirGrupo(Resource):
    @jwt_required()
    def post(self, codigo):
        usuario_id = get_jwt_identity()
        grupo = GrupoService.unir_grupo(codigo, usuario_id)
        if not grupo:
            return {'error': 'Codigo invalido'}, 404
        return {'mensaje': 'Te has unido al grupo', 'grupo_id': grupo.id}, 200