import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime, timedelta

class RiskManager:
    def __init__(self):
        self.setup_logging()
        self.position_limits = {}
        self.risk_limits = {}
        self.margin_requirements = {}
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def set_position_limits(self, limits: Dict[str, Dict]):
        """Set position limits for different instruments"""
        self.position_limits = limits
        
    def set_risk_limits(self, limits: Dict[str, float]):
        """Set various risk limits"""
        self.risk_limits = limits
        
    def set_margin_requirements(self, requirements: Dict[str, Dict]):
        """Set margin requirements for different instruments"""
        self.margin_requirements = requirements
        
    def calculate_position_size(
        self,
        capital: float,
        risk_per_trade: float,
        stop_loss: float,
        entry_price: float,
        instrument: str
    ) -> int:
        """Calculate optimal position size based on risk parameters"""
        try:
            # Check position limits
            max_position = self.position_limits.get(instrument, {}).get('max_quantity', float('inf'))
            
            # Calculate risk-based position size
            risk_amount = capital * (risk_per_trade / 100)
            position_size = int(risk_amount / abs(entry_price - stop_loss))
            
            # Apply position limit
            position_size = min(position_size, max_position)
            
            return position_size
            
        except Exception as e:
            self.logger.error(f"Error calculating position size: {e}")
            return 0
            
    def calculate_portfolio_var(
        self,
        positions: List[Dict],
        confidence_level: float = 0.95,
        time_horizon: int = 1
    ) -> float:
        """Calculate Value at Risk for the portfolio"""
        try:
            total_var = 0
            for position in positions:
                price = position['current_price']
                quantity = position['quantity']
                volatility = position.get('volatility', 0.2)  # Default 20% if not provided
                
                position_value = price * quantity
                position_var = position_value * volatility * np.sqrt(time_horizon) * norm.ppf(confidence_level)
                total_var += position_var
                
            return total_var
            
        except Exception as e:
            self.logger.error(f"Error calculating VaR: {e}")
            return 0
            
    def calculate_portfolio_metrics(self, positions: List[Dict]) -> Dict:
        """Calculate various portfolio risk metrics"""
        try:
            total_value = sum(p['current_price'] * p['quantity'] for p in positions)
            total_pnl = sum(p.get('unrealized_pnl', 0) for p in positions)
            
            metrics = {
                'total_value': total_value,
                'total_pnl': total_pnl,
                'pnl_percentage': (total_pnl / total_value * 100) if total_value > 0 else 0,
                'var_95': self.calculate_portfolio_var(positions),
                'position_count': len(positions)
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating portfolio metrics: {e}")
            return {}
            
    def check_margin_requirements(
        self,
        order: Dict,
        available_margin: float,
        existing_positions: List[Dict]
    ) -> Tuple[bool, str]:
        """Check if order meets margin requirements"""
        try:
            instrument = order['instrument']
            quantity = order['quantity']
            price = order['price']
            
            # Get margin requirements for instrument
            margin_req = self.margin_requirements.get(instrument, {})
            margin_percentage = margin_req.get('margin_percentage', 100)
            
            # Calculate required margin
            required_margin = price * quantity * (margin_percentage / 100)
            
            # Check if sufficient margin is available
            if required_margin > available_margin:
                return False, f"Insufficient margin. Required: {required_margin}, Available: {available_margin}"
                
            return True, "Margin requirements met"
            
        except Exception as e:
            self.logger.error(f"Error checking margin requirements: {e}")
            return False, str(e)
            
    def validate_order(
        self,
        order: Dict,
        portfolio: Dict,
        market_data: Dict
    ) -> Tuple[bool, str]:
        """Validate order against risk rules"""
        try:
            instrument = order['instrument']
            quantity = order['quantity']
            price = order['price']
            order_type = order['type']
            
            # Check position limits
            current_position = sum(p['quantity'] for p in portfolio.get('positions', [])
                                if p['instrument'] == instrument)
            new_position = current_position + quantity
            
            if abs(new_position) > self.position_limits.get(instrument, {}).get('max_quantity', float('inf')):
                return False, "Position limit exceeded"
                
            # Check price limits
            last_price = market_data.get(instrument, {}).get('last_price', price)
            price_limit = self.risk_limits.get('max_price_deviation', 5)  # Default 5%
            
            if abs((price - last_price) / last_price) > price_limit / 100:
                return False, "Price deviation exceeds limit"
                
            # Check value limits
            order_value = price * quantity
            if order_value > self.risk_limits.get('max_order_value', float('inf')):
                return False, "Order value exceeds limit"
                
            return True, "Order validated successfully"
            
        except Exception as e:
            self.logger.error(f"Error validating order: {e}")
            return False, str(e)
            
    def calculate_drawdown(self, portfolio_values: List[float]) -> Dict:
        """Calculate drawdown metrics"""
        try:
            values = pd.Series(portfolio_values)
            rolling_max = values.expanding().max()
            drawdowns = (values - rolling_max) / rolling_max * 100
            
            metrics = {
                'current_drawdown': float(drawdowns.iloc[-1]),
                'max_drawdown': float(drawdowns.min()),
                'avg_drawdown': float(drawdowns.mean()),
                'drawdown_duration': int((drawdowns < 0).sum())
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating drawdown: {e}")
            return {}
            
    def generate_risk_report(
        self,
        portfolio: Dict,
        market_data: Dict,
        timeframe: str = 'daily'
    ) -> Dict:
        """Generate comprehensive risk report"""
        try:
            positions = portfolio.get('positions', [])
            portfolio_values = portfolio.get('historical_values', [])
            
            report = {
                'timestamp': datetime.now().isoformat(),
                'portfolio_metrics': self.calculate_portfolio_metrics(positions),
                'var_metrics': {
                    'var_95': self.calculate_portfolio_var(positions, confidence_level=0.95),
                    'var_99': self.calculate_portfolio_var(positions, confidence_level=0.99)
                },
                'drawdown_metrics': self.calculate_drawdown(portfolio_values),
                'position_summary': {
                    'total_positions': len(positions),
                    'long_positions': sum(1 for p in positions if p['quantity'] > 0),
                    'short_positions': sum(1 for p in positions if p['quantity'] < 0)
                },
                'risk_exposure': {
                    instrument: sum(p['current_price'] * p['quantity']
                                 for p in positions if p['instrument'] == instrument)
                    for instrument in set(p['instrument'] for p in positions)
                }
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating risk report: {e}")
            return {}
