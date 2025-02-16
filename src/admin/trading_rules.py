from dataclasses import dataclass
from typing import Dict, List, Optional
from decimal import Decimal

@dataclass
class TradingRules:
    # Profit Thresholds
    min_expected_profit: float  # Minimum profit percentage to enter a trade
    target_profit: float  # Target profit percentage
    stop_loss: float  # Stop loss percentage
    
    # Risk Management
    max_trade_value: float  # Maximum value per trade
    max_trades_per_day: int  # Maximum number of trades per day
    max_loss_per_day: float  # Maximum loss allowed per day
    
    # Capital Management
    capital_per_trade: float  # Percentage of capital per trade
    reserve_capital: float  # Percentage of capital to keep as reserve
    
    # Trading Hours
    trading_start_time: str  # e.g., "09:15"
    trading_end_time: str  # e.g., "15:30"
    
    @classmethod
    def default(cls):
        return cls(
            min_expected_profit=1.0,  # 1% minimum expected profit
            target_profit=2.0,  # 2% target profit
            stop_loss=1.0,  # 1% stop loss
            
            max_trade_value=100000,  # ₹1 lakh per trade
            max_trades_per_day=5,
            max_loss_per_day=5000,  # ₹5000 max loss per day
            
            capital_per_trade=10.0,  # 10% of capital per trade
            reserve_capital=30.0,  # 30% reserve capital
            
            trading_start_time="09:15",
            trading_end_time="15:30"
        )

class TradingManager:
    def __init__(self, charge_manager, rules: Optional[TradingRules] = None):
        self.charge_manager = charge_manager
        self.rules = rules or TradingRules.default()
        self.daily_stats = {
            'trades_executed': 0,
            'total_profit': 0,
            'total_loss': 0
        }
    
    def can_execute_trade(self, 
                         trade_type: str,
                         entry_price: float,
                         quantity: int,
                         predicted_exit_price: float) -> Dict:
        """
        Check if a trade should be executed based on rules and charges
        
        Returns:
            Dictionary with:
            - can_trade: Boolean
            - reason: Explanation if can't trade
            - expected_profit: Expected profit after charges
            - charges: Breakdown of all charges
        """
        trade_value = entry_price * quantity
        
        # 1. Check trade value limit
        if trade_value > self.rules.max_trade_value:
            return {
                'can_trade': False,
                'reason': f'Trade value {trade_value} exceeds maximum {self.rules.max_trade_value}'
            }
        
        # 2. Check daily trade limit
        if self.daily_stats['trades_executed'] >= self.rules.max_trades_per_day:
            return {
                'can_trade': False,
                'reason': 'Daily trade limit reached'
            }
        
        # 3. Check daily loss limit
        if self.daily_stats['total_loss'] >= self.rules.max_loss_per_day:
            return {
                'can_trade': False,
                'reason': 'Daily loss limit reached'
            }
        
        # 4. Calculate charges
        entry_charges = self.charge_manager.calculate_charges(
            trade_type, trade_value, is_buy=True
        )
        
        exit_value = predicted_exit_price * quantity
        exit_charges = self.charge_manager.calculate_charges(
            trade_type, exit_value, is_buy=False
        )
        
        total_charges = entry_charges['total'] + exit_charges['total']
        
        # 5. Calculate expected profit
        expected_profit = exit_value - trade_value - total_charges
        profit_percentage = (expected_profit / trade_value) * 100
        
        # 6. Check minimum profit threshold
        if profit_percentage < self.rules.min_expected_profit:
            return {
                'can_trade': False,
                'reason': f'Expected profit {profit_percentage:.2f}% below minimum {self.rules.min_expected_profit}%',
                'expected_profit': expected_profit,
                'charges': {
                    'entry': entry_charges,
                    'exit': exit_charges,
                    'total': total_charges
                }
            }
        
        return {
            'can_trade': True,
            'reason': 'Trade meets all criteria',
            'expected_profit': expected_profit,
            'charges': {
                'entry': entry_charges,
                'exit': exit_charges,
                'total': total_charges
            }
        }
    
    def update_rule(self, rule_name: str, new_value: float) -> None:
        """Update a specific trading rule"""
        if hasattr(self.rules, rule_name):
            setattr(self.rules, rule_name, new_value)
        else:
            raise ValueError(f"Invalid rule name: {rule_name}")
    
    def get_trading_summary(self) -> Dict:
        """Get summary of trading rules and performance"""
        return {
            'rules': self.rules.__dict__,
            'daily_stats': self.daily_stats,
            'profit_thresholds': {
                'min_profit_needed': self.calculate_min_profit_needed(),
                'recommended_position_sizes': self.get_recommended_position_sizes()
            }
        }
    
    def calculate_min_profit_needed(self) -> Dict[str, float]:
        """Calculate minimum profit needed for each trade type"""
        trade_types = ['delivery', 'intraday', 'futures', 'options']
        min_profits = {}
        
        for trade_type in trade_types:
            # Get minimum profitable trade value
            min_trade = self.charge_manager.get_minimum_profitable_trade(trade_type)
            
            # Calculate charges for this trade
            charges = self.charge_manager.calculate_charges(trade_type, min_trade)
            
            min_profits[trade_type] = {
                'min_trade_value': min_trade,
                'min_profit_needed': charges['total'],
                'profit_percentage': (charges['total'] / min_trade) * 100
            }
        
        return min_profits
    
    def get_recommended_position_sizes(self) -> Dict[str, Dict]:
        """Get recommended position sizes for different profit targets"""
        profit_targets = [0.5, 1.0, 2.0, 3.0, 5.0]  # Percentage profits
        trade_types = ['delivery', 'intraday', 'futures', 'options']
        recommendations = {}
        
        for trade_type in trade_types:
            trade_recs = {}
            for target in profit_targets:
                # Calculate minimum trade value needed for this profit
                min_value = self.charge_manager.get_minimum_profitable_trade(trade_type)
                
                # Add buffer for target profit
                recommended_value = min_value * (1 + target/100)
                
                trade_recs[f'{target}%'] = {
                    'trade_value': recommended_value,
                    'expected_charges': self.charge_manager.calculate_charges(
                        trade_type, recommended_value
                    )['total']
                }
            
            recommendations[trade_type] = trade_recs
        
        return recommendations
