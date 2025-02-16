from typing import Dict, List, Optional, Union
import asyncio
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from ..utils.market_data import MarketData
from ..models.model_manager import ModelManager

class VolatilityTracker:
    """Track and analyze high volatility in stocks and crypto."""
    
    def __init__(self):
        self.market_data = MarketData()
        self.model_manager = ModelManager()
        
        # Initialize trackers
        self.volatility_metrics = {}
        self.breakout_signals = {}
        self.market_volatility = {}
        
        # Analysis metrics
        self.analysis_metrics = {
            "high_volatility_assets": [],
            "potential_breakouts": [],
            "risk_levels": {}
        }
    
    async def track_volatility(self, symbols: List[str]) -> Dict:
        """Track volatility for given symbols."""
        try:
            volatility_data = {}
            
            for symbol in symbols:
                # Get market data
                market_data = await self.market_data.get_real_time_data(symbol)
                
                # Calculate volatility metrics
                volatility = self._calculate_volatility_metrics(
                    symbol,
                    market_data
                )
                
                # Detect breakout signals
                breakouts = self._detect_breakout_signals(
                    symbol,
                    market_data,
                    volatility
                )
                
                volatility_data[symbol] = {
                    "volatility": volatility,
                    "breakouts": breakouts,
                    "risk_level": self._calculate_risk_level(volatility),
                    "timestamp": datetime.now()
                }
            
            return volatility_data
        except Exception as e:
            print(f"Error tracking volatility: {str(e)}")
            return {}
    
    async def get_volatility_alerts(self) -> Dict:
        """Get high volatility alerts and signals."""
        try:
            return {
                "volatility_metrics": self.volatility_metrics,
                "breakout_signals": self.breakout_signals,
                "market_volatility": self.market_volatility,
                "analysis_metrics": self.analysis_metrics,
                "last_update": datetime.now()
            }
        except Exception as e:
            print(f"Error getting volatility alerts: {str(e)}")
            return {}
    
    async def detect_volatility_patterns(self, symbol: str) -> Dict:
        """Detect volatility patterns for trading signals."""
        try:
            # Get latest volatility data
            volatility_data = await self._get_latest_volatility_data(symbol)
            
            # Analyze volatility patterns
            pattern_analysis = self._analyze_volatility_patterns(
                symbol,
                volatility_data
            )
            
            # Generate trading signals
            signals = self._generate_volatility_signals(
                symbol,
                pattern_analysis
            )
            
            return {
                "symbol": symbol,
                "signals": signals,
                "pattern_analysis": pattern_analysis,
                "confidence_score": self._calculate_signal_confidence(signals),
                "timestamp": datetime.now()
            }
        except Exception as e:
            print(f"Error detecting volatility patterns: {str(e)}")
            return {}
    
    def _calculate_volatility_metrics(self, symbol: str,
                                    market_data: pd.DataFrame) -> Dict:
        """Calculate various volatility metrics."""
        try:
            metrics = {
                "historical_volatility": self._calculate_historical_volatility(
                    market_data
                ),
                "implied_volatility": self._calculate_implied_volatility(
                    symbol,
                    market_data
                ),
                "relative_volatility": self._calculate_relative_volatility(
                    symbol,
                    market_data
                ),
                "volatility_breakout": self._check_volatility_breakout(
                    market_data
                )
            }
            
            return metrics
        except Exception:
            return {}
    
    def _detect_breakout_signals(self, symbol: str, market_data: pd.DataFrame,
                               volatility: Dict) -> List[Dict]:
        """Detect potential breakout signals."""
        try:
            signals = []
            
            # Check price breakouts
            price_breakouts = self._detect_price_breakouts(market_data)
            signals.extend(price_breakouts)
            
            # Check volume breakouts
            volume_breakouts = self._detect_volume_breakouts(market_data)
            signals.extend(volume_breakouts)
            
            # Check volatility breakouts
            vol_breakouts = self._detect_volatility_breakouts(
                volatility,
                market_data
            )
            signals.extend(vol_breakouts)
            
            return signals
        except Exception:
            return []
    
    def _calculate_risk_level(self, volatility: Dict) -> str:
        """Calculate risk level based on volatility metrics."""
        try:
            # Get volatility scores
            hist_vol = volatility.get("historical_volatility", 0)
            impl_vol = volatility.get("implied_volatility", 0)
            rel_vol = volatility.get("relative_volatility", 0)
            
            # Calculate composite score
            score = (hist_vol + impl_vol + rel_vol) / 3
            
            # Determine risk level
            if score >= 0.8:
                return "very_high"
            elif score >= 0.6:
                return "high"
            elif score >= 0.4:
                return "medium"
            elif score >= 0.2:
                return "low"
            else:
                return "very_low"
        except Exception:
            return "unknown"
    
    def _calculate_historical_volatility(self,
                                       market_data: pd.DataFrame) -> float:
        """Calculate historical volatility."""
        try:
            # Calculate daily returns
            returns = market_data["close"].pct_change().dropna()
            
            # Calculate annualized volatility
            daily_vol = returns.std()
            annual_vol = daily_vol * np.sqrt(252)
            
            return annual_vol
        except Exception:
            return 0.0
    
    def _calculate_implied_volatility(self, symbol: str,
                                    market_data: pd.DataFrame) -> float:
        """Calculate implied volatility from options data."""
        try:
            # Get options data
            options_data = self.market_data.get_options_data(symbol)
            
            if not options_data:
                return 0.0
            
            # Calculate weighted average IV
            total_weight = 0
            weighted_iv = 0
            
            for option in options_data:
                volume = option.get("volume", 0)
                iv = option.get("implied_volatility", 0)
                
                weighted_iv += volume * iv
                total_weight += volume
            
            return weighted_iv / total_weight if total_weight > 0 else 0.0
        except Exception:
            return 0.0
    
    def _calculate_relative_volatility(self, symbol: str,
                                     market_data: pd.DataFrame) -> float:
        """Calculate volatility relative to market."""
        try:
            # Get market volatility
            market_vol = self._get_market_volatility()
            
            # Get symbol volatility
            symbol_vol = self._calculate_historical_volatility(market_data)
            
            return symbol_vol / market_vol if market_vol > 0 else 1.0
        except Exception:
            return 1.0
    
    def _check_volatility_breakout(self,
                                  market_data: pd.DataFrame) -> bool:
        """Check if volatility is breaking out."""
        try:
            # Calculate current volatility
            current_vol = self._calculate_historical_volatility(
                market_data.tail(5)
            )
            
            # Calculate average volatility
            avg_vol = self._calculate_historical_volatility(
                market_data.tail(20)
            )
            
            # Check for breakout
            return current_vol > (avg_vol * 1.5)  # 50% above average
        except Exception:
            return False
    
    def _detect_price_breakouts(self,
                              market_data: pd.DataFrame) -> List[Dict]:
        """Detect price breakout patterns."""
        try:
            breakouts = []
            
            # Calculate technical indicators
            sma_20 = market_data["close"].rolling(window=20).mean()
            sma_50 = market_data["close"].rolling(window=50).mean()
            upper_bb = sma_20 + (
                market_data["close"].rolling(window=20).std() * 2
            )
            lower_bb = sma_20 - (
                market_data["close"].rolling(window=20).std() * 2
            )
            
            # Check for breakouts
            current_price = market_data["close"].iloc[-1]
            
            if current_price > upper_bb.iloc[-1]:
                breakouts.append({
                    "type": "price_breakout",
                    "direction": "up",
                    "strength": (current_price - upper_bb.iloc[-1]) / current_price,
                    "confidence": self._calculate_breakout_confidence("up")
                })
            
            if current_price < lower_bb.iloc[-1]:
                breakouts.append({
                    "type": "price_breakout",
                    "direction": "down",
                    "strength": (lower_bb.iloc[-1] - current_price) / current_price,
                    "confidence": self._calculate_breakout_confidence("down")
                })
            
            return breakouts
        except Exception:
            return []
    
    def _detect_volume_breakouts(self,
                               market_data: pd.DataFrame) -> List[Dict]:
        """Detect volume breakout patterns."""
        try:
            breakouts = []
            
            # Calculate volume metrics
            avg_volume = market_data["volume"].rolling(window=20).mean()
            vol_std = market_data["volume"].rolling(window=20).std()
            
            current_volume = market_data["volume"].iloc[-1]
            
            # Check for volume breakouts
            if current_volume > (avg_volume.iloc[-1] + (2 * vol_std.iloc[-1])):
                breakouts.append({
                    "type": "volume_breakout",
                    "magnitude": current_volume / avg_volume.iloc[-1],
                    "confidence": self._calculate_volume_breakout_confidence(
                        current_volume,
                        avg_volume.iloc[-1],
                        vol_std.iloc[-1]
                    )
                })
            
            return breakouts
        except Exception:
            return []
    
    def _detect_volatility_breakouts(self, volatility: Dict,
                                   market_data: pd.DataFrame) -> List[Dict]:
        """Detect volatility breakout patterns."""
        try:
            breakouts = []
            
            # Get volatility metrics
            hist_vol = volatility.get("historical_volatility", 0)
            impl_vol = volatility.get("implied_volatility", 0)
            rel_vol = volatility.get("relative_volatility", 0)
            
            # Check for volatility breakouts
            if hist_vol > 0.5:  # High historical volatility
                breakouts.append({
                    "type": "volatility_breakout",
                    "source": "historical",
                    "magnitude": hist_vol,
                    "confidence": self._calculate_volatility_confidence(hist_vol)
                })
            
            if impl_vol > 0.6:  # High implied volatility
                breakouts.append({
                    "type": "volatility_breakout",
                    "source": "implied",
                    "magnitude": impl_vol,
                    "confidence": self._calculate_volatility_confidence(impl_vol)
                })
            
            if rel_vol > 1.5:  # High relative volatility
                breakouts.append({
                    "type": "volatility_breakout",
                    "source": "relative",
                    "magnitude": rel_vol,
                    "confidence": self._calculate_volatility_confidence(rel_vol)
                })
            
            return breakouts
        except Exception:
            return []
    
    def _calculate_breakout_confidence(self, direction: str) -> float:
        """Calculate confidence score for price breakouts."""
        try:
            # Base confidence
            confidence = 0.5
            
            # Adjust based on market conditions
            if self._is_trending_market():
                confidence += 0.2
            
            # Adjust based on volume
            if self._is_high_volume():
                confidence += 0.2
            
            # Adjust based on direction
            if direction == "up" and self._is_bullish_market():
                confidence += 0.1
            elif direction == "down" and not self._is_bullish_market():
                confidence += 0.1
            
            return min(1.0, confidence)
        except Exception:
            return 0.5
    
    def _calculate_volume_breakout_confidence(self, current_volume: float,
                                            avg_volume: float,
                                            vol_std: float) -> float:
        """Calculate confidence score for volume breakouts."""
        try:
            # Calculate z-score
            z_score = (current_volume - avg_volume) / vol_std if vol_std > 0 else 0
            
            # Convert to confidence score
            confidence = min(1.0, z_score / 4)  # Cap at 4 standard deviations
            
            return max(0.0, confidence)
        except Exception:
            return 0.0
    
    def _calculate_volatility_confidence(self, volatility: float) -> float:
        """Calculate confidence score for volatility breakouts."""
        try:
            # Base confidence on volatility level
            confidence = min(1.0, volatility)
            
            # Adjust based on market conditions
            if self._is_high_volatility_market():
                confidence *= 0.8  # Reduce confidence in volatile markets
            
            return confidence
        except Exception:
            return 0.0
