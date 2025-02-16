from typing import Dict, List, Optional, Union
import numpy as np
import pandas as pd
from datetime import datetime
from transformers import pipeline
from .base_model import BaseAIModel

class SentimentModel(BaseAIModel):
    """Sentiment analysis model for market sentiment prediction."""
    
    def __init__(self, name: str = "sentiment_analyzer", model_name: str = "finbert"):
        super().__init__(name)
        self.model_name = model_name
        self.sentiment_analyzer = None
        self.sentiment_labels = ['positive', 'negative', 'neutral']
    
    async def train(self, data: Union[pd.DataFrame, np.ndarray],
                   labels: Optional[Union[pd.Series, np.ndarray]] = None) -> bool:
        """
        Initialize the sentiment analyzer.
        Note: We're using a pre-trained model, so no training is required.
        """
        try:
            self.sentiment_analyzer = pipeline("sentiment-analysis",
                                            model=self.model_name)
            self.is_trained = True
            self.last_trained = datetime.utcnow()
            return True
        except Exception as e:
            print(f"Error initializing sentiment analyzer: {str(e)}")
            return False
    
    async def predict(self, data: Union[pd.DataFrame, np.ndarray]) -> np.ndarray:
        """Predict sentiment scores for input text data."""
        try:
            if not self.is_trained:
                raise ValueError("Model is not initialized")
            
            if isinstance(data, pd.DataFrame):
                texts = data['text'].tolist()
            elif isinstance(data, np.ndarray):
                texts = data.tolist()
            else:
                texts = data
            
            results = self.sentiment_analyzer(texts)
            
            # Convert results to numpy array of sentiment scores
            sentiment_scores = np.array([
                [1 if r['label'] == 'positive' else -1 if r['label'] == 'negative' else 0
                 for r in results]
            ])
            
            return sentiment_scores
        except Exception as e:
            print(f"Error predicting sentiment: {str(e)}")
            return np.array([])
    
    async def evaluate(self, data: Union[pd.DataFrame, np.ndarray],
                      labels: Union[pd.Series, np.ndarray]) -> Dict:
        """Evaluate sentiment model performance."""
        try:
            predictions = await self.predict(data)
            
            # Calculate accuracy
            accuracy = np.mean(predictions == labels)
            
            # Calculate precision, recall, and F1 score for each sentiment class
            metrics = {
                'accuracy': accuracy,
                'precision': {},
                'recall': {},
                'f1_score': {}
            }
            
            for label in self.sentiment_labels:
                pred_mask = predictions == label
                true_mask = labels == label
                
                true_positives = np.sum(pred_mask & true_mask)
                false_positives = np.sum(pred_mask & ~true_mask)
                false_negatives = np.sum(~pred_mask & true_mask)
                
                precision = true_positives / (true_positives + false_positives)
                recall = true_positives / (true_positives + false_negatives)
                f1 = 2 * (precision * recall) / (precision + recall)
                
                metrics['precision'][label] = precision
                metrics['recall'][label] = recall
                metrics['f1_score'][label] = f1
            
            await self.update_performance_metrics(metrics)
            return metrics
        except Exception as e:
            print(f"Error evaluating model: {str(e)}")
            return {}
    
    async def preprocess_data(self, data: Union[pd.DataFrame, np.ndarray]) -> Union[pd.DataFrame, np.ndarray]:
        """Preprocess text data for sentiment analysis."""
        try:
            if isinstance(data, pd.DataFrame):
                # Clean text data
                data['text'] = data['text'].str.lower()
                data['text'] = data['text'].str.replace(r'http\S+|www.\S+', '', regex=True)
                data['text'] = data['text'].str.replace(r'[^\w\s]', '', regex=True)
                return data
            elif isinstance(data, np.ndarray):
                # Convert numpy array to DataFrame for text processing
                df = pd.DataFrame({'text': data})
                return await self.preprocess_data(df)
            return data
        except Exception as e:
            print(f"Error preprocessing data: {str(e)}")
            return data
    
    async def feature_importance(self) -> Dict:
        """
        Get feature importance for sentiment analysis.
        For transformer models, we can return attention weights.
        """
        return {"message": "Feature importance not implemented for transformer models"}
    
    async def explain_prediction(self, data: Union[pd.DataFrame, np.ndarray]) -> Dict:
        """Provide explanation for sentiment predictions."""
        try:
            if isinstance(data, pd.DataFrame):
                text = data['text'].iloc[0]
            else:
                text = data[0]
            
            # Get sentiment prediction with confidence scores
            result = self.sentiment_analyzer(text)[0]
            
            explanation = {
                'text': text,
                'predicted_sentiment': result['label'],
                'confidence': result['score'],
                'analysis': f"The text was classified as {result['label']} with "
                          f"{result['score']*100:.2f}% confidence."
            }
            
            return explanation
        except Exception as e:
            print(f"Error explaining prediction: {str(e)}")
            return {}
