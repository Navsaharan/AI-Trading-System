from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import os
from dotenv import load_dotenv

load_dotenv()

# Default database URL if not specified in environment
DATABASE_URL = os.getenv('DATABASE_URL', "postgresql://user:password@localhost/familyhvsdn_db")

# Database configuration
DATABASE_CONFIG = {
    'pool_size': int(os.getenv('DB_POOL_SIZE', 5)),
    'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', 10)),
    'pool_timeout': int(os.getenv('DB_POOL_TIMEOUT', 30)),
    'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', 1800)),
}

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    **DATABASE_CONFIG
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
