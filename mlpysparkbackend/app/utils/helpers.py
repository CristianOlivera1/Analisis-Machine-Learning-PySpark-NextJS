"""
Helpers - Funciones auxiliares
"""

from typing import Any, Dict, List
import pandas as pd
from pyspark.sql import DataFrame
from pyspark.sql.types import StringType, IntegerType, LongType, DoubleType, FloatType, BooleanType, DateType, TimestampType


def get_column_type(dtype) -> str:
    """
    Convertir tipo de Spark a tipo legible
    
    Args:
        dtype: Tipo de datos de Spark
        
    Returns:
        Tipo en formato string
    """
    dtype_str = str(dtype)
    
    if isinstance(dtype, StringType) or 'string' in dtype_str.lower():
        return 'string'
    elif isinstance(dtype, (IntegerType, LongType)) or 'int' in dtype_str.lower() or 'long' in dtype_str.lower():
        return 'integer'
    elif isinstance(dtype, (DoubleType, FloatType)) or 'double' in dtype_str.lower() or 'float' in dtype_str.lower() or 'decimal' in dtype_str.lower():
        return 'numeric'
    elif isinstance(dtype, BooleanType) or 'boolean' in dtype_str.lower():
        return 'boolean'
    elif isinstance(dtype, (DateType, TimestampType)) or 'date' in dtype_str.lower() or 'timestamp' in dtype_str.lower():
        return 'datetime'
    else:
        return 'unknown'


def dataframe_to_json(df: DataFrame, limit: int = 1000) -> List[Dict]:
    """
    Convertir DataFrame de Spark a lista de diccionarios
    
    Args:
        df: Spark DataFrame
        limit: Número máximo de filas
        
    Returns:
        Lista de diccionarios con los datos
    """
    pdf = df.limit(limit).toPandas()
    
    # Convertir NaN y NaT a None para JSON
    pdf = pdf.where(pd.notnull(pdf), None)
    
    return pdf.to_dict(orient='records')


def safe_float(value: Any) -> float:
    """
    Convertir valor a float de forma segura
    
    Args:
        value: Valor a convertir
        
    Returns:
        Float o None
    """
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def safe_int(value: Any) -> int:
    """
    Convertir valor a int de forma segura
    
    Args:
        value: Valor a convertir
        
    Returns:
        Int o None
    """
    if value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def clean_dict(d: Dict) -> Dict:
    """
    Limpiar diccionario eliminando valores None
    
    Args:
        d: Diccionario a limpiar
        
    Returns:
        Diccionario limpio
    """
    return {k: v for k, v in d.items() if v is not None}


def format_bytes(bytes_value: int) -> str:
    """
    Formatear bytes a formato legible
    
    Args:
        bytes_value: Número de bytes
        
    Returns:
        String formateado (ej: "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"


def truncate_string(s: str, max_length: int = 100) -> str:
    """
    Truncar string si excede longitud máxima
    
    Args:
        s: String a truncar
        max_length: Longitud máxima
        
    Returns:
        String truncado
    """
    if not s:
        return s
    
    if len(s) <= max_length:
        return s
    
    return s[:max_length - 3] + '...'
