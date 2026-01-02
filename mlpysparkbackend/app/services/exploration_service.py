"""
Exploration Service - Business logic for data exploration and analysis
"""

import math
from typing import Dict, Any
from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.functions import col, count, mean, stddev, min as spark_min, max as spark_max
import logging

from app.core.storage import DatasetStorage
from app.utils.exceptions import NotFoundError, ValidationError

logger = logging.getLogger(__name__)


def sanitize_value(value):
    """
    Sanitize a value to ensure it's JSON serializable.
    Converts NaN and Infinity to None.
    """
    if value is None:
        return None
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
    return value


def sanitize_dict(d):
    """
    Recursively sanitize all values in a dictionary.
    Converts NaN and Infinity to None for JSON compatibility.
    """
    if isinstance(d, dict):
        return {k: sanitize_dict(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [sanitize_dict(item) for item in d]
    else:
        return sanitize_value(d)


class ExplorationService:
    """Service for data exploration and analysis operations"""
    
    @staticmethod
    def _get_dataset_df(dataset_id: str) -> DataFrame:
        """Get DataFrame for a dataset ID"""
        df = DatasetStorage.get_dataframe(dataset_id)
        if df is None:
            raise NotFoundError(resource_type="Dataset", resource_id=dataset_id)
        return df
    
    @staticmethod
    def get_statistics(dataset_id: str) -> Dict[str, Any]:
        """
        Get descriptive statistics for all columns in the dataset
        """
        try:
            df = ExplorationService._get_dataset_df(dataset_id)
            
            # Separate numeric and categorical columns
            numeric_cols = [field.name for field in df.schema.fields 
                          if field.dataType.typeName() in ('integer', 'long', 'float', 'double', 'decimal')]
            categorical_cols = [field.name for field in df.schema.fields 
                              if field.dataType.typeName() == 'string']
            
            result = {
                "numeric": {},
                "categorical": {}
            }
            
            # Numeric statistics
            if numeric_cols:
                stats_exprs = []
                for col_name in numeric_cols:
                    stats_exprs.extend([
                        count(col(col_name)).alias(f"{col_name}_count"),
                        mean(col(col_name)).alias(f"{col_name}_mean"),
                        stddev(col(col_name)).alias(f"{col_name}_std"),
                        spark_min(col(col_name)).alias(f"{col_name}_min"),
                        spark_max(col(col_name)).alias(f"{col_name}_max")
                    ])
                
                stats_row = df.select(stats_exprs).first()
                
                for col_name in numeric_cols:
                    try:
                        quartiles = df.stat.approxQuantile(col_name, [0.25, 0.5, 0.75], 0.01)
                    except Exception as e:
                        logger.warning(f"Could not calculate quartiles for {col_name}: {e}")
                        quartiles = [None, None, None]
                    
                    result["numeric"][col_name] = {
                        "count": stats_row[f"{col_name}_count"],
                        "mean": round(stats_row[f"{col_name}_mean"], 4) if stats_row[f"{col_name}_mean"] is not None else None,
                        "std": round(stats_row[f"{col_name}_std"], 4) if stats_row[f"{col_name}_std"] is not None else None,
                        "min": stats_row[f"{col_name}_min"],
                        "max": stats_row[f"{col_name}_max"],
                        "quartiles": {
                            "q1": round(quartiles[0], 4) if quartiles[0] is not None else None,
                            "median": round(quartiles[1], 4) if quartiles[1] is not None else None,
                            "q3": round(quartiles[2], 4) if quartiles[2] is not None else None
                        }
                    }
            
            # Categorical statistics
            for col_name in categorical_cols:
                distinct_count = df.select(col_name).distinct().count()
                top_value_row = df.groupBy(col_name).count().orderBy(F.desc("count")).first()
                total_count = df.count()
                
                result["categorical"][col_name] = {
                    "count": total_count,
                    "unique": distinct_count,
                    "top": top_value_row[col_name] if top_value_row else None,
                    "freq": top_value_row["count"] if top_value_row else 0
                }
            
            logger.info(f"Statistics calculated for dataset: {dataset_id}")
            # Sanitize result to convert NaN/Infinity to null for JSON compatibility
            return sanitize_dict(result)
            
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error calculating statistics for {dataset_id}: {e}")
            raise ValidationError(f"Error calculating statistics: {str(e)}")
    
    @staticmethod
    def get_histogram(dataset_id: str, column: str, bins: int = 10) -> Dict[str, Any]:
        """Get histogram data for a specific column"""
        try:
            df = ExplorationService._get_dataset_df(dataset_id)
            
            if column not in df.columns:
                raise ValidationError(f"Column '{column}' not found in dataset")
            
            if bins < 1 or bins > 100:
                raise ValidationError("Number of bins must be between 1 and 100")
            
            col_type = [field.dataType.typeName() for field in df.schema.fields if field.name == column][0]
            
            if col_type not in ('integer', 'long', 'float', 'double', 'decimal'):
                raise ValidationError(f"Column '{column}' must be numeric for histogram")
            
            min_max = df.select(spark_min(col(column)).alias('min'), 
                               spark_max(col(column)).alias('max')).first()
            
            if min_max['min'] is None or min_max['max'] is None:
                return {"column": column, "bins": bins, "data": []}
            
            col_min = float(min_max['min'])
            col_max = float(min_max['max'])
            bin_width = (col_max - col_min) / bins if col_max != col_min else 1
            
            histogram_data = []
            for i in range(bins):
                bin_min = col_min + i * bin_width
                bin_max = col_min + (i + 1) * bin_width
                
                if i == bins - 1:
                    bin_count = df.filter((col(column) >= bin_min) & (col(column) <= bin_max)).count()
                else:
                    bin_count = df.filter((col(column) >= bin_min) & (col(column) < bin_max)).count()
                
                histogram_data.append({
                    "bin": f"{bin_min:.2f}-{bin_max:.2f}",
                    "count": bin_count,
                    "min": round(bin_min, 4),
                    "max": round(bin_max, 4)
                })
            
            logger.info(f"Histogram calculated for {column} in dataset {dataset_id}")
            return {"column": column, "bins": bins, "data": histogram_data}
            
        except (NotFoundError, ValidationError):
            raise
        except Exception as e:
            logger.error(f"Error calculating histogram for {column}: {e}")
            raise ValidationError(f"Error calculating histogram: {str(e)}")
