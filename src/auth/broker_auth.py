from typing import Dict, Optional
import json
import aiohttp
from datetime import datetime, timedelta
from ..models.user_models import User
from ..database import SessionLocal
from ..trading.platform_manager import BrokerType

class BrokerAuth:
    def __init__(self):
        # OAuth configurations
        self.oauth_configs = {
            'upstox': {
                'auth_url': 'https://api-v2.upstox.com/login/authorization/dialog',
                'token_url': 'https://api-v2.upstox.com/login/authorization/token',
                'redirect_uri': '/auth/upstox/callback',
                'scope': 'orders holdings positions profile'
            },
            'zerodha': {
                'auth_url': 'https://kite.zerodha.com/connect/login',
                'token_url': 'https://api.kite.trade/session/token',
                'redirect_uri': '/auth/zerodha/callback',
                'scope': 'orders holdings positions'
            },
            'angelone': {
                'auth_url': 'https://smartapi.angelbroking.com/publisher-login',
                'token_url': 'https://apiconnect.angelbroking.com/rest/auth/angelbroking/user/v1/getToken',
                'redirect_uri': '/auth/angelone/callback',
                'scope': 'orders holdings positions'
            },
            'binance': {
                'auth_url': 'https://accounts.binance.com/en/oauth/authorize',
                'token_url': 'https://api.binance.com/oauth/token',
                'redirect_uri': '/auth/binance/callback',
                'scope': 'trade account:read'
            }
        }
        
        # Manual login configurations
        self.manual_configs = {
            'groww': {
                'login_url': 'https://groww.in/login',
                'session_duration': timedelta(hours=8)
            },
            'icici': {
                'login_url': 'https://secure.icicidirect.com/trading/login',
                'session_duration': timedelta(hours=4)
            }
        }

    async def initialize_login(self, broker: str, broker_type: BrokerType) -> Dict:
        """Initialize broker login process"""
        try:
            if broker_type == BrokerType.API:
                return await self._initialize_oauth_login(broker)
            else:
                return await self._initialize_manual_login(broker)
        except Exception as e:
            print(f"Error initializing {broker} login: {str(e)}")
            return {'error': str(e)}

    async def _initialize_oauth_login(self, broker: str) -> Dict:
        """Initialize OAuth login flow"""
        try:
            config = self.oauth_configs.get(broker.lower())
            if not config:
                raise ValueError(f"Unsupported broker: {broker}")

            auth_params = {
                'response_type': 'code',
                'client_id': self._get_client_id(broker),
                'redirect_uri': config['redirect_uri'],
                'scope': config['scope'],
                'state': self._generate_state_token()
            }

            auth_url = f"{config['auth_url']}?{self._build_query_string(auth_params)}"
            
            return {
                'type': 'oauth',
                'auth_url': auth_url,
                'state': auth_params['state']
            }
            
        except Exception as e:
            print(f"OAuth initialization error for {broker}: {str(e)}")
            return {'error': str(e)}

    async def _initialize_manual_login(self, broker: str) -> Dict:
        """Initialize manual login flow"""
        try:
            config = self.manual_configs.get(broker.lower())
            if not config:
                raise ValueError(f"Unsupported broker: {broker}")

            return {
                'type': 'manual',
                'login_url': config['login_url'],
                'session_duration': config['session_duration'].total_seconds()
            }
            
        except Exception as e:
            print(f"Manual login initialization error for {broker}: {str(e)}")
            return {'error': str(e)}

    async def handle_oauth_callback(self, broker: str, code: str, state: str) -> Dict:
        """Handle OAuth callback and get access token"""
        try:
            config = self.oauth_configs.get(broker.lower())
            if not config:
                raise ValueError(f"Unsupported broker: {broker}")

            # Verify state token
            if not self._verify_state_token(state):
                raise ValueError("Invalid state token")

            # Exchange code for token
            token_params = {
                'grant_type': 'authorization_code',
                'code': code,
                'client_id': self._get_client_id(broker),
                'client_secret': self._get_client_secret(broker),
                'redirect_uri': config['redirect_uri']
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(config['token_url'], data=token_params) as response:
                    if response.status != 200:
                        raise ValueError(f"Token exchange failed: {await response.text()}")
                    
                    token_data = await response.json()
                    return self._process_oauth_token(broker, token_data)

        except Exception as e:
            print(f"OAuth callback error for {broker}: {str(e)}")
            return {'error': str(e)}

    async def handle_manual_login(self, broker: str, credentials: Dict) -> Dict:
        """Handle manual login and create session"""
        try:
            config = self.manual_configs.get(broker.lower())
            if not config:
                raise ValueError(f"Unsupported broker: {broker}")

            # Validate credentials
            if not self._validate_manual_credentials(broker, credentials):
                raise ValueError("Invalid credentials")

            # Create session
            session = {
                'broker': broker,
                'user_id': credentials['user_id'],
                'created_at': datetime.now(),
                'expires_at': datetime.now() + config['session_duration'],
                'session_id': self._generate_session_id()
            }

            # Store session
            await self._store_manual_session(session)

            return {
                'type': 'manual',
                'session_id': session['session_id'],
                'expires_at': session['expires_at'].isoformat()
            }

        except Exception as e:
            print(f"Manual login error for {broker}: {str(e)}")
            return {'error': str(e)}

    async def verify_session(self, broker: str, session_data: Dict) -> bool:
        """Verify if a broker session is valid"""
        try:
            if session_data.get('type') == 'oauth':
                return await self._verify_oauth_session(broker, session_data)
            else:
                return await self._verify_manual_session(broker, session_data)
        except:
            return False

    async def refresh_session(self, broker: str, session_data: Dict) -> Optional[Dict]:
        """Refresh a broker session"""
        try:
            if session_data.get('type') == 'oauth':
                return await self._refresh_oauth_session(broker, session_data)
            else:
                return await self._refresh_manual_session(broker, session_data)
        except:
            return None

    def _get_client_id(self, broker: str) -> str:
        """Get OAuth client ID for broker"""
        # Implement secure client ID retrieval
        return "dummy_client_id"

    def _get_client_secret(self, broker: str) -> str:
        """Get OAuth client secret for broker"""
        # Implement secure client secret retrieval
        return "dummy_client_secret"

    def _generate_state_token(self) -> str:
        """Generate secure state token for OAuth"""
        # Implement secure token generation
        return "dummy_state_token"

    def _verify_state_token(self, state: str) -> bool:
        """Verify OAuth state token"""
        # Implement token verification
        return True

    def _generate_session_id(self) -> str:
        """Generate secure session ID"""
        # Implement secure session ID generation
        return "dummy_session_id"

    def _build_query_string(self, params: Dict) -> str:
        """Build URL query string from parameters"""
        return "&".join([f"{k}={v}" for k, v in params.items()])

    def _process_oauth_token(self, broker: str, token_data: Dict) -> Dict:
        """Process and store OAuth token data"""
        # Implement token processing and storage
        return {
            'type': 'oauth',
            'access_token': token_data.get('access_token'),
            'expires_at': (datetime.now() + timedelta(seconds=token_data.get('expires_in', 3600))).isoformat()
        }

    def _validate_manual_credentials(self, broker: str, credentials: Dict) -> bool:
        """Validate manual login credentials"""
        # Implement credential validation
        return True

    async def _store_manual_session(self, session: Dict):
        """Store manual session data"""
        # Implement session storage
        pass

    async def _verify_oauth_session(self, broker: str, session_data: Dict) -> bool:
        """Verify OAuth session validity"""
        # Implement OAuth session verification
        return True

    async def _verify_manual_session(self, broker: str, session_data: Dict) -> bool:
        """Verify manual session validity"""
        # Implement manual session verification
        return True

    async def _refresh_oauth_session(self, broker: str, session_data: Dict) -> Optional[Dict]:
        """Refresh OAuth session"""
        # Implement OAuth session refresh
        return None

    async def _refresh_manual_session(self, broker: str, session_data: Dict) -> Optional[Dict]:
        """Refresh manual session"""
        # Implement manual session refresh
        return None

# Initialize global broker auth
broker_auth = BrokerAuth()
