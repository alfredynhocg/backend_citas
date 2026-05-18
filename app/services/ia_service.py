# app/services/ia_service.py
import requests
import os
from dotenv import load_dotenv

load_dotenv()

class IAService:
    @staticmethod
    def consultar_ia(mensaje):
        try:
            api_key = os.getenv('OPENROUTER_API_KEY')
            
            if not api_key:
                return {"success": False, "error": "API_KEY no encontrada en .env"}
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "openai/gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": mensaje}],
                    "max_tokens": 80
                },
                timeout=30
            )
            
            data = response.json()
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "respuesta": data['choices'][0]['message']['content'],
                    "tokens": data['usage']['total_tokens']
                }
            else:
                return {"success": False, "error": data}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def guardar_consulta_en_db(user_id, pregunta, respuesta, tokens=None):
        """Guardar en DB"""
        from ..models import db
        from datetime import datetime
        
        try:
            # Omitir guardado si no querés usar DB todavía
            print(f"Guardando consulta - User: {user_id}, Pregunta: {pregunta}")
            print(f"Respuesta: {respuesta[:100]}...")
            
            # Comentado temporalmente hasta que la tabla exista
            from ..models import ConsultaIA
            consulta = ConsultaIA(
                user_id=user_id,
                pregunta=pregunta,
                respuesta=respuesta,
                fecha=datetime.utcnow(),
                tokens_usados=tokens
            )
            db.session.add(consulta)
            db.session.commit()
            
            return True
        except Exception as e:
            print(f"Error DB: {e}")
            return False