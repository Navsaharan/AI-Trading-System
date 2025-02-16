from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime

class BaseBroker(ABC):
    """Abstract base class for all broker implementations."""
    
    def __init__(self, api_key: str, api_secret: str, **kwargs):
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = None
        self.is_connected = False
    
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection with broker API."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Close connection with broker API."""
        pass
    
    @abstractmethod
    async def get_account_info(self) -> Dict:
        """Get account information including balance and positions."""
        pass
    
    @abstractmethod
    async def place_order(self, symbol: str, side: str, quantity: float, 
                         order_type: str, price: Optional[float] = None) -> Dict:
        """Place a new order."""
        pass
    
    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an existing order."""
        pass
    
    @abstractmethod
    async def get_order_status(self, order_id: str) -> Dict:
        """Get status of an order."""
        pass
    
    @abstractmethod
    async def get_positions(self) -> List[Dict]:
        """Get current positions."""
        pass
    
    @abstractmethod
    async def get_market_data(self, symbol: str, interval: str = '1m',
                            start_time: Optional[datetime] = None,
                            end_time: Optional[datetime] = None) -> List[Dict]:
        """Get historical market data."""
        pass
    
    @abstractmethod
    async def get_ticker(self, symbol: str) -> Dict:
        """Get current market price for a symbol."""
        pass
    
    @abstractmethod
    async def get_exchange_info(self) -> Dict:
        """Get exchange information including trading rules."""
        pass
    
    def validate_order(self, symbol: str, side: str, quantity: float,
                      order_type: str, price: Optional[float] = None) -> bool:
        """Validate order parameters before submission."""
        if not symbol or not side or not quantity or not order_type:
            return False
        if order_type.lower() == 'limit' and price is None:
            return False
        if side.lower() not in ['buy', 'sell']:
            return False
        if quantity <= 0:
            return False
        if price is not None and price <= 0:
            return False
        return True
    
    def format_symbol(self, symbol: str) -> str:
        """Format symbol according to broker's requirements."""
        return symbol.upper()
    
    async def get_account_balance(self) -> float:
        """Get account balance."""
        account_info = await self.get_account_info()
        return float(account_info.get('balance', 0))
    
    async def calculate_buying_power(self) -> float:
        """Calculate available buying power considering margin."""
        account_info = await self.get_account_info()
        return float(account_info.get('buying_power', 0))
    
    @abstractmethod
    async def subscribe_to_market_data(self, symbols: List[str], callback) -> bool:
        """Subscribe to real-time market data."""
        pass
    
    @abstractmethod
    async def unsubscribe_from_market_data(self, symbols: List[str]) -> bool:
        """Unsubscribe from real-time market data."""
        pass
