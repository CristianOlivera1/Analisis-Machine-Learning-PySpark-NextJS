"""
Dataset Routes - Gestión de datasets
"""

from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

from app.services.dataset_service import DatasetService
from app.api.schemas.dataset_schemas import (
    UploadDatasetSchema,
    UploadJsonDatasetSchema,
    DatasetResponseSchema
)
from app.utils.validators import validate_file_extension, validate_request_json
from app.utils.exceptions import ValidationError, NotFoundError
from app.utils.decorators import handle_exceptions

datasets_bp = Blueprint('datasets', __name__)


@datasets_bp.route('/upload', methods=['POST'])
@handle_exceptions
def upload_dataset():
    """
    Subir un dataset (CSV o Excel)
    
    Request:
        file: Archivo CSV o Excel
        
    Returns:
        Dataset info con ID generado
    """
    if 'file' not in request.files:
        raise ValidationError('No se proporcionó ningún archivo', field='file')
    
    file = request.files['file']
    
    if file.filename == '':
        raise ValidationError('No se seleccionó ningún archivo', field='file')
    
    # Validar extensión
    if not validate_file_extension(file.filename, current_app.config['ALLOWED_EXTENSIONS']):
        allowed = ', '.join(current_app.config['ALLOWED_EXTENSIONS'])
        raise ValidationError(
            f'Formato no soportado. Formatos permitidos: {allowed}',
            field='file'
        )
    
    # Procesar archivo
    result = DatasetService.upload_file(file)
    
    return jsonify({
        'success': True,
        **DatasetResponseSchema.dump(result)
    }), 201


@datasets_bp.route('/upload-json', methods=['POST'])
@handle_exceptions
def upload_dataset_json():
    """
    Subir dataset desde JSON (localStorage)
    
    Request Body:
        data: Lista de registros
        name: Nombre del dataset (opcional)
        
    Returns:
        Dataset info con ID generado
    """
    data = validate_request_json(request, UploadJsonDatasetSchema)
    
    result = DatasetService.upload_json(
        data=data['data'],
        name=data.get('name')
    )
    
    return jsonify({
        'success': True,
        **DatasetResponseSchema.dump(result)
    }), 201


@datasets_bp.route('', methods=['GET'])
@handle_exceptions
def list_datasets():
    """
    Listar todos los datasets cargados
    
    Returns:
        Lista de datasets con info básica
    """
    datasets = DatasetService.list_all()
    
    return jsonify({
        'datasets': [DatasetResponseSchema.dump_summary(d) for d in datasets]
    })


@datasets_bp.route('/<dataset_id>', methods=['GET'])
@handle_exceptions
def get_dataset(dataset_id: str):
    """
    Obtener información de un dataset
    
    Args:
        dataset_id: ID del dataset
        
    Returns:
        Información detallada del dataset
    """
    dataset = DatasetService.get_by_id(dataset_id)
    
    if not dataset:
        raise NotFoundError('Dataset', dataset_id)
    
    return jsonify(DatasetResponseSchema.dump(dataset))


@datasets_bp.route('/<dataset_id>/preview', methods=['GET'])
@handle_exceptions
def preview_dataset(dataset_id: str):
    """
    Vista previa de los datos
    
    Args:
        dataset_id: ID del dataset
        
    Query Params:
        limit: Número de filas (default: 100)
        offset: Offset para paginación (default: 0)
        
    Returns:
        Datos paginados del dataset
    """
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    # Validar límites
    max_rows = current_app.config['MAX_PREVIEW_ROWS']
    if limit > max_rows:
        limit = max_rows
    
    result = DatasetService.get_preview(dataset_id, limit=limit, offset=offset)
    
    return jsonify(result)


@datasets_bp.route('/<dataset_id>', methods=['DELETE'])
@handle_exceptions
def delete_dataset(dataset_id: str):
    """
    Eliminar un dataset
    
    Args:
        dataset_id: ID del dataset
    """
    DatasetService.delete(dataset_id)
    
    return jsonify({
        'success': True,
        'message': 'Dataset eliminado correctamente'
    })


@datasets_bp.route('/samples', methods=['GET'])
@handle_exceptions
def get_sample_datasets():
    """
    Obtener lista de datasets de ejemplo
    
    Returns:
        Lista de datasets de ejemplo disponibles
    """
    samples = DatasetService.get_available_samples()
    
    return jsonify({'samples': samples})


@datasets_bp.route('/samples/<sample_id>/load', methods=['POST'])
@handle_exceptions
def load_sample_dataset(sample_id: str):
    """
    Cargar un dataset de ejemplo
    
    Args:
        sample_id: ID del dataset de ejemplo
        
    Returns:
        Dataset info
    """
    result = DatasetService.load_sample(sample_id)
    
    return jsonify({
        'success': True,
        **DatasetResponseSchema.dump(result)
    }), 201
