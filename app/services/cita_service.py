from datetime import datetime
from sqlalchemy import func, and_, or_
from ..models import db, User, Grupo, GrupoMiembro, Cita, Categoria, Departamento, Negocio, Progreso, FotoCita, Suscripcion
import secrets
import os
from werkzeug.utils import secure_filename
from flask import current_app

class CitaService:

    @staticmethod
    def obtener_citas_disponibles(usuario_id, departamento=None, categoria_id=None):
        """Obtener todas las citas disponibles para un usuario"""
        usuario = User.query.get(usuario_id)
        if not usuario:
            return []
        
        departamentos_desbloqueados = CitaService._obtener_departamentos_desbloqueados(usuario_id)
        
        query = Cita.query.filter(Cita.activo == True)
        
        if departamento:
            query = query.join(Departamento).filter(Departamento.nombre == departamento)
        else:
            query = query.filter(Cita.departamento_id.in_(departamentos_desbloqueados))
        
        if categoria_id:
            query = query.filter(Cita.categoria_id == categoria_id)
        
        citas = query.all()
        
        return [{
            'id': c.id,
            'nombre': c.nombre,
            'descripcion': c.descripcion[:200] + '...' if c.descripcion and len(c.descripcion) > 200 else c.descripcion,
            'categoria_id': c.categoria_id,
            'categoria_nombre': c.categoria.nombre if c.categoria else None,
            'departamento_id': c.departamento_id,
            'departamento_nombre': c.departamento.nombre if c.departamento else None,
            'negocio_id': c.negocio_id,
            'negocio_nombre': c.negocio.nombre if c.negocio else None,
            'puntos': c.puntos,
            'portada_url': c.portada_url,
            'requiere_premium': c.departamento.orden_desbloqueo > 3 if c.departamento else False
        } for c in citas]

    @staticmethod
    def obtener_detalle_cita(usuario_id, cita_id):
        """Obtener detalle completo de una cita"""
        cita = Cita.query.get(cita_id)
        if not cita:
            return None
        
        completados = Progreso.query.filter_by(cita_id=cita_id, completado=True).count()
        
        promedio = db.session.query(func.avg(Progreso.calificacion)).filter(
            Progreso.cita_id == cita_id, 
            Progreso.calificacion.isnot(None)
        ).scalar() or 0
        
        fotos = FotoCita.query.filter_by(cita_id=cita_id).limit(10).all()
        
        return {
            'id': cita.id,
            'nombre': cita.nombre,
            'descripcion': cita.descripcion,
            'categoria_id': cita.categoria_id,
            'categoria_nombre': cita.categoria.nombre if cita.categoria else None,
            'departamento_id': cita.departamento_id,
            'departamento_nombre': cita.departamento.nombre if cita.departamento else None,
            'negocio_id': cita.negocio_id,
            'negocio_nombre': cita.negocio.nombre if cita.negocio else None,
            'direccion': cita.direccion,
            'latitud': float(cita.latitud) if cita.latitud else None,
            'longitud': float(cita.longitud) if cita.longitud else None,
            'puntos': cita.puntos,
            'portada_url': cita.portada_url,
            'completados_total': completados,
            'calificacion_promedio': round(float(promedio), 1),
            'fotos': [{'url': f.url, 'descripcion': f.descripcion} for f in fotos]
        }

    @staticmethod
    def verificar_acceso_cita(usuario_id, cita_id):
        cita = Cita.query.get(cita_id)
        if not cita:
            return False
        
        if not cita.departamento:
            return True
        
        if cita.departamento.orden_desbloqueo <= 3:
            return True
        
        departamentos_desbloqueados = CitaService._obtener_departamentos_desbloqueados(usuario_id)
        return cita.departamento_id in departamentos_desbloqueados

    @staticmethod
    def _obtener_departamentos_desbloqueados(usuario_id):
        """Obtener IDs de departamentos desbloqueados por el usuario"""
        departamentos_ids = [1, 2, 3]  # La Paz, Cochabamba, Santa Cruz (gratis)
        
        suscripciones_individual = Suscripcion.query.filter(
            Suscripcion.usuario_id == usuario_id,
            Suscripcion.activo == True,
            Suscripcion.fecha_expiracion >= datetime.now().date()
        ).all()
        
        for suscripcion in suscripciones_individual:
            if suscripcion.plan:
                pass
        
        grupos = GrupoMiembro.query.filter_by(usuario_id=usuario_id).all()
        for grupo in grupos:
            suscripciones_grupo = Suscripcion.query.filter(
                Suscripcion.grupo_id == grupo.grupo_id,
                Suscripcion.activo == True,
                Suscripcion.fecha_expiracion >= datetime.now().date()
            ).all()
            for suscripcion in suscripciones_grupo:
                if suscripcion.plan:
                    pass
        
        return departamentos_ids

    @staticmethod
    def obtener_categorias():
        categorias = Categoria.query.all()
        return [{
            'id': c.id,
            'nombre': c.nombre,
            'total_citas': Cita.query.filter_by(categoria_id=c.id, activo=True).count()
        } for c in categorias]

    @staticmethod
    def obtener_departamentos():
        departamentos = Departamento.query.order_by(Departamento.orden_desbloqueo).all()
        return [{
            'id': d.id,
            'nombre': d.nombre,
            'requiere_premium': d.orden_desbloqueo > 3,
            'total_citas': Cita.query.filter_by(departamento_id=d.id, activo=True).count()
        } for d in departamentos]

    @staticmethod
    def completar_cita(usuario_id, data):
        """Marcar una cita como completada"""
        cita_id = data.get('cita_id')
        grupo_id = data.get('grupo_id')
        
        cita = Cita.query.get(cita_id)
        if not cita:
            return {'error': 'Cita no encontrada'}, 404
        
        if not CitaService.verificar_acceso_cita(usuario_id, cita_id):
            return {'error': 'No tienes acceso a esta cita'}, 403
        
        if grupo_id:
            es_miembro = GrupoMiembro.query.filter_by(grupo_id=grupo_id, usuario_id=usuario_id).first()
            if not es_miembro:
                return {'error': 'No perteneces a este grupo'}, 403
            
            existente = Progreso.query.filter_by(
                grupo_id=grupo_id, 
                cita_id=cita_id, 
                tipo='grupal'
            ).first()
            
            if existente and existente.completado:
                return {'error': 'Esta cita ya fue completada por tu grupo'}, 400
            
            if not existente:
                progreso = Progreso(
                    tipo='grupal',
                    grupo_id=grupo_id,
                    cita_id=cita_id,
                    completado=True,
                    fecha_completado=datetime.now()
                )
                db.session.add(progreso)
            else:
                existente.completado = True
                existente.fecha_completado = datetime.now()
        else:
            existente = Progreso.query.filter_by(
                usuario_id=usuario_id, 
                cita_id=cita_id, 
                tipo='individual'
            ).first()
            
            if existente and existente.completado:
                return {'error': 'Ya completaste esta cita'}, 400
            
            if not existente:
                progreso = Progreso(
                    tipo='individual',
                    usuario_id=usuario_id,
                    cita_id=cita_id,
                    completado=True,
                    fecha_completado=datetime.now()
                )
                db.session.add(progreso)
            else:
                existente.completado = True
                existente.fecha_completado = datetime.now()
        
        db.session.commit()
        
        return {
            'mensaje': 'Cita completada exitosamente',
            'cita_id': cita_id,
            'puntos_ganados': cita.puntos or 10,
            'fecha': str(datetime.now())
        }, 201

    @staticmethod
    def calificar_cita(usuario_id, cita_id, data):
        """Calificar una cita ya completada"""
        calificacion = data.get('calificacion')
        anecdota = data.get('anecdota')
        
        progreso = Progreso.query.filter(
            Progreso.cita_id == cita_id,
            or_(
                and_(Progreso.tipo == 'individual', Progreso.usuario_id == usuario_id),
                and_(Progreso.tipo == 'grupal', Progreso.grupo_id.in_(
                    db.session.query(GrupoMiembro.grupo_id).filter(GrupoMiembro.usuario_id == usuario_id)
                ))
            )
        ).first()
        
        if not progreso or not progreso.completado:
            return {'error': 'No has completado esta cita'}, 400
        
        progreso.calificacion = calificacion
        if anecdota:
            progreso.anecdota = anecdota
        
        db.session.commit()
        
        return {'mensaje': 'Calificacion guardada', 'calificacion': calificacion}, 200

    @staticmethod
    def subir_fotos(usuario_id, cita_id, fotos):
        """Subir fotos de una cita completada"""
        progreso = Progreso.query.filter(
            Progreso.cita_id == cita_id,
            or_(
                and_(Progreso.tipo == 'individual', Progreso.usuario_id == usuario_id),
                and_(Progreso.tipo == 'grupal', Progreso.grupo_id.in_(
                    db.session.query(GrupoMiembro.grupo_id).filter(GrupoMiembro.usuario_id == usuario_id)
                ))
            )
        ).first()
        
        if not progreso or not progreso.completado:
            return {'error': 'No has completado esta cita'}, 400
        
        fotos_subidas = []
        upload_folder = current_app.config.get('IMG_UPLOAD_FOLDER', 'uploads')
        
        for foto in fotos:
            if foto and foto.filename:
                filename = secure_filename(f"{secrets.token_hex(8)}_{foto.filename}")
                filepath = os.path.join(upload_folder, filename)
                foto.save(filepath)
                
                nueva_foto = FotoCita(
                    cita_id=cita_id,
                    grupo_id=progreso.grupo_id,
                    usuario_id=usuario_id,
                    url=f"/static/uploads/{filename}"
                )
                db.session.add(nueva_foto)
                fotos_subidas.append(nueva_foto.url)
        
        db.session.commit()
        
        return {'mensaje': f'{len(fotos_subidas)} fotos subidas', 'fotos': fotos_subidas}, 201

    @staticmethod
    def obtener_cita_aleatoria(usuario_id, departamento=None):
        departamentos_desbloqueados = CitaService._obtener_departamentos_desbloqueados(usuario_id)
        
        query = Cita.query.filter(Cita.activo == True)
        
        if departamento:
            query = query.join(Departamento).filter(Departamento.nombre == departamento)
        else:
            query = query.filter(Cita.departamento_id.in_(departamentos_desbloqueados))
        
        completadas = db.session.query(Progreso.cita_id).filter(
            or_(
                and_(Progreso.tipo == 'individual', Progreso.usuario_id == usuario_id),
                and_(Progreso.tipo == 'grupal', Progreso.grupo_id.in_(
                    db.session.query(GrupoMiembro.grupo_id).filter(GrupoMiembro.usuario_id == usuario_id)
                ))
            ),
            Progreso.completado == True
        ).subquery()
        
        query = query.filter(Cita.id.notin_(completadas))
        
        cita = query.order_by(func.random()).first()
        
        if not cita:
            return None
        
        return {
            'id': cita.id,
            'nombre': cita.nombre,
            'descripcion': cita.descripcion[:200] + '...' if cita.descripcion else None,
            'categoria_nombre': cita.categoria.nombre if cita.categoria else None,
            'departamento_nombre': cita.departamento.nombre if cita.departamento else None,
            'portada_url': cita.portada_url
        }

    @staticmethod
    def obtener_citas_recomendadas(usuario_id, limit=5):
        categorias_populares = db.session.query(
            Progreso.cita_id,
            func.count(Progreso.id).label('total')
        ).filter(
            or_(
                and_(Progreso.tipo == 'individual', Progreso.usuario_id == usuario_id),
                and_(Progreso.tipo == 'grupal', Progreso.grupo_id.in_(
                    db.session.query(GrupoMiembro.grupo_id).filter(GrupoMiembro.usuario_id == usuario_id)
                ))
            ),
            Progreso.completado == True
        ).group_by(Progreso.cita_id).order_by(func.count(Progreso.id).desc()).limit(limit).all()
        
        return CitaService.obtener_citas_disponibles(usuario_id, limit=limit)

    @staticmethod
    def obtener_progreso_usuario(usuario_id):
        """Obtener progreso completo de citas del usuario"""
        total_citas = Cita.query.filter_by(activo=True).count()
        
        completadas_individual = Progreso.query.filter_by(
            usuario_id=usuario_id, 
            tipo='individual', 
            completado=True
        ).count()
        
        completadas_grupal = db.session.query(Progreso).join(
            GrupoMiembro, Progreso.grupo_id == GrupoMiembro.grupo_id
        ).filter(
            GrupoMiembro.usuario_id == usuario_id,
            Progreso.tipo == 'grupal',
            Progreso.completado == True
        ).count()
        
        total_completadas = completadas_individual + completadas_grupal
        
        por_categoria = db.session.query(
            Categoria.nombre,
            func.count(Progreso.id).label('completadas')
        ).join(Cita, Cita.categoria_id == Categoria.id).outerjoin(
            Progreso, and_(
                Progreso.cita_id == Cita.id,
                or_(
                    and_(Progreso.tipo == 'individual', Progreso.usuario_id == usuario_id),
                    and_(Progreso.tipo == 'grupal', Progreso.grupo_id.in_(
                        db.session.query(GrupoMiembro.grupo_id).filter(GrupoMiembro.usuario_id == usuario_id)
                    ))
                ),
                Progreso.completado == True
            )
        ).group_by(Categoria.id).all()
        
        return {
            'total_citas': total_citas,
            'completadas': total_completadas,
            'porcentaje': round((total_completadas / total_citas) * 100, 2) if total_citas > 0 else 0,
            'por_categoria': [{'categoria': c[0], 'completadas': c[1] or 0} for c in por_categoria]
        }

    @staticmethod
    def obtener_progreso_grupo(usuario_id, grupo_id):
        es_miembro = GrupoMiembro.query.filter_by(grupo_id=grupo_id, usuario_id=usuario_id).first()
        if not es_miembro:
            return None
        
        total_citas = Cita.query.filter_by(activo=True).count()
        completadas = Progreso.query.filter_by(grupo_id=grupo_id, tipo='grupal', completado=True).count()
        
        return {
            'grupo_id': grupo_id,
            'total_citas': total_citas,
            'completadas': completadas,
            'porcentaje': round((completadas / total_citas) * 100, 2) if total_citas > 0 else 0
        }