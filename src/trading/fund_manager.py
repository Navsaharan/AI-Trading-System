from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models.fund_allocation import FundAllocation, TradeHistory, RiskModeConfig, RiskModeDescription

class FundManager:
    def __init__(self, db_session: Session):
        self.db = db_session
        
    def create_allocation(self, user_id: int, allocation_data: Dict) -> FundAllocation:
        """Create new fund allocation for user"""
        allocation = FundAllocation(
            user_id=user_id,
            total_amount=allocation_data['total_amount'],
            stocks_allocation=allocation_data.get('stocks_allocation', 0),
            fo_allocation=allocation_data.get('fo_allocation', 0),
            crypto_allocation=allocation_data.get('crypto_allocation', 0),
            forex_allocation=allocation_data.get('forex_allocation', 0),
            commodities_allocation=allocation_data.get('commodities_allocation', 0),
            risk_mode=allocation_data.get('risk_mode', 'low'),
            max_trade_size=allocation_data.get('max_trade_size', allocation_data['total_amount'] * 0.1),
            max_daily_trades=allocation_data.get('max_daily_trades', 5)
        )
        
        self.db.add(allocation)
        self.db.commit()
        return allocation
    
    def update_allocation(self, allocation_id: int, update_data: Dict) -> FundAllocation:
        """Update existing fund allocation"""
        allocation = self.db.query(FundAllocation).filter(FundAllocation.id == allocation_id).first()
        if not allocation:
            raise ValueError("Fund allocation not found")
            
        for key, value in update_data.items():
            if hasattr(allocation, key):
                setattr(allocation, key, value)
                
        self.db.commit()
        return allocation
    
    def get_allocation(self, user_id: int) -> Optional[FundAllocation]:
        """Get user's fund allocation"""
        return self.db.query(FundAllocation).filter(FundAllocation.user_id == user_id).first()
    
    def validate_trade(self, allocation_id: int, category: str, amount: float) -> bool:
        """Validate if trade is allowed based on allocation rules"""
        allocation = self.db.query(FundAllocation).filter(FundAllocation.id == allocation_id).first()
        if not allocation:
            return False
            
        # Check category allocation
        category_allocation = getattr(allocation, f"{category}_allocation")
        if amount > category_allocation:
            return False
            
        # Check max trade size
        if amount > allocation.max_trade_size:
            return False
            
        # Check daily trade limit
        today_trades = self.db.query(TradeHistory).filter(
            TradeHistory.fund_allocation_id == allocation_id,
            TradeHistory.timestamp >= datetime.utcnow().date()
        ).count()
        
        if today_trades >= allocation.max_daily_trades:
            return False
            
        return True
    
    def record_trade(self, allocation_id: int, trade_data: Dict) -> TradeHistory:
        """Record a new trade"""
        trade = TradeHistory(
            fund_allocation_id=allocation_id,
            category=trade_data['category'],
            trade_amount=trade_data['amount'],
            trade_type=trade_data['type'],
            profit_loss=trade_data.get('profit_loss', 0)
        )
        
        self.db.add(trade)
        self.db.commit()
        return trade
    
    def get_performance_metrics(self, allocation_id: int) -> Dict:
        """Get performance metrics for fund allocation"""
        allocation = self.db.query(FundAllocation).filter(FundAllocation.id == allocation_id).first()
        trades = self.db.query(TradeHistory).filter(TradeHistory.fund_allocation_id == allocation_id).all()
        
        total_profit = sum(trade.profit_loss for trade in trades)
        category_profits = {}
        for category in ['stocks', 'fo', 'crypto', 'forex', 'commodities']:
            category_trades = [t for t in trades if t.category == category]
            category_profits[category] = sum(t.profit_loss for t in category_trades)
            
        return {
            'total_profit': total_profit,
            'category_profits': category_profits,
            'total_trades': len(trades),
            'win_rate': len([t for t in trades if t.profit_loss > 0]) / len(trades) if trades else 0
        }
    
    def check_risk_management(self, allocation_id: int) -> Dict:
        """Check risk management status and get recommendations"""
        allocation = self.db.query(FundAllocation).filter(FundAllocation.id == allocation_id).first()
        recent_trades = self.db.query(TradeHistory).filter(
            TradeHistory.fund_allocation_id == allocation_id,
            TradeHistory.timestamp >= datetime.utcnow() - timedelta(days=7)
        ).all()
        
        recent_profit = sum(trade.profit_loss for trade in recent_trades)
        consecutive_losses = self._get_consecutive_losses(recent_trades)
        
        risk_status = "normal"
        recommendations = []
        
        if consecutive_losses >= 3:
            risk_status = "high"
            recommendations.append("Reduce trade size by 50%")
            recommendations.append("Switch to low-risk mode")
        elif recent_profit < -0.1 * allocation.total_amount:
            risk_status = "medium"
            recommendations.append("Reduce trade size by 25%")
            recommendations.append("Focus on less volatile assets")
            
        return {
            'risk_status': risk_status,
            'consecutive_losses': consecutive_losses,
            'weekly_profit': recent_profit,
            'recommendations': recommendations
        }
    
    def _get_consecutive_losses(self, trades: List[TradeHistory]) -> int:
        """Calculate maximum consecutive losses"""
        max_consecutive = current_consecutive = 0
        for trade in sorted(trades, key=lambda x: x.timestamp):
            if trade.profit_loss < 0:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
        return max_consecutive

    def create_risk_mode_config(self, allocation_id: int, config_data: Dict) -> RiskModeConfig:
        """Create risk mode configuration"""
        config = RiskModeConfig(
            fund_allocation_id=allocation_id,
            risk_level=config_data['risk_level'],
            allocated_amount=config_data['allocated_amount'],
            max_trade_size=config_data['max_trade_size'],
            max_daily_trades=config_data['max_daily_trades'],
            stop_loss_percentage=config_data.get('stop_loss_percentage', 5.0)
        )
        
        self.db.add(config)
        self.db.commit()
        return config
    
    def update_risk_mode_config(self, config_id: int, update_data: Dict) -> RiskModeConfig:
        """Update risk mode configuration"""
        config = self.db.query(RiskModeConfig).filter(RiskModeConfig.id == config_id).first()
        if not config:
            raise ValueError("Risk mode config not found")
            
        for key, value in update_data.items():
            if hasattr(config, key):
                setattr(config, key, value)
                
        self.db.commit()
        return config
    
    def get_risk_mode_configs(self, allocation_id: int) -> List[RiskModeConfig]:
        """Get all risk mode configs for an allocation"""
        return self.db.query(RiskModeConfig).filter(RiskModeConfig.fund_allocation_id == allocation_id).all()
    
    def get_risk_mode_description(self, risk_level: str) -> Dict:
        """Get description and details for a risk mode"""
        desc = self.db.query(RiskModeDescription).filter(RiskModeDescription.risk_level == risk_level).first()
        if not desc:
            return {}
            
        return {
            'description': desc.description,
            'recommended_assets': desc.recommended_assets,
            'typical_returns': desc.typical_returns,
            'risk_factors': desc.risk_factors
        }
    
    def auto_adjust_risk_levels(self, allocation_id: int) -> Dict:
        """Auto-adjust risk levels based on performance"""
        allocation = self.db.query(FundAllocation).filter(FundAllocation.id == allocation_id).first()
        if not allocation or not allocation.auto_adjust_enabled:
            return {}
            
        risk_configs = self.get_risk_mode_configs(allocation_id)
        performance = self.get_performance_metrics(allocation_id)
        risk_status = self.check_risk_management(allocation_id)
        
        adjustments = {}
        for config in risk_configs:
            # Calculate adjustment based on performance and risk
            adjustment = self._calculate_risk_adjustment(
                config,
                performance['category_profits'],
                risk_status
            )
            
            if adjustment['should_adjust']:
                self.update_risk_mode_config(config.id, {
                    'allocated_amount': adjustment['new_amount'],
                    'max_trade_size': adjustment['new_trade_size']
                })
                adjustments[config.risk_level] = adjustment
                
        return adjustments
    
    def _calculate_risk_adjustment(self, config: RiskModeConfig, profits: Dict, risk_status: Dict) -> Dict:
        """Calculate risk level adjustments"""
        # Base adjustment on recent performance
        profit_percentage = profits.get(config.risk_level, 0) / config.allocated_amount
        consecutive_losses = risk_status.get('consecutive_losses', 0)
        
        adjustment = {
            'should_adjust': False,
            'new_amount': config.allocated_amount,
            'new_trade_size': config.max_trade_size
        }
        
        # Adjust based on risk level and performance
        if config.risk_level == 'high':
            if consecutive_losses >= 3 or profit_percentage < -0.1:
                # Reduce high risk allocation
                adjustment['should_adjust'] = True
                adjustment['new_amount'] = config.allocated_amount * 0.7
                adjustment['new_trade_size'] = config.max_trade_size * 0.5
                
        elif config.risk_level == 'medium':
            if consecutive_losses >= 4 or profit_percentage < -0.15:
                # Reduce medium risk allocation
                adjustment['should_adjust'] = True
                adjustment['new_amount'] = config.allocated_amount * 0.8
                adjustment['new_trade_size'] = config.max_trade_size * 0.7
                
        elif config.risk_level == 'low':
            if profit_percentage > 0.1 and consecutive_losses == 0:
                # Increase low risk allocation
                adjustment['should_adjust'] = True
                adjustment['new_amount'] = config.allocated_amount * 1.2
                adjustment['new_trade_size'] = config.max_trade_size * 1.1
                
        return adjustment
