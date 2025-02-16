from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from datetime import datetime
from ..models.position import Position
from ..models.trade import Trade
from ..utils.market_data import MarketData

class RiskManager:
    """AI-powered risk management system."""
    
    def __init__(self):
        self.market_data = MarketData()
    
    async def validate_trade(self, trade: Dict, account: Dict,
                           risk_params: Dict) -> Tuple[bool, str]:
        """Validate if a trade meets risk management criteria."""
        try:
            # Check account risk limits
            if not await self._check_account_risk(trade, account, risk_params):
                return False, "Account risk limits exceeded"
            
            # Check position size limits
            if not await self._check_position_size(trade, account, risk_params):
                return False, "Position size exceeds limits"
            
            # Check daily loss limits
            if not await self._check_daily_loss_limit(account, risk_params):
                return False, "Daily loss limit reached"
            
            # Calculate potential profit after fees
            net_profit = await self._calculate_net_profit(trade)
            if net_profit <= 0:
                return False, "Trade not profitable after fees and taxes"
            
            return True, "Trade validated successfully"
        except Exception as e:
            return False, f"Error validating trade: {str(e)}"
    
    async def calculate_position_size(self, symbol: str, account: Dict,
                                    risk_params: Dict) -> float:
        """Calculate optimal position size based on risk parameters."""
        try:
            # Get current market volatility
            volatility = await self._get_market_volatility(symbol)
            
            # Calculate base position size
            account_value = float(account["balance"])
            risk_per_trade = account_value * risk_params["risk_per_trade"]
            
            # Adjust for volatility
            adjusted_risk = risk_per_trade * (1 - volatility)
            
            # Apply position limits
            max_position = account_value * risk_params["max_position_size"]
            position_size = min(adjusted_risk, max_position)
            
            return position_size
        except Exception as e:
            print(f"Error calculating position size: {str(e)}")
            return 0
    
    async def get_stop_loss(self, symbol: str, side: str, entry_price: float,
                           risk_params: Dict) -> float:
        """Calculate optimal stop-loss price."""
        try:
            # Get market volatility
            volatility = await self._get_market_volatility(symbol)
            
            # Calculate base stop distance
            base_stop = entry_price * risk_params["stop_loss"]
            
            # Adjust for volatility
            adjusted_stop = base_stop * (1 + volatility)
            
            # Calculate stop price based on side
            if side.upper() == "BUY":
                stop_price = entry_price - adjusted_stop
            else:
                stop_price = entry_price + adjusted_stop
            
            return stop_price
        except Exception as e:
            print(f"Error calculating stop loss: {str(e)}")
            return entry_price
    
    async def get_take_profit(self, symbol: str, side: str, entry_price: float,
                            risk_params: Dict) -> float:
        """Calculate optimal take-profit price."""
        try:
            # Get market volatility
            volatility = await self._get_market_volatility(symbol)
            
            # Calculate base take profit distance
            base_tp = entry_price * risk_params["take_profit"]
            
            # Adjust for volatility
            adjusted_tp = base_tp * (1 + volatility)
            
            # Calculate take profit price based on side
            if side.upper() == "BUY":
                tp_price = entry_price + adjusted_tp
            else:
                tp_price = entry_price - adjusted_tp
            
            return tp_price
        except Exception as e:
            print(f"Error calculating take profit: {str(e)}")
            return entry_price
    
    async def update_trailing_stop(self, position: Position,
                                 current_price: float) -> Optional[float]:
        """Update trailing stop price based on current market price."""
        try:
            if not position.use_trailing_stop:
                return None
            
            # Calculate new stop price
            if position.side.upper() == "BUY":
                new_stop = current_price * (1 - position.trailing_stop_distance)
                if new_stop > position.stop_loss:
                    return new_stop
            else:
                new_stop = current_price * (1 + position.trailing_stop_distance)
                if new_stop < position.stop_loss:
                    return new_stop
            
            return None
        except Exception as e:
            print(f"Error updating trailing stop: {str(e)}")
            return None
    
    async def _check_account_risk(self, trade: Dict, account: Dict,
                                risk_params: Dict) -> bool:
        """Check if trade meets account-wide risk limits."""
        try:
            # Calculate total risk exposure
            current_exposure = sum(
                p.size * p.entry_price
                for p in account.get("positions", [])
            )
            
            new_exposure = current_exposure + (trade["size"] * trade["price"])
            max_exposure = float(account["balance"]) * risk_params["max_exposure"]
            
            return new_exposure <= max_exposure
        except Exception:
            return False
    
    async def _check_position_size(self, trade: Dict, account: Dict,
                                 risk_params: Dict) -> bool:
        """Check if position size meets risk criteria."""
        try:
            # Calculate position value
            position_value = trade["size"] * trade["price"]
            account_value = float(account["balance"])
            
            # Check against maximum position size
            max_position = account_value * risk_params["max_position_size"]
            
            return position_value <= max_position
        except Exception:
            return False
    
    async def _check_daily_loss_limit(self, account: Dict,
                                    risk_params: Dict) -> bool:
        """Check if daily loss limit has been reached."""
        try:
            # Calculate today's P&L
            today = datetime.now().date()
            daily_pnl = sum(
                t.pnl for t in account.get("trades", [])
                if t.close_time.date() == today
            )
            
            # Check against daily loss limit
            daily_limit = float(account["balance"]) * risk_params["daily_loss_limit"]
            
            return daily_pnl > -daily_limit
        except Exception:
            return False
    
    async def _calculate_net_profit(self, trade: Dict) -> float:
        """Calculate potential net profit after fees and taxes."""
        try:
            # Calculate gross profit
            entry_value = trade["size"] * trade["price"]
            exit_value = trade["size"] * trade["take_profit"]
            gross_profit = exit_value - entry_value if trade["side"].upper() == "BUY" \
                         else entry_value - exit_value
            
            # Calculate fees
            brokerage = entry_value * 0.0003  # 0.03% brokerage
            stt = exit_value * 0.001  # 0.1% Securities Transaction Tax
            exchange_charges = (entry_value + exit_value) * 0.0001  # 0.01% exchange charges
            gst = (brokerage + exchange_charges) * 0.18  # 18% GST
            
            # Calculate net profit
            total_charges = brokerage + stt + exchange_charges + gst
            net_profit = gross_profit - total_charges
            
            return net_profit
        except Exception:
            return 0
    
    async def _get_market_volatility(self, symbol: str) -> float:
        """Calculate current market volatility."""
        try:
            # Get recent price data
            prices = await self.market_data.get_historical_data(
                symbol, interval="5min", limit=20
            )
            
            if not prices:
                return 0
            
            # Calculate volatility (standard deviation of returns)
            returns = np.diff(np.log(prices))
            volatility = np.std(returns)
            
            return volatility
        except Exception:
            return 0
    
    async def analyze_market_conditions(self, symbol: str) -> Dict:
        """Analyze current market conditions for risk assessment."""
        try:
            # Get market data
            data = await self.market_data.get_historical_data(
                symbol, interval="1day", limit=30
            )
            
            if not data:
                return {}
            
            # Calculate market metrics
            volatility = np.std(np.diff(np.log(data)))
            trend = np.mean(np.diff(data))
            volume = np.mean(data["volume"]) if "volume" in data else 0
            
            return {
                "volatility": volatility,
                "trend": "uptrend" if trend > 0 else "downtrend",
                "volume": volume,
                "risk_level": "high" if volatility > 0.02 else "medium" \
                            if volatility > 0.01 else "low"
            }
        except Exception as e:
            print(f"Error analyzing market conditions: {str(e)}")
            return {}
