from datetime import date

from ..extensions import db
from ..models import Categoria as Category, Grupo as Couple, Progreso as CoupleDate, Cita as Date, User
def _get_couple_for_user(user_id: int) -> Couple:
    couple = Couple.query.filter(
        (Couple.user_a_id == user_id) | (Couple.user_b_id == user_id)
    ).first()
    if not couple:
        raise LookupError("No tienes una pareja registrada")
    return couple


def create_couple(user_id: int, couple_name: str, start_date: str) -> dict:
    existing = Couple.query.filter(
        (Couple.user_a_id == user_id) | (Couple.user_b_id == user_id)
    ).first()
    if existing:
        raise ValueError("Ya perteneces a una pareja")

    couple = Couple(
        user_a_id=user_id,
        couple_name=couple_name.strip(),
        start_date=date.fromisoformat(start_date),
    )
    db.session.add(couple)
    db.session.commit()
    return _couple_dict(couple)


def invite_partner(user_id: int, partner_email: str) -> dict:
    couple = _get_couple_for_user(user_id)

    if couple.user_b_id:
        raise ValueError("La pareja ya tiene dos miembros")

    partner = User.query.filter_by(email=partner_email.lower().strip()).first()
    if not partner:
        raise LookupError("No existe un usuario con ese email")
    if partner.id == user_id:
        raise ValueError("No puedes invitarte a ti mismo")

    already = Couple.query.filter(
        (Couple.user_a_id == partner.id) | (Couple.user_b_id == partner.id)
    ).first()
    if already:
        raise ValueError("Ese usuario ya pertenece a una pareja")

    couple.user_b_id = partner.id
    db.session.commit()
    return _couple_dict(couple)


def get_my_couple(user_id: int) -> dict:
    return _couple_dict(_get_couple_for_user(user_id))


def get_progress(user_id: int) -> dict:
    couple = _get_couple_for_user(user_id)
    total  = Date.query.count()

    completed_dates = (
        CoupleDate.query
        .filter_by(couple_id=couple.id, status="completada")
        .all()
    )
    completed = len(completed_dates)
    pct = round(completed / total * 100, 1) if total else 0

    completed_date_ids = {cd.date_id for cd in completed_dates}
    categories = Category.query.all()
    by_category = []
    for cat in categories:
        cat_total = Date.query.filter_by(category_id=cat.id).count()
        cat_done  = Date.query.filter(
            Date.category_id == cat.id,
            Date.id.in_(completed_date_ids)
        ).count()
        by_category.append({
            "category_id":   cat.id,
            "category_name": cat.name,
            "icon":          cat.icon,
            "color":         cat.color,
            "total":         cat_total,
            "completed":     cat_done,
        })

    return {
        "total":       total,
        "completed":   completed,
        "percentage":  pct,
        "by_category": by_category,
    }


def get_stats(user_id: int) -> dict:
    couple = _get_couple_for_user(user_id)

    completed = CoupleDate.query.filter_by(couple_id=couple.id, status="completada").all()
    ratings   = [cd.rating for cd in completed if cd.rating is not None]
    avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else None

    from ..models import Memory
    memory_count = (
        Memory.query
        .join(CoupleDate)
        .filter(CoupleDate.couple_id == couple.id)
        .count()
    )

    best_category = None
    if completed:
        from collections import Counter
        date_ids = [cd.date_id for cd in completed]
        dates    = Date.query.filter(Date.id.in_(date_ids)).all()
        cat_counts = Counter(d.category_id for d in dates)
        top_cat_id = cat_counts.most_common(1)[0][0]
        top_cat    = db.session.get(Category, top_cat_id)
        best_category = {"id": top_cat.id, "name": top_cat.name, "icon": top_cat.icon}

    return {
        "completed":     len(completed),
        "avg_rating":    avg_rating,
        "total_memories": memory_count,
        "best_category": best_category,
    }


def _couple_dict(couple: Couple) -> dict:
    return {
        "id":          couple.id,
        "couple_name": couple.couple_name,
        "start_date":  couple.start_date.isoformat(),
        "user_a_id":   couple.user_a_id,
        "user_b_id":   couple.user_b_id,
    }
