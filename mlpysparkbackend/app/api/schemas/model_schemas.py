"""
Model Schemas - Validación para endpoints de modelos ML
"""

from typing import Dict, List


class TrainModelSchema:
    """Schema para validar solicitudes de entrenamiento"""
    
    VALID_MODEL_TYPES = ['classification', 'regression', 'clustering']
    
    VALID_ALGORITHMS = {
        'classification': [
            'logistic_regression', 'decision_tree', 'random_forest', 'gbt',
            'naive_bayes', 'linear_svc'
        ],
        'regression': [
            'linear_regression', 'decision_tree_reg', 'random_forest_reg', 'gbt_reg'
        ],
        'clustering': [
            'kmeans', 'bisecting_kmeans', 'gaussian_mixture'
        ]
    }
    
    @classmethod
    def validate(cls, data: Dict) -> tuple[bool, Dict, List[str]]:
        """
        Validar solicitud de entrenamiento
        
        Returns:
            Tuple (is_valid, validated_data, errors)
        """
        errors = []
        validated = {}
        
        if not data:
            return False, {}, ['No se proporcionaron datos']
        
        # Validar dataset_id (requerido)
        if 'dataset_id' not in data:
            errors.append('Se requiere dataset_id')
        else:
            validated['dataset_id'] = str(data['dataset_id'])
        
        # Validar model_type (requerido)
        if 'model_type' not in data:
            errors.append('Se requiere model_type')
        elif data['model_type'] not in cls.VALID_MODEL_TYPES:
            errors.append(f'model_type debe ser uno de: {", ".join(cls.VALID_MODEL_TYPES)}')
        else:
            validated['model_type'] = data['model_type']
        
        # Validar algorithm (requerido)
        if 'algorithm' not in data:
            errors.append('Se requiere algorithm')
        else:
            model_type = data.get('model_type')
            if model_type and model_type in cls.VALID_ALGORITHMS:
                if data['algorithm'] not in cls.VALID_ALGORITHMS[model_type]:
                    valid_algs = ', '.join(cls.VALID_ALGORITHMS[model_type])
                    errors.append(f'algorithm debe ser uno de: {valid_algs}')
            validated['algorithm'] = data['algorithm']
        
        # Validar features (requerido)
        if 'features' not in data:
            errors.append('Se requiere features')
        elif not isinstance(data['features'], list):
            errors.append('features debe ser una lista')
        elif len(data['features']) == 0:
            errors.append('features no puede estar vacío')
        else:
            validated['features'] = [str(f) for f in data['features']]
        
        # Validar target (requerido para clasificación y regresión)
        model_type = data.get('model_type')
        if model_type in ['classification', 'regression']:
            if 'target' not in data or not data['target']:
                errors.append(f'Se requiere target para {model_type}')
            else:
                validated['target'] = str(data['target'])
        elif 'target' in data:
            validated['target'] = str(data['target']) if data['target'] else None
        
        # Validar params (opcional)
        params = data.get('params', {})
        if not isinstance(params, dict):
            errors.append('params debe ser un objeto')
            params = {}
        validated['params'] = cls._validate_params(params, data.get('algorithm', ''))
        
        # Validar test_size
        test_size = data.get('test_size', 0.2)
        if not isinstance(test_size, (int, float)):
            errors.append('test_size debe ser un número')
            test_size = 0.2
        elif test_size <= 0 or test_size >= 1:
            errors.append('test_size debe estar entre 0 y 1')
            test_size = 0.2
        validated['test_size'] = float(test_size)
        
        return len(errors) == 0, validated, errors
    
    @classmethod
    def _validate_params(cls, params: Dict, algorithm: str) -> Dict:
        """Validar y limpiar parámetros del modelo"""
        validated = {}
        
        # Parámetros comunes
        if 'maxIter' in params:
            validated['maxIter'] = max(1, min(int(params['maxIter']), 1000))
        
        if 'regParam' in params:
            validated['regParam'] = max(0.0, float(params['regParam']))
        
        if 'maxDepth' in params:
            validated['maxDepth'] = max(1, min(int(params['maxDepth']), 30))
        
        if 'numTrees' in params:
            validated['numTrees'] = max(1, min(int(params['numTrees']), 200))
        
        if 'k' in params:  # Para clustering
            validated['k'] = max(2, min(int(params['k']), 100))
        
        if 'elasticNetParam' in params:
            validated['elasticNetParam'] = max(0.0, min(float(params['elasticNetParam']), 1.0))
        
        return validated


class ModelResponseSchema:
    """Schema para serializar respuestas de modelos"""
    
    @staticmethod
    def dump(model: Dict) -> Dict:
        """Serializar modelo completo"""
        return {
            'model_id': model.get('id'),
            'model_type': model.get('model_type'),
            'algorithm': model.get('algorithm'),
            'features': model.get('features', []),
            'target': model.get('target'),
            'params': model.get('params', {}),
            'metrics': model.get('metrics', {}),
            'created_at': model.get('created_at'),
            'dataset_id': model.get('dataset_id'),
            'train_size': model.get('train_size', 0),
            'test_size': model.get('test_size', 0)
        }
    
    @staticmethod
    def dump_summary(model: Dict) -> Dict:
        """Serializar resumen de modelo"""
        return {
            'id': model.get('id'),
            'model_type': model.get('model_type'),
            'algorithm': model.get('algorithm'),
            'features': model.get('features', []),
            'target': model.get('target'),
            'created_at': model.get('created_at'),
            'metrics': model.get('metrics', {})
        }
