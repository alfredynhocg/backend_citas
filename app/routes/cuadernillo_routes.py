from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import Progreso, db
from sqlalchemy import func

ns = Namespace('cuadernillo', description='Contenido del cuadernillo de 100 citas románticas')

INSTRUCCIONES = {
    "titulo": "Instrucciones 100 Citas Románticas en La Paz",
    "como_funciona": {
        "titulo": "¿Cómo funcionará este reto?",
        "puntos": [
            "Cada cita será una pausa en la rutina para celebrar su amor.",
            "Priorizando siempre el cariño y la conexión.",
            "No esperen ocasiones especiales: ¡cada día en La Paz puede transformarse en un momento único!"
        ]
    },
    "reglas": {
        "titulo": "Reglas del reto",
        "puntos": [
            "Capturen cada cita con fotos y videos, ¡serán su tesoro más valioso!",
            "El celular solo servirá para guardar recuerdos, nunca para distraerse.",
            "Lo más importante es la alegría de estar juntos, no la perfección del plan.",
            "Si están listos para descubrir el amor en cada rincón paceño, firmen aquí y comiencen esta travesía romántica."
        ]
    }
}

MENSAJE_CIERRE = {
    "titulo": "¡Gracias por vivir esta gran aventura de amor en La Paz!",
    "saludo": "Querida pareja:",
    "cuerpo": [
        "Llegar hasta aquí significa que juntos compartieron paisajes majestuosos, paseos entre montañas, cafés cálidos y momentos que quedarán grabados en su historia.",
        "Cada cita fue mucho más que un plan romántico: fue una promesa de amor, un regalo de tiempo compartido y un recuerdo que ahora forma parte de ustedes.",
        "Gracias por detenerse a mirar juntos el Illimani, por caminar de la mano en calles, por dejar que cada rincón paceño se convierta en testigo de su complicidad.",
        "Hoy, al cerrar este cuadernillo, no termina la aventura… apenas comienza.",
        "Porque en cada mirada, en cada abrazo y en cada \"te quiero\" que se susurran, La Paz seguirá siendo su escenario de amor eterno.",
        "Gracias por convertir lo cotidiano en extraordinario y por demostrar que, entre alturas y cielos andinos, el amor siempre florece.",
        "¡Que sigan construyendo recuerdos inolvidables, unidos y con el corazón en las alturas!"
    ]
}


@ns.route('/instrucciones')
class CuadernilloInstrucciones(Resource):
    def get(self):
        """Instrucciones y reglas del reto de 100 citas románticas"""
        return INSTRUCCIONES, 200


@ns.route('/cierre')
class CuadernilloCierre(Resource):
    def get(self):
        """Mensaje de cierre al completar las 100 citas"""
        return MENSAJE_CIERRE, 200


@ns.route('/completo')
class CuadernilloCompleto(Resource):
    def get(self):
        """Contenido completo del cuadernillo (instrucciones + mensaje de cierre)"""
        return {
            'instrucciones': INSTRUCCIONES,
            'mensaje_cierre': MENSAJE_CIERRE
        }, 200


@ns.route('/estado')
class CuadernilloEstado(Resource):
    @jwt_required()
    def get(self):
        """Estado del cuadernillo del usuario: cuántas citas completó y si desbloqueó el mensaje de cierre"""
        usuario_id = int(get_jwt_identity())

        total_completadas = Progreso.query.filter_by(
            usuario_id=usuario_id,
            completado=True
        ).count()

        completado = total_completadas >= 100
        porcentaje = min(round((total_completadas / 100) * 100, 1), 100)

        respuesta = {
            'citas_completadas': total_completadas,
            'meta': 100,
            'porcentaje': porcentaje,
            'completado': completado,
        }

        if completado:
            respuesta['mensaje_cierre'] = MENSAJE_CIERRE

        return respuesta, 200
