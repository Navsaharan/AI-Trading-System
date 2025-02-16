from typing import Dict, List, Optional, Union
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import torch
import torch.nn as nn
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
import joblib
import os
import json
from concurrent.futures import ThreadPoolExecutor
import talib
import xgboost as xgb
from lightgbm import LGBMRegressor
import tensorflow as tf

class MarketPredictor(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers):
        super(MarketPredictor, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)
        
    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        predictions = self.fc(lstm_out[:, -1, :])
        return predictions

class FreeAIService:
    def __init__(self):
        self.models_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Initialize models
        self.market_predictor = self._load_or_create_market_predictor()
        self.sentiment_model = self._load_sentiment_model()
        self.technical_analyzer = self._load_technical_model()
        self.portfolio_optimizer = self._load_portfolio_model()
        
        # Initialize tokenizer for sentiment analysis
        self.tokenizer = AutoTokenizer.from_pretrained('ProsusAI/finbert')
        
        # Initialize optimization tools
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    def _load_or_create_market_predictor(self) -> MarketPredictor:
        """Load or create market prediction model"""
        model_path = os.path.join(self.models_dir, 'market_predictor.pth')
        
        if os.path.exists(model_path):
            model = MarketPredictor(input_size=10, hidden_size=64, num_layers=2)
            model.load_state_dict(torch.load(model_path))
        else:
            model = MarketPredictor(input_size=10, hidden_size=64, num_layers=2)
            
        model.to(self.device)
        return model

    def _load_sentiment_model(self):
        """Load sentiment analysis model"""
        return AutoModelForSequenceClassification.from_pretrained('ProsusAI/finbert')

    def _load_technical_model(self):
        """Load technical analysis model"""
        model_path = os.path.join(self.models_dir, 'technical_model.joblib')
        
        if os.path.exists(model_path):
            return joblib.load(model_path)
        
        return RandomForestClassifier(n_estimators=100, random_state=42)

    def _load_portfolio_model(self):
        """Load portfolio optimization model"""
        model_path = os.path.join(self.models_dir, 'portfolio_model.joblib')
        
        if os.path.exists(model_path):
            return joblib.load(model_path)
        
        return GradientBoostingRegressor(n_estimators=100, random_state=42)

    async def predict_market_movement(self, data: pd.DataFrame) -> Dict:
        """Predict market movement using LSTM model"""
        try:
            # Prepare data
            X = self._prepare_market_data(data)
            X_tensor = torch.FloatTensor(X).to(self.device)
            
            # Make prediction
            self.market_predictor.eval()
            with torch.no_grad():
                predictions = self.market_predictor(X_tensor)
            
            # Calculate confidence
            confidence = self._calculate_prediction_confidence(predictions)
            
            return {
                "prediction": predictions.cpu().numpy()[0][0],
                "confidence": confidence,
                "timestamp": datetime.now()
            }

        except Exception as e:
            print(f"Error predicting market movement: {e}")
            return {}

    async def analyze_sentiment(self, texts: List[str]) -> List[Dict]:
        """Analyze sentiment of market-related texts"""
        try:
            results = []
            
            # Process texts in batches
            batch_size = 8
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                # Tokenize
                inputs = self.tokenizer(
                    batch,
                    padding=True,
                    truncation=True,
                    return_tensors="pt"
                ).to(self.device)
                
                # Get predictions
                outputs = self.sentiment_model(**inputs)
                predictions = torch.softmax(outputs.logits, dim=1)
                
                # Process results
                for text, pred in zip(batch, predictions):
                    sentiment_score = pred[1].item()  # Positive sentiment score
                    results.append({
                        "text": text,
                        "sentiment": "positive" if sentiment_score > 0.5 else "negative",
                        "score": sentiment_score,
                        "confidence": max(pred).item()
                    })
            
            return results

        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return []

    async def analyze_technical_indicators(self, data: pd.DataFrame) -> Dict:
        """Analyze technical indicators"""
        try:
            # Calculate technical indicators
            indicators = self._calculate_technical_indicators(data)
            
            # Make prediction
            prediction = self.technical_analyzer.predict_proba(indicators)
            
            # Generate signals
            signals = self._generate_technical_signals(prediction, indicators)
            
            return {
                "signals": signals,
                "indicators": indicators.to_dict(),
                "prediction": prediction.tolist(),
                "timestamp": datetime.now()
            }

        except Exception as e:
            print(f"Error analyzing technical indicators: {e}")
            return {}

    async def optimize_portfolio(self, portfolio: Dict, market_data: pd.DataFrame) -> Dict:
        """Optimize portfolio allocation"""
        try:
            # Prepare portfolio data
            portfolio_features = self._prepare_portfolio_data(portfolio, market_data)
            
            # Generate optimization suggestions
            suggestions = self._generate_portfolio_suggestions(portfolio_features)
            
            # Calculate expected returns
            returns = self._calculate_expected_returns(suggestions, market_data)
            
            return {
                "current_allocation": portfolio,
                "suggested_allocation": suggestions,
                "expected_returns": returns,
                "risk_metrics": self._calculate_risk_metrics(suggestions, market_data)
            }

        except Exception as e:
            print(f"Error optimizing portfolio: {e}")
            return {}

    def _prepare_market_data(self, data: pd.DataFrame) -> np.ndarray:
        """Prepare market data for prediction"""
        features = []
        
        # Calculate technical indicators
        data['RSI'] = talib.RSI(data['close'])
        data['MACD'], _, _ = talib.MACD(data['close'])
        data['ATR'] = talib.ATR(data['high'], data['low'], data['close'])
        
        # Create feature matrix
        for col in ['open', 'high', 'low', 'close', 'volume', 'RSI', 'MACD', 'ATR']:
            if col in data.columns:
                features.append(data[col].values)
        
        return np.stack(features, axis=1)

    def _calculate_prediction_confidence(self, predictions: torch.Tensor) -> float:
        """Calculate confidence score for predictions"""
        # Implementation for confidence calculation
        return float(torch.sigmoid(predictions.std()))

    def _calculate_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators"""
        indicators = pd.DataFrame()
        
        # Price-based indicators
        indicators['RSI'] = talib.RSI(data['close'])
        indicators['MACD'], _, _ = talib.MACD(data['close'])
        indicators['ATR'] = talib.ATR(data['high'], data['low'], data['close'])
        indicators['OBV'] = talib.OBV(data['close'], data['volume'])
        
        # Moving averages
        indicators['SMA_20'] = talib.SMA(data['close'], timeperiod=20)
        indicators['EMA_20'] = talib.EMA(data['close'], timeperiod=20)
        
        # Momentum indicators
        indicators['MOM'] = talib.MOM(data['close'], timeperiod=10)
        indicators['ROC'] = talib.ROC(data['close'], timeperiod=10)
        
        return indicators.dropna()

    def _generate_technical_signals(self, prediction: np.ndarray, indicators: pd.DataFrame) -> List[Dict]:
        """Generate trading signals from technical analysis"""
        signals = []
        
        # Example signal generation logic
        if prediction[0][1] > 0.7:  # Strong buy signal
            signals.append({
                "type": "buy",
                "strength": "strong",
                "confidence": float(prediction[0][1])
            })
        elif prediction[0][0] > 0.7:  # Strong sell signal
            signals.append({
                "type": "sell",
                "strength": "strong",
                "confidence": float(prediction[0][0])
            })
        
        return signals

    def _prepare_portfolio_data(self, portfolio: Dict, market_data: pd.DataFrame) -> pd.DataFrame:
        """Prepare portfolio data for optimization"""
        features = pd.DataFrame()
        
        # Calculate portfolio metrics
        for symbol, allocation in portfolio.items():
            if symbol in market_data.columns:
                features[f"{symbol}_return"] = market_data[symbol].pct_change()
                features[f"{symbol}_volatility"] = features[f"{symbol}_return"].rolling(20).std()
                features[f"{symbol}_sharpe"] = features[f"{symbol}_return"].mean() / features[f"{symbol}_volatility"]
        
        return features.dropna()

    def _generate_portfolio_suggestions(self, features: pd.DataFrame) -> Dict:
        """Generate portfolio optimization suggestions"""
        suggestions = {}
        
        # Example optimization logic
        total_sharpe = features.filter(like='sharpe').sum().sum()
        
        for col in features.columns:
            if 'sharpe' in col:
                symbol = col.split('_')[0]
                suggestions[symbol] = features[col].sum() / total_sharpe
        
        return suggestions

    def _calculate_expected_returns(self, allocation: Dict, market_data: pd.DataFrame) -> Dict:
        """Calculate expected returns for portfolio allocation"""
        returns = {}
        
        for symbol, weight in allocation.items():
            if symbol in market_data.columns:
                historical_returns = market_data[symbol].pct_change().mean()
                returns[symbol] = historical_returns * weight
        
        returns['total'] = sum(returns.values())
        return returns

    def _calculate_risk_metrics(self, allocation: Dict, market_data: pd.DataFrame) -> Dict:
        """Calculate risk metrics for portfolio"""
        returns = pd.DataFrame()
        
        # Calculate portfolio returns
        for symbol, weight in allocation.items():
            if symbol in market_data.columns:
                returns[symbol] = market_data[symbol].pct_change() * weight
        
        portfolio_returns = returns.sum(axis=1)
        
        return {
            "volatility": portfolio_returns.std(),
            "sharpe_ratio": portfolio_returns.mean() / portfolio_returns.std(),
            "max_drawdown": (portfolio_returns.cummax() - portfolio_returns).max(),
            "var_95": portfolio_returns.quantile(0.05)
        }
