"""
Exploration Routes - Exploracion y analisis de datos
"""

from flask import Blueprint, request, jsonify

from app.services.exploration_service import ExplorationService
from app.utils.exceptions import ValidationError
from app.utils.decorators import handle_exceptions

exploration_bp = Blueprint('exploration', __name__)


@exploration_bp.route('/<dataset_id>/statistics', methods=['GET'])
@handle_exceptions
def get_statistics(dataset_id: str):
    """
    Obtener estadisticas descriptivas del dataset
    
    Args:
        dataset_id: ID del dataset
        
    Returns:
        Estadisticas por columna (media, mediana, std, etc.)
    """
    statistics = ExplorationService.get_statistics(dataset_id)
    
    return jsonify({'statistics': statistics})


@exploration_bp.route('/<dataset_id>/histogram', methods=['GET'])
@handle_exceptions
def get_histogram(dataset_id: str):
    """
    Obtener datos para histograma
    
    Args:
        dataset_id: ID del dataset
        
    Query Params:
        column: Nombre de la columna (requerido)
        bins: Numero de bins (default: 20)
        
    Returns:
        Datos del histograma
    """
    column = request.args.get('column')
    bins = request.args.get('bins', 20, type=int)
    
    if not column:
        raise ValidationError('Se requiere el parametro column', field='column')
    
    if bins < 1 or bins > 100:
        raise ValidationError('bins debe estar entre 1 y 100', field='bins')
    
    result = ExplorationService.get_histogram(dataset_id, column, bins)
    
    return jsonify(result)