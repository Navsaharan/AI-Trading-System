import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from dataclasses import dataclass
from scipy import stats
import talib

@dataclass
class TechnicalIndicators:
    trend_indicators: Dict
    momentum_indicators: Dict
    volatility_indicators: Dict
    volume_indicators: Dict
    pattern_recognition: Dict
    support_resistance: Dict
    fibonacci_levels: Dict
    pivot_points: Dict

class TechnicalAnalysisService:
    def __init__(self):
        self.required_periods = {
            'short': 14,
            'medium': 50,
            'long': 200
        }

    async def analyze_stock(self, historical_data: pd.DataFrame) -> TechnicalIndicators:
        """Comprehensive technical analysis of a stock"""
        try:
            # Convert data to numpy arrays for talib
            close = historical_data['Close'].values
            high = historical_data['High'].values
            low = historical_data['Low'].values
            volume = historical_data['Volume'].values
            open_price = historical_data['Open'].values

            return TechnicalIndicators(
                trend_indicators=self._calculate_trend_indicators(open_price, high, low, close, volume),
                momentum_indicators=self._calculate_momentum_indicators(close),
                volatility_indicators=self._calculate_volatility_indicators(high, low, close),
                volume_indicators=self._calculate_volume_indicators(close, volume),
                pattern_recognition=self._identify_patterns(open_price, high, low, close),
                support_resistance=self._calculate_support_resistance(close),
                fibonacci_levels=self._calculate_fibonacci_levels(high, low),
                pivot_points=self._calculate_pivot_points(high, low, close)
            )
        except Exception as e:
            print(f"Error in technical analysis: {e}")
            return None

    def _calculate_trend_indicators(self, open_price, high, low, close, volume) -> Dict:
        """Calculate trend indicators"""
        # Moving Averages
        sma_20 = talib.SMA(close, timeperiod=20)
        sma_50 = talib.SMA(close, timeperiod=50)
        sma_200 = talib.SMA(close, timeperiod=200)
        
        # Exponential Moving Averages
        ema_12 = talib.EMA(close, timeperiod=12)
        ema_26 = talib.EMA(close, timeperiod=26)
        
        # MACD
        macd, macd_signal, macd_hist = talib.MACD(close)
        
        # Average Directional Index (ADX)
        adx = talib.ADX(high, low, close, timeperiod=14)
        
        # Parabolic SAR
        sar = talib.SAR(high, low)
        
        # Ichimoku Cloud
        tenkan_sen = self._calculate_ichimoku(high, low, 9)
        kijun_sen = self._calculate_ichimoku(high, low, 26)
        senkou_span_a = (tenkan_sen + kijun_sen) / 2
        senkou_span_b = self._calculate_ichimoku(high, low, 52)
        
        # On-Balance Volume (OBV)
        obv = talib.OBV(close, volume)
        
        return {
            'sma': {
                '20': sma_20[-1],
                '50': sma_50[-1],
                '200': sma_200[-1]
            },
            'ema': {
                '12': ema_12[-1],
                '26': ema_26[-1]
            },
            'macd': {
                'macd': macd[-1],
                'signal': macd_signal[-1],
                'histogram': macd_hist[-1]
            },
            'adx': adx[-1],
            'parabolic_sar': sar[-1],
            'ichimoku': {
                'tenkan_sen': tenkan_sen[-1],
                'kijun_sen': kijun_sen[-1],
                'senkou_span_a': senkou_span_a[-1],
                'senkou_span_b': senkou_span_b[-1]
            },
            'obv': obv[-1]
        }

    def _calculate_momentum_indicators(self, close) -> Dict:
        """Calculate momentum indicators"""
        # Relative Strength Index (RSI)
        rsi = talib.RSI(close, timeperiod=14)
        
        # Stochastic Oscillator
        slowk, slowd = talib.STOCH(high, low, close)
        
        # Commodity Channel Index (CCI)
        cci = talib.CCI(high, low, close)
        
        # Williams %R
        willr = talib.WILLR(high, low, close)
        
        # Money Flow Index (MFI)
        mfi = talib.MFI(high, low, close, volume, timeperiod=14)
        
        # Rate of Change (ROC)
        roc = talib.ROC(close, timeperiod=10)
        
        return {
            'rsi': rsi[-1],
            'stochastic': {
                'k': slowk[-1],
                'd': slowd[-1]
            },
            'cci': cci[-1],
            'williams_r': willr[-1],
            'mfi': mfi[-1],
            'roc': roc[-1]
        }

    def _calculate_volatility_indicators(self, high, low, close) -> Dict:
        """Calculate volatility indicators"""
        # Bollinger Bands
        upper, middle, lower = talib.BBANDS(close)
        
        # Average True Range (ATR)
        atr = talib.ATR(high, low, close)
        
        # Keltner Channel
        keltner_middle = talib.EMA(close, timeperiod=20)
        atr_multiplier = 2
        keltner_upper = keltner_middle + (atr * atr_multiplier)
        keltner_lower = keltner_middle - (atr * atr_multiplier)
        
        # Standard Deviation
        std = talib.STDDEV(close, timeperiod=20)
        
        # Chaikin Volatility
        chaikin = self._calculate_chaikin_volatility(high, low)
        
        return {
            'bollinger_bands': {
                'upper': upper[-1],
                'middle': middle[-1],
                'lower': lower[-1]
            },
            'atr': atr[-1],
            'keltner_channel': {
                'upper': keltner_upper[-1],
                'middle': keltner_middle[-1],
                'lower': keltner_lower[-1]
            },
            'standard_deviation': std[-1],
            'chaikin_volatility': chaikin[-1]
        }

    def _calculate_volume_indicators(self, close, volume) -> Dict:
        """Calculate volume indicators"""
        # Chaikin A/D Line
        chaikin_ad = talib.AD(high, low, close, volume)
        
        # Chaikin Money Flow
        cmf = talib.ADOSC(high, low, close, volume)
        
        # Ease of Movement
        emv = self._calculate_emv(high, low, volume)
        
        # Force Index
        fi = self._calculate_force_index(close, volume)
        
        # Volume Price Trend
        vpt = self._calculate_vpt(close, volume)
        
        # Negative Volume Index
        nvi = self._calculate_nvi(close, volume)
        
        return {
            'chaikin_ad': chaikin_ad[-1],
            'cmf': cmf[-1],
            'emv': emv[-1],
            'force_index': fi[-1],
            'vpt': vpt[-1],
            'nvi': nvi[-1]
        }

    def _identify_patterns(self, open_price, high, low, close) -> Dict:
        """Identify candlestick patterns"""
        patterns = {}
        
        # Single Candlestick Patterns
        patterns['doji'] = talib.CDLDOJI(open_price, high, low, close)[-1]
        patterns['hammer'] = talib.CDLHAMMER(open_price, high, low, close)[-1]
        patterns['shooting_star'] = talib.CDLSHOOTINGSTAR(open_price, high, low, close)[-1]
        
        # Double Candlestick Patterns
        patterns['engulfing'] = talib.CDLENGULFING(open_price, high, low, close)[-1]
        patterns['harami'] = talib.CDLHARAMI(open_price, high, low, close)[-1]
        
        # Triple Candlestick Patterns
        patterns['morning_star'] = talib.CDLMORNINGSTAR(open_price, high, low, close)[-1]
        patterns['evening_star'] = talib.CDLEVENINGSTAR(open_price, high, low, close)[-1]
        
        return {k: bool(v) for k, v in patterns.items()}

    def _calculate_support_resistance(self, close) -> Dict:
        """Calculate support and resistance levels"""
        # Use local minima and maxima
        prices = pd.Series(close)
        resistance_levels = self._find_peaks(prices)
        support_levels = self._find_peaks(-prices)
        
        return {
            'support_levels': sorted(support_levels)[-3:],  # Top 3 support levels
            'resistance_levels': sorted(resistance_levels)[-3:]  # Top 3 resistance levels
        }

    def _calculate_fibonacci_levels(self, high, low) -> Dict:
        """Calculate Fibonacci retracement levels"""
        max_price = np.max(high)
        min_price = np.min(low)
        diff = max_price - min_price
        
        return {
            '0.236': max_price - 0.236 * diff,
            '0.382': max_price - 0.382 * diff,
            '0.500': max_price - 0.500 * diff,
            '0.618': max_price - 0.618 * diff,
            '0.786': max_price - 0.786 * diff
        }

    def _calculate_pivot_points(self, high, low, close) -> Dict:
        """Calculate pivot points"""
        pp = (high[-1] + low[-1] + close[-1]) / 3
        r1 = 2 * pp - low[-1]
        r2 = pp + (high[-1] - low[-1])
        s1 = 2 * pp - high[-1]
        s2 = pp - (high[-1] - low[-1])
        
        return {
            'pivot_point': pp,
            'resistance': {'r1': r1, 'r2': r2},
            'support': {'s1': s1, 's2': s2}
        }

    def _calculate_ichimoku(self, high, low, period):
        """Calculate Ichimoku cloud components"""
        highs = pd.Series(high)
        lows = pd.Series(low)
        return (highs.rolling(window=period).max() + lows.rolling(window=period).min()) / 2

    def _calculate_chaikin_volatility(self, high, low, period=10):
        """Calculate Chaikin Volatility"""
        hl_range = pd.Series(high) - pd.Series(low)
        return hl_range.rolling(window=period).std()

    def _calculate_emv(self, high, low, volume):
        """Calculate Ease of Movement"""
        high = pd.Series(high)
        low = pd.Series(low)
        volume = pd.Series(volume)
        
        distance = ((high + low) / 2) - ((high.shift(1) + low.shift(1)) / 2)
        box_ratio = volume / (high - low)
        return distance / box_ratio

    def _calculate_force_index(self, close, volume, period=13):
        """Calculate Force Index"""
        close = pd.Series(close)
        return close.diff() * pd.Series(volume)

    def _calculate_vpt(self, close, volume):
        """Calculate Volume Price Trend"""
        close = pd.Series(close)
        volume = pd.Series(volume)
        return volume * ((close - close.shift(1)) / close.shift(1)).cumsum()

    def _calculate_nvi(self, close, volume):
        """Calculate Negative Volume Index"""
        close = pd.Series(close)
        volume = pd.Series(volume)
        ret = close.pct_change()
        vol_decrease = volume < volume.shift(1)
        nvi = pd.Series(index=close.index, data=100.0)
        
        for i in range(1, len(close)):
            if vol_decrease.iloc[i]:
                nvi.iloc[i] = nvi.iloc[i-1] * (1.0 + ret.iloc[i])
            else:
                nvi.iloc[i] = nvi.iloc[i-1]
        
        return nvi

    def _find_peaks(self, prices, window=20):
        """Find peaks in price series for support/resistance"""
        peaks = []
        for i in range(window, len(prices)-window):
            if all(prices[i] > prices[i-window:i]) and all(prices[i] > prices[i+1:i+window+1]):
                peaks.append(prices[i])
        return peaks
