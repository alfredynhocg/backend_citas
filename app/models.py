from datetime import datetime, timezone
from .extensions import db
from flask_login import UserMixin

def _now():
    return datetime.now(timezone.utc)

class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=True)
class User(UserMixin,db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=True)
    rol_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=True, default=2)
    departamento_actual = db.Column(db.String(50), nullable=True)
    fecha_registro = db.Column(db.DateTime, default=_now, nullable=True)
    activo = db.Column(db.Boolean, default=True, nullable=True)

    @property
    def is_active(self):
        return self.activo
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)

    rol = db.relationship("Role", backref="usuarios")
    grupos_miembro = db.relationship("GrupoMiembro", back_populates="usuario", lazy="dynamic")
    grupos_creados = db.relationship("Grupo", back_populates="creador")
    pagos_realizados = db.relationship("Pago", foreign_keys="Pago.usuario_id", back_populates="usuario")
    pagos_aprobados = db.relationship("Pago", foreign_keys="Pago.aprobado_por", back_populates="aprobador")
    suscripciones = db.relationship("Suscripcion", foreign_keys="Suscripcion.usuario_id", back_populates="usuario")
    fotos_citas = db.relationship("FotoCita", back_populates="usuario")
    progresos_individuales = db.relationship("Progreso", foreign_keys="Progreso.usuario_id", back_populates="usuario")
    certificados_usuario = db.relationship("Certificado", foreign_keys="Certificado.usuario_id", back_populates="usuario")
    mensajes_enviados = db.relationship("Mensaje", foreign_keys="Mensaje.de_usuario_id", back_populates="emisor")
    mensajes_recibidos = db.relationship("Mensaje", foreign_keys="Mensaje.para_usuario_id", back_populates="receptor")
def crear_roles_por_defecto():
    from .extensions import db
    from sqlalchemy import func
    # Verificar si existe rol con id=1
    admin = Role.query.get(1)
    normal = Role.query.get(2)
    if not admin:
        admin = Role(id=1, nombre='administrador')
        db.session.add(admin)
    if not normal:
        normal = Role(id=2, nombre='usuario_normal')
        db.session.add(normal)
    db.session.commit()
    
class Grupo(db.Model):
    __tablename__ = "grupos"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=True)
    tipo = db.Column(db.String(30), nullable=True)
    codigo_invitacion = db.Column(db.String(10), unique=True, nullable=True)
    creado_por = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=_now, nullable=True)
    activo = db.Column(db.Boolean, default=True, nullable=True)

    creador = db.relationship("User", back_populates="grupos_creados")
    miembros = db.relationship("GrupoMiembro", back_populates="grupo", lazy="dynamic")
    pagos_grupo = db.relationship("Pago", back_populates="grupo")
    suscripciones_grupo = db.relationship("Suscripcion", foreign_keys="Suscripcion.grupo_id", back_populates="grupo")
    fotos_citas_grupo = db.relationship("FotoCita", back_populates="grupo")
    progresos_grupo = db.relationship("Progreso", foreign_keys="Progreso.grupo_id", back_populates="grupo")
    certificados_grupo = db.relationship("Certificado", foreign_keys="Certificado.grupo_id", back_populates="grupo")
    mensajes_grupo = db.relationship("Mensaje", back_populates="grupo")

class GrupoMiembro(db.Model):
    __tablename__ = "grupo_miembros"

    id = db.Column(db.Integer, primary_key=True)
    grupo_id = db.Column(db.Integer, db.ForeignKey("grupos.id", ondelete="CASCADE"), nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=True)
    es_admin = db.Column(db.Boolean, default=False, nullable=True)
    fecha_union = db.Column(db.DateTime, default=_now, nullable=True)

    grupo = db.relationship("Grupo", back_populates="miembros")
    usuario = db.relationship("User", back_populates="grupos_miembro")

