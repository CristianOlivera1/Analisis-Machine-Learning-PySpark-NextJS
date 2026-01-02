import os
import sys
import logging

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.config import config_by_name

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Determinar entorno
env = os.getenv('FLASK_ENV', 'development')

app = create_app(config_by_name.get(env, config_by_name['default']))

if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("ML PySpark Backend Server")
    logger.info("=" * 60)
    logger.info(f"Environment: {env}")
    logger.info(f"Debug Mode: {app.config['DEBUG']}")
    logger.info(f"Upload Folder: {app.config['UPLOAD_FOLDER']}")
    logger.info("=" * 60)
    
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    
    logger.info(f"Starting server on http://{host}:{port}")
    logger.info("=" * 60)
    
    # Iniciar servidor
    app.run(
        host=host,
        port=port,
        debug=app.config['DEBUG']
    )
