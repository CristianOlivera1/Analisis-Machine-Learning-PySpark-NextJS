"""
Decorators - Decoradores para rutas
"""

from functools import wraps
from flask import jsonify
import logging
import traceback

from app.utils.exceptions import BaseAPIException, InternalServerError

logger = logging.getLogger(__name__)


def handle_exceptions(f):
    """
    Decorador para manejar excepciones en endpoints
    
    Captura excepciones y retorna respuestas JSON apropiadas
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except BaseAPIException as e:
            # Excepciones personalizadas de la API
            logger.warning(f"API Exception in {f.__name__}: {e.message}")
            response = jsonify(e.to_dict())
            response.status_code = e.status_code
            return response
        except Exception as e:
            # Excepciones no manejadas
            logger.error(f"Unhandled exception in {f.__name__}: {str(e)}")
            logger.error(traceback.format_exc())
            
            error = InternalServerError(
                message=f"Error interno: {str(e)}" if logger.level == logging.DEBUG else "Error interno del servidor"
            )
            response = jsonify(error.to_dict())
            response.status_code = error.status_code
            return response
    
    return decorated_function


def require_dataset(f):
    """
    Decorador para validar que existe un dataset
    
    Espera que el endpoint tenga un parámetro dataset_id
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from app.core.storage import DatasetStorage
        from app.utils.exceptions import NotFoundError
        
        dataset_id = kwargs.get('dataset_id')
        if not dataset_id:
            raise NotFoundError('Dataset ID', 'missing')
        
        if not DatasetStorage.exists(dataset_id):
            raise NotFoundError('Dataset', dataset_id)
        
        return f(*args, **kwargs)
    
    return decorated_function


def require_model(f):
    """
    Decorador para validar que existe un modelo
    
    Espera que el endpoint tenga un parámetro model_id
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from app.core.storage import ModelStorage
        from app.utils.exceptions import NotFoundError
        
        model_id = kwargs.get('model_id')
        if not model_id:
            raise NotFoundError('Model ID', 'missing')
        
        if not ModelStorage.exists(model_id):
            raise NotFoundError('Model', model_id)
        
        return f(*args, **kwargs)
    
    return decorated_function


def log_execution_time(f):
    """
    Decorador para loggear tiempo de ejecución
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        import time
        start_time = time.time()
        
        result = f(*args, **kwargs)
        
        execution_time = time.time() - start_time
        logger.info(f"{f.__name__} executed in {execution_time:.2f}s")
        
        return result
    
    return decorated_function
