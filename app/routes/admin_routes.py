from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.admin_service import AdminService
from ..utils.decoradores import admin_requerido

ns = Namespace('admin', description='Administracion', decorators=[admin_requerido])

@ns.route('/pagos/pendientes')
class PagosPendientes(Resource):
    @jwt_required()
    def get(self):
        pagos = AdminService.obtener_pagos_pendientes()
        return [{
            'id': p.id,
            'usuario': p.usuario.nombre,
            'monto': float(p.monto),
            'comprobante_url': p.comprobante_url,
            'fecha_pago': str(p.fecha_pago)
        } for p in pagos], 200

@ns.route('/pagos/<int:pago_id>/aprobar')
class AprobarPago(Resource):
    @jwt_required()
    def post(self, pago_id):
        admin_id = get_jwt_identity()
        resultado = AdminService.aprobar_pago(pago_id, admin_id)
        return resultado, 200

@ns.route('/negocios/pendientes')
class NegociosPendientes(Resource):
    @jwt_required()
    def get(self):
        negocios = AdminService.obtener_negocios_pendientes()
        return [{
            'id': n.id,
            'nombre': n.nombre,
            'categoria_negocio': n.categoria_negocio,
            'departamento': n.departamento.nombre if n.departamento else None
        } for n in negocios], 200

@ns.route('/negocios/<int:negocio_id>/aprobar')
class AprobarNegocio(Resource):
    @jwt_required()
    def post(self, negocio_id):
        AdminService.aprobar_negocio(negocio_id)
        return {'mensaje': 'Negocio aprobado'}, 200

@ns.route('/reportes')
class Reportes(Resource):
    @jwt_required()
    def get(self):
        reportes = AdminService.obtener_reportes()
        return reportes, 200