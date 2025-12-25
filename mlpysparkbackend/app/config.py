"""
Configuración de la aplicación
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Directorio base
BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    """Configuración base"""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # Carpetas de almacenamiento
    UPLOAD_FOLDER = Path(os.getenv('UPLOAD_FOLDER', BASE_DIR / 'storage' / 'uploads'))
    MODELS_FOLDER = Path(os.getenv('MODELS_FOLDER', BASE_DIR / 'storage' / 'models'))
    REPORTS_FOLDER = Path(os.getenv('REPORTS_FOLDER', BASE_DIR / 'storage' / 'reports'))
    
    # Límites
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 100 * 1024 * 1024))  # 100MB
    MAX_PREVIEW_ROWS = int(os.getenv('MAX_PREVIEW_ROWS', 1000))
    MAX_CHART_POINTS = int(os.getenv('MAX_CHART_POINTS', 10000))
    
    # Spark
    SPARK_APP_NAME = os.getenv('SPARK_APP_NAME', 'MLPySparkApp')
    SPARK_DRIVER_MEMORY = os.getenv('SPARK_DRIVER_MEMORY', '4g')
    SPARK_EXECUTOR_MEMORY = os.getenv('SPARK_EXECUTOR_MEMORY', '4g')
    
    # Formatos soportados
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
    
    @classmethod
    def init_folders(cls):
        """Crear carpetas necesarias si no existen"""
        for folder in [cls.UPLOAD_FOLDER, cls.MODELS_FOLDER, cls.REPORTS_FOLDER]:
            folder.mkdir(parents=True, exist_ok=True)


class DevelopmentConfig(Config):
    """Configuración de desarrollo"""
    DEBUG = True


class ProductionConfig(Config):
    """Configuración de producción"""
    DEBUG = False
    
    
class TestingConfig(Config):
    """Configuración de testing"""
    TESTING = True
    DEBUG = True


# Mapeo de configuraciones
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
