"""
Training Service - Business logic for ML model training and management
Handles all ML operations including training, prediction, evaluation, and model lifecycle
"""

import os
import uuid
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, count, when, isnan, lit, udf, array
from pyspark.ml import Pipeline, PipelineModel
from pyspark.ml.feature import (
    VectorAssembler, 
    StandardScaler, 
    StringIndexer,
    IndexToString
)
from pyspark.ml.classification import (
    LogisticRegression,
    DecisionTreeClassifier,
    RandomForestClassifier,
    GBTClassifier
)
from pyspark.ml.regression import (
    LinearRegression,
    DecisionTreeRegressor,
    RandomForestRegressor,
    GBTRegressor
)
from pyspark.ml.clustering import KMeans, BisectingKMeans
from pyspark.ml.evaluation import (
    BinaryClassificationEvaluator,
    MulticlassClassificationEvaluator,
    RegressionEvaluator,
    ClusteringEvaluator
)
from pyspark.mllib.evaluation import MulticlassMetrics

from app.core.spark_manager import SparkManager
from app.core.storage import DatasetStorage, ModelStorage
from app.utils.helpers import pandas_to_spark
from app.utils.exceptions import (
    ValidationError,
    NotFoundError,
    BadRequestError,
    InternalServerError
)

logger = logging.getLogger(__name__)


