from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func, extract
from ..extensions import db
from ..models import (
    Progreso, Cita, Categoria, User, GrupoMiembro, Grupo,
    Pago, PlanSuscripcion, Negocio, Departamento, FotoCita
)
from ..services.ia_service import IAService
from datetime import datetime, timedelta

ns = Namespace('reportes', description='Reportes inteligentes del sistema')

@ns.route('/general')
class ReporteGeneral(Resource):
    @jwt_required()
    def get(self):
        total_usuarios  = User.query.filter_by(activo=True).count()
        total_citas_cat = Cita.query.filter_by(activo=True).count()
        total_grupos    = Grupo.query.filter_by(activo=True).count()
        total_recuerdos = FotoCita.query.count()

        total_completadas = Progreso.query.filter_by(completado=True).count()
        pct_global = round(total_completadas / total_citas_cat * 100, 1) if total_citas_cat else 0

        cal_prom = db.session.query(func.avg(Progreso.calificacion))\
            .filter(Progreso.completado == True, Progreso.calificacion != None).scalar()
        cal_prom = round(float(cal_prom), 2) if cal_prom else 0

        ingresos = db.session.query(func.sum(Pago.monto))\
            .filter(Pago.estado == 'aprobado').scalar() or 0
        total_pagos = Pago.query.filter_by(estado='aprobado').count()

        top_citas = db.session.query(
            Cita.nombre, Categoria.nombre, func.count(Progreso.id).label('total')
        ).join(Progreso, Progreso.cita_id == Cita.id)\
         .join(Categoria, Cita.categoria_id == Categoria.id)\
         .filter(Progreso.completado == True)\
         .group_by(Cita.id).order_by(func.count(Progreso.id).desc()).limit(5).all()

        por_categoria = db.session.query(
            Categoria.nombre,
            func.count(Progreso.id).label('completadas'),
            func.count(Cita.id.distinct()).label('total_citas')
        ).join(Cita, Cita.categoria_id == Categoria.id)\
         .outerjoin(Progreso, (Progreso.cita_id == Cita.id) & (Progreso.completado == True))\
         .group_by(Categoria.id).all()

        cats_str = '; '.join(f"{c}: {comp} completadas" for c, comp, _ in por_categoria)
        top_str  = ', '.join(f"{n} ({t}x)" for n, _, t in top_citas)
        prompt = f"""Eres analista de la app "100 Citas Románticas en La Paz". Analiza estos datos del sistema completo:

- Usuarios activos: {total_usuarios}
- Citas disponibles: {total_citas_cat}
- Citas completadas en total: {total_completadas} ({pct_global}% del catálogo)
- Calificación promedio del sistema: {cal_prom}/5
- Grupos/parejas activos: {total_grupos}
- Recuerdos guardados: {total_recuerdos}
- Ingresos por suscripciones: Bs {float(ingresos):.2f} ({total_pagos} pagos aprobados)
- Completadas por categoría: {cats_str}
- Top citas más populares: {top_str}

Responde SOLO con este JSON (sin markdown):
{{"resumen": "2 oraciones sobre el estado general del sistema", "punto_fuerte": "qué funciona mejor", "punto_debil": "qué necesita atención", "conclusion": "conclusión ejecutiva en 1 oración"}}"""

        ia = IAService.consultar_ia(prompt)
        analisis = {}
        if ia.get('success'):
            import json as _j
            try:
                txt = ia['respuesta'].strip()
                if '```' in txt:
                    txt = txt.split('```')[1]
                    if txt.startswith('json'): txt = txt[4:]
                analisis = _j.loads(txt)
            except Exception:
                analisis = {'resumen': ia['respuesta'], 'punto_fuerte': '', 'punto_debil': '', 'conclusion': ''}

        return {
            'metricas': {
                'total_usuarios':    total_usuarios,
                'total_citas':       total_citas_cat,
                'total_completadas': total_completadas,
                'pct_global':        pct_global,
                'cal_promedio':      cal_prom,
                'total_grupos':      total_grupos,
                'total_recuerdos':   total_recuerdos,
                'ingresos_bs':       float(ingresos),
                'total_pagos':       total_pagos,
            },
            'top_citas': [{'nombre': n, 'categoria': c, 'total': t} for n, c, t in top_citas],
            'por_categoria': [{'categoria': c, 'completadas': comp, 'total_citas': tc} for c, comp, tc in por_categoria],
            'analisis_ia': analisis,
        }, 200


