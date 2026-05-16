"""
Migración: agrega columnas role e is_active a la tabla users.
Ejecutar una sola vez: python migrate_add_role.py
"""
from app import create_app
from app.extensions import db

app = create_app()

with app.app_context():
    with db.engine.connect() as conn:
        result = conn.execute(db.text("SHOW COLUMNS FROM users LIKE 'role'"))
        if not result.fetchone():
            conn.execute(db.text(
                "ALTER TABLE users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'couple'"
            ))
            print("Columna 'role' agregada.")
        else:
            print("Columna 'role' ya existe.")

        result = conn.execute(db.text("SHOW COLUMNS FROM users LIKE 'is_active'"))
        if not result.fetchone():
            conn.execute(db.text(
                "ALTER TABLE users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE"
            ))
            print("Columna 'is_active' agregada.")
        else:
            print("Columna 'is_active' ya existe.")

        conn.commit()
    print("Migración completada.")
