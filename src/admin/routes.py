from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from .admin_panel import AdminPanel
from ..database import get_db
from ..schemas.admin import (
    SystemStats,
    UserList,
    UserUpdate,
    APIKeyList,
    APIKeyUpdate,
    TradingAccountList,
    StrategyList,
    SystemSettings,
    SystemLogs,
    PerformanceMetrics
)

router = APIRouter(prefix="/admin", tags=["admin"])
admin_panel = AdminPanel()

@router.get("/stats", response_model=SystemStats)
async def get_system_stats(
    db: Session = Depends(get_db),
    _: bool = Depends(admin_panel.verify_admin_token)
):
    """Get system-wide statistics."""
    return await admin_panel.get_system_stats(db)

@router.get("/users", response_model=List[UserList])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    _: bool = Depends(admin_panel.verify_admin_token)
):
    """Get list of users."""
    return await admin_panel.get_user_list(db, skip, limit)

@router.put("/users/{user_id}", response_model=UserUpdate)
async def update_user(
    user_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    _: bool = Depends(admin_panel.verify_admin_token)
):
    """Update user's active status."""
    return await admin_panel.update_user_status(user_id, is_active, db)

@router.get("/api-keys", response_model=List[APIKeyList])
async def get_api_keys(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    _: bool = Depends(admin_panel.verify_admin_token)
):
    """Get list of API keys."""
    return await admin_panel.get_api_keys(db, skip, limit)

@router.put("/api-keys/{key_id}", response_model=APIKeyUpdate)
async def update_api_key(
    key_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    _: bool = Depends(admin_panel.verify_admin_token)
):
    """Update API key's active status."""
    return await admin_panel.update_api_key_status(key_id, is_active, db)

@router.get("/trading-accounts", response_model=List[TradingAccountList])
async def get_trading_accounts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    _: bool = Depends(admin_panel.verify_admin_token)
):
    """Get list of trading accounts."""
    return await admin_panel.get_trading_accounts(db, skip, limit)

@router.get("/strategies", response_model=List[StrategyList])
async def get_strategies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    _: bool = Depends(admin_panel.verify_admin_token)
):
    """Get list of active trading strategies."""
    return await admin_panel.get_active_strategies(db, skip, limit)

@router.put("/settings", response_model=SystemSettings)
async def update_settings(
    settings: SystemSettings,
    db: Session = Depends(get_db),
    _: bool = Depends(admin_panel.verify_admin_token)
):
    """Update system-wide settings."""
    return await admin_panel.update_system_settings(settings.dict(), db)

@router.get("/logs", response_model=List[SystemLogs])
async def get_logs(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    level: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    _: bool = Depends(admin_panel.verify_admin_token)
):
    """Get system logs with filtering options."""
    return await admin_panel.get_system_logs(start_time, end_time, level, limit)

@router.get("/performance", response_model=PerformanceMetrics)
async def get_performance(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: Session = Depends(get_db),
    _: bool = Depends(admin_panel.verify_admin_token)
):
    """Get system performance metrics."""
    return await admin_panel.get_performance_metrics(db, start_time, end_time)