class PlanSuscripcion(db.Model):
    __tablename__ = "planes_suscripcion"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=True)
    codigo = db.Column(db.String(20), unique=True, nullable=True)
    descripcion = db.Column(db.Text, nullable=True)
    precio_mensual = db.Column(db.Numeric(10,2), nullable=True)
    precio_anual = db.Column(db.Numeric(10,2), nullable=True)
    max_integrantes = db.Column(db.Integer, nullable=True)
    permite_grupo = db.Column(db.Boolean, default=False, nullable=True)
    permite_individual = db.Column(db.Boolean, default=False, nullable=True)
    departamentos_desbloquea = db.Column(db.Integer, nullable=True)
    ventajas = db.Column(db.Text, nullable=True)
    activo = db.Column(db.Boolean, default=True, nullable=True)

    pagos = db.relationship("Pago", back_populates="plan")
    suscripciones = db.relationship("Suscripcion", back_populates="plan")

class Pago(db.Model):
    __tablename__ = "pagos"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)
    grupo_id = db.Column(db.Integer, db.ForeignKey("grupos.id"), nullable=True)
    plan_id = db.Column(db.Integer, db.ForeignKey("planes_suscripcion.id"), nullable=True)
    monto = db.Column(db.Numeric(10,2), nullable=True)
    metodo_pago = db.Column(db.String(30), nullable=True)
    comprobante_url = db.Column(db.String(300), nullable=True)
    tipo_periodo = db.Column(db.String(20), nullable=True)
    estado = db.Column(db.String(20), default="pendiente", nullable=True)
    fecha_pago = db.Column(db.DateTime, default=_now, nullable=True)
    fecha_aprobacion = db.Column(db.DateTime, nullable=True)
    aprobado_por = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)

    usuario = db.relationship("User", foreign_keys=[usuario_id], back_populates="pagos_realizados")
    grupo = db.relationship("Grupo", back_populates="pagos_grupo")
    plan = db.relationship("PlanSuscripcion", back_populates="pagos")
    aprobador = db.relationship("User", foreign_keys=[aprobado_por], back_populates="pagos_aprobados")
    suscripciones = db.relationship("Suscripcion", back_populates="pago")

class Suscripcion(db.Model):
    __tablename__ = "suscripciones"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)
    grupo_id = db.Column(db.Integer, db.ForeignKey("grupos.id"), nullable=True)
    plan_id = db.Column(db.Integer, db.ForeignKey("planes_suscripcion.id"), nullable=True)
    pago_id = db.Column(db.Integer, db.ForeignKey("pagos.id"), nullable=True)
    fecha_inicio = db.Column(db.Date, nullable=True)
    fecha_expiracion = db.Column(db.Date, nullable=True)
    activo = db.Column(db.Boolean, default=False, nullable=True)
    tipo_periodo = db.Column(db.String(20), nullable=True)

    usuario = db.relationship("User", foreign_keys=[usuario_id], back_populates="suscripciones")
    grupo = db.relationship("Grupo", foreign_keys=[grupo_id], back_populates="suscripciones_grupo")
    plan = db.relationship("PlanSuscripcion", back_populates="suscripciones")
    pago = db.relationship("Pago", back_populates="suscripciones")
    departamentos = db.relationship("SuscripcionDepartamento", back_populates="suscripcion", lazy="dynamic")

class SuscripcionDepartamento(db.Model):
    __tablename__ = "suscripcion_departamentos"

    id = db.Column(db.Integer, primary_key=True)
    suscripcion_id = db.Column(db.Integer, db.ForeignKey("suscripciones.id", ondelete="CASCADE"), nullable=True)
    departamento_id = db.Column(db.Integer, db.ForeignKey("departamentos.id"), nullable=True)

    suscripcion = db.relationship("Suscripcion", back_populates="departamentos")
    departamento = db.relationship("Departamento", back_populates="suscripciones")

class Departamento(db.Model):
    __tablename__ = "departamentos"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=True)
    orden_desbloqueo = db.Column(db.Integer, default=0, nullable=True)

    negocios = db.relationship("Negocio", back_populates="departamento")
    citas = db.relationship("Cita", back_populates="departamento")
    suscripciones = db.relationship("SuscripcionDepartamento", back_populates="departamento")

