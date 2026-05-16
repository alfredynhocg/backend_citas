from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Namespace, Resource, fields

from ..services import couples as couples_service

ns = Namespace("couples", description="Gestión de parejas y progreso")

couple_model = ns.model("Couple", {
    "id":          fields.Integer(),
    "couple_name": fields.String(),
    "start_date":  fields.String(),
    "user_a_id":   fields.Integer(),
    "user_b_id":   fields.Integer(),
})
create_model = ns.model("CreateCouple", {
    "couple_name": fields.String(required=True),
    "start_date":  fields.String(required=True, description="YYYY-MM-DD"),
})
invite_model = ns.model("InvitePartner", {
    "partner_email": fields.String(required=True),
})
category_progress_model = ns.model("CategoryProgress", {
    "category_id":   fields.Integer(),
    "category_name": fields.String(),
    "icon":          fields.String(),
    "color":         fields.String(),
    "total":         fields.Integer(),
    "completed":     fields.Integer(),
})
progress_model = ns.model("Progress", {
    "total":       fields.Integer(),
    "completed":   fields.Integer(),
    "percentage":  fields.Float(),
    "by_category": fields.List(fields.Nested(category_progress_model)),
})
best_cat_model = ns.model("BestCategory", {
    "id":   fields.Integer(),
    "name": fields.String(),
    "icon": fields.String(),
})
stats_model = ns.model("Stats", {
    "completed":      fields.Integer(),
    "avg_rating":     fields.Float(),
    "total_memories": fields.Integer(),
    "best_category":  fields.Nested(best_cat_model, allow_null=True),
})


@ns.route("/")
class CoupleCreate(Resource):
    @jwt_required()
    @ns.expect(create_model, validate=True)
    @ns.marshal_with(couple_model, code=201)
    def post(self):
        """Crear una nueva pareja"""
        body    = request.json
        user_id = int(get_jwt_identity())
        try:
            result = couples_service.create_couple(user_id, body["couple_name"], body["start_date"])
        except ValueError as e:
            ns.abort(400, str(e))
        return result, 201


@ns.route("/mine")
class MyCouple(Resource):
    @jwt_required()
    @ns.marshal_with(couple_model)
    def get(self):
        """Obtener mi pareja"""
        user_id = int(get_jwt_identity())
        try:
            return couples_service.get_my_couple(user_id)
        except LookupError as e:
            ns.abort(404, str(e))


@ns.route("/mine/invite")
class InvitePartner(Resource):
    @jwt_required()
    @ns.expect(invite_model, validate=True)
    @ns.marshal_with(couple_model)
    def post(self):
        """Invitar a la pareja por email"""
        body    = request.json
        user_id = int(get_jwt_identity())
        try:
            result = couples_service.invite_partner(user_id, body["partner_email"])
        except (ValueError, LookupError) as e:
            ns.abort(400, str(e))
        return result


@ns.route("/mine/progress")
class CoupleProgress(Resource):
    @jwt_required()
    @ns.marshal_with(progress_model)
    def get(self):
        """Progreso de la pareja (total / completadas / por categoría)"""
        user_id = int(get_jwt_identity())
        try:
            return couples_service.get_progress(user_id)
        except LookupError as e:
            ns.abort(404, str(e))


@ns.route("/mine/stats")
class CoupleStats(Resource):
    @jwt_required()
    @ns.marshal_with(stats_model)
    def get(self):
        """Estadísticas de la pareja"""
        user_id = int(get_jwt_identity())
        try:
            return couples_service.get_stats(user_id)
        except LookupError as e:
            ns.abort(404, str(e))
