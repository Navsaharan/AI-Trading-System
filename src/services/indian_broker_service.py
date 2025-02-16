from typing import Dict, Optional
import logging
from kiteconnect import KiteConnect
from smartapi import SmartConnect
from upstox_api.api import Upstox
from py5paisa import FivePaisaClient
import pyotp
import json
import os
from cryptography.fernet import Fernet

class IndianBrokerService:
    def __init__(self):
        self.initialize_service()
        self.setup_logging()
        
    def initialize_service(self):
        """Initialize broker service"""
        try:
            self.key = self._load_or_create_key()
            self.cipher = Fernet(self.key)
            self.brokers = {}
            self.load_credentials()
            logging.info("Indian broker service initialized")
        except Exception as e:
            logging.error(f"Error initializing broker service: {e}")
            raise

    def load_credentials(self):
        """Load broker credentials"""
        try:
            creds_file = "config/broker_credentials.json"
            if os.path.exists(creds_file):
                with open(creds_file, "r") as f:
                    encrypted_creds = json.load(f)
                    self.credentials = self._decrypt_credentials(encrypted_creds)
            else:
                self.credentials = {}
        except Exception as e:
            logging.error(f"Error loading credentials: {e}")
            self.credentials = {}

    def save_credentials(self, broker: str, credentials: Dict):
        """Save broker credentials"""
        try:
            # Validate credentials
            self._validate_credentials(broker, credentials)
            
            # Encrypt credentials
            self.credentials[broker] = credentials
            encrypted_creds = self._encrypt_credentials(self.credentials)
            
            # Save to file
            with open("config/broker_credentials.json", "w") as f:
                json.dump(encrypted_creds, f, indent=4)
                
            # Initialize broker connection
            self._initialize_broker(broker, credentials)
            
            logging.info(f"Saved credentials for {broker}")
            return True
            
        except Exception as e:
            logging.error(f"Error saving credentials for {broker}: {e}")
            return False

    def _initialize_broker(self, broker: str, credentials: Dict):
        """Initialize broker connection"""
        try:
            if broker == "zerodha":
                self.brokers[broker] = self._init_zerodha(credentials)
            elif broker == "angel":
                self.brokers[broker] = self._init_angel(credentials)
            elif broker == "upstox":
                self.brokers[broker] = self._init_upstox(credentials)
            elif broker == "5paisa":
                self.brokers[broker] = self._init_5paisa(credentials)
            elif broker == "iifl":
                self.brokers[broker] = self._init_iifl(credentials)
                
            logging.info(f"Initialized {broker} connection")
            
        except Exception as e:
            logging.error(f"Error initializing {broker}: {e}")
            raise

    def _init_zerodha(self, credentials: Dict) -> KiteConnect:
        """Initialize Zerodha connection"""
        try:
            kite = KiteConnect(api_key=credentials["apiKey"])
            
            # Generate session
            if "accessToken" not in credentials:
                credentials["accessToken"] = self._generate_zerodha_session(
                    kite, credentials
                )
                self.save_credentials("zerodha", credentials)
            
            kite.set_access_token(credentials["accessToken"])
            return kite
            
        except Exception as e:
            logging.error(f"Error initializing Zerodha: {e}")
            raise

    def _init_angel(self, credentials: Dict) -> SmartConnect:
        """Initialize Angel Broking connection"""
        try:
            angel = SmartConnect(
                api_key=credentials["apiKey"]
            )
            
            # Generate session
            session = angel.generateSession(
                credentials["clientCode"],
                credentials["apiSecret"]
            )
            
            angel.getProfile(session['data']['jwtToken'])
            return angel
            
        except Exception as e:
            logging.error(f"Error initializing Angel: {e}")
            raise

    def _init_upstox(self, credentials: Dict) -> Upstox:
        """Initialize Upstox connection"""
        try:
            upstox = Upstox(
                credentials["apiKey"],
                credentials["apiSecret"]
            )
            
            if "accessToken" not in credentials:
                credentials["accessToken"] = self._generate_upstox_session(
                    upstox, credentials
                )
                self.save_credentials("upstox", credentials)
            
            upstox.set_token(credentials["accessToken"])
            return upstox
            
        except Exception as e:
            logging.error(f"Error initializing Upstox: {e}")
            raise

    def _init_5paisa(self, credentials: Dict) -> FivePaisaClient:
        """Initialize 5paisa connection"""
        try:
            client = FivePaisaClient(
                email=credentials["email"],
                passwd=credentials["password"],
                dob=credentials["dob"],
                app_name=credentials["appName"],
                app_source=credentials["appSource"]
            )
            client.login()
            return client
            
        except Exception as e:
            logging.error(f"Error initializing 5paisa: {e}")
            raise

    def _validate_credentials(self, broker: str, credentials: Dict):
        """Validate broker credentials"""
        required_fields = {
            "zerodha": ["apiKey", "apiSecret", "userId"],
            "angel": ["apiKey", "apiSecret", "clientCode"],
            "upstox": ["apiKey", "apiSecret", "redirectUri"],
            "5paisa": ["appName", "appSource", "email", "password", "dob"],
            "iifl": ["apiKey", "apiSecret", "userId"]
        }
        
        if broker not in required_fields:
            raise ValueError(f"Unsupported broker: {broker}")
            
        missing_fields = [
            field for field in required_fields[broker]
            if field not in credentials
        ]
        
        if missing_fields:
            raise ValueError(
                f"Missing required fields for {broker}: {missing_fields}"
            )

    def _encrypt_credentials(self, credentials: Dict) -> Dict:
        """Encrypt broker credentials"""
        encrypted = {}
        for broker, creds in credentials.items():
            encrypted[broker] = {
                k: self.cipher.encrypt(str(v).encode()).decode()
                for k, v in creds.items()
            }
        return encrypted

    def _decrypt_credentials(self, encrypted_creds: Dict) -> Dict:
        """Decrypt broker credentials"""
        decrypted = {}
        for broker, creds in encrypted_creds.items():
            decrypted[broker] = {
                k: self.cipher.decrypt(v.encode()).decode()
                for k, v in creds.items()
            }
        return decrypted

    def _load_or_create_key(self) -> bytes:
        """Load or create encryption key"""
        key_file = "config/broker_key.key"
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)
            return key

    def get_broker(self, broker: str):
        """Get broker instance"""
        return self.brokers.get(broker)

    def get_positions(self, broker: str) -> Dict:
        """Get positions for specified broker"""
        try:
            broker_instance = self.get_broker(broker)
            if not broker_instance:
                raise ValueError(f"Broker not initialized: {broker}")
                
            if broker == "zerodha":
                return broker_instance.positions()
            elif broker == "angel":
                return broker_instance.position()
            elif broker == "upstox":
                return broker_instance.get_positions()
            elif broker == "5paisa":
                return broker_instance.positions()
                
        except Exception as e:
            logging.error(f"Error getting positions for {broker}: {e}")
            return {}

    def place_order(self, broker: str, order: Dict) -> Dict:
        """Place order with specified broker"""
        try:
            broker_instance = self.get_broker(broker)
            if not broker_instance:
                raise ValueError(f"Broker not initialized: {broker}")
                
            if broker == "zerodha":
                return broker_instance.place_order(
                    variety=order.get("variety", "regular"),
                    exchange=order["exchange"],
                    tradingsymbol=order["symbol"],
                    transaction_type=order["transaction_type"],
                    quantity=order["quantity"],
                    price=order.get("price", 0),
                    product=order.get("product", "CNC"),
                    order_type=order.get("order_type", "MARKET")
                )
            elif broker == "angel":
                return broker_instance.placeOrder(order)
            elif broker == "upstox":
                return broker_instance.place_order(
                    quantity=order["quantity"],
                    symbol=order["symbol"],
                    side=order["transaction_type"],
                    order_type=order.get("order_type", "MARKET"),
                    product=order.get("product", "CNC")
                )
            elif broker == "5paisa":
                return broker_instance.place_order(
                    order_type=order.get("order_type", "MARKET"),
                    exchange=order["exchange"],
                    symbol=order["symbol"],
                    quantity=order["quantity"],
                    side=order["transaction_type"],
                    price=order.get("price", 0)
                )
                
        except Exception as e:
            logging.error(f"Error placing order with {broker}: {e}")
            return {"status": "error", "message": str(e)}

# Initialize broker service
broker_service = IndianBrokerService()
