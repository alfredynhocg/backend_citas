"""
Seeder completo para todos los modulos de la app.
Agrega datos faltantes sin borrar lo existente.

Ejecutar: ./env/Scripts/python seed_completo.py
"""

from app import create_app
from app.extensions import db
from app.models import (
    User, Cita, Categoria, Departamento, Negocio, FotoNegocio,
    Grupo, GrupoMiembro, Progreso, Pago, PlanSuscripcion,
    Suscripcion, Mensaje, FotoCita, Certificado
)
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

app = create_app()

def _now():
    return datetime.now(timezone.utc)

def _ago(days=0, hours=0):
    return _now() - timedelta(days=days, hours=hours)

with app.app_context():
    users  = {u.email: u for u in User.query.all()}
    carlos    = users.get("carlos@citas.bo")
    sofia     = users.get("sofia@citas.bo")
    diego     = users.get("diego@citas.bo")
    valentina = users.get("valentina@citas.bo")
    admin_u   = users.get("admin@citas.bo")

    if not carlos:
        print("[ERROR] No hay usuarios seed. Ejecuta primero seed_all.py")
        exit(1)

    # ── 1. PROGRESO INDIVIDUAL — mas registros para recuerdos ─────────────────
    print("\n[1] Progreso individual (recuerdos)...")
    citas_db = Cita.query.filter_by(activo=True).order_by(Cita.id).all()

    ANECDOTAS = [
        "Una noche magica que nunca olvidaremos en La Paz.",
        "Nos reimos tanto que no podiamos caminar de regreso.",
        "El frio pacenio no pudo con nosotros, llegamos abrazados.",
        "Descubrimos un lugar nuevo de nuestra ciudad juntos.",
        "Prometimos volver a hacer esto cada anio, nuestra tradicion.",
        "Aprendimos algo nuevo el uno del otro en esta aventura.",
        "La ciudad nos regalo una vista que no esperabamos.",
        "Fue mas dificil de lo pensado, pero lo logramos juntos.",
        "El mejor plan improvisado que hemos tenido como pareja.",
        "Lloramos de risa y tambien de emocion, fue perfecto.",
        "Nunca pensamos que esto estaria tan cerca y fuera tan especial.",
        "La comida, la musica y la compania: todo fue increible.",
    ]

    # Carlos: 20 citas completadas
    prog_carlos = {p.cita_id for p in Progreso.query.filter_by(usuario_id=carlos.id, tipo="individual").all()}
    nuevos = 0
    for i, cita in enumerate(citas_db[:30]):
        if cita.id in prog_carlos:
            continue
        db.session.add(Progreso(
            usuario_id=carlos.id, cita_id=cita.id, tipo="individual",
            completado=True, calificacion=((i % 5) + 1),
            anecdota=ANECDOTAS[i % len(ANECDOTAS)],
            fecha_completado=_ago(days=(30 - i)),
        ))
        nuevos += 1
    db.session.commit()
    print(f"   Carlos: +{nuevos} registros")

    # Sofia: 18 citas completadas
    prog_sofia = {p.cita_id for p in Progreso.query.filter_by(usuario_id=sofia.id, tipo="individual").all()}
    nuevos = 0
    for i, cita in enumerate(citas_db[5:28]):
        if cita.id in prog_sofia:
            continue
        db.session.add(Progreso(
            usuario_id=sofia.id, cita_id=cita.id, tipo="individual",
            completado=True, calificacion=((i % 5) + 1),
            anecdota=ANECDOTAS[i % len(ANECDOTAS)],
            fecha_completado=_ago(days=(25 - i)),
        ))
        nuevos += 1
    db.session.commit()
    print(f"   Sofia: +{nuevos} registros")

    # Diego: 15 citas completadas
    prog_diego = {p.cita_id for p in Progreso.query.filter_by(usuario_id=diego.id, tipo="individual").all()}
    nuevos = 0
    for i, cita in enumerate(citas_db[10:30]):
        if cita.id in prog_diego:
            continue
        db.session.add(Progreso(
            usuario_id=diego.id, cita_id=cita.id, tipo="individual",
            completado=True, calificacion=((i % 5) + 1),
            anecdota=ANECDOTAS[i % len(ANECDOTAS)],
            fecha_completado=_ago(days=(20 - i)),
        ))
        nuevos += 1
    db.session.commit()
    print(f"   Diego: +{nuevos} registros")

    # Valentina: 12 citas completadas
    prog_valentina = {p.cita_id for p in Progreso.query.filter_by(usuario_id=valentina.id, tipo="individual").all()}
    nuevos = 0
    for i, cita in enumerate(citas_db[15:30]):
        if cita.id in prog_valentina:
            continue
        db.session.add(Progreso(
            usuario_id=valentina.id, cita_id=cita.id, tipo="individual",
            completado=True, calificacion=((i % 5) + 1),
            anecdota=ANECDOTAS[i % len(ANECDOTAS)],
            fecha_completado=_ago(days=(15 - i)),
        ))
        nuevos += 1
    db.session.commit()
    print(f"   Valentina: +{nuevos} registros")

    # ── 2. PROGRESO GRUPAL — para todos los grupos de pareja ──────────────────
    print("\n[2] Progreso grupal...")
    grupos_pareja = Grupo.query.filter_by(tipo="pareja", activo=True).all()
    total_grupal = 0
    for idx, grupo in enumerate(grupos_pareja):
        citas_para_grupo = citas_db[40 + idx*12 : 40 + idx*12 + 12]
        for j, cita in enumerate(citas_para_grupo):
            existe = Progreso.query.filter_by(grupo_id=grupo.id, cita_id=cita.id).first()
            if not existe:
                db.session.add(Progreso(
                    grupo_id=grupo.id, cita_id=cita.id, tipo="grupal",
                    completado=True, calificacion=((j % 5) + 1),
                    anecdota=ANECDOTAS[j % len(ANECDOTAS)],
                    fecha_completado=_ago(days=(12 - j) * 4),
                ))
                total_grupal += 1
    db.session.commit()
    print(f"   +{total_grupal} registros grupales")

    # ── 3. MENSAJES — en todos los grupos ─────────────────────────────────────
    print("\n[3] Mensajes en grupos...")
    grupos_todos = Grupo.query.filter_by(activo=True).all()
    total_msg = 0

    MENSAJES_DATA = [
        (carlos,    "Hola a todos! Listos para la proxima cita?"),
        (sofia,     "Yo ya tengo ganas, que emocion!"),
        (diego,     "Cuenta conmigo, esta semana libre tengo"),
        (valentina, "Perfecto, coordinen el lugar y hora"),
        (carlos,    "Propongo el teleférico nocturno este viernes"),
        (sofia,     "Me parece genial! Ya fui una vez y es hermoso"),
        (diego,     "Estan de acuerdo con el viernes a las 7pm?"),
        (valentina, "Si, perfecto para mi"),
        (carlos,    "Listo entonces, nos vemos el viernes!"),
        (sofia,     "Alguien recuerda el codigo del grupo para invitar a mas?"),
    ]

    for grupo in grupos_todos:
        miembros_ids = {m.usuario_id for m in GrupoMiembro.query.filter_by(grupo_id=grupo.id).all()}
        msg_existentes = Mensaje.query.filter_by(grupo_id=grupo.id).count()
        if msg_existentes >= 5:
            continue
        count = 0
        for i, (autor, texto) in enumerate(MENSAJES_DATA):
            if not autor or autor.id not in miembros_ids:
                continue
            db.session.add(Mensaje(
                grupo_id=grupo.id,
                de_usuario_id=autor.id,
                mensaje=texto,
                fecha=_ago(hours=(len(MENSAJES_DATA) - i) * 2),
            ))
            count += 1
            total_msg += 1
            if count >= 6:
                break
    db.session.commit()
    print(f"   +{total_msg} mensajes en {len(grupos_todos)} grupos")

    # ── 4. PAGOS ADICIONALES ──────────────────────────────────────────────────
    print("\n[4] Pagos adicionales...")
    plan_pareja      = PlanSuscripcion.query.filter_by(codigo="pareja").first()
    plan_aventureros = PlanSuscripcion.query.filter_by(codigo="aventureros").first()
    plan_free        = PlanSuscripcion.query.filter_by(codigo="free").first()

    pagos_nuevos = 0
    pagos_a_agregar = []

    # Carlos — pago aprobado plan aventureros
    if carlos and plan_aventureros and admin_u:
        pagos_a_agregar.append(Pago(
            usuario_id=carlos.id, plan_id=plan_aventureros.id,
            monto=Decimal("59.00"), metodo_pago="qr",
            tipo_periodo="mensual", estado="aprobado",
            fecha_pago=_ago(days=45), fecha_aprobacion=_ago(days=44),
            aprobado_por=admin_u.id,
        ))
    # Sofia — pago pendiente plan pareja
    if sofia and plan_pareja:
        pagos_a_agregar.append(Pago(
            usuario_id=sofia.id, plan_id=plan_pareja.id,
            monto=Decimal("29.00"), metodo_pago="efectivo",
            tipo_periodo="mensual", estado="pendiente",
            fecha_pago=_ago(hours=6),
        ))
    # Diego — pago aprobado plan pareja
    if diego and plan_pareja and admin_u:
        pagos_a_agregar.append(Pago(
            usuario_id=diego.id, plan_id=plan_pareja.id,
            monto=Decimal("290.00"), metodo_pago="transferencia",
            tipo_periodo="anual", estado="aprobado",
            fecha_pago=_ago(days=60), fecha_aprobacion=_ago(days=59),
            aprobado_por=admin_u.id,
        ))
    # Valentina — pago rechazado
    if valentina and plan_aventureros and admin_u:
        pagos_a_agregar.append(Pago(
            usuario_id=valentina.id, plan_id=plan_aventureros.id,
            monto=Decimal("590.00"), metodo_pago="qr",
            tipo_periodo="anual", estado="rechazado",
            fecha_pago=_ago(days=10), fecha_aprobacion=_ago(days=9),
            aprobado_por=admin_u.id,
        ))
    # Carlos — segundo pago pendiente
    if carlos and plan_pareja:
        pagos_a_agregar.append(Pago(
            usuario_id=carlos.id, plan_id=plan_pareja.id,
            monto=Decimal("29.00"), metodo_pago="transferencia",
            tipo_periodo="mensual", estado="pendiente",
            fecha_pago=_ago(hours=2),
        ))

    for p in pagos_a_agregar:
        db.session.add(p)
        pagos_nuevos += 1
    db.session.commit()
    print(f"   +{pagos_nuevos} pagos nuevos")

    # ── 5. SUSCRIPCIONES ADICIONALES ──────────────────────────────────────────
    print("\n[5] Suscripciones adicionales...")
    subs_nuevas = 0
    for u, plan, dias_inicio, dias_exp, periodo in [
        (carlos,    plan_aventureros, 45, -25, "mensual"),
        (sofia,     plan_pareja,      20,  10, "mensual"),
        (valentina, plan_pareja,      90, 275, "anual"),
    ]:
        if not u or not plan:
            continue
        existe = Suscripcion.query.filter_by(usuario_id=u.id, plan_id=plan.id, activo=True).first()
        if existe:
            continue
        db.session.add(Suscripcion(
            usuario_id=u.id, plan_id=plan.id,
            fecha_inicio=date.today() - timedelta(days=dias_inicio),
            fecha_expiracion=date.today() + timedelta(days=dias_exp),
            activo=True, tipo_periodo=periodo,
        ))
        subs_nuevas += 1
    db.session.commit()
    print(f"   +{subs_nuevas} suscripciones")

    # ── 6. FOTOS DE CITA ──────────────────────────────────────────────────────
    print("\n[6] Fotos de cita (portadas)...")
    FOTOS_URLS = [
        "/uploads/citas/cafe_prado.jpg",
        "/uploads/citas/killi_killi.jpg",
        "/uploads/citas/tiwanaku.jpg",
        "/uploads/citas/teleferico.jpg",
        "/uploads/citas/valle_luna.jpg",
        "/uploads/citas/spa_andes.jpg",
        "/uploads/citas/galeria_arte.jpg",
        "/uploads/citas/paintball.jpg",
    ]
    citas_con_foto = citas_db[:8]
    fotos_nuevas = 0
    grupo_carlos = Grupo.query.filter_by(tipo="pareja", activo=True).join(GrupoMiembro).filter(
        GrupoMiembro.usuario_id == carlos.id
    ).first()

    for i, cita in enumerate(citas_con_foto):
        existe = FotoCita.query.filter_by(cita_id=cita.id, usuario_id=carlos.id).first()
        if existe:
            continue
        db.session.add(FotoCita(
            cita_id=cita.id,
            grupo_id=grupo_carlos.id if grupo_carlos else None,
            usuario_id=carlos.id,
            url=FOTOS_URLS[i % len(FOTOS_URLS)],
            descripcion="Foto de la cita",
            fecha_subida=_ago(days=i * 3),
        ))
        fotos_nuevas += 1
    db.session.commit()
    print(f"   +{fotos_nuevas} fotos de cita")

    # ── 7. NEGOCIOS ───────────────────────────────────────────────────────────
    print("\n[7] Negocios...")
    departs = {d.nombre: d for d in Departamento.query.all()}
    dep_lp  = departs.get("La Paz")

    NEGOCIOS_DATA = [
        ("Café del Prado",        "Av. 16 de Julio 1490, La Paz",   "restaurante",  -16.4955, -68.1336),
        ("Teleférico La Paz",     "Estación Central, La Paz",        "aventura",     -16.5000, -68.1193),
        ("Valle de la Luna",      "Muela del Diablo, La Paz",        "naturaleza",   -16.5762, -68.0762),
        ("Spa Andes Relax",       "Calle Loayza 233, La Paz",        "bienestar",    -16.4955, -68.1336),
        ("Galería de Arte TAM",   "Calle Sagárnaga 78, La Paz",      "cultura",      -16.4960, -68.1350),
        ("Paintball La Paz",      "Av. Hernando Siles, La Paz",      "aventura",     -16.5100, -68.1100),
        ("Killi Killi Mirador",   "Mirador Killi Killi, La Paz",     "naturaleza",   -16.4890, -68.1270),
        ("Restaurant Gustu",      "Calle 10 de Calacoto 300",        "restaurante",  -16.5310, -68.0760),
        ("Kuska Spa",             "Av. Sánchez Lima 2234, La Paz",   "bienestar",    -16.5020, -68.1180),
        ("Tiwanaku Ruins Tour",   "Tiwanaku, 70km de La Paz",        "cultura",      -16.5554, -68.6736),
        ("Mercado de Brujas",     "Calle Linares, La Paz",           "cultura",      -16.4955, -68.1380),
        ("Cine Center La Paz",    "Av. Arce 2799, La Paz",           "entretenimiento", -16.5072, -68.1172),
    ]

    admin_u2 = User.query.filter_by(email="admin@citas.bo").first()
    negocios_existentes = {n.nombre for n in Negocio.query.all()}
    negocios_nuevos = 0
    negocios_creados = []

    for nombre, direccion, cat, lat, lng in NEGOCIOS_DATA:
        if nombre in negocios_existentes:
            continue
        n = Negocio(
            nombre=nombre, direccion=direccion,
            categoria_negocio=cat, latitud=lat, longitud=lng,
            departamento_id=dep_lp.id if dep_lp else None,
            activo=True, admin_id=admin_u2.id if admin_u2 else None,
        )
        db.session.add(n)
        negocios_creados.append((nombre, n))
        negocios_nuevos += 1

    db.session.flush()

    for nombre, n in negocios_creados:
        db.session.add(FotoNegocio(
            negocio_id=n.id,
            url=f"/uploads/negocios/{nombre.lower().replace(' ', '_')}.jpg",
            descripcion=f"Foto principal de {nombre}",
        ))

    db.session.commit()
    print(f"   +{negocios_nuevos} negocios creados")

    # Vincular algunos negocios a citas
    citas_db2 = Cita.query.filter(Cita.negocio_id.is_(None)).limit(12).all()
    negocios_db = Negocio.query.filter_by(activo=True).all()
    citas_actualizadas = 0
    for i, cita in enumerate(citas_db2):
        cita.negocio_id = negocios_db[i % len(negocios_db)].id
        citas_actualizadas += 1
    db.session.commit()
    print(f"   {citas_actualizadas} citas vinculadas a negocios")

    # ── 8. CERTIFICADOS ───────────────────────────────────────────────────────
    print("\n[8] Certificados...")
    cert_nuevos = 0
    grupos_db = Grupo.query.filter_by(tipo="pareja", activo=True).all()
    niveles = ["bronce", "plata", "oro"]

    for i, grupo in enumerate(grupos_db):
        for j, nivel in enumerate(niveles[:2]):
            existe = Certificado.query.filter_by(grupo_id=grupo.id, nivel=nivel).first()
            if not existe:
                db.session.add(Certificado(
                    grupo_id=grupo.id,
                    nivel=nivel,
                    fecha=_ago(days=(60 - i * 10 - j * 15)),
                    pdf_url=f"/certificados/grupo_{grupo.id}_{nivel}.pdf",
                ))
                cert_nuevos += 1

    if carlos:
        for nivel in ["bronce"]:
            existe = Certificado.query.filter_by(usuario_id=carlos.id, nivel=nivel).first()
            if not existe:
                db.session.add(Certificado(
                    usuario_id=carlos.id,
                    nivel=nivel,
                    fecha=_ago(days=45),
                    pdf_url=f"/certificados/usuario_{carlos.id}_{nivel}.pdf",
                ))
                cert_nuevos += 1

    db.session.commit()
    print(f"   +{cert_nuevos} certificados creados")

    # ── 9. CITAS — verificar que admin/citas las vea todas ────────────────────
    print("\n[9] Verificando citas para admin/citas...")
    total_citas = Cita.query.count()
    activas     = Cita.query.filter_by(activo=True).count()
    con_negocio = Cita.query.filter(Cita.negocio_id.isnot(None)).count()
    print(f"   Total: {total_citas}, activas: {activas}, con negocio: {con_negocio}")

    # ── RESUMEN FINAL ─────────────────────────────────────────────────────────
    print()
    print("=" * 50)
    print("RESUMEN FINAL BD")
    print("=" * 50)
    print(f"  Usuarios:      {User.query.count()}")
    print(f"  Citas:         {Cita.query.count()} activas")
    print(f"  Negocios:      {Negocio.query.count()} ({Negocio.query.filter_by(activo=True).count()} activos)")
    print(f"  Grupos:        {Grupo.query.count()} ({Grupo.query.filter_by(tipo='pareja').count()} parejas, {Grupo.query.filter_by(tipo='amigos').count()} amigos, {Grupo.query.filter_by(tipo='familia').count()} familia)")
    tot_prog = Progreso.query.count()
    ind_prog = Progreso.query.filter_by(tipo="individual").count()
    grp_prog = Progreso.query.filter_by(tipo="grupal").count()
    print(f"  Progreso:      {tot_prog} ({ind_prog} individual, {grp_prog} grupal)")
    tot_pag  = Pago.query.count()
    pend_pag = Pago.query.filter_by(estado="pendiente").count()
    apro_pag = Pago.query.filter_by(estado="aprobado").count()
    rech_pag = Pago.query.filter_by(estado="rechazado").count()
    print(f"  Pagos:         {tot_pag} ({pend_pag} pendientes, {apro_pag} aprobados, {rech_pag} rechazados)")
    print(f"  Suscripciones: {Suscripcion.query.count()}")
    print(f"  Mensajes:      {Mensaje.query.count()}")
    print(f"  FotosCita:     {FotoCita.query.count()}")
    print(f"  Certificados:  {Certificado.query.count()}")
    print()
    print("Modulos listos:")
    print("  /dashboard      -> graficas con datos reales")
    print("  /catalogo       -> 100 citas")
    print("  /recuerdos      -> 60+ recuerdos con anecdotas")
    print("  /grupos         -> grupos con miembros y mensajes")
    print("  /parejas        -> 2 parejas vinculadas")
    print("  /mensajes       -> mensajes entre usuarios")
    print("  /suscripciones  -> pagos y planes activos")
    print("  /certificados   -> certificados por nivel")
    print("  /admin/citas    -> 100 citas gestionables")
    print("  /admin/negocios -> 12 negocios con fotos")
    print("  /admin/pagos    -> pagos (pendientes/aprobados/rechazados)")
    print("  /users/list     -> usuarios")
