from ..extensions import db
from ..models import PlanSuscripcion, Pago, Suscripcion


class SuscripcionService:

    @staticmethod
    def obtener_planes():
        return PlanSuscripcion.query.filter_by(activo=True).all()

    @staticmethod
    def obtener_suscripciones_usuario(usuario_id):
        return Suscripcion.query.filter_by(usuario_id=usuario_id).all()

    @staticmethod
    def crear_pago(usuario_id, data):
        plan_id = data.get('plan_id')
        tipo_periodo = data.get('tipo_periodo', 'mensual')
        grupo_id = data.get('grupo_id')

        plan = PlanSuscripcion.query.get(plan_id)
        if not plan:
            raise ValueError("Plan no encontrado")

        monto = float(plan.precio_mensual) if tipo_periodo == 'mensual' else float(plan.precio_anual)

        pago = Pago(
            usuario_id=usuario_id,
            grupo_id=grupo_id,
            plan_id=plan_id,
            monto=monto,
            metodo_pago=data.get('metodo_pago', 'transferencia'),
            comprobante_url=data.get('comprobante_url'),
            tipo_periodo=tipo_periodo,
            estado='pendiente',
        )
        db.session.add(pago)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return pago

    @staticmethod
    def cancelar_suscripcion(suscripcion_id, usuario_id):
        sus = Suscripcion.query.filter_by(id=suscripcion_id, usuario_id=usuario_id).first()
        if not sus:
            raise LookupError("Suscripción no encontrada")
        sus.activo = False
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return sus
