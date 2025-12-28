"""
Report Schemas - Validación para endpoints de reportes
"""

from typing import Dict, List


class GenerateReportSchema:
    """Schema para validar generación de reportes"""
    
    VALID_FORMATS = ['excel', 'json']
    
    @classmethod
    def validate(cls, data: Dict) -> tuple[bool, Dict, List[str]]:
        """
        Validar solicitud de generación de reporte
        
        Returns:
            Tuple (is_valid, validated_data, errors)
        """
        errors = []
        validated = {}
        
        if not data:
            data = {}
        
        # Validar model_id (opcional)
        if 'model_id' in data and data['model_id']:
            validated['model_id'] = str(data['model_id'])
        
        # Validar formato
        format_type = data.get('format', 'excel')
        if format_type not in cls.VALID_FORMATS:
            errors.append(f'format debe ser uno de: {", ".join(cls.VALID_FORMATS)}')
        validated['format'] = format_type
        
        # Validar include_data
        include_data = data.get('include_data', False)
        if not isinstance(include_data, bool):
            include_data = str(include_data).lower() in ('true', '1', 'yes')
        validated['include_data'] = include_data
        
        return len(errors) == 0, validated, errors
