from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime, time
import pytz
import logging
from .indian_broker_service import IndianBrokerService

class IndianTradingFeatures:
    def __init__(self, broker_service: IndianBrokerService):
        self.broker_service = broker_service
        self.ist_timezone = pytz.timezone('Asia/Kolkata')
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging for trading features"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def is_market_open(self) -> bool:
        """Check if Indian market is open"""
        current_time = datetime.now(self.ist_timezone).time()
        
        # NSE/BSE market hours (9:15 AM to 3:30 PM IST)
        market_open = time(9, 15)
        market_close = time(15, 30)
        
        # Check if current time is within market hours
        return market_open <= current_time <= market_close

    async def get_nifty_data(self) -> Dict:
        """Get Nifty 50 index data"""
        try:
            nifty_data = await self.broker_service.get_market_data("^NSEI")
            return {
                "index": "NIFTY 50",
                "last_price": nifty_data["last_price"],
                "change": nifty_data["change"],
                "change_percent": nifty_data["change_percent"]
            }
        except Exception as e:
            self.logger.error(f"Error fetching Nifty data: {e}")
            return {}

    async def get_bank_nifty_data(self) -> Dict:
        """Get Bank Nifty index data"""
        try:
            banknifty_data = await self.broker_service.get_market_data("^NSEBANK")
            return {
                "index": "BANK NIFTY",
                "last_price": banknifty_data["last_price"],
                "change": banknifty_data["change"],
                "change_percent": banknifty_data["change_percent"]
            }
        except Exception as e:
            self.logger.error(f"Error fetching Bank Nifty data: {e}")
            return {}

    async def get_option_chain(self, symbol: str, expiry: str) -> Dict:
        """Get option chain for a symbol"""
        try:
            return await self.broker_service.get_option_chain(symbol, expiry)
        except Exception as e:
            self.logger.error(f"Error fetching option chain: {e}")
            return {}

    async def place_bracket_order(
        self,
        broker: str,
        symbol: str,
        quantity: int,
        order_type: str,
        price: float,
        target: float,
        stoploss: float
    ) -> Dict:
        """Place bracket order"""
        try:
            return await self.broker_service.place_bracket_order(
                broker=broker,
                symbol=symbol,
                quantity=quantity,
                order_type=order_type,
                price=price,
                target=target,
                stoploss=stoploss
            )
        except Exception as e:
            self.logger.error(f"Error placing bracket order: {e}")
            return {"status": "error", "message": str(e)}

    async def place_cover_order(
        self,
        broker: str,
        symbol: str,
        quantity: int,
        order_type: str,
        price: float,
        stoploss: float
    ) -> Dict:
        """Place cover order"""
        try:
            return await self.broker_service.place_cover_order(
                broker=broker,
                symbol=symbol,
                quantity=quantity,
                order_type=order_type,
                price=price,
                stoploss=stoploss
            )
        except Exception as e:
            self.logger.error(f"Error placing cover order: {e}")
            return {"status": "error", "message": str(e)}

    async def get_margin_required(
        self,
        broker: str,
        symbol: str,
        quantity: int,
        order_type: str
    ) -> float:
        """Calculate margin required for trade"""
        try:
            return await self.broker_service.get_margin_required(
                broker=broker,
                symbol=symbol,
                quantity=quantity,
                order_type=order_type
            )
        except Exception as e:
            self.logger.error(f"Error calculating margin: {e}")
            return 0.0

    def calculate_position_size(
        self,
        capital: float,
        risk_per_trade: float,
        stoploss_points: float
    ) -> int:
        """Calculate position size based on risk management"""
        try:
            risk_amount = capital * (risk_per_trade / 100)
            position_size = int(risk_amount / stoploss_points)
            return position_size
        except Exception as e:
            self.logger.error(f"Error calculating position size: {e}")
            return 0

    async def get_delivery_positions(self, broker: str) -> List[Dict]:
        """Get delivery positions"""
        try:
            return await self.broker_service.get_holdings(broker)
        except Exception as e:
            self.logger.error(f"Error fetching delivery positions: {e}")
            return []

    async def get_intraday_positions(self, broker: str) -> List[Dict]:
        """Get intraday positions"""
        try:
            return await self.broker_service.get_positions(broker)
        except Exception as e:
            self.logger.error(f"Error fetching intraday positions: {e}")
            return []

    async def get_order_history(
        self,
        broker: str,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None
    ) -> List[Dict]:
        """Get order history"""
        try:
            return await self.broker_service.get_order_history(
                broker=broker,
                from_date=from_date,
                to_date=to_date
            )
        except Exception as e:
            self.logger.error(f"Error fetching order history: {e}")
            return []

    async def get_fund_limits(self, broker: str) -> Dict:
        """Get fund limits and margins"""
        try:
            return await self.broker_service.get_fund_limits(broker)
        except Exception as e:
            self.logger.error(f"Error fetching fund limits: {e}")
            return {}

    def calculate_intraday_indicators(self, ohlcv_data: pd.DataFrame) -> Dict:
        """Calculate intraday technical indicators"""
        try:
            # Calculate basic indicators
            ohlcv_data['SMA_20'] = ohlcv_data['close'].rolling(window=20).mean()
            ohlcv_data['EMA_20'] = ohlcv_data['close'].ewm(span=20).mean()
            
            # RSI
            delta = ohlcv_data['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            ohlcv_data['RSI'] = 100 - (100 / (1 + rs))
            
            # MACD
            exp1 = ohlcv_data['close'].ewm(span=12, adjust=False).mean()
            exp2 = ohlcv_data['close'].ewm(span=26, adjust=False).mean()
            ohlcv_data['MACD'] = exp1 - exp2
            ohlcv_data['Signal_Line'] = ohlcv_data['MACD'].ewm(span=9, adjust=False).mean()
            
            # Bollinger Bands
            std = ohlcv_data['close'].rolling(window=20).std()
            ohlcv_data['BB_Upper'] = ohlcv_data['SMA_20'] + (std * 2)
            ohlcv_data['BB_Lower'] = ohlcv_data['SMA_20'] - (std * 2)
            
            return ohlcv_data.tail(1).to_dict('records')[0]
            
        except Exception as e:
            self.logger.error(f"Error calculating indicators: {e}")
            return {}

    def get_market_depth(self, symbol: str) -> Dict:
        """Get market depth (Level 2 data)"""
        try:
            return self.broker_service.get_market_depth(symbol)
        except Exception as e:
            self.logger.error(f"Error fetching market depth: {e}")
            return {}

    async def place_gtt_order(
        self,
        broker: str,
        symbol: str,
        trigger_price: float,
        order_type: str,
        quantity: int,
        price: Optional[float] = None
    ) -> Dict:
        """Place Good Till Triggered (GTT) order"""
        try:
            return await self.broker_service.place_gtt_order(
                broker=broker,
                symbol=symbol,
                trigger_price=trigger_price,
                order_type=order_type,
                quantity=quantity,
                price=price
            )
        except Exception as e:
            self.logger.error(f"Error placing GTT order: {e}")
            return {"status": "error", "message": str(e)}

    def get_option_greeks(
        self,
        symbol: str,
        strike_price: float,
        expiry: str,
        option_type: str,
        spot_price: float,
        interest_rate: float = 0.1,
        volatility: Optional[float] = None
    ) -> Dict:
        """Calculate option Greeks"""
        try:
            # If volatility not provided, calculate historical volatility
            if volatility is None:
                historical_data = self.broker_service.get_historical_data(
                    symbol, "1d", days=30
                )
                returns = np.log(historical_data['close'] / historical_data['close'].shift(1))
                volatility = returns.std() * np.sqrt(252)
            
            # Calculate time to expiry in years
            expiry_date = datetime.strptime(expiry, '%Y-%m-%d')
            days_to_expiry = (expiry_date - datetime.now()).days
            time_to_expiry = days_to_expiry / 365
            
            # Calculate option Greeks using Black-Scholes model
            # This is a simplified version, you might want to use a proper options library
            # like QuantLib for more accurate calculations
            d1 = (np.log(spot_price / strike_price) + (interest_rate + volatility**2/2) * time_to_expiry) / (volatility * np.sqrt(time_to_expiry))
            d2 = d1 - volatility * np.sqrt(time_to_expiry)
            
            if option_type.upper() == 'CE':
                delta = norm.cdf(d1)
                gamma = norm.pdf(d1) / (spot_price * volatility * np.sqrt(time_to_expiry))
                theta = (-spot_price * norm.pdf(d1) * volatility / (2 * np.sqrt(time_to_expiry)) - 
                        interest_rate * strike_price * np.exp(-interest_rate * time_to_expiry) * norm.cdf(d2))
                vega = spot_price * np.sqrt(time_to_expiry) * norm.pdf(d1)
            else:  # PE
                delta = -norm.cdf(-d1)
                gamma = norm.pdf(d1) / (spot_price * volatility * np.sqrt(time_to_expiry))
                theta = (-spot_price * norm.pdf(d1) * volatility / (2 * np.sqrt(time_to_expiry)) + 
                        interest_rate * strike_price * np.exp(-interest_rate * time_to_expiry) * norm.cdf(-d2))
                vega = spot_price * np.sqrt(time_to_expiry) * norm.pdf(d1)
            
            return {
                "delta": delta,
                "gamma": gamma,
                "theta": theta,
                "vega": vega,
                "implied_volatility": volatility
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating option Greeks: {e}")
            return {}
