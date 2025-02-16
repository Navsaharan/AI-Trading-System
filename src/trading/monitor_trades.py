import os
import sys
import time
import asyncio
from datetime import datetime
import logging
from typing import Dict, List
import pandas as pd
from ..core.trading_engine import TradingEngine
from ..core.risk_manager import RiskManager
from .auto_trader import AutoTrader

logger = logging.getLogger(__name__)

class TradingMonitor:
    def __init__(self):
        self.trading_engine = TradingEngine()
        self.risk_manager = RiskManager()
        self.auto_trader = AutoTrader(self.trading_engine, self.risk_manager)
        
        # Monitoring thresholds
        self.max_loss_percent = float(os.getenv('MAX_DAILY_LOSS', '0.02'))  # 2% max daily loss
        self.max_drawdown = float(os.getenv('MAX_DRAWDOWN', '0.05'))  # 5% max drawdown
        self.min_win_rate = float(os.getenv('MIN_WIN_RATE', '0.40'))  # 40% minimum win rate
        
        # Performance tracking
        self.start_balance = 0
        self.current_balance = 0
        self.peak_balance = 0
        self.daily_trades = []
        
    async def start_monitoring(self):
        """Start monitoring trading activity."""
        try:
            logger.info("Starting trading monitor...")
            
            # Get initial account balance
            account_info = await self.auto_trader.get_account_info()
            self.start_balance = account_info['balance']
            self.peak_balance = self.start_balance
            
            while True:
                await self.check_system_health()
                await asyncio.sleep(60)  # Check every minute
                
        except Exception as e:
            logger.error(f"Monitoring error: {str(e)}")
            await self.handle_monitoring_error()
            
    async def check_system_health(self):
        """Check various system health metrics."""
        try:
            # Get current metrics
            metrics = self.auto_trader.get_performance_metrics()
            account_info = await self.auto_trader.get_account_info()
            self.current_balance = account_info['balance']
            
            # Update peak balance
            if self.current_balance > self.peak_balance:
                self.peak_balance = self.current_balance
                
            # Calculate key metrics
            daily_pnl = self.current_balance - self.start_balance
            daily_return = daily_pnl / self.start_balance
            drawdown = (self.peak_balance - self.current_balance) / self.peak_balance
            win_rate = metrics['win_rate'] if metrics['total_trades'] > 0 else 0
            
            # Check thresholds
            if daily_return <= -self.max_loss_percent:
                await self.handle_max_loss()
                
            if drawdown >= self.max_drawdown:
                await self.handle_max_drawdown()
                
            if metrics['total_trades'] >= 10 and win_rate < self.min_win_rate:
                await self.handle_low_win_rate()
                
            # Log metrics
            self._log_metrics({
                'timestamp': datetime.now(),
                'balance': self.current_balance,
                'daily_pnl': daily_pnl,
                'drawdown': drawdown,
                'win_rate': win_rate,
                'total_trades': metrics['total_trades']
            })
            
        except Exception as e:
            logger.error(f"Health check error: {str(e)}")
            await self.handle_monitoring_error()
            
    async def handle_max_loss(self):
        """Handle maximum daily loss threshold breach."""
        logger.error("ALERT: Maximum daily loss threshold breached!")
        await self.auto_trader.stop(emergency=True)
        self._send_alert("Maximum daily loss threshold breached. Trading stopped.")
        
    async def handle_max_drawdown(self):
        """Handle maximum drawdown threshold breach."""
        logger.error("ALERT: Maximum drawdown threshold breached!")
        await self.auto_trader.stop(emergency=True)
        self._send_alert("Maximum drawdown threshold breached. Trading stopped.")
        
    async def handle_low_win_rate(self):
        """Handle low win rate alert."""
        logger.warning("ALERT: Win rate below minimum threshold!")
        self._send_alert("Win rate below minimum threshold. Please check strategy performance.")
        
    async def handle_monitoring_error(self):
        """Handle monitoring system errors."""
        logger.error("Critical monitoring error! Initiating emergency stop.")
        await self.auto_trader.stop(emergency=True)
        self._send_alert("Critical monitoring error. Trading stopped.")
        
    def _log_metrics(self, metrics: Dict):
        """Log trading metrics to file."""
        try:
            df = pd.DataFrame([metrics])
            mode = 'a' if os.path.exists('logs/trading_metrics.csv') else 'w'
            df.to_csv('logs/trading_metrics.csv', mode=mode, header=(mode=='w'), index=False)
        except Exception as e:
            logger.error(f"Error logging metrics: {str(e)}")
            
    def _send_alert(self, message: str):
        """Send alert to administrators."""
        try:
            # Log alert
            logger.warning(f"ALERT: {message}")
            
            # Save to alerts log
            with open('logs/alerts.log', 'a') as f:
                f.write(f"{datetime.now()}: {message}\n")
                
            # TODO: Implement additional alert methods (email, SMS, etc.)
            
        except Exception as e:
            logger.error(f"Error sending alert: {str(e)}")

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # Start monitoring
    monitor = TradingMonitor()
    asyncio.run(monitor.start_monitoring())
