from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Namespace, Resource, fields
#Muy Importante: flask run --debug
from ..services import auth as auth_service

ns = Namespace("dev", description="Pruebas y Estado")

@ns.route('/')
class DevTest(Resource):
    def get(self):
        """Endpoint de prueba para verificar que la API está funcionando"""
        return {"message": "Estado Funcional al 2000 de Citas"}, 200
