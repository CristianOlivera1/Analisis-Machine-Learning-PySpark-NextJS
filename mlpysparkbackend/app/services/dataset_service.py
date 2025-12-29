"""
Dataset Service - Business logic for dataset management
Handles all dataset-related operations including upload, processing, and retrieval
"""

import os
import uuid
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path
import tempfile

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
    """
    Service class for dataset management operations
    Handles file uploads, data processing, and dataset lifecycle
    """
    
    # Supported file extensions
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
    
    # Maximum file size (100MB)
    MAX_FILE_SIZE = 100 * 1024 * 1024
    
    @staticmethod
    def upload_file(file: FileStorage) -> Dict[str, Any]:
        """
        Process and upload a CSV or Excel file
        
        Args:
            file: File uploaded by user (CSV or Excel)
            
        Returns:
            Dictionary containing dataset_id, filename, and dataset info
            
        Raises:
            ValidationError: If file validation fails
            InternalServerError: If processing fails
        """
        try:
            # Validate file presence
            if not file or file.filename == '':
                raise ValidationError("No se seleccionó ningún archivo")
            
            filename = file.filename
            
            # Validate file extension
            if not validate_file_extension(filename, DatasetService.ALLOWED_EXTENSIONS):
                raise ValidationError(
                    f"Formato de archivo no soportado. Use: {', '.join(DatasetService.ALLOWED_EXTENSIONS)}"
                )
            
            # Validate file size
            if not validate_file_size(file, DatasetService.MAX_FILE_SIZE):
                raise ValidationError(
                    f"El archivo excede el tamaño máximo permitido ({DatasetService.MAX_FILE_SIZE // (1024*1024)}MB)"
                )
            
            # Generate unique dataset ID
            dataset_id = str(uuid.uuid4())
            file_ext = os.path.splitext(filename)[1].lower()
            
            # Save file temporarily
            upload_folder = current_app.config.get('UPLOAD_FOLDER')
            os.makedirs(upload_folder, exist_ok=True)
            
            temp_path = os.path.join(upload_folder, f"{dataset_id}{file_ext}")
            
            # Reset file pointer to beginning before saving
            file.seek(0)
            file.save(temp_path)
            
            logger.info(f"File saved temporarily: {temp_path}")
            
            # Load file into Spark DataFrame
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
                logger.info(f"CSV file loaded: {filename}")
                
            elif file_ext in ['.xlsx', '.xls']:
                # For Excel, convert through pandas first
                pdf = pd.read_excel(temp_path, engine='openpyxl' if file_ext == '.xlsx' else 'xlrd')
                df = pandas_to_spark(spark, pdf)
                logger.info(f"Excel file loaded: {filename}")
                
            else:
                # Cleanup and raise error
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                raise ValidationError("Formato de archivo no soportado")
            
            # Get dataset information
            info = DatasetService._get_dataset_info(df)
            
            # Store dataset
            DatasetStorage.add_dataset(
                id=dataset_id,
                dataframe=df,
                filename=filename,
                path=temp_path,
                info=info
            )
            
            logger.info(f"Dataset stored successfully: {dataset_id} ({filename})")
            
            return {
                'id': dataset_id,
                'filename': filename,
                'path': temp_path,
                'created_at': datetime.now().isoformat(),
                'info': info
            }
            
        except (ValidationError, BadRequestError) as e:
            # Cleanup temporary file on validation error
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.remove(temp_path)
            logger.warning(f"Validation error during file upload: {str(e)}")
            raise
            
        except Exception as e:
            # Cleanup temporary file on any error
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.remove(temp_path)
            logger.error(f"Error uploading file: {str(e)}", exc_info=True)
            raise InternalServerError(f"Error al procesar el archivo: {str(e)}")
    
    @staticmethod
    def upload_json(data: Dict[str, Any], name: Optional[str] = None) -> Dict[str, Any]:
        """
        Process and upload dataset from JSON data (e.g., from localStorage)
        
        Args:
            data: Dictionary containing 'data' key with list of records
            name: Optional name for the dataset
            
        Returns:
            Dictionary containing dataset_id, filename, and dataset info
            
        Raises:
            ValidationError: If data validation fails
            InternalServerError: If processing fails
        """
        try:
            # Validate data presence
            if not data or 'data' not in data:
                raise ValidationError("No se proporcionaron datos válidos")
            
            records = data['data']
            
            if not isinstance(records, list) or len(records) == 0:
                raise ValidationError("Los datos deben ser una lista no vacía de registros")
            
            # Generate unique dataset ID
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
            
            # Get dataset information
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
    def get_available_samples() -> List[Dict[str, Any]]:
        """
        Get list of available sample datasets
        
        Returns:
            List of sample dataset metadata
        """
        samples = [
            {
                'id': 'iris',
                'name': 'Iris Dataset',
                'description': 'Dataset clásico de clasificación de flores iris con 3 especies',
                'rows': 150,
                'columns': 5,
                'type': 'classification',
                'features': ['sepal_length', 'sepal_width', 'petal_length', 'petal_width'],
                'target': 'species'
            },
            {
                'id': 'wine',
                'name': 'Wine Quality',
                'description': 'Calidad de vinos para clasificación basada en propiedades químicas',
                'rows': 178,
                'columns': 14,
                'type': 'classification',
                'features': 'chemical properties',
                'target': 'wine_class'
            },
            {
                'id': 'housing',
                'name': 'California Housing',
                'description': 'Precios de viviendas en California para regresión',
                'rows': 20640,
                'columns': 9,
                'type': 'regression',
                'features': ['MedInc', 'HouseAge', 'AveRooms', 'AveBedrms', 'Population', 'AveOccup', 'Latitude', 'Longitude'],
                'target': 'price'
            }
        ]
        
        logger.info(f"Retrieved {len(samples)} sample datasets")
        
        return samples
    
    @staticmethod
    def load_sample(sample_id: str) -> Dict[str, Any]:
        """
        Load a sample dataset from sklearn
        
        Args:
            sample_id: Sample dataset identifier ('iris', 'wine', 'housing')
            
        Returns:
            Dictionary containing dataset_id, filename, and dataset info
            
        Raises:
            ValidationError: If sample_id is invalid
            InternalServerError: If loading fails
        """
        try:
            # Import sklearn datasets
            try:
                from sklearn import datasets
            except ImportError:
                raise InternalServerError(
                    "scikit-learn no está instalado. Instale con: pip install scikit-learn"
                )
            
            spark = SparkManager.get_session()
            dataset_id = str(uuid.uuid4())
            
            # Load appropriate sample dataset
            if sample_id == 'iris':
                iris = datasets.load_iris()
                pdf = pd.DataFrame(
                    iris.data,
                    columns=['sepal_length', 'sepal_width', 'petal_length', 'petal_width']
                )
                pdf['species'] = iris.target.astype(int)
                # Map target to species names
                species_names = ['setosa', 'versicolor', 'virginica']
                pdf['species_name'] = pdf['species'].apply(lambda x: species_names[x])
                name = 'Iris Dataset'
                logger.info("Iris dataset loaded from sklearn")
                
            elif sample_id == 'wine':
                wine = datasets.load_wine()
                pdf = pd.DataFrame(wine.data, columns=wine.feature_names)
                pdf['target'] = wine.target.astype(int)
                # Map target to wine class names (convert to string explicitly)
                pdf['wine_class'] = pdf['target'].apply(lambda x: str(wine.target_names[x]))
                name = 'Wine Quality Dataset'
                logger.info("Wine dataset loaded from sklearn")
                
            elif sample_id == 'housing' or sample_id == 'boston':
                # Boston is deprecated, use California Housing instead
                try:
                    from sklearn.datasets import fetch_california_housing
                    housing = fetch_california_housing()
                    pdf = pd.DataFrame(housing.data, columns=housing.feature_names)
                    pdf['price'] = housing.target.astype(float)
                    name = 'California Housing Dataset'
                    logger.info("California Housing dataset loaded from sklearn")
                except Exception as e:
                    logger.error(f"Error loading housing dataset: {str(e)}")
                    raise InternalServerError("Error al cargar el dataset de viviendas")
                
            else:
                raise ValidationError(
                    f"Dataset de ejemplo '{sample_id}' no encontrado. "
                    f"Opciones válidas: iris, wine, housing"
                )
            
            # Convert to Spark DataFrame (Windows-safe method)
            df = pandas_to_spark(spark, pdf)
            
            # Get dataset information
            info = DatasetService._get_dataset_info(df)
            
            # Store dataset (no file path for sample datasets)
            DatasetStorage.add_dataset(
                id=dataset_id,
                dataframe=df,
                filename=name,
                path=None,
                info=info
            )
            
            logger.info(f"Sample dataset stored successfully: {dataset_id} ({name})")
            
            return {
                'id': dataset_id,
                'filename': name,
                'path': None,
                'created_at': datetime.now().isoformat(),
                'sample_id': sample_id,
                'info': info
            }
            
        except (ValidationError, BadRequestError):
            raise
            
        except Exception as e:
            logger.error(f"Error loading sample dataset {sample_id}: {str(e)}", exc_info=True)
            raise InternalServerError(f"Error al cargar dataset de ejemplo: {str(e)}")
    
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
