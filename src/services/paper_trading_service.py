from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import os
import aiohttp
import asyncio
from enum import Enum
import pandas as pd
import numpy as np
from .market_data_service import MarketDataService
from .trading_allocation_service import TradingMode, TradingRiskLevel

class PaperTradeStatus(Enum):
    PENDING = "pending"
    EXECUTED = "executed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

@dataclass
class PaperTrade:
    id: str
    symbol: str
    quantity: int
    price: float
    trade_type: str  # buy/sell
    order_type: str  # market/limit
    status: PaperTradeStatus
    timestamp: datetime
    execution_price: Optional[float] = None
    execution_time: Optional[datetime] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

class PaperTradingService:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.market_data = MarketDataService()
        self.paper_portfolio = self._load_portfolio()
        self.trade_history = self._load_trade_history()
        self.virtual_balance = self._load_virtual_balance()
        self.pending_orders = []
        self.active_positions = {}

    async def execute_paper_trade(self, trade_params: Dict) -> Dict:
        """Execute a paper trade"""
        try:
            # Validate trade parameters
            if not self._validate_trade_params(trade_params):
                return {
                    "status": "error",
                    "message": "Invalid trade parameters"
                }

            # Create paper trade
            trade = self._create_paper_trade(trade_params)

            # Execute trade based on type
            if trade.order_type == "market":
                result = await self._execute_market_order(trade)
            else:
                result = await self._execute_limit_order(trade)

            # Update portfolio and history
            if result["status"] == "success":
                self._update_portfolio(trade)
                self._update_trade_history(trade)
                self._save_state()

            return result

        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    async def get_paper_portfolio(self) -> Dict:
        """Get current paper trading portfolio"""
        try:
            # Update portfolio with latest market prices
            await self._update_portfolio_prices()

            return {
                "balance": self.virtual_balance,
                "positions": self.paper_portfolio,
                "total_value": self._calculate_portfolio_value(),
                "pnl": self._calculate_total_pnl()
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    async def get_trade_history(self, 
                              start_date: Optional[datetime] = None,
                              end_date: Optional[datetime] = None) -> List[Dict]:
        """Get paper trading history"""
        try:
            filtered_history = self._filter_trade_history(start_date, end_date)
            return filtered_history

        except Exception as e:
            return []

    async def replay_market(self, 
                          symbol: str,
                          start_date: datetime,
                          end_date: datetime,
                          strategy_config: Dict) -> Dict:
        """Replay market data for backtesting"""
        try:
            # Get historical data
            historical_data = await self.market_data.get_historical_data(
                symbol, start_date, end_date
            )

            # Initialize replay environment
            replay_portfolio = self._initialize_replay_portfolio(strategy_config)

            # Run strategy on historical data
            replay_results = await self._run_replay_strategy(
                historical_data, replay_portfolio, strategy_config
            )

            return {
                "status": "success",
                "results": replay_results
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    async def _execute_market_order(self, trade: PaperTrade) -> Dict:
        """Execute a market order in paper trading"""
        try:
            # Get current market price
            current_price = await self.market_data.get_live_price(trade.symbol)
            
            # Check if we have enough balance
            if trade.trade_type == "buy":
                required_amount = trade.quantity * current_price
                if required_amount > self.virtual_balance:
                    return {
                        "status": "error",
                        "message": "Insufficient virtual balance"
                    }

            # Execute trade
            trade.execution_price = current_price
            trade.execution_time = datetime.now()
            trade.status = PaperTradeStatus.EXECUTED

            # Update virtual balance
            if trade.trade_type == "buy":
                self.virtual_balance -= trade.quantity * trade.execution_price
            else:
                self.virtual_balance += trade.quantity * trade.execution_price

            return {
                "status": "success",
                "trade": trade
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    async def _execute_limit_order(self, trade: PaperTrade) -> Dict:
        """Execute a limit order in paper trading"""
        try:
            # Add to pending orders
            self.pending_orders.append(trade)

            return {
                "status": "success",
                "message": "Limit order placed",
                "trade": trade
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    async def _update_portfolio_prices(self):
        """Update portfolio with latest market prices"""
        try:
            for symbol, position in self.paper_portfolio.items():
                current_price = await self.market_data.get_live_price(symbol)
                position['current_price'] = current_price
                position['current_value'] = position['quantity'] * current_price
                position['unrealized_pnl'] = (
                    position['current_value'] - 
                    (position['quantity'] * position['average_price'])
                )

        except Exception as e:
            print(f"Error updating portfolio prices: {e}")

    def _calculate_portfolio_value(self) -> float:
        """Calculate total portfolio value"""
        try:
            portfolio_value = self.virtual_balance
            for position in self.paper_portfolio.values():
                portfolio_value += position['current_value']
            return portfolio_value

        except Exception as e:
            print(f"Error calculating portfolio value: {e}")
            return 0.0

    def _calculate_total_pnl(self) -> float:
        """Calculate total P&L"""
        try:
            total_pnl = 0.0
            for position in self.paper_portfolio.values():
                total_pnl += position['unrealized_pnl']
            return total_pnl

        except Exception as e:
            print(f"Error calculating total PNL: {e}")
            return 0.0

    def _create_paper_trade(self, params: Dict) -> PaperTrade:
        """Create a new paper trade"""
        return PaperTrade(
            id=self._generate_trade_id(),
            symbol=params['symbol'],
            quantity=params['quantity'],
            price=params['price'],
            trade_type=params['trade_type'],
            order_type=params['order_type'],
            status=PaperTradeStatus.PENDING,
            timestamp=datetime.now(),
            stop_loss=params.get('stop_loss'),
            take_profit=params.get('take_profit')
        )

    def _update_portfolio(self, trade: PaperTrade):
        """Update portfolio after trade execution"""
        symbol = trade.symbol
        if symbol not in self.paper_portfolio:
            self.paper_portfolio[symbol] = {
                'quantity': 0,
                'average_price': 0,
                'current_price': trade.execution_price,
                'current_value': 0,
                'unrealized_pnl': 0
            }

        position = self.paper_portfolio[symbol]
        
        if trade.trade_type == "buy":
            new_quantity = position['quantity'] + trade.quantity
            position['average_price'] = (
                (position['quantity'] * position['average_price'] +
                 trade.quantity * trade.execution_price) / new_quantity
            )
            position['quantity'] = new_quantity
        else:
            position['quantity'] -= trade.quantity

        if position['quantity'] == 0:
            del self.paper_portfolio[symbol]
        else:
            position['current_value'] = (
                position['quantity'] * position['current_price']
            )
            position['unrealized_pnl'] = (
                position['current_value'] - 
                (position['quantity'] * position['average_price'])
            )

    def _update_trade_history(self, trade: PaperTrade):
        """Update trade history"""
        self.trade_history.append({
            'id': trade.id,
            'symbol': trade.symbol,
            'quantity': trade.quantity,
            'price': trade.price,
            'execution_price': trade.execution_price,
            'trade_type': trade.trade_type,
            'order_type': trade.order_type,
            'timestamp': trade.timestamp,
            'execution_time': trade.execution_time,
            'status': trade.status.value
        })

    def _load_portfolio(self) -> Dict:
        """Load paper trading portfolio"""
        try:
            portfolio_path = self._get_portfolio_path()
            if os.path.exists(portfolio_path):
                with open(portfolio_path, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading portfolio: {e}")
            return {}

    def _load_trade_history(self) -> List[Dict]:
        """Load trade history"""
        try:
            history_path = self._get_history_path()
            if os.path.exists(history_path):
                with open(history_path, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Error loading trade history: {e}")
            return []

    def _load_virtual_balance(self) -> float:
        """Load virtual balance"""
        try:
            balance_path = self._get_balance_path()
            if os.path.exists(balance_path):
                with open(balance_path, 'r') as f:
                    data = json.load(f)
                    return float(data['balance'])
            return 100000.0  # Default 100k
        except Exception as e:
            print(f"Error loading virtual balance: {e}")
            return 100000.0

    def _save_state(self):
        """Save current state"""
        try:
            # Save portfolio
            portfolio_path = self._get_portfolio_path()
            os.makedirs(os.path.dirname(portfolio_path), exist_ok=True)
            with open(portfolio_path, 'w') as f:
                json.dump(self.paper_portfolio, f, indent=4)

            # Save trade history
            history_path = self._get_history_path()
            with open(history_path, 'w') as f:
                json.dump(self.trade_history, f, indent=4)

            # Save virtual balance
            balance_path = self._get_balance_path()
            with open(balance_path, 'w') as f:
                json.dump({'balance': self.virtual_balance}, f, indent=4)

        except Exception as e:
            print(f"Error saving state: {e}")

    def _get_portfolio_path(self) -> str:
        return os.path.join(os.path.dirname(__file__), 
                          '..', 'data', 
                          f'paper_portfolio_{self.user_id}.json')

    def _get_history_path(self) -> str:
        return os.path.join(os.path.dirname(__file__), 
                          '..', 'data', 
                          f'paper_history_{self.user_id}.json')

    def _get_balance_path(self) -> str:
        return os.path.join(os.path.dirname(__file__), 
                          '..', 'data', 
                          f'paper_balance_{self.user_id}.json')

    def _generate_trade_id(self) -> str:
        """Generate unique trade ID"""
        return f"PAPER_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(self.trade_history)}"

    def _validate_trade_params(self, params: Dict) -> bool:
        """Validate trade parameters"""
        required_fields = ['symbol', 'quantity', 'price', 
                         'trade_type', 'order_type']
        
        if not all(field in params for field in required_fields):
            return False

        if params['quantity'] <= 0 or params['price'] <= 0:
            return False

        if params['trade_type'] not in ['buy', 'sell']:
            return False

        if params['order_type'] not in ['market', 'limit']:
            return False

        return True

    async def _run_replay_strategy(self,
                                 historical_data: pd.DataFrame,
                                 portfolio: Dict,
                                 strategy_config: Dict) -> Dict:
        """Run strategy on historical data"""
        try:
            results = {
                'trades': [],
                'portfolio_values': [],
                'pnl': []
            }

            for index, row in historical_data.iterrows():
                # Update market data
                current_price = row['close']
                
                # Run strategy
                signals = self._generate_strategy_signals(
                    row, strategy_config
                )
                
                # Execute trades
                for signal in signals:
                    trade_result = self._execute_replay_trade(
                        signal, current_price, portfolio
                    )
                    if trade_result:
                        results['trades'].append(trade_result)
                
                # Update portfolio value
                portfolio_value = self._calculate_replay_portfolio_value(
                    portfolio, current_price
                )
                results['portfolio_values'].append(portfolio_value)
                
                # Calculate PnL
                pnl = self._calculate_replay_pnl(portfolio, current_price)
                results['pnl'].append(pnl)

            return results

        except Exception as e:
            print(f"Error running replay strategy: {e}")
            return {}
