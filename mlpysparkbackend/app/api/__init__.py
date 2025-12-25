"""
API Module - Registro de Blueprints
"""

from flask import Flask


def register_blueprints(app: Flask):
    """Registrar todos los blueprints de la API"""
    
    from app.api.routes.health import health_bp
    from app.api.routes.datasets import datasets_bp
    from app.api.routes.exploration import exploration_bp
    from app.api.routes.models import models_bp
    from app.api.routes.reports import reports_bp
    
    # Registrar con prefijo /api
    app.register_blueprint(health_bp, url_prefix='/api')
    app.register_blueprint(datasets_bp, url_prefix='/api/datasets')
    app.register_blueprint(exploration_bp, url_prefix='/api/datasets')
    app.register_blueprint(models_bp, url_prefix='/api/models')
    app.register_blueprint(reports_bp, url_prefix='/api/reports')
