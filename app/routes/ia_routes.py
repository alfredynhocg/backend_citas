# routes/ia_routes.py
from flask_restx import Namespace, Resource
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity 
from ..services.ia_service import IAService

ns = Namespace('ia', description='IA')
# app/routes/ia_routes.py
@ns.route('/consulta')
class IAConsulta(Resource):
    @jwt_required()
    def post(self):
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            pregunta = data.get('mensaje', '')
            
            resultado = IAService.consultar_ia(pregunta)
            
            if resultado.get('success'):
                # Guardar en DB (opcional)
                IAService.guardar_consulta_en_db(user_id, pregunta, resultado['respuesta'], resultado['tokens'])
                
                # CORREGIDO: No uses 'tokens' si no existe
                return {
                    "respuesta": resultado['respuesta']
                    # "tokens_usados": resultado.get('tokens', 0)  ← COMENTADO
                }, 200
            else:
                return {"error": resultado.get('error')}, 500
                
        except Exception as e:
            print(f"Error: {e}")
            return {"error": str(e)}, 500