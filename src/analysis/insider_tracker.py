from typing import Dict, List, Optional, Union
import asyncio
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from ..utils.market_data import MarketData
from ..models.model_manager import ModelManager

class InsiderTracker:
    """Track and analyze insider trading patterns and institutional holdings."""
    
    def __init__(self):
        self.market_data = MarketData()
        self.model_manager = ModelManager()
        
        # Initialize trackers
        self.insider_trades = {}
        self.institutional_holdings = {}
        self.bulk_deals = {}
        
        # Analysis metrics
        self.analysis_metrics = {
            "insider_buy_signals": [],
            "insider_sell_signals": [],
            "institutional_changes": []
        }
    
    async def track_insider_activity(self, symbols: List[str]) -> Dict:
        """Track insider trading activity for given symbols."""
        try:
            activities = {}
            
            for symbol in symbols:
                # Get insider trading data
                insider_data = await self._get_insider_trades(symbol)
                
                # Analyze institutional holdings
                holdings_data = await self._analyze_institutional_holdings(symbol)
                
                # Track bulk & block deals
                deals_data = await self._track_bulk_deals(symbol)
                
                # Generate trading signals
                signals = self._generate_insider_signals(
                    symbol,
                    insider_data,
                    holdings_data,
                    deals_data
                )
                
                activities[symbol] = {
                    "insider_data": insider_data,
                    "holdings_data": holdings_data,
                    "deals_data": deals_data,
                    "signals": signals,
                    "timestamp": datetime.now()
                }
            
            return activities
        except Exception as e:
            print(f"Error tracking insider activity: {str(e)}")
            return {}
    
    async def get_insider_alerts(self) -> Dict:
        """Get aggregated insider trading alerts and signals."""
        try:
            return {
                "insider_trades": self.insider_trades,
                "institutional_holdings": self.institutional_holdings,
                "bulk_deals": self.bulk_deals,
                "analysis_metrics": self.analysis_metrics,
                "last_update": datetime.now()
            }
        except Exception as e:
            print(f"Error getting insider alerts: {str(e)}")
            return {}
    
    async def detect_insider_patterns(self, symbol: str) -> Dict:
        """Detect trading patterns from insider activity."""
        try:
            # Get latest insider data
            insider_data = await self._get_latest_insider_data(symbol)
            
            # Analyze trading patterns
            pattern_analysis = self._analyze_trading_patterns(
                symbol,
                insider_data
            )
            
            # Detect institutional activity
            institutional_activity = self._detect_institutional_activity(
                symbol,
                insider_data
            )
            
            # Generate trading signals
            signals = self._generate_trading_signals(
                symbol,
                pattern_analysis,
                institutional_activity
            )
            
            return {
                "symbol": symbol,
                "signals": signals,
                "pattern_analysis": pattern_analysis,
                "institutional_activity": institutional_activity,
                "confidence_score": self._calculate_signal_confidence(signals),
                "timestamp": datetime.now()
            }
        except Exception as e:
            print(f"Error detecting insider patterns: {str(e)}")
            return {}
    
    async def _get_insider_trades(self, symbol: str) -> Dict:
        """Get insider trading data from various sources."""
        try:
            trades = {
                "promoter_trades": [],
                "director_trades": [],
                "key_personnel_trades": []
            }
            
            # Get promoter trading data
            promoter_trades = await self._fetch_promoter_trades(symbol)
            trades["promoter_trades"] = promoter_trades
            
            # Get director trading data
            director_trades = await self._fetch_director_trades(symbol)
            trades["director_trades"] = director_trades
            
            # Get key personnel trading data
            key_personnel_trades = await self._fetch_key_personnel_trades(symbol)
            trades["key_personnel_trades"] = key_personnel_trades
            
            return trades
        except Exception:
            return {}
    
    async def _analyze_institutional_holdings(self, symbol: str) -> Dict:
        """Analyze institutional holdings and changes."""
        try:
            holdings = {
                "mutual_funds": [],
                "fii_holdings": [],
                "dii_holdings": [],
                "changes": []
            }
            
            # Get mutual fund holdings
            mf_holdings = await self._fetch_mutual_fund_holdings(symbol)
            holdings["mutual_funds"] = mf_holdings
            
            # Get FII holdings
            fii_holdings = await self._fetch_fii_holdings(symbol)
            holdings["fii_holdings"] = fii_holdings
            
            # Get DII holdings
            dii_holdings = await self._fetch_dii_holdings(symbol)
            holdings["dii_holdings"] = dii_holdings
            
            # Calculate changes
            holdings["changes"] = self._calculate_holding_changes(
                symbol,
                mf_holdings,
                fii_holdings,
                dii_holdings
            )
            
            return holdings
        except Exception:
            return {}
    
    async def _track_bulk_deals(self, symbol: str) -> Dict:
        """Track bulk and block deals."""
        try:
            deals = {
                "bulk_deals": [],
                "block_deals": [],
                "significant_trades": []
            }
            
            # Get bulk deals
            bulk_deals = await self._fetch_bulk_deals(symbol)
            deals["bulk_deals"] = bulk_deals
            
            # Get block deals
            block_deals = await self._fetch_block_deals(symbol)
            deals["block_deals"] = block_deals
            
            # Identify significant trades
            deals["significant_trades"] = self._identify_significant_trades(
                bulk_deals,
                block_deals
            )
            
            return deals
        except Exception:
            return {}
    
    def _generate_insider_signals(self, symbol: str, insider_data: Dict,
                                holdings_data: Dict, deals_data: Dict) -> List[Dict]:
        """Generate trading signals based on insider activity."""
        try:
            signals = []
            
            # Analyze promoter trades
            promoter_signals = self._analyze_promoter_signals(
                insider_data["promoter_trades"]
            )
            signals.extend(promoter_signals)
            
            # Analyze institutional changes
            institutional_signals = self._analyze_institutional_signals(
                holdings_data
            )
            signals.extend(institutional_signals)
            
            # Analyze bulk/block deals
            deals_signals = self._analyze_deals_signals(deals_data)
            signals.extend(deals_signals)
            
            return sorted(
                signals,
                key=lambda x: x.get("confidence", 0),
                reverse=True
            )
        except Exception:
            return []
    
    def _analyze_promoter_signals(self, promoter_trades: List[Dict]) -> List[Dict]:
        """Analyze promoter trading signals."""
        try:
            signals = []
            
            for trade in promoter_trades:
                signal = {
                    "type": "promoter_trade",
                    "action": trade.get("action"),
                    "quantity": trade.get("quantity"),
                    "price": trade.get("price"),
                    "confidence": self._calculate_promoter_confidence(trade)
                }
                
                signals.append(signal)
            
            return signals
        except Exception:
            return []
    
    def _analyze_institutional_signals(self, holdings_data: Dict) -> List[Dict]:
        """Analyze institutional holding signals."""
        try:
            signals = []
            
            # Analyze mutual fund changes
            mf_signals = self._analyze_mf_changes(
                holdings_data.get("mutual_funds", [])
            )
            signals.extend(mf_signals)
            
            # Analyze FII changes
            fii_signals = self._analyze_fii_changes(
                holdings_data.get("fii_holdings", [])
            )
            signals.extend(fii_signals)
            
            # Analyze DII changes
            dii_signals = self._analyze_dii_changes(
                holdings_data.get("dii_holdings", [])
            )
            signals.extend(dii_signals)
            
            return signals
        except Exception:
            return []
    
    def _analyze_deals_signals(self, deals_data: Dict) -> List[Dict]:
        """Analyze bulk and block deal signals."""
        try:
            signals = []
            
            # Analyze bulk deals
            bulk_signals = self._analyze_bulk_deal_signals(
                deals_data.get("bulk_deals", [])
            )
            signals.extend(bulk_signals)
            
            # Analyze block deals
            block_signals = self._analyze_block_deal_signals(
                deals_data.get("block_deals", [])
            )
            signals.extend(block_signals)
            
            return signals
        except Exception:
            return []
    
    def _calculate_promoter_confidence(self, trade: Dict) -> float:
        """Calculate confidence score for promoter trades."""
        try:
            # Base confidence
            confidence = 0.5
            
            # Adjust based on quantity
            quantity_factor = min(1.0, trade.get("quantity", 0) / 100000)
            confidence += quantity_factor * 0.2
            
            # Adjust based on price
            if trade.get("price", 0) > trade.get("market_price", 0):
                confidence += 0.1
            
            # Adjust based on timing
            if self._is_good_timing(trade.get("date")):
                confidence += 0.1
            
            return min(1.0, confidence)
        except Exception:
            return 0.5
    
    def _is_good_timing(self, trade_date: datetime) -> bool:
        """Check if trade timing is favorable."""
        try:
            if not trade_date:
                return False
            
            # Check if trade is near quarter end
            quarter_end = self._get_quarter_end(trade_date)
            days_to_quarter_end = (quarter_end - trade_date).days
            
            return days_to_quarter_end <= 30
        except Exception:
            return False
    
    def _get_quarter_end(self, date: datetime) -> datetime:
        """Get quarter end date for given date."""
        try:
            year = date.year
            month = date.month
            
            # Calculate quarter end month
            quarter_end_month = ((month - 1) // 3 + 1) * 3
            
            # If we're already past quarter end, move to next quarter
            if month > quarter_end_month:
                if quarter_end_month == 12:
                    year += 1
                    quarter_end_month = 3
                else:
                    quarter_end_month += 3
            
            return datetime(year, quarter_end_month, 1) + timedelta(days=32)
        except Exception:
            return date
