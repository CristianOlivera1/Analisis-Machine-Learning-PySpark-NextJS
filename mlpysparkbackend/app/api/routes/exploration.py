"""
Exploration Routes - Exploración y análisis de datos
"""

from flask import Blueprint, request, jsonify, current_app

from app.services.exploration_service import ExplorationService
from app.api.schemas.exploration_schemas import FilterSchema, ChartRequestSchema
from app.utils.validators import validate_request_json
from app.utils.exceptions import ValidationError, NotFoundError
from app.utils.decorators import handle_exceptions

exploration_bp = Blueprint('exploration', __name__)


@exploration_bp.route('/<dataset_id>/statistics', methods=['GET'])
@handle_exceptions
def get_statistics(dataset_id: str):
    """
    Obtener estadísticas descriptivas del dataset
    
    Args:
        dataset_id: ID del dataset
        
    Returns:
        Estadísticas por columna (media, mediana, std, etc.)
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
        bins: Número de bins (default: 20)
        
    Returns:
        Datos del histograma
    """
    column = request.args.get('column')
    bins = request.args.get('bins', 20, type=int)
    
    if not column:
        raise ValidationError('Se requiere el parámetro column', field='column')
    
    if bins < 1 or bins > 100:
        raise ValidationError('bins debe estar entre 1 y 100', field='bins')
    
    result = ExplorationService.get_histogram(dataset_id, column, bins)
    
    return jsonify(result)


@exploration_bp.route('/<dataset_id>/chart', methods=['GET'])
@handle_exceptions
def get_chart_data(dataset_id: str):
    """
    Obtener datos para gráficos
    
    Args:
        dataset_id: ID del dataset
        
    Query Params:
        type: Tipo de gráfico (bar, line, pie)
        x: Columna para eje X (requerido)
        y: Columna para eje Y (opcional)
        aggregation: Tipo de agregación (sum, mean, count, min, max)
        limit: Límite de puntos (default: 50)
        
    Returns:
        Datos para el gráfico
    """
    chart_type = request.args.get('type', 'bar')
    x_column = request.args.get('x')
    y_column = request.args.get('y')
    aggregation = request.args.get('aggregation', 'sum')
    limit = request.args.get('limit', 50, type=int)
    
    if not x_column:
        raise ValidationError('Se requiere el parámetro x', field='x')
    
    # Validar límite
    max_points = current_app.config['MAX_CHART_POINTS']
    if limit > max_points:
        limit = max_points
    
    result = ExplorationService.get_chart_data(
        dataset_id=dataset_id,
        chart_type=chart_type,
        x_column=x_column,
        y_column=y_column,
        aggregation=aggregation,
        limit=limit
    )
    
    return jsonify(result)


@exploration_bp.route('/<dataset_id>/correlation', methods=['GET'])
@handle_exceptions
def get_correlation(dataset_id: str):
    """
    Obtener matriz de correlación
    
    Args:
        dataset_id: ID del dataset
        
    Returns:
        Matriz de correlación para columnas numéricas
    """
    result = ExplorationService.get_correlation_matrix(dataset_id)
    
    return jsonify(result)


@exploration_bp.route('/<dataset_id>/filter', methods=['POST'])
@handle_exceptions
def filter_dataset(dataset_id: str):
    """
    Filtrar dataset con condiciones
    
    Args:
        dataset_id: ID del dataset
        
    Request Body:
        filters: Lista de filtros [{column, operator, value}]
        limit: Límite de filas (default: 100)
        
    Returns:
        Datos filtrados
    """
    data = validate_request_json(request, FilterSchema)
    
    filters = data.get('filters', [])
    limit = data.get('limit', 100)
    
    result = ExplorationService.filter_data(dataset_id, filters, limit)
    
    return jsonify(result)


@exploration_bp.route('/<dataset_id>/describe', methods=['GET'])
@handle_exceptions
def describe_column(dataset_id: str):
    """
    Descripción detallada de una columna
    
    Args:
        dataset_id: ID del dataset
        
    Query Params:
        column: Nombre de la columna
        
    Returns:
        Descripción estadística de la columna
    """
    column = request.args.get('column')
    
    if not column:
        raise ValidationError('Se requiere el parámetro column', field='column')
    
    result = ExplorationService.describe_column(dataset_id, column)
    
    return jsonify(result)


@exploration_bp.route('/<dataset_id>/missing', methods=['GET'])
@handle_exceptions
def get_missing_values(dataset_id: str):
    """
    Obtener resumen de valores faltantes
    
    Args:
        dataset_id: ID del dataset
        
    Returns:
        Resumen de valores nulos por columna
    """
    result = ExplorationService.get_missing_values_summary(dataset_id)
    
    return jsonify(result)
