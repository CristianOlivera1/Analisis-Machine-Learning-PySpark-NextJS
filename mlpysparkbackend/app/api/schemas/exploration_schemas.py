"""
Exploration Schemas - Validación para endpoints de exploración
"""

from typing import Dict, List


class HistogramRequestSchema:
    """Schema para validar solicitudes de histograma"""
    
    @classmethod
    def validate(cls, data: Dict) -> tuple[bool, Dict, List[str]]:
        """Validar solicitud de histograma"""
        errors = []
        validated = {}
        
        if 'column' not in data:
            errors.append('Se requiere columna')
        else:
            validated['column'] = str(data['column'])
        
        bins = data.get('bins', 20)
        if not isinstance(bins, int):
            try:
                bins = int(bins)
            except (ValueError, TypeError):
                errors.append('bins debe ser un número entero')
                bins = 20
        
        validated['bins'] = min(max(bins, 1), 100)
        
        return len(errors) == 0, validated, errors