class Categoria(db.Model):
    __tablename__ = "categorias"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=True)

    citas = db.relationship("Cita", back_populates="categoria")

class Negocio(db.Model):
    __tablename__ = "negocios"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=True)
    direccion = db.Column(db.Text, nullable=True)
    latitud = db.Column(db.Numeric(10,8), nullable=True)
    longitud = db.Column(db.Numeric(11,8), nullable=True)
    departamento_id = db.Column(db.Integer, db.ForeignKey("departamentos.id"), nullable=True)
    telefono = db.Column(db.String(20), nullable=True)
    categoria_negocio = db.Column(db.String(50), nullable=True)
    logo_url = db.Column(db.String(300), nullable=True)
    activo = db.Column(db.Boolean, default=False, nullable=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)
    fecha_registro = db.Column(db.DateTime, default=_now, nullable=True)

    departamento = db.relationship("Departamento", back_populates="negocios")
    admin = db.relationship("User", foreign_keys=[admin_id])
    fotos = db.relationship("FotoNegocio", back_populates="negocio", lazy="dynamic")
    citas = db.relationship("Cita", back_populates="negocio")

class FotoNegocio(db.Model):
    __tablename__ = "fotos_negocios"

    id = db.Column(db.Integer, primary_key=True)
    negocio_id = db.Column(db.Integer, db.ForeignKey("negocios.id", ondelete="CASCADE"), nullable=True)
    url = db.Column(db.String(300), nullable=True)
    descripcion = db.Column(db.Text, nullable=True)
    fecha_subida = db.Column(db.DateTime, default=_now, nullable=True)

    negocio = db.relationship("Negocio", back_populates="fotos")

class Cita(db.Model):
    __tablename__ = "citas"

    id = db.Column(db.Integer, primary_key=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias.id"), nullable=True)
    negocio_id = db.Column(db.Integer, db.ForeignKey("negocios.id"), nullable=True)
    departamento_id = db.Column(db.Integer, db.ForeignKey("departamentos.id"), nullable=True)
    nombre = db.Column(db.String(150), nullable=True)
    descripcion = db.Column(db.Text, nullable=True)
    latitud = db.Column(db.Numeric(10,8), nullable=True)
    longitud = db.Column(db.Numeric(11,8), nullable=True)
    direccion = db.Column(db.Text, nullable=True)
    puntos = db.Column(db.Integer, default=10, nullable=True)
    portada_url = db.Column(db.String(300), nullable=True)
    activo = db.Column(db.Boolean, default=True, nullable=True)

    categoria = db.relationship("Categoria", back_populates="citas")
    negocio = db.relationship("Negocio", back_populates="citas")
    departamento = db.relationship("Departamento", back_populates="citas")
    fotos = db.relationship("FotoCita", back_populates="cita", lazy="dynamic")
    progresos = db.relationship("Progreso", back_populates="cita", lazy="dynamic")

class FotoCita(db.Model):
    __tablename__ = "fotos_citas"

    id = db.Column(db.Integer, primary_key=True)
    cita_id = db.Column(db.Integer, db.ForeignKey("citas.id", ondelete="CASCADE"), nullable=True)
    grupo_id = db.Column(db.Integer, db.ForeignKey("grupos.id", ondelete="CASCADE"), nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=True)
    url = db.Column(db.String(300), nullable=True)
    descripcion = db.Column(db.Text, nullable=True)
    fecha_subida = db.Column(db.DateTime, default=_now, nullable=True)

    cita = db.relationship("Cita", back_populates="fotos")
    grupo = db.relationship("Grupo", back_populates="fotos_citas_grupo")
    usuario = db.relationship("User", back_populates="fotos_citas")

class Progreso(db.Model):
    __tablename__ = "progreso"
    __table_args__ = (
        db.CheckConstraint(
            "(tipo = 'grupal' AND grupo_id IS NOT NULL AND usuario_id IS NULL) OR "
            "(tipo = 'individual' AND usuario_id IS NOT NULL AND grupo_id IS NULL)",
            name="chk_progreso"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20), nullable=True)
    grupo_id = db.Column(db.Integer, db.ForeignKey("grupos.id"), nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)
    cita_id = db.Column(db.Integer, db.ForeignKey("citas.id"), nullable=True)
    completado = db.Column(db.Boolean, default=False, nullable=True)
    calificacion = db.Column(db.Integer, nullable=True)
    anecdota = db.Column(db.Text, nullable=True)
    fecha_completado = db.Column(db.DateTime, nullable=True)

    grupo = db.relationship("Grupo", foreign_keys=[grupo_id], back_populates="progresos_grupo")
    usuario = db.relationship("User", foreign_keys=[usuario_id], back_populates="progresos_individuales")
    cita = db.relationship("Cita", back_populates="progresos")

class Certificado(db.Model):
    __tablename__ = "certificados"

    id = db.Column(db.Integer, primary_key=True)
    grupo_id = db.Column(db.Integer, db.ForeignKey("grupos.id"), nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)
    nivel = db.Column(db.String(30), nullable=True)
    fecha = db.Column(db.DateTime, default=_now, nullable=True)
    pdf_url = db.Column(db.String(300), nullable=True)

    grupo = db.relationship("Grupo", foreign_keys=[grupo_id], back_populates="certificados_grupo")
    usuario = db.relationship("User", foreign_keys=[usuario_id], back_populates="certificados_usuario")

class Mensaje(db.Model):
    __tablename__ = "mensajes"

    id = db.Column(db.Integer, primary_key=True)
    grupo_id = db.Column(db.Integer, db.ForeignKey("grupos.id"), nullable=True)
    de_usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)
    para_usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)
    mensaje = db.Column(db.Text, nullable=True)
    leido = db.Column(db.Boolean, default=False, nullable=True)
    fecha = db.Column(db.DateTime, default=_now, nullable=True)

    grupo = db.relationship("Grupo", back_populates="mensajes_grupo")
    emisor = db.relationship("User", foreign_keys=[de_usuario_id], back_populates="mensajes_enviados")
    receptor = db.relationship("User", foreign_keys=[para_usuario_id], back_populates="mensajes_recibidos")
