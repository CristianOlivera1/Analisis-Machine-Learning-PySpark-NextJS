import os
from typing import Any, Dict, Set
from werkzeug.datastructures import FileStorage
from flask import Request

from app.utils.exceptions import ValidationError


def validate_file_extension(filename: str, allowed_extensions: Set[str]) -> bool:
    """
    Validar extensión de archivo
    
    Args:
        filename: Nombre del archivo
        allowed_extensions: Set de extensiones permitidas
        
    Returns:
        True si la extensión es válida
    """
    if not filename:
        return False
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def validate_file_size(file: FileStorage, max_size: int) -> bool:
    """
    Validar tamaño de archivo
    
    Args:
        file: Archivo a validar
        max_size: Tamaño máximo en bytes
        
    Returns:
        True si el tamaño es válido
    """
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    return size <= max_size


def validate_request_json(request: Request, schema_class: Any) -> Dict:
    """
    Validar JSON de request usando un schema
    
    Args:
        request: Request de Flask
        schema_class: Clase de schema para validación
        
    Returns:
        Datos validados
        
    Raises:
        ValidationError: Si la validación falla
    """
    data = request.get_json()
    
    if not data:
        raise ValidationError("No se proporcionaron datos")
    
    # Si el schema tiene método validate
    if hasattr(schema_class, 'validate'):
        is_valid, validated_data, errors = schema_class.validate(data)
        
        if not is_valid:
            error_message = '; '.join(errors) if isinstance(errors, list) else str(errors)
            raise ValidationError(error_message)
        
        return validated_data
    
    return data


def validate_dataset_id(dataset_id: str) -> str:
    """
    Validar formato de ID de dataset
    
    Args:
        dataset_id: ID a validar
        
    Returns:
        ID validado
        
    Raises:
        ValidationError: Si el ID no es válido
    """
    if not dataset_id:
        raise ValidationError("ID de dataset requerido")
    
    if not isinstance(dataset_id, str):
        raise ValidationError("ID de dataset debe ser una cadena")
    
    return dataset_id.strip()


def validate_model_id(model_id: str) -> str:
    """
    Validar formato de ID de modelo
    
    Args:
        model_id: ID a validar
        
    Returns:
        ID validado
        
    Raises:
        ValidationError: Si el ID no es válido
    """
    if not model_id:
        raise ValidationError("ID de modelo requerido")
    
    if not isinstance(model_id, str):
        raise ValidationError("ID de modelo debe ser una cadena")
    
    return model_id.strip()


def validate_column_name(column: str, available_columns: list) -> str:
    """
    Validar que una columna existe
    
    Args:
        column: Nombre de la columna
        available_columns: Lista de columnas disponibles
        
    Returns:
        Nombre de columna validado
        
    Raises:
        ValidationError: Si la columna no existe
    """
    if not column:
        raise ValidationError("Nombre de columna requerido")
    
    if column not in available_columns:
        raise ValidationError(f"Columna '{column}' no encontrada en el dataset")
    
    return column


def validate_positive_integer(value: Any, name: str, min_value: int = 1, max_value: int = None) -> int:
    """
    Validar entero positivo
    
    Args:
        value: Valor a validar
        name: Nombre del campo
        min_value: Valor mínimo permitido
        max_value: Valor máximo permitido
        
    Returns:
        Valor validado
        
    Raises:
        ValidationError: Si el valor no es válido
    """
    try:
        int_value = int(value)
    except (ValueError, TypeError):
        raise ValidationError(f"{name} debe ser un número entero")
    
    if int_value < min_value:
        raise ValidationError(f"{name} debe ser al menos {min_value}")
    
    if max_value is not None and int_value > max_value:
        raise ValidationError(f"{name} no puede exceder {max_value}")
    
    return int_value


def validate_float_range(value: Any, name: str, min_value: float = 0.0, max_value: float = 1.0) -> float:
    """
    Validar número flotante en rango
    
    Args:
        value: Valor a validar
        name: Nombre del campo
        min_value: Valor mínimo
        max_value: Valor máximo
        
    Returns:
        Valor validado
        
    Raises:
        ValidationError: Si el valor no es válido
    """
    try:
        float_value = float(value)
    except (ValueError, TypeError):
        raise ValidationError(f"{name} debe ser un número")
    
    if float_value < min_value or float_value > max_value:
        raise ValidationError(f"{name} debe estar entre {min_value} y {max_value}")
    
    return float_value
