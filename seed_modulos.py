"""
Seeder de datos para los modulos pendientes:
  - Negocios (con aprobados y pendientes)
  - Citas actualizadas con negocio_id y portada_url
  - Grupos adicionales (trio de amigos)
  - Pagos pendientes y aprobados
  - Progreso grupal

Ejecutar: python seed_modulos.py
"""

from app import create_app
from app.extensions import bcrypt, db
from app.models import (
    User, Negocio, Cita, Departamento, Categoria,
    Grupo, GrupoMiembro, Pago, PlanSuscripcion,
    Progreso, Suscripcion, FotoCita,
)
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

app = create_app()

def _now():
    return datetime.now(timezone.utc)

def _ago(days=0, hours=0):
    return _now() - timedelta(days=days, hours=hours)

NEGOCIOS = [
    # (nombre, direccion, telefono, categoria_negocio, depto_nombre, activo)
    ("Café del Prado",          "Av. El Prado 1045, La Paz",           "72345678", "Cafetería",      "Sopocachi",                True),
    ("Restaurante El Arriero",  "C. Linares 862, Centro",              "72456789", "Restaurante",    "La Paz Centro",            True),
    ("Mirador Killi Killi Bar", "Mirador Killi Killi s/n, Villa Pabón","79012345", "Bar / Mirador",  "La Paz Centro",            True),
    ("Spa Andes Wellness",      "Av. Arce 2235, Sopocachi",            "72567890", "Spa",            "Sopocachi",                True),
    ("Galería Mamani Arte",     "C. Sagárnaga 321, Centro",            "71234567", "Galería de Arte","La Paz Centro",            True),
    ("Teleférico Tours",        "Estación Central, La Paz",            "22340000", "Turismo",        "La Paz Centro",            True),
    ("Valle de la Luna Lodge",  "Valle de la Luna s/n, Mallasa",       "72678901", "Ecolodge",       "Valle de la Luna / Mallasa",True),
    ("Tiwanaku Experience",     "Ruinas Tiwanaku, Provincia Ingavi",   "72789012", "Turismo",        "Excursiones (Tiwanaku, Urmiri)", True),
    ("Chichería Don Rufino",    "C. Illampu 543, San Pedro",           "73890123", "Chichería",      "La Paz Centro",            True),
    ("Paintball La Paz",        "Av. Periférica 1200, El Alto",        "71901234", "Entretenimiento","El Alto",                  True),
    # Pendientes de aprobación (activo=False)
    ("Karaoke Corazón",         "Av. 6 de Agosto 2100, Sopocachi",     "79111222", "Entretenimiento","Sopocachi",                False),
    ("Masajes Suma Qamaña",     "C. Bueno 234, Miraflores",            "79222333", "Spa",            "Miraflores",               False),
]

GRUPOS_EXTRA = [
    # (nombre, tipo, codigo, emails_miembros)
    ("Aventureros La Paz",  "amigos",  "AVENLPZ1", ["carlos@citas.bo", "diego@citas.bo"]),
    ("Trío Romántico",      "amigos",  "TIORMT2",  ["sofia@citas.bo",  "valentina@citas.bo"]),
]


