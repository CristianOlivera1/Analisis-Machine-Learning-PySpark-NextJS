"""
Exploration Service - Business logic for data exploration and analysis
"""

from typing import Dict, List, Optional, Any, Union
from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.functions import col, count, mean, stddev, min as spark_min, max as spark_max
from pyspark.sql.functions import when, isnan, isnull, sum as spark_sum, expr
import logging

from app.core.storage import DatasetStorage
from app.utils.exceptions import NotFoundError, ValidationError

logger = logging.getLogger(__name__)


class ExplorationService:
    """Service for data exploration and analysis operations"""
    
    # Supported filter operators
    FILTER_OPERATORS = {
        'equals', 'not_equals', 'greater_than', 'less_than',
        'greater_equal', 'less_equal', 'contains', 'starts_with',
        'ends_with', 'is_null', 'is_not_null', 'in', 'not_in'
    }
    
    # Supported aggregation functions
    AGGREGATION_FUNCTIONS = {'sum', 'mean', 'count', 'min', 'max'}
    
    @staticmethod
    def _get_dataset_df(dataset_id: str) -> DataFrame:
        """
        Get DataFrame for a dataset ID
        
        Args:
            dataset_id: Dataset identifier
            
        Returns:
            Spark DataFrame
            
        Raises:
            NotFoundError: If dataset not found
        """
        df = DatasetStorage.get_dataframe(dataset_id)
        if df is None:
            raise NotFoundError(resource_type="Dataset", resource_id=dataset_id)
        return df
    
    @staticmethod
    def get_statistics(dataset_id: str) -> Dict[str, Any]:
        """
        Get descriptive statistics for all columns in the dataset
        
        Args:
            dataset_id: Dataset identifier
            
        Returns:
            Dictionary with statistics for numeric and categorical columns
            
        Example:
            {
                "numeric": {
                    "age": {
                        "count": 1000,
                        "mean": 35.5,
                        "std": 12.3,
                        "min": 18,
                        "max": 80,
                        "quartiles": [25, 35, 50]
                    }
                },
                "categorical": {
                    "category": {
                        "count": 1000,
                        "unique": 5,
                        "top": "A",
                        "freq": 350
                    }
                }
            }
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
                # Calculate basic stats
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
                    # Get quartiles
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
                # Count distinct values
                distinct_count = df.select(col_name).distinct().count()
                
                # Get top value and frequency
                top_value_row = df.groupBy(col_name).count().orderBy(F.desc("count")).first()
                
                total_count = df.count()
                
                result["categorical"][col_name] = {
                    "count": total_count,
                    "unique": distinct_count,
                    "top": top_value_row[col_name] if top_value_row else None,
                    "freq": top_value_row["count"] if top_value_row else 0
                }
            
            logger.info(f"Statistics calculated for dataset: {dataset_id}")
            return result
            
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error calculating statistics for {dataset_id}: {e}")
            raise ValidationError(f"Error calculating statistics: {str(e)}")
    
    @staticmethod
    def get_histogram(dataset_id: str, column: str, bins: int = 10) -> Dict[str, Any]:
        """
        Get histogram data for a specific column
        
        Args:
            dataset_id: Dataset identifier
            column: Column name
            bins: Number of bins (default: 10)
            
        Returns:
            Dictionary with histogram data
            
        Example:
            {
                "column": "age",
                "bins": 10,
                "data": [
                    {"bin": "18-28", "count": 150, "min": 18, "max": 28},
                    {"bin": "28-38", "count": 200, "min": 28, "max": 38}
                ]
            }
        """
        try:
            df = ExplorationService._get_dataset_df(dataset_id)
            
            # Validate column exists
            if column not in df.columns:
                raise ValidationError(f"Column '{column}' not found in dataset")
            
            # Validate bins
            if bins < 1 or bins > 100:
                raise ValidationError("Number of bins must be between 1 and 100")
            
            # Get column type
            col_type = [field.dataType.typeName() for field in df.schema.fields if field.name == column][0]
            
            if col_type not in ('integer', 'long', 'float', 'double', 'decimal'):
                raise ValidationError(f"Column '{column}' must be numeric for histogram")
            
            # Get min and max
            min_max = df.select(spark_min(col(column)).alias('min'), 
                               spark_max(col(column)).alias('max')).first()
            
            if min_max['min'] is None or min_max['max'] is None:
                return {
                    "column": column,
                    "bins": bins,
                    "data": []
                }
            
            col_min = float(min_max['min'])
            col_max = float(min_max['max'])
            
            # Calculate bin width
            bin_width = (col_max - col_min) / bins if col_max != col_min else 1
            
            # Create bins
            histogram_data = []
            for i in range(bins):
                bin_min = col_min + i * bin_width
                bin_max = col_min + (i + 1) * bin_width
                
                # Count values in bin (inclusive lower, exclusive upper, except for last bin)
                if i == bins - 1:  # Last bin is inclusive on both ends
                    bin_count = df.filter(
                        (col(column) >= bin_min) & (col(column) <= bin_max)
                    ).count()
                else:
                    bin_count = df.filter(
                        (col(column) >= bin_min) & (col(column) < bin_max)
                    ).count()
                
                histogram_data.append({
                    "bin": f"{bin_min:.2f}-{bin_max:.2f}",
                    "count": bin_count,
                    "min": round(bin_min, 4),
                    "max": round(bin_max, 4)
                })
            
            logger.info(f"Histogram calculated for {column} in dataset {dataset_id}")
            return {
                "column": column,
                "bins": bins,
                "data": histogram_data
            }
            
        except (NotFoundError, ValidationError):
            raise
        except Exception as e:
            logger.error(f"Error calculating histogram for {column}: {e}")
            raise ValidationError(f"Error calculating histogram: {str(e)}")
    
    @staticmethod
    def get_chart_data(
        dataset_id: str,
        chart_type: str,
        x_column: Optional[str] = None,
        y_column: Optional[str] = None,
        aggregation: str = 'count',
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Get data for various chart types
        
        Args:
            dataset_id: Dataset identifier
            chart_type: Type of chart (bar, line, scatter, pie)
            x_column: X-axis column name
            y_column: Y-axis column name (optional for some charts)
            aggregation: Aggregation function (sum, mean, count, min, max)
            limit: Maximum number of data points
            
        Returns:
            Dictionary with chart data
            
        Example:
            {
                "chart_type": "bar",
                "x_column": "category",
                "y_column": "sales",
                "aggregation": "sum",
                "data": [
                    {"x": "A", "y": 1000},
                    {"x": "B", "y": 1500}
                ]
            }
        """
        try:
            df = ExplorationService._get_dataset_df(dataset_id)
            
            # Validate chart type
            valid_chart_types = ['bar', 'line', 'scatter', 'pie']
            if chart_type not in valid_chart_types:
                raise ValidationError(f"Invalid chart type. Must be one of: {valid_chart_types}")
            
            # Validate aggregation
            if aggregation not in ExplorationService.AGGREGATION_FUNCTIONS:
                raise ValidationError(f"Invalid aggregation. Must be one of: {ExplorationService.AGGREGATION_FUNCTIONS}")
            
            # Validate columns exist
            if x_column and x_column not in df.columns:
                raise ValidationError(f"Column '{x_column}' not found in dataset")
            if y_column and y_column not in df.columns:
                raise ValidationError(f"Column '{y_column}' not found in dataset")
            
            # Validate limit
            if limit < 1 or limit > 10000:
                raise ValidationError("Limit must be between 1 and 10000")
            
            chart_data = []
            
            if chart_type in ['bar', 'line', 'pie']:
                # These charts require grouping by x_column
                if not x_column:
                    raise ValidationError(f"{chart_type} chart requires x_column")
                
                if y_column:
                    # Group by x_column and aggregate y_column
                    agg_func = ExplorationService._get_agg_function(aggregation)
                    grouped_df = df.groupBy(x_column).agg(
                        agg_func(col(y_column)).alias('value')
                    ).orderBy(F.desc('value')).limit(limit)
                    
                    for row in grouped_df.collect():
                        chart_data.append({
                            "x": row[x_column],
                            "y": round(row['value'], 4) if row['value'] is not None else 0
                        })
                else:
                    # Just count by x_column
                    grouped_df = df.groupBy(x_column).count().orderBy(F.desc('count')).limit(limit)
                    
                    for row in grouped_df.collect():
                        chart_data.append({
                            "x": row[x_column],
                            "y": row['count']
                        })
            
            elif chart_type == 'scatter':
                # Scatter plot requires both x and y columns
                if not x_column or not y_column:
                    raise ValidationError("Scatter chart requires both x_column and y_column")
                
                scatter_df = df.select(x_column, y_column).limit(limit)
                
                for row in scatter_df.collect():
                    chart_data.append({
                        "x": row[x_column],
                        "y": row[y_column]
                    })
            
            logger.info(f"Chart data generated for {chart_type} chart in dataset {dataset_id}")
            return {
                "chart_type": chart_type,
                "x_column": x_column,
                "y_column": y_column,
                "aggregation": aggregation if y_column else 'count',
                "data": chart_data
            }
            
        except (NotFoundError, ValidationError):
            raise
        except Exception as e:
            logger.error(f"Error generating chart data: {e}")
            raise ValidationError(f"Error generating chart data: {str(e)}")
    
    @staticmethod
    def get_correlation_matrix(dataset_id: str) -> Dict[str, Any]:
        """
        Calculate correlation matrix for numeric columns
        
        Args:
            dataset_id: Dataset identifier
            
        Returns:
            Dictionary with correlation matrix
            
        Example:
            {
                "columns": ["age", "salary", "experience"],
                "matrix": [
                    [1.0, 0.85, 0.92],
                    [0.85, 1.0, 0.78],
                    [0.92, 0.78, 1.0]
                ]
            }
        """
        try:
            df = ExplorationService._get_dataset_df(dataset_id)
            
            # Get numeric columns
            numeric_cols = [field.name for field in df.schema.fields 
                          if field.dataType.typeName() in ('integer', 'long', 'float', 'double', 'decimal')]
            
            if len(numeric_cols) < 2:
                raise ValidationError("Need at least 2 numeric columns for correlation matrix")
            
            # Calculate correlation matrix
            matrix = []
            for col1 in numeric_cols:
                row = []
                for col2 in numeric_cols:
                    if col1 == col2:
                        row.append(1.0)
                    else:
                        try:
                            corr = df.stat.corr(col1, col2)
                            row.append(round(corr, 4) if corr is not None else 0.0)
                        except Exception as e:
                            logger.warning(f"Could not calculate correlation between {col1} and {col2}: {e}")
                            row.append(0.0)
                matrix.append(row)
            
            logger.info(f"Correlation matrix calculated for dataset {dataset_id}")
            return {
                "columns": numeric_cols,
                "matrix": matrix
            }
            
        except (NotFoundError, ValidationError):
            raise
        except Exception as e:
            logger.error(f"Error calculating correlation matrix: {e}")
            raise ValidationError(f"Error calculating correlation matrix: {str(e)}")
    
    @staticmethod
    def filter_data(
        dataset_id: str,
        filters: List[Dict[str, Any]],
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Apply filters to dataset and return filtered data
        
        Args:
            dataset_id: Dataset identifier
            filters: List of filter conditions
            limit: Maximum number of rows to return
            
        Filter format:
            {
                "column": "age",
                "operator": "greater_than",
                "value": 30
            }
            
        Returns:
            Dictionary with filtered data and metadata
            
        Example:
            {
                "total_rows": 500,
                "filtered_rows": 150,
                "data": [...],
                "filters_applied": [...]
            }
        """
        try:
            df = ExplorationService._get_dataset_df(dataset_id)
            original_count = df.count()
            
            # Apply filters
            filtered_df = df
            applied_filters = []
            
            for filter_obj in filters:
                column = filter_obj.get('column')
                operator = filter_obj.get('operator')
                value = filter_obj.get('value')
                
                # Validate filter
                if not column or not operator:
                    raise ValidationError("Each filter must have 'column' and 'operator'")
                
                if column not in df.columns:
                    raise ValidationError(f"Column '{column}' not found in dataset")
                
                if operator not in ExplorationService.FILTER_OPERATORS:
                    raise ValidationError(f"Invalid operator '{operator}'. Must be one of: {ExplorationService.FILTER_OPERATORS}")
                
                # Apply filter based on operator
                filtered_df = ExplorationService._apply_filter(filtered_df, column, operator, value)
                applied_filters.append(filter_obj)
            
            # Get filtered count
            filtered_count = filtered_df.count()
            
            # Limit results
            limited_df = filtered_df.limit(limit)
            
            # Convert to list of dictionaries
            data = [row.asDict() for row in limited_df.collect()]
            
            logger.info(f"Filters applied to dataset {dataset_id}: {len(filters)} filters, {filtered_count} rows")
            return {
                "total_rows": original_count,
                "filtered_rows": filtered_count,
                "returned_rows": len(data),
                "limit": limit,
                "data": data,
                "filters_applied": applied_filters
            }
            
        except (NotFoundError, ValidationError):
            raise
        except Exception as e:
            logger.error(f"Error filtering data: {e}")
            raise ValidationError(f"Error filtering data: {str(e)}")
    
    @staticmethod
    def describe_column(dataset_id: str, column: str) -> Dict[str, Any]:
        """
        Get detailed description of a specific column
        
        Args:
            dataset_id: Dataset identifier
            column: Column name
            
        Returns:
            Dictionary with detailed column information
            
        Example:
            {
                "name": "age",
                "type": "integer",
                "nullable": true,
                "count": 1000,
                "null_count": 10,
                "null_percentage": 1.0,
                "unique_count": 50,
                "statistics": {...},
                "sample_values": [25, 30, 35, 40, 45]
            }
        """
        try:
            df = ExplorationService._get_dataset_df(dataset_id)
            
            # Validate column exists
            if column not in df.columns:
                raise ValidationError(f"Column '{column}' not found in dataset")
            
            # Get column metadata
            col_field = [field for field in df.schema.fields if field.name == column][0]
            col_type = col_field.dataType.typeName()
            col_nullable = col_field.nullable
            
            # Count total and null values
            total_count = df.count()
            null_count = df.filter(col(column).isNull()).count()
            null_percentage = (null_count / total_count * 100) if total_count > 0 else 0
            
            # Count unique values (limit to avoid expensive operations)
            unique_count = df.select(column).distinct().count()
            
            result = {
                "name": column,
                "type": col_type,
                "nullable": col_nullable,
                "count": total_count,
                "null_count": null_count,
                "null_percentage": round(null_percentage, 2),
                "unique_count": unique_count
            }
            
            # Add type-specific statistics
            if col_type in ('integer', 'long', 'float', 'double', 'decimal'):
                # Numeric statistics
                stats = df.select(
                    mean(col(column)).alias('mean'),
                    stddev(col(column)).alias('std'),
                    spark_min(col(column)).alias('min'),
                    spark_max(col(column)).alias('max')
                ).first()
                
                try:
                    quartiles = df.stat.approxQuantile(column, [0.25, 0.5, 0.75], 0.01)
                except:
                    quartiles = [None, None, None]
                
                result["statistics"] = {
                    "mean": round(stats['mean'], 4) if stats['mean'] is not None else None,
                    "std": round(stats['std'], 4) if stats['std'] is not None else None,
                    "min": stats['min'],
                    "max": stats['max'],
                    "q1": round(quartiles[0], 4) if quartiles[0] is not None else None,
                    "median": round(quartiles[1], 4) if quartiles[1] is not None else None,
                    "q3": round(quartiles[2], 4) if quartiles[2] is not None else None
                }
                
                # Sample values
                sample_values = df.select(column).filter(col(column).isNotNull()).limit(5).collect()
                result["sample_values"] = [row[column] for row in sample_values]
                
            elif col_type == 'string':
                # Categorical statistics
                top_values = df.groupBy(column).count().orderBy(F.desc('count')).limit(5).collect()
                
                result["statistics"] = {
                    "top_values": [
                        {"value": row[column], "count": row['count']} 
                        for row in top_values
                    ]
                }
                
                # Sample values
                sample_values = df.select(column).filter(col(column).isNotNull()).limit(5).collect()
                result["sample_values"] = [row[column] for row in sample_values]
            
            else:
                # For other types, just show samples
                sample_values = df.select(column).filter(col(column).isNotNull()).limit(5).collect()
                result["sample_values"] = [str(row[column]) for row in sample_values]
            
            logger.info(f"Column description generated for '{column}' in dataset {dataset_id}")
            return result
            
        except (NotFoundError, ValidationError):
            raise
        except Exception as e:
            logger.error(f"Error describing column {column}: {e}")
            raise ValidationError(f"Error describing column: {str(e)}")
    
    @staticmethod
    def get_missing_values_summary(dataset_id: str) -> Dict[str, Any]:
        """
        Get summary of missing values for all columns
        
        Args:
            dataset_id: Dataset identifier
            
        Returns:
            Dictionary with missing values summary
            
        Example:
            {
                "total_rows": 1000,
                "columns": [
                    {
                        "name": "age",
                        "null_count": 10,
                        "null_percentage": 1.0
                    },
                    {
                        "name": "name",
                        "null_count": 0,
                        "null_percentage": 0.0
                    }
                ],
                "total_missing_cells": 15,
                "total_cells": 5000,
                "missing_percentage": 0.3
            }
        """
        try:
            df = ExplorationService._get_dataset_df(dataset_id)
            
            total_rows = df.count()
            columns_info = []
            total_missing = 0
            
            # Calculate null counts for all columns
            null_counts_exprs = [
                spark_sum(when(col(c).isNull(), 1).otherwise(0)).alias(c)
                for c in df.columns
            ]
            
            null_counts = df.select(null_counts_exprs).first()
            
            for column in df.columns:
                null_count = null_counts[column]
                null_percentage = (null_count / total_rows * 100) if total_rows > 0 else 0
                
                columns_info.append({
                    "name": column,
                    "null_count": null_count,
                    "null_percentage": round(null_percentage, 2)
                })
                
                total_missing += null_count
            
            # Sort by null_count descending
            columns_info.sort(key=lambda x: x['null_count'], reverse=True)
            
            total_cells = total_rows * len(df.columns)
            missing_percentage = (total_missing / total_cells * 100) if total_cells > 0 else 0
            
            logger.info(f"Missing values summary generated for dataset {dataset_id}")
            return {
                "total_rows": total_rows,
                "total_columns": len(df.columns),
                "columns": columns_info,
                "total_missing_cells": total_missing,
                "total_cells": total_cells,
                "missing_percentage": round(missing_percentage, 2)
            }
            
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error calculating missing values summary: {e}")
            raise ValidationError(f"Error calculating missing values summary: {str(e)}")
    
    @staticmethod
    def _get_agg_function(aggregation: str):
        """Get Spark aggregation function by name"""
        agg_map = {
            'sum': spark_sum,
            'mean': mean,
            'count': count,
            'min': spark_min,
            'max': spark_max
        }
        return agg_map.get(aggregation, count)
    
    @staticmethod
    def _apply_filter(df: DataFrame, column: str, operator: str, value: Any) -> DataFrame:
        """
        Apply a single filter to DataFrame
        
        Args:
            df: Spark DataFrame
            column: Column name
            operator: Filter operator
            value: Filter value
            
        Returns:
            Filtered DataFrame
        """
        try:
            if operator == 'equals':
                return df.filter(col(column) == value)
            
            elif operator == 'not_equals':
                return df.filter(col(column) != value)
            
            elif operator == 'greater_than':
                return df.filter(col(column) > value)
            
            elif operator == 'less_than':
                return df.filter(col(column) < value)
            
            elif operator == 'greater_equal':
                return df.filter(col(column) >= value)
            
            elif operator == 'less_equal':
                return df.filter(col(column) <= value)
            
            elif operator == 'contains':
                return df.filter(col(column).contains(str(value)))
            
            elif operator == 'starts_with':
                return df.filter(col(column).startswith(str(value)))
            
            elif operator == 'ends_with':
                return df.filter(col(column).endswith(str(value)))
            
            elif operator == 'is_null':
                return df.filter(col(column).isNull())
            
            elif operator == 'is_not_null':
                return df.filter(col(column).isNotNull())
            
            elif operator == 'in':
                if not isinstance(value, list):
                    raise ValidationError(f"'in' operator requires a list value")
                return df.filter(col(column).isin(value))
            
            elif operator == 'not_in':
                if not isinstance(value, list):
                    raise ValidationError(f"'not_in' operator requires a list value")
                return df.filter(~col(column).isin(value))
            
            else:
                raise ValidationError(f"Unsupported operator: {operator}")
                
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error applying filter {operator} on {column}: {e}")
            raise ValidationError(f"Error applying filter: {str(e)}")
