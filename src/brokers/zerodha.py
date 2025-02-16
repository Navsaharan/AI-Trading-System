from typing import Dict, List, Optional
from datetime import datetime
from kiteconnect import KiteConnect
from kiteconnect import KiteTicker
import pandas as pd
from .base import BaseBroker

class ZerodhaBroker(BaseBroker):
    """Zerodha (Kite) broker implementation."""
    
    def __init__(self, api_key: str, api_secret: str):
        super().__init__(api_key, api_secret)
        self.kite = None
        self.ticker = None
        self.access_token = None
    
    async def connect(self) -> bool:
        """Connect to Zerodha API."""
        try:
            self.kite = KiteConnect(api_key=self.api_key)
            
            if not self.access_token:
                # Generate session
                data = self.kite.generate_session(request_token=self.api_secret,
                                                api_secret=self.api_secret)
                self.access_token = data["access_token"]
            
            self.kite.set_access_token(self.access_token)
            
            # Initialize ticker
            self.ticker = KiteTicker(self.api_key, self.access_token)
            
            self.is_connected = True
            return True
        except Exception as e:
            print(f"Error connecting to Zerodha: {str(e)}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from Zerodha API."""
        try:
            if self.ticker:
                self.ticker.close()
            self.is_connected = False
            return True
        except Exception as e:
            print(f"Error disconnecting from Zerodha: {str(e)}")
            return False
    
    async def get_account_info(self) -> Dict:
        """Get account information."""
        try:
            margins = self.kite.margins()
            return {
                'balance': float(margins['equity']['available']['cash']),
                'used_margin': float(margins['equity']['utilised']['debits']),
                'available_margin': float(margins['equity']['net'])
            }
        except Exception as e:
            print(f"Error getting account info: {str(e)}")
            return {}
    
    async def place_order(self, symbol: str, side: str, quantity: float,
                         order_type: str = 'MARKET', price: Optional[float] = None) -> Dict:
        """Place a new order."""
        try:
            order_params = {
                "tradingsymbol": self.format_symbol(symbol),
                "exchange": "NSE",  # or BSE, NFO depending on the symbol
                "transaction_type": "BUY" if side.upper() == "BUY" else "SELL",
                "quantity": int(quantity),
                "order_type": order_type.upper(),
                "product": "MIS"  # or CNC for delivery
            }
            
            if order_type.upper() == "LIMIT" and price:
                order_params["price"] = price
            
            order_id = self.kite.place_order(**order_params)
            
            # Get order details
            order = self.kite.order_history(order_id)[-1]
            
            return {
                'order_id': order_id,
                'status': order['status'],
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
            self.kite.cancel_order(order_id=order_id)
            return True
        except Exception as e:
            print(f"Error canceling order: {str(e)}")
            return False
    
    async def get_order_status(self, order_id: str) -> Dict:
        """Get status of an order."""
        try:
            order = self.kite.order_history(order_id)[-1]
            return {
                'order_id': order['order_id'],
                'status': order['status'],
                'filled_quantity': order['filled_quantity'],
                'pending_quantity': order['pending_quantity'],
                'average_price': order['average_price']
            }
        except Exception as e:
            print(f"Error getting order status: {str(e)}")
            return {}
    
    async def get_positions(self) -> List[Dict]:
        """Get current positions."""
        try:
            positions = self.kite.positions()['net']
            return [{
                'symbol': pos['tradingsymbol'],
                'quantity': pos['quantity'],
                'average_price': pos['average_price'],
                'current_price': pos['last_price'],
                'pnl': pos['pnl']
            } for pos in positions]
        except Exception as e:
            print(f"Error getting positions: {str(e)}")
            return []
    
    async def get_market_data(self, symbol: str, interval: str = 'minute',
                            start_time: Optional[datetime] = None,
                            end_time: Optional[datetime] = None) -> List[Dict]:
        """Get historical market data."""
        try:
            # Convert interval to Kite format
            interval_map = {
                'minute': 'minute',
                '5minute': '5minute',
                '15minute': '15minute',
                'hour': '60minute',
                'day': 'day'
            }
            
            kite_interval = interval_map.get(interval, 'minute')
            
            # Get instrument token
            instruments = self.kite.instruments()
            instrument = next((i for i in instruments if i['tradingsymbol'] == symbol), None)
            
            if not instrument:
                raise ValueError(f"Symbol not found: {symbol}")
            
            # Fetch historical data
            data = self.kite.historical_data(
                instrument['instrument_token'],
                from_date=start_time,
                to_date=end_time,
                interval=kite_interval
            )
            
            return [{
                'timestamp': candle['date'],
                'open': candle['open'],
                'high': candle['high'],
                'low': candle['low'],
                'close': candle['close'],
                'volume': candle['volume']
            } for candle in data]
        except Exception as e:
            print(f"Error getting market data: {str(e)}")
            return []
    
    async def get_ticker(self, symbol: str) -> Dict:
        """Get current market price for a symbol."""
        try:
            quote = self.kite.quote(self.format_symbol(symbol))
            data = quote[self.format_symbol(symbol)]
            
            return {
                'symbol': symbol,
                'last_price': data['last_price'],
                'volume': data['volume'],
                'change': data['net_change'],
                'high': data['ohlc']['high'],
                'low': data['ohlc']['low']
            }
        except Exception as e:
            print(f"Error getting ticker: {str(e)}")
            return {}
    
    async def get_exchange_info(self) -> Dict:
        """Get exchange information."""
        try:
            instruments = self.kite.instruments()
            return {
                'symbols': [i['tradingsymbol'] for i in instruments],
                'exchange_status': 'open',  # Zerodha doesn't provide direct status
                'instruments': instruments
            }
        except Exception as e:
            print(f"Error getting exchange info: {str(e)}")
            return {}
    
    def format_symbol(self, symbol: str) -> str:
        """Format symbol according to Zerodha requirements."""
        # Zerodha uses NSE:SYMBOL format
        if ":" not in symbol:
            return f"NSE:{symbol}"
        return symbol
    
    async def subscribe_to_market_data(self, symbols: List[str], callback) -> bool:
        """Subscribe to real-time market data."""
        try:
            # Get instrument tokens
            instruments = self.kite.instruments()
            tokens = [
                i['instrument_token'] 
                for i in instruments 
                if i['tradingsymbol'] in symbols
            ]
            
            def on_ticks(ws, ticks):
                for tick in ticks:
                    callback({
                        'symbol': tick['tradingsymbol'],
                        'price': tick['last_price'],
                        'volume': tick['volume'],
                        'timestamp': tick['timestamp']
                    })
            
            def on_connect(ws, response):
                ws.subscribe(tokens)
                ws.set_mode(ws.MODE_FULL, tokens)
            
            self.ticker.on_ticks = on_ticks
            self.ticker.on_connect = on_connect
            self.ticker.connect()
            
            return True
        except Exception as e:
            print(f"Error subscribing to market data: {str(e)}")
            return False
    
    async def unsubscribe_from_market_data(self, symbols: List[str]) -> bool:
        """Unsubscribe from real-time market data."""
        try:
            instruments = self.kite.instruments()
            tokens = [
                i['instrument_token'] 
                for i in instruments 
                if i['tradingsymbol'] in symbols
            ]
            self.ticker.unsubscribe(tokens)
            return True
        except Exception as e:
            print(f"Error unsubscribing from market data: {str(e)}")
            return False