class TrainingService:
    """
    Service class for ML model training and management operations
    Handles complete ML pipeline from preprocessing to prediction
    """
    
    # Supported algorithms by type
    ALGORITHMS = {
        'classification': {
            'logistic_regression': {
                'class': LogisticRegression,
                'name': 'Logistic Regression',
                'params': ['maxIter', 'regParam', 'elasticNetParam']
            },
            'decision_tree': {
                'class': DecisionTreeClassifier,
                'name': 'Decision Tree',
                'params': ['maxDepth', 'minInstancesPerNode', 'impurity']
            },
            'random_forest': {
                'class': RandomForestClassifier,
                'name': 'Random Forest',
                'params': ['numTrees', 'maxDepth', 'minInstancesPerNode', 'subsamplingRate']
            },
            'gbt': {
                'class': GBTClassifier,
                'name': 'Gradient Boosted Trees',
                'params': ['maxIter', 'maxDepth', 'stepSize']
            }
        },
        'regression': {
            'linear_regression': {
                'class': LinearRegression,
                'name': 'Linear Regression',
                'params': ['maxIter', 'regParam', 'elasticNetParam']
            },
            'decision_tree_reg': {
                'class': DecisionTreeRegressor,
                'name': 'Decision Tree Regressor',
                'params': ['maxDepth', 'minInstancesPerNode', 'impurity']
            },
            'random_forest_reg': {
                'class': RandomForestRegressor,
                'name': 'Random Forest Regressor',
                'params': ['numTrees', 'maxDepth', 'minInstancesPerNode', 'subsamplingRate']
            },
            'gbt_reg': {
                'class': GBTRegressor,
                'name': 'Gradient Boosted Trees Regressor',
                'params': ['maxIter', 'maxDepth', 'stepSize']
            }
        },
        'clustering': {
            'kmeans': {
                'class': KMeans,
                'name': 'K-Means',
                'params': ['k', 'maxIter', 'seed']
            },
            'bisecting_kmeans': {
                'class': BisectingKMeans,
                'name': 'Bisecting K-Means',
                'params': ['k', 'maxIter', 'seed']
            }
        }
    }
    
    @staticmethod
    def get_available_models() -> Dict[str, Any]:
        """
        Get all available ML algorithms organized by type
        
        Returns:
            Dict with classification, regression, and clustering algorithms
        """
        result = {}
        for model_type, algorithms in TrainingService.ALGORITHMS.items():
            result[model_type] = {
                alg_key: {
                    'name': alg_info['name'],
                    'params': alg_info['params']
                }
                for alg_key, alg_info in algorithms.items()
            }
        
        logger.info(f"Retrieved {len(result)} model types with algorithms")
        return result
    
    @staticmethod
    def train(
        dataset_id: str,
        model_type: str,
        algorithm: str,
        features: List[str],
        target: Optional[str],
        params: Optional[Dict[str, Any]] = None,
        test_size: float = 0.3
    ) -> Dict[str, Any]:
        """
        Train an ML model with complete preprocessing pipeline
        
        Args:
            dataset_id: ID of the dataset to use
            model_type: Type of model (classification, regression, clustering)
            algorithm: Algorithm to use
            features: List of feature column names
            target: Target column name (not needed for clustering)
            params: Algorithm hyperparameters
            test_size: Proportion of data for testing (0-1)
            
        Returns:
            Dict with model ID, metrics, and training info
            
        Raises:
            ValidationError: Invalid parameters
            NotFoundError: Dataset not found
            InternalServerError: Training failed
        """
        logger.info(f"Starting training: {model_type}/{algorithm} on dataset {dataset_id}")
        
        TrainingService._validate_training_inputs(
            model_type, algorithm, features, target, test_size
        )
        
        # Get dataset
        df = DatasetStorage.get_dataframe(dataset_id)
        if df is None:
            raise NotFoundError(f"Dataset {dataset_id} not found")
        
        try:
            processed_df = TrainingService._preprocess_data(
                df, features, target, model_type
            )
            
            train_df, test_df = TrainingService._split_data(
                processed_df, test_size
            )
            
            train_count = train_df.count()
            test_count = test_df.count()
            logger.info(f"Data split: {train_count} train, {test_count} test samples")
            
            pipeline_model = TrainingService._build_and_train_pipeline(
                train_df, model_type, algorithm, features, target, params or {}
            )
            
            predictions = pipeline_model.transform(test_df)
            
            metrics = TrainingService._calculate_metrics(
                model_type, predictions, target
            )

            feature_importance = TrainingService._extract_feature_importance(
                pipeline_model, algorithm, features
            )
            if feature_importance:
                metrics['feature_importance'] = feature_importance
            
            model_id = str(uuid.uuid4())
            ModelStorage.add_model(
                id=model_id,
                pipeline_model=pipeline_model,
                model_type=model_type,
                algorithm=algorithm,
                features=features,
                target=target,
                params=params or {},
                metrics=metrics,
                dataset_id=dataset_id,
                train_size=train_count,
                test_size=test_count
            )
            
            logger.info(f"Model {model_id} trained successfully")
            
            return {
                'model_id': model_id,
                'model_type': model_type,
                'algorithm': algorithm,
                'features': features,
                'target': target,
                'metrics': metrics,
                'train_size': train_count,
                'test_size': test_count,
                'created_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Training failed: {str(e)}", exc_info=True)
            raise InternalServerError(f"Training failed: {str(e)}")
    
    @staticmethod
    def list_all() -> List[Dict[str, Any]]:
        """
        List all trained models
        
        Returns:
            List of model information dicts
        """
        models = ModelStorage.list_all()
        logger.info(f"Listed {len(models)} models")
        return models
    
    @staticmethod
    def delete(model_id: str) -> bool:
        """
        Delete a trained model
        
        Args:
            model_id: Model ID
            
        Returns:
            True if deleted successfully
            
        Raises:
            NotFoundError: Model not found
        """
        if not ModelStorage.exists(model_id):
            raise NotFoundError(f"Model {model_id} not found")
        
        deleted = ModelStorage.delete(model_id)
        logger.info(f"Model {model_id} deleted")
        return deleted
    
    # ==================== Private Helper Methods ====================
    
    @staticmethod
    def _validate_training_inputs(
        model_type: str,
        algorithm: str,
        features: List[str],
        target: Optional[str],
        test_size: float
    ) -> None:
        """Validate training inputs"""
        if model_type not in TrainingService.ALGORITHMS:
            raise ValidationError(
                f"Invalid model_type: {model_type}. "
                f"Must be one of: {', '.join(TrainingService.ALGORITHMS.keys())}"
            )
        
        if algorithm not in TrainingService.ALGORITHMS[model_type]:
            valid_algs = ', '.join(TrainingService.ALGORITHMS[model_type].keys())
            raise ValidationError(
                f"Invalid algorithm: {algorithm} for {model_type}. "
                f"Must be one of: {valid_algs}"
            )
        
        if not features or len(features) == 0:
            raise ValidationError("At least one feature must be specified")
        
        if model_type != 'clustering' and not target:
            raise ValidationError(
                f"Target column required for {model_type}"
            )
        
        if test_size <= 0 or test_size >= 1:
            raise ValidationError("test_size must be between 0 and 1")
    
    @staticmethod
    def _preprocess_data(
        df: DataFrame,
        features: List[str],
        target: Optional[str],
        model_type: str
    ) -> DataFrame:
        """
        Preprocess data: handle nulls, select columns
        
        Args:
            df: Input DataFrame
            features: Feature columns
            target: Target column
            model_type: Type of model
            
        Returns:
            Preprocessed DataFrame
        """
        logger.info("Preprocessing data")
        
        # Select relevant columns
        columns_to_select = features.copy()
        if target:
            columns_to_select.append(target)
        
        # Check if columns exist
        missing_cols = set(columns_to_select) - set(df.columns)
        if missing_cols:
            raise ValidationError(
                f"Missing columns in dataset: {', '.join(missing_cols)}"
            )
        
        # Select columns
        df = df.select(columns_to_select)
        
        initial_count = df.count()
        df = df.dropna()
        final_count = df.count()
        
        if final_count < initial_count:
            logger.warning(
                f"Dropped {initial_count - final_count} rows with null values"
            )
        
        if final_count == 0:
            raise ValidationError("No data remaining after removing null values")
        
        return df
    
    @staticmethod
    def _split_data(df: DataFrame, test_size: float) -> Tuple[DataFrame, DataFrame]:
        """Split data into train and test sets"""
        train_size = 1.0 - test_size
        train_df, test_df = df.randomSplit([train_size, test_size], seed=42)
        return train_df, test_df
    
    @staticmethod
    def _build_and_train_pipeline(
        train_df: DataFrame,
        model_type: str,
        algorithm: str,
        features: List[str],
        target: Optional[str],
        params: Dict[str, Any]
    ) -> PipelineModel:
        """
        Build and train ML pipeline with preprocessing
        
        Args:
            train_df: Training DataFrame
            model_type: Type of model
            algorithm: Algorithm to use
            features: Feature columns
            target: Target column
            params: Algorithm parameters
            
        Returns:
            Trained PipelineModel
        """
        logger.info(f"Building pipeline for {model_type}/{algorithm}")
        
        stages = []
        
        # Handle categorical features with StringIndexer
        categorical_features = []
        numerical_features = []
        
        for feature in features:
            dtype = str(train_df.schema[feature].dataType)
            if 'String' in dtype:
                categorical_features.append(feature)
            else:
                numerical_features.append(feature)
        
        # Index categorical features
        indexed_features = []
        for cat_feature in categorical_features:
            indexer = StringIndexer(
                inputCol=cat_feature,
                outputCol=f"{cat_feature}_indexed",
                handleInvalid='keep'
            )
            stages.append(indexer)
            indexed_features.append(f"{cat_feature}_indexed")
        
        all_features = numerical_features + indexed_features
        
        assembler = VectorAssembler(
            inputCols=all_features,
            outputCol='features_raw',
            handleInvalid='skip'
        )
        stages.append(assembler)
        
        scaler = StandardScaler(
            inputCol='features_raw',
            outputCol='features',
            withStd=True,
            withMean=False
        )
        stages.append(scaler)
        
        if model_type in ['classification', 'regression']:
            target_dtype = str(train_df.schema[target].dataType)
            
            if model_type == 'classification':
                if 'String' in target_dtype:
                    label_indexer = StringIndexer(
                        inputCol=target,
                        outputCol='label',
                        handleInvalid='keep'
                    )
                    stages.append(label_indexer)
                else:
                    from pyspark.ml.feature import SQLTransformer
                    sql_transformer = SQLTransformer(
                        statement=f"SELECT *, `{target}` as label FROM __THIS__"
                    )
                    stages.append(sql_transformer)
            else:  # regression
                # For regression, ensure target is numeric
                if 'String' in target_dtype:
                    raise ValidationError(
                        f"Target column '{target}' must be numeric for regression"
                    )
                # Use SQL transformer to rename to label
                from pyspark.ml.feature import SQLTransformer
                sql_transformer = SQLTransformer(
                    statement=f"SELECT *, `{target}` as label FROM __THIS__"
                )
                stages.append(sql_transformer)
        
        model_class = TrainingService.ALGORITHMS[model_type][algorithm]['class']
        
        model_params = TrainingService._build_model_params(
            model_class, params
        )
        
        if model_type == 'clustering':
            model = model_class(featuresCol='features', **model_params)
        else:
            model = model_class(
                featuresCol='features',
                labelCol='label',
                **model_params
            )
        
        stages.append(model)
        
        pipeline = Pipeline(stages=stages)
        
        logger.info(f"Training pipeline with {len(stages)} stages")
        pipeline_model = pipeline.fit(train_df)
        logger.info("Pipeline training complete")
        
        return pipeline_model
    
    @staticmethod
    def _build_model_params(model_class, params: Dict[str, Any]) -> Dict[str, Any]:
        """Build model parameters with type conversion"""
        model_params = {}
        
        param_mapping = {
            'maxIter': ('maxIter', int),
            'regParam': ('regParam', float),
            'elasticNetParam': ('elasticNetParam', float),
            'maxDepth': ('maxDepth', int),
            'minInstancesPerNode': ('minInstancesPerNode', int),
            'impurity': ('impurity', str),
            'numTrees': ('numTrees', int),
            'subsamplingRate': ('subsamplingRate', float),
            'stepSize': ('stepSize', float),
            'k': ('k', int),
            'seed': ('seed', int)
        }
        
        for param_key, param_value in params.items():
            if param_key in param_mapping:
                param_name, param_type = param_mapping[param_key]
                try:
                    model_params[param_name] = param_type(param_value)
                except (ValueError, TypeError):
                    logger.warning(
                        f"Could not convert {param_key}={param_value} to {param_type}"
                    )
        
        return model_params
    
    @staticmethod
    def _calculate_metrics(
        model_type: str,
        predictions: DataFrame,
        target: Optional[str]
    ) -> Dict[str, Any]:
        """
        Calculate evaluation metrics based on model type
        
        Args:
            model_type: Type of model
            predictions: DataFrame with predictions
            target: Target column name
            
        Returns:
            Dict with metrics
        """
        logger.info(f"Calculating {model_type} metrics")
        
        if model_type == 'classification':
            return TrainingService._calculate_classification_metrics(predictions)
        elif model_type == 'regression':
            return TrainingService._calculate_regression_metrics(predictions)
        else:  # clustering
            return TrainingService._calculate_clustering_metrics(predictions)
    
    @staticmethod
    def _calculate_classification_metrics(predictions: DataFrame) -> Dict[str, Any]:
        """Calculate classification metrics"""
        # Basic metrics
        evaluator_accuracy = MulticlassClassificationEvaluator(
            labelCol='label',
            predictionCol='prediction',
            metricName='accuracy'
        )
        accuracy = evaluator_accuracy.evaluate(predictions)
        
        evaluator_f1 = MulticlassClassificationEvaluator(
            labelCol='label',
            predictionCol='prediction',
            metricName='f1'
        )
        f1 = evaluator_f1.evaluate(predictions)
        
        evaluator_precision = MulticlassClassificationEvaluator(
            labelCol='label',
            predictionCol='prediction',
            metricName='weightedPrecision'
        )
        precision = evaluator_precision.evaluate(predictions)
        
        evaluator_recall = MulticlassClassificationEvaluator(
            labelCol='label',
            predictionCol='prediction',
            metricName='weightedRecall'
        )
        recall = evaluator_recall.evaluate(predictions)
        
        # Confusion matrix using MLlib
        predictions_rdd = predictions.select(['prediction', 'label']).rdd.map(
            lambda row: (float(row['prediction']), float(row['label']))
        )
        metrics = MulticlassMetrics(predictions_rdd)
        confusion_matrix = metrics.confusionMatrix().toArray().tolist()
        
        result = {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1': float(f1),
            'confusion_matrix': confusion_matrix
        }
        
        # Try to calculate ROC AUC for binary classification
        try:
            n_classes = len(confusion_matrix)
            if n_classes == 2:
                binary_evaluator = BinaryClassificationEvaluator(
                    labelCol='label',
                    rawPredictionCol='rawPrediction',
                    metricName='areaUnderROC'
                )
                roc_auc = binary_evaluator.evaluate(predictions)
                result['roc_auc'] = float(roc_auc)
        except Exception as e:
            logger.warning(f"Could not calculate ROC AUC: {str(e)}")
        
        return result
    
    @staticmethod
    def _calculate_regression_metrics(predictions: DataFrame) -> Dict[str, Any]:
        """Calculate regression metrics"""
        evaluator_rmse = RegressionEvaluator(
            labelCol='label',
            predictionCol='prediction',
            metricName='rmse'
        )
        rmse = evaluator_rmse.evaluate(predictions)
        
        evaluator_mae = RegressionEvaluator(
            labelCol='label',
            predictionCol='prediction',
            metricName='mae'
        )
        mae = evaluator_mae.evaluate(predictions)
        
        evaluator_r2 = RegressionEvaluator(
            labelCol='label',
            predictionCol='prediction',
            metricName='r2'
        )
        r2 = evaluator_r2.evaluate(predictions)
        
        # Get sample predictions vs actual for visualization
        sample_data = predictions.select('label', 'prediction').limit(100).collect()
        prediction_vs_actual = [
            {'actual': float(row['label']), 'predicted': float(row['prediction'])}
            for row in sample_data
        ]
        
        return {
            'rmse': float(rmse),
            'mae': float(mae),
            'r2': float(r2),
            'prediction_vs_actual': prediction_vs_actual
        }
    
    @staticmethod
    def _calculate_clustering_metrics(predictions: DataFrame) -> Dict[str, Any]:
        """Calculate clustering metrics"""
        # Silhouette score
        evaluator = ClusteringEvaluator(
            featuresCol='features',
            predictionCol='prediction',
            metricName='silhouette'
        )
        silhouette = evaluator.evaluate(predictions)
        
        # Cluster distribution
        cluster_dist = predictions.groupBy('prediction').count().collect()
        cluster_distribution = {
            f'cluster_{int(row["prediction"])}': int(row['count'])
            for row in cluster_dist
        }
        
        # Try to get cluster centers
        cluster_centers = []
        try:
            # This would work if we had access to the model directly
            # For now, we'll skip this as it requires model extraction
            pass
        except Exception as e:
            logger.warning(f"Could not extract cluster centers: {str(e)}")
        
        result = {
            'silhouette_score': float(silhouette),
            'cluster_distribution': cluster_distribution,
            'num_clusters': len(cluster_distribution)
        }
        
        if cluster_centers:
            result['cluster_centers'] = cluster_centers
        
        return result
    
    @staticmethod
    def _extract_feature_importance(
        pipeline_model: PipelineModel,
        algorithm: str,
        features: List[str]
    ) -> Optional[Dict[str, float]]:
        """
        Extract feature importance from tree-based models
        
        Args:
            pipeline_model: Trained pipeline
            algorithm: Algorithm name
            features: Feature names
            
        Returns:
            Dict mapping feature names to importance scores, or None
        """
        tree_based = ['decision_tree', 'random_forest', 'gbt', 
                      'decision_tree_reg', 'random_forest_reg', 'gbt_reg']
        
        if algorithm not in tree_based:
            return None
        
        try:
            # Get the last stage (the model)
            model = pipeline_model.stages[-1]
            
            # Check if model has featureImportances
            if not hasattr(model, 'featureImportances'):
                return None
            
            importances = model.featureImportances.toArray()
            
            # Get actual feature names (accounting for indexed categorical features)
            # We need to map back to original feature names
            feature_assembler = None
            for stage in pipeline_model.stages:
                if isinstance(stage, VectorAssembler):
                    feature_assembler = stage
                    break
            
            if feature_assembler:
                assembled_features = feature_assembler.getInputCols()
            else:
                assembled_features = features
            
            # Create importance dict
            importance_dict = {}
            for i, importance in enumerate(importances):
                if i < len(assembled_features):
                    feature_name = assembled_features[i]
                    # Remove '_indexed' suffix if present
                    if feature_name.endswith('_indexed'):
                        feature_name = feature_name[:-8]
                    importance_dict[feature_name] = float(importance)
            
            # Sort by importance
            importance_dict = dict(
                sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
            )
            
            return importance_dict
            
        except Exception as e:
            logger.warning(f"Could not extract feature importance: {str(e)}")
            return None
