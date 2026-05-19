from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, User, WaEtiqueta, WaConversacion, wa_conv_etiqueta

ns = Namespace('whatsapp', description='Gestion de etiquetas y conversaciones WhatsApp')


def _admin_check():
    uid = int(get_jwt_identity())
    u = User.query.get(uid)
    return u and u.rol_id == 1


@ns.route('/etiquetas')
class EtiquetaLista(Resource):
    @jwt_required()
    def get(self):
        if not _admin_check():
            return {'error': 'Acceso denegado'}, 403
        etiquetas = WaEtiqueta.query.order_by(WaEtiqueta.id).all()
        return {'data': [{'id': e.id, 'nombre': e.nombre, 'color': e.color} for e in etiquetas]}, 200

    @jwt_required()
    def post(self):
        if not _admin_check():
            return {'error': 'Acceso denegado'}, 403
        data = request.get_json()
        nombre = (data.get('nombre') or '').strip()
        if not nombre:
            return {'error': 'Nombre requerido'}, 400
        if WaEtiqueta.query.filter_by(nombre=nombre).first():
            return {'error': 'Ya existe una etiqueta con ese nombre'}, 400
        e = WaEtiqueta(nombre=nombre, color=data.get('color', '#6366f1'))
        db.session.add(e)
        db.session.commit()
        return {'id': e.id, 'nombre': e.nombre, 'color': e.color}, 201


@ns.route('/etiquetas/<int:etiqueta_id>')
class EtiquetaDetalle(Resource):
    @jwt_required()
    def put(self, etiqueta_id):
        if not _admin_check():
            return {'error': 'Acceso denegado'}, 403
        e = WaEtiqueta.query.get(etiqueta_id)
        if not e:
            return {'error': 'Etiqueta no encontrada'}, 404
        data = request.get_json()
        if 'nombre' in data and data['nombre'].strip():
            e.nombre = data['nombre'].strip()
        if 'color' in data:
            e.color = data['color']
        db.session.commit()
        return {'id': e.id, 'nombre': e.nombre, 'color': e.color}, 200

    @jwt_required()
    def delete(self, etiqueta_id):
        if not _admin_check():
            return {'error': 'Acceso denegado'}, 403
        e = WaEtiqueta.query.get(etiqueta_id)
        if not e:
            return {'error': 'Etiqueta no encontrada'}, 404
        db.session.delete(e)
        db.session.commit()
        return {'mensaje': 'Etiqueta eliminada'}, 200



@ns.route('/conversaciones/<string:phone>/etiquetas')
class ConvEtiquetas(Resource):
    @jwt_required()
    def post(self, phone):
        if not _admin_check():
            return {'error': 'Acceso denegado'}, 403
        conv = WaConversacion.query.filter_by(phone=phone).first()
        if not conv:
            return {'error': 'Conversacion no encontrada'}, 404
        data = request.get_json()
        ids = data.get('etiqueta_ids', [])
        etiquetas = WaEtiqueta.query.filter(WaEtiqueta.id.in_(ids)).all()
        conv.etiquetas = etiquetas
        db.session.commit()
        return {
            'etiquetas': [{'id': e.id, 'nombre': e.nombre, 'color': e.color} for e in conv.etiquetas]
        }, 200



@ns.route('/upsert-conversacion')
class UpsertConversacion(Resource):
    def post(self):
        """Llamado por el bot Node.js para registrar/actualizar una conversacion"""
        data = request.get_json()
        phone = (data.get('phone') or '').strip()
        if not phone:
            return {'error': 'phone requerido'}, 400
        conv = WaConversacion.query.filter_by(phone=phone).first()
        if not conv:
            conv = WaConversacion(phone=phone)
            db.session.add(conv)
        if data.get('nombre') is not None:
            conv.nombre = data['nombre']
        if data.get('estado') is not None:
            conv.estado = data['estado']
        db.session.commit()
        return {'id': conv.id}, 200
