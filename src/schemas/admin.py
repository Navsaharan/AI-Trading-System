from pydantic import BaseModel, EmailStr, Field
from typing import Dict, List, Optional
from datetime import datetime

class SystemStats(BaseModel):
    """System-wide statistics schema."""
    total_users: int
    active_users: int
    total_trading_accounts: int
    active_strategies: int
    system_status: str
    last_updated: datetime

class UserList(BaseModel):
    """User list item schema."""
    id: int
    email: EmailStr
    is_active: bool
    is_admin: bool
    created_at: datetime
    last_login: Optional[datetime]

class UserUpdate(BaseModel):
    """User update response schema."""
    id: int
    email: EmailStr
    is_active: bool
    message: str

class APIKeyList(BaseModel):
    """API key list item schema."""
    id: int
    user_id: int
    broker: str
    is_active: bool
    created_at: datetime
    last_used: Optional[datetime]

class APIKeyUpdate(BaseModel):
    """API key update response schema."""
    id: int
    broker: str
    is_active: bool
    message: str

class TradingAccountList(BaseModel):
    """Trading account list item schema."""
    id: int
    user_id: int
    broker: str
    account_type: str
    is_active: bool
    balance: float
    created_at: datetime

class StrategyList(BaseModel):
    """Strategy list item schema."""
    id: int
    user_id: int
    name: str
    type: str
    performance: Dict
    created_at: datetime
    last_updated: datetime

class SystemSettings(BaseModel):
    """System settings schema."""
    max_users: Optional[int] = Field(None, ge=1)
    max_strategies_per_user: Optional[int] = Field(None, ge=1)
    default_risk_limit: Optional[float] = Field(None, ge=0, le=1)
    maintenance_mode: Optional[bool] = None
    allowed_brokers: Optional[List[str]] = None
    trading_hours: Optional[Dict[str, str]] = None

class SystemLogs(BaseModel):
    """System log entry schema."""
    timestamp: datetime
    level: str
    message: str
    source: str

class PerformanceMetrics(BaseModel):
    """System performance metrics schema."""
    metrics: Dict[str, Dict[str, float]]
    timestamp: datetime

class AdminToken(BaseModel):
    """Admin authentication token schema."""
    access_token: str
    token_type: str = "bearer"
