from ..models import Categoria as Category, Progreso as CoupleDate, Grupo as Couple, Cita as Date
from ..extensions import db
from datetime import datetime, timezone


def list_categories() -> list:
    categories = Category.query.order_by(Category.id).all()
    return [
        {
            "id":          c.id,
            "name":        c.name,
            "icon":        c.icon,
            "color":       c.color,
            "total_dates": Date.query.filter_by(category_id=c.id).count(),
        }
        for c in categories
    ]


def list_dates(category_id: int = None) -> list:
    q = Date.query.order_by(Date.order_num)
    if category_id:
        q = q.filter_by(category_id=category_id)
    return [_date_dict(d) for d in q.all()]


def get_date(date_id: int) -> dict:
    d = db.session.get(Date, date_id)
    if not d:
        raise LookupError("Cita no encontrada")
    return _date_dict(d)


def get_couple_history(user_id: int) -> list:
    couple = Couple.query.filter(
        (Couple.user_a_id == user_id) | (Couple.user_b_id == user_id)
    ).first()
    if not couple:
        raise LookupError("No tienes una pareja registrada")

    couple_dates = (
        CoupleDate.query
        .filter_by(couple_id=couple.id)
        .join(Date)
        .order_by(Date.order_num)
        .all()
    )
    return [_couple_date_dict(cd) for cd in couple_dates]


def start_date(user_id: int, date_id: int) -> dict:
    couple = Couple.query.filter(
        (Couple.user_a_id == user_id) | (Couple.user_b_id == user_id)
    ).first()
    if not couple:
        raise LookupError("No tienes una pareja registrada")

    d = db.session.get(Date, date_id)
    if not d:
        raise LookupError("Cita no encontrada")

    existing = CoupleDate.query.filter_by(couple_id=couple.id, date_id=date_id).first()
    if existing:
        return _couple_date_dict(existing)

    cd = CoupleDate(couple_id=couple.id, date_id=date_id, status="en_progreso")
    db.session.add(cd)
    db.session.commit()
    return _couple_date_dict(cd)


def complete_date(user_id: int, couple_date_id: int) -> dict:
    cd = _get_couple_date_for_user(user_id, couple_date_id)
    if cd.status == "completada":
        raise ValueError("Esta cita ya está completada")
    cd.status       = "completada"
    cd.completed_at = datetime.now(timezone.utc)
    db.session.commit()
    return _couple_date_dict(cd)


def rate_date(user_id: int, couple_date_id: int, rating: int) -> dict:
    if rating < 1 or rating > 5:
        raise ValueError("El rating debe ser entre 1 y 5")
    cd = _get_couple_date_for_user(user_id, couple_date_id)
    if cd.status != "completada":
        raise ValueError("Solo puedes calificar citas completadas")
    cd.rating = rating
    db.session.commit()
    return _couple_date_dict(cd)


def _get_couple_date_for_user(user_id: int, couple_date_id: int) -> CoupleDate:
    couple = Couple.query.filter(
        (Couple.user_a_id == user_id) | (Couple.user_b_id == user_id)
    ).first()
    if not couple:
        raise LookupError("No tienes una pareja registrada")
    cd = CoupleDate.query.filter_by(id=couple_date_id, couple_id=couple.id).first()
    if not cd:
        raise LookupError("Registro de cita no encontrado")
    return cd


def _date_dict(d: Date) -> dict:
    return {
        "id":            d.id,
        "order_num":     d.order_num,
        "title":         d.title,
        "description":   d.description,
        "difficulty":    d.difficulty,
        "duration":      d.duration,
        "cost":          d.cost,
        "location_hint": d.location_hint,
        "category": {
            "id":    d.category.id,
            "name":  d.category.name,
            "icon":  d.category.icon,
            "color": d.category.color,
        },
    }


def _couple_date_dict(cd: CoupleDate) -> dict:
    return {
        "id":           cd.id,
        "date_id":      cd.date_id,
        "status":       cd.status,
        "rating":       cd.rating,
        "completed_at": cd.completed_at.isoformat() if cd.completed_at else None,
        "created_at":   cd.created_at.isoformat(),
    }
