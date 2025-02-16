from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from ..config.database import Base
import enum

class IPOStatus(enum.Enum):
    UPCOMING = "upcoming"
    ONGOING = "ongoing"
    CLOSED = "closed"
    LISTED = "listed"

class IPORiskLevel(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class IPO(Base):
    __tablename__ = 'ipos'
    
    id = Column(Integer, primary_key=True)
    company_name = Column(String, nullable=False)
    symbol = Column(String)
    industry = Column(String)
    issue_price_min = Column(Float, nullable=False)
    issue_price_max = Column(Float, nullable=False)
    lot_size = Column(Integer, nullable=False)
    issue_size = Column(Float)  # In crores
    fresh_issue = Column(Float)  # In crores
    offer_for_sale = Column(Float)  # In crores
    
    # Dates
    open_date = Column(DateTime)
    close_date = Column(DateTime)
    listing_date = Column(DateTime)
    
    # Status
    status = Column(Enum(IPOStatus), default=IPOStatus.UPCOMING)
    exchange = Column(String)  # NSE/BSE/Both
    
    # Performance
    listing_price = Column(Float)
    current_price = Column(Float)
    subscription_retail = Column(Float, default=0)
    subscription_hni = Column(Float, default=0)
    subscription_qib = Column(Float, default=0)
    total_subscription = Column(Float, default=0)
    
    # AI Analysis
    sentiment_score = Column(Float)  # 0 to 1
    hype_level = Column(Float)  # 0 to 1
    risk_level = Column(Enum(IPORiskLevel))
    expected_listing_gain = Column(Float)  # Percentage
    allotment_probability = Column(Float)  # 0 to 1
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    grey_market_prices = relationship("GreyMarketPrice", back_populates="ipo")
    news_items = relationship("IPONews", back_populates="ipo")
    institutional_investments = relationship("InstitutionalInvestment", back_populates="ipo")

class GreyMarketPrice(Base):
    __tablename__ = 'grey_market_prices'
    
    id = Column(Integer, primary_key=True)
    ipo_id = Column(Integer, ForeignKey('ipos.id'))
    premium = Column(Float)  # Premium/Discount amount
    timestamp = Column(DateTime, default=datetime.utcnow)
    source = Column(String)
    
    # Relationship
    ipo = relationship("IPO", back_populates="grey_market_prices")

class IPONews(Base):
    __tablename__ = 'ipo_news'
    
    id = Column(Integer, primary_key=True)
    ipo_id = Column(Integer, ForeignKey('ipos.id'))
    title = Column(String, nullable=False)
    content = Column(Text)
    source = Column(String)
    url = Column(String)
    sentiment_score = Column(Float)  # -1 to 1
    published_at = Column(DateTime)
    
    # Relationship
    ipo = relationship("IPO", back_populates="news_items")

class InstitutionalInvestment(Base):
    __tablename__ = 'institutional_investments'
    
    id = Column(Integer, primary_key=True)
    ipo_id = Column(Integer, ForeignKey('ipos.id'))
    institution_name = Column(String, nullable=False)
    investment_amount = Column(Float)  # In crores
    category = Column(String)  # Mutual Fund, FII, etc.
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    ipo = relationship("IPO", back_populates="institutional_investments")
