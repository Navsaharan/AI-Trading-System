from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config.settings import DATABASE_URL

def init_database():
    """Initialize the database and create all tables."""
    try:
        # Create database engine
        engine = create_engine(DATABASE_URL)
        
        # Create all tables
        Base.metadata.create_all(engine)
        
        # Create session factory
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        print("Database initialized successfully!")
        return engine, SessionLocal
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        raise

if __name__ == "__main__":
    init_database()
