from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import jwt
from ..database import get_db
from ..models.user import User
from ..models.api_key import APIKey
from ..models.trading_account import TradingAccount
from ..models.strategy import Strategy
from ..core.config import settings

router = APIRouter(prefix="/admin", tags=["admin"])
security = HTTPBearer()

class AdminPanel:
    """Admin panel for managing users, API keys, and system settings."""
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.admin_token_expire = timedelta(hours=4)
    
    def verify_admin_token(self, credentials: HTTPAuthorizationCredentials = Security(security)) -> bool:
        """Verify admin authentication token."""
        try:
            token = credentials.credentials
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            if not payload.get("is_admin"):
                raise HTTPException(status_code=403, detail="Not an admin user")
            return True
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    async def create_admin_token(self, user_id: int, db: Session) -> str:
        """Create admin authentication token."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_admin:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        payload = {
            "user_id": user_id,
            "is_admin": True,
            "exp": datetime.utcnow() + self.admin_token_expire
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
    
    async def get_system_stats(self, db: Session) -> Dict:
        """Get system-wide statistics."""
        try:
            total_users = db.query(User).count()
            active_users = db.query(User).filter(User.is_active == True).count()
            total_accounts = db.query(TradingAccount).count()
            active_strategies = db.query(Strategy).filter(Strategy.is_active == True).count()
            
            return {
                "total_users": total_users,
                "active_users": active_users,
                "total_trading_accounts": total_accounts,
                "active_strategies": active_strategies,
                "system_status": "healthy",
                "last_updated": datetime.utcnow()
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting system stats: {str(e)}")
    
    async def get_user_list(self, db: Session, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Get list of users with their details."""
        try:
            users = db.query(User).offset(skip).limit(limit).all()
            return [{
                "id": user.id,
                "email": user.email,
                "is_active": user.is_active,
                "is_admin": user.is_admin,
                "created_at": user.created_at,
                "last_login": user.last_login
            } for user in users]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting user list: {str(e)}")
    
    async def update_user_status(self, user_id: int, is_active: bool, db: Session) -> Dict:
        """Update user's active status."""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            user.is_active = is_active
            db.commit()
            
            return {
                "id": user.id,
                "email": user.email,
                "is_active": user.is_active,
                "message": "User status updated successfully"
            }
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error updating user status: {str(e)}")
    
    async def get_api_keys(self, db: Session, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Get list of API keys."""
        try:
            api_keys = db.query(APIKey).offset(skip).limit(limit).all()
            return [{
                "id": key.id,
                "user_id": key.user_id,
                "broker": key.broker,
                "is_active": key.is_active,
                "created_at": key.created_at,
                "last_used": key.last_used
            } for key in api_keys]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting API keys: {str(e)}")
    
    async def update_api_key_status(self, key_id: int, is_active: bool, db: Session) -> Dict:
        """Update API key's active status."""
        try:
            api_key = db.query(APIKey).filter(APIKey.id == key_id).first()
            if not api_key:
                raise HTTPException(status_code=404, detail="API key not found")
            
            api_key.is_active = is_active
            db.commit()
            
            return {
                "id": api_key.id,
                "broker": api_key.broker,
                "is_active": api_key.is_active,
                "message": "API key status updated successfully"
            }
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error updating API key status: {str(e)}")
    
    async def get_trading_accounts(self, db: Session, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Get list of trading accounts."""
        try:
            accounts = db.query(TradingAccount).offset(skip).limit(limit).all()
            return [{
                "id": account.id,
                "user_id": account.user_id,
                "broker": account.broker,
                "account_type": account.account_type,
                "is_active": account.is_active,
                "balance": account.balance,
                "created_at": account.created_at
            } for account in accounts]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting trading accounts: {str(e)}")
    
    async def get_active_strategies(self, db: Session, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Get list of active trading strategies."""
        try:
            strategies = db.query(Strategy).filter(Strategy.is_active == True)\
                                        .offset(skip).limit(limit).all()
            return [{
                "id": strategy.id,
                "user_id": strategy.user_id,
                "name": strategy.name,
                "type": strategy.type,
                "performance": strategy.performance,
                "created_at": strategy.created_at,
                "last_updated": strategy.last_updated
            } for strategy in strategies]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting strategies: {str(e)}")
    
    async def update_system_settings(self, settings: Dict, db: Session) -> Dict:
        """Update system-wide settings."""
        try:
            # Update settings in database
            for key, value in settings.items():
                setting = db.query(SystemSetting).filter(SystemSetting.key == key).first()
                if setting:
                    setting.value = value
                    setting.updated_at = datetime.utcnow()
            
            db.commit()
            return {
                "message": "System settings updated successfully",
                "updated_settings": settings
            }
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error updating system settings: {str(e)}")
    
    async def get_system_logs(self, start_time: Optional[datetime] = None,
                            end_time: Optional[datetime] = None,
                            level: Optional[str] = None,
                            limit: int = 100) -> List[Dict]:
        """Get system logs with filtering options."""
        try:
            query = db.query(SystemLog)
            
            if start_time:
                query = query.filter(SystemLog.timestamp >= start_time)
            if end_time:
                query = query.filter(SystemLog.timestamp <= end_time)
            if level:
                query = query.filter(SystemLog.level == level.upper())
            
            logs = query.order_by(SystemLog.timestamp.desc()).limit(limit).all()
            
            return [{
                "timestamp": log.timestamp,
                "level": log.level,
                "message": log.message,
                "source": log.source
            } for log in logs]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting system logs: {str(e)}")
    
    async def get_performance_metrics(self, db: Session,
                                   start_time: Optional[datetime] = None,
                                   end_time: Optional[datetime] = None) -> Dict:
        """Get system performance metrics."""
        try:
            metrics = {
                "cpu_usage": self._get_cpu_usage(),
                "memory_usage": self._get_memory_usage(),
                "api_latency": self._get_api_latency(),
                "database_connections": self._get_db_connections(db),
                "active_websockets": self._get_active_websockets()
            }
            
            return {
                "metrics": metrics,
                "timestamp": datetime.utcnow()
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting performance metrics: {str(e)}")
    
    def _get_cpu_usage(self) -> float:
        """Get current CPU usage."""
        import psutil
        return psutil.cpu_percent()
    
    def _get_memory_usage(self) -> Dict:
        """Get current memory usage."""
        import psutil
        memory = psutil.virtual_memory()
        return {
            "total": memory.total,
            "available": memory.available,
            "percent": memory.percent
        }
    
    def _get_api_latency(self) -> Dict:
        """Get API endpoint latencies."""
        # Implementation depends on monitoring setup
        return {
            "average": 100,  # ms
            "p95": 200,     # ms
            "p99": 300      # ms
        }
    
    def _get_db_connections(self, db: Session) -> int:
        """Get number of active database connections."""
        result = db.execute("SELECT count(*) FROM pg_stat_activity")
        return result.scalar()
    
    def _get_active_websockets(self) -> int:
        """Get number of active WebSocket connections."""
        # Implementation depends on WebSocket server
        return 0  # Placeholder
