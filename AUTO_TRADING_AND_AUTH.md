# Auto Trading Setup and Authentication Guide

## 1. Firebase Authentication Setup

### Initial Setup
```bash
# Install Firebase Admin SDK
pip install firebase-admin

# Install Firebase client SDK for frontend
npm install firebase
```

### Backend Configuration
1. Create `src/auth/firebase_config.py`:
```python
import firebase_admin
from firebase_admin import credentials, auth

def init_firebase():
    cred = credentials.Certificate('path/to/serviceAccountKey.json')
    firebase_admin.initialize_app(cred)

def verify_token(token):
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token['uid']
    except:
        return None
```

2. Create authentication middleware `src/auth/auth_middleware.py`:
```python
from functools import wraps
from flask import request, jsonify
from .firebase_config import verify_token

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'No token provided'}), 401
            
        user_id = verify_token(token.split('Bearer ')[1])
        if not user_id:
            return jsonify({'error': 'Invalid token'}), 401
            
        return f(user_id, *args, **kwargs)
    return decorated
```

### Frontend Configuration
```javascript
// src/frontend/src/config/firebase.js
import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';

const firebaseConfig = {
    apiKey: "your-api-key",
    authDomain: "your-domain.firebaseapp.com",
    projectId: "your-project-id",
    // ... other config
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
```

## 2. Broker Integration

### Angel One Setup

1. Create `src/brokers/angelone.py`:
```python
from smartapi import SmartConnect
import os
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AngelOne:
    def __init__(self):
        self.api_key = os.getenv('ANGEL_API_KEY')
        self.client_id = os.getenv('ANGEL_CLIENT_ID')
        self.password = os.getenv('ANGEL_PASSWORD')
        self.token = os.getenv('ANGEL_TOKEN')
        self.obj = SmartConnect(api_key=self.api_key)
        
    def login(self):
        try:
            data = self.obj.generateSession(self.client_id, self.password, self.token)
            refreshToken = data['data']['refreshToken']
            self.obj.getProfile(refreshToken)
            return True
        except Exception as e:
            logger.error(f"Angel One Login Error: {str(e)}")
            return False
            
    def place_order(self, symbol, qty, side, order_type='MARKET'):
        try:
            orderparams = {
                "variety": "NORMAL",
                "tradingsymbol": symbol,
                "symboltoken": self.get_token(symbol),
                "transactiontype": side,
                "exchange": "NSE",
                "ordertype": order_type,
                "producttype": "INTRADAY",
                "duration": "DAY",
                "quantity": qty
            }
            order_id = self.obj.placeOrder(orderparams)
            return order_id
        except Exception as e:
            logger.error(f"Order Placement Error: {str(e)}")
            return None
            
    def get_token(self, symbol):
        try:
            data = self.obj.searchScrip(symbol)
            return data['data'][0]['token']
        except:
            return None
```

## 3. Auto Trading System

### 1. Strategy Definition
Create `src/trading/strategies.py`:
```python
from dataclasses import dataclass
from typing import List, Dict
import numpy as np
import pandas as pd

@dataclass
class TradingStrategy:
    name: str
    timeframe: str
    risk_per_trade: float
    max_positions: int
    
class MomentumStrategy(TradingStrategy):
    def __init__(self):
        super().__init__(
            name="Momentum",
            timeframe="5min",
            risk_per_trade=0.01,  # 1% risk per trade
            max_positions=5
        )
    
    def analyze(self, data: pd.DataFrame) -> Dict:
        # Calculate indicators
        data['SMA20'] = data['close'].rolling(20).mean()
        data['RSI'] = self.calculate_rsi(data['close'])
        
        # Generate signals
        signal = 'BUY' if (
            data['close'].iloc[-1] > data['SMA20'].iloc[-1] and
            data['RSI'].iloc[-1] > 30 and
            data['RSI'].iloc[-1] < 70
        ) else 'SELL' if (
            data['close'].iloc[-1] < data['SMA20'].iloc[-1] and
            data['RSI'].iloc[-1] > 70
        ) else 'NEUTRAL'
        
        return {
            'signal': signal,
            'confidence': self.calculate_confidence(data),
            'stop_loss': self.calculate_stop_loss(data, signal),
            'target': self.calculate_target(data, signal)
        }
    
    def calculate_confidence(self, data):
        # Simple confidence based on RSI and trend
        rsi = data['RSI'].iloc[-1]
        trend_strength = abs(data['close'].iloc[-1] - data['SMA20'].iloc[-1]) / data['SMA20'].iloc[-1]
        return min(0.9, (trend_strength * 100 + (abs(rsi - 50) / 50)) / 2)
```

