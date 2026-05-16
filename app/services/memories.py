import os
import uuid

from flask import current_app
from werkzeug.datastructures import FileStorage

from ..extensions import db
from ..models import Couple, CoupleDate, Memory

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}


def _allowed(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _save_photo(file: FileStorage) -> str:
    if not _allowed(file.filename):
        raise ValueError("Formato de imagen no permitido (jpg, png, webp)")
    ext      = file.filename.rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4()}.{ext}"
    folder   = current_app.config["IMG_UPLOAD_FOLDER"]
    file.save(os.path.join(folder, filename))
    return current_app.config["IMG_UPLOAD_URL"] + filename


def _delete_photo(photo_url: str) -> None:
    if not photo_url:
        return
    filename = photo_url.split("/")[-1]
    path = os.path.join(current_app.config["IMG_UPLOAD_FOLDER"], filename)
    if os.path.exists(path):
        os.remove(path)


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


def add_memory(user_id: int, couple_date_id: int, note: str = None, photo: FileStorage = None) -> dict:
    if not note and not photo:
        raise ValueError("Debes incluir una nota o una foto")
    cd        = _get_couple_date_for_user(user_id, couple_date_id)
    photo_url = _save_photo(photo) if photo else None
    memory    = Memory(couple_date_id=cd.id, note=note, photo_url=photo_url)
    db.session.add(memory)
    db.session.commit()
    return _memory_dict(memory)


def delete_memory(user_id: int, memory_id: int) -> None:
    couple = Couple.query.filter(
        (Couple.user_a_id == user_id) | (Couple.user_b_id == user_id)
    ).first()
    if not couple:
        raise LookupError("No tienes una pareja registrada")

    memory = (
        Memory.query
        .join(CoupleDate)
        .filter(Memory.id == memory_id, CoupleDate.couple_id == couple.id)
        .first()
    )
    if not memory:
        raise LookupError("Recuerdo no encontrado")

    _delete_photo(memory.photo_url)
    db.session.delete(memory)
    db.session.commit()


def get_memories_by_couple_date(user_id: int, couple_date_id: int) -> list:
    cd = _get_couple_date_for_user(user_id, couple_date_id)
    return [_memory_dict(m) for m in cd.memories.order_by(Memory.created_at).all()]


def get_all_couple_memories(user_id: int) -> list:
    couple = Couple.query.filter(
        (Couple.user_a_id == user_id) | (Couple.user_b_id == user_id)
    ).first()
    if not couple:
        raise LookupError("No tienes una pareja registrada")

    memories = (
        Memory.query
        .join(CoupleDate)
        .filter(CoupleDate.couple_id == couple.id)
        .order_by(Memory.created_at.desc())
        .all()
    )
    return [_memory_dict(m) for m in memories]


def _memory_dict(m: Memory) -> dict:
    return {
        "id":             m.id,
        "couple_date_id": m.couple_date_id,
        "note":           m.note,
        "photo_url":      m.photo_url,
        "created_at":     m.created_at.isoformat(),
    }
