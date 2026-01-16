"""
Dataset Service - Business logic for dataset management
Handles all dataset-related operations including upload, processing, and retrieval
"""

import os
import uuid
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

import pandas as pd
from werkzeug.datastructures import FileStorage
from flask import current_app
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, count, when, isnan

from app.core.spark_manager import SparkManager
from app.core.storage import DatasetStorage
from app.utils.helpers import get_column_type, dataframe_to_json, pandas_to_spark
from app.utils.exceptions import (
    ValidationError,
    NotFoundError,
    BadRequestError,
    InternalServerError
)
from app.utils.validators import validate_file_extension, validate_file_size


logger = logging.getLogger(__name__)

class DatasetService:
  
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
    
    MAX_FILE_SIZE = 100 * 1024 * 1024
    
    @staticmethod
    def upload_file(file: FileStorage) -> Dict[str, Any]:
  
        try:
            if not file or file.filename == '':
                raise ValidationError("No se seleccionó ningún archivo")
            
            filename = file.filename
            
            if not validate_file_extension(filename, DatasetService.ALLOWED_EXTENSIONS):
                raise ValidationError(
                    f"Formato de archivo no soportado. Use: {', '.join(DatasetService.ALLOWED_EXTENSIONS)}"
                )
            
            if not validate_file_size(file, DatasetService.MAX_FILE_SIZE):
                raise ValidationError(
                    f"El archivo excede el tamaño máximo permitido ({DatasetService.MAX_FILE_SIZE // (1024*1024)}MB)"
                )
            
            dataset_id = str(uuid.uuid4())
            file_ext = os.path.splitext(filename)[1].lower()
            
            upload_folder = current_app.config.get('UPLOAD_FOLDER')
            os.makedirs(upload_folder, exist_ok=True)
            
            temp_path = os.path.join(upload_folder, f"{dataset_id}{file_ext}")
            
            file.seek(0)
            file.save(temp_path)
            
            logger.info(f"Archivo guardado temporalmente: {temp_path}")
            
            spark = SparkManager.get_session()
            
            if file_ext == '.csv':
                df = spark.read.csv(
                    temp_path,
                    header=True,
                    inferSchema=True,
                    encoding='utf-8',
                    multiLine=True,
                    escape='"'
                )
                logger.info(f"Archivo CSV cargado: {filename}")
                
            elif file_ext in ['.xlsx', '.xls']:
                pdf = pd.read_excel(temp_path, engine='openpyxl' if file_ext == '.xlsx' else 'xlrd')
                df = pandas_to_spark(spark, pdf)
                logger.info(f"Archivo Excel cargado: {filename}")
                
            else:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                raise ValidationError("Formato de archivo no soportado")
            
            info = DatasetService._get_dataset_info(df)
            
            DatasetStorage.add_dataset(
                id=dataset_id,
                dataframe=df,
                filename=filename,
                path=temp_path,
                info=info
            )
            
            logger.info(f"Dataset almacenado correctamente: {dataset_id} ({filename})")
            
            return {
                'id': dataset_id,
                'filename': filename,
                'path': temp_path,
                'created_at': datetime.now().isoformat(),
                'info': info
            }
            
        except (ValidationError, BadRequestError) as e:
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.remove(temp_path)
            logger.warning(f"Error de validación durante la carga del archivo: {str(e)}")
            raise
            
        except Exception as e:
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.remove(temp_path)
            logger.error(f"Error al subir el archivo: {str(e)}", exc_info=True)
            raise InternalServerError(f"Error al procesar el archivo: {str(e)}")
    
    @staticmethod
    def upload_json(data: Dict[str, Any], name: Optional[str] = None) -> Dict[str, Any]:
        try:
            if not data or 'data' not in data:
                raise ValidationError("No se proporcionaron datos válidos")
            
            records = data['data']
            
            if not isinstance(records, list) or len(records) == 0:
                raise ValidationError("Los datos deben ser una lista no vacía de registros")
            
            dataset_id = str(uuid.uuid4())
            filename = name or data.get('name', f'dataset_{dataset_id[:8]}')
            
            # Convert JSON to DataFrame
            spark = SparkManager.get_session()
            
            try:
                pdf = pd.DataFrame(records)
                df = pandas_to_spark(spark, pdf)
            except Exception as e:
                raise ValidationError(f"Error al convertir datos a DataFrame: {str(e)}")
            
            logger.info(f"JSON data converted to DataFrame: {len(records)} rows")
            
            info = DatasetService._get_dataset_info(df)
            
            # Store dataset (no file path for JSON data)
            DatasetStorage.add_dataset(
                id=dataset_id,
                dataframe=df,
                filename=filename,
                path=None,
                info=info
            )
            
            logger.info(f"JSON dataset stored successfully: {dataset_id} ({filename})")
            
            return {
                'id': dataset_id,
                'filename': filename,
                'path': None,
                'created_at': datetime.now().isoformat(),
                'info': info
            }
            
        except (ValidationError, BadRequestError) as e:
            logger.warning(f"Validation error during JSON upload: {str(e)}")
            raise
            
        except Exception as e:
            logger.error(f"Error uploading JSON data: {str(e)}", exc_info=True)
            raise InternalServerError(f"Error al procesar los datos JSON: {str(e)}")
    
    @staticmethod
    def get_by_id(dataset_id: str) -> Dict[str, Any]:
        """
        Get dataset information by ID
        
        Args:
            dataset_id: Unique dataset identifier
            
        Returns:
            Dictionary with dataset metadata
            
        Raises:
            NotFoundError: If dataset doesn't exist
        """
        try:
            info = DatasetStorage.get_info(dataset_id)
            
            if not info:
                raise NotFoundError("Dataset", dataset_id)
            
            return info
            
        except NotFoundError:
            raise
            
        except Exception as e:
            logger.error(f"Error getting dataset {dataset_id}: {str(e)}", exc_info=True)
            raise InternalServerError(f"Error al obtener el dataset: {str(e)}")
    
    @staticmethod
    def get_preview(
        dataset_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get paginated preview of dataset data
        
        Args:
            dataset_id: Unique dataset identifier
            limit: Maximum number of rows to return
            offset: Number of rows to skip
            
        Returns:
            Dictionary with data preview, total_rows, and columns
            
        Raises:
            NotFoundError: If dataset doesn't exist
            ValidationError: If parameters are invalid
        """
        try:
            # Validate parameters
            if limit < 1 or limit > 10000:
                raise ValidationError("El límite debe estar entre 1 y 10000")
            
            if offset < 0:
                raise ValidationError("El offset no puede ser negativo")
            
            # Get dataset
            df = DatasetStorage.get_dataframe(dataset_id)
            
            if df is None:
                raise NotFoundError("Dataset", dataset_id)
            
            dataset_info = DatasetStorage.get_info(dataset_id)
            
            # Get paginated data
            if offset > 0:
                # For offset, we need to collect data and slice
                pdf = df.limit(offset + limit).toPandas()
                # Handle case where offset exceeds available data
                if offset >= len(pdf):
                    data = []
                else:
                    data = pdf.iloc[offset:offset + limit].to_dict(orient='records')
            else:
                data = dataframe_to_json(df, limit)
            
            # Replace NaN with None for JSON serialization
            data = [{k: (None if pd.isna(v) else v) for k, v in record.items()} for record in data]
            
            logger.info(f"Preview retrieved for dataset {dataset_id}: {len(data)} rows")
            
            return {
                'data': data,
                'total_rows': dataset_info['info']['row_count'],
                'columns': [col['name'] for col in dataset_info['info']['columns']],
                'offset': offset,
                'limit': limit
            }
            
        except (NotFoundError, ValidationError):
            raise
            
        except Exception as e:
            logger.error(f"Error getting preview for dataset {dataset_id}: {str(e)}", exc_info=True)
            raise InternalServerError(f"Error al obtener vista previa: {str(e)}")
    
    @staticmethod
    def list_all() -> List[Dict[str, Any]]:
        """
        List all available datasets
        
        Returns:
            List of dataset summaries (without DataFrame objects)
        """
        try:
            datasets = []
            
            for dataset in DatasetStorage.list_all():
                info = dataset.get('info', {})
                columns_info = info.get('columns', [])
                
                datasets.append({
                    'id': dataset['id'],
                    'filename': dataset['filename'],
                    'path': dataset.get('path'),
                    'created_at': dataset['created_at'],
                    'info': info  # Include full info for schema to process
                })
            
            logger.info(f"Listed {len(datasets)} datasets")
            
            return datasets
            
        except Exception as e:
            logger.error(f"Error listing datasets: {str(e)}", exc_info=True)
            raise InternalServerError(f"Error al listar datasets: {str(e)}")
    
    @staticmethod
    def delete(dataset_id: str) -> bool:
        """
        Delete a dataset and cleanup associated files
        
        Args:
            dataset_id: Unique dataset identifier
            
        Returns:
            True if deletion was successful
            
        Raises:
            NotFoundError: If dataset doesn't exist
        """
        try:
            # Get dataset info before deletion
            dataset = DatasetStorage.get(dataset_id)
            
            if not dataset:
                raise NotFoundError("Dataset", dataset_id)
            
            # Remove file if it exists
            if dataset.get('path') and os.path.exists(dataset['path']):
                try:
                    os.remove(dataset['path'])
                    logger.info(f"File deleted: {dataset['path']}")
                except Exception as e:
                    logger.warning(f"Could not delete file {dataset['path']}: {str(e)}")
            
            # Remove from storage
            success = DatasetStorage.delete(dataset_id)
            
            if success:
                logger.info(f"Dataset deleted successfully: {dataset_id}")
            else:
                logger.warning(f"Dataset not found in storage: {dataset_id}")
            
            return success
            
        except NotFoundError:
            raise
            
        except Exception as e:
            logger.error(f"Error deleting dataset {dataset_id}: {str(e)}", exc_info=True)
            raise InternalServerError(f"Error al eliminar el dataset: {str(e)}")
    
    @staticmethod
    def _get_dataset_info(df: DataFrame) -> Dict[str, Any]:
        """
        Extract comprehensive metadata from a Spark DataFrame
        
        Args:
            df: Spark DataFrame
            
        Returns:
            Dictionary with row count, column count, and detailed column information
        """
        try:
            columns_info = []
            
            for field in df.schema.fields:
                # Get null count statistics
                # Use backticks to escape column names with special characters (dots, spaces, etc.)
                col_name = f"`{field.name}`"
                col_stats = df.select(
                    count(
                        when(
                            col(col_name).isNull() | 
                            (isnan(col(col_name)) if get_column_type(field.dataType) == 'numeric' else col(col_name).isNull()),
                            True
                        )
                    ).alias('null_count'),
                    count(col(col_name)).alias('non_null_count')
                ).first()
                
                columns_info.append({
                    'name': field.name,
                    'type': get_column_type(field.dataType),
                    'spark_type': str(field.dataType),
                    'nullable': field.nullable,
                    'null_count': int(col_stats['null_count']) if col_stats else 0,
                    'non_null_count': int(col_stats['non_null_count']) if col_stats else 0
                })
            
            row_count = df.count()
            
            info = {
                'row_count': row_count,
                'column_count': len(df.columns),
                'columns': columns_info
            }
            
            logger.debug(f"Dataset info extracted: {row_count} rows, {len(df.columns)} columns")
            
            return info
            
        except Exception as e:
            logger.error(f"Error extracting dataset info: {str(e)}", exc_info=True)
            raise InternalServerError(f"Error al obtener información del dataset: {str(e)}")
    
    @staticmethod
    def get_dataframe(dataset_id: str) -> Optional[DataFrame]:
        """
        Get the Spark DataFrame for a dataset
        
        Args:
            dataset_id: Unique dataset identifier
            
        Returns:
            Spark DataFrame or None if not found
            
        Raises:
            NotFoundError: If dataset doesn't exist
        """
        df = DatasetStorage.get_dataframe(dataset_id)
        
        if df is None:
            raise NotFoundError("Dataset", dataset_id)
        
        return df
    
    @staticmethod
    def exists(dataset_id: str) -> bool:
        """
        Check if a dataset exists
        
        Args:
            dataset_id: Unique dataset identifier
            
        Returns:
            True if dataset exists, False otherwise
        """
        return DatasetStorage.exists(dataset_id)
    
    @staticmethod
    def get_column_names(dataset_id: str) -> List[str]:
        """
        Get list of column names for a dataset
        
        Args:
            dataset_id: Unique dataset identifier
            
        Returns:
            List of column names
            
        Raises:
            NotFoundError: If dataset doesn't exist
        """
        df = DatasetService.get_dataframe(dataset_id)
        return df.columns
    
    @staticmethod
    def get_column_info(dataset_id: str, column_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific column
        
        Args:
            dataset_id: Unique dataset identifier
            column_name: Name of the column
            
        Returns:
            Dictionary with column metadata or None if not found
            
        Raises:
            NotFoundError: If dataset doesn't exist
            ValidationError: If column doesn't exist
        """
        info = DatasetService.get_by_id(dataset_id)
        
        for col_info in info['info']['columns']:
            if col_info['name'] == column_name:
                return col_info
        
        raise ValidationError(f"Columna '{column_name}' no encontrada en el dataset")
