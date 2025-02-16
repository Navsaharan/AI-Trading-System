from typing import Dict, List, Optional
import asyncio
from datetime import datetime
from enum import Enum
from ..models.api_models import APIConfiguration
from ..database import SessionLocal

class PlatformType(Enum):
    STOCKS = "stocks"
    CRYPTO = "crypto"
    FOREX = "forex"
    FUTURES = "futures"

class BrokerType(Enum):
    API = "api"
    MANUAL = "manual"

class TradingPlatform:
    def __init__(self, 
                 name: str,
                 platform_type: PlatformType,
                 broker_type: BrokerType,
                 credentials: Dict = None):
        self.name = name
        self.platform_type = platform_type
        self.broker_type = broker_type
        self.credentials = credentials
        self.session = None
        self.is_active = False
        self.last_active = None
        self.error_count = 0
        self.supported_assets = set()

class PlatformManager:
    def __init__(self):
        self.platforms: Dict[str, TradingPlatform] = {}
        self.active_platforms: Dict[PlatformType, TradingPlatform] = {}
        self._monitor_task = None
        
        # Initialize supported assets
        self.asset_mappings = {
            PlatformType.STOCKS: {
                "zerodha": ["NSE", "BSE"],
                "upstox": ["NSE", "BSE"],
                "angelone": ["NSE", "BSE", "MCX"]
            },
            PlatformType.CRYPTO: {
                "binance": ["BTC", "ETH", "BNB"],
                "wazirx": ["BTC", "ETH", "WRX"],
                "coinbase": ["BTC", "ETH", "USDT"]
            },
            PlatformType.FOREX: {
                "fyers": ["USD/INR", "EUR/INR", "GBP/INR"],
                "icici": ["USD/INR", "EUR/INR", "GBP/INR"]
            },
            PlatformType.FUTURES: {
                "zerodha": ["NIFTY", "BANKNIFTY"],
                "upstox": ["NIFTY", "BANKNIFTY"],
                "angelone": ["NIFTY", "BANKNIFTY", "MCX"]
            }
        }

    async def add_platform(self, 
                          name: str,
                          platform_type: PlatformType,
                          broker_type: BrokerType,
                          credentials: Dict = None) -> bool:
        """Add a new trading platform"""
        try:
            platform = TradingPlatform(name, platform_type, broker_type, credentials)
            
            # Initialize platform session
            if broker_type == BrokerType.API:
                session = await self._initialize_api_session(name, credentials)
                if not session:
                    return False
                platform.session = session
            
            # Set supported assets
            platform.supported_assets = self._get_supported_assets(name, platform_type)
            
            self.platforms[name] = platform
            
            # If first platform of this type, make it active
            if platform_type not in self.active_platforms:
                await self.activate_platform(name)
            
            return True
            
        except Exception as e:
            print(f"Error adding platform {name}: {str(e)}")
            return False

    async def activate_platform(self, name: str) -> bool:
        """Activate a trading platform"""
        try:
            if name not in self.platforms:
                return False
            
            platform = self.platforms[name]
            
            # Deactivate current platform of same type
            if platform.platform_type in self.active_platforms:
                current = self.active_platforms[platform.platform_type]
                current.is_active = False
            
            # Activate new platform
            platform.is_active = True
            platform.last_active = datetime.now()
            self.active_platforms[platform.platform_type] = platform
            
            # Verify/refresh session
            if platform.broker_type == BrokerType.API:
                if not await self._verify_session(platform):
                    await self._refresh_session(platform)
            
            return True
            
        except Exception as e:
            print(f"Error activating platform {name}: {str(e)}")
            return False

    async def start_monitoring(self):
        """Start platform monitoring"""
        if self._monitor_task:
            return
        
        self._monitor_task = asyncio.create_task(self._monitor_platforms())

    async def _monitor_platforms(self):
        """Monitor platform health and sessions"""
        while True:
            try:
                for platform in self.platforms.values():
                    if platform.is_active:
                        # Check API platforms
                        if platform.broker_type == BrokerType.API:
                            if not await self._verify_session(platform):
                                platform.error_count += 1
                                if platform.error_count > 3:
                                    await self._handle_platform_failure(platform)
                                else:
                                    await self._refresh_session(platform)
                            else:
                                platform.error_count = 0
                        
                        # Check manual platforms
                        else:
                            if not await self._verify_manual_session(platform):
                                await self._handle_manual_platform_failure(platform)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                print(f"Error in platform monitoring: {str(e)}")
                await asyncio.sleep(60)

    async def _handle_platform_failure(self, platform: TradingPlatform):
        """Handle platform failure by switching to backup"""
        print(f"Platform {platform.name} failed, switching to backup...")
        
        # Find backup platform of same type
        backup = None
        for p in self.platforms.values():
            if (p.platform_type == platform.platform_type and 
                p.name != platform.name and 
                not p.is_active):
                backup = p
                break
        
        if backup:
            await self.activate_platform(backup.name)
        else:
            print(f"No backup platform available for {platform.platform_type}")

    async def _handle_manual_platform_failure(self, platform: TradingPlatform):
        """Handle manual platform session failure"""
        print(f"Manual platform {platform.name} session expired")
        # Notify admin to refresh session
        await self._notify_admin_manual_session(platform)

    async def get_active_platforms(self) -> Dict[PlatformType, str]:
        """Get currently active platforms by type"""
        return {
            ptype: platform.name 
            for ptype, platform in self.active_platforms.items()
        }

    async def get_platform_status(self) -> List[Dict]:
        """Get status of all platforms"""
        return [{
            'name': p.name,
            'type': p.platform_type.value,
            'broker_type': p.broker_type.value,
            'is_active': p.is_active,
            'last_active': p.last_active.isoformat() if p.last_active else None,
            'error_count': p.error_count,
            'supported_assets': list(p.supported_assets)
        } for p in self.platforms.values()]

    def _get_supported_assets(self, name: str, platform_type: PlatformType) -> set:
        """Get supported assets for a platform"""
        platform_assets = self.asset_mappings.get(platform_type, {})
        return set(platform_assets.get(name.lower(), []))

    # Platform-specific session management
    async def _initialize_api_session(self, name: str, credentials: Dict) -> Optional[Dict]:
        """Initialize API session for a platform"""
        try:
            if name.lower() == "zerodha":
                return await self._init_zerodha_session(credentials)
            elif name.lower() == "upstox":
                return await self._init_upstox_session(credentials)
            elif name.lower() == "binance":
                return await self._init_binance_session(credentials)
            elif name.lower() == "angelone":
                return await self._init_angelone_session(credentials)
            else:
                raise ValueError(f"Unsupported platform: {name}")
        except Exception as e:
            print(f"Error initializing {name} session: {str(e)}")
            return None

    async def _verify_session(self, platform: TradingPlatform) -> bool:
        """Verify API session validity"""
        try:
            if platform.name.lower() == "zerodha":
                return await self._verify_zerodha_session(platform.session)
            elif platform.name.lower() == "upstox":
                return await self._verify_upstox_session(platform.session)
            elif platform.name.lower() == "binance":
                return await self._verify_binance_session(platform.session)
            elif platform.name.lower() == "angelone":
                return await self._verify_angelone_session(platform.session)
            return False
        except:
            return False

    async def _verify_manual_session(self, platform: TradingPlatform) -> bool:
        """Verify manual session validity"""
        # Implement manual session verification logic
        return True

    async def _refresh_session(self, platform: TradingPlatform) -> bool:
        """Refresh API session"""
        try:
            new_session = await self._initialize_api_session(
                platform.name,
                platform.credentials
            )
            if new_session:
                platform.session = new_session
                return True
            return False
        except:
            return False

    async def _notify_admin_manual_session(self, platform: TradingPlatform):
        """Notify admin about manual session expiry"""
        # Implement admin notification logic
        pass

# Initialize global platform manager
platform_manager = PlatformManager()
