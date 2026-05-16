"""Punto de entrada para Gunicorn en producción.

Uso:
    gunicorn wsgi:application --workers 2 --bind 0.0.0.0:5000
"""
from app import create_app

application = create_app()
