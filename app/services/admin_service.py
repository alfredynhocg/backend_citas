from datetime import datetime, timezone
from ..extensions import db
from ..models import Pago, Suscripcion, Negocio, User, Cita, Grupo
from sqlalchemy import func


class AdminService:

    # ==================== PAGOS ====================

    @staticmethod
    def obtener_pagos_pendientes():
        return Pago.query.filter_by(estado='pendiente').order_by(Pago.fecha_pago.desc()).all()

    @staticmethod
    def aprobar_pago(pago_id, admin_id):
        pago = Pago.query.get(pago_id)
        if not pago:
            raise LookupError("Pago no encontrado")
        if pago.estado != 'pendiente':
            raise ValueError("El pago ya fue procesado")

        pago.estado = 'aprobado'
        pago.aprobado_por = admin_id
        pago.fecha_aprobacion = datetime.now(timezone.utc)

        from datetime import date, timedelta
        inicio = date.today()
        if pago.tipo_periodo == 'anual':
            fin = inicio.replace(year=inicio.year + 1)
        else:
            fin = inicio + timedelta(days=30)

        suscripcion = Suscripcion(
            usuario_id=pago.usuario_id,
            grupo_id=pago.grupo_id,
            plan_id=pago.plan_id,
            pago_id=pago.id,
            fecha_inicio=inicio,
            fecha_expiracion=fin,
            activo=True,
            tipo_periodo=pago.tipo_periodo,
        )
        db.session.add(suscripcion)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return {'mensaje': 'Pago aprobado y suscripción activada'}

    @staticmethod
    def rechazar_pago(pago_id, admin_id):
        pago = Pago.query.get(pago_id)
        if not pago:
            raise LookupError("Pago no encontrado")
        pago.estado = 'rechazado'
        pago.aprobado_por = admin_id
        pago.fecha_aprobacion = datetime.now(timezone.utc)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return {'mensaje': 'Pago rechazado'}

    # ==================== NEGOCIOS ====================

    @staticmethod
    def obtener_negocios_pendientes():
        return Negocio.query.filter_by(activo=False).order_by(Negocio.fecha_registro.desc()).all()

    @staticmethod
    def aprobar_negocio(negocio_id):
        negocio = Negocio.query.get(negocio_id)
        if not negocio:
            raise LookupError("Negocio no encontrado")
        negocio.activo = True
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return {'mensaje': 'Negocio aprobado'}

    @staticmethod
    def rechazar_negocio(negocio_id):
        negocio = Negocio.query.get(negocio_id)
        if not negocio:
            raise LookupError("Negocio no encontrado")
        db.session.delete(negocio)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return {'mensaje': 'Negocio rechazado y eliminado'}

    # ==================== REPORTES ====================

    @staticmethod
    def obtener_reportes():
        total_usuarios = User.query.count()
        total_grupos = Grupo.query.filter_by(activo=True).count()
        total_citas = Cita.query.filter_by(activo=True).count()
        total_negocios = Negocio.query.filter_by(activo=True).count()
        pagos_pendientes = Pago.query.filter_by(estado='pendiente').count()
        pagos_aprobados = Pago.query.filter_by(estado='aprobado').count()
        ingresos = db.session.query(func.sum(Pago.monto)).filter_by(estado='aprobado').scalar() or 0
        negocios_pendientes = Negocio.query.filter_by(activo=False).count()

        return {
            'total_usuarios': total_usuarios,
            'total_grupos': total_grupos,
            'total_citas': total_citas,
            'total_negocios': total_negocios,
            'pagos_pendientes': pagos_pendientes,
            'pagos_aprobados': pagos_aprobados,
            'ingresos_totales': float(ingresos),
            'negocios_pendientes': negocios_pendientes,
        }