@ns.route('/tendencias')
class ReporteTendencias(Resource):
    @jwt_required()
    def get(self):
        hoy = datetime.utcnow()

        actividad_mensual = db.session.query(
            func.date_format(Progreso.fecha_completado, '%Y-%m').label('mes'),
            func.count(Progreso.id).label('total')
        ).filter(
            Progreso.completado == True,
            Progreso.fecha_completado >= hoy - timedelta(days=180)
        ).group_by('mes').order_by('mes').all()

        usuarios_activos = db.session.query(
            User.nombre, func.count(Progreso.id).label('completadas')
        ).join(Progreso, Progreso.usuario_id == User.id)\
         .filter(Progreso.completado == True)\
         .group_by(User.id).order_by(func.count(Progreso.id).desc()).limit(5).all()

        hace_30  = hoy - timedelta(days=30)
        hace_60  = hoy - timedelta(days=60)

        recientes = db.session.query(
            Categoria.nombre, func.count(Progreso.id).label('n')
        ).join(Cita, Cita.categoria_id == Categoria.id)\
         .join(Progreso, Progreso.cita_id == Cita.id)\
         .filter(Progreso.completado == True, Progreso.fecha_completado >= hace_30)\
         .group_by(Categoria.id).all()

        anteriores = db.session.query(
            Categoria.nombre, func.count(Progreso.id).label('n')
        ).join(Cita, Cita.categoria_id == Categoria.id)\
         .join(Progreso, Progreso.cita_id == Cita.id)\
         .filter(Progreso.completado == True,
                 Progreso.fecha_completado >= hace_60,
                 Progreso.fecha_completado < hace_30)\
         .group_by(Categoria.id).all()

        rec_map = {c: n for c, n in recientes}
        ant_map = {c: n for c, n in anteriores}
        todas_cats = set(list(rec_map.keys()) + list(ant_map.keys()))
        tendencia_cats = []
        for cat in todas_cats:
            r, a = rec_map.get(cat, 0), ant_map.get(cat, 0)
            delta = r - a
            pct   = round((delta / a * 100), 1) if a else 100.0
            tendencia_cats.append({'categoria': cat, 'recientes': r, 'anteriores': a, 'delta': delta, 'pct_cambio': pct})
        tendencia_cats.sort(key=lambda x: x['delta'], reverse=True)

        cal_por_cat = db.session.query(
            Categoria.nombre,
            func.avg(Progreso.calificacion).label('promedio'),
            func.count(Progreso.id).label('n')
        ).join(Cita, Cita.categoria_id == Categoria.id)\
         .join(Progreso, Progreso.cita_id == Cita.id)\
         .filter(Progreso.completado == True, Progreso.calificacion != None)\
         .group_by(Categoria.id).all()

        meses_str = ', '.join(f"{m}: {t}" for m, t in actividad_mensual)
        trend_str = ', '.join(f"{t['categoria']} {'+' if t['delta']>=0 else ''}{t['delta']}" for t in tendencia_cats[:5])
        top_u_str = ', '.join(f"{n} ({c} citas)" for n, c in usuarios_activos)

        prompt = f"""Eres analista de la app "100 Citas Románticas en La Paz". Analiza las tendencias:

- Actividad mensual (últimos 6 meses): {meses_str}
- Variación de categorías (últimos 30 días vs 30 anteriores): {trend_str}
- Usuarios más activos: {top_u_str}

Responde SOLO con este JSON (sin markdown):
{{"tendencia_general": "describe la tendencia de actividad en 2 oraciones", "categoria_en_auge": "categoría con más crecimiento y por qué", "alerta": "algo que preocupa o merece atención", "recomendacion": "qué hacer para mantener o mejorar el ritmo"}}"""

        ia = IAService.consultar_ia(prompt)
        analisis = {}
        if ia.get('success'):
            import json as _j
            try:
                txt = ia['respuesta'].strip()
                if '```' in txt:
                    txt = txt.split('```')[1]
                    if txt.startswith('json'): txt = txt[4:]
                analisis = _j.loads(txt)
            except Exception:
                analisis = {'tendencia_general': ia['respuesta'], 'categoria_en_auge': '', 'alerta': '', 'recomendacion': ''}

        return {
            'actividad_mensual':  [{'mes': m, 'total': t} for m, t in actividad_mensual],
            'usuarios_activos':   [{'nombre': n, 'completadas': c} for n, c in usuarios_activos],
            'tendencia_categorias': tendencia_cats,
            'calificacion_por_categoria': [
                {'categoria': c, 'promedio': round(float(p), 2), 'n': n} for c, p, n in cal_por_cat
            ],
            'analisis_ia': analisis,
        }, 200


