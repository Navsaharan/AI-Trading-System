from enum import Enum
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from datetime import datetime

class OrderType(str, Enum):
    REGULAR = "regular"
    BRACKET = "bracket"
    COVER = "cover"
    GTT = "gtt"

class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class PriceType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    SL = "SL"
    SL_M = "SL-M"

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    OPEN = "OPEN"
    COMPLETE = "COMPLETE"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"

class ProductType(str, Enum):
    CNC = "CNC"  # Cash and Carry (Delivery)
    MIS = "MIS"  # Margin Intraday Square-off
    NRML = "NRML"  # Normal (F&O)

class Exchange(str, Enum):
    NSE = "NSE"
    BSE = "BSE"
    NFO = "NFO"  # NSE F&O
    BFO = "BFO"  # BSE F&O
    MCX = "MCX"  # Commodities
    CDS = "CDS"  # Currency Derivatives

class Segment(str, Enum):
    EQUITY = "EQUITY"
    FNO = "FNO"
    CURRENCY = "CURRENCY"
    COMMODITY = "COMMODITY"

class GTTType(str, Enum):
    SINGLE = "SINGLE"  # Single target price
    OCO = "OCO"  # One Cancels Other (dual target price)

class Order(BaseModel):
    id: Optional[str] = None
    user_id: Optional[str] = None
    type: OrderType
    symbol: str
    exchange: Exchange
    segment: Segment
    side: OrderSide
    quantity: int
    price_type: PriceType
    product_type: ProductType
    price: Optional[float] = None
    trigger_price: Optional[float] = None
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    trailing_sl: Optional[float] = None
    status: Optional[OrderStatus] = OrderStatus.PENDING
    filled_quantity: int = 0
    average_price: Optional[float] = None
    order_timestamp: Optional[datetime] = None
    validity: Optional[str] = "DAY"
    disclosed_quantity: Optional[int] = None
    notes: Optional[str] = None

class GTTOrder(BaseModel):
    id: Optional[str] = None
    user_id: Optional[str] = None
    symbol: str
    exchange: Exchange
    type: GTTType
    side: OrderSide
    quantity: int
    price: float
    trigger_prices: List[float]
    status: str = "ACTIVE"
    expiry_date: Optional[datetime] = None
    created_at: Optional[datetime] = None

class Position(BaseModel):
    id: str
    user_id: str
    symbol: str
    exchange: Exchange
    product_type: ProductType
    quantity: int
    average_price: float
    last_price: float
    pnl: float
    day_pnl: float
    realized_pnl: float
    unrealized_pnl: float
    value: float
    multiplier: float = 1
    overnight_quantity: int = 0
    buy_value: float = 0
    sell_value: float = 0
    buy_quantity: int = 0
    sell_quantity: int = 0

class Trade(BaseModel):
    id: str
    user_id: str
    order_id: str
    symbol: str
    exchange: Exchange
    side: OrderSide
    quantity: int
    price: float
    trade_timestamp: datetime
    product_type: ProductType

class Stock(BaseModel):
    symbol: str
    name: str
    exchange: Exchange
    segment: Segment
    series: Optional[str] = None
    token: Optional[str] = None
    isin: Optional[str] = None
    last_price: float
    change: float
    change_percent: float
    open: float
    high: float
    low: float
    close: float
    volume: int
    value: float
    last_trade_time: datetime
    oi: Optional[int] = None  # Open Interest for F&O
    expiry: Optional[datetime] = None  # For F&O instruments

class MarketDepth(BaseModel):
    symbol: str
    exchange: Exchange
    timestamp: datetime
    bids: List[Dict[str, float]]  # [{"quantity": x, "price": y, "orders": z}]
    asks: List[Dict[str, float]]
    total_buy_quantity: int
    total_sell_quantity: int
    average_trade_price: float
    last_trade_price: float
    last_trade_quantity: int
    volume: int
    total_trades: int
    oi: Optional[int] = None
    oi_change: Optional[int] = None

class WatchlistItem(BaseModel):
    id: Optional[str] = None
    user_id: str
    symbol: str
    exchange: Exchange
    added_at: Optional[datetime] = None
    notes: Optional[str] = None
    alerts: Optional[List[Dict]] = None

class OHLC(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    oi: Optional[int] = None

class OrderBook(BaseModel):
    orders: List[Order]
    total: int
    page: int
    per_page: int

class PositionBook(BaseModel):
    positions: List[Position]
    total: int
    total_pnl: float
    day_pnl: float

class TradeBook(BaseModel):
    trades: List[Trade]
    total: int
    page: int
    per_page: int

class MarketStatus(BaseModel):
    exchange: Exchange
    segment: Segment
    status: str
    next_state: Optional[str] = None
    next_state_timestamp: Optional[datetime] = None

class Holding(BaseModel):
    symbol: str
    exchange: Exchange
    isin: str
    quantity: int
    collateral_quantity: int = 0
    collateral_type: Optional[str] = None
    average_price: float
    last_price: float
    pnl: float
    day_pnl: float
    value: float

class Fund(BaseModel):
    user_id: str
    total_balance: float
    available_balance: float
    used_margin: float
    available_margin: float
    opening_balance: float
    payin_amount: float
    payout_amount: float
    span_margin: Optional[float] = None
    exposure_margin: Optional[float] = None
    collateral_value: Optional[float] = None
    updated_at: datetime

class MarginRequired(BaseModel):
    total: float
    span: Optional[float] = None
    exposure: Optional[float] = None
    var: Optional[float] = None
    extreme_loss: Optional[float] = None
    delivery: Optional[float] = None
    additional: Optional[float] = None
    bo: Optional[float] = None  # Bracket Order
    cash: Optional[float] = None
