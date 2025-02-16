from typing import Dict, List, Optional, Union
import asyncio
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from ..utils.market_data import MarketData
from ..models.model_manager import ModelManager

class EconomicCalendar:
    """Track and analyze economic events and their market impact."""
    
    def __init__(self):
        self.market_data = MarketData()
        self.model_manager = ModelManager()
        
        # Initialize trackers
        self.economic_events = {}
        self.market_impacts = {}
        self.global_trends = {}
        
        # Analysis metrics
        self.analysis_metrics = {
            "high_impact_events": [],
            "market_sentiment": {},
            "correlation_data": {}
        }
    
    async def track_economic_events(self) -> Dict:
        """Track upcoming and recent economic events."""
        try:
            events = {
                "upcoming": await self._get_upcoming_events(),
                "recent": await self._get_recent_events(),
                "high_impact": await self._get_high_impact_events(),
                "market_impact": self._calculate_market_impact(),
                "timestamp": datetime.now()
            }
            
            # Update internal trackers
            self.economic_events = events
            
            return events
        except Exception as e:
            print(f"Error tracking economic events: {str(e)}")
            return {}
    
    async def analyze_global_markets(self) -> Dict:
        """Analyze global market trends and correlations."""
        try:
            analysis = {
                "us_markets": await self._analyze_us_markets(),
                "european_markets": await self._analyze_european_markets(),
                "asian_markets": await self._analyze_asian_markets(),
                "forex_markets": await self._analyze_forex_markets(),
                "crypto_markets": await self._analyze_crypto_markets(),
                "correlations": self._calculate_market_correlations(),
                "timestamp": datetime.now()
            }
            
            # Update internal trackers
            self.global_trends = analysis
            
            return analysis
        except Exception as e:
            print(f"Error analyzing global markets: {str(e)}")
            return {}
    
    async def get_trading_signals(self) -> Dict:
        """Generate trading signals based on economic events."""
        try:
            signals = {
                "event_based": self._generate_event_signals(),
                "market_based": self._generate_market_signals(),
                "correlation_based": self._generate_correlation_signals(),
                "confidence_scores": self._calculate_signal_confidence(),
                "timestamp": datetime.now()
            }
            
            return signals
        except Exception as e:
            print(f"Error generating trading signals: {str(e)}")
            return {}
    
    async def _get_upcoming_events(self) -> List[Dict]:
        """Get upcoming economic events."""
        try:
            events = []
            
            # Get events from various sources
            fed_events = await self._get_fed_events()
            events.extend(fed_events)
            
            rbi_events = await self._get_rbi_events()
            events.extend(rbi_events)
            
            earnings_events = await self._get_earnings_events()
            events.extend(earnings_events)
            
            # Sort by date and impact
            events = sorted(
                events,
                key=lambda x: (x.get("date"), -x.get("impact_score", 0))
            )
            
            return events
        except Exception:
            return []
    
    async def _get_recent_events(self) -> List[Dict]:
        """Get recent economic events and their impact."""
        try:
            events = []
            
            # Get recent events from various sources
            fed_events = await self._get_recent_fed_events()
            events.extend(fed_events)
            
            rbi_events = await self._get_recent_rbi_events()
            events.extend(rbi_events)
            
            earnings_events = await self._get_recent_earnings_events()
            events.extend(earnings_events)
            
            # Calculate impact for each event
            for event in events:
                event["market_impact"] = self._calculate_event_impact(event)
            
            return sorted(
                events,
                key=lambda x: x.get("date"),
                reverse=True
            )
        except Exception:
            return []
    
    async def _get_high_impact_events(self) -> List[Dict]:
        """Get high-impact economic events."""
        try:
            events = []
            
            # Get all events
            all_events = await self._get_upcoming_events()
            
            # Filter high-impact events
            for event in all_events:
                if event.get("impact_score", 0) >= 0.7:  # High impact threshold
                    events.append(event)
            
            return events
        except Exception:
            return []
    
    def _calculate_market_impact(self) -> Dict:
        """Calculate market impact of economic events."""
        try:
            impact = {
                "immediate": self._calculate_immediate_impact(),
                "delayed": self._calculate_delayed_impact(),
                "sector_specific": self._calculate_sector_impact(),
                "global": self._calculate_global_impact()
            }
            
            return impact
        except Exception:
            return {}
    
    async def _analyze_us_markets(self) -> Dict:
        """Analyze US market trends."""
        try:
            analysis = {
                "indices": await self._analyze_us_indices(),
                "sectors": await self._analyze_us_sectors(),
                "futures": await self._analyze_us_futures(),
                "sentiment": self._calculate_us_sentiment()
            }
            
            return analysis
        except Exception:
            return {}
    
    async def _analyze_european_markets(self) -> Dict:
        """Analyze European market trends."""
        try:
            analysis = {
                "indices": await self._analyze_eu_indices(),
                "currencies": await self._analyze_eu_currencies(),
                "sentiment": self._calculate_eu_sentiment()
            }
            
            return analysis
        except Exception:
            return {}
    
    async def _analyze_asian_markets(self) -> Dict:
        """Analyze Asian market trends."""
        try:
            analysis = {
                "indices": await self._analyze_asian_indices(),
                "currencies": await self._analyze_asian_currencies(),
                "sentiment": self._calculate_asian_sentiment()
            }
            
            return analysis
        except Exception:
            return {}
    
    def _calculate_market_correlations(self) -> Dict:
        """Calculate correlations between different markets."""
        try:
            correlations = {
                "us_india": self._calculate_us_india_correlation(),
                "europe_india": self._calculate_europe_india_correlation(),
                "asia_india": self._calculate_asia_india_correlation(),
                "crypto_equity": self._calculate_crypto_equity_correlation()
            }
            
            return correlations
        except Exception:
            return {}
    
    def _generate_event_signals(self) -> List[Dict]:
        """Generate trading signals based on economic events."""
        try:
            signals = []
            
            # Generate signals for each high-impact event
            for event in self.economic_events.get("high_impact", []):
                signal = self._generate_event_based_signal(event)
                if signal:
                    signals.append(signal)
            
            return signals
        except Exception:
            return []
    
    def _generate_market_signals(self) -> List[Dict]:
        """Generate trading signals based on market trends."""
        try:
            signals = []
            
            # Generate signals for each market
            us_signals = self._generate_us_market_signals()
            signals.extend(us_signals)
            
            eu_signals = self._generate_eu_market_signals()
            signals.extend(eu_signals)
            
            asia_signals = self._generate_asia_market_signals()
            signals.extend(asia_signals)
            
            return signals
        except Exception:
            return []
    
    def _generate_correlation_signals(self) -> List[Dict]:
        """Generate trading signals based on market correlations."""
        try:
            signals = []
            
            # Generate correlation-based signals
            correlations = self._calculate_market_correlations()
            
            for market, correlation in correlations.items():
                if abs(correlation) > 0.7:  # Strong correlation threshold
                    signal = {
                        "type": "correlation",
                        "market": market,
                        "correlation": correlation,
                        "confidence": abs(correlation),
                        "timestamp": datetime.now()
                    }
                    signals.append(signal)
            
            return signals
        except Exception:
            return []
    
    def _calculate_signal_confidence(self) -> Dict:
        """Calculate confidence scores for trading signals."""
        try:
            confidence = {
                "event_signals": self._calculate_event_signal_confidence(),
                "market_signals": self._calculate_market_signal_confidence(),
                "correlation_signals": self._calculate_correlation_signal_confidence()
            }
            
            return confidence
        except Exception:
            return {}
