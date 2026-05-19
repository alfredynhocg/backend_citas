from datetime import datetime, timezone
from ..extensions import db
from ..models import Progreso, Cita


class ProgresoService:

    @staticmethod
    def obtener_progreso_usuario(usuario_id):
        return Progreso.query.filter_by(usuario_id=usuario_id, tipo='individual').all()

    @staticmethod
    def obtener_progreso_grupo(grupo_id):
        return Progreso.query.filter_by(grupo_id=grupo_id, tipo='grupal').all()

    @staticmethod
    def completar_cita(usuario_id, data):
        cita_id = data.get('cita_id')
        tipo = data.get('tipo', 'individual')
        grupo_id = data.get('grupo_id')

        if not cita_id:
            raise ValueError("cita_id es requerido")
        if not Cita.query.get(cita_id):
            raise LookupError("Cita no encontrada")

        filtro = {'cita_id': cita_id, 'tipo': tipo}
        if tipo == 'individual':
            filtro['usuario_id'] = usuario_id
        else:
            if not grupo_id:
                raise ValueError("grupo_id es requerido para progreso grupal")
            filtro['grupo_id'] = grupo_id

        progreso = Progreso.query.filter_by(**filtro).first()
        if not progreso:
            progreso = Progreso(
                tipo=tipo,
                cita_id=cita_id,
                usuario_id=usuario_id if tipo == 'individual' else None,
                grupo_id=grupo_id if tipo == 'grupal' else None,
            )
            db.session.add(progreso)

        progreso.completado = True
        progreso.fecha_completado = datetime.now(timezone.utc)
        progreso.calificacion = data.get('calificacion')
        progreso.anecdota = data.get('anecdota')

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return progreso

    @staticmethod
    def obtener_estadisticas(usuario_id):
        completadas = Progreso.query.filter_by(
            usuario_id=usuario_id, tipo='individual', completado=True
        ).count()
        total = Cita.query.filter_by(activo=True).count()
        return {
            'completadas': completadas,
            'total': total,
            'porcentaje': round(completadas / total * 100, 1) if total else 0,
        }
