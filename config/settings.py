from pathlib import Path
from typing import Dict, List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Security settings
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Database settings
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./trading.db')

# Redis settings for caching and Celery
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Supported brokers configuration
SUPPORTED_BROKERS = {
    'upstox': {
        'class': 'brokers.upstox.UpstoxBroker',
        'api_version': 'v2',
        'base_url': 'https://api.upstox.com/v2/',
    },
    'zerodha': {
        'class': 'brokers.zerodha.ZerodhaBroker',
        'api_version': 'v3',
        'base_url': 'https://api.kite.trade/',
    },
    'angelone': {
        'class': 'brokers.angelone.AngelOneBroker',
        'api_version': 'v1',
        'base_url': 'https://apiconnect.angelbroking.com/',
    },
    'binance': {
        'class': 'brokers.binance.BinanceBroker',
        'api_version': 'v3',
        'base_url': 'https://api.binance.com/',
    }
}

# Trading settings
TRADING_SETTINGS = {
    'default_risk_level': 'medium',
    'max_position_size': 0.1,  # 10% of portfolio
    'stop_loss_default': 0.02,  # 2%
    'take_profit_default': 0.04,  # 4%
    'max_trades_per_day': 10,
    'trading_hours': {
        'start': '09:15',
        'end': '15:30',
    }
}

# AI Model settings
AI_SETTINGS = {
    'model_update_frequency': 24,  # hours
    'min_confidence_threshold': 0.7,
    'sentiment_sources': ['twitter', 'reddit', 'news'],
    'technical_indicators': [
        'SMA', 'EMA', 'RSI', 'MACD', 'Bollinger_Bands',
        'Volume', 'OBV', 'ATR', 'ADX'
    ]
}

# Asset class settings
ASSET_CLASSES = {
    'stocks': {
        'enabled': True,
        'min_capital': 500,
        'max_leverage': 1,
    },
    'futures': {
        'enabled': True,
        'min_capital': 1000,
        'max_leverage': 2,
    },
    'options': {
        'enabled': True,
        'min_capital': 1000,
        'max_leverage': 1,
    },
    'crypto': {
        'enabled': True,
        'min_capital': 100,
        'max_leverage': 2,
    },
    'forex': {
        'enabled': True,
        'min_capital': 1000,
        'max_leverage': 3,
    }
}

# API rate limiting
RATE_LIMIT = {
    'default': '100/minute',
    'trading': '10/minute',
    'market_data': '1000/minute',
}

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs/trading.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}
