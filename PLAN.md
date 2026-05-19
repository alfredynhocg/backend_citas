# Plan de Desarrollo — backend_citas

> Generado: 2026-05-18  
> Estado actual: ~40% de endpoints funcionales

---

## Resumen Ejecutivo

El backend tiene una arquitectura sólida (Flask + Flask-RESTX + SQLAlchemy), los modelos están completos y los módulos de auth, couples, dates y memories funcionan bien. El problema principal es que **7 servicios están vacíos** y sus rutas nunca se registraron en la API, lo que deja inactivo el 60% del sistema.

---

## Estado Actual por Módulo

| Módulo | Estado | Problema |
|--------|--------|----------|
| `auth` | Funcional | OK |
| `couples` | Funcional | OK |
| `dates` | Funcional | OK |
| `memories` | Funcional | OK |
| `ia` | Parcial | Sin manejo de errores robusto |
| `admin/citas` | Roto | Imports faltantes en el service |
| `users` | Roto | Nombres de campo incorrectos (inglés vs español) |
| `grupo` | Muerto | Service vacío, ruta no registrada |
| `pago` | Muerto | Service vacío, ruta no registrada |
| `suscripcion` | Muerto | Service vacío, ruta no registrada |
| `mensaje` | Muerto | Service vacío, ruta no registrada |
| `negocio` | Muerto | Service vacío, ruta no registrada |
| `progreso` | Muerto | Service vacío, ruta no registrada |
| `admin` | Muerto | `AdminService` no existe, ruta no registrada |

---

## Prioridad 1 — Correcciones Urgentes (bugs que rompen lo existente)

### 1.1 Corregir `services/users.py` — Nombres de campo incorrectos
**Archivo:** `app/services/users.py`  
**Problema:** El service usa nombres en inglés (`name`, `role`, `is_active`) pero el modelo usa español (`nombre`, `rol_id`, `activo`).  
**Correcciones:**
- `user.name` → `user.nombre`
- `user.role` → `user.rol_id`
- `user.is_active` → `user.activo`
- `user.created_at` → `user.fecha_registro`
- Corregir `_user_dict()` con todos los campos correctos

### 1.2 Corregir imports en `services/admin_cita_service.py`
**Archivo:** `app/services/admin_cita_service.py`  
**Problema:** Usa `current_app`, `os` y `secrets` sin importarlos.  
**Correcciones:**
```python
from flask import current_app
import os
import secrets
```

### 1.3 Agregar dependencias faltantes al entorno virtual
Instalar y agregar a `requirements.txt`:
```
flask-admin==2.2.0
flask-appbuilder==5.2.1
Babel==2.18.0
Pillow==12.2.0
requests==2.34.2
```
Comando:
```bash
pip install flask-admin flask-appbuilder Babel Pillow requests
```

---

## Prioridad 2 — Implementar Servicios Vacíos

Estos 6 archivos están en `app/services/` con **0 líneas** y bloquean sus rutas correspondientes.

### 2.1 `grupo_service.py`
Métodos requeridos por `grupo_routes.py`:
- `obtener_grupos_usuario(usuario_id)` — listar grupos del usuario
- `crear_grupo(data, usuario_id)` — crear grupo, generar código de invitación
- `obtener_grupo(grupo_id, usuario_id)` — detalle de un grupo
- `unirse_por_codigo(codigo, usuario_id)` — unirse con código de invitación
- `actualizar_grupo(grupo_id, data, usuario_id)` — editar grupo (solo admin)
- `eliminar_grupo(grupo_id, usuario_id)` — eliminar grupo (solo admin)
- `obtener_miembros(grupo_id)` — listar miembros
- `expulsar_miembro(grupo_id, miembro_id, admin_id)` — expulsar miembro

**Modelos involucrados:** `Grupo`, `GrupoMiembro`, `User`

