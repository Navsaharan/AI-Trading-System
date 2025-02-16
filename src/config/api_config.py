from typing import Dict, Optional
import os
from dataclasses import dataclass
import json
from cryptography.fernet import Fernet

@dataclass
class APIConfig:
    # Authentication & Communication
    FIREBASE_CONFIG: Dict
    TWILIO_CONFIG: Dict
    SENDGRID_CONFIG: Dict
    
    # Trading APIs
    BINANCE_CONFIG: Dict
    ZERODHA_CONFIG: Dict
    UPSTOX_CONFIG: Dict
    ANGELONE_CONFIG: Dict
    
    # AI Services
    OPENAI_CONFIG: Dict
    HUGGINGFACE_CONFIG: Dict
    COHERE_CONFIG: Dict
    
    # Market Data
    ALPHA_VANTAGE_CONFIG: Dict
    YAHOO_FINANCE_CONFIG: Dict
    TRADING_VIEW_CONFIG: Dict
    
    # Database
    MONGODB_CONFIG: Dict
    REDIS_CONFIG: Dict
    POSTGRESQL_CONFIG: Dict

class APIConfigManager:
    def __init__(self):
        self.config_file = "api_keys.json"
        self.key_file = "encryption.key"
        self._load_or_create_key()
        self.fernet = Fernet(self.encryption_key)
        self.config = self._load_config()

    def _load_or_create_key(self):
        """Load existing encryption key or create new one"""
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as f:
                self.encryption_key = f.read()
        else:
            self.encryption_key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(self.encryption_key)

    def _load_config(self) -> APIConfig:
        """Load and decrypt API configuration"""
        default_config = {
            # Authentication & Communication
            "FIREBASE_CONFIG": {
                "apiKey": "",
                "authDomain": "",
                "projectId": "",
                "storageBucket": "",
                "messagingSenderId": "",
                "appId": ""
            },
            "TWILIO_CONFIG": {
                "account_sid": "",
                "auth_token": "",
                "phone_number": ""
            },
            "SENDGRID_CONFIG": {
                "api_key": "",
                "from_email": ""
            },
            
            # Trading APIs
            "BINANCE_CONFIG": {
                "api_key": "",
                "api_secret": "",
                "testnet": True
            },
            "ZERODHA_CONFIG": {
                "api_key": "",
                "api_secret": "",
                "user_id": ""
            },
            "UPSTOX_CONFIG": {
                "api_key": "",
                "api_secret": "",
                "redirect_uri": ""
            },
            "ANGELONE_CONFIG": {
                "api_key": "",
                "client_code": "",
                "pin": ""
            },
            
            # AI Services
            "OPENAI_CONFIG": {
                "api_key": "",
                "organization": ""
            },
            "HUGGINGFACE_CONFIG": {
                "api_key": "",
                "model_endpoint": ""
            },
            "COHERE_CONFIG": {
                "api_key": "",
                "model_name": ""
            },
            
            # Market Data
            "ALPHA_VANTAGE_CONFIG": {
                "api_key": "",
                "premium": False
            },
            "YAHOO_FINANCE_CONFIG": {
                "api_key": "",
                "premium": False
            },
            "TRADING_VIEW_CONFIG": {
                "username": "",
                "password": ""
            },
            
            # Database
            "MONGODB_CONFIG": {
                "uri": "",
                "database": ""
            },
            "REDIS_CONFIG": {
                "host": "",
                "port": "",
                "password": ""
            },
            "POSTGRESQL_CONFIG": {
                "host": "",
                "port": "",
                "database": "",
                "user": "",
                "password": ""
            }
        }

        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                encrypted_config = json.load(f)
                decrypted_config = self._decrypt_config(encrypted_config)
                # Merge with default config to ensure all fields exist
                for key in default_config:
                    if key not in decrypted_config:
                        decrypted_config[key] = default_config[key]
                return APIConfig(**decrypted_config)
        return APIConfig(**default_config)

    def save_config(self, config: Dict):
        """Encrypt and save API configuration"""
        encrypted_config = self._encrypt_config(config)
        with open(self.config_file, 'w') as f:
            json.dump(encrypted_config, f, indent=4)
        self.config = APIConfig(**config)

    def _encrypt_config(self, config: Dict) -> Dict:
        """Encrypt sensitive configuration data"""
        encrypted = {}
        for key, value in config.items():
            if isinstance(value, dict):
                encrypted[key] = self._encrypt_config(value)
            elif isinstance(value, str) and value:
                encrypted[key] = self.fernet.encrypt(value.encode()).decode()
            else:
                encrypted[key] = value
        return encrypted

    def _decrypt_config(self, config: Dict) -> Dict:
        """Decrypt sensitive configuration data"""
        decrypted = {}
        for key, value in config.items():
            if isinstance(value, dict):
                decrypted[key] = self._decrypt_config(value)
            elif isinstance(value, str) and value:
                try:
                    decrypted[key] = self.fernet.decrypt(value.encode()).decode()
                except:
                    decrypted[key] = value
            else:
                decrypted[key] = value
        return decrypted

    def get_config(self, service: str) -> Optional[Dict]:
        """Get configuration for specific service"""
        return getattr(self.config, f"{service}_CONFIG", None)

    def update_config(self, service: str, config: Dict):
        """Update configuration for specific service"""
        current_config = vars(self.config)
        current_config[f"{service}_CONFIG"] = config
        self.save_config(current_config)

    def validate_config(self, service: str) -> bool:
        """Validate service configuration"""
        config = self.get_config(service)
        if not config:
            return False
            
        # Check if all required fields have values
        required_fields = {
            "FIREBASE": ["apiKey", "authDomain", "projectId"],
            "TWILIO": ["account_sid", "auth_token"],
            "SENDGRID": ["api_key"],
            "BINANCE": ["api_key", "api_secret"],
            "ZERODHA": ["api_key", "api_secret"],
            "OPENAI": ["api_key"],
            "HUGGINGFACE": ["api_key"],
            "COHERE": ["api_key"],
            "ALPHA_VANTAGE": ["api_key"],
            "MONGODB": ["uri"],
            "REDIS": ["host", "port"],
            "POSTGRESQL": ["host", "database", "user", "password"]
        }
        
        if service in required_fields:
            return all(field in config and config[field] for field in required_fields[service])
        return True

# Initialize API configuration manager
api_config = APIConfigManager()
