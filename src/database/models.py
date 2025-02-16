from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    api_keys = relationship("BrokerAPIKey", back_populates="user")
    trading_accounts = relationship("TradingAccount", back_populates="user")
    strategies = relationship("Strategy", back_populates="user")

class BrokerAPIKey(Base):
    __tablename__ = 'broker_api_keys'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    broker_name = Column(String, nullable=False)
    api_key = Column(String, nullable=False)
    api_secret = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")

class TradingAccount(Base):
    __tablename__ = 'trading_accounts'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    broker_name = Column(String, nullable=False)
    account_id = Column(String, nullable=False)
    account_type = Column(String)  # real/paper
    balance = Column(Float)
    currency = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="trading_accounts")
    positions = relationship("Position", back_populates="account")

class Strategy(Base):
    __tablename__ = 'strategies'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String, nullable=False)
    description = Column(String)
    type = Column(String)  # AI/Manual
    parameters = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="strategies")
    trades = relationship("Trade", back_populates="strategy")

class Position(Base):
    __tablename__ = 'positions'
    
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey('trading_accounts.id'))
    symbol = Column(String, nullable=False)
    quantity = Column(Float)
    entry_price = Column(Float)
    current_price = Column(Float)
    unrealized_pnl = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    account = relationship("TradingAccount", back_populates="positions")

class Trade(Base):
    __tablename__ = 'trades'
    
    id = Column(Integer, primary_key=True)
    strategy_id = Column(Integer, ForeignKey('strategies.id'))
    symbol = Column(String, nullable=False)
    side = Column(String)  # buy/sell
    quantity = Column(Float)
    price = Column(Float)
    status = Column(String)  # open/closed/cancelled
    pnl = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime)
    
    # Relationships
    strategy = relationship("Strategy", back_populates="trades")

class AIModel(Base):
    __tablename__ = 'ai_models'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String)  # prediction/sentiment/risk
    parameters = Column(JSON)
    performance_metrics = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_trained = Column(DateTime)
    last_used = Column(DateTime)

class MarketData(Base):
    __tablename__ = 'market_data'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    source = Column(String)  # broker name

class SentimentData(Base):
    __tablename__ = 'sentiment_data'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    source = Column(String)  # twitter/reddit/news
    sentiment_score = Column(Float)
    sentiment_magnitude = Column(Float)
    raw_data = Column(JSON)
