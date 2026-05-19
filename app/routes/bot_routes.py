from flask_restx import Namespace, Resource
from flask import request
from ..models import db, Categoria, Cita, Negocio, Departamento, Grupo, GrupoMiembro, User
from ..services.suscripcion_service import SuscripcionService
from sqlalchemy import func

ns = Namespace('bot', description='Endpoints publicos para el bot de WhatsApp')


@ns.route('/categorias')
class BotCategorias(Resource):
    def get(self):
        """Categorias con conteo de citas activas"""
        categorias = Categoria.query.all()
        return {
            'categorias': [{
                'id': c.id,
                'nombre': c.nombre,
                'total_citas': Cita.query.filter_by(categoria_id=c.id, activo=True).count()
            } for c in categorias]
        }, 200


@ns.route('/citas')
class BotCitas(Resource):
    def get(self):
        """Listado de citas activas con filtros opcionales"""
        categoria_id = request.args.get('categoria_id', type=int)
        limit = request.args.get('limit', 20, type=int)

        q = Cita.query.filter_by(activo=True)
        if categoria_id:
            q = q.filter_by(categoria_id=categoria_id)
        citas = q.order_by(Cita.puntos.desc()).limit(limit).all()

        return {
            'total': len(citas),
            'citas': [{
                'id': c.id,
                'nombre': c.nombre,
                'descripcion': c.descripcion,
                'categoria_nombre': c.categoria.nombre if c.categoria else None,
                'departamento_nombre': c.departamento.nombre if c.departamento else None,
                'negocio_nombre': c.negocio.nombre if c.negocio else None,
                'direccion': c.direccion,
                'puntos': c.puntos,
                'portada_url': c.portada_url,
            } for c in citas]
        }, 200


@ns.route('/negocios')
class BotNegocios(Resource):
    def get(self):
        """Negocios activos"""
        negocios = Negocio.query.filter_by(activo=True).all()
        return {
            'negocios': [{
                'id': n.id,
                'nombre': n.nombre,
                'direccion': n.direccion,
                'telefono': n.telefono,
                'categoria_negocio': n.categoria_negocio,
                'logo_url': n.logo_url,
                'activo': n.activo,
            } for n in negocios]
        }, 200


@ns.route('/estadisticas')
class BotEstadisticas(Resource):
    def get(self):
        """Estadisticas generales del sistema"""
        total_citas = Cita.query.count()
        citas_activas = Cita.query.filter_by(activo=True).count()
        total_categorias = Categoria.query.count()
        total_negocios = Negocio.query.count()
        negocios_activos = Negocio.query.filter_by(activo=True).count()

        citas_por_categoria = db.session.query(
            Categoria.nombre,
            func.count(Cita.id).label('total')
        ).outerjoin(Cita, Cita.categoria_id == Categoria.id).group_by(Categoria.id).all()

        return {
            'total_citas': total_citas,
            'citas_activas': citas_activas,
            'total_categorias': total_categorias,
            'total_negocios': total_negocios,
            'negocios_activos': negocios_activos,
            'citas_por_categoria': [{'categoria': r[0] or 'Sin categoria', 'total': r[1]} for r in citas_por_categoria]
        }, 200


@ns.route('/planes')
class BotPlanes(Resource):
    def get(self):
        """Planes de suscripcion disponibles"""
        try:
            from ..models import Plan
            planes = Plan.query.filter_by(activo=True).all()
            return {
                'planes': [{
                    'id': p.id,
                    'nombre': p.nombre,
                    'descripcion': p.descripcion if hasattr(p, 'descripcion') else None,
                    'precio_mensual': float(p.precio_mensual) if p.precio_mensual else 0,
                    'precio_anual': float(p.precio_anual) if hasattr(p, 'precio_anual') and p.precio_anual else 0,
                    'ventajas': p.ventajas if hasattr(p, 'ventajas') else None,
                } for p in planes]
            }, 200
        except Exception:
            return {
                'planes': [
                    {'nombre': 'Free', 'descripcion': 'Acceso basico', 'precio_mensual': 0, 'precio_anual': 0},
                    {'nombre': 'Pareja', 'descripcion': 'Para parejas', 'precio_mensual': 29, 'precio_anual': 290},
                    {'nombre': 'Aventureros', 'descripcion': 'Para grupos', 'precio_mensual': 59, 'precio_anual': 590},
                ]
            }, 200


@ns.route('/parejas')
class BotParejas(Resource):
    def get(self):
        """Parejas registradas en el sistema"""
        grupos = Grupo.query.filter_by(tipo='pareja', activo=True).all()
        resultado = []
        for g in grupos:
            miembros = (GrupoMiembro.query
                        .filter_by(grupo_id=g.id)
                        .join(User, GrupoMiembro.usuario_id == User.id)
                        .all())
            datos = [{'id': m.usuario_id, 'nombre': m.usuario.nombre} for m in miembros if m.usuario]
            if len(datos) == 2:
                resultado.append({
                    'id': g.id,
                    'nombre': g.nombre,
                    'miembro1': datos[0],
                    'miembro2': datos[1],
                })
        return resultado, 200
