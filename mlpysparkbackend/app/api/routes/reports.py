"""
Reports Routes - Generación de reportes
"""

from flask import Blueprint, request, jsonify, send_file

from app.services.report_service import ReportService
from app.api.schemas.report_schemas import GenerateReportSchema
from app.utils.validators import validate_request_json
from app.utils.exceptions import ValidationError, NotFoundError
from app.utils.decorators import handle_exceptions

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/generate', methods=['POST'])
@handle_exceptions
def generate_report():
    """
    Generar reporte de modelo
    
    Request Body:
        model_id: ID del modelo (opcional, si no se proporciona genera reporte de todos)
        format: Formato de salida (excel, json)
        include_data: Incluir datos de ejemplo (default: false)
        
    Returns:
        Archivo de reporte o JSON
    """
    data = validate_request_json(request, GenerateReportSchema)
    
    model_id = data.get('model_id')
    format_type = data.get('format', 'excel')
    include_data = data.get('include_data', False)
    
    if format_type == 'json':
        result = ReportService.generate_json_report(model_id)
        return jsonify({
            'success': True,
            'report': result
        })
    
    elif format_type == 'excel':
        file_buffer, filename = ReportService.generate_excel_report(
            model_id=model_id,
            include_data=include_data
        )
        
        return send_file(
            file_buffer,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    
    else:
        raise ValidationError(f'Formato {format_type} no soportado', field='format')


@reports_bp.route('/export-dataset/<dataset_id>', methods=['GET'])
@handle_exceptions
def export_dataset(dataset_id: str):
    """
    Exportar dataset a archivo
    
    Args:
        dataset_id: ID del dataset
        
    Query Params:
        format: Formato de salida (csv, excel)
        
    Returns:
        Archivo del dataset
    """
    format_type = request.args.get('format', 'csv')
    
    if format_type not in ['csv', 'excel']:
        raise ValidationError(f'Formato {format_type} no soportado', field='format')
    
    file_buffer, filename, mimetype = ReportService.export_dataset(
        dataset_id=dataset_id,
        format_type=format_type
    )
    
    return send_file(
        file_buffer,
        mimetype=mimetype,
        as_attachment=True,
        download_name=filename
    )


@reports_bp.route('/model/<model_id>/metrics', methods=['GET'])
@handle_exceptions
def get_model_metrics_report(model_id: str):
    """
    Obtener reporte de métricas de un modelo
    
    Args:
        model_id: ID del modelo
        
    Returns:
        Métricas detalladas del modelo
    """
    result = ReportService.get_model_metrics_report(model_id)
    
    return jsonify(result)


@reports_bp.route('/summary', methods=['GET'])
@handle_exceptions
def get_summary_report():
    """
    Obtener resumen general del sistema
    
    Returns:
        Estadísticas de datasets y modelos
    """
    result = ReportService.get_summary_report()
    
    return jsonify(result)
