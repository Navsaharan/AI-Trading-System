from typing import Dict, List, Optional
from dataclasses import dataclass
import json
import os
from datetime import datetime, timedelta
import asyncio
import aiohttp
from cryptography.fernet import Fernet
import base64
from enum import Enum
import logging
import boto3
from google.cloud import storage
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_platform_services import ResourceControllerV2
import oci
from binance.client import Client as BinanceClient
from coinbase.wallet.client import Client as CoinbaseClient
import yfinance as yf
import pandas as pd
import requests
import tweepy
import praw
from fredapi import Fred
import wbgapi as wb
from ratelimit import limits, sleep_and_retry

class APIType(Enum):
    BROKER = "broker"
    EXCHANGE = "exchange"
    DATA_PROVIDER = "data_provider"
    PERSONAL = "personal"

class RefreshInterval(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    NEVER = "never"

@dataclass
class APICredential:
    id: str
    user_id: str
    name: str
    api_type: APIType
    credentials: Dict
    refresh_interval: RefreshInterval
    last_refresh: datetime
    is_active: bool
    created_at: datetime
    updated_at: datetime
    encrypted: bool

class APIManagementService:
    def __init__(self):
        self.credentials_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'credentials')
        os.makedirs(self.credentials_dir, exist_ok=True)
        self.encryption_key = self._load_or_generate_key()
        self.fernet = Fernet(self.encryption_key)
        self.api_manager = APIManager()

    async def add_api_credentials(self, user_id: str, credentials: Dict) -> APICredential:
        """Add new API credentials"""
        try:
            # Validate credentials
            if not self._validate_credentials(credentials):
                raise ValueError("Invalid credentials format")
            
            # Create credential object
            api_cred = APICredential(
                id=self._generate_id(),
                user_id=user_id,
                name=credentials["name"],
                api_type=APIType(credentials["type"]),
                credentials=self._encrypt_credentials(credentials["credentials"]),
                refresh_interval=RefreshInterval(credentials.get("refresh_interval", "never")),
                last_refresh=datetime.now(),
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                encrypted=True
            )
            
            # Save credentials
            await self._save_credentials(api_cred)
            
            return api_cred

        except Exception as e:
            print(f"Error adding API credentials: {e}")
            return None

    async def get_user_credentials(self, user_id: str) -> List[APICredential]:
        """Get all API credentials for a user"""
        try:
            credentials = []
            cred_files = os.listdir(self.credentials_dir)
            
            for file in cred_files:
                if file.startswith(f"cred_{user_id}_"):
                    cred = await self._load_credentials_from_file(file)
                    if cred:
                        credentials.append(cred)
            
            return credentials

        except Exception as e:
            print(f"Error getting user credentials: {e}")
            return []

    async def update_credentials(self, cred_id: str, updates: Dict) -> APICredential:
        """Update existing API credentials"""
        try:
            # Load existing credentials
            cred = await self._load_credentials(cred_id)
            if not cred:
                return None
            
            # Apply updates
            if "name" in updates:
                cred.name = updates["name"]
            if "credentials" in updates:
                cred.credentials = self._encrypt_credentials(updates["credentials"])
            if "refresh_interval" in updates:
                cred.refresh_interval = RefreshInterval(updates["refresh_interval"])
            if "is_active" in updates:
                cred.is_active = updates["is_active"]
            
            cred.updated_at = datetime.now()
            
            # Save updated credentials
            await self._save_credentials(cred)
            
            return cred

        except Exception as e:
            print(f"Error updating credentials: {e}")
            return None

    async def refresh_credentials(self, cred_id: str) -> bool:
        """Refresh API credentials"""
        try:
            # Load credentials
            cred = await self._load_credentials(cred_id)
            if not cred:
                return False
            
            # Check if refresh is needed
            if not self._needs_refresh(cred):
                return True
            
            # Get new credentials
            new_creds = await self._get_new_credentials(cred)
            if not new_creds:
                return False
            
            # Update credentials
            cred.credentials = self._encrypt_credentials(new_creds)
            cred.last_refresh = datetime.now()
            cred.updated_at = datetime.now()
            
            # Save updated credentials
            await self._save_credentials(cred)
            
            return True

        except Exception as e:
            print(f"Error refreshing credentials: {e}")
            return False

    async def validate_credentials(self, cred_id: str) -> bool:
        """Validate API credentials"""
        try:
            # Load credentials
            cred = await self._load_credentials(cred_id)
            if not cred:
                return False
            
            # Decrypt credentials
            decrypted = self._decrypt_credentials(cred.credentials)
            
            # Test API connection
            valid = await self._test_api_connection(cred.api_type, decrypted)
            
            return valid

        except Exception as e:
            print(f"Error validating credentials: {e}")
            return False

    async def auto_refresh_all(self) -> Dict[str, bool]:
        """Auto-refresh all credentials that need refreshing"""
        try:
            results = {}
            cred_files = os.listdir(self.credentials_dir)
            
            for file in cred_files:
                cred = await self._load_credentials_from_file(file)
                if cred and self._needs_refresh(cred):
                    success = await self.refresh_credentials(cred.id)
                    results[cred.id] = success
            
            return results

        except Exception as e:
            print(f"Error in auto-refresh: {e}")
            return {}

    def _encrypt_credentials(self, credentials: Dict) -> Dict:
        """Encrypt sensitive credential data"""
        try:
            encrypted = {}
            for key, value in credentials.items():
                if isinstance(value, str):
                    encrypted[key] = self.fernet.encrypt(value.encode()).decode()
                else:
                    encrypted[key] = value
            return encrypted

        except Exception as e:
            print(f"Error encrypting credentials: {e}")
            return credentials

    def _decrypt_credentials(self, credentials: Dict) -> Dict:
        """Decrypt sensitive credential data"""
        try:
            decrypted = {}
            for key, value in credentials.items():
                if isinstance(value, str):
                    try:
                        decrypted[key] = self.fernet.decrypt(value.encode()).decode()
                    except:
                        decrypted[key] = value
                else:
                    decrypted[key] = value
            return decrypted

        except Exception as e:
            print(f"Error decrypting credentials: {e}")
            return credentials

    def _needs_refresh(self, cred: APICredential) -> bool:
        """Check if credentials need refreshing"""
        if cred.refresh_interval == RefreshInterval.NEVER:
            return False
            
        now = datetime.now()
        last_refresh = cred.last_refresh
        
        if cred.refresh_interval == RefreshInterval.DAILY:
            return (now - last_refresh) > timedelta(days=1)
        elif cred.refresh_interval == RefreshInterval.WEEKLY:
            return (now - last_refresh) > timedelta(days=7)
        elif cred.refresh_interval == RefreshInterval.MONTHLY:
            return (now - last_refresh) > timedelta(days=30)
        
        return False

    async def _get_new_credentials(self, cred: APICredential) -> Optional[Dict]:
        """Get new credentials from provider"""
        try:
            # Implement provider-specific refresh logic
            if cred.api_type == APIType.BROKER:
                return await self._refresh_broker_credentials(cred)
            elif cred.api_type == APIType.EXCHANGE:
                return await self._refresh_exchange_credentials(cred)
            elif cred.api_type == APIType.DATA_PROVIDER:
                return await self._refresh_data_provider_credentials(cred)
            
            return None

        except Exception as e:
            print(f"Error getting new credentials: {e}")
            return None

    async def _test_api_connection(self, api_type: APIType, credentials: Dict) -> bool:
        """Test API connection with credentials"""
        try:
            # Implement provider-specific connection testing
            if api_type == APIType.BROKER:
                return await self._test_broker_connection(credentials)
            elif api_type == APIType.EXCHANGE:
                return await self._test_exchange_connection(credentials)
            elif api_type == APIType.DATA_PROVIDER:
                return await self._test_data_provider_connection(credentials)
            
            return False

        except Exception as e:
            print(f"Error testing API connection: {e}")
            return False

    def _load_or_generate_key(self) -> bytes:
        """Load or generate encryption key"""
        key_file = os.path.join(self.credentials_dir, 'encryption.key')
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return base64.urlsafe_b64decode(f.read())
        
        key = Fernet.generate_key()
        with open(key_file, 'wb') as f:
            f.write(base64.urlsafe_b64encode(key))
        
        return key

    def _validate_credentials(self, credentials: Dict) -> bool:
        """Validate credentials format"""
        required_fields = ["name", "type", "credentials"]
        return all(field in credentials for field in required_fields)

    def _generate_id(self) -> str:
        """Generate unique ID"""
        return f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{os.urandom(4).hex()}"

    async def _save_credentials(self, cred: APICredential) -> bool:
        """Save credentials to file"""
        try:
            file_path = os.path.join(
                self.credentials_dir,
                f"cred_{cred.user_id}_{cred.id}.json"
            )
            
            with open(file_path, 'w') as f:
                json.dump(cred.__dict__, f, indent=4, default=str)
            
            return True

        except Exception as e:
            print(f"Error saving credentials: {e}")
            return False

    async def _load_credentials(self, cred_id: str) -> Optional[APICredential]:
        """Load credentials from file"""
        try:
            cred_files = os.listdir(self.credentials_dir)
            
            for file in cred_files:
                if cred_id in file:
                    return await self._load_credentials_from_file(file)
            
            return None

        except Exception as e:
            print(f"Error loading credentials: {e}")
            return None