with app.app_context():
    deptos = {d.nombre: d for d in Departamento.query.all()}
    cats   = {c.nombre: c for c in Categoria.query.all()}
    users  = {u.email: u for u in User.query.all()}

    carlos    = users.get("carlos@citas.bo")
    sofia     = users.get("sofia@citas.bo")
    diego     = users.get("diego@citas.bo")
    valentina = users.get("valentina@citas.bo")
    admin_u   = users.get("admin@citas.bo")

    if Negocio.query.count() == 0:
        negocios_creados = []
        for nombre, direccion, telefono, cat_neg, depto_nombre, activo in NEGOCIOS:
            depto = deptos.get(depto_nombre)
            n = Negocio(
                nombre=nombre,
                direccion=direccion,
                telefono=telefono,
                categoria_negocio=cat_neg,
                departamento_id=depto.id if depto else None,
                activo=activo,
                fecha_registro=_now(),
            )
            db.session.add(n)
            negocios_creados.append(n)
        db.session.commit()
        print(f"[OK] {len(negocios_creados)} negocios creados ({sum(1 for _,_,_,_,_,a in NEGOCIOS if not a)} pendientes)")
    else:
        print(f"[-] Negocios ya existen ({Negocio.query.count()})")

    negocios_db = {n.nombre: n for n in Negocio.query.all()}

    mapeo_cita_negocio = {
        "Salteñas de madrugada":          "Restaurante El Arriero",
        "Ruta de api con pastel":          "Chichería Don Rufino",
        "Café de altura en Sopocachi":     "Café del Prado",
        "Cena romántica paceña":           "Restaurante El Arriero",
        "Amanecer en Killi Killi":         "Mirador Killi Killi Bar",
        "Valle de la Luna al atardecer":   "Valle de la Luna Lodge",
        "Teleférico nocturno":             "Teleférico Tours",
        "Todas las líneas del teleférico": "Teleférico Tours",
        "Tiwanaku de día completo":        "Tiwanaku Experience",
        "Día de spa en pareja":            "Spa Andes Wellness",
        "Clase de yoga para parejas":      "Spa Andes Wellness",
        "Galería de arte en Sopocachi":    "Galería Mamani Arte",
        "Paintball en La Paz":             "Paintball La Paz",
        "Bar de cócteles artesanales":     "Mirador Killi Killi Bar",
    }
    actualizadas = 0
    for nombre_cita, nombre_negocio in mapeo_cita_negocio.items():
        negocio = negocios_db.get(nombre_negocio)
        if not negocio:
            continue
        cita = Cita.query.filter(Cita.nombre.ilike(f"%{nombre_cita[:20]}%")).first()
        if cita and cita.negocio_id is None:
            cita.negocio_id = negocio.id
            actualizadas += 1
    db.session.commit()
    print(f"[OK] {actualizadas} citas vinculadas a negocios")

    grupos_creados = 0
    for nombre, tipo, codigo, emails in GRUPOS_EXTRA:
        if Grupo.query.filter_by(codigo_invitacion=codigo).first():
            continue
        primer_user = users.get(emails[0])
        if not primer_user:
            continue
        g = Grupo(
            nombre=nombre, tipo=tipo,
            codigo_invitacion=codigo,
            creado_por=primer_user.id,
            activo=True, fecha_creacion=_now(),
        )
        db.session.add(g)
        db.session.flush()
        for i, email in enumerate(emails):
            u = users.get(email)
            if u:
                db.session.add(GrupoMiembro(
                    grupo_id=g.id, usuario_id=u.id, es_admin=(i == 0)
                ))
        grupos_creados += 1
    db.session.commit()
    print(f"[OK] {grupos_creados} grupos adicionales creados")

    if Pago.query.count() == 0:
        plan_pareja     = PlanSuscripcion.query.filter_by(codigo="pareja").first()
        plan_aventureros = PlanSuscripcion.query.filter_by(codigo="aventureros").first()
        plan_free       = PlanSuscripcion.query.filter_by(codigo="free").first()

        pagos_data = []

        if diego and plan_pareja and admin_u:
            p = Pago(
                usuario_id=diego.id,
                plan_id=plan_pareja.id,
                monto=Decimal("29.00"),
                metodo_pago="transferencia",
                tipo_periodo="mensual",
                estado="aprobado",
                fecha_pago=_ago(days=15),
                fecha_aprobacion=_ago(days=14),
                aprobado_por=admin_u.id,
            )
            db.session.add(p)
            pagos_data.append(p)

        if sofia and plan_aventureros and admin_u:
            p = Pago(
                usuario_id=sofia.id,
                plan_id=plan_aventureros.id,
                monto=Decimal("590.00"),
                metodo_pago="qr",
                tipo_periodo="anual",
                estado="aprobado",
                fecha_pago=_ago(days=30),
                fecha_aprobacion=_ago(days=29),
                aprobado_por=admin_u.id,
            )
            db.session.add(p)
            pagos_data.append(p)

        # Valentina: pago PENDIENTE (plan pareja mensual) — aparece en admin/pagos
        if valentina and plan_pareja:
            p = Pago(
                usuario_id=valentina.id,
                plan_id=plan_pareja.id,
                monto=Decimal("29.00"),
                metodo_pago="transferencia",
                tipo_periodo="mensual",
                estado="pendiente",
                fecha_pago=_ago(hours=3),
            )
            db.session.add(p)
            pagos_data.append(p)

        # Diego segundo pago: PENDIENTE (plan aventureros)
        if diego and plan_aventureros:
            p = Pago(
                usuario_id=diego.id,
                plan_id=plan_aventureros.id,
                monto=Decimal("59.00"),
                metodo_pago="efectivo",
                tipo_periodo="mensual",
                estado="pendiente",
                fecha_pago=_ago(hours=1),
            )
            db.session.add(p)
            pagos_data.append(p)

        db.session.commit()
        print(f"[OK] {len(pagos_data)} pagos creados ({sum(1 for p in pagos_data if p.estado=='pendiente')} pendientes)")
    else:
        print(f"[-] Pagos ya existen ({Pago.query.count()})")

    # ── 5. SUSCRIPCIONES para Diego y Sofía ───────────────────────────────────
    if Suscripcion.query.count() <= 1:
        plan_pareja      = PlanSuscripcion.query.filter_by(codigo="pareja").first()
        plan_aventureros = PlanSuscripcion.query.filter_by(codigo="aventureros").first()

        subs = []
        if diego and plan_pareja:
            subs.append(Suscripcion(
                usuario_id=diego.id, plan_id=plan_pareja.id,
                fecha_inicio=date.today() - timedelta(days=15),
                fecha_expiracion=date.today() + timedelta(days=15),
                activo=True, tipo_periodo="mensual",
            ))
        if sofia and plan_aventureros:
            subs.append(Suscripcion(
                usuario_id=sofia.id, plan_id=plan_aventureros.id,
                fecha_inicio=date.today() - timedelta(days=30),
                fecha_expiracion=date.today() + timedelta(days=335),
                activo=True, tipo_periodo="anual",
            ))
        db.session.add_all(subs)
        db.session.commit()
        print(f"[OK] {len(subs)} suscripciones adicionales creadas")
    else:
        print(f"[-] Suscripciones ya existen ({Suscripcion.query.count()})")

    # ── 6. PROGRESO GRUPAL para los grupos de pareja ──────────────────────────
    grupos_pareja = Grupo.query.filter_by(tipo="pareja", activo=True).all()
    citas_db = Cita.query.order_by(Cita.id).all()

    ANECDOTAS = [
        "Una noche magica que nunca olvidaremos en La Paz.",
        "Nos reimos tanto que no podiamos caminar de regreso.",
        "El frio paceño no pudo con nosotros, llegamos abrazados.",
        "Descubrimos un lugar nuevo de nuestra ciudad juntos.",
        "Prometimos volver a hacer esto cada año, nuestra tradicion.",
        "Aprendimos algo nuevo el uno del otro en esta aventura.",
        "La ciudad nos regalo una vista que no esperabamos.",
        "Fue mas dificil de lo pensado, pero lo logramos juntos.",
    ]

    progreso_grupal_creado = 0
    for i, grupo in enumerate(grupos_pareja):
        citas_para_grupo = citas_db[10 + i*5 : 10 + i*5 + 8]
        for j, cita in enumerate(citas_para_grupo):
            existe = Progreso.query.filter_by(
                grupo_id=grupo.id, cita_id=cita.id
            ).first()
            if not existe:
                dias = (8 - j) * 5
                db.session.add(Progreso(
                    grupo_id=grupo.id,
                    cita_id=cita.id,
                    tipo="grupal",
                    completado=True,
                    calificacion=((j % 5) + 1),
                    anecdota=ANECDOTAS[j % len(ANECDOTAS)],
                    fecha_completado=_ago(days=dias),
                ))
                progreso_grupal_creado += 1

    db.session.commit()
    print(f"[OK] {progreso_grupal_creado} registros de progreso grupal creados")

    # ── 7. RESUMEN FINAL ──────────────────────────────────────────────────────
    print()
    print("=== RESUMEN BD ===")
    print(f"  Negocios:      {Negocio.query.count()} ({Negocio.query.filter_by(activo=True).count()} activos, {Negocio.query.filter_by(activo=False).count()} pendientes)")
    print(f"  Grupos:        {Grupo.query.count()} ({Grupo.query.filter_by(tipo='pareja').count()} parejas, {Grupo.query.filter_by(tipo='amigos').count()} amigos)")
    print(f"  Pagos:         {Pago.query.count()} ({Pago.query.filter_by(estado='pendiente').count()} pendientes, {Pago.query.filter_by(estado='aprobado').count()} aprobados)")
    print(f"  Progreso:      {Progreso.query.count()} ({Progreso.query.filter_by(tipo='individual').count()} individual, {Progreso.query.filter_by(tipo='grupal').count()} grupal)")
    print(f"  Suscripciones: {Suscripcion.query.count()} activas")
    print(f"  Citas con negocio: {Cita.query.filter(Cita.negocio_id != None).count()}")
    print()
    print("Modulos listos para probar:")
    print("  /grupos        -> 4 grupos (2 parejas + 2 de amigos)")
    print("  /parejas       -> Carlos&Sofia, Diego&Valentina vinculados")
    print("  /recuerdos     -> 27+ recuerdos (individual y grupal)")
    print("  /admin/negocios -> 10 negocios activos + 2 pendientes")
    print("  /admin/citas    -> 100 citas, 14 vinculadas a negocios")
    print("  /admin/pagos    -> 2 pagos pendientes (Valentina, Diego)")
