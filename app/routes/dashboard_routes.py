from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from ..extensions import db
from ..models import Progreso, Cita, Categoria, GrupoMiembro, User, Pago, Suscripcion
from ..services.ia_service import IAService
from datetime import datetime, timedelta

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

        cals = [p.calificacion for p in completadas_q if p.calificacion]
        cal_promedio = round(sum(cals) / len(cals), 1) if cals else None

        mejor = max(completadas_q, key=lambda p: p.calificacion or 0, default=None)
        cita_favorita = None
        if mejor and mejor.cita:
            cita_favorita = {
                'nombre': mejor.cita.nombre,
                'calificacion': mejor.calificacion,
                'categoria': mejor.cita.categoria.nombre if mejor.cita.categoria else None,
            }

        fechas = sorted(set(
            p.fecha_completado.date() for p in completadas_q if p.fecha_completado
        ), reverse=True)
        racha = 0
        hoy = datetime.utcnow().date()
        for i, f in enumerate(fechas):
            esperado = hoy - timedelta(days=i)
            if f == esperado:
                racha += 1
            else:
                break

        actividad_mensual = {}
        for p in completadas_q:
            if not p.fecha_completado:
                continue
            key = p.fecha_completado.strftime('%Y-%m')
            actividad_mensual[key] = actividad_mensual.get(key, 0) + 1
        actividad_mensual = [
            {'mes': k, 'citas': v}
            for k, v in sorted(actividad_mensual.items())[-6:]
        ]

        return {
            'total_completadas': total_completadas,
            'total_recuerdos': total_recuerdos,
            'total_parejas': total_parejas,
            'total_citas': total_citas,
            'pendientes': pendientes,
            'cal_promedio': cal_promedio,
            'cita_favorita': cita_favorita,
            'racha_dias': racha,
            'actividad_mensual': actividad_mensual,
            'citas_recientes': citas_recientes_data,
            'progreso_categorias': progreso_categorias,
        }, 200


@ns.route('/analisis-ia')
class DashboardAnalisisIA(Resource):
    @jwt_required()
    def get(self):
        usuario_id = int(get_jwt_identity())
        usuario = User.query.get(usuario_id)

        total_citas = Cita.query.filter_by(activo=True).count()
        completadas_q = Progreso.query.filter_by(usuario_id=usuario_id, completado=True).all()
        total_completadas = len(completadas_q)
        pendientes = max(0, total_citas - total_completadas)
        pct = round((total_completadas / total_citas * 100), 1) if total_citas else 0

        cals = [p.calificacion for p in completadas_q if p.calificacion]
        cal_promedio = round(sum(cals) / len(cals), 1) if cals else 0

        categorias = Categoria.query.all()
        resumen_cats = []
        for cat in categorias:
            total_cat = Cita.query.filter_by(categoria_id=cat.id, activo=True).count()
            if not total_cat:
                continue
            completadas_cat = (
                Progreso.query.join(Cita, Progreso.cita_id == Cita.id)
                .filter(Progreso.usuario_id == usuario_id, Progreso.completado == True, Cita.categoria_id == cat.id)
                .count()
            )
            resumen_cats.append(f"{cat.nombre}: {completadas_cat}/{total_cat}")

        nombre = usuario.nombre.split()[0] if usuario and usuario.nombre else 'Usuario'

        prompt = f"""Eres un asistente de experiencias románticas para la app "100 Citas Románticas en La Paz".
            Analiza el progreso de {nombre} y genera un análisis motivador con recomendaciones concretas.

            Datos del usuario:
            - Citas completadas: {total_completadas} de {total_citas} ({pct}%)
            - Citas pendientes: {pendientes}
            - Calificación promedio que da a sus citas: {cal_promedio}/5
            - Progreso por categoría: {'; '.join(resumen_cats) if resumen_cats else 'Sin datos'}

            Responde con exactamente este formato JSON (sin markdown, solo el objeto):
            {{
            "resumen": "2-3 oraciones describiendo el progreso de forma motivadora",
            "logro_destacado": "Su mayor logro hasta ahora en una oración",
            "recomendaciones": ["recomendación 1 concreta", "recomendación 2 concreta", "recomendación 3 concreta"],
            "proxima_meta": "Una meta específica y alcanzable para las próximas semanas",
            "mensaje_motivacional": "Un mensaje cálido y personalizado de máximo 2 oraciones"
            }}"""

        resultado = IAService.consultar_ia(prompt)

        if not resultado.get('success'):
            return {'error': resultado.get('error', 'Error al consultar la IA')}, 500

        import json as _json
        try:
            texto = resultado['respuesta'].strip()
            if '```' in texto:
                texto = texto.split('```')[1]
                if texto.startswith('json'):
                    texto = texto[4:]
            analisis = _json.loads(texto)
        except Exception:
            analisis = {
                'resumen': resultado['respuesta'],
                'recomendaciones': [],
                'proxima_meta': '',
                'mensaje_motivacional': '',
                'logro_destacado': '',
            }

        IAService.guardar_consulta_en_db(usuario_id, prompt[:200], resultado['respuesta'], resultado.get('tokens', 0))

        return {'analisis': analisis}, 200
