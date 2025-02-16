from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
import pandas as pd
from ..admin.charge_manager import ChargeManager
from ..data.market_data import MarketDataManager

class PaperTradingAccount:
    def __init__(self, user_id: str, initial_balance: float = 100000):
        self.user_id = user_id
        self.initial_balance = Decimal(str(initial_balance))
        self.current_balance = self.initial_balance
        self.positions: Dict[str, Dict] = {}  # Current positions
        self.orders: List[Dict] = []  # Order history
        self.trades: List[Dict] = []  # Trade history
        
        self.charge_manager = ChargeManager()
        self.market_data = MarketDataManager()
        
    def place_order(self, 
                   symbol: str, 
                   order_type: str,
                   transaction_type: str,  # BUY/SELL
                   quantity: int,
                   price: Optional[float] = None,
                   stop_loss: Optional[float] = None,
                   target: Optional[float] = None) -> Dict:
        """Place a paper trading order"""
        
        # Get current market price if not provided
        if not price:
            price = self.market_data.get_last_price(symbol)
        
        order_value = Decimal(str(price)) * Decimal(str(quantity))
        
        # Check if enough balance for buy order
        if transaction_type == "BUY":
            if order_value > self.current_balance:
                return {
                    "status": "rejected",
                    "reason": "Insufficient balance",
                    "required": float(order_value),
                    "available": float(self.current_balance)
                }
        
        # Calculate charges
        charges = self.charge_manager.calculate_charges(
            "intraday" if order_type == "INTRADAY" else "delivery",
            float(order_value),
            is_buy=(transaction_type == "BUY")
        )
        
        order = {
            "order_id": f"PT{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "user_id": self.user_id,
            "symbol": symbol,
            "order_type": order_type,
            "transaction_type": transaction_type,
            "quantity": quantity,
            "price": float(price),
            "order_value": float(order_value),
            "charges": charges,
            "status": "OPEN",
            "stop_loss": stop_loss,
            "target": target,
            "timestamp": datetime.now(),
            "average_price": None,
            "filled_quantity": 0
        }
        
        self.orders.append(order)
        
        # Execute market orders immediately
        if order_type == "MARKET":
            self._execute_order(order)
        
        return {
            "status": "success",
            "order_id": order["order_id"],
            "message": "Order placed successfully"
        }
    
    def _execute_order(self, order: Dict) -> None:
        """Execute a paper trade order"""
        symbol = order["symbol"]
        quantity = order["quantity"]
        price = order["price"]
        transaction_type = order["transaction_type"]
        
        # Update position
        if symbol not in self.positions:
            self.positions[symbol] = {
                "quantity": 0,
                "average_price": 0,
                "trades": []
            }
        
        position = self.positions[symbol]
        
        if transaction_type == "BUY":
            # Update average price
            total_value = (position["quantity"] * position["average_price"]) + (quantity * price)
            new_quantity = position["quantity"] + quantity
            position["average_price"] = total_value / new_quantity if new_quantity > 0 else 0
            position["quantity"] = new_quantity
            
            # Deduct from balance
            total_cost = Decimal(str(price * quantity)) + Decimal(str(order["charges"]["total"]))
            self.current_balance -= total_cost
            
        else:  # SELL
            # Calculate P&L
            buy_value = position["average_price"] * quantity
            sell_value = price * quantity
            profit_loss = sell_value - buy_value - order["charges"]["total"]
            
            # Update position
            position["quantity"] -= quantity
            if position["quantity"] == 0:
                position["average_price"] = 0
            
            # Add to balance
            self.current_balance += Decimal(str(sell_value)) - Decimal(str(order["charges"]["total"]))
        
        # Record trade
        trade = {
            "trade_id": f"T{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "order_id": order["order_id"],
            "symbol": symbol,
            "transaction_type": transaction_type,
            "quantity": quantity,
            "price": price,
            "charges": order["charges"],
            "timestamp": datetime.now()
        }
        
        if transaction_type == "SELL":
            trade["profit_loss"] = float(profit_loss)
        
        self.trades.append(trade)
        position["trades"].append(trade)
        
        # Update order status
        order["status"] = "COMPLETED"
        order["average_price"] = price
        order["filled_quantity"] = quantity
    
    def modify_order(self, order_id: str, modifications: Dict) -> Dict:
        """Modify an existing paper trading order"""
        order = next((o for o in self.orders if o["order_id"] == order_id), None)
        if not order:
            return {"status": "error", "message": "Order not found"}
        
        if order["status"] != "OPEN":
            return {"status": "error", "message": "Can only modify open orders"}
        
        # Update allowed fields
        allowed_modifications = ["price", "quantity", "stop_loss", "target"]
        for field in allowed_modifications:
            if field in modifications:
                order[field] = modifications[field]
        
        return {"status": "success", "message": "Order modified successfully"}
    
    def cancel_order(self, order_id: str) -> Dict:
        """Cancel an open paper trading order"""
        order = next((o for o in self.orders if o["order_id"] == order_id), None)
        if not order:
            return {"status": "error", "message": "Order not found"}
        
        if order["status"] != "OPEN":
            return {"status": "error", "message": "Can only cancel open orders"}
        
        order["status"] = "CANCELLED"
        return {"status": "success", "message": "Order cancelled successfully"}
    
    def get_positions(self) -> Dict[str, Dict]:
        """Get current positions with P&L calculations"""
        positions_with_pl = {}
        for symbol, position in self.positions.items():
            if position["quantity"] > 0:
                current_price = self.market_data.get_last_price(symbol)
                market_value = position["quantity"] * current_price
                cost_value = position["quantity"] * position["average_price"]
                unrealized_pl = market_value - cost_value
                
                positions_with_pl[symbol] = {
                    **position,
                    "current_price": current_price,
                    "market_value": market_value,
                    "cost_value": cost_value,
                    "unrealized_pl": unrealized_pl,
                    "pl_percentage": (unrealized_pl / cost_value) * 100 if cost_value > 0 else 0
                }
        
        return positions_with_pl
    
    def get_account_summary(self) -> Dict:
        """Get paper trading account summary"""
        positions = self.get_positions()
        total_investment = sum(p["cost_value"] for p in positions.values())
        total_market_value = sum(p["market_value"] for p in positions.values())
        unrealized_pl = sum(p["unrealized_pl"] for p in positions.values())
        realized_pl = sum(t.get("profit_loss", 0) for t in self.trades)
        
        return {
            "initial_balance": float(self.initial_balance),
            "current_balance": float(self.current_balance),
            "total_investment": float(total_investment),
            "total_market_value": float(total_market_value),
            "unrealized_pl": float(unrealized_pl),
            "realized_pl": float(realized_pl),
            "total_pl": float(unrealized_pl + realized_pl),
            "number_of_trades": len(self.trades),
            "open_positions": len([p for p in positions.values() if p["quantity"] > 0])
        }
    
    def get_trade_history(self, 
                         symbol: Optional[str] = None,
                         start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None) -> List[Dict]:
        """Get filtered trade history"""
        trades = self.trades
        
        if symbol:
            trades = [t for t in trades if t["symbol"] == symbol]
        
        if start_date:
            trades = [t for t in trades if t["timestamp"] >= start_date]
        
        if end_date:
            trades = [t for t in trades if t["timestamp"] <= end_date]
        
        return trades

    def get_performance_metrics(self) -> Dict:
        """Calculate trading performance metrics"""
        trades = self.trades
        if not trades:
            return {}
        
        profitable_trades = [t for t in trades if t.get("profit_loss", 0) > 0]
        loss_trades = [t for t in trades if t.get("profit_loss", 0) < 0]
        
        total_pl = sum(t.get("profit_loss", 0) for t in trades)
        win_rate = len(profitable_trades) / len(trades) * 100 if trades else 0
        
        avg_profit = sum(t["profit_loss"] for t in profitable_trades) / len(profitable_trades) if profitable_trades else 0
        avg_loss = sum(t["profit_loss"] for t in loss_trades) / len(loss_trades) if loss_trades else 0
        
        return {
            "total_trades": len(trades),
            "profitable_trades": len(profitable_trades),
            "loss_trades": len(loss_trades),
            "win_rate": win_rate,
            "average_profit": float(avg_profit),
            "average_loss": float(avg_loss),
            "profit_factor": abs(avg_profit / avg_loss) if avg_loss != 0 else 0,
            "total_pl": float(total_pl),
            "largest_profit": float(max((t.get("profit_loss", 0) for t in trades), default=0)),
            "largest_loss": float(min((t.get("profit_loss", 0) for t in trades), default=0))
        }
