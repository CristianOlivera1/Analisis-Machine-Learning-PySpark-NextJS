"""
Dataset Schemas - Validación de datos para endpoints de datasets
"""

from typing import Dict, List


class DatasetResponseSchema:
    """Schema para serializar respuestas de datasets"""
    
    @staticmethod
    def dump(dataset: Dict) -> Dict:
        """Serializar dataset completo"""
        info = dataset.get('info', {})
        columns_info = info.get('columns', [])
        
        return {
            'id': dataset.get('id') or dataset.get('dataset_id'),
            'name': dataset.get('filename'),
            'file_path': dataset.get('path', ''),
            'rows': info.get('row_count', 0),
            'columns': info.get('column_count', 0),
            'column_names': [col.get('name') for col in columns_info],
            'column_types': {col.get('name'): col.get('type') for col in columns_info},
            'created_at': dataset.get('created_at', '')
        }
    
    @staticmethod
    def dump_summary(dataset: Dict) -> Dict:
        """Serializar resumen de dataset"""
        info = dataset.get('info', {})
        columns_info = info.get('columns', [])
        
        return {
            'id': dataset.get('id'),
            'name': dataset.get('filename'),
            'file_path': dataset.get('path', ''),
            'rows': info.get('row_count', 0),
            'columns': info.get('column_count', 0),
            'column_names': [col.get('name') for col in columns_info],
            'column_types': {col.get('name'): col.get('type') for col in columns_info},
            'created_at': dataset.get('created_at', '')
        }
