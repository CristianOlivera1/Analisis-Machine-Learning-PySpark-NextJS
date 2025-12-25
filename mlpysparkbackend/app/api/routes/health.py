"""
Health Check Routes
"""

from flask import Blueprint, jsonify
from datetime import datetime

from app.core.spark_manager import SparkManager
from app.core.storage import DatasetStorage, ModelStorage

health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    Verificar estado del servidor
    
    Returns:
        JSON con estado del servidor, Spark y estadísticas
    """
    spark_status = "running" if SparkManager.is_initialized() else "not initialized"
    
    try:
        # Verificar que Spark responde
        spark = SparkManager.get_session()
        if spark:
            spark.sql("SELECT 1")
        else:
            spark_status = "not available"
    except Exception as e:
        spark_status = f"error: {str(e)}"
    
    return jsonify({
        'status': 'ok',
        'spark_status': spark_status,
        'datasets_loaded': DatasetStorage.count(),
        'models_trained': ModelStorage.count(),
        'timestamp': datetime.now().isoformat()
    })


@health_bp.route('/health/spark', methods=['GET'])
def spark_status():
    """Obtener estado detallado de Spark"""
    try:
        spark = SparkManager.get_session()
        if not spark:
            return jsonify({
                'status': 'not initialized',
                'details': None
            })
        
        return jsonify({
            'status': 'running',
            'details': {
                'app_name': spark.sparkContext.appName,
                'master': spark.sparkContext.master,
                'version': spark.version,
                'default_parallelism': spark.sparkContext.defaultParallelism
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500
