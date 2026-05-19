from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from ..extensions import db
from ..models import Progreso, Cita, Categoria, GrupoMiembro

ns = Namespace('dashboard', description='Dashboard del usuario')


@ns.route('/resumen')
class DashboardResumen(Resource):
    @jwt_required()
    def get(self):
        usuario_id = int(get_jwt_identity())

        total_citas = Cita.query.filter_by(activo=True).count()

        completadas_q = (
            Progreso.query
            .filter_by(usuario_id=usuario_id, completado=True)
            .all()
        )
        total_completadas = len(completadas_q)
        total_recuerdos = sum(1 for p in completadas_q if p.anecdota or p.calificacion)
        pendientes = max(0, total_citas - total_completadas)

        total_parejas = (
            GrupoMiembro.query
            .filter_by(usuario_id=usuario_id)
            .count()
        )

        citas_recientes = (
            Progreso.query
            .filter_by(usuario_id=usuario_id, completado=True)
            .order_by(Progreso.fecha_completado.desc())
            .limit(5)
            .all()
        )

        citas_recientes_data = []
        for p in citas_recientes:
            cita = p.cita
            citas_recientes_data.append({
                'id': p.id,
                'nombre': cita.nombre if cita else None,
                'categoria': cita.categoria.nombre if cita and cita.categoria else None,
                'calificacion': p.calificacion,
                'fecha_completado': str(p.fecha_completado) if p.fecha_completado else None,
                'portada_url': cita.portada_url if cita else None,
            })

        categorias = Categoria.query.all()
        progreso_categorias = []
        for cat in categorias:
            total_cat = Cita.query.filter_by(categoria_id=cat.id, activo=True).count()
            if total_cat == 0:
                continue
            completadas_cat = (
                Progreso.query
                .join(Cita, Progreso.cita_id == Cita.id)
                .filter(
                    Progreso.usuario_id == usuario_id,
                    Progreso.completado == True,
                    Cita.categoria_id == cat.id,
                )
                .count()
            )
            progreso_categorias.append({
                'id': cat.id,
                'nombre': cat.nombre,
                'total': total_cat,
                'completadas': completadas_cat,
            })

        return {
            'total_completadas': total_completadas,
            'total_recuerdos': total_recuerdos,
            'total_parejas': total_parejas,
            'total_citas': total_citas,
            'pendientes': pendientes,
            'citas_recientes': citas_recientes_data,
            'progreso_categorias': progreso_categorias,
        }, 200
