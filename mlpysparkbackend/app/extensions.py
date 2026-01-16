from flask_cors import CORS

cors = CORS()

def init_extensions(app):
    """Inicializar todas las extensiones"""
    
    cors.init_app(app, resources={
        r"/api/*": {
            "origins": app.config.get('CORS_ORIGINS', '*'),
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Inicializar carpetas
    from app.config import Config
    Config.init_folders()
