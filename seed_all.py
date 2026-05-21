"""
Seeder completo para 100 Citas Románticas en La Paz.
Ejecutar: python seed_all.py

Crea:
  - 2 roles (admin, usuario_normal)
  - 7 departamentos de La Paz
  - 10 categorías
  - 100 citas repartidas entre categorías y departamentos
  - 3 planes de suscripción
  - 4 usuarios de prueba (1 admin + 3 usuarios)
  - 2 grupos (parejas)
  - Miembros en los grupos
  - Progreso / recuerdos de ejemplo
  - Mensajes de ejemplo
  - Suscripciones de ejemplo
"""

from app import create_app
from app.extensions import bcrypt, db
from app.models import (
    Role, User, Departamento, Categoria, Cita,
    PlanSuscripcion, Grupo, GrupoMiembro,
    Progreso, Mensaje, Suscripcion,
)
from datetime import date, datetime, timedelta, timezone

app = create_app()

def _now():
    return datetime.now(timezone.utc)


DEPARTAMENTOS = [
    {"nombre": "La Paz Centro",               "orden_desbloqueo": 1},
    {"nombre": "Sopocachi",                   "orden_desbloqueo": 2},
    {"nombre": "Miraflores",                  "orden_desbloqueo": 3},
    {"nombre": "San Miguel / Calacoto",       "orden_desbloqueo": 4},
    {"nombre": "El Alto",                     "orden_desbloqueo": 5},
    {"nombre": "Valle de la Luna / Mallasa",  "orden_desbloqueo": 6},
    {"nombre": "Excursiones (Tiwanaku, Urmiri)", "orden_desbloqueo": 7},
]

