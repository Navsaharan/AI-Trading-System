from typing import Dict, List, Optional, Union, Any
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import torch
import torch.nn as nn
from torch.cuda.amp import autocast, GradScaler
import tensorflow as tf
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from sklearn.preprocessing import StandardScaler
import talib
from scipy import stats
import json
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import joblib
import os
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')

class MarketAnalysisService:
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.scaler = StandardScaler()
        self.executor = ThreadPoolExecutor(max_workers=8)
        self.initialize_components()

    def initialize_components(self):
        """Initialize analysis components"""
        try:
            # Load models and configurations
            self.load_models()
            self.load_indicators()
            print("Market analysis service initialized successfully")
        except Exception as e:
            print(f"Error initializing market analysis: {e}")

    async def analyze_market(
        self,
        market_data: pd.DataFrame,
        timeframe: str = '1d'
    ) -> Dict:
        """Comprehensive market analysis"""
        try:
            # Process in parallel
            with ThreadPoolExecutor() as executor:
                # Technical analysis
                technical = executor.submit(
                    self._technical_analysis, market_data
                )
                
                # Statistical analysis
                statistical = executor.submit(
                    self._statistical_analysis, market_data
                )
                
                # Sentiment analysis
                sentiment = executor.submit(
                    self._sentiment_analysis, market_data
                )
                
                # Volume analysis
                volume = executor.submit(
                    self._volume_analysis, market_data
                )
                
                # Wait for results
                results = {
                    "technical": technical.result(),
                    "statistical": statistical.result(),
                    "sentiment": sentiment.result(),
                    "volume": volume.result()
                }

            # Combine analyses
            analysis = self._combine_analyses(results)
            
            # Generate signals
            signals = await self._generate_signals(analysis)
            
            # Calculate market conditions
            conditions = self._calculate_market_conditions(analysis)

            return {
                "analysis": analysis,
                "signals": signals,
                "conditions": conditions,
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "timeframe": timeframe
                }
            }

        except Exception as e:
            print(f"Error in market analysis: {e}")
            return {}

    def _technical_analysis(self, data: pd.DataFrame) -> Dict:
        """Perform technical analysis"""
        try:
            results = {}
            
            # Trend indicators
            results["trend"] = {
                "sma": talib.SMA(data['close']),
                "ema": talib.EMA(data['close']),
                "macd": talib.MACD(data['close'])[0],
                "adx": talib.ADX(data['high'], data['low'], data['close'])
            }
            
            # Momentum indicators
            results["momentum"] = {
                "rsi": talib.RSI(data['close']),
                "stoch": talib.STOCH(data['high'], data['low'], data['close'])[0],
                "cci": talib.CCI(data['high'], data['low'], data['close']),
                "mfi": talib.MFI(data['high'], data['low'], data['close'], data['volume'])
            }
            
            # Volatility indicators
            results["volatility"] = {
                "atr": talib.ATR(data['high'], data['low'], data['close']),
                "bbands": talib.BBANDS(data['close']),
                "natr": talib.NATR(data['high'], data['low'], data['close'])
            }
            
            # Volume indicators
            results["volume"] = {
                "obv": talib.OBV(data['close'], data['volume']),
                "ad": talib.AD(data['high'], data['low'], data['close'], data['volume']),
                "adosc": talib.ADOSC(data['high'], data['low'], data['close'], data['volume'])
            }

            return results

        except Exception as e:
            print(f"Error in technical analysis: {e}")
            return {}

    def _statistical_analysis(self, data: pd.DataFrame) -> Dict:
        """Perform statistical analysis"""
        try:
            returns = data['close'].pct_change().dropna()
            
            results = {
                "distribution": {
                    "mean": float(returns.mean()),
                    "std": float(returns.std()),
                    "skew": float(stats.skew(returns)),
                    "kurtosis": float(stats.kurtosis(returns))
                },
                "hypothesis_tests": {
                    "normality": float(stats.normaltest(returns)[0]),
                    "stationarity": float(stats.adfuller(returns)[0])
                },
                "correlations": self._calculate_correlations(data),
                "volatility": self._calculate_volatility(returns)
            }

            return results

        except Exception as e:
            print(f"Error in statistical analysis: {e}")
            return {}

    async def _sentiment_analysis(self, data: pd.DataFrame) -> Dict:
        """Analyze market sentiment"""
        try:
            results = {
                "price_action": self._analyze_price_action(data),
                "volume_sentiment": self._analyze_volume_sentiment(data),
                "momentum_sentiment": self._analyze_momentum_sentiment(data),
                "overall_sentiment": self._calculate_overall_sentiment(data)
            }

            return results

        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            return {}

    def _volume_analysis(self, data: pd.DataFrame) -> Dict:
        """Analyze trading volume patterns"""
        try:
            volume = data['volume']
            price = data['close']
            
            results = {
                "volume_trends": {
                    "sma": float(talib.SMA(volume)[-1]),
                    "ema": float(talib.EMA(volume)[-1]),
                    "variance": float(volume.var())
                },
                "price_volume_correlation": float(
                    np.corrcoef(price, volume)[0, 1]
                ),
                "volume_breakouts": self._detect_volume_breakouts(data),
                "liquidity_analysis": self._analyze_liquidity(data)
            }

            return results

        except Exception as e:
            print(f"Error in volume analysis: {e}")
            return {}

    def _calculate_correlations(self, data: pd.DataFrame) -> Dict:
        """Calculate various market correlations"""
        try:
            # Calculate correlation matrix
            corr_matrix = data.corr()
            
            # Extract relevant correlations
            correlations = {
                "price_volume": float(corr_matrix.loc['close', 'volume']),
                "high_low": float(corr_matrix.loc['high', 'low']),
                "open_close": float(corr_matrix.loc['open', 'close'])
            }

            return correlations

        except Exception as e:
            print(f"Error calculating correlations: {e}")
            return {}

    def _calculate_volatility(self, returns: pd.Series) -> Dict:
        """Calculate various volatility metrics"""
        try:
            # Calculate different volatility measures
            daily_vol = returns.std()
            annual_vol = daily_vol * np.sqrt(252)
            
            results = {
                "daily": float(daily_vol),
                "annual": float(annual_vol),
                "parkinson": float(self._parkinson_volatility(returns)),
                "garch": float(self._garch_volatility(returns))
            }

            return results

        except Exception as e:
            print(f"Error calculating volatility: {e}")
            return {}

    @staticmethod
    def _parkinson_volatility(returns: pd.Series) -> float:
        """Calculate Parkinson volatility"""
        try:
            high_low_ratio = np.log(returns.high / returns.low)
            return np.sqrt(1 / (4 * np.log(2)) * (high_low_ratio ** 2).mean())
        except Exception:
            return 0.0

    def _garch_volatility(self, returns: pd.Series) -> float:
        """Estimate GARCH(1,1) volatility"""
        try:
            # Simple GARCH(1,1) implementation
            omega = 0.000001
            alpha = 0.1
            beta = 0.8
            
            h = np.zeros_like(returns)
            h[0] = returns.var()
            
            for t in range(1, len(returns)):
                h[t] = omega + alpha * returns[t-1]**2 + beta * h[t-1]
            
            return np.sqrt(h[-1])
        except Exception:
            return 0.0

    async def _generate_signals(self, analysis: Dict) -> List[Dict]:
        """Generate trading signals from analysis"""
        try:
            signals = []
            
            # Technical signals
            tech_signals = self._generate_technical_signals(
                analysis['technical']
            )
            
            # Statistical signals
            stat_signals = self._generate_statistical_signals(
                analysis['statistical']
            )
            
            # Sentiment signals
            sent_signals = self._generate_sentiment_signals(
                analysis['sentiment']
            )
            
            # Combine and filter signals
            all_signals = tech_signals + stat_signals + sent_signals
            filtered_signals = self._filter_signals(all_signals)
            
            return filtered_signals

        except Exception as e:
            print(f"Error generating signals: {e}")
            return []

    def _calculate_market_conditions(self, analysis: Dict) -> Dict:
        """Calculate overall market conditions"""
        try:
            conditions = {
                "trend": self._determine_trend(analysis),
                "volatility": self._determine_volatility(analysis),
                "liquidity": self._determine_liquidity(analysis),
                "sentiment": self._determine_sentiment(analysis),
                "risk_level": self._calculate_risk_level(analysis)
            }
            
            # Calculate market state
            conditions["market_state"] = self._determine_market_state(conditions)
            
            return conditions

        except Exception as e:
            print(f"Error calculating market conditions: {e}")
            return {}

    def _determine_trend(self, analysis: Dict) -> str:
        """Determine market trend"""
        try:
            # Get technical indicators
            macd = analysis['technical']['trend']['macd']
            adx = analysis['technical']['trend']['adx']
            
            # Determine trend strength
            trend_strength = 'weak'
            if adx[-1] > 25:
                trend_strength = 'strong'
            elif adx[-1] > 20:
                trend_strength = 'moderate'
            
            # Determine trend direction
            if macd[-1] > 0:
                return f"{trend_strength}_uptrend"
            elif macd[-1] < 0:
                return f"{trend_strength}_downtrend"
            return "sideways"

        except Exception as e:
            print(f"Error determining trend: {e}")
            return "unknown"

    def _determine_volatility(self, analysis: Dict) -> str:
        """Determine market volatility"""
        try:
            # Get volatility metrics
            atr = analysis['technical']['volatility']['atr'][-1]
            vol = analysis['statistical']['volatility']['daily']
            
            # Classify volatility
            if vol > 0.02 or atr > 0.02:
                return "high"
            elif vol > 0.01 or atr > 0.01:
                return "moderate"
            return "low"

        except Exception as e:
            print(f"Error determining volatility: {e}")
            return "unknown"

    def _determine_liquidity(self, analysis: Dict) -> str:
        """Determine market liquidity"""
        try:
            # Get volume metrics
            volume = analysis['volume']['volume_trends']['sma']
            variance = analysis['volume']['volume_trends']['variance']
            
            # Classify liquidity
            if volume > 1000000 and variance < 0.5:
                return "high"
            elif volume > 100000:
                return "moderate"
            return "low"

        except Exception as e:
            print(f"Error determining liquidity: {e}")
            return "unknown"

    def _determine_sentiment(self, analysis: Dict) -> str:
        """Determine market sentiment"""
        try:
            sentiment = analysis['sentiment']['overall_sentiment']
            
            if sentiment > 0.6:
                return "bullish"
            elif sentiment < 0.4:
                return "bearish"
            return "neutral"

        except Exception as e:
            print(f"Error determining sentiment: {e}")
            return "unknown"

    def _calculate_risk_level(self, analysis: Dict) -> str:
        """Calculate market risk level"""
        try:
            # Get risk metrics
            volatility = analysis['statistical']['volatility']['annual']
            sentiment = analysis['sentiment']['overall_sentiment']
            volume = analysis['volume']['volume_trends']['variance']
            
            # Calculate risk score
            risk_score = (
                0.4 * volatility +
                0.3 * (1 - sentiment) +
                0.3 * volume
            )
            
            # Classify risk
            if risk_score > 0.7:
                return "high"
            elif risk_score > 0.3:
                return "moderate"
            return "low"

        except Exception as e:
            print(f"Error calculating risk level: {e}")
            return "unknown"

    def _determine_market_state(self, conditions: Dict) -> str:
        """Determine overall market state"""
        try:
            # Define state rules
            states = {
                "strong_bull": {
                    "trend": "strong_uptrend",
                    "sentiment": "bullish",
                    "volatility": "low"
                },
                "weak_bull": {
                    "trend": "weak_uptrend",
                    "sentiment": "neutral",
                    "volatility": "moderate"
                },
                "strong_bear": {
                    "trend": "strong_downtrend",
                    "sentiment": "bearish",
                    "volatility": "high"
                },
                "weak_bear": {
                    "trend": "weak_downtrend",
                    "sentiment": "neutral",
                    "volatility": "moderate"
                },
                "consolidation": {
                    "trend": "sideways",
                    "volatility": "low"
                }
            }
            
            # Match current conditions to states
            for state, criteria in states.items():
                if all(conditions[k] == v for k, v in criteria.items()):
                    return state
            
            return "mixed"

        except Exception as e:
            print(f"Error determining market state: {e}")
            return "unknown"

# Initialize market analysis service
market_analyzer = MarketAnalysisService()
