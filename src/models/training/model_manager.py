import os
import mlflow
import optuna
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union
from datetime import datetime
import tensorflow as tf
import torch
import pytorch_lightning as pl
from sklearn.model_selection import train_test_split
from ..base_model import BaseAIModel

class ModelManager:
    """Manages AI model training, optimization, and deployment."""
    
    def __init__(self, model_dir: str = "models", experiment_name: str = "trading_models"):
        self.model_dir = model_dir
        self.experiment_name = experiment_name
        self.models = {}
        self.active_models = {}
        
        # Initialize MLflow
        mlflow.set_tracking_uri("sqlite:///mlflow.db")
        self.experiment = mlflow.get_or_create_experiment(experiment_name)
        
        # Initialize GPU settings
        self.setup_gpu()
    
    def setup_gpu(self):
        """Configure GPU settings for optimal performance."""
        try:
            # TensorFlow GPU configuration
            gpus = tf.config.list_physical_devices('GPU')
            if gpus:
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)
            
            # PyTorch GPU configuration
            if torch.cuda.is_available():
                torch.backends.cudnn.benchmark = True
        except Exception as e:
            print(f"GPU setup warning: {str(e)}")
    
    async def train_model(self, model: BaseAIModel, data: pd.DataFrame,
                         model_type: str, hyperparameters: Dict = None) -> bool:
        """Train an AI model with optional hyperparameter optimization."""
        try:
            # Start MLflow run
            with mlflow.start_run(experiment_id=self.experiment.experiment_id) as run:
                # Log basic parameters
                mlflow.log_params({
                    "model_type": model_type,
                    "data_size": len(data),
                    "features": list(data.columns)
                })
                
                # Split data
                train_data, val_data = train_test_split(data, test_size=0.2)
                
                # Hyperparameter optimization if not provided
                if not hyperparameters:
                    hyperparameters = await self.optimize_hyperparameters(
                        model, train_data, val_data, model_type
                    )
                
                # Train model
                model.model_params.update(hyperparameters)
                success = await model.train(train_data)
                
                if success:
                    # Evaluate model
                    metrics = await model.evaluate(val_data, val_data['target'])
                    
                    # Log metrics
                    mlflow.log_metrics(metrics)
                    
                    # Save model
                    model_path = os.path.join(self.model_dir, f"{model_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                    await model.save_model(model_path)
                    mlflow.log_artifact(model_path)
                    
                    # Register model
                    self.models[model_type] = model
                    return True
                
                return False
        except Exception as e:
            print(f"Error training model: {str(e)}")
            return False
    
    async def optimize_hyperparameters(self, model: BaseAIModel, train_data: pd.DataFrame,
                                     val_data: pd.DataFrame, model_type: str) -> Dict:
        """Optimize model hyperparameters using Optuna."""
        def objective(trial):
            # Define hyperparameter search space based on model type
            if model_type == "technical":
                params = {
                    "n_layers": trial.suggest_int("n_layers", 2, 5),
                    "hidden_size": trial.suggest_int("hidden_size", 32, 256),
                    "learning_rate": trial.suggest_loguniform("learning_rate", 1e-5, 1e-2),
                    "dropout": trial.suggest_float("dropout", 0.1, 0.5)
                }
            elif model_type == "sentiment":
                params = {
                    "batch_size": trial.suggest_int("batch_size", 16, 128),
                    "max_length": trial.suggest_int("max_length", 64, 512),
                    "learning_rate": trial.suggest_loguniform("learning_rate", 1e-5, 1e-3)
                }
            else:
                params = {
                    "n_estimators": trial.suggest_int("n_estimators", 100, 1000),
                    "max_depth": trial.suggest_int("max_depth", 3, 10),
                    "learning_rate": trial.suggest_loguniform("learning_rate", 1e-3, 1e-1)
                }
            
            # Update model parameters
            model.model_params.update(params)
            
            # Train and evaluate
            await model.train(train_data)
            metrics = await model.evaluate(val_data, val_data['target'])
            
            return metrics.get('accuracy', 0)
        
        # Create study
        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=20)
        
        return study.best_params
    
    async def deploy_model(self, model_type: str, version: str = "latest") -> bool:
        """Deploy a trained model for production use."""
        try:
            if model_type not in self.models:
                return False
            
            model = self.models[model_type]
            self.active_models[model_type] = model
            
            # Log deployment
            with mlflow.start_run(experiment_id=self.experiment.experiment_id) as run:
                mlflow.log_param("deployment_version", version)
                mlflow.log_param("deployment_time", datetime.now().isoformat())
            
            return True
        except Exception as e:
            print(f"Error deploying model: {str(e)}")
            return False
    
    async def predict(self, model_type: str, data: pd.DataFrame) -> np.ndarray:
        """Make predictions using deployed model."""
        if model_type not in self.active_models:
            raise ValueError(f"No active model found for type: {model_type}")
        
        model = self.active_models[model_type]
        return await model.predict(data)
    
    async def update_model(self, model_type: str, new_data: pd.DataFrame) -> bool:
        """Update an existing model with new data."""
        try:
            if model_type not in self.models:
                return False
            
            model = self.models[model_type]
            
            # Incremental training
            success = await model.train(new_data)
            
            if success:
                # Update active model if deployed
                if model_type in self.active_models:
                    self.active_models[model_type] = model
                return True
            
            return False
        except Exception as e:
            print(f"Error updating model: {str(e)}")
            return False
    
    def get_model_info(self, model_type: str) -> Dict:
        """Get information about a specific model."""
        if model_type not in self.models:
            return {}
        
        model = self.models[model_type]
        return model.get_model_info()
    
    async def evaluate_all_models(self, test_data: pd.DataFrame) -> Dict:
        """Evaluate all active models on test data."""
        results = {}
        for model_type, model in self.active_models.items():
            metrics = await model.evaluate(test_data, test_data['target'])
            results[model_type] = metrics
        return results
    
    def list_available_models(self) -> List[str]:
        """List all available model types."""
        return list(self.models.keys())
    
    def is_model_active(self, model_type: str) -> bool:
        """Check if a model is currently active/deployed."""
        return model_type in self.active_models
