from typing import Dict, Optional
from decimal import Decimal
from datetime import datetime, timedelta
from .profit_calculator import ProfitCalculator
from ..models.trade_history import TradeHistory
from sqlalchemy.orm import Session

class TradeExecutor:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.profit_calculator = ProfitCalculator()
        
    async def execute_trade(
        self,
        symbol: str,
        trade_type: str,
        quantity: int,
        base_price: float,
        current_price: float,
        min_profit_target: Optional[float] = None,
        allow_partial: bool = True
    ) -> Dict:
        """Execute trade with profit consideration"""
        try:
            # Calculate potential profit
            profit_analysis = self.profit_calculator.calculate_net_profit(
                base_price,
                current_price,
                quantity
            )
            
            # Check if trade is profitable
            if not profit_analysis['is_profitable']:
                # Try to find better alternatives
                alternatives = await self._find_trade_alternatives(
                    symbol,
                    base_price,
                    current_price,
                    quantity,
                    min_profit_target,
                    allow_partial
                )
                
                return {
                    'status': 'rejected',
                    'reason': 'Trade not profitable',
                    'analysis': profit_analysis,
                    'alternatives': alternatives
                }
            
            # Execute the trade
            trade_result = await self._place_trade(
                symbol,
                trade_type,
                quantity,
                current_price
            )
            
            # Record trade
            self._record_trade(
                symbol,
                trade_type,
                quantity,
                base_price,
                current_price,
                profit_analysis
            )
            
            return {
                'status': 'executed',
                'trade_id': trade_result['trade_id'],
                'execution_price': trade_result['execution_price'],
                'analysis': profit_analysis
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'reason': str(e)
            }
    
    async def _find_trade_alternatives(
        self,
        symbol: str,
        base_price: float,
        current_price: float,
        quantity: int,
        min_profit_target: Optional[float] = None,
        allow_partial: bool = True
    ) -> Dict:
        """Find alternative trade strategies"""
        alternatives = {}
        
        # 1. Calculate better price
        if min_profit_target:
            better_price = self.profit_calculator.suggest_better_price(
                base_price,
                quantity,
                min_profit_target
            )
            alternatives['better_price'] = {
                'price': better_price['suggested_price'],
                'expected_profit': better_price['expected_profit']
            }
        
        # 2. Check partial sell strategy
        if allow_partial:
            partial_strategy = self.profit_calculator.calculate_partial_sell_strategy(
                base_price,
                current_price,
                quantity,
                min_profit_target or 0
            )
            if partial_strategy['should_partial_sell']:
                alternatives['partial_sell'] = partial_strategy
        
        # 3. Get market analysis for hold recommendation
        market_analysis = await self._analyze_market_trend(symbol)
        if market_analysis['trend'] == 'upward':
            alternatives['hold_recommendation'] = {
                'action': 'hold',
                'reason': 'Upward trend detected',
                'expected_price': market_analysis['target_price'],
                'timeframe': market_analysis['timeframe']
            }
        
        return alternatives
    
    async def _analyze_market_trend(self, symbol: str) -> Dict:
        """Analyze market trend for hold recommendations"""
        # Implement market analysis logic
        return {
            'trend': 'upward',
            'target_price': 1000.0,
            'timeframe': '2 hours'
        }
    
    async def _place_trade(
        self,
        symbol: str,
        trade_type: str,
        quantity: int,
        price: float
    ) -> Dict:
        """Place actual trade order"""
        # Implement actual trade execution logic
        return {
            'trade_id': 'TRADE123',
            'execution_price': price
        }
    
    def _record_trade(
        self,
        symbol: str,
        trade_type: str,
        quantity: int,
        base_price: float,
        execution_price: float,
        profit_analysis: Dict
    ) -> None:
        """Record trade in database"""
        trade = TradeHistory(
            symbol=symbol,
            trade_type=trade_type,
            quantity=quantity,
            base_price=base_price,
            execution_price=execution_price,
            gross_profit=profit_analysis['gross_profit'],
            total_charges=profit_analysis['total_charges'],
            net_profit=profit_analysis['net_profit'],
            timestamp=datetime.utcnow()
        )
        
        self.db.add(trade)
        self.db.commit()
