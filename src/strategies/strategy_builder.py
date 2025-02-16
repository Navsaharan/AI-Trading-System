from typing import Dict, List, Optional, Union
import numpy as np
import pandas as pd
from datetime import datetime
from transformers import pipeline
import torch
from ..models.base_model import BaseAIModel
from ..utils.market_data import MarketData
from ..core.risk_manager import RiskManager

class AIStrategyBuilder:
    """AI-powered trading strategy builder that converts natural language to executable strategies."""
    
    def __init__(self):
        self.nlp = pipeline("text2text-generation", model="facebook/bart-large")
        self.risk_manager = RiskManager()
        self.market_data = MarketData()
    
    async def create_strategy_from_prompt(self, prompt: str,
                                        risk_level: str = "medium",
                                        investment_amount: float = 100000,
                                        markets: List[str] = ["stocks"]) -> Dict:
        """Create a trading strategy from natural language prompt."""
        try:
            # Parse the prompt to extract key components
            strategy_components = await self._parse_strategy_prompt(prompt)
            
            # Generate strategy configuration
            strategy_config = {
                "name": strategy_components["name"],
                "type": strategy_components["type"],
                "entry_conditions": strategy_components["entry_conditions"],
                "exit_conditions": strategy_components["exit_conditions"],
                "risk_level": risk_level,
                "investment_amount": investment_amount,
                "markets": markets,
                "parameters": await self._generate_strategy_parameters(
                    strategy_components, risk_level
                ),
                "risk_management": await self._generate_risk_parameters(
                    risk_level, investment_amount
                )
            }
            
            # Validate strategy
            if not await self._validate_strategy(strategy_config):
                raise ValueError("Generated strategy failed validation")
            
            return strategy_config
        except Exception as e:
            print(f"Error creating strategy: {str(e)}")
            return {}
    
    async def _parse_strategy_prompt(self, prompt: str) -> Dict:
        """Parse natural language prompt into strategy components."""
        # Generate strategy structure using NLP model
        generated = self.nlp(prompt, max_length=512, num_return_sequences=1)[0]
        
        # Extract key components using NLP
        components = {
            "name": self._extract_strategy_name(generated),
            "type": self._determine_strategy_type(generated),
            "entry_conditions": self._extract_conditions(generated, "entry"),
            "exit_conditions": self._extract_conditions(generated, "exit"),
            "timeframe": self._extract_timeframe(generated),
            "indicators": self._extract_indicators(generated)
        }
        
        return components
    
    async def _generate_strategy_parameters(self, components: Dict,
                                          risk_level: str) -> Dict:
        """Generate optimal strategy parameters based on components and risk level."""
        params = {
            "timeframe": components["timeframe"],
            "indicators": {}
        }
        
        # Configure indicator parameters based on risk level
        for indicator in components["indicators"]:
            if indicator == "moving_average":
                params["indicators"][indicator] = {
                    "short_period": 10 if risk_level == "high" else 20,
                    "long_period": 30 if risk_level == "high" else 50
                }
            elif indicator == "rsi":
                params["indicators"][indicator] = {
                    "period": 9 if risk_level == "high" else 14,
                    "overbought": 70,
                    "oversold": 30
                }
            elif indicator == "macd":
                params["indicators"][indicator] = {
                    "fast_period": 12,
                    "slow_period": 26,
                    "signal_period": 9
                }
        
        # Add position sizing parameters
        params["position_sizing"] = {
            "max_position_size": 0.2 if risk_level == "high" else 0.1,
            "max_positions": 5 if risk_level == "high" else 3,
            "position_scaling": True if risk_level == "high" else False
        }
        
        return params
    
    async def _generate_risk_parameters(self, risk_level: str,
                                      investment_amount: float) -> Dict:
        """Generate risk management parameters based on risk level."""
        risk_multiplier = {
            "low": 0.01,
            "medium": 0.02,
            "high": 0.03
        }
        
        return {
            "stop_loss": risk_multiplier[risk_level] * 2,
            "take_profit": risk_multiplier[risk_level] * 3,
            "max_drawdown": risk_multiplier[risk_level] * 10,
            "position_size_limit": investment_amount * risk_multiplier[risk_level],
            "daily_loss_limit": investment_amount * risk_multiplier[risk_level] * 2,
            "use_trailing_stop": risk_level == "high"
        }
    
    async def _validate_strategy(self, strategy: Dict) -> bool:
        """Validate generated strategy configuration."""
        try:
            # Check required fields
            required_fields = ["name", "type", "entry_conditions", "exit_conditions",
                             "parameters", "risk_management"]
            if not all(field in strategy for field in required_fields):
                return False
            
            # Validate risk parameters
            risk_params = strategy["risk_management"]
            if not (0 < risk_params["stop_loss"] < 1 and
                   0 < risk_params["take_profit"] < 1 and
                   0 < risk_params["max_drawdown"] < 1):
                return False
            
            # Validate position sizing
            position_params = strategy["parameters"]["position_sizing"]
            if not (0 < position_params["max_position_size"] <= 1 and
                   position_params["max_positions"] > 0):
                return False
            
            return True
        except Exception:
            return False
    
    def _extract_strategy_name(self, text: str) -> str:
        """Extract strategy name from generated text."""
        # Implementation using NLP to extract strategy name
        return "Custom AI Strategy"  # Placeholder
    
    def _determine_strategy_type(self, text: str) -> str:
        """Determine strategy type from generated text."""
        # Implementation using NLP to determine strategy type
        return "trend_following"  # Placeholder
    
    def _extract_conditions(self, text: str, condition_type: str) -> List[Dict]:
        """Extract entry or exit conditions from generated text."""
        # Implementation using NLP to extract conditions
        return []  # Placeholder
    
    def _extract_timeframe(self, text: str) -> str:
        """Extract trading timeframe from generated text."""
        # Implementation using NLP to extract timeframe
        return "5min"  # Placeholder
    
    def _extract_indicators(self, text: str) -> List[str]:
        """Extract technical indicators from generated text."""
        # Implementation using NLP to extract indicators
        return ["moving_average", "rsi", "macd"]  # Placeholder
    
    async def backtest_strategy(self, strategy: Dict,
                              historical_data: pd.DataFrame) -> Dict:
        """Backtest the generated strategy."""
        try:
            # Initialize results
            positions = []
            trades = []
            equity = strategy["investment_amount"]
            current_position = None
            
            # Apply strategy rules
            for i in range(len(historical_data)):
                if i < 50:  # Skip initial period for indicators
                    continue
                
                # Check entry conditions
                if not current_position:
                    if await self._check_entry_conditions(
                        historical_data.iloc[:i+1], strategy["entry_conditions"]
                    ):
                        # Enter position
                        entry_price = historical_data.iloc[i]["close"]
                        position_size = self._calculate_position_size(
                            equity, strategy["risk_management"]
                        )
                        current_position = {
                            "entry_price": entry_price,
                            "size": position_size,
                            "entry_time": historical_data.index[i]
                        }
                        positions.append(current_position)
                
                # Check exit conditions
                elif await self._check_exit_conditions(
                    historical_data.iloc[:i+1],
                    strategy["exit_conditions"],
                    current_position
                ):
                    # Exit position
                    exit_price = historical_data.iloc[i]["close"]
                    profit = (exit_price - current_position["entry_price"]) * \
                            current_position["size"]
                    equity += profit
                    
                    trades.append({
                        "entry_time": current_position["entry_time"],
                        "exit_time": historical_data.index[i],
                        "entry_price": current_position["entry_price"],
                        "exit_price": exit_price,
                        "profit": profit,
                        "return": profit / current_position["size"]
                    })
                    
                    current_position = None
            
            # Calculate performance metrics
            performance = self._calculate_performance_metrics(trades, equity)
            
            return {
                "trades": trades,
                "final_equity": equity,
                "performance": performance
            }
        except Exception as e:
            print(f"Error in backtesting: {str(e)}")
            return {}
    
    async def _check_entry_conditions(self, data: pd.DataFrame,
                                    conditions: List[Dict]) -> bool:
        """Check if entry conditions are met."""
        # Implementation of entry condition checking
        return True  # Placeholder
    
    async def _check_exit_conditions(self, data: pd.DataFrame,
                                   conditions: List[Dict],
                                   position: Dict) -> bool:
        """Check if exit conditions are met."""
        # Implementation of exit condition checking
        return False  # Placeholder
    
    def _calculate_position_size(self, equity: float,
                               risk_params: Dict) -> float:
        """Calculate position size based on risk parameters."""
        return equity * risk_params["position_size_limit"]
    
    def _calculate_performance_metrics(self, trades: List[Dict],
                                    final_equity: float) -> Dict:
        """Calculate strategy performance metrics."""
        if not trades:
            return {}
        
        returns = [t["return"] for t in trades]
        
        return {
            "total_trades": len(trades),
            "winning_trades": len([r for r in returns if r > 0]),
            "average_return": np.mean(returns),
            "sharpe_ratio": np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0,
            "max_drawdown": self._calculate_max_drawdown(trades),
            "final_return": (final_equity - trades[0]["entry_price"]) / trades[0]["entry_price"]
        }
    
    def _calculate_max_drawdown(self, trades: List[Dict]) -> float:
        """Calculate maximum drawdown from trade history."""
        if not trades:
            return 0
        
        equity_curve = []
        current_equity = 1000000  # Starting equity
        
        for trade in trades:
            current_equity += trade["profit"]
            equity_curve.append(current_equity)
        
        equity_curve = np.array(equity_curve)
        peak = np.maximum.accumulate(equity_curve)
        drawdown = (peak - equity_curve) / peak
        
        return np.max(drawdown) if len(drawdown) > 0 else 0