### 2.2 `suscripcion_service.py`
Métodos requeridos por `suscripcion_routes.py`:
- `obtener_planes()` — listar planes disponibles (PlanSuscripcion)
- `obtener_suscripciones_usuario(usuario_id)` — suscripciones activas del usuario
- `crear_pago(data, usuario_id)` — crear solicitud de pago (estado: pendiente)
- `obtener_pago(pago_id, usuario_id)` — detalle de pago
- `cancelar_suscripcion(suscripcion_id, usuario_id)` — cancelar suscripción

**Modelos involucrados:** `PlanSuscripcion`, `Pago`, `Suscripcion`, `SuscripcionDepartamento`

### 2.3 `pago_service.py`
Métodos requeridos por `pago_routes.py`:
- `obtener_historial_usuario(usuario_id)` — historial de pagos del usuario
- `subir_comprobante(pago_id, file, usuario_id)` — subir imagen de comprobante

**Modelos involucrados:** `Pago`

### 2.4 `negocio_service.py`
Métodos requeridos por `negocio_routes.py`:
- `listar_negocios(departamento_id, categoria)` — listar con filtros
- `obtener_negocio(negocio_id)` — detalle de negocio
- `crear_negocio(data, usuario_id)` — crear negocio (requiere aprobación)
- `actualizar_negocio(negocio_id, data, usuario_id)` — editar (solo dueño)
- `obtener_fotos(negocio_id)` — fotos del negocio
- `agregar_foto(negocio_id, file, usuario_id)` — subir foto

**Modelos involucrados:** `Negocio`, `FotoNegocio`, `Departamento`

### 2.5 `mensaje_service.py`
Métodos requeridos por `mensaje_routes.py`:
- `obtener_mensajes(grupo_id, usuario_id)` — mensajes de un grupo
- `enviar_mensaje(data, usuario_id)` — enviar mensaje
- `marcar_leidos(grupo_id, usuario_id)` — marcar como leídos
- `obtener_no_leidos(usuario_id)` — conteo de no leídos

**Modelos involucrados:** `Mensaje`, `Grupo`, `GrupoMiembro`

### 2.6 `progreso_service.py`
Métodos requeridos por `progreso_routes.py`:
- `obtener_progreso_usuario(usuario_id)` — progreso individual
- `obtener_progreso_grupo(grupo_id, usuario_id)` — progreso del grupo
- `completar_cita(data, usuario_id)` — registrar cita completada
- `obtener_estadisticas(usuario_id)` — estadísticas y logros

**Modelos involucrados:** `Progreso`, `Cita`, `Grupo`, `Certificado`

---

## Prioridad 3 — Crear `AdminService` (archivo faltante)

**Archivo a crear:** `app/services/admin_service.py`  
Métodos requeridos por `admin_routes.py`:
- `obtener_pagos_pendientes()` — listar pagos en estado pendiente
- `aprobar_pago(pago_id, admin_id)` — aprobar pago, activar suscripción
- `rechazar_pago(pago_id, motivo, admin_id)` — rechazar pago
- `obtener_negocios_pendientes()` — listar negocios sin aprobar
- `aprobar_negocio(negocio_id, admin_id)` — activar negocio
- `rechazar_negocio(negocio_id, motivo, admin_id)` — rechazar negocio
- `obtener_reportes()` — estadísticas generales del sistema

**Modelos involucrados:** `Pago`, `Suscripcion`, `Negocio`, `User`

---

## Prioridad 4 — Registrar Rutas en la API

**Archivo:** `app/__init__.py`  
Agregar las 7 rutas que existen pero nunca se registraron:

```python
from app.routes.grupo_routes import grupo_ns
from app.routes.pago_routes import pago_ns
from app.routes.suscripcion_routes import suscripcion_ns
from app.routes.mensaje_routes import mensaje_ns
from app.routes.negocio_routes import negocio_ns
from app.routes.progreso_routes import progreso_ns
from app.routes.admin_routes import admin_ns

api.add_namespace(grupo_ns, path='/api/grupos')
api.add_namespace(pago_ns, path='/api/pagos')
api.add_namespace(suscripcion_ns, path='/api/suscripciones')
api.add_namespace(mensaje_ns, path='/api/mensajes')
api.add_namespace(negocio_ns, path='/api/negocios')
api.add_namespace(progreso_ns, path='/api/progreso')
api.add_namespace(admin_ns, path='/api/admin')
```

