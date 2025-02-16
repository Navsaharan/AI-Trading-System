import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List, Optional
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import logging

class LSTMPricePredictor(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int, num_layers: int, output_dim: int):
        super(LSTMPricePredictor, self).__init__()
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_dim, output_dim)
        
    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim).to(x.device)
        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :])
        return out

class TransformerSentimentAnalyzer:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained('ProsusAI/finbert')
        self.model = AutoModelForSequenceClassification.from_pretrained('ProsusAI/finbert')
        
    def analyze_sentiment(self, texts: List[str]) -> List[Dict[str, float]]:
        inputs = self.tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
        outputs = self.model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        return [{
            'positive': float(p[0]),
            'negative': float(p[1]),
            'neutral': float(p[2])
        } for p in probs]

class MarketRegimeClassifier:
    def __init__(self, n_clusters: int = 4):
        self.n_clusters = n_clusters
        self.scaler = MinMaxScaler()
        
    def identify_regime(self, data: pd.DataFrame) -> str:
        features = self._extract_features(data)
        regime = self._classify_regime(features)
        return regime
        
    def _extract_features(self, data: pd.DataFrame) -> np.ndarray:
        # Calculate technical features
        returns = data['close'].pct_change()
        volatility = returns.rolling(window=20).std()
        momentum = returns.rolling(window=10).mean()
        
        features = np.column_stack([
            returns.fillna(0),
            volatility.fillna(0),
            momentum.fillna(0)
        ])
        
        return self.scaler.fit_transform(features)
        
    def _classify_regime(self, features: np.ndarray) -> str:
        # Simple regime classification based on volatility and momentum
        vol = features[:, 1].mean()
        mom = features[:, 2].mean()
        
        if vol > 0.7 and mom > 0:
            return 'Bullish Volatile'
        elif vol > 0.7 and mom < 0:
            return 'Bearish Volatile'
        elif vol <= 0.7 and mom > 0:
            return 'Bullish Stable'
        else:
            return 'Bearish Stable'

class AITradingSystem:
    def __init__(self):
        self.price_predictor = None
        self.sentiment_analyzer = TransformerSentimentAnalyzer()
        self.regime_classifier = MarketRegimeClassifier()
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def initialize_price_predictor(
        self,
        input_dim: int,
        hidden_dim: int = 64,
        num_layers: int = 2,
        output_dim: int = 1
    ):
        self.price_predictor = LSTMPricePredictor(
            input_dim=input_dim,
            hidden_dim=hidden_dim,
            num_layers=num_layers,
            output_dim=output_dim
        )
        
    def prepare_data(
        self,
        data: pd.DataFrame,
        sequence_length: int,
        target_column: str = 'close'
    ) -> tuple:
        """Prepare data for LSTM model"""
        try:
            # Normalize data
            scaler = MinMaxScaler()
            scaled_data = scaler.fit_transform(data)
            
            # Create sequences
            X, y = [], []
            for i in range(len(scaled_data) - sequence_length):
                X.append(scaled_data[i:(i + sequence_length)])
                y.append(scaled_data[i + sequence_length, data.columns.get_loc(target_column)])
                
            return (
                torch.FloatTensor(np.array(X)),
                torch.FloatTensor(np.array(y)),
                scaler
            )
        except Exception as e:
            self.logger.error(f"Error preparing data: {e}")
            return None, None, None
            
    def train_price_predictor(
        self,
        train_data: torch.Tensor,
        train_labels: torch.Tensor,
        epochs: int = 100,
        learning_rate: float = 0.01
    ):
        """Train the LSTM price predictor"""
        try:
            criterion = nn.MSELoss()
            optimizer = torch.optim.Adam(self.price_predictor.parameters(), lr=learning_rate)
            
            for epoch in range(epochs):
                self.price_predictor.train()
                optimizer.zero_grad()
                
                # Forward pass
                outputs = self.price_predictor(train_data)
                loss = criterion(outputs, train_labels)
                
                # Backward pass and optimize
                loss.backward()
                optimizer.step()
                
                if (epoch + 1) % 10 == 0:
                    self.logger.info(f'Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}')
                    
        except Exception as e:
            self.logger.error(f"Error training model: {e}")
            
    def predict_price(
        self,
        input_sequence: torch.Tensor,
        scaler: MinMaxScaler
    ) -> Optional[float]:
        """Predict future price"""
        try:
            self.price_predictor.eval()
            with torch.no_grad():
                predicted = self.price_predictor(input_sequence)
                predicted = scaler.inverse_transform(predicted.numpy())
                return float(predicted[0, 0])
        except Exception as e:
            self.logger.error(f"Error predicting price: {e}")
            return None
            
    def analyze_market_sentiment(self, news_texts: List[str]) -> Dict[str, float]:
        """Analyze market sentiment from news"""
        try:
            sentiments = self.sentiment_analyzer.analyze_sentiment(news_texts)
            avg_sentiment = {
                'positive': sum(s['positive'] for s in sentiments) / len(sentiments),
                'negative': sum(s['negative'] for s in sentiments) / len(sentiments),
                'neutral': sum(s['neutral'] for s in sentiments) / len(sentiments)
            }
            return avg_sentiment
        except Exception as e:
            self.logger.error(f"Error analyzing sentiment: {e}")
            return {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}
            
    def get_market_regime(self, market_data: pd.DataFrame) -> str:
        """Identify current market regime"""
        try:
            return self.regime_classifier.identify_regime(market_data)
        except Exception as e:
            self.logger.error(f"Error identifying market regime: {e}")
            return 'Unknown'
            
    def generate_trading_signals(
        self,
        price_prediction: float,
        current_price: float,
        sentiment: Dict[str, float],
        market_regime: str,
        threshold: float = 0.02
    ) -> Dict[str, any]:
        """Generate trading signals based on AI analysis"""
        try:
            # Calculate predicted return
            predicted_return = (price_prediction - current_price) / current_price
            
            # Initialize signal
            signal = {
                'action': 'HOLD',
                'confidence': 0.0,
                'factors': {
                    'price_prediction': predicted_return,
                    'sentiment': sentiment,
                    'market_regime': market_regime
                }
            }
            
            # Determine signal based on multiple factors
            price_signal = 1 if predicted_return > threshold else (-1 if predicted_return < -threshold else 0)
            sentiment_signal = 1 if sentiment['positive'] > 0.6 else (-1 if sentiment['negative'] > 0.6 else 0)
            regime_signal = 1 if 'Bullish' in market_regime else (-1 if 'Bearish' in market_regime else 0)
            
            # Combine signals with weights
            combined_signal = (
                0.5 * price_signal +
                0.3 * sentiment_signal +
                0.2 * regime_signal
            )
            
            # Set final signal
            if combined_signal > 0.3:
                signal['action'] = 'BUY'
                signal['confidence'] = combined_signal
            elif combined_signal < -0.3:
                signal['action'] = 'SELL'
                signal['confidence'] = abs(combined_signal)
                
            return signal
            
        except Exception as e:
            self.logger.error(f"Error generating trading signals: {e}")
            return {'action': 'HOLD', 'confidence': 0.0, 'factors': {}}
