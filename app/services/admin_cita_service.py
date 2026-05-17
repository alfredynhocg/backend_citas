from datetime import datetime
from ..models import db, Categoria, Negocio, Cita, FotoCita, Departamento, User
from sqlalchemy import func

class AdminCitaService:

    # ==================== CATEGORIAS ====================
    @staticmethod
    def crear_cita_con_archivos(data, archivos):
        """Crear cita con imágenes subidas como archivos"""
        
        # Crear la cita
        cita = Cita(
            nombre=data.get('nombre'),
            descripcion=data.get('descripcion'),
            categoria_id=data.get('categoria_id'),
            departamento_id=data.get('departamento_id'),
            negocio_id=data.get('negocio_id'),
            latitud=data.get('latitud'),
            longitud=data.get('longitud'),
            direccion=data.get('direccion'),
            puntos=data.get('puntos', 10),
            portada_url=data.get('portada_url'),
            activo=data.get('activo', True)
        )
        db.session.add(cita)
        db.session.flush()  # Para obtener el ID sin commit
        
        # Subir las fotos
        fotos_subidas = []
        upload_folder = current_app.config.get('IMG_UPLOAD_FOLDER', 'app/static/uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        for archivo in archivos:
            if archivo and archivo.filename:
                # Generar nombre único
                ext = archivo.filename.rsplit('.', 1)[1].lower()
                filename = f"cita_{cita.id}_{secrets.token_hex(8)}.{ext}"
                filepath = os.path.join(upload_folder, filename)
                archivo.save(filepath)
                
                foto_url = f"/static/uploads/{filename}"
                
                foto = FotoCita(
                    cita_id=cita.id,
                    url=foto_url,
                    descripcion=data.get('foto_descripcion')
                )
                db.session.add(foto)
                fotos_subidas.append(foto_url)
        
        db.session.commit()
        
        return {
            'id': cita.id,
            'nombre': cita.nombre,
            'fotos': fotos_subidas
        }
    
    @staticmethod
    def agregar_fotos_a_cita(cita_id, archivos):
        """Agregar fotos a una cita existente"""
        cita = Cita.query.get(cita_id)
        if not cita:
            return None
        
        fotos_subidas = []
        upload_folder = current_app.config.get('IMG_UPLOAD_FOLDER', 'app/static/uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        for archivo in archivos:
            if archivo and archivo.filename:
                ext = archivo.filename.rsplit('.', 1)[1].lower()
                filename = f"cita_{cita_id}_{secrets.token_hex(8)}.{ext}"
                filepath = os.path.join(upload_folder, filename)
                archivo.save(filepath)
                
                foto_url = f"/static/uploads/{filename}"
                
                foto = FotoCita(
                    cita_id=cita_id,
                    url=foto_url
                )
                db.session.add(foto)
                fotos_subidas.append(foto_url)
        
        db.session.commit()
        return fotos_subidas

    @staticmethod
    def obtener_todas_categorias():
        categorias = Categoria.query.all()
        return [{
            'id': c.id,
            'nombre': c.nombre,
            'total_citas': Cita.query.filter_by(categoria_id=c.id, activo=True).count()
        } for c in categorias]

    @staticmethod
    def obtener_categoria_por_id(categoria_id):
        c = Categoria.query.get(categoria_id)
        if not c:
            return None
        return {
            'id': c.id,
            'nombre': c.nombre,
            'total_citas': Cita.query.filter_by(categoria_id=c.id, activo=True).count()
        }

    @staticmethod
    def crear_categoria(data):
        nombre = data.get('nombre', '').strip()
        if not nombre:
            return {'error': 'El nombre de la categoria es requerido'}, 400
        
        existe = Categoria.query.filter_by(nombre=nombre).first()
        if existe:
            return {'error': 'Ya existe una categoria con ese nombre'}, 400
        
        categoria = Categoria(nombre=nombre)
        db.session.add(categoria)
        db.session.commit()
        
        return {'mensaje': 'Categoria creada', 'id': categoria.id, 'nombre': categoria.nombre}, 201

    @staticmethod
    def actualizar_categoria(categoria_id, data):
        categoria = Categoria.query.get(categoria_id)
        if not categoria:
            return {'error': 'Categoria no encontrada'}, 404
        
        nombre = data.get('nombre', '').strip()
        if nombre:
            categoria.nombre = nombre
        
        db.session.commit()
        return {'mensaje': 'Categoria actualizada', 'id': categoria.id, 'nombre': categoria.nombre}, 200

    @staticmethod
    def eliminar_categoria(categoria_id):
        categoria = Categoria.query.get(categoria_id)
        if not categoria:
            return {'error': 'Categoria no encontrada'}, 404
        
        citas_asociadas = Cita.query.filter_by(categoria_id=categoria_id).count()
        if citas_asociadas > 0:
            return {'error': f'No se puede eliminar: hay {citas_asociadas} citas asociadas'}, 400
        
        db.session.delete(categoria)
        db.session.commit()
        return {'mensaje': 'Categoria eliminada'}, 200


    # ==================== NEGOCIOS ====================

    @staticmethod
    def obtener_todos_negocios():
        negocios = Negocio.query.all()
        return [{
            'id': n.id,
            'nombre': n.nombre,
            'direccion': n.direccion,
            'departamento_id': n.departamento_id,
            'departamento_nombre': n.departamento.nombre if n.departamento else None,
            'telefono': n.telefono,
            'categoria_negocio': n.categoria_negocio,
            'logo_url': n.logo_url,
            'activo': n.activo,
            'total_citas': Cita.query.filter_by(negocio_id=n.id).count()
        } for n in negocios]

    @staticmethod
    def obtener_negocio_por_id(negocio_id):
        n = Negocio.query.get(negocio_id)
        if not n:
            return None
        return {
            'id': n.id,
            'nombre': n.nombre,
            'direccion': n.direccion,
            'latitud': float(n.latitud) if n.latitud else None,
            'longitud': float(n.longitud) if n.longitud else None,
            'departamento_id': n.departamento_id,
            'departamento_nombre': n.departamento.nombre if n.departamento else None,
            'telefono': n.telefono,
            'categoria_negocio': n.categoria_negocio,
            'logo_url': n.logo_url,
            'activo': n.activo,
            'total_citas': Cita.query.filter_by(negocio_id=n.id).count()
        }

    @staticmethod
    def crear_negocio(data):
        nombre = data.get('nombre', '').strip()
        if not nombre:
            return {'error': 'El nombre del negocio es requerido'}, 400
        
        negocio = Negocio(
            nombre=nombre,
            direccion=data.get('direccion'),
            latitud=data.get('latitud'),
            longitud=data.get('longitud'),
            departamento_id=data.get('departamento_id'),
            telefono=data.get('telefono'),
            categoria_negocio=data.get('categoria_negocio'),
            logo_url=data.get('logo_url'),
            activo=data.get('activo', True)
        )
        db.session.add(negocio)
        db.session.commit()
        
        return {'mensaje': 'Negocio creado', 'id': negocio.id, 'nombre': negocio.nombre}, 201

    @staticmethod
    def actualizar_negocio(negocio_id, data):
        negocio = Negocio.query.get(negocio_id)
        if not negocio:
            return {'error': 'Negocio no encontrado'}, 404
        
        if 'nombre' in data:
            negocio.nombre = data['nombre']
        if 'direccion' in data:
            negocio.direccion = data['direccion']
        if 'latitud' in data:
            negocio.latitud = data['latitud']
        if 'longitud' in data:
            negocio.longitud = data['longitud']
        if 'departamento_id' in data:
            negocio.departamento_id = data['departamento_id']
        if 'telefono' in data:
            negocio.telefono = data['telefono']
        if 'categoria_negocio' in data:
            negocio.categoria_negocio = data['categoria_negocio']
        if 'logo_url' in data:
            negocio.logo_url = data['logo_url']
        if 'activo' in data:
            negocio.activo = data['activo']
        
        db.session.commit()
        return {'mensaje': 'Negocio actualizado', 'id': negocio.id}, 200

    @staticmethod
    def eliminar_negocio(negocio_id):
        negocio = Negocio.query.get(negocio_id)
        if not negocio:
            return {'error': 'Negocio no encontrado'}, 404
        
        citas_asociadas = Cita.query.filter_by(negocio_id=negocio_id).count()
        if citas_asociadas > 0:
            return {'error': f'No se puede eliminar: hay {citas_asociadas} citas asociadas'}, 400
        
        db.session.delete(negocio)
        db.session.commit()
        return {'mensaje': 'Negocio eliminado'}, 200


    # ==================== CITAS ====================

    @staticmethod
    def crear_cita(data):
        nombre = data.get('nombre', '').strip()
        if not nombre:
            return {'error': 'El nombre de la cita es requerido'}, 400
        
        cita = Cita(
            nombre=nombre,
            descripcion=data.get('descripcion'),
            categoria_id=data.get('categoria_id'),
            departamento_id=data.get('departamento_id'),
            negocio_id=data.get('negocio_id'),
            latitud=data.get('latitud'),
            longitud=data.get('longitud'),
            direccion=data.get('direccion'),
            puntos=data.get('puntos', 10),
            portada_url=data.get('portada_url'),
            activo=data.get('activo', True)
        )
        db.session.add(cita)
        db.session.commit()
        
        return {'mensaje': 'Cita creada', 'id': cita.id, 'nombre': cita.nombre}

    @staticmethod
    def actualizar_cita(cita_id, data):
        cita = Cita.query.get(cita_id)
        if not cita:
            return {'error': 'Cita no encontrada'}, 404
        
        if 'nombre' in data:
            cita.nombre = data['nombre']
        if 'descripcion' in data:
            cita.descripcion = data['descripcion']
        if 'categoria_id' in data:
            cita.categoria_id = data['categoria_id']
        if 'departamento_id' in data:
            cita.departamento_id = data['departamento_id']
        if 'negocio_id' in data:
            cita.negocio_id = data['negocio_id']
        if 'latitud' in data:
            cita.latitud = data['latitud']
        if 'longitud' in data:
            cita.longitud = data['longitud']
        if 'direccion' in data:
            cita.direccion = data['direccion']
        if 'puntos' in data:
            cita.puntos = data['puntos']
        if 'portada_url' in data:
            cita.portada_url = data['portada_url']
        if 'activo' in data:
            cita.activo = data['activo']
        
        db.session.commit()
        return {'mensaje': 'Cita actualizada', 'id': cita.id}

    @staticmethod
    def eliminar_cita(cita_id):
        cita = Cita.query.get(cita_id)
        if not cita:
            return {'error': 'Cita no encontrada'}, 404
        
        FotoCita.query.filter_by(cita_id=cita_id).delete()
        db.session.delete(cita)
        db.session.commit()
        return {'mensaje': 'Cita eliminada'}
    # ==================== ESTADISTICAS ====================

    @staticmethod
    def obtener_estadisticas():
        total_citas = Cita.query.count()
        total_activas = Cita.query.filter_by(activo=True).count()
        total_categorias = Categoria.query.count()
        total_negocios = Negocio.query.count()
        total_negocios_activos = Negocio.query.filter_by(activo=True).count()
        
        citas_por_categoria = db.session.query(
            Categoria.nombre,
            func.count(Cita.id).label('total')
        ).outerjoin(Cita, Cita.categoria_id == Categoria.id).group_by(Categoria.id).all()
        
        return {
            'total_citas': total_citas,
            'citas_activas': total_activas,
            'total_categorias': total_categorias,
            'total_negocios': total_negocios,
            'negocios_activos': total_negocios_activos,
            'citas_por_categoria': [{'categoria': c[0] or 'Sin categoria', 'total': c[1]} for c in citas_por_categoria]
        }, 200