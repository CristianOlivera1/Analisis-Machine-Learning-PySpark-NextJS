"""
Exploration Schemas - Validación para endpoints de exploración
"""

from typing import Dict, List, Optional


class FilterSchema:
    """Schema para validar filtros de datos"""
    
    VALID_OPERATORS = [
        'equals', 'not_equals', 'greater_than', 'less_than',
        'greater_equal', 'less_equal', 'contains', 'starts_with',
        'ends_with', 'is_null', 'is_not_null', 'in', 'not_in'
    ]
    
    @classmethod
    def validate(cls, data: Dict) -> tuple[bool, Dict, List[str]]:
        """
        Validar esquema de filtros
        
        Returns:
            Tuple (is_valid, validated_data, errors)
        """
        errors = []
        validated = {}
        
        if not data:
            return True, {'filters': [], 'limit': 100}, []
        
        # Validar filtros
        filters = data.get('filters', [])
        if not isinstance(filters, list):
            errors.append('filters debe ser una lista')
        else:
            validated_filters = []
            for i, f in enumerate(filters):
                if not isinstance(f, dict):
                    errors.append(f'Filter {i} debe ser un objeto')
                    continue
                
                # Validar campos del filtro
                if 'column' not in f:
                    errors.append(f'Filter {i}: se requiere campo "column"')
                    continue
                    
                if 'operator' not in f:
                    errors.append(f'Filter {i}: se requiere campo "operator"')
                    continue
                
                if f['operator'] not in cls.VALID_OPERATORS:
                    errors.append(f'Filter {i}: operador "{f["operator"]}" no válido')
                    continue
                
                # El valor es requerido excepto para is_null y is_not_null
                if f['operator'] not in ['is_null', 'is_not_null'] and 'value' not in f:
                    errors.append(f'Filter {i}: se requiere campo "value"')
                    continue
                
                validated_filters.append({
                    'column': str(f['column']),
                    'operator': f['operator'],
                    'value': f.get('value')
                })
            
            validated['filters'] = validated_filters
        
        # Validar límite
        limit = data.get('limit', 100)
        if not isinstance(limit, int):
            try:
                limit = int(limit)
            except (ValueError, TypeError):
                errors.append('limit debe ser un número entero')
                limit = 100
        
        if limit < 1:
            limit = 1
        elif limit > 10000:
            limit = 10000
        
        validated['limit'] = limit
        
        return len(errors) == 0, validated, errors


class ChartRequestSchema:
    """Schema para validar solicitudes de gráficos"""
    
    VALID_CHART_TYPES = ['bar', 'line', 'pie', 'scatter', 'area']
    VALID_AGGREGATIONS = ['sum', 'mean', 'count', 'min', 'max', 'median']
    
    @classmethod
    def validate(cls, data: Dict) -> tuple[bool, Dict, List[str]]:
        """
        Validar solicitud de gráfico
        
        Returns:
            Tuple (is_valid, validated_data, errors)
        """
        errors = []
        validated = {}
        
        if not data:
            return False, {}, ['No se proporcionaron datos']
        
        # Validar tipo de gráfico
        chart_type = data.get('type', 'bar')
        if chart_type not in cls.VALID_CHART_TYPES:
            errors.append(f'Tipo de gráfico "{chart_type}" no válido')
        validated['type'] = chart_type
        
        # Validar columna X (requerido)
        if 'x' not in data:
            errors.append('Se requiere columna X')
        else:
            validated['x'] = str(data['x'])
        
        # Validar columna Y (opcional)
        if 'y' in data:
            validated['y'] = str(data['y'])
        
        # Validar agregación
        aggregation = data.get('aggregation', 'sum')
        if aggregation not in cls.VALID_AGGREGATIONS:
            errors.append(f'Agregación "{aggregation}" no válida')
        validated['aggregation'] = aggregation
        
        # Validar límite
        limit = data.get('limit', 50)
        if not isinstance(limit, int):
            try:
                limit = int(limit)
            except (ValueError, TypeError):
                errors.append('limit debe ser un número entero')
                limit = 50
        
        validated['limit'] = min(max(limit, 1), 1000)
        
        return len(errors) == 0, validated, errors


class HistogramRequestSchema:
    """Schema para validar solicitudes de histograma"""
    
    @classmethod
    def validate(cls, data: Dict) -> tuple[bool, Dict, List[str]]:
        """Validar solicitud de histograma"""
        errors = []
        validated = {}
        
        # Validar columna (requerido)
        if 'column' not in data:
            errors.append('Se requiere columna')
        else:
            validated['column'] = str(data['column'])
        
        # Validar bins
        bins = data.get('bins', 20)
        if not isinstance(bins, int):
            try:
                bins = int(bins)
            except (ValueError, TypeError):
                errors.append('bins debe ser un número entero')
                bins = 20
        
        validated['bins'] = min(max(bins, 1), 100)
        
        return len(errors) == 0, validated, errors