### 2. Auto Trading Engine
Create `src/trading/auto_trader.py`:
```python
import threading
import time
from typing import Dict, List
from datetime import datetime
import logging
from .strategies import TradingStrategy
from ..brokers.angelone import AngelOne
from ..brokers.zerodha import Zerodha

logger = logging.getLogger(__name__)

class AutoTrader:
    def __init__(self):
        self.brokers: Dict[str, Any] = {
            'angel': AngelOne(),
            'zerodha': Zerodha()
        }
        self.strategies: List[TradingStrategy] = []
        self.active_trades: Dict = {}
        self.is_running = False
        
    def add_strategy(self, strategy: TradingStrategy):
        self.strategies.append(strategy)
        
    def start(self):
        self.is_running = True
        self.trading_thread = threading.Thread(target=self._trading_loop)
        self.trading_thread.start()
        
    def stop(self):
        self.is_running = False
        
    def _trading_loop(self):
        while self.is_running:
            try:
                self._check_market_hours()
                self._process_strategies()
                self._manage_positions()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Trading Loop Error: {str(e)}")
                
    def _check_market_hours(self):
        now = datetime.now()
        if now.hour < 9 or now.hour >= 15:
            return False
        return True
        
    def _process_strategies(self):
        for strategy in self.strategies:
            signals = strategy.analyze(self._get_market_data())
            if signals['confidence'] > 0.7:  # High confidence trades only
                self._execute_trade(strategy, signals)
                
    def _execute_trade(self, strategy, signals):
        # Calculate position size based on risk
        account_value = self._get_account_value()
        risk_amount = account_value * strategy.risk_per_trade
        position_size = self._calculate_position_size(
            risk_amount,
            signals['stop_loss']
        )
        
        # Place orders
        if signals['signal'] == 'BUY':
            order_id = self.brokers['angel'].place_order(
                symbol=signals['symbol'],
                qty=position_size,
                side='BUY'
            )
            if order_id:
                self._place_stop_loss(order_id, signals['stop_loss'])
                self._place_target(order_id, signals['target'])
                
    def _manage_positions(self):
        # Trail stops, manage targets, handle exits
        for trade_id, trade in self.active_trades.items():
            current_price = self._get_current_price(trade['symbol'])
            if self._should_exit(trade, current_price):
                self._exit_trade(trade_id)
```

### 3. Risk Management
Create `src/trading/risk_manager.py`:
```python
class RiskManager:
    def __init__(self):
        self.max_daily_loss = 0.02  # 2% max daily loss
        self.max_position_size = 0.05  # 5% max position size
        self.max_correlated_positions = 3
        
    def check_trade(self, trade_params):
        # Check various risk parameters
        if not self._check_daily_loss():
            return False, "Daily loss limit reached"
            
        if not self._check_position_size(trade_params['size']):
            return False, "Position size too large"
            
        if not self._check_correlation(trade_params['symbol']):
            return False, "Too many correlated positions"
            
        return True, "Trade approved"
        
    def _check_daily_loss(self):
        # Implement daily loss checking logic
        pass
        
    def _check_position_size(self, size):
        # Implement position size checking
        pass
        
    def _check_correlation(self, symbol):
        # Implement correlation checking
        pass
```

## 4. Environment Variables

Add these to your `.env` file:
```bash
# Firebase
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY=your-private-key
FIREBASE_CLIENT_EMAIL=your-client-email

# Angel One
ANGEL_API_KEY=your-angel-api-key
ANGEL_CLIENT_ID=your-client-id
ANGEL_PASSWORD=your-password
ANGEL_TOKEN=your-token

# Risk Management
MAX_DAILY_LOSS=0.02
MAX_POSITION_SIZE=0.05
MAX_CORRELATED_POSITIONS=3
```

## 5. Auto Trading Configuration

1. **Strategy Parameters:**
   - Time frames: 1min, 5min, 15min, 1hour
   - Risk per trade: 0.5% to 2%
   - Maximum positions: 3 to 10
   - Stop loss: ATR-based or Support/Resistance
   - Take profit: Risk:Reward 1:2 to 1:4

2. **Risk Management:**
   - Maximum daily loss: 2%
   - Maximum position size: 5%
   - Maximum correlated positions: 3
   - Minimum profit factor: 1.5

3. **Execution Settings:**
   - Order types: MARKET, LIMIT
   - Slippage tolerance: 0.1%
   - Position sizing: Risk-based
   - Entry conditions: Price action + indicators

## 6. Starting Auto Trading

```bash
# 1. Start the system
python start.py

# 2. Enable auto trading
python src/trading/enable_auto_trading.py

# 3. Monitor trades
python src/trading/monitor_trades.py
```

## 7. Monitoring Auto Trading

1. **Real-time Monitoring:**
   - Active positions
   - P&L tracking
   - Risk metrics
   - Strategy performance

2. **Alerts:**
   - Trade execution
   - Stop loss hits
   - Target achieved
   - Risk limits reached

3. **Reports:**
   - Daily performance
   - Strategy metrics
   - Risk analysis
   - Trade journal

## 8. Emergency Procedures

1. **Stop All Trading:**
```bash
python src/trading/emergency_stop.py
```

2. **Close All Positions:**
```bash
python src/trading/close_all_positions.py
```

3. **Reset Risk Limits:**
```bash
python src/trading/reset_risk_limits.py
```
