"# citas_frontend" 
# 📚 Citas Bolivia - Base de Datos

## Sistema de Gestión de Citas Románticas en Bolivia

---

## 📌 Descripción

Base de datos relacional para una aplicación de citas románticas que permite a usuarios individuales o grupos (parejas, amigos) descubrir, completar y documentar experiencias en diferentes departamentos de Bolivia.

---

## 🗂️ Tablas (18 tablas)

| # | Tabla | Descripción |
|---|-------|-------------|
| 1 | roles | Roles de usuario (admin, usuario, etc.) |
| 2 | usuarios | Datos de usuarios registrados |
| 3 | grupos | Grupos (parejas, amigos, familias) |
| 4 | grupo_miembros | Miembros de cada grupo |
| 5 | planes_suscripcion | Planes de suscripción (Lite, Plus, Premium) |
| 6 | pagos | Registro de pagos realizados |
| 7 | suscripciones | Suscripciones activas por usuario/grupo |
| 8 | suscripcion_departamentos | Departamentos desbloqueados por suscripción |
| 9 | departamentos | Departamentos de Bolivia |
| 10 | categorias | Categorías de citas |
| 11 | negocios | Negocios (restaurantes, cafés, hoteles) |
| 12 | fotos_negocios | Galería de fotos de negocios |
| 13 | citas | Las 100 citas románticas |
| 14 | fotos_citas | Fotos subidas por usuarios/grupos |
| 15 | progreso | Progreso de citas (individual o grupal) |
| 16 | certificados | Certificados ganados por logros |
| 17 | mensajes | Mensajes grupales y privados |

---

## 🔗 Relaciones Principales
usuarios (1) ──┼── (N) grupo_miembros ── (N) ── grupos
│
└── (N) pagos ── (1) planes_suscripcion
│
└── (N) suscripciones
│
└── (N) progreso (individual)

grupos (1) ──┼── (N) grupo_miembros ── (N) ── usuarios
│
└── (N) pagos
│
└── (N) suscripciones
│
└── (N) progreso (grupal)
│
└── (N) mensajes

suscripciones (1) ── (N) ── suscripcion_departamentos ── (1) ── departamentos

citas (1) ── (N) ── fotos_citas
citas (1) ── (N) ── progreso
citas (N) ── (1) ── categorias
citas (N) ── (1) ── negocios
citas (N) ── (1) ── departamentos

negocios (1) ── (N) ── fotos_negocios
negocios (N) ── (1) ── departamentos

text

---

## 📊 Diagrama Entidad-Relación
┌─────────────┐ ┌──────────────────┐ ┌─────────────┐
│ usuarios │────<│ grupo_miembros │>────│ grupos │
└─────────────┘ └──────────────────┘ └─────────────┘
│ │ │
│ │ │
▼ ▼ ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ pagos │────<│suscripciones│ │ progreso │
└─────────────┘ └─────────────┘ └─────────────┘
│ │ │
│ │ │
▼ ▼ ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│planes_suscr.│ │suscripcion_ │ │ citas │
└─────────────┘ │departamentos│ └─────────────┘
└─────────────┘ │
│ │
▼ ▼
┌─────────────┐ ┌─────────────┐
│departamentos│ │ categorias │
└─────────────┘ └─────────────┘
│
▼
┌─────────────┐
│ negocios │
└─────────────┘
│
▼
┌─────────────┐
│fotos_negocios│
└─────────────┘

text

---

## 🎯 Planes de Suscripción

| Plan | Precio Mensual | Precio Anual | Máx. Integrantes | Departamentos |
|------|----------------|--------------|------------------|---------------|
| Lite | Bs 9.99 | Bs 89.99 | 1 | 1 extra |
| Plus | Bs 19.99 | Bs 179.99 | 2 | 3 extra |
| Premium | Bs 29.99 | Bs 269.99 | 10 | 9 (todos) |

---

## 🔐 Tipos de Progreso

| tipo | grupo_id | usuario_id | Uso |
|------|----------|------------|-----|
| 'grupal' | NOT NULL | NULL | Toda la pareja/grupo completa la cita |
| 'individual' | NULL | NOT NULL | Us
pero todo dame en vodigo mieda en codig .md
markdown
# 📚 Citas Bolivia - Base de Datos

## Sistema de Gestión de Citas Románticas en Bolivia

---

## 📌 Descripción

Base de datos relacional para una aplicación de citas románticas que permite a usuarios individuales o grupos (parejas, amigos) descubrir, completar y documentar experiencias en diferentes departamentos de Bolivia.

---

## 🗂️ Tablas (18 tablas)

| # | Tabla | Descripción |
|---|-------|-------------|
| 1 | roles | Roles de usuario (admin, usuario, etc.) |
| 2 | usuarios | Datos de usuarios registrados |
| 3 | grupos | Grupos (parejas, amigos, familias) |
| 4 | grupo_miembros | Miembros de cada grupo |
| 5 | planes_suscripcion | Planes de suscripción (Lite, Plus, Premium) |
| 6 | pagos | Registro de pagos realizados |
| 7 | suscripciones | Suscripciones activas por usuario/grupo |
| 8 | suscripcion_departamentos | Departamentos desbloqueados por suscripción |
| 9 | departamentos | Departamentos de Bolivia |
| 10 | categorias | Categorías de citas |
| 11 | negocios | Negocios (restaurantes, cafés, hoteles) |
| 12 | fotos_negocios | Galería de fotos de negocios |
| 13 | citas | Las 100 citas románticas |
| 14 | fotos_citas | Fotos subidas por usuarios/grupos |
| 15 | progreso | Progreso de citas (individual o grupal) |
| 16 | certificados | Certificados ganados por logros |
| 17 | mensajes | Mensajes grupales y privados |

---

## 🔗 Relaciones Principales
usuarios (1) ──┼── (N) grupo_miembros ── (N) ── grupos
│
└── (N) pagos ── (1) planes_suscripcion
│
└── (N) suscripciones
│
└── (N) progreso (individual)

grupos (1) ──┼── (N) grupo_miembros ── (N) ── usuarios
│
└── (N) pagos
│
└── (N) suscripciones
│
└── (N) progreso (grupal)
│
└── (N) mensajes

suscripciones (1) ── (N) ── suscripcion_departamentos ── (1) ── departamentos

citas (1) ── (N) ── fotos_citas
citas (1) ── (N) ── progreso
citas (N) ── (1) ── categorias
citas (N) ── (1) ── negocios
citas (N) ── (1) ── departamentos

negocios (1) ── (N) ── fotos_negocios
negocios (N) ── (1) ── departamentos

text

---

## 📊 Diagrama Entidad-Relación
┌─────────────┐ ┌──────────────────┐ ┌─────────────┐
│ usuarios │────<│ grupo_miembros │>────│ grupos │
└─────────────┘ └──────────────────┘ └─────────────┘
│ │ │
│ │ │
▼ ▼ ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ pagos │────<│suscripciones│ │ progreso │
└─────────────┘ └─────────────┘ └─────────────┘
│ │ │
│ │ │
▼ ▼ ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│planes_suscr.│ │suscripcion_ │ │ citas │
└─────────────┘ │departamentos│ └─────────────┘
└─────────────┘ │
│ │
▼ ▼
┌─────────────┐ ┌─────────────┐
│departamentos│ │ categorias │
└─────────────┘ └─────────────┘
│
▼
┌─────────────┐
│ negocios │
└─────────────┘
│
▼
┌─────────────┐
│fotos_negocios│
└─────────────┘