@ns.route('/prediccion')
class ReportePrediccion(Resource):
    @jwt_required()
    def get(self):
        hoy = datetime.utcnow()

        meses = db.session.query(
            func.date_format(Progreso.fecha_completado, '%Y-%m').label('mes'),
            func.count(Progreso.id).label('total')
        ).filter(
            Progreso.completado == True,
            Progreso.fecha_completado >= hoy - timedelta(days=150)
        ).group_by('mes').order_by('mes').all()

        totales = [t for _, t in meses]
        promedio_mensual = round(sum(totales) / len(totales), 1) if totales else 0
        ultimo_mes = totales[-1] if totales else 0
        proyeccion_3m = round(promedio_mensual * 3, 0)

        citas_sin_completar = db.session.query(Cita.nombre, Categoria.nombre)\
            .join(Categoria, Cita.categoria_id == Categoria.id)\
            .outerjoin(Progreso, Progreso.cita_id == Cita.id)\
            .filter(Cita.activo == True, Progreso.id == None)\
            .limit(6).all()

        hace_30 = hoy - timedelta(days=30)
        usuarios_inactivos = db.session.query(
            User.nombre,
            func.max(Progreso.fecha_completado).label('ultima_actividad'),
            func.count(Progreso.id).label('total')
        ).join(Progreso, Progreso.usuario_id == User.id)\
         .filter(Progreso.completado == True)\
         .group_by(User.id)\
         .having(func.max(Progreso.fecha_completado) < hace_30)\
         .all()

        cats_baja = []
        for cat in Categoria.query.all():
            total_cat = Cita.query.filter_by(categoria_id=cat.id, activo=True).count()
            comp_cat  = Progreso.query.join(Cita, Progreso.cita_id == Cita.id)\
                .filter(Cita.categoria_id == cat.id, Progreso.completado == True).count()
            if total_cat > 0:
                pct = round(comp_cat / total_cat * 100, 1)
                if pct < 30:
                    cats_baja.append({'categoria': cat.nombre, 'pct': pct, 'completadas': comp_cat, 'total': total_cat})
        cats_baja.sort(key=lambda x: x['pct'])

        plan_popular = db.session.query(
            PlanSuscripcion.nombre, func.count(Pago.id).label('n')
        ).join(Pago, Pago.plan_id == PlanSuscripcion.id)\
         .filter(Pago.estado == 'aprobado')\
         .group_by(PlanSuscripcion.id).order_by(func.count(Pago.id).desc()).first()

        dormidas_str  = ', '.join(f"{c} ({cat})" for c, cat in citas_sin_completar[:4])
        inactivos_str = ', '.join(f"{n} (última: {str(u)[:10]})" for n, u, _ in usuarios_inactivos[:3])
        baja_str      = ', '.join(f"{c['categoria']} {c['pct']}%" for c in cats_baja[:4])

        prompt = f"""Eres analista predictivo de la app "100 Citas Románticas en La Paz". Genera predicciones y recomendaciones:

- Promedio de citas completadas por mes: {promedio_mensual}
- Último mes registrado: {ultimo_mes}
- Proyección para los próximos 3 meses: {proyeccion_3m} citas
- Citas que nadie ha completado aún: {dormidas_str if dormidas_str else 'ninguna'}
- Usuarios sin actividad en 30+ días: {inactivos_str if inactivos_str else 'ninguno'}
- Categorías con baja adopción (<30%): {baja_str if baja_str else 'ninguna'}
- Plan más contratado: {plan_popular[0] if plan_popular else 'sin datos'}

Responde SOLO con este JSON (sin markdown):
{{"prediccion": "qué se espera en los próximos meses en 2 oraciones", "riesgo_principal": "el mayor riesgo detectado", "recomendaciones": ["acción concreta 1", "acción concreta 2", "acción concreta 3"], "oportunidad": "la mayor oportunidad de crecimiento detectada"}}"""

        ia = IAService.consultar_ia(prompt)
        analisis = {}
        if ia.get('success'):
            import json as _j
            try:
                txt = ia['respuesta'].strip()
                if '```' in txt:
                    txt = txt.split('```')[1]
                    if txt.startswith('json'): txt = txt[4:]
                analisis = _j.loads(txt)
            except Exception:
                analisis = {'prediccion': ia['respuesta'], 'riesgo_principal': '', 'recomendaciones': [], 'oportunidad': ''}

        return {
            'proyeccion': {
                'promedio_mensual': promedio_mensual,
                'ultimo_mes':       ultimo_mes,
                'proyeccion_3m':    proyeccion_3m,
                'historial':        [{'mes': m, 'total': t} for m, t in meses],
            },
            'citas_sin_completar':  [{'nombre': n, 'categoria': c} for n, c in citas_sin_completar],
            'usuarios_inactivos':   [{'nombre': n, 'ultima_actividad': str(u)[:10], 'total': t} for n, u, t in usuarios_inactivos],
            'categorias_baja_adopcion': cats_baja,
            'plan_popular': plan_popular[0] if plan_popular else None,
            'analisis_ia': analisis,
        }, 200
