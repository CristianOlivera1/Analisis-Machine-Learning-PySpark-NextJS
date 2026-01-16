from flask import Flask
from flask_cors import CORS

from app.config import Config
from app.extensions import init_extensions
from app.api import register_blueprints
from app.core.spark_manager import SparkManager
from app.utils.exceptions import register_error_handlers


def create_app(config_class=Config):

    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Inicializar extensiones
    init_extensions(app)
    
    # Registrar blueprints (rutas)
    register_blueprints(app)
    
    # Registrar manejadores de errores
    register_error_handlers(app)
    
    # Inicializar Spark Manager
    with app.app_context():
        SparkManager.initialize(app.config)
    
    return app
