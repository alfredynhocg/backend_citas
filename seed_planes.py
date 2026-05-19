"""
Ejecutar: python seed_planes.py
Inserta planes de suscripción y departamentos por defecto.
"""
from app import create_app
from app.extensions import db
from app.models import PlanSuscripcion, Departamento

app = create_app()

DEPARTAMENTOS = [
    {"nombre": "La Paz Centro", "orden_desbloqueo": 1},
    {"nombre": "Sopocachi", "orden_desbloqueo": 2},
    {"nombre": "Miraflores", "orden_desbloqueo": 3},
    {"nombre": "San Miguel / Calacoto", "orden_desbloqueo": 4},
    {"nombre": "El Alto", "orden_desbloqueo": 5},
    {"nombre": "Valle de la Luna / Mallasa", "orden_desbloqueo": 6},
    {"nombre": "Excursiones (Tiwanaku, Urmiri)", "orden_desbloqueo": 7},
]

PLANES = [
    {
        "nombre": "Gratuito",
        "codigo": "free",
        "descripcion": "Acceso al primer departamento. Perfecto para empezar.",
        "precio_mensual": 0,
        "precio_anual": 0,
        "max_integrantes": 2,
        "permite_grupo": False,
        "permite_individual": True,
        "departamentos_desbloquea": 1,
        "ventajas": "1 departamento incluido",
        "activo": True,
    },
    {
        "nombre": "Pareja",
        "codigo": "pareja",
        "descripcion": "Desbloquea 3 departamentos. Ideal para parejas.",
        "precio_mensual": 29,
        "precio_anual": 290,
        "max_integrantes": 2,
        "permite_grupo": False,
        "permite_individual": True,
        "departamentos_desbloquea": 3,
        "ventajas": "3 departamentos, acceso a citas exclusivas",
        "activo": True,
    },
    {
        "nombre": "Aventureros",
        "codigo": "aventureros",
        "descripcion": "Acceso completo a todos los departamentos y grupos.",
        "precio_mensual": 59,
        "precio_anual": 590,
        "max_integrantes": 6,
        "permite_grupo": True,
        "permite_individual": True,
        "departamentos_desbloquea": 7,
        "ventajas": "Todos los departamentos, grupos, citas premium",
        "activo": True,
    },
]

with app.app_context():
    # Departamentos
    if Departamento.query.count() == 0:
        for d in DEPARTAMENTOS:
            db.session.add(Departamento(**d))
        db.session.commit()
        print(f"✓ {len(DEPARTAMENTOS)} departamentos insertados")
    else:
        print("- Departamentos ya existen, saltando")

    # Planes
    if PlanSuscripcion.query.count() == 0:
        for p in PLANES:
            db.session.add(PlanSuscripcion(**p))
        db.session.commit()
        print(f"✓ {len(PLANES)} planes insertados")
    else:
        print("- Planes ya existen, saltando")

    print("\nSeed completado.")