---

## Prioridad 5 — Seguridad y Buenas Prácticas

### 5.1 Mover secrets a variables de entorno
**Archivos:** `config.py`, `app/__init__.py`  
- `SECRET_KEY` → leer desde `.env`
- `JWT_SECRET_KEY` → leer desde `.env`
- Password del admin panel → leer desde `.env`
- Cadena de conexión MySQL → leer desde `.env`

Agregar a `.env`:
```
SECRET_KEY=...
JWT_SECRET_KEY=...
ADMIN_PASSWORD=...
DATABASE_URL=mysql+pymysql://root:@localhost/citas_romanticas
```

### 5.2 Corregir `datetime.utcnow()` deprecado
**Archivo:** `app/models.py` (línea 313)  
Cambiar:
```python
# antes
datetime.utcnow()
# después
datetime.now(timezone.utc)
```

### 5.3 Agregar manejo de transacciones
En los services que usan `db.session.commit()` sin try-except, envolver en:
```python
try:
    db.session.commit()
except Exception:
    db.session.rollback()
    raise
```

---

## Prioridad 6 — Limpieza de Código

- Eliminar o archivar `app/modelsOld.py` (no se usa)
- Eliminar o archivar `app/views.py` (no se usa)
- Revisar aliases al final de `models.py` (líneas 319-323)
- Eliminar `app/routes/test.py` antes de producción o protegerlo

---

## Orden de Implementación Recomendado

```
Semana 1 — Estabilizar lo existente
  [ ] 1.1 Corregir users.py (campo names)
  [ ] 1.2 Corregir imports en admin_cita_service.py
  [ ] 1.3 Instalar dependencias faltantes

Semana 2 — Servicios de grupos y mensajes
  [ ] 2.1 Implementar grupo_service.py
  [ ] 2.5 Implementar mensaje_service.py
  [ ] Registrar grupo_ns y mensaje_ns

Semana 3 — Servicios de negocio y pagos
  [ ] 2.3 Implementar pago_service.py
  [ ] 2.4 Implementar negocio_service.py
  [ ] 2.2 Implementar suscripcion_service.py
  [ ] Registrar pago_ns, negocio_ns, suscripcion_ns

Semana 4 — Progreso, Admin y seguridad
  [ ] 2.6 Implementar progreso_service.py
  [ ] 3   Crear admin_service.py
  [ ] 4   Registrar todas las rutas restantes
  [ ] 5   Mover secrets a .env
  [ ] 5.2 Corregir datetime deprecado

Semana 5 — Limpieza y pruebas
  [ ] 6   Eliminar archivos legacy
  [ ] Pruebas de integración por módulo
  [ ] Documentación Swagger completa
```

---

## Archivos a Tocar por Tarea

| Tarea | Archivos |
|-------|----------|
| 1.1 | `app/services/users.py` |
| 1.2 | `app/services/admin_cita_service.py` |
| 1.3 | `requirements.txt` + entorno virtual |
| 2.1 | `app/services/grupo_service.py` |
| 2.2 | `app/services/suscripcion_service.py` |
| 2.3 | `app/services/pago_service.py` |
| 2.4 | `app/services/negocio_service.py` |
| 2.5 | `app/services/mensaje_service.py` |
| 2.6 | `app/services/progreso_service.py` |
| 3   | `app/services/admin_service.py` (nuevo) |
| 4   | `app/__init__.py` |
| 5   | `config.py`, `app/__init__.py`, `.env` |
| 6   | `app/modelsOld.py`, `app/views.py` |
