import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.services.indian_trading_features import IndianTradingFeatures
from src.services.indian_broker_service import IndianBrokerService
from src.ai.models.price_prediction import AITradingSystem

@pytest.fixture
def trading_features():
    broker_service = IndianBrokerService()
    return IndianTradingFeatures(broker_service)

@pytest.fixture
def ai_system():
    return AITradingSystem()

@pytest.fixture
def sample_market_data():
    dates = pd.date_range(start='2025-01-01', end='2025-02-16', freq='D')
    data = pd.DataFrame({
        'open': np.random.uniform(100, 200, len(dates)),
        'high': np.random.uniform(150, 250, len(dates)),
        'low': np.random.uniform(90, 180, len(dates)),
        'close': np.random.uniform(100, 200, len(dates)),
        'volume': np.random.uniform(1000000, 5000000, len(dates))
    }, index=dates)
    return data

def test_market_hours(trading_features):
    # Test during market hours
    current_time = datetime.strptime('09:30:00', '%H:%M:%S').time()
    assert trading_features.is_market_open(current_time) == True
    
    # Test before market hours
    current_time = datetime.strptime('08:30:00', '%H:%M:%S').time()
    assert trading_features.is_market_open(current_time) == False
    
    # Test after market hours
    current_time = datetime.strptime('16:30:00', '%H:%M:%S').time()
    assert trading_features.is_market_open(current_time) == False

def test_position_size_calculation(trading_features):
    position_size = trading_features.calculate_position_size(
        capital=100000,
        risk_per_trade=1,
        stop_loss=495,
        entry_price=500
    )
    assert position_size > 0
    assert isinstance(position_size, int)

def test_technical_indicators(trading_features, sample_market_data):
    indicators = trading_features.calculate_intraday_indicators(sample_market_data)
    
    assert 'SMA_20' in indicators
    assert 'RSI' in indicators
    assert 'MACD' in indicators
    assert 'Signal_Line' in indicators
    assert 'BB_Upper' in indicators
    assert 'BB_Lower' in indicators

def test_ai_price_prediction(ai_system, sample_market_data):
    # Initialize price predictor
    ai_system.initialize_price_predictor(
        input_dim=5,  # OHLCV
        hidden_dim=64,
        num_layers=2
    )
    
    # Prepare data
    sequence_length = 10
    X, y, scaler = ai_system.prepare_data(
        data=sample_market_data,
        sequence_length=sequence_length
    )
    
    assert X is not None
    assert y is not None
    assert scaler is not None
    
    # Make prediction
    prediction = ai_system.predict_price(X[:1], scaler)
    assert isinstance(prediction, float)

def test_sentiment_analysis(ai_system):
    news_texts = [
        "Company XYZ reports strong quarterly earnings, beating market expectations",
        "Market shows signs of weakness amid global economic concerns"
    ]
    
    sentiment = ai_system.analyze_market_sentiment(news_texts)
    
    assert 'positive' in sentiment
    assert 'negative' in sentiment
    assert 'neutral' in sentiment
    assert sum(sentiment.values()) == pytest.approx(1.0)

def test_market_regime_classification(ai_system, sample_market_data):
    regime = ai_system.get_market_regime(sample_market_data)
    
    assert regime in [
        'Bullish Volatile',
        'Bearish Volatile',
        'Bullish Stable',
        'Bearish Stable'
    ]

def test_trading_signals(ai_system):
    signal = ai_system.generate_trading_signals(
        price_prediction=105,
        current_price=100,
        sentiment={'positive': 0.7, 'negative': 0.2, 'neutral': 0.1},
        market_regime='Bullish Stable',
        threshold=0.02
    )
    
    assert 'action' in signal
    assert signal['action'] in ['BUY', 'SELL', 'HOLD']
    assert 'confidence' in signal
    assert 0 <= signal['confidence'] <= 1
    assert 'factors' in signal
