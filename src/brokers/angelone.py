from typing import Dict, List, Optional
from datetime import datetime
from smartapi import SmartConnect
import os
import pandas as pd
import logging
from .base import BaseBroker

logger = logging.getLogger(__name__)

class AngelOneBroker(BaseBroker):
    """Angel One broker implementation using Smart API."""
    
    def __init__(self):
        self.api_key = os.getenv('ANGEL_API_KEY')
        self.client_id = os.getenv('ANGEL_CLIENT_ID')
        self.password = os.getenv('ANGEL_PASSWORD')
        self.token = os.getenv('ANGEL_TOKEN')
        
        if not all([self.api_key, self.client_id, self.password, self.token]):
            raise ValueError("Missing required Angel One credentials in environment variables")
            
        super().__init__(self.api_key, self.token)
        self.smart_api = None
        self.feed_token = None
        self.is_connected = False
        
    async def connect(self) -> bool:
        """Connect to Angel One API."""
        try:
            if self.is_connected:
                logger.info("Already connected to Angel One")
                return True
                
            self.smart_api = SmartConnect(api_key=self.api_key)
            data = self.smart_api.generateSession(self.client_id, self.password)
            
            if not data.get('data'):
                logger.error(f"Failed to generate session: {data.get('message')}")
                return False
                
            self.feed_token = data['data']['feedToken']
            
            # Verify connection
            profile = self.smart_api.getProfile(self.feed_token)
            if profile.get('status'):
                self.is_connected = True
                logger.info("Successfully connected to Angel One")
                return True
                
            logger.error(f"Failed to get profile: {profile.get('message')}")
            return False
            
        except Exception as e:
            logger.error(f"Error connecting to Angel One: {str(e)}")
            return False
            
    async def disconnect(self) -> bool:
        """Disconnect from Angel One API."""
        try:
            if not self.is_connected:
                logger.info("Already disconnected from Angel One")
                return True
                
            if self.smart_api:
                self.smart_api.terminateSession(self.client_id)
                
            self.is_connected = False
            self.feed_token = None
            logger.info("Successfully disconnected from Angel One")
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting from Angel One: {str(e)}")
            return False
            
    async def get_account_info(self) -> Dict:
        """Get account information."""
        try:
            if not self.is_connected:
                logger.error("Not connected to Angel One")
                return {}
                
            rms_data = self.smart_api.rmsLimit()['data']
            return {
                'balance': float(rms_data['availablecash']),
                'used_margin': float(rms_data['utilizedamount']),
                'available_margin': float(rms_data['net'])
            }
        except Exception as e:
            logger.error(f"Error getting account info: {str(e)}")
            return {}
    
    async def place_order(self, symbol: str, qty: int, side: str, order_type: str = 'MARKET') -> Optional[str]:
        """Place a new order."""
        try:
            if not self.is_connected:
                logger.error("Not connected to Angel One")
                return None
                
            orderparams = {
                "variety": "NORMAL",
                "tradingsymbol": symbol,
                "symboltoken": self.get_token(symbol),
                "transactiontype": side,
                "exchange": "NSE",
                "ordertype": order_type,
                "producttype": "INTRADAY",
                "duration": "DAY",
                "quantity": qty
            }
            
            order_id = self.smart_api.placeOrder(orderparams)
            if order_id:
                logger.info(f"Successfully placed order: {order_id}")
                return order_id
                
            logger.error("Failed to place order")
            return None
            
        except Exception as e:
            logger.error(f"Error placing order: {str(e)}")
            return None
            
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an existing order."""
        try:
            if not self.is_connected:
                logger.error("Not connected to Angel One")
                return False
                
            response = self.smart_api.cancelOrder(order_id, "NORMAL")
            return response['status']
        except Exception as e:
            logger.error(f"Error canceling order: {str(e)}")
            return False
    
    async def get_order_status(self, order_id: str) -> Dict:
        """Get status of an order."""
        try:
            if not self.is_connected:
                logger.error("Not connected to Angel One")
                return {}
                
            orders = self.smart_api.orderBook()['data']
            order = next((o for o in orders if o['orderid'] == order_id), None)
            
            if order:
                return {
                    'order_id': order['orderid'],
                    'status': order['orderstatus'],
                    'filled_quantity': int(order['filledshares']),
                    'remaining_quantity': int(order['unfilledshares']),
                    'average_price': float(order['averageprice'])
                }
            return {}
        except Exception as e:
            logger.error(f"Error getting order status: {str(e)}")
            return {}
    
    async def get_positions(self) -> List[Dict]:
        """Get current positions."""
        try:
            if not self.is_connected:
                logger.error("Not connected to Angel One")
                return []
                
            positions = self.smart_api.position()['data']
            return [{
                'symbol': pos['tradingsymbol'],
                'quantity': int(pos['netqty']),
                'average_price': float(pos['averageprice']),
                'current_price': float(pos['ltp']),
                'pnl': float(pos['pnl'])
            } for pos in positions]
        except Exception as e:
            logger.error(f"Error getting positions: {str(e)}")
            return []
    
    async def get_market_data(self, symbol: str, interval: str = 'ONE_MINUTE',
                            start_time: Optional[datetime] = None,
                            end_time: Optional[datetime] = None) -> List[Dict]:
        """Get historical market data."""
        try:
            if not self.is_connected:
                logger.error("Not connected to Angel One")
                return []
                
            # Convert interval to Angel One format
            interval_map = {
                'minute': 'ONE_MINUTE',
                '5minute': 'FIVE_MINUTE',
                '15minute': 'FIFTEEN_MINUTE',
                'hour': 'ONE_HOUR',
                'day': 'ONE_DAY'
            }
            
            token = self.get_token(symbol)
            
            params = {
                "exchange": "NSE",
                "symboltoken": token,
                "interval": interval_map.get(interval, 'ONE_MINUTE'),
                "fromdate": start_time.strftime("%Y-%m-%d %H:%M") if start_time else None,
                "todate": end_time.strftime("%Y-%m-%d %H:%M") if end_time else None
            }
            
            candles = self.smart_api.getCandleData(params)['data']
            
            return [{
                'timestamp': candle[0],
                'open': float(candle[1]),
                'high': float(candle[2]),
                'low': float(candle[3]),
                'close': float(candle[4]),
                'volume': float(candle[5])
            } for candle in candles]
        except Exception as e:
            logger.error(f"Error getting market data: {str(e)}")
            return []
    
    async def get_ticker(self, symbol: str) -> Dict:
        """Get current market price for a symbol."""
        try:
            if not self.is_connected:
                logger.error("Not connected to Angel One")
                return {}
                
            token = self.get_token(symbol)
            quote = self.smart_api.ltpData("NSE", symbol, token)['data']
            
            return {
                'symbol': symbol,
                'last_price': float(quote['ltp']),
                'volume': float(quote.get('volume', 0)),
                'change': float(quote.get('change', 0)),
                'exchange': quote['exchange'],
                'token': quote['token']
            }
        except Exception as e:
            logger.error(f"Error getting ticker: {str(e)}")
            return {}
    
    async def get_exchange_info(self) -> Dict:
        """Get exchange information."""
        try:
            if not self.is_connected:
                logger.error("Not connected to Angel One")
                return {}
                
            response = self.smart_api.exchangeInfo()
            return {
                'exchange_status': response['data']['exchangestatus'],
                'market_type': response['data']['markettype'],
                'exchange_timezone': response['data']['exchangetimezone']
            }
        except Exception as e:
            logger.error(f"Error getting exchange info: {str(e)}")
            return {}
    
    def format_symbol(self, symbol: str) -> str:
        """Format symbol according to Angel One requirements."""
        # Angel One uses simple symbol names
        return symbol.upper()
    
    def get_token(self, symbol: str) -> Optional[str]:
        """Get token for a symbol."""
        try:
            if not self.is_connected:
                logger.error("Not connected to Angel One")
                return None
                
            data = self.smart_api.searchScrip(symbol)
            if data and data.get('data'):
                return data['data'][0]['token']
                
            logger.error(f"Failed to get token for {symbol}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting token: {str(e)}")
            return None
    
    async def subscribe_to_market_data(self, symbols: List[str], callback) -> bool:
        """Subscribe to real-time market data."""
        try:
            if not self.is_connected:
                logger.error("Not connected to Angel One")
                return False
                
            tokens = [self.get_token(s) for s in symbols]
            
            def on_message(ws, message):
                callback(message)
            
            def on_open(ws):
                ws.subscribe(tokens)
                ws.set_mode(ws.MODE_LTP, tokens)
            
            self.smart_api.start_websocket(
                subscribe_callback=on_message,
                socket_open_callback=on_open
            )
            
            return True
        except Exception as e:
            logger.error(f"Error subscribing to market data: {str(e)}")
            return False
    
    async def unsubscribe_from_market_data(self, symbols: List[str]) -> bool:
        """Unsubscribe from real-time market data."""
        try:
            if not self.is_connected:
                logger.error("Not connected to Angel One")
                return False
                
            tokens = [self.get_token(s) for s in symbols]
            self.smart_api.ws.unsubscribe(tokens)
            return True
        except Exception as e:
            logger.error(f"Error unsubscribing from market data: {str(e)}")
            return False
            
    def login(self):
        try:
            data = self.obj.generateSession(self.client_id, self.password, self.token)
            refreshToken = data['data']['refreshToken']
            self.obj.getProfile(refreshToken)
            return True
        except Exception as e:
            logger.error(f"Angel One Login Error: {str(e)}")
            return False
