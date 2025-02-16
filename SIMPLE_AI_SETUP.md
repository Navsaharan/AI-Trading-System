# Simple AI Setup Guide for FamilyHVSDN

## Step 1: Initial Setup

1. First, create these folders in your project:
```
familyhvsdn/
├── training_data/          # Automatically managed by data collector
│   ├── stocks/            # Stock-wise data
│   ├── indices/           # Index data
│   ├── processed/         # Processed data for AI
│   └── news/             # News data
├── ai_models/             # Trained models are saved here
└── src/
    └── ai/
        ├── models/        # AI model code
        ├── training/      # Training scripts
        ├── data_collection/ # Data collection scripts
        └── utils/         # Helper functions
```

2. Install required Python packages:
```bash
pip install torch pandas numpy scikit-learn transformers yfinance ta-lib schedule requests
```

## Step 2: Setup Automatic Data Collection

1. **Start the Data Collector:**
```bash
# This will automatically:
# - Download historical data (2010-present) for all Nifty 500 stocks
# - Update data daily after market close
# - Calculate technical indicators
python src/ai/data_collection/auto_data_collector.py
```

2. **Verify Data Collection:**
- Check `training_data/stocks/` for individual stock data
- Each stock will have a CSV file with:
  - OHLCV data
  - Technical indicators (SMA, RSI, MACD)
  - 13+ years of historical data

## Step 3: Train Price Prediction Model

1. Create price prediction model at `src/ai/models/price_model.py`:
```python
import torch
import torch.nn as nn

class PricePredictor(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=7,  # OHLCV + SMA20 + RSI
            hidden_size=128,
            num_layers=2,
            dropout=0.2
        )
        self.linear = nn.Linear(128, 1)
    
    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        return self.linear(lstm_out[:, -1, :])
```

2. Create training script at `src/ai/training/train_price.py`:
```python
import torch
from models.price_model import PricePredictor
import pandas as pd
import glob
import numpy as np

def prepare_data(file_path, sequence_length=30):
    # Load data
    df = pd.read_csv(file_path)
    
    # Use all features
    features = ['Open', 'High', 'Low', 'Close', 'Volume', 'SMA_20', 'RSI']
    data = df[features].values
    
    # Create sequences
    X, y = [], []
    for i in range(len(data) - sequence_length):
        X.append(data[i:i+sequence_length])
        y.append(data[i+sequence_length, 3])  # Next day's close price
    
    return torch.FloatTensor(X), torch.FloatTensor(y)

def train_model():
    model = PricePredictor()
    optimizer = torch.optim.Adam(model.parameters())
    criterion = nn.MSELoss()
    
    # Train on all stocks
    stock_files = glob.glob('training_data/stocks/*_historical.csv')
    
    for epoch in range(50):
        total_loss = 0
        for file in stock_files:
            X, y = prepare_data(file)
            
            # Train
            optimizer.zero_grad()
            output = model(X)
            loss = criterion(output.squeeze(), y)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
        
        print(f'Epoch {epoch}, Loss: {total_loss/len(stock_files)}')
    
    # Save model
    torch.save(model.state_dict(), 'ai_models/price_model.pth')

if __name__ == '__main__':
    train_model()
```

## Step 4: Train Sentiment Model

1. Create sentiment model at `src/ai/models/sentiment_model.py`:
```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

class MarketSentimentAnalyzer:
    def __init__(self):
        self.model = AutoModelForSequenceClassification.from_pretrained(
            'finiteautomata/bertweet-base-sentiment-analysis'
        )
        self.tokenizer = AutoTokenizer.from_pretrained(
            'finiteautomata/bertweet-base-sentiment-analysis'
        )
    
    def analyze(self, texts):
        inputs = self.tokenizer(texts, return_tensors='pt', padding=True, truncation=True)
        outputs = self.model(**inputs)
        return torch.softmax(outputs.logits, dim=1)
    
    def save(self, path):
        self.model.save_pretrained(f'{path}/model')
        self.tokenizer.save_pretrained(f'{path}/tokenizer')
```

## Step 5: Create Trading System

1. Create prediction system at `src/ai/trading_system.py`:
```python
import torch
from models.price_model import PricePredictor
from models.sentiment_model import MarketSentimentAnalyzer
import pandas as pd
import glob
import os

class TradingSystem:
    def __init__(self):
        self.price_model = PricePredictor()
        self.price_model.load_state_dict(torch.load('ai_models/price_model.pth'))
        self.sentiment_analyzer = MarketSentimentAnalyzer()
        
        # Load latest data
        self.load_latest_data()
    
    def load_latest_data(self):
        """Load and prepare latest market data"""
        self.market_data = {}
        for file in glob.glob('training_data/stocks/*_historical.csv'):
            symbol = os.path.basename(file).replace('_historical.csv', '')
            df = pd.read_csv(file).tail(30)  # Last 30 days
            self.market_data[symbol] = df
    
    def predict(self, symbol):
        """Make prediction for a symbol"""
        if symbol not in self.market_data:
            return None
            
        # Prepare data
        df = self.market_data[symbol]
        features = ['Open', 'High', 'Low', 'Close', 'Volume', 'SMA_20', 'RSI']
        data = torch.FloatTensor(df[features].values).unsqueeze(0)
        
        # Get price prediction
        with torch.no_grad():
            price_pred = self.price_model(data)
        
        return {
            'predicted_price': price_pred.item(),
            'current_price': df['Close'].iloc[-1],
            'change_percent': ((price_pred.item() - df['Close'].iloc[-1]) / df['Close'].iloc[-1]) * 100
        }
```

## Step 6: Running Everything

1. **Start Data Collection:**
```bash
# Start automatic data collection
python src/ai/data_collection/auto_data_collector.py
```

2. **Train Models:**
```bash
# Train price prediction model
python src/ai/training/train_price.py

# Train sentiment model
python src/ai/training/train_sentiment.py
```

3. **Make Predictions:**
```python
from trading_system import TradingSystem

# Initialize system
system = TradingSystem()

# Get prediction for a stock
prediction = system.predict('RELIANCE')
print(prediction)
```

## Automatic Updates

The system will:
1. Collect new data daily at market close (3:30 PM IST)
2. Update technical indicators
3. Keep historical data up to date
4. Handle all error cases automatically

## Common Issues and Solutions

1. **No Data Available:**
   - Check if data collector is running
   - Verify internet connection
   - Check `training_data/logs/collector.log`

2. **Poor Predictions:**
   - Ensure at least 2 years of training data
   - Increase training epochs
   - Add more technical indicators

3. **Memory Issues:**
   - Reduce batch size in training
   - Process stocks one by one
   - Use data loader for large datasets

## Need Help?

1. Check data collector logs: `training_data/logs/collector.log`
2. Verify model files in `ai_models/`
3. Check if all dependencies are installed

For more details on data collection, see `src/ai/data_collection/DATA_COLLECTION_GUIDE.md`
