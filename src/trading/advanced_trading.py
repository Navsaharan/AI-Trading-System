from typing import Dict, List, Optional, Union
import asyncio
from datetime import datetime, timedelta
import numpy as np
from ..core.trading_engine import TradingEngine
from ..core.risk_manager import RiskManager
from ..brokers.base import BaseBroker
from ..models.order import Order
from ..utils.market_data import MarketData

class AdvancedTrading:
    """Advanced trading features including HFT and order spoofing."""
    
    def __init__(self, trading_engine: TradingEngine,
                 risk_manager: RiskManager):
        self.trading_engine = trading_engine
        self.risk_manager = risk_manager
        self.market_data = MarketData()
        self.hft_enabled = False
        self.spoofing_enabled = False
        self.max_fake_orders = 5
        self.min_cancel_delay = 0.1  # seconds
        self.max_cancel_delay = 0.5  # seconds
    
    async def enable_hft(self, capital_allocation: float,
                        max_positions: int = 5) -> bool:
        """Enable High-Frequency Trading mode."""
        try:
            # Validate capital allocation
            if not await self._validate_hft_allocation(capital_allocation):
                return False
            
            self.hft_config = {
                "capital_allocation": capital_allocation,
                "max_positions": max_positions,
                "min_profit_threshold": 0.0001,  # 0.01%
                "max_slippage": 0.0002,         # 0.02%
                "position_timeout": 10,          # seconds
                "execution_delay": 0.001         # 1ms
            }
            
            self.hft_enabled = True
            return True
        except Exception as e:
            print(f"Error enabling HFT: {str(e)}")
            return False
    
    async def disable_hft(self) -> bool:
        """Disable High-Frequency Trading mode."""
        try:
            # Close all HFT positions
            await self._close_hft_positions()
            
            self.hft_enabled = False
            return True
        except Exception as e:
            print(f"Error disabling HFT: {str(e)}")
            return False
    
    async def enable_spoofing(self, max_fake_orders: int = 5) -> bool:
        """Enable order spoofing (use with caution)."""
        try:
            if not await self._validate_spoofing_config(max_fake_orders):
                return False
            
            self.spoofing_config = {
                "max_fake_orders": max_fake_orders,
                "min_order_size": 100,
                "max_order_size": 1000,
                "price_deviation": 0.001,  # 0.1%
                "cancel_probability": 0.95
            }
            
            self.spoofing_enabled = True
            return True
        except Exception as e:
            print(f"Error enabling spoofing: {str(e)}")
            return False
    
    async def disable_spoofing(self) -> bool:
        """Disable order spoofing."""
        try:
            # Cancel all fake orders
            await self._cancel_all_fake_orders()
            
            self.spoofing_enabled = False
            return True
        except Exception as e:
            print(f"Error disabling spoofing: {str(e)}")
            return False
    
    async def execute_hft_strategy(self, symbol: str, strategy: Dict) -> Dict:
        """Execute HFT strategy on a symbol."""
        try:
            if not self.hft_enabled:
                raise ValueError("HFT mode is not enabled")
            
            # Initialize strategy metrics
            metrics = {
                "trades": [],
                "profit": 0,
                "positions": 0,
                "latency": []
            }
            
            # Start market data stream
            stream = await self.market_data.subscribe_to_market_data(
                [symbol],
                self._handle_market_data
            )
            
            # Main HFT loop
            while self.hft_enabled:
                # Check for opportunities
                opportunity = await self._find_hft_opportunity(symbol)
                if opportunity:
                    # Execute trade with minimal latency
                    start_time = datetime.now()
                    
                    trade = await self._execute_hft_trade(
                        symbol,
                        opportunity["side"],
                        opportunity["price"],
                        opportunity["size"]
                    )
                    
                    end_time = datetime.now()
                    latency = (end_time - start_time).total_seconds()
                    
                    if trade:
                        metrics["trades"].append(trade)
                        metrics["profit"] += trade["profit"]
                        metrics["latency"].append(latency)
                
                # Check position timeout
                await self._check_position_timeout()
                
                # Small delay to prevent excessive CPU usage
                await asyncio.sleep(self.hft_config["execution_delay"])
            
            # Clean up
            await stream.close()
            
            return metrics
        except Exception as e:
            print(f"Error executing HFT strategy: {str(e)}")
            return {}
    
    async def execute_spoofing_strategy(self, symbol: str,
                                      direction: str) -> Dict:
        """Execute spoofing strategy to influence market."""
        try:
            if not self.spoofing_enabled:
                raise ValueError("Spoofing is not enabled")
            
            # Get current market price
            price = await self.market_data.get_real_time_price(symbol)
            if not price:
                return {}
            
            # Generate fake orders
            fake_orders = await self._generate_fake_orders(
                symbol,
                price["price"],
                direction
            )
            
            # Place fake orders
            placed_orders = []
            for order in fake_orders:
                if await self._place_fake_order(order):
                    placed_orders.append(order)
            
            # Schedule order cancellation
            for order in placed_orders:
                await self._schedule_order_cancel(order)
            
            return {
                "symbol": symbol,
                "direction": direction,
                "fake_orders": len(placed_orders),
                "timestamp": datetime.now()
            }
        except Exception as e:
            print(f"Error executing spoofing strategy: {str(e)}")
            return {}
    
    async def _validate_hft_allocation(self, allocation: float) -> bool:
        """Validate HFT capital allocation."""
        try:
            account = await self.trading_engine.get_account_info()
            
            # Check if allocation is reasonable
            if allocation > account["balance"] * 0.5:
                return False
            
            # Check if account has enough margin
            if allocation > account["available_margin"]:
                return False
            
            return True
        except Exception:
            return False
    
    async def _validate_spoofing_config(self, max_orders: int) -> bool:
        """Validate spoofing configuration."""
        try:
            # Check if max orders is reasonable
            if max_orders > self.max_fake_orders:
                return False
            
            # Check if account has enough margin for fake orders
            account = await self.trading_engine.get_account_info()
            required_margin = max_orders * 1000  # Assuming minimum margin
            
            if required_margin > account["available_margin"]:
                return False
            
            return True
        except Exception:
            return False
    
    async def _find_hft_opportunity(self, symbol: str) -> Optional[Dict]:
        """Find HFT trading opportunity."""
        try:
            # Get order book
            book = await self.market_data.get_market_depth(symbol)
            if not book:
                return None
            
            # Look for price discrepancies
            spread = book["asks"][0]["price"] - book["bids"][0]["price"]
            
            if spread > self.hft_config["min_profit_threshold"]:
                return {
                    "side": "BUY",
                    "price": book["asks"][0]["price"],
                    "size": min(
                        book["asks"][0]["size"],
                        self.hft_config["capital_allocation"] / book["asks"][0]["price"]
                    )
                }
            
            return None
        except Exception:
            return None
    
    async def _execute_hft_trade(self, symbol: str, side: str,
                               price: float, size: float) -> Optional[Dict]:
        """Execute HFT trade with minimal latency."""
        try:
            # Place order with immediate-or-cancel flag
            order = await self.trading_engine.place_order(
                symbol=symbol,
                side=side,
                quantity=size,
                price=price,
                order_type="IOC"
            )
            
            if not order:
                return None
            
            # Wait for execution
            start_time = datetime.now()
            while datetime.now() - start_time < timedelta(seconds=1):
                status = await self.trading_engine.get_order_status(order["order_id"])
                if status["status"] in ["FILLED", "REJECTED", "CANCELED"]:
                    break
                await asyncio.sleep(0.001)
            
            if status["status"] == "FILLED":
                return {
                    "order_id": order["order_id"],
                    "symbol": symbol,
                    "side": side,
                    "price": price,
                    "size": size,
                    "profit": (status["average_price"] - price) * size \
                             if side == "BUY" else \
                             (price - status["average_price"]) * size
                }
            
            return None
        except Exception:
            return None
    
    async def _generate_fake_orders(self, symbol: str, current_price: float,
                                  direction: str) -> List[Dict]:
        """Generate fake orders to create market pressure."""
        try:
            orders = []
            
            for _ in range(self.spoofing_config["max_fake_orders"]):
                size = np.random.randint(
                    self.spoofing_config["min_order_size"],
                    self.spoofing_config["max_order_size"]
                )
                
                if direction.upper() == "UP":
                    price = current_price * (1 + np.random.random() *
                                          self.spoofing_config["price_deviation"])
                    side = "BUY"
                else:
                    price = current_price * (1 - np.random.random() *
                                          self.spoofing_config["price_deviation"])
                    side = "SELL"
                
                orders.append({
                    "symbol": symbol,
                    "side": side,
                    "price": price,
                    "size": size
                })
            
            return orders
        except Exception:
            return []
    
    async def _place_fake_order(self, order: Dict) -> bool:
        """Place a fake order."""
        try:
            placed_order = await self.trading_engine.place_order(
                symbol=order["symbol"],
                side=order["side"],
                quantity=order["size"],
                price=order["price"],
                order_type="LIMIT"
            )
            
            return bool(placed_order)
        except Exception:
            return False
    
    async def _schedule_order_cancel(self, order: Dict):
        """Schedule cancellation of fake order."""
        try:
            # Random delay before cancellation
            delay = np.random.uniform(
                self.min_cancel_delay,
                self.max_cancel_delay
            )
            
            await asyncio.sleep(delay)
            
            if np.random.random() < self.spoofing_config["cancel_probability"]:
                await self.trading_engine.cancel_order(order["order_id"])
        except Exception:
            pass
    
    async def _close_hft_positions(self):
        """Close all HFT positions."""
        try:
            positions = await self.trading_engine.get_positions()
            
            for position in positions:
                if position["strategy"] == "HFT":
                    await self.trading_engine.close_position(position["id"])
        except Exception:
            pass
    
    async def _cancel_all_fake_orders(self):
        """Cancel all pending fake orders."""
        try:
            orders = await self.trading_engine.get_open_orders()
            
            for order in orders:
                if order["strategy"] == "SPOOFING":
                    await self.trading_engine.cancel_order(order["id"])
        except Exception:
            pass
    
    async def _check_position_timeout(self):
        """Check and close timed-out HFT positions."""
        try:
            positions = await self.trading_engine.get_positions()
            
            for position in positions:
                if position["strategy"] == "HFT":
                    if (datetime.now() - position["open_time"]).total_seconds() > \
                       self.hft_config["position_timeout"]:
                        await self.trading_engine.close_position(position["id"])
        except Exception:
            pass
    
    def _handle_market_data(self, data: Dict):
        """Handle real-time market data updates."""
        try:
            # Process market data for HFT
            if self.hft_enabled:
                asyncio.create_task(
                    self._process_hft_data(data)
                )
        except Exception:
            pass
    
    async def _process_hft_data(self, data: Dict):
        """Process market data for HFT strategies."""
        try:
            if not self.hft_enabled:
                return
            
            # Look for opportunities
            if "price" in data and "symbol" in data:
                opportunity = await self._find_hft_opportunity(data["symbol"])
                if opportunity:
                    await self._execute_hft_trade(
                        data["symbol"],
                        opportunity["side"],
                        opportunity["price"],
                        opportunity["size"]
                    )
        except Exception:
            pass
