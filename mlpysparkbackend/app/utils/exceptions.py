"""
Custom Exceptions
"""


class BaseAPIException(Exception):
    """Excepción base para la API"""
    
    status_code = 500
    message = "Error interno del servidor"
    
    def __init__(self, message=None, status_code=None, payload=None):
        super().__init__()
        if message is not None:
            self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload
    
    def to_dict(self):
        rv = dict(self.payload or ())
        rv['error'] = self.message
        return rv


class ValidationError(BaseAPIException):
    """Error de validación (400)"""
    
    status_code = 400
    
    def __init__(self, message="Error de validación", field=None, **kwargs):
        super().__init__(message, **kwargs)
        self.field = field
    
    def to_dict(self):
        rv = super().to_dict()
        if self.field:
            rv['field'] = self.field
        return rv


class NotFoundError(BaseAPIException):
    """Recurso no encontrado (404)"""
    
    status_code = 404
    
    def __init__(self, resource_type="Recurso", resource_id=None, **kwargs):
        message = f"{resource_type} no encontrado"
        if resource_id:
            message += f": {resource_id}"
        super().__init__(message, **kwargs)


class ConflictError(BaseAPIException):
    """Conflicto (409)"""
    
    status_code = 409
    message = "El recurso ya existe"


class UnauthorizedError(BaseAPIException):
    """No autorizado (401)"""
    
    status_code = 401
    message = "No autorizado"


class ForbiddenError(BaseAPIException):
    """Prohibido (403)"""
    
    status_code = 403
    message = "Acceso prohibido"


class BadRequestError(BaseAPIException):
    """Solicitud incorrecta (400)"""
    
    status_code = 400
    message = "Solicitud incorrecta"


class InternalServerError(BaseAPIException):
    """Error interno del servidor (500)"""
    
    status_code = 500
    message = "Error interno del servidor"


def register_error_handlers(app):
    """Registrar manejadores de errores globales"""
    
    @app.errorhandler(BaseAPIException)
    def handle_api_exception(error):
        """Manejar excepciones personalizadas de la API"""
        from flask import jsonify
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """Manejar 404"""
        from flask import jsonify
        return jsonify({'error': 'Endpoint no encontrado'}), 404
    
    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        """Manejar 405"""
        from flask import jsonify
        return jsonify({'error': 'Método no permitido'}), 405
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        """Manejar 500"""
        from flask import jsonify
        import logging
        logging.error(f"Internal error: {error}")
        return jsonify({'error': 'Error interno del servidor'}), 500