class APIManager:
    def __init__(self):
        self.initialize_service()
        self.setup_logging()
        self.initialize_clients()
        
    def initialize_service(self):
        """Initialize API management service"""
        try:
            self.key = self._load_or_create_key()
            self.cipher = Fernet(self.key)
            self.api_keys = self._load_api_keys()
            self.setup_rate_limits()
            logging.info("API management service initialized")
        except Exception as e:
            logging.error(f"Error initializing API service: {e}")
            raise

    def initialize_clients(self):
        """Initialize API clients for various services"""
        try:
            # Cloud Providers
            self.cloud_clients = {
                "oracle": self._init_oracle_client(),
                "google": self._init_google_client(),
                "aws": self._init_aws_client(),
                "azure": self._init_azure_client(),
                "ibm": self._init_ibm_client()
            }
            
            # Trading APIs
            self.trading_clients = {
                "binance": self._init_binance_client(),
                "coinbase": self._init_coinbase_client(),
                "yahoo": self._init_yahoo_client()
            }
            
            # News APIs
            self.news_clients = {
                "twitter": self._init_twitter_client(),
                "reddit": self._init_reddit_client()
            }
            
            # Economic APIs
            self.economic_clients = {
                "fred": self._init_fred_client(),
                "world_bank": self._init_worldbank_client()
            }
            
            logging.info("API clients initialized")
        except Exception as e:
            logging.error(f"Error initializing API clients: {e}")
            raise

    def _init_oracle_client(self) -> oci.identity.IdentityClient:
        """Initialize Oracle Cloud client"""
        config = self.api_keys["cloud_providers"]["oracle"]
        return oci.identity.IdentityClient(config)

    def _init_google_client(self) -> storage.Client:
        """Initialize Google Cloud client"""
        config = self.api_keys["cloud_providers"]["google_cloud"]
        return storage.Client.from_service_account_info(config)

    def _init_aws_client(self) -> boto3.Session:
        """Initialize AWS client"""
        config = self.api_keys["cloud_providers"]["aws"]
        return boto3.Session(
            aws_access_key_id=config["access_key_id"],
            aws_secret_access_key=config["secret_access_key"],
            region_name=config["region"]
        )

    def _init_azure_client(self) -> SecretClient:
        """Initialize Azure client"""
        config = self.api_keys["cloud_providers"]["azure"]
        credential = DefaultAzureCredential()
        return SecretClient(
            vault_url=f"https://{config['vault_name']}.vault.azure.net/",
            credential=credential
        )

    def _init_ibm_client(self) -> ResourceControllerV2:
        """Initialize IBM Cloud client"""
        config = self.api_keys["cloud_providers"]["ibm_cloud"]
        authenticator = IAMAuthenticator(config["api_key"])
        return ResourceControllerV2(authenticator=authenticator)

    def _init_binance_client(self) -> BinanceClient:
        """Initialize Binance client"""
        config = self.api_keys["trading_apis"]["binance"]
        return BinanceClient(config["api_key"], config["api_secret"])

    def _init_coinbase_client(self) -> CoinbaseClient:
        """Initialize Coinbase client"""
        config = self.api_keys["trading_apis"]["coinbase"]
        return CoinbaseClient(config["api_key"], config["api_secret"])

    def _init_yahoo_client(self) -> yf.Ticker:
        """Initialize Yahoo Finance client"""
        return yf

    def _init_twitter_client(self) -> tweepy.API:
        """Initialize Twitter client"""
        config = self.api_keys["news_apis"]["twitter"]
        auth = tweepy.OAuthHandler(
            config["api_key"],
            config["api_secret"]
        )
        auth.set_access_token(
            config["access_token"],
            config["access_secret"]
        )
        return tweepy.API(auth)

    def _init_reddit_client(self) -> praw.Reddit:
        """Initialize Reddit client"""
        config = self.api_keys["news_apis"]["reddit"]
        return praw.Reddit(
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            user_agent="trading_system"
        )

    def _init_fred_client(self) -> Fred:
        """Initialize FRED client"""
        config = self.api_keys["economic_apis"]["fred"]
        return Fred(api_key=config["api_key"])

    def _init_worldbank_client(self) -> wb:
        """Initialize World Bank client"""
        return wb

    @sleep_and_retry
    @limits(calls=100, period=60)
    async def make_api_request(self, api_name: str, endpoint: str, method: str = "GET", **kwargs) -> Dict:
        """Make rate-limited API request"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(method, endpoint, **kwargs) as response:
                    if response.status == 429:  # Rate limit exceeded
                        retry_after = int(response.headers.get("Retry-After", 60))
                        await asyncio.sleep(retry_after)
                        return await self.make_api_request(api_name, endpoint, method, **kwargs)
                    
                    response.raise_for_status()
                    return await response.json()
                    
        except Exception as e:
            logging.error(f"Error making API request to {api_name}: {e}")
            raise

    def get_cloud_client(self, provider: str) -> Any:
        """Get cloud provider client"""
        return self.cloud_clients.get(provider)

    def get_trading_client(self, exchange: str) -> Any:
        """Get trading API client"""
        return self.trading_clients.get(exchange)

    def get_news_client(self, source: str) -> Any:
        """Get news API client"""
        return self.news_clients.get(source)

    def get_economic_client(self, source: str) -> Any:
        """Get economic data client"""
        return self.economic_clients.get(source)

    def _load_or_create_key(self) -> bytes:
        """Load or create encryption key"""
        key_file = "config/encryption.key"
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)
            return key

    def _load_api_keys(self) -> Dict:
        """Load and decrypt API keys"""
        with open("config/api_keys.json", "r") as f:
            encrypted_keys = json.load(f)
        return self._decrypt_keys(encrypted_keys)

    def _encrypt_keys(self, keys: Dict) -> Dict:
        """Encrypt API keys"""
        encrypted = {}
        for category, apis in keys.items():
            encrypted[category] = {}
            for api, config in apis.items():
                encrypted[category][api] = {
                    k: self.cipher.encrypt(str(v).encode()).decode()
                    for k, v in config.items()
                }
        return encrypted

    def _decrypt_keys(self, encrypted_keys: Dict) -> Dict:
        """Decrypt API keys"""
        decrypted = {}
        for category, apis in encrypted_keys.items():
            decrypted[category] = {}
            for api, config in apis.items():
                decrypted[category][api] = {
                    k: self.cipher.decrypt(v.encode()).decode()
                    for k, v in config.items()
                }
        return decrypted

    def rotate_api_keys(self, category: str, api: str):
        """Rotate API keys for security"""
        try:
            if category == "cloud_providers":
                self._rotate_cloud_provider_keys(api)
            elif category == "trading_apis":
                self._rotate_trading_api_keys(api)
            elif category == "news_apis":
                self._rotate_news_api_keys(api)
            elif category == "economic_apis":
                self._rotate_economic_api_keys(api)
                
            logging.info(f"Rotated keys for {category}.{api}")
            
        except Exception as e:
            logging.error(f"Error rotating keys for {category}.{api}: {e}")
            raise

    def monitor_api_usage(self):
        """Monitor API usage and limits"""
        try:
            usage = {}
            for category, apis in self.api_keys.items():
                usage[category] = {}
                for api in apis:
                    usage[category][api] = self._get_api_usage(category, api)
            
            return usage
            
        except Exception as e:
            logging.error(f"Error monitoring API usage: {e}")
            return {}

    def validate_api_keys(self):
        """Validate all API keys"""
        try:
            invalid_keys = []
            for category, apis in self.api_keys.items():
                for api in apis:
                    if not self._validate_api_key(category, api):
                        invalid_keys.append(f"{category}.{api}")
            
            return invalid_keys
            
        except Exception as e:
            logging.error(f"Error validating API keys: {e}")
            return []

# Initialize API manager
api_manager = APIManager()
