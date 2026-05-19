"""
Seeder de grupos adicionales para probar /grupos.
Agrega grupos de tipo amigos y familia con todos los usuarios seed.

Ejecutar: ./env/Scripts/python seed_grupos.py
"""

from app import create_app
from app.extensions import db
from app.models import User, Grupo, GrupoMiembro
from datetime import datetime, timezone, timedelta

app = create_app()

def _now():
    return datetime.now(timezone.utc)

def _ago(days=0):
    return _now() - timedelta(days=days)

GRUPOS = [
    ("Aventureros La Paz",       "amigos",  "AVENLPZ1", ["carlos@citas.bo",    "diego@citas.bo"]),
    ("Trío Romántico",           "amigos",  "TIORMT22", ["sofia@citas.bo",     "valentina@citas.bo"]),
    ("Squad Paceño",             "amigos",  "SQPACE33", ["carlos@citas.bo",    "sofia@citas.bo",  "diego@citas.bo"]),
    ("Girls Night Out",          "amigos",  "GIRLS444", ["sofia@citas.bo",     "valentina@citas.bo"]),
    ("Bros La Paz",              "amigos",  "BROLPZ55", ["carlos@citas.bo",    "diego@citas.bo"]),
    ("Familia Mamani",           "familia", "FAMAM661", ["carlos@citas.bo",    "sofia@citas.bo",  "diego@citas.bo", "valentina@citas.bo"]),
    ("Familia Quispe",           "familia", "FAQUI772", ["sofia@citas.bo",     "valentina@citas.bo"]),
    ("Viajeros del Altiplano",   "amigos",  "VIALT883", ["diego@citas.bo",     "valentina@citas.bo", "carlos@citas.bo"]),
]

with app.app_context():
    users = {u.email: u for u in User.query.all()}

    carlos    = users.get("carlos@citas.bo")
    sofia     = users.get("sofia@citas.bo")
    diego     = users.get("diego@citas.bo")
    valentina = users.get("valentina@citas.bo")

    if not all([carlos, sofia, diego, valentina]):
        print("[ERROR] Faltan usuarios seed. Ejecuta primero seed_all.py")
        exit(1)

    creados = 0
    for nombre, tipo, codigo, emails in GRUPOS:
        if Grupo.query.filter_by(codigo_invitacion=codigo).first():
            print(f"[-] Grupo '{nombre}' ya existe, saltando...")
            continue

        primer_email = emails[0]
        creador = users.get(primer_email)
        if not creador:
            print(f"[WARN] Usuario {primer_email} no encontrado, saltando grupo '{nombre}'")
            continue

        g = Grupo(
            nombre=nombre,
            tipo=tipo,
            codigo_invitacion=codigo,
            creado_por=creador.id,
            activo=True,
            fecha_creacion=_ago(days=creados * 3 + 1),
        )
        db.session.add(g)
        db.session.flush()

        for i, email in enumerate(emails):
            u = users.get(email)
            if u:
                db.session.add(GrupoMiembro(
                    grupo_id=g.id,
                    usuario_id=u.id,
                    es_admin=(i == 0),
                ))

        creados += 1
        print(f"[OK] Grupo '{nombre}' ({tipo}) creado con {len(emails)} miembros")

    db.session.commit()

    print()
    print("=== RESUMEN GRUPOS ===")
    total = Grupo.query.filter_by(activo=True).count()
    amigos  = Grupo.query.filter_by(tipo='amigos',  activo=True).count()
    familia = Grupo.query.filter_by(tipo='familia', activo=True).count()
    pareja  = Grupo.query.filter_by(tipo='pareja',  activo=True).count()
    print(f"  Total grupos activos: {total}")
    print(f"    Pareja:  {pareja}")
    print(f"    Amigos:  {amigos}")
    print(f"    Familia: {familia}")
    print()
    print("Usuarios y sus grupos:")
    for email in ["carlos@citas.bo", "sofia@citas.bo", "diego@citas.bo", "valentina@citas.bo"]:
        u = users.get(email)
        if u:
            mis_grupos = Grupo.query.join(GrupoMiembro).filter(
                GrupoMiembro.usuario_id == u.id, Grupo.activo == True
            ).all()
            print(f"  {email}: {len(mis_grupos)} grupos ({', '.join(g.nombre for g in mis_grupos)})")
