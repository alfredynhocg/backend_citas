from .extensions import db
from .models import Category, Date

CATEGORIES = [
    {"name": "Gastronomía Local",     "icon": "🍽️",  "color": "#E8A87C"},
    {"name": "Naturaleza y Miradores","icon": "🌄",  "color": "#82C341"},
    {"name": "Cultura e Historia",    "icon": "🏛️",  "color": "#D4A017"},
    {"name": "Arte y Creatividad",    "icon": "🎨",  "color": "#C9449D"},
    {"name": "Aventura Urbana",       "icon": "🚵",  "color": "#3A86FF"},
    {"name": "Spa y Bienestar",       "icon": "💆",  "color": "#A8DADC"},
    {"name": "Noche Romántica",       "icon": "🌙",  "color": "#6A0572"},
    {"name": "En Casa",               "icon": "🏠",  "color": "#F4A261"},
    {"name": "Mercados y Artesanía",  "icon": "🛍️",  "color": "#E76F51"},
    {"name": "Voluntariado Juntos",   "icon": "❤️",  "color": "#E63946"},
]

DATES_DATA = [
    (1,  "Salteñas de madrugada", "Madrugar juntos para comer las mejores salteñas de La Paz antes de las 10am. Busquen su salteñería favorita de barrio.", 0, "facil", "1 hora", "gratis", "Centro / cualquier barrio"),
    (2,  "Recorrido de tucumanas", "Prueben tucumanas de diferentes puestos del mercado y voten cuál es la mejor. Una tarde de jueces gastronómicos.", 0, "facil", "2 horas", "economica", "Mercado Rodriguez, Sopocachi"),
    (3,  "Cena en el Mercado Lanza", "Elijan un puesto del Mercado Lanza y coman como locales: picante de pollo, fricasé o pique macho.", 0, "facil", "2 horas", "economica", "Mercado Lanza, Centro"),
    (4,  "Cocinemos juntos comida típica", "Elijan una receta paceña (chairo, fricasé) y cocínenla juntos desde cero. El que menos sabe cocina más.", 0, "media", "3 horas", "economica", "En casa"),
    (5,  "Café de altura en Sopocachi", "Reserven una mesa en una cafetería boutique de Sopocachi y pidan el café de especialidad más exótico del menú.", 0, "facil", "2 horas", "moderada", "Sopocachi"),
    (6,  "Ruta de api con pastel", "Una mañana de invierno, busquen el mejor api caliente con pastel de la ciudad. Comparen 3 puestos.", 0, "facil", "2 horas", "gratis", "Mercado central / calles del centro"),
    (7,  "Cena romántica en restaurante paceño", "Reserven en un restaurante de cocina boliviana contemporánea y pidan el menú degustación.", 0, "media", "3 horas", "moderada", "Sopocachi / Calacoto"),
    (8,  "Helados artesanales en el parque", "Compren helados artesanales de sabores bolivianos (mocochinchi, tumbo) y paseen por el parque.", 0, "facil", "1-2 horas", "gratis", "Parque Urbano Central"),
    (9,  "Desayuno sorpresa en cama", "Uno de los dos prepara un desayuno boliviano completo (marraquetas, queso, api, huevo frito) y se lo lleva a la cama.", 0, "media", "2 horas", "economica", "En casa"),
    (10, "Picante de lengua en el mercado", "Atrevanse con el plato más contundente de la gastronomía paceña: picante de lengua con chuño phuti.", 0, "media", "2 horas", "economica", "Mercado de comidas, Centro"),
    (11, "Noche de anticuchos", "Busquen el mejor puesto de anticuchos de la ciudad al caer la noche y coman parados en la calle como verdaderos paceños.", 0, "facil", "1-2 horas", "gratis", "Av. 6 de Agosto / calles del centro"),
    (12, "Clase de cocina boliviana", "Inscríbanse juntos en un taller de cocina boliviana y aprendan a preparar platos tradicionales paceños.", 0, "retadora", "4 horas", "moderada", "Escuelas de gastronomía, Miraflores"),
    (13, "Merienda de humintas", "Compren humintas recién hechas en el mercado y cómanlas mientras pasean por el malecón.", 0, "facil", "1 hora", "gratis", "Mercados barriales"),
    (14, "Degustación de chicha y singani", "Visiten una chichería tradicional y prueben la chicha de maíz paceña, luego un singani boliviano.", 0, "media", "2 horas", "economica", "Achachicala / zonas tradicionales"),
    (15, "Tapi y chocolate caliente", "Una tarde lluviosa: preparen tapi (maíz tostado) y chocolate caliente en casa mientras ven una película.", 0, "facil", "2 horas", "gratis", "En casa"),
    (16, "Amanecer en el Mirador Killi Killi", "Madrugar para ver el amanecer sobre La Paz desde el Mirador Killi Killi. Llevar termos de café.", 1, "media", "2 horas", "gratis", "Killi Killi, Villa Pabón"),
    (17, "Valle de la Luna al atardecer", "Recorrer las formaciones lunares del Valle de la Luna y ver el atardecer desde sus puntos más altos.", 1, "facil", "3 horas", "economica", "Valle de la Luna, Mallasa"),
    (18, "Picnic en el Parque Urbano", "Preparar una canasta con snacks y telas, y pasar la tarde haciendo picnic en el Parque Urbano Central.", 1, "facil", "3 horas", "economica", "Parque Urbano Central, Av. Arce"),
    (19, "Teleférico nocturno", "Tomar el teleférico de noche para ver las luces de La Paz desde las cabinas. Elegir la línea con mejor panorama.", 1, "facil", "2 horas", "economica", "Red de teleféricos"),
    (20, "Caminata al Choqueyapu", "Seguir el recorrido del río Choqueyapu por la ciudad, desde su cauce histórico hasta zonas verdes.", 1, "media", "3 horas", "gratis", "Centro histórico"),
    (21, "Mirador de El Alto al anochecer", "Subir a El Alto y ver cómo se enciende la mancha urbana de La Paz al caer la noche.", 1, "media", "2 horas", "economica", "El Alto, zona norte"),
    (22, "Jardín Botánico de Cota Cota", "Recorrer el Jardín Botánico de la UMSA, aprendiendo sobre flora nativa boliviana.", 1, "facil", "2 horas", "gratis", "Cota Cota, sur de La Paz"),
    (23, "Caminata a Hampaturi", "Excursión de día completo a las lagunas de Hampaturi, llevando almuerzo y termo.", 1, "retadora", "8 horas", "economica", "Hampaturi, afueras de La Paz"),
    (24, "Parque Mallasa en bicicleta", "Alquilar bicicletas y recorrer el Parque Mallasa y sus alrededores naturales.", 1, "media", "4 horas", "economica", "Mallasa"),
    (25, "Observación de estrellas en altura", "Subir a un punto alto de la ciudad (Killi Killi o ladera este) de noche para observar estrellas. Llevar frazadas.", 1, "media", "3 horas", "gratis", "Mirador Killi Killi o similar"),
    (26, "Rincón de la Muerte al amanecer", "Madrugar para ver cómo los colores del amanecer pintan el dramático paisaje del Rincón de la Muerte en La Paz.", 1, "retadora", "3 horas", "gratis", "Ladera oeste, La Paz"),
    (27, "Paseo por el Parque de las Culturas", "Pasear por el Parque de las Culturas, observar arte urbano y disfrutar del espacio verde del centro.", 1, "facil", "2 horas", "gratis", "Parque de las Culturas, Miraflores"),
    (28, "Museo Nacional de Etnografía y Folklore", "Recorrer el MUSEF juntos y descubrir la diversidad cultural de Bolivia. Busquen el objeto que más les sorprenda.", 2, "facil", "2 horas", "economica", "MUSEF, Centro histórico"),
    (29, "Calle Jaén y sus museos", "Recorrer la calle Jaén, la más colonial de La Paz, visitando sus 5 pequeños museos temáticos.", 2, "facil", "3 horas", "economica", "Calle Jaén, Centro"),
    (30, "Tour del centro histórico", "Contratar un tour a pie por el centro histórico: Plaza Murillo, Congreso, Catedral y calles coloniales.", 2, "facil", "3 horas", "economica", "Centro histórico"),
    (31, "Museo de Metales Preciosos", "Visitar el Museo de Metales Preciosos (Museo del Oro) y aprender sobre la orfebrería precolombina boliviana.", 2, "facil", "2 horas", "economica", "Calle Jaén, Centro"),
    (32, "Tiwanaku de día completo", "Excursión a las ruinas de Tiwanaku, la civilización precolombina más importante del altiplano boliviano.", 2, "retadora", "10 horas", "moderada", "Tiwanaku (72 km de La Paz)"),
    (33, "Biblioteca Municipal y lectura en pareja", "Ir juntos a la Biblioteca Municipal, elegir un libro cada uno y leer en silencio compartido por una hora.", 2, "facil", "2 horas", "gratis", "Biblioteca Municipal, Centro"),
    (34, "Asistir a una obra de teatro", "Comprar entradas para una obra de teatro en el Teatro Municipal o el Teatro de Cámara.", 2, "media", "3 horas", "moderada", "Teatro Municipal Alberto Saavedra Pérez"),
    (35, "Recorrido de iglesias históricas", "Visitar las iglesias más antiguas de La Paz: San Francisco, Sagrado Corazón, Santo Domingo.", 2, "facil", "3 horas", "gratis", "Centro histórico"),
    (36, "Museo de Arte Contemporáneo Plaza", "Recorrer el Museo de Arte Contemporáneo Plaza y conversar sobre las obras que más les impactan.", 2, "facil", "2 horas", "economica", "Sopocachi"),
    (37, "Visita al Archivo Histórico de La Paz", "Pedir ver documentos históricos paceños en el Archivo Histórico y aprender sobre la historia de la ciudad.", 2, "media", "2 horas", "gratis", "UMSA, Miraflores"),
    (38, "Barrio de San Pedro a pie", "Recorrer el barrio de San Pedro: su mercado, plaza, iglesia y la icónica cárcel convertida en atracción.", 2, "facil", "3 horas", "gratis", "San Pedro"),
    (39, "Concierto de música folclórica", "Asistir a un concierto de música folklórica boliviana (peña folclórica) y aprender los ritmos del altiplano.", 2, "media", "3 horas", "economica", "Peñas folclóricas del centro"),
    (40, "Taller de pintura en pareja", "Inscribirse en un taller de pintura para parejas: cada uno pinta al otro. Guardar los cuadros como recuerdo.", 3, "media", "3 horas", "moderada", "Talleres de arte, Sopocachi"),
    (41, "Galería de arte en Sopocachi", "Recorrer las galerías de arte de Sopocachi un sábado por la tarde. Elegir su obra favorita y por qué.", 3, "facil", "2 horas", "gratis", "Sopocachi"),
    (42, "Taller de cerámica", "Aprender juntos a hacer cerámica y crear un objeto que compartan. Llevarlo a casa como recuerdo.", 3, "media", "4 horas", "moderada", "Talleres de cerámica, La Paz"),
    (43, "Fotografía urbana en pareja", "Salir con sus celulares a fotografiar La Paz como si fueran turistas por primera vez. Exponer sus mejores fotos.", 3, "facil", "3 horas", "gratis", "Centro histórico / Sopocachi"),
    (44, "Graffiti tour en La Paz", "Recorrer los murales y graffitis más importantes de la ciudad. Buscar el que mejor los represente como pareja.", 3, "facil", "3 horas", "gratis", "Sopocachi / Miraflores"),
    (45, "Escribir una historia juntos", "Empezar a escribir juntos un cuento corto sobre una pareja en La Paz. Alternar párrafos sin planear el final.", 3, "facil", "2 horas", "gratis", "En casa / cafetería"),
    (46, "Visitar una feria de artistas locales", "Ir a una feria de arte y artesanía local, conocer artistas paceños y comprar una obra pequeña como recuerdo.", 3, "facil", "3 horas", "economica", "Ferias de arte, Sopocachi / El Prado"),
    (47, "Noche de cine independiente", "Ir al Cinematógrafo del MUSEF o Cinemascope a ver una película boliviana o latinoamericana independiente.", 3, "facil", "3 horas", "economica", "MUSEF / Cinemateca Boliviana"),
    (48, "Taller de origami", "Aprender origami juntos en casa con tutoriales. Al terminar, intercambiar las figuras que hicieron.", 3, "facil", "2 horas", "gratis", "En casa"),
    (49, "Scrapbook de sus mejores recuerdos", "Imprimir fotos de sus momentos favoritos y crear juntos un álbum scrapbook con notas y decoraciones.", 3, "media", "4 horas", "economica", "En casa"),
    (50, "Todas las líneas del teleférico en un día", "El reto: recorrer todas las líneas del Mi Teleférico en un solo día, sin repetir estación.", 4, "retadora", "6 horas", "economica", "Red de teleféricos de La Paz"),
    (51, "Bicicleta por la ciclovía dominical", "Los domingos, la Av. Arce se convierte en ciclovía. Alquilar bicicletas y recorrerla de punta a punta.", 4, "facil", "3 horas", "economica", "Av. Arce, domingos"),
    (52, "Correr juntos el Parque Urbano", "Madrugar y salir a correr juntos por el Parque Urbano. Al terminar, desayuno saludable.", 4, "media", "2 horas", "gratis", "Parque Urbano Central"),
    (53, "Escalar el Huayna Potosí (campo base)", "Contratar guía y llegar al campo base del Huayna Potosí. Ver el glaciar más cercano a La Paz.", 4, "retadora", "8 horas", "moderada", "Huayna Potosí (25 km de La Paz)"),
    (54, "Geocaching urbano", "Descargar una app de geocaching y buscar tesoros escondidos por toda la ciudad de La Paz.", 4, "media", "4 horas", "gratis", "Toda la ciudad"),
    (55, "Descubrir una calle desconocida", "Elegir al azar un barrio del mapa y explorar una calle que ninguno de los dos conoce.", 4, "facil", "3 horas", "gratis", "Barrios de La Paz"),
    (56, "Paintball en La Paz", "Ir juntos a jugar paintball. Un equipo contra el otro (o juntos contra el mundo).", 4, "media", "2 horas", "moderada", "Paintball La Paz, zona norte"),
    (57, "Yoga al amanecer en el parque", "Encontrar una clase de yoga al aire libre en el parque o hacer su propia sesión al amanecer.", 4, "facil", "2 horas", "gratis", "Parques de Sopocachi / Miraflores"),
    (58, "Rally fotográfico por La Paz", "Crear una lista de 10 cosas raras de La Paz para fotografiar y ver quién las encuentra primero.", 4, "media", "4 horas", "gratis", "Toda la ciudad"),
    (59, "Tour en minibús de El Alto", "Subir a El Alto y recorrer sus mercados, avenidas y miradores en minibús como locales.", 4, "media", "4 horas", "gratis", "El Alto"),
    (60, "Día de spa en pareja", "Reservar un paquete de spa para dos: masajes, jacuzzi y sauna. Un día dedicado al descanso compartido.", 5, "facil", "4 horas", "moderada", "Spas de Calacoto / San Miguel"),
    (61, "Masajes relajantes en casa", "Comprar aceites de masaje y darse masajes mutuamente. Poner música suave y apagar el teléfono.", 5, "facil", "2 horas", "economica", "En casa"),
    (62, "Baños termales de Urmiri", "Excursión de día a los baños termales de Urmiri, a 2 horas de La Paz. Relajarse en aguas naturales.", 5, "media", "8 horas", "moderada", "Urmiri (2h de La Paz)"),
    (63, "Meditación guiada en pareja", "Seguir una meditación guiada de 30 minutos juntos. Luego compartir cómo se sienten.", 5, "facil", "1 hora", "gratis", "En casa"),
    (64, "Tarde de máscaras faciales", "Comprar máscaras faciales, ponérselas juntos y ver una película. Fotografiarse con las máscaras puestas.", 5, "facil", "2 horas", "economica", "En casa"),
    (65, "Caminata meditativa en la naturaleza", "Ir al Valle de la Luna o Mallasa y caminar en silencio durante 20 minutos, observando sin hablar.", 5, "media", "3 horas", "economica", "Valle de la Luna / Mallasa"),
    (66, "Clase de yoga para parejas", "Buscar una clase de yoga para parejas (acro-yoga o yoga restaurativo) e inscribirse juntos.", 5, "media", "2 horas", "moderada", "Studios de yoga, Sopocachi"),
    (67, "Noche de reflexión y gratitud", "Apagar pantallas, encender velas y escribir cada uno 10 cosas que agradecen del otro. Leerlas en voz alta.", 5, "facil", "2 horas", "gratis", "En casa"),
    (68, "Cena a la luz de velas en casa", "Preparar juntos una cena especial, decorar la mesa con velas y flores, y comer sin teléfonos.", 6, "media", "4 horas", "economica", "En casa"),
    (69, "Bar de cócteles artesanales", "Ir a un bar de cócteles artesanales de Sopocachi y pedir el cóctel más inusual del menú.", 6, "facil", "3 horas", "moderada", "Sopocachi"),
    (70, "Noche de baile de salsa", "Tomar una clase rápida de salsa y después ir a una discoteca latina a practicar.", 6, "media", "4 horas", "moderada", "Academias y discotecas, La Paz"),
    (71, "Karaoke en pareja", "Ir a un karaoke y cantarse canciones el uno al otro. Vale elegir canciones románticas cursis.", 6, "facil", "3 horas", "economica", "Karaokes del centro / Sopocachi"),
    (72, "Concierto en vivo", "Comprar entradas para un concierto en vivo: jazz, rock, folclore o cualquier género que les guste a ambos.", 6, "facil", "3 horas", "moderada", "Venues de La Paz"),
    (73, "Stargazing con botella de vino", "Subir a un punto alto de la ciudad con una botella de vino boliviano y observar las estrellas.", 6, "media", "3 horas", "economica", "Miradores de La Paz"),
    (74, "Cena con vista a La Paz nocturna", "Reservar en un restaurante con terraza y vista panorámica nocturna de la ciudad.", 6, "facil", "3 horas", "moderada", "Restaurantes con vista, Sopocachi"),
    (75, "Escribirse cartas a mano", "Cada uno escribe una carta sincera al otro. Intercambiarlas, leerlas en silencio y guardarlas.", 6, "facil", "2 horas", "gratis", "En casa"),
    (76, "Noche de juegos de mesa", "Elegir 3 juegos de mesa y pasar la noche jugando. El que pierde prepara el desayuno del día siguiente.", 6, "facil", "4 horas", "gratis", "En casa"),
    (77, "Recrear su primera cita", "Volver al lugar de su primera cita y recrear el momento. Si fue en otro lugar, describírselo al otro.", 6, "media", "3 horas", "economica", "Lugar de la primera cita"),
    (78, "Maratón de películas favoritas", "Cada uno elige su película favorita de todos los tiempos. Las ven juntos y explican por qué la eligieron.", 7, "facil", "6 horas", "gratis", "En casa"),
    (79, "Concurso de cocina en casa", "Cada uno cocina un plato sorpresa con los mismos 5 ingredientes. Catan los platos y votan.", 7, "media", "3 horas", "economica", "En casa"),
    (80, "Mapa de sueños compartidos", "Hacer un vision board juntos: recortar imágenes y palabras de lo que quieren lograr como pareja.", 7, "facil", "3 horas", "economica", "En casa"),
    (81, "Noche de karaoke en pijama", "Ponerse pijamas, abrir YouTube y cantar juntos las canciones más vergonzosas de su infancia.", 7, "facil", "2 horas", "gratis", "En casa"),
    (82, "Construir una fortaleza de almohadas", "Usar todos los almohadones, cobijas y sillas de la casa para construir la mejor fortaleza. Merendar adentro.", 7, "facil", "3 horas", "gratis", "En casa"),
    (83, "Álbum de fotos de la relación", "Juntar todas las fotos digitales de su relación, imprimirlas y ordenarlas en un álbum físico.", 7, "media", "4 horas", "economica", "En casa"),
    (84, "Maratón de series nuevas", "Elegir juntos una serie que ninguno haya visto y ver los primeros 3 episodios. Decidir si continúan.", 7, "facil", "4 horas", "gratis", "En casa"),
    (85, "Cuestionario de los 36 preguntas", "Responder juntos las famosas 36 preguntas que según la ciencia acercan a las personas. Sin filtros.", 7, "media", "3 horas", "gratis", "En casa"),
    (86, "Feria 16 de Julio en El Alto", "Ir a la Feria 16 de Julio (jueves o domingo): el mercado más grande de Bolivia. Perderse juntos en él.", 8, "media", "5 horas", "economica", "Feria 16 de Julio, El Alto"),
    (87, "Mercado de brujas", "Recorrer la Calle Linares y el Mercado de Brujas. Comprar un amuleto para la pareja.", 8, "facil", "2 horas", "economica", "Calle Linares / Sagárnaga, Centro"),
    (88, "Artesanías de la Calle Sagárnaga", "Recorrer la Calle Sagárnaga buscando la artesanía más representativa de Bolivia para llevar a casa.", 8, "facil", "3 horas", "economica", "Calle Sagárnaga, Centro"),
    (89, "Mercado Rodríguez al amanecer", "Madrugar e ir al Mercado Rodríguez cuando abren los puestos de flores y frutas. Comprar flores el uno al otro.", 8, "facil", "2 horas", "economica", "Mercado Rodríguez"),
    (90, "Buscar un objeto viejo en el mercado de pulgas", "Ir al mercado de pulgas a buscar un objeto antiguo que cuente una historia. Compartirla.", 8, "facil", "3 horas", "economica", "Mercados de pulgas, La Paz"),
    (91, "Taller de tejido artesanal", "Aprender a tejer con agujas en un taller artesanal y crear una pequeña prenda para el otro.", 8, "retadora", "4 horas", "moderada", "Talleres de artesanía, La Paz"),
    (92, "Comprar ingredientes y cocinar en el mercado", "Ir al mercado, comprar ingredientes frescos y cocinar juntos con lo que encuentren ese día.", 8, "media", "4 horas", "economica", "Mercado más cercano"),
    (93, "Feria de productores ecológicos", "Ir a una feria de productos orgánicos y ecológicos, probar muestras y comprar algo especial.", 8, "facil", "3 horas", "economica", "Ferias ecológicas, Sopocachi"),
    (94, "Voluntariado en albergue de animales", "Pasar una mañana como voluntarios en un albergue de animales de La Paz: dar de comer, limpiar y jugar.", 9, "media", "4 horas", "gratis", "Albergues de animales, La Paz"),
    (95, "Donación de ropa juntos", "Revisar juntos sus closets, seleccionar ropa en buen estado y llevarla a un centro de donación.", 9, "facil", "3 horas", "gratis", "Centros de donación, La Paz"),
    (96, "Plantar un árbol", "Contactar con una organización ambiental de La Paz y participar en una jornada de reforestación.", 9, "media", "4 horas", "gratis", "Zonas de reforestación, La Paz"),
    (97, "Cocinar para una olla común", "Preparar comida en cantidad y llevarla a una olla común barrial o comedor popular.", 9, "media", "5 horas", "economica", "Comedores populares, La Paz"),
    (98, "Limpiar un espacio verde", "Unirse a una jornada de limpieza de parque o quebrada de la ciudad. Ir con guantes y bolsas.", 9, "facil", "3 horas", "gratis", "Parques y quebradas de La Paz"),
    (99, "Enseñar algo que saben a otros", "Cada uno comparte algo que sabe hacer (cocina, idioma, música, dibujo) en un espacio comunitario.", 9, "retadora", "4 horas", "gratis", "Centros comunitarios, La Paz"),
    (100, "Cita 100: Celebración final", "Han completado las 100 citas. Crear juntos su propia celebración especial: el lugar, la comida y la actividad son elegidos por ustedes. Este momento es suyo.", 9, "retadora", "libre", "moderada", "Donde elijan"),
]


def seed_all() -> None:
    if Category.query.count() > 0:
        print("El seed ya fue ejecutado anteriormente. Saltando.")
        return

    categories = []
    for cat in CATEGORIES:
        c = Category(name=cat["name"], icon=cat["icon"], color=cat["color"])
        db.session.add(c)
        categories.append(c)

    db.session.flush()

    for row in DATES_DATA:
        order_num, title, description, cat_idx, difficulty, duration, cost, location_hint = row
        db.session.add(Date(
            order_num=order_num,
            title=title,
            description=description,
            category_id=categories[cat_idx].id,
            difficulty=difficulty,
            duration=duration,
            cost=cost,
            location_hint=location_hint,
        ))

    db.session.commit()
    print(f"Seed completado: {len(CATEGORIES)} categorías, {len(DATES_DATA)} citas.")
