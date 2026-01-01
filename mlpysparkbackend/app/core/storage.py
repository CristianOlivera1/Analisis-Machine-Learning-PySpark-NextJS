"""
Storage - Almacenamiento en memoria para datasets y modelos
Implementa patrón Repository
"""

from typing import Dict, Optional, List, Any
from datetime import datetime
from threading import Lock
import logging

logger = logging.getLogger(__name__)


class BaseStorage:
    """Clase base para almacenamiento en memoria"""
    
    _data: Dict[str, Dict] = {}
    _lock: Lock = Lock()
    
    @classmethod
    def get(cls, id: str) -> Optional[Dict]:
        """Obtener item por ID"""
        return cls._data.get(id)
    
    @classmethod
    def get_all(cls) -> List[Dict]:
        """Obtener todos los items"""
        return list(cls._data.values())
    
    @classmethod
    def add(cls, id: str, data: Dict) -> None:
        """Agregar nuevo item"""
        with cls._lock:
            cls._data[id] = data
    
    @classmethod
    def update(cls, id: str, data: Dict) -> bool:
        """Actualizar item existente"""
        with cls._lock:
            if id in cls._data:
                cls._data[id].update(data)
                return True
            return False
    
    @classmethod
    def delete(cls, id: str) -> bool:
        """Eliminar item"""
        with cls._lock:
            if id in cls._data:
                del cls._data[id]
                return True
            return False
    
    @classmethod
    def exists(cls, id: str) -> bool:
        """Verificar si existe un item"""
        return id in cls._data
    
    @classmethod
    def count(cls) -> int:
        """Contar items"""
        return len(cls._data)
    
    @classmethod
    def clear(cls) -> None:
        """Limpiar todo el almacenamiento"""
        with cls._lock:
            cls._data.clear()


class DatasetStorage(BaseStorage):
    """Almacenamiento de datasets"""
    
    _data: Dict[str, Dict] = {}
    _lock: Lock = Lock()
    
    @classmethod
    def add_dataset(
        cls,
        id: str,
        dataframe: Any,
        filename: str,
        path: Optional[str],
        info: Dict
    ) -> None:
        """
        Agregar un dataset al almacenamiento
        
        Args:
            id: ID único del dataset
            dataframe: Spark DataFrame
            filename: Nombre del archivo
            path: Ruta del archivo (si existe)
            info: Información del dataset
        """
        cls.add(id, {
            'id': id,
            'dataframe': dataframe,
            'filename': filename,
            'path': path,
            'created_at': datetime.now().isoformat(),
            'info': info
        })
        logger.info(f"Dataset added: {id} ({filename})")
    
    @classmethod
    def get_dataframe(cls, id: str) -> Optional[Any]:
        """Obtener el DataFrame de un dataset"""
        dataset = cls.get(id)
        return dataset.get('dataframe') if dataset else None
    
    @classmethod
    def get_info(cls, id: str) -> Optional[Dict]:
        """Obtener información de un dataset"""
        dataset = cls.get(id)
        if not dataset:
            return None
        return {
            'id': dataset['id'],
            'filename': dataset['filename'],
            'created_at': dataset['created_at'],
            'info': dataset['info']
        }
    
    @classmethod
    def list_all(cls) -> List[Dict]:
        """Listar todos los datasets (sin DataFrame)"""
        return [
            {
                'id': d['id'],
                'filename': d['filename'],
                'created_at': d['created_at'],
                'info': d['info']
            }
            for d in cls._data.values()
        ]


class ModelStorage(BaseStorage):
    """Almacenamiento de modelos ML"""
    
    _data: Dict[str, Dict] = {}
    _lock: Lock = Lock()
    
    @classmethod
    def add_model(
        cls,
        id: str,
        pipeline_model: Any,
        model_type: str,
        algorithm: str,
        features: List[str],
        target: Optional[str],
        params: Dict,
        metrics: Dict,
        dataset_id: str,
        train_size: int,
        test_size: int
    ) -> None:
        """
        Agregar un modelo al almacenamiento
        
        Args:
            id: ID único del modelo
            pipeline_model: Pipeline entrenado de Spark
            model_type: Tipo de modelo (classification, regression)
            algorithm: Algoritmo utilizado
            features: Lista de features
            target: Columna objetivo
            params: Parámetros del modelo
            metrics: Métricas de evaluación
            dataset_id: ID del dataset utilizado
            train_size: Tamaño del conjunto de entrenamiento
            test_size: Tamaño del conjunto de prueba
        """
        cls.add(id, {
            'id': id,
            'pipeline_model': pipeline_model,
            'model_type': model_type,
            'algorithm': algorithm,
            'features': features,
            'target': target,
            'params': params,
            'metrics': metrics,
            'dataset_id': dataset_id,
            'train_size': train_size,
            'test_size': test_size,
            'created_at': datetime.now().isoformat()
        })
        logger.info(f"Model added: {id} ({model_type}/{algorithm})")
    
    @classmethod
    def get_pipeline(cls, id: str) -> Optional[Any]:
        """Obtener el pipeline de un modelo"""
        model = cls.get(id)
        return model.get('pipeline_model') if model else None
    
    @classmethod
    def get_info(cls, id: str) -> Optional[Dict]:
        """Obtener información de un modelo (sin pipeline)"""
        model = cls.get(id)
        if not model:
            return None
        return {k: v for k, v in model.items() if k != 'pipeline_model'}
    
    @classmethod
    def list_all(cls) -> List[Dict]:
        """Listar todos los modelos (sin pipeline)"""
        return [
            {k: v for k, v in m.items() if k != 'pipeline_model'}
            for m in cls._data.values()
        ]


class TrainingResultsStorage(BaseStorage):
    """Almacenamiento de resultados de entrenamiento"""
    
    _data: Dict[str, Dict] = {}
    _lock: Lock = Lock()
    
    @classmethod
    def add_result(cls, model_id: str, result: Dict) -> None:
        """Agregar resultado de entrenamiento"""
        cls.add(model_id, {
            'model_id': model_id,
            **result,
            'timestamp': datetime.now().isoformat()
        })
