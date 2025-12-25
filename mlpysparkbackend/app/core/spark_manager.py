"""
Spark Manager - Gestión centralizada de Spark Session
Implementa patrón Singleton para la sesión de Spark
"""

from typing import Optional, Dict, Any
import logging
import os
import sys
from threading import Lock

# Configurar para Windows antes de importar PySpark
if sys.platform == 'win32':
    os.environ['PYSPARK_PYTHON'] = sys.executable
    os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

from pyspark.sql import SparkSession

logger = logging.getLogger(__name__)


class SparkManager:
    """
    Gestor centralizado de Spark Session
    Implementa patrón Singleton thread-safe
    """
    
    _instance: Optional[SparkSession] = None
    _lock: Lock = Lock()
    _config: Dict[str, Any] = {}
    _initialized: bool = False
    
    @classmethod
    def initialize(cls, config: Dict[str, Any]) -> None:
        """
        Inicializar el SparkManager con configuración
        
        Args:
            config: Diccionario de configuración de Flask
        """
        cls._config = {
            'app_name': config.get('SPARK_APP_NAME', 'MLPySparkApp'),
            'driver_memory': config.get('SPARK_DRIVER_MEMORY', '4g'),
            'executor_memory': config.get('SPARK_EXECUTOR_MEMORY', '4g'),
        }
        logger.info("SparkManager initialized with config: %s", cls._config)
    
    @classmethod
    def get_session(cls) -> SparkSession:
        """
        Obtener la sesión de Spark (lazy initialization)
        
        Returns:
            SparkSession activa
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls._create_session()
                    cls._initialized = True
        
        return cls._instance
    
    @classmethod
    def _create_session(cls) -> SparkSession:
        """
        Crear una nueva sesión de Spark
        
        Returns:
            Nueva SparkSession
        """
        try:
            builder = SparkSession.builder \
                .appName(cls._config.get('app_name', 'MLPySparkApp')) \
                .master("local[*]") \
                .config("spark.driver.memory", cls._config.get('driver_memory', '4g')) \
                .config("spark.executor.memory", cls._config.get('executor_memory', '4g')) \
                .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
                .config("spark.sql.session.timeZone", "UTC") \
                .config("spark.driver.extraJavaOptions", "-Duser.timezone=UTC") \
                .config("spark.executor.extraJavaOptions", "-Duser.timezone=UTC") \
                .config("spark.driver.host", "localhost")
            
            # Configuraciones adicionales para Windows
            if sys.platform == 'win32':
                builder = builder.config("spark.sql.warehouse.dir", "file:///C:/temp/spark-warehouse")
            
            session = builder.getOrCreate()
            
            # Configurar nivel de log
            session.sparkContext.setLogLevel("WARN")
            
            logger.info("Spark session created successfully")
            return session
            
        except Exception as e:
            logger.error("Failed to create Spark session: %s", str(e))
            raise
    
    @classmethod
    def is_initialized(cls) -> bool:
        """Verificar si Spark está inicializado"""
        return cls._initialized and cls._instance is not None
    
    @classmethod
    def stop(cls) -> None:
        """Detener la sesión de Spark"""
        with cls._lock:
            if cls._instance is not None:
                try:
                    cls._instance.stop()
                    logger.info("Spark session stopped")
                except Exception as e:
                    logger.error("Error stopping Spark session: %s", str(e))
                finally:
                    cls._instance = None
                    cls._initialized = False
    
    @classmethod
    def restart(cls) -> SparkSession:
        """Reiniciar la sesión de Spark"""
        cls.stop()
        return cls.get_session()
    
    @classmethod
    def get_status(cls) -> Dict[str, Any]:
        """
        Obtener estado de Spark
        
        Returns:
            Diccionario con información de estado
        """
        if not cls.is_initialized():
            return {
                'status': 'not_initialized',
                'details': None
            }
        
        try:
            session = cls._instance
            return {
                'status': 'running',
                'details': {
                    'app_name': session.sparkContext.appName,
                    'app_id': session.sparkContext.applicationId,
                    'master': session.sparkContext.master,
                    'version': session.version,
                    'default_parallelism': session.sparkContext.defaultParallelism,
                    'ui_web_url': session.sparkContext.uiWebUrl
                }
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
