from typing import Dict, List, Optional, Union
import asyncio
from datetime import datetime, timedelta
import pandas as pd
from ..core.trading_engine import TradingEngine
from ..core.risk_manager import RiskManager
from ..models.model_manager import ModelManager
from ..strategies.optimizer import StrategyOptimizer
from ..utils.market_data import MarketData
from ..analysis.sentiment_analyzer import SentimentAnalyzer
from ..portfolio.optimizer import PortfolioOptimizer
import threading
import time
import logging
from .strategies import TradingStrategy
from ..brokers.angelone import AngelOne
from ..brokers.zerodha import Zerodha

logger = logging.getLogger(__name__)

class AutoTrader:
    """Fully automated trading system with AI-powered decision making."""
    
    def __init__(self, trading_engine: TradingEngine,
                 risk_manager: RiskManager):
        # Core components
        self.trading_engine = trading_engine
        self.risk_manager = risk_manager
        self.model_manager = ModelManager()
        self.strategy_optimizer = StrategyOptimizer()
        self.market_data = MarketData()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.portfolio_optimizer = PortfolioOptimizer()
        
        # Brokers
        self.brokers: Dict[str, Any] = {}
        self._initialize_brokers()
        
        # Trading state
        self.is_running = False
        self.is_trading = False
        self.active_trades: Dict = {}
        self.pending_orders: Dict = {}
        self.trade_history: List = []
        self.strategies: List[TradingStrategy] = []
        
        # Performance tracking
        self.performance_metrics = {
            "total_trades": 0,
            "winning_trades": 0,
            "total_profit": 0,
            "max_drawdown": 0,
            "sharpe_ratio": 0,
            "win_rate": 0
        }
        
        # Error handling
        self.error_count = 0
        self.last_error_time = None
        self.max_errors = 3  # Max errors before emergency stop
        
        # Locks for thread safety
        self.trade_lock = threading.Lock()
        self.state_lock = threading.Lock()
        
    def _initialize_brokers(self):
        """Initialize broker connections with error handling."""
        try:
            self.brokers['angel'] = AngelOne()
            self.brokers['zerodha'] = Zerodha()
            logger.info("Successfully initialized brokers")
        except Exception as e:
            logger.error(f"Failed to initialize brokers: {str(e)}")
            raise
            
    async def start(self):
        """Start the auto trading system."""
        try:
            with self.state_lock:
                if self.is_running:
                    logger.warning("Auto trader is already running")
                    return False
                    
                # Connect to brokers
                for name, broker in self.brokers.items():
                    if not await broker.connect():
                        logger.error(f"Failed to connect to {name}")
                        return False
                        
                self.is_running = True
                self.error_count = 0
                self.last_error_time = None
                
            # Start trading loop in a separate thread
            self.trading_thread = threading.Thread(target=self._trading_loop)
            self.trading_thread.start()
            
            logger.info("Auto trader started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start auto trader: {str(e)}")
            return False
            
    async def stop(self, emergency: bool = False):
        """Stop the auto trading system."""
        try:
            with self.state_lock:
                if not self.is_running:
                    logger.warning("Auto trader is not running")
                    return True
                    
                self.is_running = False
                self.is_trading = False
                
                if emergency:
                    await self._emergency_stop()
                else:
                    await self._graceful_stop()
                    
                # Disconnect from brokers
                for name, broker in self.brokers.items():
                    if not await broker.disconnect():
                        logger.error(f"Failed to disconnect from {name}")
                        
            logger.info("Auto trader stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop auto trader: {str(e)}")
            return False
            
    async def _emergency_stop(self):
        """Emergency stop - close all positions immediately."""
        logger.warning("Initiating emergency stop!")
        try:
            with self.trade_lock:
                # Close all active trades
                for trade_id in list(self.active_trades.keys()):
                    await self._exit_trade(trade_id, emergency=True)
                    
                # Cancel all pending orders
                for order_id in list(self.pending_orders.keys()):
                    await self._cancel_order(order_id)
                    
        except Exception as e:
            logger.error(f"Error during emergency stop: {str(e)}")
            
    async def _graceful_stop(self):
        """Graceful stop - wait for positions to close normally."""
        logger.info("Initiating graceful stop...")
        try:
            # Wait for active trades to close naturally
            timeout = 300  # 5 minutes timeout
            start_time = time.time()
            
            while self.active_trades and time.time() - start_time < timeout:
                await asyncio.sleep(1)
                
            # Force close any remaining trades
            if self.active_trades:
                logger.warning("Forcing close of remaining trades")
                await self._emergency_stop()
                
        except Exception as e:
            logger.error(f"Error during graceful stop: {str(e)}")
            
    def _trading_loop(self):
        """Main trading loop."""
        while self.is_running:
            try:
                # Check market hours
                if not self._check_market_hours():
                    time.sleep(60)
                    continue
                    
                # Process strategies
                with self.trade_lock:
                    self._process_strategies()
                    self._manage_positions()
                    self._update_metrics()
                    
                # Check for errors
                if self.error_count >= self.max_errors:
                    logger.error("Too many errors, initiating emergency stop")
                    asyncio.run(self.stop(emergency=True))
                    break
                    
                time.sleep(1)  # Prevent excessive CPU usage
                
            except Exception as e:
                self._handle_error(e)
                
    def _handle_error(self, error: Exception):
        """Handle errors in the trading loop."""
        now = datetime.now()
        self.error_count += 1
        self.last_error_time = now
        
        logger.error(f"Trading loop error: {str(error)}")
        
        # Reset error count if last error was more than 1 hour ago
        if self.last_error_time and (now - self.last_error_time).hours >= 1:
            self.error_count = 1
            
    def _check_market_hours(self) -> bool:
        """Check if market is open."""
        now = datetime.now()
        
        # Check for holidays
        if self._is_holiday(now):
            return False
            
        # Check market hours (9:15 AM to 3:30 PM IST)
        market_start = now.replace(hour=9, minute=15, second=0)
        market_end = now.replace(hour=15, minute=30, second=0)
        
        return market_start <= now <= market_end
        
    def _is_holiday(self, date: datetime) -> bool:
        """Check if given date is a trading holiday."""
        # Implement holiday checking logic
        return False  # Placeholder
        
    def add_strategy(self, strategy: TradingStrategy):
        """Add a new trading strategy."""
        try:
            if not isinstance(strategy, TradingStrategy):
                raise ValueError("Invalid strategy type")
                
            with self.state_lock:
                self.strategies.append(strategy)
                logger.info(f"Added strategy: {strategy.name}")
                
        except Exception as e:
            logger.error(f"Error adding strategy: {str(e)}")
            
    def get_performance_metrics(self) -> Dict:
        """Get current performance metrics."""
        try:
            with self.state_lock:
                metrics = self.performance_metrics.copy()
                
            # Calculate additional metrics
            if metrics['total_trades'] > 0:
                metrics['win_rate'] = (metrics['winning_trades'] / 
                                     metrics['total_trades']) * 100
                                     
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {str(e)}")
            return {}
            
    async def start_auto_trading(self, config: Dict) -> bool:
        """Start automated trading with specified configuration."""
        try:
            if self.is_trading:
                return False
            
            # Validate configuration
            if not self._validate_config(config):
                return False
            
            # Initialize trading parameters
            self.config = config
            self.is_trading = True
            
            # Start trading loop
            asyncio.create_task(self._trading_loop())
            
            return True
        except Exception as e:
            print(f"Error starting auto trading: {str(e)}")
            return False
    
    async def stop_auto_trading(self) -> bool:
        """Stop automated trading."""
        try:
            if not self.is_trading:
                return False
            
            # Stop trading
            self.is_trading = False
            
            # Close all positions if configured
            if self.config.get("close_positions_on_stop", True):
                await self._close_all_positions()
            
            # Cancel all pending orders
            await self._cancel_all_orders()
            
            return True
        except Exception as e:
            print(f"Error stopping auto trading: {str(e)}")
            return False
    
    async def update_trading_config(self, new_config: Dict) -> bool:
        """Update trading configuration in real-time."""
        try:
            # Validate new configuration
            if not self._validate_config(new_config):
                return False
            
            # Update configuration
            self.config = new_config
            
            # Adjust positions if necessary
            if new_config.get("adjust_positions", True):
                await self._adjust_positions_to_config()
            
            return True
        except Exception as e:
            print(f"Error updating config: {str(e)}")
            return False
    
    async def get_trading_status(self) -> Dict:
        """Get current trading status and performance metrics."""
        try:
            # Get account information
            account = await self.trading_engine.get_account_info()
            
            # Get open positions
            positions = await self.trading_engine.get_positions()
            
            # Calculate current performance
            performance = self._calculate_performance()
            
            return {
                "is_trading": self.is_trading,
                "account_summary": account,
                "open_positions": positions,
                "pending_orders": self.pending_orders,
                "performance": performance,
                "last_update": datetime.now()
            }
        except Exception as e:
            print(f"Error getting status: {str(e)}")
            return {}
    
    async def _trading_loop(self):
        """Main trading loop for automated trading."""
        while self.is_trading:
            try:
                # Get market data
                market_data = await self._get_market_data()
                
                # Update AI models
                await self._update_models(market_data)
                
                # Generate trading signals
                signals = await self._generate_trading_signals(market_data)
                
                # Validate signals with risk manager
                valid_signals = await self._validate_signals(signals)
                
                # Execute trades
                for signal in valid_signals:
                    await self._execute_trade(signal)
                
                # Monitor and adjust positions
                await self._monitor_positions()
                
                # Update performance metrics
                self._update_performance_metrics()
                
                # Small delay to prevent excessive API calls
                await asyncio.sleep(self.config.get("update_interval", 1))
            except Exception as e:
                print(f"Error in trading loop: {str(e)}")
                await asyncio.sleep(5)  # Longer delay on error
    
    async def _get_market_data(self) -> Dict:
        """Get real-time market data for trading decisions."""
        try:
            data = {}
            
            # Get price data
            for symbol in self.config["symbols"]:
                price_data = await self.market_data.get_real_time_price(symbol)
                data[symbol] = price_data
            
            # Get sentiment data if enabled
            if self.config.get("use_sentiment", True):
                sentiment = await self.sentiment_analyzer.get_market_sentiment()
                data["sentiment"] = sentiment
            
            # Get technical indicators
            indicators = await self.market_data.get_technical_indicators(
                self.config["symbols"],
                self.config.get("indicators", ["sma", "rsi", "macd"])
            )
            data["indicators"] = indicators
            
            return data
        except Exception:
            return {}
    
    async def _update_models(self, market_data: Dict):
        """Update AI models with new market data."""
        try:
            for model_type in self.config.get("models", []):
                for symbol in self.config["symbols"]:
                    await self.model_manager.update_model(
                        model_type,
                        symbol,
                        market_data
                    )
        except Exception:
            pass
    
    async def _generate_trading_signals(self, market_data: Dict) -> List[Dict]:
        """Generate trading signals using AI models and strategies."""
        try:
            signals = []
            
            # Get predictions from each model
            for model_type in self.config.get("models", []):
                for symbol in self.config["symbols"]:
                    prediction = await self.model_manager.predict(
                        model_type,
                        symbol,
                        market_data
                    )
                    
                    if prediction.get("confidence", 0) >= \
                       self.config.get("min_confidence", 0.7):
                        signals.append(self._convert_prediction_to_signal(
                            prediction,
                            symbol
                        ))
            
            # Get strategy signals
            strategy_signals = await self.strategy_optimizer.generate_signals(
                market_data
            )
            signals.extend(strategy_signals)
            
            return signals
        except Exception:
            return []
    
    async def _validate_signals(self, signals: List[Dict]) -> List[Dict]:
        """Validate trading signals with risk manager."""
        try:
            valid_signals = []
            
            for signal in signals:
                # Check risk limits
                if await self.risk_manager.validate_trade(signal):
                    # Check portfolio constraints
                    if await self._check_portfolio_constraints(signal):
                        valid_signals.append(signal)
            
            return valid_signals
        except Exception:
            return []
    
    async def _execute_trade(self, signal: Dict):
        """Execute trading signal."""
        try:
            # Calculate position size
            size = await self._calculate_position_size(signal)
            
            # Place order
            order = await self.trading_engine.place_order(
                symbol=signal["symbol"],
                side=signal["side"],
                quantity=size,
                order_type=signal.get("order_type", "MARKET"),
                price=signal.get("price"),
                stop_loss=signal.get("stop_loss"),
                take_profit=signal.get("take_profit")
            )
            
            if order:
                # Track order
                self.pending_orders[order["order_id"]] = {
                    "signal": signal,
                    "order": order,
                    "timestamp": datetime.now()
                }
                
                # Update metrics
                self.performance_metrics["total_trades"] += 1
        except Exception as e:
            print(f"Error executing trade: {str(e)}")
    
    async def _monitor_positions(self):
        """Monitor and manage open positions."""
        try:
            positions = await self.trading_engine.get_positions()
            
            for position in positions:
                # Check stop loss and take profit
                await self._check_exit_conditions(position)
                
                # Update trailing stops
                await self._update_trailing_stop(position)
                
                # Check position health
                await self._check_position_health(position)
        except Exception:
            pass
    
    async def _close_all_positions(self):
        """Close all open positions."""
        try:
            positions = await self.trading_engine.get_positions()
            
            for position in positions:
                await self.trading_engine.close_position(
                    position["id"]
                )
        except Exception:
            pass
    
    async def _cancel_all_orders(self):
        """Cancel all pending orders."""
        try:
            for order_id in self.pending_orders:
                await self.trading_engine.cancel_order(order_id)
            self.pending_orders.clear()
        except Exception:
            pass
    
    async def _adjust_positions_to_config(self):
        """Adjust positions based on new configuration."""
        try:
            # Get optimal portfolio allocation
            optimal_allocation = await self.portfolio_optimizer.optimize_portfolio(
                self.config["symbols"],
                self.config.get("investment_amount", 100000),
                self.config.get("risk_tolerance", 0.5)
            )
            
            # Get current positions
            current_positions = await self.trading_engine.get_positions()
            
            # Generate rebalancing trades
            rebalancing = await self.portfolio_optimizer.rebalance_portfolio(
                current_positions,
                optimal_allocation["weights"]
            )
            
            # Execute rebalancing trades
            for trade in rebalancing["trades"]:
                await self._execute_trade(trade)
        except Exception:
            pass
    
    def _validate_config(self, config: Dict) -> bool:
        """Validate trading configuration."""
        required_fields = ["symbols", "investment_amount", "risk_tolerance"]
        return all(field in config for field in required_fields)
    
    async def _calculate_position_size(self, signal: Dict) -> float:
        """Calculate appropriate position size for trade."""
        try:
            # Get account information
            account = await self.trading_engine.get_account_info()
            
            # Get risk per trade
            risk_per_trade = account["balance"] * \
                           self.config.get("risk_per_trade", 0.01)
            
            # Calculate size based on risk
            price = await self.market_data.get_real_time_price(signal["symbol"])
            stop_loss = signal.get("stop_loss", price["price"] * 0.99)
            
            risk_per_share = abs(price["price"] - stop_loss)
            size = risk_per_trade / risk_per_share
            
            # Apply position limits
            max_size = account["balance"] * \
                      self.config.get("max_position_size", 0.1)
            return min(size, max_size)
        except Exception:
            return 0
    
    def _convert_prediction_to_signal(self, prediction: Dict,
                                    symbol: str) -> Dict:
        """Convert model prediction to trading signal."""
        try:
            return {
                "symbol": symbol,
                "side": "BUY" if prediction["prediction"] > 0 else "SELL",
                "confidence": prediction["confidence"],
                "source": "model",
                "model_type": prediction["model_type"],
                "timestamp": datetime.now()
            }
        except Exception:
            return {}
    
    async def _check_portfolio_constraints(self, signal: Dict) -> bool:
        """Check if trade satisfies portfolio constraints."""
        try:
            # Get current portfolio
            positions = await self.trading_engine.get_positions()
            
            # Check concentration limits
            symbol_exposure = sum(
                p["value"] for p in positions
                if p["symbol"] == signal["symbol"]
            )
            
            total_value = sum(p["value"] for p in positions)
            
            # Check if new trade would exceed limits
            if symbol_exposure / total_value > \
               self.config.get("max_symbol_concentration", 0.2):
                return False
            
            return True
        except Exception:
            return False
    
    def _calculate_performance(self) -> Dict:
        """Calculate detailed performance metrics."""
        try:
            return {
                "total_trades": self.performance_metrics["total_trades"],
                "winning_trades": self.performance_metrics["winning_trades"],
                "win_rate": self.performance_metrics["winning_trades"] / \
                           max(self.performance_metrics["total_trades"], 1),
                "total_profit": self.performance_metrics["total_profit"],
                "max_drawdown": self.performance_metrics["max_drawdown"],
                "sharpe_ratio": self._calculate_sharpe_ratio(),
                "last_updated": datetime.now()
            }
        except Exception:
            return {}
    
    def _calculate_sharpe_ratio(self) -> float:
        """Calculate Sharpe ratio of trading performance."""
        try:
            if not self.trade_history:
                return 0
            
            returns = pd.Series([t["return"] for t in self.trade_history])
            return (returns.mean() - 0.02) / returns.std()  # Assuming 2% risk-free rate
        except Exception:
            return 0
    
    def add_strategy(self, strategy: TradingStrategy):
        self.strategies.append(strategy)
        
    def start(self):
        self.is_running = True
        self.trading_thread = threading.Thread(target=self._trading_loop)
        self.trading_thread.start()
        
    def stop(self):
        self.is_running = False
        
    def _trading_loop(self):
        while self.is_running:
            try:
                self._check_market_hours()
                self._process_strategies()
                self._manage_positions()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Trading Loop Error: {str(e)}")
                
    def _check_market_hours(self):
        now = datetime.now()
        if now.hour < 9 or now.hour >= 15:
            return False
        return True
        
    def _process_strategies(self):
        for strategy in self.strategies:
            signals = strategy.analyze(self._get_market_data())
            if signals['confidence'] > 0.7:  # High confidence trades only
                self._execute_trade(strategy, signals)
                
    def _execute_trade(self, strategy, signals):
        # Calculate position size based on risk
        account_value = self._get_account_value()
        risk_amount = account_value * strategy.risk_per_trade
        position_size = self._calculate_position_size(
            risk_amount,
            signals['stop_loss']
        )
        
        # Place orders
        if signals['signal'] == 'BUY':
            order_id = self.brokers['angel'].place_order(
                symbol=signals['symbol'],
                qty=position_size,
                side='BUY'
            )
            if order_id:
                self._place_stop_loss(order_id, signals['stop_loss'])
                self._place_target(order_id, signals['target'])
                
    def _manage_positions(self):
        # Trail stops, manage targets, handle exits
        for trade_id, trade in self.active_trades.items():
            current_price = self._get_current_price(trade['symbol'])
            if self._should_exit(trade, current_price):
                self._exit_trade(trade_id)
