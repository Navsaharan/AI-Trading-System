import asyncio
import uvicorn
from api.main import app
from database.init_db import init_database
import logging
from pathlib import Path
import os

# Project name
PROJECT_NAME = 'FamilyHVSDN'

# Configure logging
log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/trading.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def startup():
    """Initialize the application."""
    try:
        logger.info(f"Starting {PROJECT_NAME} Trading System...")
        
        # Initialize database
        await init_database()
        logger.info("Database initialized successfully")
        
        # Initialize other components
        # TODO: Add other initialization steps
        
        logger.info(f"{PROJECT_NAME} Trading System started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start {PROJECT_NAME}: {str(e)}")
        raise

def main():
    """Main entry point for the application."""
    try:
        # Run startup tasks
        asyncio.run(startup())
        
        # Start the application
        port = int(os.getenv('PORT', 8000))
        debug = os.getenv('DEBUG', 'False').lower() == 'true'
        
        # Run the FastAPI application
        uvicorn.run(
            "api.main:app",
            host="0.0.0.0",
            port=port,
            reload=debug,
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
