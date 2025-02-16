from typing import Dict, List, Optional
from datetime import datetime
import upstox_client
from upstox_client.rest import ApiException
from .base import BaseBroker

class UpstoxBroker(BaseBroker):
    """Upstox broker implementation."""
    
    def __init__(self, api_key: str, api_secret: str, redirect_uri: str):
        super().__init__(api_key, api_secret)
        self.redirect_uri = redirect_uri
        self.client = None
        self.access_token = None
        
    async def connect(self) -> bool:
        """Connect to Upstox API."""
        try:
            configuration = upstox_client.Configuration(
                host = "https://api.upstox.com/v2"
            )
            configuration.api_key['apiKey'] = self.api_key
            configuration.api_key['accessToken'] = self.access_token
            
            self.client = upstox_client.ApiClient(configuration)
            self.market_api = upstox_client.MarketApi(self.client)
            self.trading_api = upstox_client.TradingApi(self.client)
            self.user_api = upstox_client.UserApi(self.client)
            
            # Verify connection
            profile = self.user_api.get_profile()
            self.is_connected = True
            return True
        except Exception as e:
            print(f"Error connecting to Upstox: {str(e)}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from Upstox API."""
        try:
            if self.client:
                self.client.close()
            self.is_connected = False
            return True
        except Exception as e:
            print(f"Error disconnecting from Upstox: {str(e)}")
            return False
    
    async def get_account_info(self) -> Dict:
        """Get account information."""
        try:
            funds = self.trading_api.get_fund_limits()
            return {
                'balance': float(funds.data.utilized.fund),
                'available_margin': float(funds.data.utilized.available_margin),
                'used_margin': float(funds.data.utilized.used_margin)
            }
        except Exception as e:
            print(f"Error getting account info: {str(e)}")
            return {}
    
    async def place_order(self, symbol: str, side: str, quantity: float,
                         order_type: str = 'MARKET', price: Optional[float] = None) -> Dict:
        """Place a new order."""
        try:
            order_params = {
                "quantity": int(quantity),
                "symbol": self.format_symbol(symbol),
                "side": "BUY" if side.upper() == "BUY" else "SELL",
                "order_type": order_type.upper(),
                "product": "D",  # Day trading
                "validity": "DAY"
            }
            
            if order_type.upper() == "LIMIT" and price:
                order_params["price"] = price
            
            response = self.trading_api.place_order(**order_params)
            
            return {
                'order_id': response.data.order_id,
                'status': response.data.status,
                'symbol': symbol,
                'quantity': quantity,
                'side': side,
                'type': order_type,
                'price': price
            }
        except Exception as e:
            print(f"Error placing order: {str(e)}")
            return {}
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an existing order."""
        try:
            response = self.trading_api.cancel_order(order_id)
            return response.status == "success"
        except Exception as e:
            print(f"Error canceling order: {str(e)}")
            return False
    
    async def get_order_status(self, order_id: str) -> Dict:
        """Get status of an order."""
        try:
            response = self.trading_api.get_order_details(order_id)
            return {
                'order_id': response.data.order_id,
                'status': response.data.status,
                'filled_quantity': response.data.filled_quantity,
                'remaining_quantity': response.data.remaining_quantity,
                'average_price': response.data.average_price
            }
        except Exception as e:
            print(f"Error getting order status: {str(e)}")
            return {}
    
    async def get_positions(self) -> List[Dict]:
        """Get current positions."""
        try:
            response = self.trading_api.get_positions()
            positions = []
            for pos in response.data:
                positions.append({
                    'symbol': pos.symbol,
                    'quantity': pos.quantity,
                    'average_price': pos.average_price,
                    'current_price': pos.last_price,
                    'pnl': pos.pnl
                })
            return positions
        except Exception as e:
            print(f"Error getting positions: {str(e)}")
            return []
    
    async def get_market_data(self, symbol: str, interval: str = '1minute',
                            start_time: Optional[datetime] = None,
                            end_time: Optional[datetime] = None) -> List[Dict]:
        """Get historical market data."""
        try:
            params = {
                "symbol": self.format_symbol(symbol),
                "interval": interval,
                "from_date": start_time.strftime("%Y-%m-%d") if start_time else None,
                "to_date": end_time.strftime("%Y-%m-%d") if end_time else None
            }
            
            response = self.market_api.get_historical_candle_data(**params)
            
            candles = []
            for candle in response.data:
                candles.append({
                    'timestamp': candle.timestamp,
                    'open': candle.open,
                    'high': candle.high,
                    'low': candle.low,
                    'close': candle.close,
                    'volume': candle.volume
                })
            return candles
        except Exception as e:
            print(f"Error getting market data: {str(e)}")
            return []
    
    async def get_ticker(self, symbol: str) -> Dict:
        """Get current market price for a symbol."""
        try:
            response = self.market_api.get_market_quote(self.format_symbol(symbol))
            return {
                'symbol': symbol,
                'last_price': response.data.last_price,
                'volume': response.data.volume,
                'change': response.data.change_percentage,
                'high': response.data.high,
                'low': response.data.low
            }
        except Exception as e:
            print(f"Error getting ticker: {str(e)}")
            return {}
    
    async def get_exchange_info(self) -> Dict:
        """Get exchange information."""
        try:
            response = self.market_api.get_market_quotes_info()
            return {
                'exchange_status': response.data.exchange_status,
                'market_type': response.data.market_type,
                'symbols': response.data.symbols
            }
        except Exception as e:
            print(f"Error getting exchange info: {str(e)}")
            return {}
    
    def format_symbol(self, symbol: str) -> str:
        """Format symbol according to Upstox requirements."""
        # Upstox requires symbols in format: NSE_EQ|BSE_EQ|NSE_FO|BSE_FO
        if "_" not in symbol:
            return f"NSE_EQ:{symbol}"
        return symbol
    
    async def subscribe_to_market_data(self, symbols: List[str], callback) -> bool:
        """Subscribe to real-time market data."""
        try:
            formatted_symbols = [self.format_symbol(s) for s in symbols]
            self.market_api.subscribe(formatted_symbols)
            # Implementation of WebSocket connection and data handling
            return True
        except Exception as e:
            print(f"Error subscribing to market data: {str(e)}")
            return False
    
    async def unsubscribe_from_market_data(self, symbols: List[str]) -> bool:
        """Unsubscribe from real-time market data."""
        try:
            formatted_symbols = [self.format_symbol(s) for s in symbols]
            self.market_api.unsubscribe(formatted_symbols)
            return True
        except Exception as e:
            print(f"Error unsubscribing from market data: {str(e)}")
            return False
