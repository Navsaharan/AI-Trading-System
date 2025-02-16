from abc import ABC, abstractmethod
import yfinance as yf
import pandas as pd
from alpha_vantage.timeseries import TimeSeries
from tradingview_ta import TA_Handler
import investpy
import requests
from typing import Dict, List, Optional
from ..models.api_models import APIConfiguration

class MarketDataSource(ABC):
    @abstractmethod
    async def get_price(self, symbol: str) -> float:
        pass
    
    @abstractmethod
    async def get_historical_data(self, symbol: str, interval: str = '1d') -> pd.DataFrame:
        pass
    
    @abstractmethod
    async def get_news(self, symbol: str) -> List[Dict]:
        pass

class YahooFinanceSource(MarketDataSource):
    async def get_price(self, symbol: str) -> float:
        ticker = yf.Ticker(symbol)
        return ticker.info['regularMarketPrice']
    
    async def get_historical_data(self, symbol: str, interval: str = '1d') -> pd.DataFrame:
        ticker = yf.Ticker(symbol)
        return ticker.history(period='1y', interval=interval)
    
    async def get_news(self, symbol: str) -> List[Dict]:
        ticker = yf.Ticker(symbol)
        return ticker.news

class AlphaVantageSource(MarketDataSource):
    def __init__(self, api_key: str):
        self.ts = TimeSeries(key=api_key, output_format='pandas')
    
    async def get_price(self, symbol: str) -> float:
        data, _ = self.ts.get_quote_endpoint(symbol)
        return float(data['05. price'][0])
    
    async def get_historical_data(self, symbol: str, interval: str = '1d') -> pd.DataFrame:
        data, _ = self.ts.get_daily(symbol=symbol, outputsize='full')
        return data
    
    async def get_news(self, symbol: str) -> List[Dict]:
        # Alpha Vantage doesn't provide news, return empty list
        return []

class TradingViewSource(MarketDataSource):
    def __init__(self, exchange: str = 'NSE'):
        self.exchange = exchange
    
    async def get_price(self, symbol: str) -> float:
        handler = TA_Handler(
            symbol=symbol,
            exchange=self.exchange,
            screener="india",
            interval="1d"
        )
        analysis = handler.get_analysis()
        return analysis.indicators['close']
    
    async def get_historical_data(self, symbol: str, interval: str = '1d') -> pd.DataFrame:
        handler = TA_Handler(
            symbol=symbol,
            exchange=self.exchange,
            screener="india",
            interval=interval
        )
        return handler.get_analysis().indicators
    
    async def get_news(self, symbol: str) -> List[Dict]:
        # TradingView API doesn't provide news directly
        return []

class InvestingComSource(MarketDataSource):
    async def get_price(self, symbol: str) -> float:
        search_result = investpy.search_quotes(text=symbol, products=['stocks'], countries=['india'])
        return search_result[0].retrieve_recent_data()['Close'].iloc[-1]
    
    async def get_historical_data(self, symbol: str, interval: str = '1d') -> pd.DataFrame:
        search_result = investpy.search_quotes(text=symbol, products=['stocks'], countries=['india'])
        return search_result[0].retrieve_historical_data()
    
    async def get_news(self, symbol: str) -> List[Dict]:
        news = investpy.news.economic_calendar()
        return news.to_dict('records')

class MarketDataManager:
    def __init__(self):
        self.sources: Dict[str, MarketDataSource] = {}
        self.active_source: Optional[str] = None
    
    async def add_source(self, name: str, source: MarketDataSource):
        """Add a new data source"""
        self.sources[name] = source
        if not self.active_source:
            self.active_source = name
    
    async def switch_source(self, name: str):
        """Switch to a different data source"""
        if name not in self.sources:
            raise ValueError(f"Source {name} not found")
        self.active_source = name
    
    async def get_price(self, symbol: str) -> float:
        """Get price from active source with fallback"""
        try:
            return await self.sources[self.active_source].get_price(symbol)
        except Exception as e:
            print(f"Error with primary source: {str(e)}")
            # Try other sources
            for name, source in self.sources.items():
                if name != self.active_source:
                    try:
                        return await source.get_price(symbol)
                    except:
                        continue
            raise Exception("All data sources failed")
    
    async def get_historical_data(self, symbol: str, interval: str = '1d') -> pd.DataFrame:
        """Get historical data from active source with fallback"""
        try:
            return await self.sources[self.active_source].get_historical_data(symbol, interval)
        except Exception as e:
            print(f"Error with primary source: {str(e)}")
            # Try other sources
            for name, source in self.sources.items():
                if name != self.active_source:
                    try:
                        return await source.get_historical_data(symbol, interval)
                    except:
                        continue
            raise Exception("All data sources failed")
    
    async def get_news(self, symbol: str) -> List[Dict]:
        """Get news from all available sources"""
        all_news = []
        for source in self.sources.values():
            try:
                news = await source.get_news(symbol)
                all_news.extend(news)
            except:
                continue
        return all_news

# Initialize with default sources
async def initialize_market_data():
    manager = MarketDataManager()
    
    # Get API configurations from database
    configs = APIConfiguration.query.filter_by(is_active=True).all()
    
    for config in configs:
        if config.provider.name == 'alpha_vantage':
            await manager.add_source('alpha_vantage', 
                AlphaVantageSource(config.credentials['api_key']))
    
    # Add free sources
    await manager.add_source('yahoo_finance', YahooFinanceSource())
    await manager.add_source('trading_view', TradingViewSource())
    await manager.add_source('investing_com', InvestingComSource())
    
    return manager
