from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..config.database import Base

class FundAllocation(Base):
    __tablename__ = 'fund_allocations'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    total_amount = Column(Float, nullable=False)
    stocks_allocation = Column(Float, default=0)
    fo_allocation = Column(Float, default=0)
    crypto_allocation = Column(Float, default=0)
    forex_allocation = Column(Float, default=0)
    commodities_allocation = Column(Float, default=0)
    risk_mode = Column(Enum('low', 'medium', 'high', name='risk_modes'), default='low')
    max_trade_size = Column(Float, nullable=False)
    max_daily_trades = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    auto_adjust_enabled = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="fund_allocation")
    trade_history = relationship("TradeHistory", back_populates="fund_allocation")
    risk_configs = relationship("RiskModeConfig", back_populates="fund_allocation")

class TradeHistory(Base):
    __tablename__ = 'trade_history'
    
    id = Column(Integer, primary_key=True)
    fund_allocation_id = Column(Integer, ForeignKey('fund_allocations.id'))
    category = Column(Enum('stocks', 'fo', 'crypto', 'forex', 'commodities', name='trade_categories'))
    trade_amount = Column(Float, nullable=False)
    trade_type = Column(Enum('buy', 'sell', name='trade_types'))
    profit_loss = Column(Float, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    fund_allocation = relationship("FundAllocation", back_populates="trade_history")

class RiskModeConfig(Base):
    __tablename__ = 'risk_mode_configs'
    
    id = Column(Integer, primary_key=True)
    fund_allocation_id = Column(Integer, ForeignKey('fund_allocations.id'))
    risk_level = Column(Enum('low', 'medium', 'high', name='risk_levels'))
    allocated_amount = Column(Float, nullable=False)
    max_trade_size = Column(Float, nullable=False)
    max_daily_trades = Column(Integer, nullable=False)
    stop_loss_percentage = Column(Float, nullable=False)
    auto_adjust_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    fund_allocation = relationship("FundAllocation", back_populates="risk_configs")

class RiskModeDescription(Base):
    __tablename__ = 'risk_mode_descriptions'
    
    id = Column(Integer, primary_key=True)
    risk_level = Column(Enum('low', 'medium', 'high', name='risk_levels'), unique=True)
    description = Column(String, nullable=False)
    recommended_assets = Column(String, nullable=False)
    typical_returns = Column(String, nullable=False)
    risk_factors = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
