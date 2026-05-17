from datetime import datetime, timezone

from .extensions import db


def _now():
    return datetime.now(timezone.utc)


class User(db.Model):
    __tablename__ = "users"

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(150), nullable=False)
    email         = db.Column(db.String(254), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role          = db.Column(db.String(20), nullable=False, default="couple")
    is_active     = db.Column(db.Boolean, nullable=False, default=True)
    created_at    = db.Column(db.DateTime, default=_now, nullable=False)

    couple_a = db.relationship("Couple", foreign_keys="Couple.user_a_id", back_populates="user_a", uselist=False)
    couple_b = db.relationship("Couple", foreign_keys="Couple.user_b_id", back_populates="user_b", uselist=False)


class Couple(db.Model):
    __tablename__ = "couples"

    id           = db.Column(db.Integer, primary_key=True)
    user_a_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user_b_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    couple_name  = db.Column(db.String(120), nullable=False)
    start_date   = db.Column(db.Date, nullable=False)
    created_at   = db.Column(db.DateTime, default=_now, nullable=False)

    user_a       = db.relationship("User", foreign_keys=[user_a_id], back_populates="couple_a")
    user_b       = db.relationship("User", foreign_keys=[user_b_id], back_populates="couple_b")
    couple_dates = db.relationship("CoupleDate", back_populates="couple", lazy="dynamic")


class Category(db.Model):
    __tablename__ = "categories"

    id    = db.Column(db.Integer, primary_key=True)
    name  = db.Column(db.String(120), unique=True, nullable=False)
    icon  = db.Column(db.String(10), nullable=False)
    color = db.Column(db.String(20), nullable=False)

    dates = db.relationship("Date", back_populates="category", lazy="dynamic")


class Date(db.Model):
    __tablename__ = "dates"

    id            = db.Column(db.Integer, primary_key=True)
    order_num     = db.Column(db.Integer, unique=True, nullable=False)
    title         = db.Column(db.String(200), nullable=False)
    description   = db.Column(db.Text, nullable=False)
    category_id   = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    difficulty    = db.Column(db.String(20), nullable=False)
    duration      = db.Column(db.String(50), nullable=False)
    cost          = db.Column(db.String(20), nullable=False)
    location_hint = db.Column(db.String(200), nullable=False)

    category     = db.relationship("Category", back_populates="dates")
    couple_dates = db.relationship("CoupleDate", back_populates="date", lazy="dynamic")


class CoupleDate(db.Model):
    __tablename__ = "couple_dates"

    id           = db.Column(db.Integer, primary_key=True)
    couple_id    = db.Column(db.Integer, db.ForeignKey("couples.id"), nullable=False)
    date_id      = db.Column(db.Integer, db.ForeignKey("dates.id"), nullable=False)
    status       = db.Column(db.String(20), nullable=False, default="pendiente")
    rating       = db.Column(db.Integer, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at   = db.Column(db.DateTime, default=_now, nullable=False)

    couple   = db.relationship("Couple", back_populates="couple_dates")
    date     = db.relationship("Date", back_populates="couple_dates")
    memories = db.relationship("Memory", back_populates="couple_date", lazy="dynamic")


class Memory(db.Model):
    __tablename__ = "memories"

    id             = db.Column(db.Integer, primary_key=True)
    couple_date_id = db.Column(db.Integer, db.ForeignKey("couple_dates.id"), nullable=False)
    note           = db.Column(db.Text, nullable=True)
    photo_url      = db.Column(db.String(300), nullable=True)
    created_at     = db.Column(db.DateTime, default=_now, nullable=False)

    couple_date = db.relationship("CoupleDate", back_populates="memories")
