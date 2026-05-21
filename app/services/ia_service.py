# app/services/ia_service.py
import requests
import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL  = os.getenv('OLLAMA_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.2:3b')


class IAService:
    @staticmethod
    def consultar_ia(mensaje):
        try:
            response = requests.post(
                f"{OLLAMA_URL}/api/chat",
                json={
                    "model": OLLAMA_MODEL,
                    "messages": [{"role": "user", "content": mensaje}],
                    "stream": False,
                    "options": {"temperature": 0.7, "num_predict": 800},
                },
                timeout=120,
            )

            if response.status_code == 200:
                data = response.json()
                texto = data.get('message', {}).get('content', '')
                return {"success": True, "respuesta": texto, "tokens": 0}
            else:
                return {"success": False, "error": f"Ollama error {response.status_code}: {response.text}"}

        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "No se pudo conectar con Ollama. Asegúrate de que esté corriendo (ollama serve)."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def guardar_consulta_en_db(user_id, pregunta, respuesta, tokens=None):
        from ..models import db, ConsultaIA
        from datetime import datetime
        try:
            consulta = ConsultaIA(
                user_id=user_id,
                pregunta=pregunta,
                respuesta=respuesta,
                fecha=datetime.utcnow(),
                tokens_usados=tokens or 0,
            )
            db.session.add(consulta)
            db.session.commit()
            return True
        except Exception as e:
            print(f"Error DB ConsultaIA: {e}")
            return False
