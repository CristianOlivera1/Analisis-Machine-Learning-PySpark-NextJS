"""
Dataset Schemas - Validación de datos para endpoints de datasets
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass


class UploadDatasetSchema:
    """Schema para validar subida de archivos"""
    
    @staticmethod
    def validate(data: Dict) -> Dict:
        """Validar datos de subida"""
        errors = {}
        
        # El archivo se valida en el route
        return data if not errors else None


class UploadJsonDatasetSchema:
    """Schema para validar subida de datos JSON"""
    
    REQUIRED_FIELDS = ['data']
    
    @classmethod
    def validate(cls, data: Dict) -> tuple[bool, Dict, List[str]]:
        """
        Validar datos JSON para subida
        
        Returns:
            Tuple (is_valid, validated_data, errors)
        """
        errors = []
        validated = {}
        
        if not data:
            return False, {}, ['No se proporcionaron datos']
        
        # Validar campo data
        if 'data' not in data:
            errors.append('El campo "data" es requerido')
        elif not isinstance(data['data'], list):
            errors.append('El campo "data" debe ser una lista')
        elif len(data['data']) == 0:
            errors.append('El campo "data" no puede estar vacío')
        else:
            validated['data'] = data['data']
        
        # Validar nombre (opcional)
        if 'name' in data:
            if not isinstance(data['name'], str):
                errors.append('El campo "name" debe ser una cadena de texto')
            elif len(data['name']) > 255:
                errors.append('El nombre no puede exceder 255 caracteres')
            else:
                validated['name'] = data['name'].strip()
        
        return len(errors) == 0, validated, errors


class DatasetResponseSchema:
    """Schema para serializar respuestas de datasets"""
    
    @staticmethod
    def dump(dataset: Dict) -> Dict:
        """Serializar dataset completo"""
        return {
            'dataset_id': dataset.get('id'),
            'filename': dataset.get('filename'),
            'created_at': dataset.get('created_at'),
            'info': dataset.get('info', {})
        }
    
    @staticmethod
    def dump_summary(dataset: Dict) -> Dict:
        """Serializar resumen de dataset"""
        info = dataset.get('info', {})
        return {
            'id': dataset.get('id'),
            'filename': dataset.get('filename'),
            'created_at': dataset.get('created_at'),
            'row_count': info.get('row_count', 0),
            'column_count': info.get('column_count', 0)
        }


class ColumnSchema:
    """Schema para información de columnas"""
    
    @staticmethod
    def dump(column: Dict) -> Dict:
        return {
            'name': column.get('name'),
            'type': column.get('type'),
            'spark_type': column.get('spark_type'),
            'nullable': column.get('nullable', True),
            'null_count': column.get('null_count', 0),
            'non_null_count': column.get('non_null_count', 0)
        }
