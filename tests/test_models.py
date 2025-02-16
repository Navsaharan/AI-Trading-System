import pytest
import torch
import numpy as np
import pandas as pd
from src.ai.models.price_prediction import (
    LSTMPricePredictor,
    TransformerSentimentAnalyzer,
    MarketRegimeClassifier,
    AITradingSystem
)

@pytest.fixture
def lstm_model():
    return LSTMPricePredictor(
        input_dim=5,  # OHLCV
        hidden_dim=64,
        num_layers=2,
        output_dim=1
    )

@pytest.fixture
def sentiment_analyzer():
    return TransformerSentimentAnalyzer()

@pytest.fixture
def regime_classifier():
    return MarketRegimeClassifier()

@pytest.fixture
def ai_system():
    return AITradingSystem()

@pytest.fixture
def sample_data():
    # Generate sample market data
    dates = pd.date_range(start='2025-01-01', end='2025-02-16', freq='D')
    data = pd.DataFrame({
        'open': np.random.uniform(100, 200, len(dates)),
        'high': np.random.uniform(150, 250, len(dates)),
        'low': np.random.uniform(90, 180, len(dates)),
        'close': np.random.uniform(100, 200, len(dates)),
        'volume': np.random.uniform(1000000, 5000000, len(dates))
    }, index=dates)
    return data

def test_lstm_model_structure(lstm_model):
    # Test model structure
    assert isinstance(lstm_model.lstm, torch.nn.LSTM)
    assert isinstance(lstm_model.fc, torch.nn.Linear)
    
    # Test model parameters
    assert lstm_model.hidden_dim == 64
    assert lstm_model.num_layers == 2

def test_lstm_forward_pass(lstm_model):
    # Create sample input
    batch_size = 32
    seq_length = 10
    input_dim = 5
    x = torch.randn(batch_size, seq_length, input_dim)
    
    # Forward pass
    output = lstm_model(x)
    
    # Check output shape
    assert output.shape == (batch_size, 1)
    assert not torch.isnan(output).any()

def test_sentiment_analyzer(sentiment_analyzer):
    texts = [
        "Company reports strong quarterly earnings",
        "Market crashes amid economic concerns",
        "Stock prices remain stable"
    ]
    
    sentiments = sentiment_analyzer.analyze_sentiment(texts)
    
    assert len(sentiments) == len(texts)
    for sentiment in sentiments:
        assert 'positive' in sentiment
        assert 'negative' in sentiment
        assert 'neutral' in sentiment
        assert abs(sum(sentiment.values()) - 1.0) < 1e-6

def test_market_regime_classifier(regime_classifier, sample_data):
    # Test regime classification
    regime = regime_classifier.identify_regime(sample_data)
    
    assert regime in [
        'Bullish Volatile',
        'Bearish Volatile',
        'Bullish Stable',
        'Bearish Stable'
    ]
    
    # Test feature extraction
    features = regime_classifier._extract_features(sample_data)
    assert isinstance(features, np.ndarray)
    assert features.shape[1] == 3  # returns, volatility, momentum

def test_ai_system_initialization(ai_system):
    # Test initialization
    ai_system.initialize_price_predictor(
        input_dim=5,
        hidden_dim=64,
        num_layers=2
    )
    
    assert ai_system.price_predictor is not None
    assert isinstance(ai_system.sentiment_analyzer, TransformerSentimentAnalyzer)
    assert isinstance(ai_system.regime_classifier, MarketRegimeClassifier)

def test_ai_system_data_preparation(ai_system, sample_data):
    sequence_length = 10
    X, y, scaler = ai_system.prepare_data(
        data=sample_data,
        sequence_length=sequence_length
    )
    
    assert isinstance(X, torch.Tensor)
    assert isinstance(y, torch.Tensor)
    assert X.shape[1] == sequence_length
    assert X.shape[2] == 5  # OHLCV
    assert y.shape[0] == X.shape[0]

def test_ai_system_price_prediction(ai_system, sample_data):
    # Initialize and prepare
    ai_system.initialize_price_predictor(input_dim=5)
    sequence_length = 10
    X, y, scaler = ai_system.prepare_data(
        data=sample_data,
        sequence_length=sequence_length
    )
    
    # Train
    ai_system.train_price_predictor(
        train_data=X,
        train_labels=y,
        epochs=2
    )
    
    # Predict
    prediction = ai_system.predict_price(X[:1], scaler)
    assert isinstance(prediction, float)
    assert prediction > 0

def test_ai_system_sentiment_analysis(ai_system):
    news = [
        "Markets rally on positive economic data",
        "Tech stocks surge to new highs",
        "Investors remain cautious amid uncertainty"
    ]
    
    sentiment = ai_system.analyze_market_sentiment(news)
    
    assert isinstance(sentiment, dict)
    assert all(k in sentiment for k in ['positive', 'negative', 'neutral'])
    assert abs(sum(sentiment.values()) - 1.0) < 1e-6

def test_ai_system_trading_signals(ai_system):
    signal = ai_system.generate_trading_signals(
        price_prediction=105,
        current_price=100,
        sentiment={'positive': 0.6, 'negative': 0.2, 'neutral': 0.2},
        market_regime='Bullish Stable'
    )
    
    assert isinstance(signal, dict)
    assert 'action' in signal
    assert signal['action'] in ['BUY', 'SELL', 'HOLD']
    assert 'confidence' in signal
    assert 0 <= signal['confidence'] <= 1

def test_model_error_handling(ai_system):
    # Test with invalid data
    with pytest.raises(Exception):
        ai_system.prepare_data(
            data=None,
            sequence_length=10
        )
    
    # Test with invalid sentiment texts
    with pytest.raises(Exception):
        ai_system.analyze_market_sentiment(None)
    
    # Test with invalid prediction input
    with pytest.raises(Exception):
        ai_system.predict_price(None, None)

def test_model_persistence(lstm_model, tmp_path):
    # Save model
    model_path = tmp_path / "model.pt"
    torch.save(lstm_model.state_dict(), model_path)
    
    # Load model
    new_model = LSTMPricePredictor(
        input_dim=5,
        hidden_dim=64,
        num_layers=2,
        output_dim=1
    )
    new_model.load_state_dict(torch.load(model_path))
    
    # Compare parameters
    for p1, p2 in zip(lstm_model.parameters(), new_model.parameters()):
        assert torch.equal(p1, p2)
