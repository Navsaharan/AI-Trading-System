from typing import Dict, List, Optional, Union
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import yfinance as yf
from ..brokers.base import BaseBroker

class MarketData:
    """Handles real-time and historical market data from multiple sources."""
    
    def __init__(self):
        self.data_sources = {
            "primary": ["broker_api", "yahoo_finance"],
            "secondary": ["google_finance", "investing_com"],
            "fallback": ["web_scraping"]
        }
        self.cache = {}
        self.cache_timeout = 5  # seconds
    
    async def get_real_time_price(self, symbol: str,
                                broker: Optional[BaseBroker] = None) -> Dict:
        """Get real-time price from multiple sources for arbitrage."""
        try:
            prices = {}
            tasks = []
            
            # Get price from broker API if available
            if broker and broker.is_connected:
                prices["broker"] = await broker.get_ticker(symbol)
            
            # Get price from Yahoo Finance
            tasks.append(self._get_yahoo_finance_price(symbol))
            
            # Get price from Google Finance
            tasks.append(self._get_google_finance_price(symbol))
            
            # Get prices from all sources concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Combine results
            for i, source in enumerate(["yahoo", "google"]):
                if isinstance(results[i], dict):
                    prices[source] = results[i]
            
            # Check for arbitrage opportunities
            if len(prices) >= 2:
                arbitrage = await self._check_arbitrage(prices)
                if arbitrage["opportunity"]:
                    prices["arbitrage"] = arbitrage
            
            return prices
        except Exception as e:
            print(f"Error getting real-time price: {str(e)}")
            return {}
    
    async def get_historical_data(self, symbol: str, interval: str = "1d",
                                start_date: Optional[datetime] = None,
                                end_date: Optional[datetime] = None,
                                limit: Optional[int] = None) -> pd.DataFrame:
        """Get historical market data from multiple sources."""
        try:
            # Try to get from cache first
            cache_key = f"{symbol}_{interval}_{start_date}_{end_date}"
            if cache_key in self.cache:
                cache_time, data = self.cache[cache_key]
                if datetime.now() - cache_time < timedelta(seconds=self.cache_timeout):
                    return data
            
            # Set default dates if not provided
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                if limit:
                    start_date = end_date - timedelta(days=limit)
                else:
                    start_date = end_date - timedelta(days=30)
            
            # Try primary sources first
            data = await self._get_yahoo_finance_history(
                symbol, interval, start_date, end_date
            )
            
            if data.empty:
                # Try secondary sources
                data = await self._get_investing_com_history(
                    symbol, interval, start_date, end_date
                )
            
            # Cache the data
            self.cache[cache_key] = (datetime.now(), data)
            
            return data
        except Exception as e:
            print(f"Error getting historical data: {str(e)}")
            return pd.DataFrame()
    
    async def get_market_depth(self, symbol: str,
                             broker: Optional[BaseBroker] = None) -> Dict:
        """Get market depth (order book) data."""
        try:
            if broker and broker.is_connected:
                return await broker.get_market_depth(symbol)
            return {}
        except Exception as e:
            print(f"Error getting market depth: {str(e)}")
            return {}
    
    async def get_technical_indicators(self, symbol: str,
                                    indicators: List[str]) -> Dict:
        """Calculate technical indicators for a symbol."""
        try:
            # Get historical data
            data = await self.get_historical_data(symbol, interval="1d", limit=100)
            if data.empty:
                return {}
            
            results = {}
            
            # Calculate requested indicators
            for indicator in indicators:
                if indicator == "sma":
                    results["sma_20"] = self._calculate_sma(data, 20)
                    results["sma_50"] = self._calculate_sma(data, 50)
                elif indicator == "ema":
                    results["ema_12"] = self._calculate_ema(data, 12)
                    results["ema_26"] = self._calculate_ema(data, 26)
                elif indicator == "rsi":
                    results["rsi"] = self._calculate_rsi(data)
                elif indicator == "macd":
                    results["macd"] = self._calculate_macd(data)
            
            return results
        except Exception as e:
            print(f"Error calculating indicators: {str(e)}")
            return {}
    
    async def _get_yahoo_finance_price(self, symbol: str) -> Dict:
        """Get real-time price from Yahoo Finance."""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return {
                "price": info.get("regularMarketPrice", 0),
                "volume": info.get("regularMarketVolume", 0),
                "timestamp": datetime.now(),
                "source": "yahoo"
            }
        except Exception:
            return {}
    
    async def _get_google_finance_price(self, symbol: str) -> Dict:
        """Get real-time price from Google Finance."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://www.google.com/finance/quote/{symbol}"
                async with session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, "html.parser")
                        price_div = soup.find("div", {"class": "YMlKec fxKbKc"})
                        if price_div:
                            return {
                                "price": float(price_div.text.replace(",", "")),
                                "timestamp": datetime.now(),
                                "source": "google"
                            }
            return {}
        except Exception:
            return {}
    
    async def _get_yahoo_finance_history(self, symbol: str, interval: str,
                                       start_date: datetime,
                                       end_date: datetime) -> pd.DataFrame:
        """Get historical data from Yahoo Finance."""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(
                start=start_date,
                end=end_date,
                interval=interval
            )
            return data
        except Exception:
            return pd.DataFrame()
    
    async def _get_investing_com_history(self, symbol: str, interval: str,
                                       start_date: datetime,
                                       end_date: datetime) -> pd.DataFrame:
        """Get historical data from Investing.com."""
        # Implementation for scraping Investing.com
        return pd.DataFrame()
    
    async def _check_arbitrage(self, prices: Dict) -> Dict:
        """Check for arbitrage opportunities between different price sources."""
        try:
            price_list = [p.get("price", 0) for p in prices.values() if p.get("price")]
            if not price_list:
                return {"opportunity": False}
            
            min_price = min(price_list)
            max_price = max(price_list)
            spread = max_price - min_price
            
            # Calculate if arbitrage is profitable after fees
            fees = max_price * 0.001  # Assuming 0.1% trading fee
            net_profit = spread - fees
            
            return {
                "opportunity": net_profit > 0,
                "buy_price": min_price,
                "sell_price": max_price,
                "spread": spread,
                "net_profit": net_profit,
                "timestamp": datetime.now()
            }
        except Exception:
            return {"opportunity": False}
    
    def _calculate_sma(self, data: pd.DataFrame, period: int) -> pd.Series:
        """Calculate Simple Moving Average."""
        return data["Close"].rolling(window=period).mean()
    
    def _calculate_ema(self, data: pd.DataFrame, period: int) -> pd.Series:
        """Calculate Exponential Moving Average."""
        return data["Close"].ewm(span=period, adjust=False).mean()
    
    def _calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index."""
        delta = data["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def _calculate_macd(self, data: pd.DataFrame) -> Dict[str, pd.Series]:
        """Calculate MACD (Moving Average Convergence Divergence)."""
        exp1 = data["Close"].ewm(span=12, adjust=False).mean()
        exp2 = data["Close"].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal
        return {
            "macd": macd,
            "signal": signal,
            "histogram": histogram
        }
