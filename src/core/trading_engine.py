from typing import Dict, List, Optional
import asyncio
from datetime import datetime
import pandas as pd
import numpy as np
from ..database.models import User, Strategy, Trade, Position
from ..brokers.base import BaseBroker
from ..models.base_model import BaseAIModel

class TradingEngine:
    """Core trading engine that manages trading operations and risk."""
    
    def __init__(self, user: User, broker: BaseBroker, strategy: Strategy,
                 ai_models: Dict[str, BaseAIModel], risk_params: Dict = None):
        self.user = user
        self.broker = broker
        self.strategy = strategy
        self.ai_models = ai_models
        self.risk_params = risk_params or {
            'max_position_size': 0.1,  # 10% of portfolio
            'stop_loss': 0.02,  # 2%
            'take_profit': 0.04,  # 4%
            'max_trades_per_day': 10
        }
        self.is_running = False
        self.positions = []
        self.trades = []
    
    async def start(self) -> bool:
        """Start the trading engine."""
        try:
            if not await self.broker.connect():
                raise Exception("Failed to connect to broker")
            
            self.is_running = True
            await self.run_trading_loop()
            return True
        except Exception as e:
            print(f"Error starting trading engine: {str(e)}")
            return False
    
    async def stop(self) -> bool:
        """Stop the trading engine."""
        try:
            self.is_running = False
            await self.broker.disconnect()
            return True
        except Exception as e:
            print(f"Error stopping trading engine: {str(e)}")
            return False
    
    async def run_trading_loop(self) -> None:
        """Main trading loop."""
        while self.is_running:
            try:
                # Update market data
                market_data = await self.get_market_data()
                
                # Update AI predictions
                predictions = await self.get_ai_predictions(market_data)
                
                # Generate trading signals
                signals = await self.generate_trading_signals(predictions)
                
                # Execute trades based on signals
                for signal in signals:
                    if await self.validate_trade(signal):
                        await self.execute_trade(signal)
                
                # Update positions and risk
                await self.update_positions()
                await self.manage_risk()
                
                # Sleep for the defined interval
                await asyncio.sleep(self.strategy.parameters.get('interval', 60))
            except Exception as e:
                print(f"Error in trading loop: {str(e)}")
                await asyncio.sleep(5)
    
    async def get_market_data(self) -> pd.DataFrame:
        """Fetch and process market data."""
        try:
            symbols = self.strategy.parameters.get('symbols', [])
            interval = self.strategy.parameters.get('interval', '1m')
            
            data = []
            for symbol in symbols:
                market_data = await self.broker.get_market_data(symbol, interval)
                if market_data:
                    df = pd.DataFrame(market_data)
                    df['symbol'] = symbol
                    data.append(df)
            
            return pd.concat(data) if data else pd.DataFrame()
        except Exception as e:
            print(f"Error getting market data: {str(e)}")
            return pd.DataFrame()
    
    async def get_ai_predictions(self, market_data: pd.DataFrame) -> Dict:
        """Get predictions from AI models."""
        predictions = {}
        try:
            for model_name, model in self.ai_models.items():
                if model.is_trained:
                    pred = await model.predict(market_data)
                    predictions[model_name] = pred
            return predictions
        except Exception as e:
            print(f"Error getting AI predictions: {str(e)}")
            return {}
    
    async def generate_trading_signals(self, predictions: Dict) -> List[Dict]:
        """Generate trading signals based on AI predictions."""
        signals = []
        try:
            # Combine predictions from different models
            for symbol in self.strategy.parameters.get('symbols', []):
                signal = {
                    'symbol': symbol,
                    'side': None,
                    'confidence': 0,
                    'timestamp': datetime.utcnow()
                }
                
                # Calculate combined signal
                technical_score = predictions.get('technical', {}).get(symbol, 0)
                sentiment_score = predictions.get('sentiment', {}).get(symbol, 0)
                
                # Weight the signals based on strategy parameters
                weights = self.strategy.parameters.get('model_weights', {
                    'technical': 0.7,
                    'sentiment': 0.3
                })
                
                combined_score = (
                    technical_score * weights['technical'] +
                    sentiment_score * weights['sentiment']
                )
                
                # Generate trading signal based on combined score
                if combined_score > self.strategy.parameters.get('buy_threshold', 0.7):
                    signal['side'] = 'buy'
                    signal['confidence'] = combined_score
                elif combined_score < self.strategy.parameters.get('sell_threshold', -0.7):
                    signal['side'] = 'sell'
                    signal['confidence'] = abs(combined_score)
                
                if signal['side']:
                    signals.append(signal)
            
            return signals
        except Exception as e:
            print(f"Error generating trading signals: {str(e)}")
            return []
    
    async def validate_trade(self, signal: Dict) -> bool:
        """Validate trading signal against risk parameters."""
        try:
            # Check trading hours
            if not self.is_trading_hours():
                return False
            
            # Check maximum trades per day
            if len(self.trades) >= self.risk_params['max_trades_per_day']:
                return False
            
            # Check position size
            account_value = await self.broker.get_account_balance()
            ticker = await self.broker.get_ticker(signal['symbol'])
            position_size = (account_value * self.risk_params['max_position_size'])
            
            if position_size <= 0:
                return False
            
            return True
        except Exception as e:
            print(f"Error validating trade: {str(e)}")
            return False
    
    async def execute_trade(self, signal: Dict) -> bool:
        """Execute trade based on signal."""
        try:
            # Calculate position size
            account_value = await self.broker.get_account_balance()
            position_size = (account_value * self.risk_params['max_position_size'])
            
            # Get current market price
            ticker = await self.broker.get_ticker(signal['symbol'])
            price = float(ticker['last'])
            
            # Calculate quantity
            quantity = position_size / price
            
            # Place order
            order = await self.broker.place_order(
                symbol=signal['symbol'],
                side=signal['side'],
                quantity=quantity,
                order_type='market'
            )
            
            if order:
                # Record trade
                trade = Trade(
                    strategy_id=self.strategy.id,
                    symbol=signal['symbol'],
                    side=signal['side'],
                    quantity=quantity,
                    price=price,
                    status='open'
                )
                self.trades.append(trade)
                return True
            
            return False
        except Exception as e:
            print(f"Error executing trade: {str(e)}")
            return False
    
    async def update_positions(self) -> None:
        """Update current positions and calculate P&L."""
        try:
            positions = await self.broker.get_positions()
            self.positions = positions
            
            for position in self.positions:
                # Update position with current market price
                ticker = await self.broker.get_ticker(position['symbol'])
                position['current_price'] = float(ticker['last'])
                position['unrealized_pnl'] = (
                    position['current_price'] - position['entry_price']
                ) * position['quantity']
        except Exception as e:
            print(f"Error updating positions: {str(e)}")
    
    async def manage_risk(self) -> None:
        """Manage risk for open positions."""
        try:
            for position in self.positions:
                # Check stop loss
                stop_loss = position['entry_price'] * (1 - self.risk_params['stop_loss'])
                take_profit = position['entry_price'] * (1 + self.risk_params['take_profit'])
                
                if position['current_price'] <= stop_loss or position['current_price'] >= take_profit:
                    await self.broker.place_order(
                        symbol=position['symbol'],
                        side='sell' if position['side'] == 'buy' else 'buy',
                        quantity=position['quantity'],
                        order_type='market'
                    )
        except Exception as e:
            print(f"Error managing risk: {str(e)}")
    
    def is_trading_hours(self) -> bool:
        """Check if current time is within trading hours."""
        now = datetime.utcnow()
        trading_hours = self.strategy.parameters.get('trading_hours', {
            'start': '09:30',
            'end': '16:00'
        })
        
        start_time = datetime.strptime(trading_hours['start'], '%H:%M').time()
        end_time = datetime.strptime(trading_hours['end'], '%H:%M').time()
        
        return start_time <= now.time() <= end_time
