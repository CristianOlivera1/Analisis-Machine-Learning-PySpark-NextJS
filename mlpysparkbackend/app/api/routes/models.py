"""
Models Routes - Entrenamiento y gestión de modelos ML
"""

from flask import Blueprint, request, jsonify

from app.services.training_service import TrainingService
from app.api.schemas.model_schemas import (
    TrainModelSchema,
    ModelResponseSchema
)
from app.utils.validators import validate_request_json
from app.utils.exceptions import ValidationError
from app.utils.decorators import handle_exceptions

models_bp = Blueprint('models', __name__)


@models_bp.route('/types', methods=['GET'])
@handle_exceptions
def get_model_types():
    """
    Obtener tipos de modelos disponibles
    
    Returns:
        Diccionario con modelos de clasificación, regresión y clustering
    """
    return jsonify(TrainingService.get_available_models())


@models_bp.route('/train', methods=['POST'])
@handle_exceptions
def train_model():
    """
    Entrenar un modelo de ML
    
    Request Body:
        dataset_id: ID del dataset
        model_type: Tipo (classification, regression, clustering)
        algorithm: Algoritmo específico
        features: Lista de columnas predictoras
        target: Columna objetivo (no aplica para clustering)
        params: Parámetros del modelo
        test_size: Proporción de datos de prueba (default: 0.2)
        
    Returns:
        Modelo entrenado con métricas
    """
    data = validate_request_json(request, TrainModelSchema)
    
    # Validaciones adicionales de negocio
    if data['model_type'] in ['classification', 'regression'] and not data.get('target'):
        raise ValidationError(
            'Se requiere target para clasificación y regresión',
            field='target'
        )
    
    if not data.get('features') or len(data['features']) == 0:
        raise ValidationError(
            'Se requiere al menos una feature',
            field='features'
        )
    
    result = TrainingService.train(
        dataset_id=data['dataset_id'],
        model_type=data['model_type'],
        algorithm=data['algorithm'],
        features=data['features'],
        target=data.get('target'),
        params=data.get('params', {}),
        test_size=data.get('test_size', 0.2)
    )
    
    return jsonify({
        'success': True,
        **ModelResponseSchema.dump(result)
    }), 201


@models_bp.route('', methods=['GET'])
@handle_exceptions
def list_models():
    """
    Listar todos los modelos entrenados
    
    Returns:
        Lista de modelos con info básica
    """
    models = TrainingService.list_all()
    
    return jsonify({
        'models': [ModelResponseSchema.dump_summary(m) for m in models]
    })


@models_bp.route('/<model_id>', methods=['DELETE'])
@handle_exceptions
def delete_model(model_id: str):
    """
    Eliminar un modelo
    
    Args:
        model_id: ID del modelo
    """
    TrainingService.delete(model_id)
    
    return jsonify({
        'success': True,
        'message': 'Modelo eliminado correctamente'
    })
