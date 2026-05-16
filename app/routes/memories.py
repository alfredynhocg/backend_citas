from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Namespace, Resource, fields

from ..services import memories as memories_service

ns = Namespace("memories", description="Recuerdos de las citas")

memory_model = ns.model("Memory", {
    "id":             fields.Integer(),
    "couple_date_id": fields.Integer(),
    "note":           fields.String(),
    "photo_url":      fields.String(),
    "created_at":     fields.String(),
})


@ns.route("/")
class AllMemories(Resource):
    @jwt_required()
    @ns.marshal_list_with(memory_model)
    def get(self):
        """Todos los recuerdos de la pareja"""
        user_id = int(get_jwt_identity())
        try:
            return memories_service.get_all_couple_memories(user_id)
        except LookupError as e:
            ns.abort(404, str(e))


@ns.route("/couple-date/<int:couple_date_id>")
class MemoriesByCoupleDate(Resource):
    @jwt_required()
    @ns.marshal_list_with(memory_model)
    def get(self, couple_date_id):
        """Recuerdos de una cita específica"""
        user_id = int(get_jwt_identity())
        try:
            return memories_service.get_memories_by_couple_date(user_id, couple_date_id)
        except LookupError as e:
            ns.abort(404, str(e))

    @jwt_required()
    @ns.marshal_with(memory_model, code=201)
    def post(self, couple_date_id):
        """Agregar un recuerdo (nota y/o foto) — multipart/form-data"""
        user_id = int(get_jwt_identity())
        note    = request.form.get("note")
        photo   = request.files.get("photo")
        try:
            result = memories_service.add_memory(user_id, couple_date_id, note, photo)
        except (ValueError, LookupError) as e:
            ns.abort(400, str(e))
        return result, 201


@ns.route("/<int:memory_id>")
class MemoryDetail(Resource):
    @jwt_required()
    def delete(self, memory_id):
        """Eliminar un recuerdo"""
        user_id = int(get_jwt_identity())
        try:
            memories_service.delete_memory(user_id, memory_id)
        except LookupError as e:
            ns.abort(404, str(e))
        return "", 204
