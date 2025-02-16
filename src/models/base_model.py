from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union
import numpy as np
import pandas as pd
from datetime import datetime

class BaseAIModel(ABC):
    """Base class for all AI models in the trading system."""
    
    def __init__(self, name: str, model_params: Dict = None):
        self.name = name
        self.model_params = model_params or {}
        self.model = None
        self.is_trained = False
        self.last_trained = None
        self.performance_metrics = {}
    
    @abstractmethod
    async def train(self, data: Union[pd.DataFrame, np.ndarray], 
                   labels: Optional[Union[pd.Series, np.ndarray]] = None) -> bool:
        """Train the model on historical data."""
        pass
    
    @abstractmethod
    async def predict(self, data: Union[pd.DataFrame, np.ndarray]) -> np.ndarray:
        """Make predictions using the trained model."""
        pass
    
    @abstractmethod
    async def evaluate(self, data: Union[pd.DataFrame, np.ndarray],
                      labels: Union[pd.Series, np.ndarray]) -> Dict:
        """Evaluate model performance on test data."""
        pass
    
    async def preprocess_data(self, data: Union[pd.DataFrame, np.ndarray]) -> Union[pd.DataFrame, np.ndarray]:
        """Preprocess input data before training or prediction."""
        return data
    
    async def validate_data(self, data: Union[pd.DataFrame, np.ndarray]) -> bool:
        """Validate input data format and contents."""
        if data is None or (isinstance(data, (pd.DataFrame, np.ndarray)) and len(data) == 0):
            return False
        return True
    
    async def save_model(self, path: str) -> bool:
        """Save the trained model to disk."""
        try:
            if not self.is_trained:
                raise ValueError("Model is not trained yet")
            # Implement model saving logic here
            return True
        except Exception as e:
            print(f"Error saving model: {str(e)}")
            return False
    
    async def load_model(self, path: str) -> bool:
        """Load a trained model from disk."""
        try:
            # Implement model loading logic here
            self.is_trained = True
            return True
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            return False
    
    async def update_performance_metrics(self, metrics: Dict) -> None:
        """Update model performance metrics."""
        self.performance_metrics.update(metrics)
        self.performance_metrics['last_updated'] = datetime.utcnow()
    
    def get_model_info(self) -> Dict:
        """Get model information and current state."""
        return {
            'name': self.name,
            'is_trained': self.is_trained,
            'last_trained': self.last_trained,
            'model_params': self.model_params,
            'performance_metrics': self.performance_metrics
        }
    
    @abstractmethod
    async def feature_importance(self) -> Dict:
        """Get feature importance scores if applicable."""
        pass
    
    @abstractmethod
    async def explain_prediction(self, data: Union[pd.DataFrame, np.ndarray]) -> Dict:
        """Provide explanation for model predictions if applicable."""
        pass