class ConsultaIA(db.Model):
    __tablename__ = 'consultas_ia'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)  # ← CAMBIADO: 'usuarios.id'
    pregunta = db.Column(db.Text, nullable=False)
    respuesta = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    modelo_usado = db.Column(db.String(100), default='gpt-3.5-turbo')
    tokens_usados = db.Column(db.Integer, default=0)
    
    # Relación con User
    user = db.relationship('User', backref='consultas_ia', lazy=True, foreign_keys=[user_id])
Category = Categoria
Couple = Grupo
CoupleDate = Progreso
Date = Cita
Memory = FotoCita

# ── WhatsApp Bot ──────────────────────────────────────────────────────────────

wa_conv_etiqueta = db.Table(
    'wa_conv_etiqueta',
    db.Column('conversacion_id', db.Integer, db.ForeignKey('wa_conversaciones.id'), primary_key=True),
    db.Column('etiqueta_id',     db.Integer, db.ForeignKey('wa_etiquetas.id'),     primary_key=True),
)

class WaEtiqueta(db.Model):
    __tablename__ = 'wa_etiquetas'
    id     = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(60), nullable=False, unique=True)
    color  = db.Column(db.String(20), nullable=False, default='#6366f1')

class WaConversacion(db.Model):
    __tablename__ = 'wa_conversaciones'
    id         = db.Column(db.Integer, primary_key=True)
    phone      = db.Column(db.String(40), nullable=False, unique=True)
    nombre     = db.Column(db.String(100), nullable=True)
    estado     = db.Column(db.String(40), nullable=False, default='menu')
    updated_at = db.Column(db.DateTime, default=_now, onupdate=_now)
    etiquetas  = db.relationship('WaEtiqueta', secondary=wa_conv_etiqueta, lazy='subquery')