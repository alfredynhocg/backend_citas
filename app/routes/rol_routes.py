from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models import Role, User

ns = Namespace('roles', description='Gestión de roles')

rol_modelo = ns.model('Rol', {
    'nombre': fields.String(required=True),
})

def _admin_check():
    uid = int(get_jwt_identity())
    user = db.session.get(User, uid)
    if not user or user.rol_id != 1:
        ns.abort(403, 'Solo administradores')

def _serializar(r):
    return {
        'id': r.id,
        'nombre': r.nombre,
        'total_usuarios': len(r.usuarios),
    }

@ns.route('')
class RolLista(Resource):
    @jwt_required()
    def get(self):
        """Listar todos los roles"""
        roles = Role.query.order_by(Role.id).all()
        return [_serializar(r) for r in roles], 200

    @jwt_required()
    @ns.expect(rol_modelo)
    def post(self):
        """Crear nuevo rol (admin)"""
        _admin_check()
        data = request.get_json()
        nombre = (data.get('nombre') or '').strip()
        if not nombre:
            return {'message': 'El nombre es requerido'}, 400
        if Role.query.filter_by(nombre=nombre).first():
            return {'message': 'Ya existe un rol con ese nombre'}, 400
        rol = Role(nombre=nombre)
        db.session.add(rol)
        db.session.commit()
        return _serializar(rol), 201


@ns.route('/<int:rol_id>')
class RolDetalle(Resource):
    @jwt_required()
    def get(self, rol_id):
        """Obtener un rol"""
        rol = db.session.get(Role, rol_id)
        if not rol:
            return {'message': 'Rol no encontrado'}, 404
        return _serializar(rol), 200

    @jwt_required()
    @ns.expect(rol_modelo)
    def put(self, rol_id):
        """Actualizar nombre de un rol (admin)"""
        _admin_check()
        rol = db.session.get(Role, rol_id)
        if not rol:
            return {'message': 'Rol no encontrado'}, 404
        data = request.get_json()
        nombre = (data.get('nombre') or '').strip()
        if not nombre:
            return {'message': 'El nombre es requerido'}, 400
        conflicto = Role.query.filter_by(nombre=nombre).first()
        if conflicto and conflicto.id != rol_id:
            return {'message': 'Ya existe un rol con ese nombre'}, 400
        rol.nombre = nombre
        db.session.commit()
        return _serializar(rol), 200

    @jwt_required()
    def delete(self, rol_id):
        """Eliminar rol (admin) — solo si no tiene usuarios"""
        _admin_check()
        rol = db.session.get(Role, rol_id)
        if not rol:
            return {'message': 'Rol no encontrado'}, 404
        if rol.usuarios:
            return {'message': f'No se puede eliminar: {len(rol.usuarios)} usuario(s) tienen este rol'}, 400
        db.session.delete(rol)
        db.session.commit()
        return {'message': 'Rol eliminado'}, 200
