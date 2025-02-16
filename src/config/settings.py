import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project name and version
PROJECT_NAME = "FamilyHVSDN"
VERSION = "1.0.0"

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Environment
ENV = os.getenv("ENV", "development")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# API Settings
API_V1_STR = "/api/v1"
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", f"postgresql://user:password@localhost/familyhvsdn_db")

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Firebase
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")
FIREBASE_PRIVATE_KEY = os.getenv("FIREBASE_PRIVATE_KEY")
FIREBASE_CLIENT_EMAIL = os.getenv("FIREBASE_CLIENT_EMAIL")

# Trading Settings
MAX_DAILY_LOSS = float(os.getenv("MAX_DAILY_LOSS", "0.02"))  # 2%
MAX_POSITION_SIZE = float(os.getenv("MAX_POSITION_SIZE", "0.05"))  # 5%
MIN_WIN_RATE = float(os.getenv("MIN_WIN_RATE", "0.40"))  # 40%

# Broker Settings
BROKER = os.getenv("BROKER", "angelone")
BROKER_API_KEY = os.getenv("BROKER_API_KEY")
BROKER_CLIENT_ID = os.getenv("BROKER_CLIENT_ID")
BROKER_CLIENT_SECRET = os.getenv("BROKER_CLIENT_SECRET")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Email
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# Monitoring
ENABLE_MONITORING = os.getenv("ENABLE_MONITORING", "True").lower() == "true"
MONITORING_INTERVAL = int(os.getenv("MONITORING_INTERVAL", "60"))  # seconds

# AI Model Settings
MODEL_UPDATE_FREQUENCY = os.getenv("MODEL_UPDATE_FREQUENCY", "daily")
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.75"))

# Paths
LOGS_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Create necessary directories
LOGS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)
