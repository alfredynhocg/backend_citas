# app/services/usuario_service.py

from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from ..models import User as Usuario, Grupo, GrupoMiembro, Suscripcion, PlanSuscripcion, Pago, Progreso, Certificado, Departamento
from ..extensions import db
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class UsuarioService:

    @staticmethod
    def obtener_todos():
        return Usuario.query.filter_by(activo=True).all()

    @staticmethod
    def obtener_por_id(usuario_id):
        return Usuario.query.get(usuario_id)
    @staticmethod
    def obtener_perfil_completo(usuario_id):
        try:
            usuario = Usuario.query.get(usuario_id)
            if not usuario:
                return {'error': 'Usuario no encontrado'}, 404
            
            # Obtener grupos con manejo de errores
            try:
                grupos = UsuarioService.obtener_grupos(usuario_id)
                grupos_lista = [{
                    'id': g.id, 
                    'nombre': g.nombre or 'Sin nombre', 
                    'tipo': g.tipo or 'desconocido'
                } for g in (grupos or [])]
            except Exception as e:
                grupos_lista = []
            
            # Obtener pareja con manejo de errores
            try:
                pareja = UsuarioService.obtener_pareja(usuario_id)
                pareja_data = {
                    'id': pareja.id,
                    'nombre': pareja.nombre or 'Sin nombre',
                    'email': pareja.email or 'sin@email.com'
                } if pareja else None
            except Exception as e:
                pareja_data = None
            
            return {
                'id': usuario.id,
                'nombre': usuario.nombre or 'Sin nombre',
                'email': usuario.email or 'sin@email.com',
                'departamento_actual': usuario.departamento_actual or 'No especificado',
                'fecha_registro': str(usuario.fecha_registro) if usuario.fecha_registro else None,
                'activo': usuario.activo if usuario.activo is not None else True,
                'tiene_pareja': pareja_data is not None,
                'pareja': pareja_data,
                'grupos': grupos_lista,
                'total_grupos': len(grupos_lista)
            }, 200
            
        except Exception as e:
            return {
                'error': 'Error al obtener perfil',
                'detalle': str(e)
            }, 500
    @staticmethod
    def actualizar(usuario_id, data):
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return None
        if 'nombre' in data:
            usuario.nombre = data['nombre']
        if 'departamento_actual' in data:
            usuario.departamento_actual = data['departamento_actual']
        db.session.commit()
        return usuario

    @staticmethod
    def desactivar(usuario_id):
        usuario = Usuario.query.get(usuario_id)
        if usuario:
            usuario.activo = False
            db.session.commit()
        return True

    @staticmethod
    def cambiar_password(usuario_id, data):
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return False
        if not check_password_hash(usuario.password_hash, data['password_actual']):
            return False
        usuario.password_hash = generate_password_hash(data['password_nuevo'])
        db.session.commit()
        return True

    @staticmethod
    def obtener_grupos(usuario_id):
        return Grupo.query.join(GrupoMiembro).filter(GrupoMiembro.usuario_id == usuario_id, Grupo.activo == True).all()

    @staticmethod
    def obtener_pareja(usuario_id):
        grupos = Grupo.query.join(GrupoMiembro).filter(
            GrupoMiembro.usuario_id == usuario_id,
            Grupo.tipo == 'pareja',
            Grupo.activo == True
        ).all()
        for grupo in grupos:
            miembros = GrupoMiembro.query.filter_by(grupo_id=grupo.id).all()
            for miembro in miembros:
                if miembro.usuario_id != usuario_id:
                    return Usuario.query.get(miembro.usuario_id)
        return None

    @staticmethod
    def obtener_fecha_union(usuario_id, pareja_id):
        grupo = Grupo.query.join(GrupoMiembro).filter(
            Grupo.tipo == 'pareja',
            GrupoMiembro.usuario_id.in_([usuario_id, pareja_id])
        ).first()
        if grupo:
            miembro = GrupoMiembro.query.filter_by(grupo_id=grupo.id, usuario_id=usuario_id).first()
            return miembro.fecha_union if miembro else None
        return None

    @staticmethod
    def crear_invitar_pareja(usuario_id, data):
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        
        # VALIDACIÓN 1: El usuario ya tiene pareja activa?
        pareja_activa = UsuarioService.obtener_pareja(usuario_id)
        if pareja_activa:
            return {'error': 'Ya tienes una pareja activa. Debes desvincularla antes de crear una nueva.'}, 400
        
        # VALIDACIÓN 2: El usuario ya tiene una invitación pendiente?
        grupos_pendientes = Grupo.query.join(GrupoMiembro).filter(
            GrupoMiembro.usuario_id == usuario_id,
            Grupo.tipo == 'pareja',
            Grupo.activo == True
        ).all()
        
        for grupo in grupos_pendientes:
            miembros_count = GrupoMiembro.query.filter_by(grupo_id=grupo.id).count()
            if miembros_count == 1:
                return {'error': 'Ya tienes una invitación de pareja pendiente. Espera que se unan o cancélala.'}, 400
        
        # VALIDACIÓN 3: El email es el mismo que el usuario actual?
        if data['email_pareja'].lower() == usuario.email.lower():
            return {'error': 'No puedes ser pareja de ti mismo'}, 400
        
        pareja_existente = Usuario.query.filter_by(email=data['email_pareja']).first()
        
        # VALIDACIÓN 4: La persona invitada ya tiene pareja?
        if pareja_existente:
            pareja_de_ella = UsuarioService.obtener_pareja(pareja_existente.id)
            if pareja_de_ella:
                return {'error': 'La persona que intentas invitar ya tiene una pareja activa.'}, 400
        
        # VALIDACIÓN 5: Ya existe un grupo de pareja entre estos dos usuarios?
        if pareja_existente:
            grupo_existente = Grupo.query.join(GrupoMiembro).filter(
                Grupo.tipo == 'pareja',
                Grupo.activo == True,
                GrupoMiembro.usuario_id.in_([usuario_id, pareja_existente.id])
            ).group_by(Grupo.id).having(db.func.count(GrupoMiembro.id) == 2).first()
            
            if grupo_existente:
                return {'error': 'Ya existe una pareja entre ustedes dos.'}, 400
        
        codigo = secrets.token_hex(4).upper()
        
        grupo = Grupo(
            nombre=data['nombre_pareja'],
            tipo='pareja',
            codigo_invitacion=codigo,
            creado_por=usuario_id
        )
        db.session.add(grupo)
        db.session.flush()
        
        miembro1 = GrupoMiembro(grupo_id=grupo.id, usuario_id=usuario_id, es_admin=True)
        db.session.add(miembro1)
        
        if pareja_existente:
            miembro2 = GrupoMiembro(grupo_id=grupo.id, usuario_id=pareja_existente.id)
            db.session.add(miembro2)
            db.session.commit()
            return {
                'mensaje': 'Pareja vinculada exitosamente',
                'grupo_id': grupo.id,
                'nombre_pareja': grupo.nombre,
                'miembros': [usuario_id, pareja_existente.id]
            }, 200
        else:
            db.session.commit()
            return {
                'mensaje': 'Invitación enviada. Comparte este código con tu pareja.',
                'codigo': codigo,
                'grupo_id': grupo.id,
                'email_invitado': data['email_pareja']
            }, 201

    @staticmethod
    def unir_pareja(usuario_id, codigo):
        grupo = Grupo.query.filter_by(codigo_invitacion=codigo, tipo='pareja', activo=True).first()
        if not grupo:
            return None
        existe = GrupoMiembro.query.filter_by(grupo_id=grupo.id, usuario_id=usuario_id).first()
        if existe:
            return None
        miembro = GrupoMiembro(grupo_id=grupo.id, usuario_id=usuario_id)
        db.session.add(miembro)
        db.session.commit()
        return grupo

    @staticmethod
    def desvincular_pareja(usuario_id):
        grupos = Grupo.query.join(GrupoMiembro).filter(
            GrupoMiembro.usuario_id == usuario_id,
            Grupo.tipo == 'pareja'
        ).all()
        for grupo in grupos:
            miembros = GrupoMiembro.query.filter_by(grupo_id=grupo.id).all()
            if len(miembros) <= 2:
                for m in miembros:
                    db.session.delete(m)
                db.session.delete(grupo)
        db.session.commit()
        return True

    @staticmethod
    def obtener_suscripciones(usuario_id):
        return Suscripcion.query.filter_by(usuario_id=usuario_id).all()

    @staticmethod
    def obtener_suscripcion_activa(usuario_id):
        return Suscripcion.query.filter(
            Suscripcion.usuario_id == usuario_id,
            Suscripcion.activo == True,
            Suscripcion.fecha_expiracion >= date.today()
        ).first()

    @staticmethod
    def contratar_suscripcion(usuario_id, data):
        plan = PlanSuscripcion.query.get(data['plan_id'])
        if not plan:
            return {'error': 'Plan no encontrado'}, 404
        
        if data['tipo'] == 'individual' and not plan.permite_individual:
            return {'error': 'Este plan no permite suscripcion individual'}, 400
        if data['tipo'] == 'grupal' and not plan.permite_grupo:
            return {'error': 'Este plan no permite suscripcion grupal'}, 400
        
        tipo_periodo = data.get('tipo_periodo', 'mensual')
        precio = plan.precio_mensual if tipo_periodo == 'mensual' else plan.precio_anual
        dias = 30 if tipo_periodo == 'mensual' else 365
        
        suscripcion = Suscripcion(
            usuario_id=usuario_id if data['tipo'] == 'individual' else None,
            grupo_id=data.get('grupo_id') if data['tipo'] == 'grupal' else None,
            plan_id=plan.id,
            fecha_inicio=date.today(),
            fecha_expiracion=date.today() + timedelta(days=dias),
            activo=False,
            tipo_periodo=tipo_periodo
        )
        db.session.add(suscripcion)
        db.session.flush()
        
        return {
            'suscripcion_id': suscripcion.id,
            'monto': float(precio),
            'mensaje': 'Suscripcion creada, proceda con el pago'
        }, 201

    @staticmethod
    def realizar_pago(usuario_id, data):
        suscripcion = Suscripcion.query.get(data['suscripcion_id'])
        if not suscripcion:
            return None
        
        plan = PlanSuscripcion.query.get(suscripcion.plan_id)
        if not plan:
            return None
        
        precio = plan.precio_mensual if suscripcion.tipo_periodo == 'mensual' else plan.precio_anual
        
        pago = Pago(
            usuario_id=usuario_id,
            suscripcion_id=suscripcion.id,
            monto=precio,
            metodo_pago=data['metodo_pago'],
            comprobante_url=data.get('comprobante_url'),
            estado='pendiente'
        )
        db.session.add(pago)
        suscripcion.pago_id = pago.id
        db.session.commit()
        return pago

    @staticmethod
    def obtener_pagos_usuario(usuario_id):
        return Pago.query.filter_by(usuario_id=usuario_id).all()

    @staticmethod
    def obtener_progreso_completo(usuario_id):
        progresos = Progreso.query.filter_by(usuario_id=usuario_id, tipo='individual').all()
        completadas = [p for p in progresos if p.completado]
        
        from ..models import Cita
        total_citas = Cita.query.filter_by(activo=True).count()
        
        return {
            'total': total_citas,
            'completadas': len(completadas),
            'puntos': sum(p.calificacion or 0 for p in completadas),
            'racha': 0,
            'racha_maxima': 0,
            'ultimas': [{'cita': p.cita.nombre if p.cita else None, 'calificacion': p.calificacion, 'fecha_completado': p.fecha_completado} for p in completadas[-5:]],
            'por_categoria': [],
            'detalle': [{'cita': p.cita.nombre if p.cita else None, 'completado': p.completado, 'calificacion': p.calificacion, 'fecha_completado': p.fecha_completado} for p in progresos]
        }

    @staticmethod
    def obtener_certificados(usuario_id):
        return Certificado.query.filter_by(usuario_id=usuario_id).all()

    @staticmethod
    def enviar_codigo_verificacion(usuario_id):
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return False
        codigo = secrets.token_hex(3).upper()
        usuario.codigo_verificacion = codigo
        db.session.commit()
        return True

    @staticmethod
    def verificar_email(usuario_id, codigo):
        usuario = Usuario.query.get(usuario_id)
        if usuario and usuario.codigo_verificacion == codigo:
            usuario.email_verificado = True
            usuario.codigo_verificacion = None
            db.session.commit()
            return True
        return False

    @staticmethod
    def obtener_departamentos_desbloqueados(usuario_id):
        suscripcion_activa = UsuarioService.obtener_suscripcion_activa(usuario_id)
        departamentos_gratis = Departamento.query.filter(Departamento.orden_desbloqueo <= 3).all()
        
        if suscripcion_activa and suscripcion_activa.plan:
            plan = suscripcion_activa.plan
            cantidad = plan.departamentos_desbloquea or 0
            departamentos_premium = Departamento.query.filter(Departamento.orden_desbloqueo > 3).limit(cantidad).all()
        else:
            departamentos_premium = []
        
        return {
            'gratis': departamentos_gratis,
            'premium': departamentos_premium
        }

    @staticmethod
    def obtener_departamento_actual(usuario_id):
        usuario = Usuario.query.get(usuario_id)
        return usuario.departamento_actual if usuario else None

    @staticmethod
    def cambiar_departamento_actual(usuario_id, nuevo_departamento):
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return False
        
        departamentos = UsuarioService.obtener_departamentos_desbloqueados(usuario_id)
        todos = list(departamentos['gratis']) + list(departamentos['premium'])
        
        if any(d.nombre == nuevo_departamento for d in todos):
            usuario.departamento_actual = nuevo_departamento
            db.session.commit()
            return True
        return False

    @staticmethod
    def obtener_estadisticas_globales():
        total_usuarios = Usuario.query.filter_by(activo=True).count()
        usuarios_activos = Usuario.query.filter_by(activo=True).count()
        
        suscripciones_activas = Suscripcion.query.filter(
            Suscripcion.activo == True,
            Suscripcion.fecha_expiracion >= date.today()
        ).count()
        
        total_parejas = Grupo.query.filter_by(tipo='pareja', activo=True).count()
        
        citas_completadas = Progreso.query.filter_by(completado=True).count()
        
        from sqlalchemy import func
        ingresos = db.session.query(func.sum(Pago.monto)).filter_by(estado='aprobado').scalar() or 0
        
        top = Usuario.query.join(Progreso, Usuario.id == Progreso.usuario_id).filter(
            Progreso.completado == True
        ).group_by(Usuario.id).order_by(func.count().desc()).limit(10).all()
        
        return {
            'total_usuarios': total_usuarios,
            'usuarios_activos': usuarios_activos,
            'usuarios_premium': suscripciones_activas,
            'total_parejas': total_parejas,
            'citas_completadas': citas_completadas,
            'ingresos': float(ingresos),
            'top': [{'nombre': u.nombre, 'total': getattr(u, 'total', 0)} for u in top]
        }

    @staticmethod
    def obtener_progreso_pareja(usuario_id):
        pareja = UsuarioService.obtener_pareja(usuario_id)
        if not pareja:
            return {'completadas': 0, 'puntos': 0, 'racha': 0}
        
        grupo = Grupo.query.join(GrupoMiembro).filter(
            Grupo.tipo == 'pareja',
            GrupoMiembro.usuario_id.in_([usuario_id, pareja.id])
        ).first()
        
        if grupo:
            progresos = Progreso.query.filter_by(grupo_id=grupo.id, tipo='grupal', completado=True).all()
            return {
                'completadas': len(progresos),
                'puntos': sum(p.calificacion or 0 for p in progresos),
                'racha': 0
            }
        return {'completadas': 0, 'puntos': 0, 'racha': 0}

    @staticmethod
    def obtener_solicitudes_pendientes(usuario_id):
        return []

    @staticmethod
    def responder_solicitud(solicitud_id, usuario_id, aceptar):
        return True