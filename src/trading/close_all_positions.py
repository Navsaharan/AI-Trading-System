import os
import sys
import asyncio
from datetime import datetime
import logging
from ..core.trading_engine import TradingEngine
from ..core.risk_manager import RiskManager
from .auto_trader import AutoTrader

logger = logging.getLogger(__name__)

async def close_all_positions():
    """Close all open trading positions."""
    try:
        # Initialize components
        trading_engine = TradingEngine()
        risk_manager = RiskManager()
        auto_trader = AutoTrader(trading_engine, risk_manager)
        
        logger.info("Closing all positions...")
        
        # Get all open positions
        positions = await auto_trader.get_positions()
        
        if not positions:
            logger.info("No open positions found")
            return True
            
        # Close each position
        for position in positions:
            try:
                # Determine closing side
                side = 'SELL' if position['quantity'] > 0 else 'BUY'
                
                # Place closing order
                order_id = await auto_trader.place_order(
                    symbol=position['symbol'],
                    quantity=abs(position['quantity']),
                    side=side,
                    order_type='MARKET'
                )
                
                if order_id:
                    logger.info(f"Closed position for {position['symbol']}")
                else:
                    logger.error(f"Failed to close position for {position['symbol']}")
                    
            except Exception as e:
                logger.error(f"Error closing position for {position['symbol']}: {str(e)}")
                
        # Verify all positions are closed
        remaining = await auto_trader.get_positions()
        if remaining:
            logger.warning(f"Some positions could not be closed: {len(remaining)} remaining")
            return False
            
        logger.info("Successfully closed all positions")
        return True
        
    except Exception as e:
        logger.error(f"Failed to close positions: {str(e)}")
        return False

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run position closure
    asyncio.run(close_all_positions())
