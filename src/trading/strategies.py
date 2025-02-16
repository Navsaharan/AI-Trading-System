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