CATEGORIAS = [
    "Gastronomía Local",
    "Naturaleza y Miradores",
    "Cultura e Historia",
    "Arte y Creatividad",
    "Aventura Urbana",
    "Spa y Bienestar",
    "Noche Romántica",
    "En Casa",
    "Mercados y Artesanía",
    "Voluntariado Juntos",
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

# (nombre, descripcion, cat_idx 0-based, depto_idx 0-based)
CITAS = [
    # Gastronomía Local (0) — depto La Paz Centro (0) y Sopocachi (1)
    ("Salteñas de madrugada",        "Madrugar juntos para comer las mejores salteñas de La Paz antes de las 10am.", 0, 0),
    ("Recorrido de tucumanas",       "Prueben tucumanas de 3 puestos del mercado y voten cuál es la mejor.", 0, 0),
    ("Cena en el Mercado Lanza",     "Elijan un puesto del Mercado Lanza y coman como locales: picante, fricasé o pique macho.", 0, 0),
    ("Cocinemos comida típica",      "Elijan una receta paceña (chairo, fricasé) y cocínenla juntos desde cero.", 0, 0),
    ("Café de altura en Sopocachi",  "Reserven una mesa en una cafetería boutique y pidan el café más exótico del menú.", 0, 1),
    ("Ruta de api con pastel",       "Una mañana de invierno, busquen el mejor api caliente con pastel de la ciudad.", 0, 0),
    ("Cena romántica paceña",        "Reserven en un restaurante de cocina boliviana contemporánea.", 0, 1),
    ("Helados artesanales en el parque", "Compren helados de sabores bolivianos y paseen por el Parque Urbano.", 0, 1),
    ("Desayuno sorpresa en cama",    "Prepara un desayuno boliviano completo y llévaselo a la cama.", 0, 0),
    ("Picante de lengua en el mercado", "Atrevanse con el plato más contundente: picante de lengua con chuño phuti.", 0, 0),

    # Naturaleza y Miradores (1) — deptos varios
    ("Amanecer en Killi Killi",      "Madrugar para ver el amanecer sobre La Paz desde el Mirador Killi Killi.", 1, 0),
    ("Valle de la Luna al atardecer","Recorrer las formaciones lunares y ver el atardecer desde sus puntos más altos.", 1, 5),
    ("Picnic en el Parque Urbano",   "Preparar una canasta con snacks y pasar la tarde de picnic en el Parque Urbano.", 1, 1),
    ("Teleférico nocturno",          "Tomar el teleférico de noche para ver las luces de La Paz desde las cabinas.", 1, 0),
    ("Caminata al Choqueyapu",       "Seguir el recorrido del río Choqueyapu por la ciudad.", 1, 0),
    ("Mirador de El Alto al anochecer","Subir a El Alto y ver cómo se enciende la mancha urbana de La Paz.", 1, 4),
    ("Jardín Botánico de Cota Cota", "Recorrer el Jardín Botánico de la UMSA, aprendiendo sobre flora nativa boliviana.", 1, 1),
    ("Caminata a Hampaturi",         "Excursión a las lagunas de Hampaturi, llevando almuerzo y termo.", 1, 5),
    ("Parque Mallasa en bicicleta",  "Alquilar bicicletas y recorrer el Parque Mallasa y sus alrededores naturales.", 1, 5),
    ("Observación de estrellas en altura","Subir a Killi Killi de noche para observar estrellas. Llevar frazadas.", 1, 0),

    # Cultura e Historia (2) — Centro y excursiones
    ("Museo de Etnografía MUSEF",    "Recorrer el MUSEF y descubrir la diversidad cultural de Bolivia.", 2, 0),
    ("Calle Jaén y sus museos",      "Recorrer la calle Jaén, la más colonial de La Paz, visitando sus 5 museos.", 2, 0),
    ("Tour del centro histórico",    "Tour a pie: Plaza Murillo, Congreso, Catedral y calles coloniales.", 2, 0),
    ("Museo de Metales Preciosos",   "Visitar el Museo del Oro y aprender sobre orfebrería precolombina boliviana.", 2, 0),
    ("Tiwanaku de día completo",     "Excursión a las ruinas de Tiwanaku, la civilización más importante del altiplano.", 2, 6),
    ("Biblioteca Municipal",         "Ir juntos a la Biblioteca, elegir un libro y leer en silencio compartido.", 2, 0),
    ("Obra de teatro",               "Comprar entradas para una obra de teatro en el Teatro Municipal.", 2, 0),
    ("Recorrido de iglesias históricas","Visitar las iglesias más antiguas: San Francisco, Sagrado Corazón, Santo Domingo.", 2, 0),
    ("Museo de Arte Contemporáneo",  "Recorrer el Museo de Arte Contemporáneo Plaza y conversar sobre las obras.", 2, 1),
    ("Barrio de San Pedro a pie",    "Recorrer el barrio de San Pedro: su mercado, plaza e iglesia.", 2, 0),

    # Arte y Creatividad (3) — Sopocachi
    ("Taller de pintura en pareja",  "Inscribirse en un taller: cada uno pinta al otro. Guardar los cuadros como recuerdo.", 3, 1),
    ("Galería de arte en Sopocachi", "Recorrer las galerías de arte de Sopocachi un sábado por la tarde.", 3, 1),
    ("Taller de cerámica",           "Aprender juntos a hacer cerámica y crear un objeto compartido.", 3, 1),
    ("Fotografía urbana en pareja",  "Salir con sus celulares a fotografiar La Paz como si fueran turistas.", 3, 0),
    ("Graffiti tour en La Paz",      "Recorrer los murales y graffitis más importantes de la ciudad.", 3, 1),
    ("Escribir una historia juntos", "Empezar un cuento corto sobre una pareja en La Paz. Alternar párrafos.", 3, 1),
    ("Feria de artistas locales",    "Ir a una feria de arte local, conocer artistas paceños y comprar una obra.", 3, 1),
    ("Noche de cine independiente",  "Ir al Cinematógrafo del MUSEF a ver una película boliviana independiente.", 3, 0),
    ("Taller de origami",            "Aprender origami juntos en casa con tutoriales. Intercambiar figuras.", 3, 0),
    ("Scrapbook de sus recuerdos",   "Imprimir fotos y crear juntos un álbum scrapbook con notas y decoraciones.", 3, 0),

    # Aventura Urbana (4) — El Alto y teleférico
    ("Todas las líneas del teleférico","El reto: recorrer todas las líneas del Mi Teleférico en un solo día.", 4, 0),
    ("Bicicleta por la ciclovía",    "Los domingos la Av. Arce es ciclovía. Alquilar bicicletas y recorrerla.", 4, 1),
    ("Correr juntos el Parque Urbano","Madrugar y salir a correr juntos por el Parque Urbano.", 4, 1),
    ("Escalar el Huayna Potosí",     "Contratar guía y llegar al campo base del Huayna Potosí.", 4, 6),
    ("Geocaching urbano",            "Descargar una app de geocaching y buscar tesoros escondidos por la ciudad.", 4, 0),
    ("Descubrir una calle desconocida","Elegir al azar un barrio del mapa y explorar una calle que nadie conoce.", 4, 4),
    ("Paintball en La Paz",          "Ir juntos a jugar paintball. Un equipo contra el otro.", 4, 4),
    ("Yoga al amanecer en el parque","Hacer su propia sesión de yoga al amanecer en el parque.", 4, 1),
    ("Rally fotográfico por La Paz", "Crear una lista de 10 cosas raras de La Paz para fotografiar.", 4, 0),
    ("Tour en minibús de El Alto",   "Subir a El Alto y recorrer sus mercados y miradores en minibús.", 4, 4),

    # Spa y Bienestar (5) — Calacoto / Mallasa
    ("Día de spa en pareja",         "Reservar un paquete de spa para dos: masajes, jacuzzi y sauna.", 5, 3),
    ("Masajes relajantes en casa",   "Comprar aceites de masaje y darse masajes mutuamente. Poner música suave.", 5, 0),
    ("Baños termales de Urmiri",     "Excursión a los baños termales de Urmiri, a 2 horas de La Paz.", 5, 6),
    ("Meditación guiada en pareja",  "Seguir una meditación guiada de 30 minutos juntos.", 5, 0),
    ("Tarde de máscaras faciales",   "Comprar máscaras faciales, ponérselas juntos y ver una película.", 5, 0),
    ("Caminata meditativa en la naturaleza","Ir al Valle de la Luna y caminar en silencio durante 20 minutos.", 5, 5),
    ("Clase de yoga para parejas",   "Buscar una clase de yoga para parejas e inscribirse juntos.", 5, 1),
    ("Noche de reflexión y gratitud","Apagar pantallas, encender velas y escribir 10 cosas que agradecen del otro.", 5, 0),
    ("Spa en casa con ritual",       "Preparar un ritual de spa completo en casa con sales, velas y aceites.", 5, 0),
    ("Desconexión digital de 24h",   "Apagar teléfonos por 24 horas y dedicarse completamente el uno al otro.", 5, 0),

    # Noche Romántica (6) — Sopocachi / centro
    ("Cena a la luz de velas en casa","Preparar juntos una cena especial, decorar con velas y comer sin teléfonos.", 6, 0),
    ("Bar de cócteles artesanales",  "Ir a un bar de cócteles de Sopocachi y pedir el más inusual del menú.", 6, 1),
    ("Noche de baile de salsa",      "Tomar una clase de salsa y después ir a una discoteca latina a practicar.", 6, 0),
    ("Karaoke en pareja",            "Ir a un karaoke y cantarse canciones el uno al otro.", 6, 0),
    ("Concierto en vivo",            "Comprar entradas para un concierto: jazz, rock, folclore o lo que gusten.", 6, 1),
    ("Stargazing con vino boliviano","Subir a un mirador con una botella de vino y observar las estrellas.", 6, 0),
    ("Cena con vista nocturna",      "Reservar en un restaurante con terraza y vista panorámica de la ciudad.", 6, 1),
    ("Escribirse cartas a mano",     "Cada uno escribe una carta sincera al otro. Intercambiarlas y leerlas.", 6, 0),
    ("Noche de juegos de mesa",      "Elegir 3 juegos de mesa y pasar la noche jugando.", 6, 0),
    ("Recrear su primera cita",      "Volver al lugar de su primera cita y recrear el momento.", 6, 1),

    # En Casa (7)
    ("Maratón de películas favoritas","Cada uno elige su película favorita de todos los tiempos. Verlas juntos.", 7, 0),
    ("Concurso de cocina en casa",   "Cocinar un plato sorpresa con los mismos 5 ingredientes y catar.", 7, 0),
    ("Mapa de sueños compartidos",   "Hacer un vision board: recortar imágenes de lo que quieren lograr juntos.", 7, 0),
    ("Noche de karaoke en pijama",   "Ponerse pijamas y cantar juntos las canciones más vergonzosas de la infancia.", 7, 0),
    ("Fortaleza de almohadas",       "Construir la mejor fortaleza con almohadones y cobijas. Merendar adentro.", 7, 0),
    ("Álbum de fotos de la relación","Juntar fotos digitales, imprimirlas y ordenarlas en un álbum físico.", 7, 0),
    ("Maratón de series nuevas",     "Elegir una serie que ninguno haya visto y ver los 3 primeros episodios.", 7, 0),
    ("Las 36 preguntas de la ciencia","Responder las 36 preguntas que acercan a las personas. Sin filtros.", 7, 0),
    ("Tarde de juegos retro",        "Buscar juegos retro de la infancia (cartas, monopoly) y jugar toda la tarde.", 7, 0),
    ("Noche de recetas nuevas",      "Elegir una receta que nunca hayan hecho y prepararla juntos desde cero.", 7, 0),

    # Mercados y Artesanía (8) — Centro / El Alto
    ("Feria 16 de Julio en El Alto", "Ir a la Feria 16 de Julio: el mercado más grande de Bolivia.", 8, 4),
    ("Mercado de brujas",            "Recorrer la Calle Linares y el Mercado de Brujas. Comprar un amuleto.", 8, 0),
    ("Artesanías de la Calle Sagárnaga","Recorrer la Calle Sagárnaga buscando la artesanía más representativa.", 8, 0),
    ("Mercado Rodríguez al amanecer","Madrugar e ir al Mercado Rodríguez cuando abren los puestos de flores.", 8, 0),
    ("Mercado de pulgas",            "Ir al mercado de pulgas a buscar un objeto antiguo que cuente una historia.", 8, 0),
    ("Taller de tejido artesanal",   "Aprender a tejer en un taller artesanal y crear una prenda para el otro.", 8, 0),
    ("Comprar e ir al mercado",      "Ir al mercado, comprar ingredientes frescos y cocinar con lo que encuentren.", 8, 0),
    ("Feria de productores ecológicos","Ir a una feria orgánica, probar muestras y comprar algo especial.", 8, 1),
    ("Anticuchos nocturnos",         "Buscar el mejor puesto de anticuchos de la ciudad al caer la noche.", 8, 0),
    ("Noche de anticuchos y chicha", "Combinar una noche de anticuchos con chicha paceña en una chichería.", 8, 0),

    # Voluntariado Juntos (9) — varios
    ("Voluntariado en albergue",     "Pasar una mañana como voluntarios en un albergue de animales de La Paz.", 9, 0),
    ("Donación de ropa juntos",      "Revisar sus closets, seleccionar ropa en buen estado y llevarla a donación.", 9, 0),
    ("Plantar un árbol",             "Participar en una jornada de reforestación con una organización ambiental.", 9, 5),
    ("Cocinar para una olla común",  "Preparar comida en cantidad y llevarla a un comedor popular.", 9, 0),
    ("Limpiar un espacio verde",     "Unirse a una jornada de limpieza de parque o quebrada de la ciudad.", 9, 0),
    ("Enseñar algo a otros",         "Compartir algo que saben en un espacio comunitario (cocina, música, idioma).", 9, 0),
    ("Visitar adultos mayores",      "Llevar flores o entretenimiento a un asilo de ancianos de La Paz.", 9, 0),
    ("Apoyo escolar en comunidad",   "Ir a un colegio de zona periférica a apoyar una jornada educativa.", 9, 4),
    ("Construir junto a TECHO",      "Participar en una construcción de vivienda con la organización TECHO Bolivia.", 9, 4),
    ("Cita 100 — Celebración Final", "¡Lo lograron! Crear juntos su propia celebración especial. Este momento es suyo.", 9, 1),
]

USUARIOS = [
    {"nombre": "Admin Principal",   "email": "admin@citas.bo",    "password": "admin123",   "rol_id": 1},
    {"nombre": "Carlos Mamani",     "email": "carlos@citas.bo",   "password": "test1234",   "rol_id": 2},
    {"nombre": "Sofía Quispe",      "email": "sofia@citas.bo",    "password": "test1234",   "rol_id": 2},
    {"nombre": "Diego Flores",      "email": "diego@citas.bo",    "password": "test1234",   "rol_id": 2},
    {"nombre": "Valentina Cruz",    "email": "valentina@citas.bo","password": "test1234",   "rol_id": 2},
]

ANECDOTAS = [
    "Fue una noche mágica que nunca olvidaremos. La ciudad de La Paz nos recibió con sus luces y su cielo estrellado.",
    "Nos reímos tanto que casi no podíamos caminar. Definitivamente repetiremos esta cita.",
    "Fue más difícil de lo que pensábamos, pero lo logramos juntos. Eso es lo que importa.",
    "El frío de La Paz no pudo con nosotros. Llegamos abrazados desde el principio hasta el final.",
    "Descubrimos un lugar nuevo de nuestra ciudad que no conocíamos. La Paz siempre sorprende.",
    "Nos prometimos volver a hacer esto cada año. Una tradición romántica paceña.",
    "Fue nuestra primera vez haciendo esto juntos y no será la última.",
    "Aprendimos algo nuevo el uno del otro. La aventura nunca termina.",
]

# ─── SEEDER ───────────────────────────────────────────────────────────────────

with app.app_context():

    # 1. Roles
    if Role.query.count() == 0:
        db.session.add_all([
            Role(id=1, nombre='administrador'),
            Role(id=2, nombre='usuario_normal'),
        ])
        db.session.commit()
        print("✓ Roles creados")
    else:
        print("- Roles ya existen")

    # 2. Departamentos
    if Departamento.query.count() == 0:
        deptos = [Departamento(**d) for d in DEPARTAMENTOS]
        db.session.add_all(deptos)
        db.session.commit()
        print(f"✓ {len(deptos)} departamentos creados")
    else:
        print("- Departamentos ya existen")
    deptos_db = Departamento.query.order_by(Departamento.orden_desbloqueo).all()

    # 3. Categorías
    if Categoria.query.count() == 0:
        cats = [Categoria(nombre=n) for n in CATEGORIAS]
        db.session.add_all(cats)
        db.session.commit()
        print(f"✓ {len(cats)} categorías creadas")
    else:
        print("- Categorías ya existen")
    cats_db = Categoria.query.order_by(Categoria.id).all()

    # 4. Planes
    if PlanSuscripcion.query.count() == 0:
        planes = [PlanSuscripcion(**p) for p in PLANES]
        db.session.add_all(planes)
        db.session.commit()
        print(f"✓ {len(planes)} planes creados")
    else:
        print("- Planes ya existen")

    # 5. Citas
    if Cita.query.count() == 0:
        for nombre, desc, cat_idx, depto_idx in CITAS:
            cat_id   = cats_db[cat_idx].id   if cat_idx < len(cats_db)   else None
            depto_id = deptos_db[depto_idx].id if depto_idx < len(deptos_db) else None
            db.session.add(Cita(
                nombre=nombre,
                descripcion=desc,
                categoria_id=cat_id,
                departamento_id=depto_id,
                activo=True,
            ))
        db.session.commit()
        print(f"✓ {len(CITAS)} citas creadas")
    else:
        print("- Citas ya existen")
    citas_db = Cita.query.order_by(Cita.id).all()

    # 6. Usuarios
    emails_existentes = {u.email for u in User.query.all()}
    usuarios_creados = []
    for u in USUARIOS:
        if u["email"] not in emails_existentes:
            nuevo = User(
                nombre=u["nombre"],
                email=u["email"],
                password_hash=bcrypt.generate_password_hash(u["password"]).decode("utf-8"),
                rol_id=u["rol_id"],
                activo=True,
                fecha_registro=_now(),
            )
            db.session.add(nuevo)
            usuarios_creados.append(nuevo)
    if usuarios_creados:
        db.session.commit()
        print(f"✓ {len(usuarios_creados)} usuarios creados")
    else:
        print("- Usuarios seed ya existen")
    usuarios_db = User.query.order_by(User.id).all()

    # A partir de aquí usamos los usuarios normales (índice 1 en adelante)
    user_carlos    = next((u for u in usuarios_db if u.email == "carlos@citas.bo"),    None)
    user_sofia     = next((u for u in usuarios_db if u.email == "sofia@citas.bo"),     None)
    user_diego     = next((u for u in usuarios_db if u.email == "diego@citas.bo"),     None)
    user_valentina = next((u for u in usuarios_db if u.email == "valentina@citas.bo"), None)

    # 7. Grupos
    codigos_existentes = {g.codigo_invitacion for g in Grupo.query.all()}
    if "CARSOFI1" not in codigos_existentes and user_carlos and user_sofia:
        g1 = Grupo(
            nombre="Carlos & Sofía",
            tipo="pareja",
            codigo_invitacion="CARSOFI1",
            creado_por=user_carlos.id,
            activo=True,
            fecha_creacion=_now(),
        )
        db.session.add(g1)
        db.session.flush()

        db.session.add_all([
            GrupoMiembro(grupo_id=g1.id, usuario_id=user_carlos.id, es_admin=True),
            GrupoMiembro(grupo_id=g1.id, usuario_id=user_sofia.id,  es_admin=False),
        ])

        if user_diego and user_valentina:
            g2 = Grupo(
                nombre="Diego & Valentina",
                tipo="pareja",
                codigo_invitacion="DIEGOVAL2",
                creado_por=user_diego.id,
                activo=True,
                fecha_creacion=_now(),
            )
            db.session.add(g2)
            db.session.flush()
            db.session.add_all([
                GrupoMiembro(grupo_id=g2.id, usuario_id=user_diego.id,     es_admin=True),
                GrupoMiembro(grupo_id=g2.id, usuario_id=user_valentina.id, es_admin=False),
            ])

        db.session.commit()
        print("✓ Grupos y miembros creados")
    else:
        print("- Grupos ya existen o faltan usuarios")

    # 8. Progreso / Recuerdos (Carlos completó 12 citas, Diego 5)
    prog_carlos_existe = user_carlos and Progreso.query.filter_by(usuario_id=user_carlos.id).count() > 0
    if not prog_carlos_existe and user_carlos and citas_db:
        progresos = []
        for i, cita in enumerate(citas_db[:12]):
            dias_atras = (12 - i) * 7
            fecha = _now() - timedelta(days=dias_atras)
            progresos.append(Progreso(
                usuario_id=user_carlos.id,
                cita_id=cita.id,
                tipo="individual",
                completado=True,
                calificacion=((i % 5) + 1),
                anecdota=ANECDOTAS[i % len(ANECDOTAS)],
                fecha_completado=fecha,
            ))

        if user_diego:
            for i, cita in enumerate(citas_db[:5]):
                dias_atras = (5 - i) * 10
                fecha = _now() - timedelta(days=dias_atras)
                progresos.append(Progreso(
                    usuario_id=user_diego.id,
                    cita_id=cita.id,
                    tipo="individual",
                    completado=True,
                    calificacion=((i % 5) + 1),
                    anecdota=ANECDOTAS[(i + 3) % len(ANECDOTAS)],
                    fecha_completado=fecha,
                ))

        db.session.add_all(progresos)
        db.session.commit()
        print(f"✓ {len(progresos)} registros de progreso creados")
    else:
        print("- Progreso ya existe o faltan datos")

    # 9. Mensajes de ejemplo
    msgs_existen = user_carlos and Mensaje.query.filter_by(de_usuario_id=user_carlos.id).count() > 0
    if not msgs_existen and user_carlos and user_sofia:
        msgs = [
            Mensaje(de_usuario_id=user_carlos.id, para_usuario_id=user_sofia.id,
                    mensaje="¿Cuándo hacemos la próxima cita? 😍", leido=True,  fecha=_now() - timedelta(hours=5)),
            Mensaje(de_usuario_id=user_sofia.id,  para_usuario_id=user_carlos.id,
                    mensaje="Este fin de semana! Ya tengo todo listo 🌹", leido=True,  fecha=_now() - timedelta(hours=4)),
            Mensaje(de_usuario_id=user_carlos.id, para_usuario_id=user_sofia.id,
                    mensaje="¡Perfecto! Pasaremos a buscarte a las 7pm", leido=False, fecha=_now() - timedelta(hours=1)),
        ]
        db.session.add_all(msgs)
        db.session.commit()
        print(f"✓ {len(msgs)} mensajes creados")
    else:
        print("- Mensajes ya existen")

    # 10. Suscripciones
    sub_carlos_existe = user_carlos and Suscripcion.query.filter_by(usuario_id=user_carlos.id).count() > 0
    if not sub_carlos_existe and user_carlos:
        plan_pareja = PlanSuscripcion.query.filter_by(codigo="pareja").first()
        if plan_pareja:
            sus = Suscripcion(
                usuario_id=user_carlos.id,
                plan_id=plan_pareja.id,
                fecha_inicio=date.today() - timedelta(days=30),
                fecha_expiracion=date.today() + timedelta(days=335),
                activo=True,
                tipo_periodo="anual",
            )
            db.session.add(sus)
            db.session.commit()
            print("✓ Suscripción de ejemplo creada")
    else:
        print("- Suscripciones ya existen")

    print("\n✅ Seed completado exitosamente.\n")
    print("Credenciales de prueba:")
    print("  admin@citas.bo       / admin123   (Administrador)")
    print("  carlos@citas.bo      / test1234   (Usuario con 12 citas completadas)")
    print("  sofia@citas.bo       / test1234   (Pareja de Carlos)")
    print("  diego@citas.bo       / test1234   (Usuario con 5 citas completadas)")
    print("  valentina@citas.bo   / test1234   (Pareja de Diego)")