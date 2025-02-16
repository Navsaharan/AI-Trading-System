import os
import sys
import asyncio
from datetime import datetime
import logging
from ..core.trading_engine import TradingEngine
from ..core.risk_manager import RiskManager
from .auto_trader import AutoTrader

logger = logging.getLogger(__name__)

async def emergency_stop():
    """Emergency stop all trading activities."""
    try:
        # Initialize components
        trading_engine = TradingEngine()
        risk_manager = RiskManager()
        auto_trader = AutoTrader(trading_engine, risk_manager)
        
        logger.warning("INITIATING EMERGENCY STOP!")
        
        # Stop auto trader with emergency flag
        await auto_trader.stop(emergency=True)
        
        # Log the emergency stop
        with open('logs/emergency_stops.log', 'a') as f:
            f.write(f"{datetime.now()}: Emergency stop initiated\n")
            
        logger.info("Emergency stop completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to execute emergency stop: {str(e)}")
        return False

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run emergency stop
    asyncio.run(emergency_stop())
