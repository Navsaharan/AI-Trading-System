from typing import Dict, List, Optional
from datetime import datetime
import ccxt
import asyncio
from .base import BaseBroker

class BinanceBroker(BaseBroker):
    """Binance broker implementation."""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = False):
        super().__init__(api_key, api_secret)
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot',
                'adjustForTimeDifference': True,
                'testnet': testnet
            }
        })
    
    async def connect(self) -> bool:
        try:
            await self.exchange.load_markets()
            self.is_connected = True
            return True
        except Exception as e:
            print(f"Error connecting to Binance: {str(e)}")
            return False
    
    async def disconnect(self) -> bool:
        self.is_connected = False
        return True
    
    async def get_account_info(self) -> Dict:
        try:
            balance = await self.exchange.fetch_balance()
            return {
                'total': balance['total'],
                'free': balance['free'],
                'used': balance['used']
            }
        except Exception as e:
            print(f"Error fetching account info: {str(e)}")
            return {}
    
    async def place_order(self, symbol: str, side: str, quantity: float,
                         order_type: str = 'market', price: Optional[float] = None) -> Dict:
        try:
            if not self.validate_order(symbol, side, quantity, order_type, price):
                raise ValueError("Invalid order parameters")
            
            params = {
                'symbol': self.format_symbol(symbol),
                'type': order_type,
                'side': side,
                'amount': quantity
            }
            
            if order_type.lower() == 'limit':
                params['price'] = price
            
            order = await self.exchange.create_order(**params)
            return order
        except Exception as e:
            print(f"Error placing order: {str(e)}")
            return {}
    
    async def cancel_order(self, order_id: str) -> bool:
        try:
            await self.exchange.cancel_order(order_id)
            return True
        except Exception as e:
            print(f"Error canceling order: {str(e)}")
            return False
    
    async def get_order_status(self, order_id: str) -> Dict:
        try:
            order = await self.exchange.fetch_order(order_id)
            return order
        except Exception as e:
            print(f"Error fetching order status: {str(e)}")
            return {}
    
    async def get_positions(self) -> List[Dict]:
        try:
            positions = await self.exchange.fetch_positions()
            return positions
        except Exception as e:
            print(f"Error fetching positions: {str(e)}")
            return []
    
    async def get_market_data(self, symbol: str, interval: str = '1m',
                            start_time: Optional[datetime] = None,
                            end_time: Optional[datetime] = None) -> List[Dict]:
        try:
            timeframe = interval
            limit = 1000
            
            ohlcv = await self.exchange.fetch_ohlcv(
                symbol=self.format_symbol(symbol),
                timeframe=timeframe,
                limit=limit,
                since=int(start_time.timestamp() * 1000) if start_time else None
            )
            
            return [{
                'timestamp': candle[0],
                'open': candle[1],
                'high': candle[2],
                'low': candle[3],
                'close': candle[4],
                'volume': candle[5]
            } for candle in ohlcv]
        except Exception as e:
            print(f"Error fetching market data: {str(e)}")
            return []
    
    async def get_ticker(self, symbol: str) -> Dict:
        try:
            ticker = await self.exchange.fetch_ticker(self.format_symbol(symbol))
            return ticker
        except Exception as e:
            print(f"Error fetching ticker: {str(e)}")
            return {}
    
    async def get_exchange_info(self) -> Dict:
        try:
            markets = self.exchange.markets
            return {
                'symbols': list(markets.keys()),
                'exchange_filters': self.exchange.exchange_filters,
                'markets': markets
            }
        except Exception as e:
            print(f"Error fetching exchange info: {str(e)}")
            return {}
    
    def format_symbol(self, symbol: str) -> str:
        """Format symbol according to Binance's requirements."""
        return symbol.upper().replace('-', '')
    
    async def subscribe_to_market_data(self, symbols: List[str], callback) -> bool:
        # Note: This is a simplified implementation. In a production environment,
        # you would want to use Binance's WebSocket API for real-time data
        try:
            while True:
                for symbol in symbols:
                    ticker = await self.get_ticker(symbol)
                    await callback(ticker)
                await asyncio.sleep(1)
        except Exception as e:
            print(f"Error in market data subscription: {str(e)}")
            return False
    
    async def unsubscribe_from_market_data(self, symbols: List[str]) -> bool:
        # Implement WebSocket connection closing logic here
        return True
