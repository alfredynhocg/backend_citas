from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Namespace, Resource, fields

from ..services import dates as dates_service

ns = Namespace("dates", description="Catálogo de citas y progreso de pareja")

category_model = ns.model("Category", {
    "id":          fields.Integer(),
    "name":        fields.String(),
    "icon":        fields.String(),
    "color":       fields.String(),
    "total_dates": fields.Integer(),
})
date_model = ns.model("Date", {
    "id":            fields.Integer(),
    "order_num":     fields.Integer(),
    "title":         fields.String(),
    "description":   fields.String(),
    "difficulty":    fields.String(),
    "duration":      fields.String(),
    "cost":          fields.String(),
    "location_hint": fields.String(),
    "category":      fields.Nested(ns.model("DateCategory", {
        "id":    fields.Integer(),
        "name":  fields.String(),
        "icon":  fields.String(),
        "color": fields.String(),
    })),
})
couple_date_model = ns.model("CoupleDate", {
    "id":           fields.Integer(),
    "date_id":      fields.Integer(),
    "status":       fields.String(),
    "rating":       fields.Integer(),
    "completed_at": fields.String(),
    "created_at":   fields.String(),
})
start_model = ns.model("StartDate", {
    "date_id": fields.Integer(required=True),
})
rate_model = ns.model("RateDate", {
    "rating": fields.Integer(required=True, min=1, max=5),
})


@ns.route("/categories")
class Categories(Resource):
    @jwt_required()
    @ns.marshal_list_with(category_model)
    def get(self):
        """Listar todas las categorías"""
        return dates_service.list_categories()


@ns.route("/")
class DateList(Resource):
    @jwt_required()
    @ns.marshal_list_with(date_model)
    def get(self):
        """Listar citas (opcional: ?category=id)"""
        category_id = request.args.get("category", type=int)
        return dates_service.list_dates(category_id)


@ns.route("/<int:date_id>")
class DateDetail(Resource):
    @jwt_required()
    @ns.marshal_with(date_model)
    def get(self, date_id):
        """Detalle de una cita"""
        try:
            return dates_service.get_date(date_id)
        except LookupError as e:
            ns.abort(404, str(e))


@ns.route("/history")
class CoupleHistory(Resource):
    @jwt_required()
    @ns.marshal_list_with(couple_date_model)
    def get(self):
        """Historial de citas de la pareja"""
        user_id = int(get_jwt_identity())
        try:
            return dates_service.get_couple_history(user_id)
        except LookupError as e:
            ns.abort(404, str(e))


@ns.route("/start")
class StartDate(Resource):
    @jwt_required()
    @ns.expect(start_model, validate=True)
    @ns.marshal_with(couple_date_model, code=201)
    def post(self):
        """Marcar una cita como en progreso"""
        user_id = int(get_jwt_identity())
        try:
            result = dates_service.start_date(user_id, request.json["date_id"])
        except LookupError as e:
            ns.abort(404, str(e))
        return result, 201


@ns.route("/<int:couple_date_id>/complete")
class CompleteDate(Resource):
    @jwt_required()
    @ns.marshal_with(couple_date_model)
    def patch(self, couple_date_id):
        """Marcar una cita como completada"""
        user_id = int(get_jwt_identity())
        try:
            return dates_service.complete_date(user_id, couple_date_id)
        except LookupError as e:
            ns.abort(404, str(e))
        except ValueError as e:
            ns.abort(400, str(e))


@ns.route("/<int:couple_date_id>/rate")
class RateDate(Resource):
    @jwt_required()
    @ns.expect(rate_model, validate=True)
    @ns.marshal_with(couple_date_model)
    def patch(self, couple_date_id):
        """Calificar una cita completada (1-5)"""
        user_id = int(get_jwt_identity())
        try:
            return dates_service.rate_date(user_id, couple_date_id, request.json["rating"])
        except LookupError as e:
            ns.abort(404, str(e))
        except ValueError as e:
            ns.abort(400, str(e))
