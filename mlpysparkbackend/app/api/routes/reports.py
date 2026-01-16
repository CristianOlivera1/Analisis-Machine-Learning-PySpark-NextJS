"""
Reports Routes - Generación de reportes
"""

from flask import Blueprint, request, jsonify, send_file

from app.services.report_service import ReportService
from app.api.schemas.report_schemas import GenerateReportSchema
from app.utils.validators import validate_request_json
from app.utils.exceptions import ValidationError
from app.utils.decorators import handle_exceptions

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/generate', methods=['POST'])
@handle_exceptions
def generate_report():

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
        file_buffer = ReportService.generate_excel_report(
            model_id=model_id,
            include_data=include_data
        )
        
        if model_id:
            filename = f'model_{model_id[:8]}_report.xlsx'
        else:
            filename = 'models_comparison_report.xlsx'
        
        return send_file(
            file_buffer,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    
    else:
        raise ValidationError(f'Formato {format_type} no soportado', field='format')
