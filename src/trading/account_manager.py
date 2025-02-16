from typing import Dict, List, Optional
import asyncio
from datetime import datetime
from ..models.api_models import APIConfiguration
from ..database import SessionLocal

class TradingAccount:
    def __init__(self, broker_name: str, account_id: str, credentials: Dict):
        self.broker_name = broker_name
        self.account_id = account_id
        self.credentials = credentials
        self.session = None
        self.last_active = datetime.now()
        self.is_active = False

class AccountManager:
    def __init__(self):
        self.accounts: Dict[str, TradingAccount] = {}
        self.active_account: Optional[TradingAccount] = None
        self._session_refresh_task = None
    
    async def add_account(self, broker_name: str, account_id: str, credentials: Dict) -> bool:
        """Add a new trading account"""
        try:
            account = TradingAccount(broker_name, account_id, credentials)
            
            # Initialize broker session
            session = await self._initialize_broker_session(broker_name, credentials)
            if not session:
                return False
            
            account.session = session
            self.accounts[account_id] = account
            
            # If this is the first account, make it active
            if not self.active_account:
                await self.switch_account(account_id)
            
            return True
        except Exception as e:
            print(f"Error adding account: {str(e)}")
            return False
    
    async def switch_account(self, account_id: str) -> bool:
        """Switch to a different trading account"""
        try:
            if account_id not in self.accounts:
                return False
            
            # Deactivate current account
            if self.active_account:
                self.active_account.is_active = False
            
            # Activate new account
            account = self.accounts[account_id]
            account.is_active = True
            account.last_active = datetime.now()
            self.active_account = account
            
            # Ensure session is active
            if not await self._verify_session(account):
                await self._refresh_session(account)
            
            return True
        except Exception as e:
            print(f"Error switching account: {str(e)}")
            return False
    
    async def _initialize_broker_session(self, broker_name: str, credentials: Dict) -> Optional[Dict]:
        """Initialize broker-specific trading session"""
        try:
            if broker_name == "upstox":
                return await self._init_upstox_session(credentials)
            elif broker_name == "zerodha":
                return await self._init_zerodha_session(credentials)
            elif broker_name == "angelone":
                return await self._init_angelone_session(credentials)
            elif broker_name == "binance":
                return await self._init_binance_session(credentials)
            else:
                raise ValueError(f"Unsupported broker: {broker_name}")
        except Exception as e:
            print(f"Error initializing {broker_name} session: {str(e)}")
            return None
    
    async def _verify_session(self, account: TradingAccount) -> bool:
        """Verify if the trading session is still valid"""
        try:
            if account.broker_name == "upstox":
                return await self._verify_upstox_session(account.session)
            elif account.broker_name == "zerodha":
                return await self._verify_zerodha_session(account.session)
            elif account.broker_name == "angelone":
                return await self._verify_angelone_session(account.session)
            elif account.broker_name == "binance":
                return await self._verify_binance_session(account.session)
            return False
        except:
            return False
    
    async def _refresh_session(self, account: TradingAccount) -> bool:
        """Refresh trading session if expired"""
        try:
            new_session = await self._initialize_broker_session(
                account.broker_name, 
                account.credentials
            )
            if new_session:
                account.session = new_session
                return True
            return False
        except:
            return False
    
    async def start_session_refresh(self):
        """Start background task to refresh sessions"""
        if self._session_refresh_task:
            return
        
        self._session_refresh_task = asyncio.create_task(self._session_refresh_loop())
    
    async def _session_refresh_loop(self):
        """Background loop to refresh sessions"""
        while True:
            try:
                for account in self.accounts.values():
                    if account.is_active:
                        if not await self._verify_session(account):
                            await self._refresh_session(account)
                
                await asyncio.sleep(300)  # Check every 5 minutes
            except Exception as e:
                print(f"Error in session refresh: {str(e)}")
                await asyncio.sleep(60)
    
    async def get_active_account(self) -> Optional[TradingAccount]:
        """Get currently active trading account"""
        return self.active_account
    
    async def get_all_accounts(self) -> List[Dict]:
        """Get list of all trading accounts"""
        return [{
            'broker_name': acc.broker_name,
            'account_id': acc.account_id,
            'is_active': acc.is_active,
            'last_active': acc.last_active.isoformat()
        } for acc in self.accounts.values()]
    
    # Broker-specific session initialization
    async def _init_upstox_session(self, credentials: Dict) -> Optional[Dict]:
        """Initialize Upstox trading session"""
        try:
            api_key = credentials.get('api_key')
            api_secret = credentials.get('api_secret')
            # Implement Upstox login logic
            return {'api_key': api_key, 'session_token': 'dummy_token'}
        except:
            return None
    
    async def _init_zerodha_session(self, credentials: Dict) -> Optional[Dict]:
        """Initialize Zerodha trading session"""
        try:
            api_key = credentials.get('api_key')
            api_secret = credentials.get('api_secret')
            # Implement Zerodha login logic
            return {'api_key': api_key, 'session_token': 'dummy_token'}
        except:
            return None
    
    async def _init_angelone_session(self, credentials: Dict) -> Optional[Dict]:
        """Initialize Angel One trading session"""
        try:
            api_key = credentials.get('api_key')
            api_secret = credentials.get('api_secret')
            # Implement Angel One login logic
            return {'api_key': api_key, 'session_token': 'dummy_token'}
        except:
            return None
    
    async def _init_binance_session(self, credentials: Dict) -> Optional[Dict]:
        """Initialize Binance trading session"""
        try:
            api_key = credentials.get('api_key')
            api_secret = credentials.get('api_secret')
            # Implement Binance login logic
            return {'api_key': api_key, 'session_token': 'dummy_token'}
        except:
            return None
    
    # Broker-specific session verification
    async def _verify_upstox_session(self, session: Dict) -> bool:
        """Verify Upstox session validity"""
        # Implement session verification logic
        return True
    
    async def _verify_zerodha_session(self, session: Dict) -> bool:
        """Verify Zerodha session validity"""
        # Implement session verification logic
        return True
    
    async def _verify_angelone_session(self, session: Dict) -> bool:
        """Verify Angel One session validity"""
        # Implement session verification logic
        return True
    
    async def _verify_binance_session(self, session: Dict) -> bool:
        """Verify Binance session validity"""
        # Implement session verification logic
        return True

# Initialize global account manager
account_manager = AccountManager()
