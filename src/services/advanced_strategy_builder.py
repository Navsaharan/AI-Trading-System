from typing import Dict, List, Optional, Union, Any
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import torch
import torch.nn as nn
from torch.cuda.amp import autocast, GradScaler
import tensorflow as tf
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from sklearn.preprocessing import StandardScaler
import talib
import json
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import joblib
import os
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')

@dataclass
class StrategyConfig:
    name: str
    description: str
    risk_level: str
    time_horizon: str
    capital_required: float
    indicators: List[str]
    entry_conditions: List[Dict]
    exit_conditions: List[Dict]
    position_sizing: Dict
    risk_management: Dict
    backtesting_params: Dict

class AdvancedStrategyBuilder:
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.scaler = StandardScaler()
        self.executor = ThreadPoolExecutor(max_workers=8)
        self.initialize_components()

    def initialize_components(self):
        """Initialize strategy components"""
        try:
            # Load pre-trained models and configurations
            self.load_models()
            self.load_indicators()
            self.load_templates()
            print("Strategy builder initialized successfully")
        except Exception as e:
            print(f"Error initializing strategy builder: {e}")

    async def create_strategy(
        self,
        config: StrategyConfig,
        market_data: pd.DataFrame,
        user_preferences: Dict
    ) -> Dict:
        """Create a new trading strategy"""
        try:
            # Validate inputs
            self._validate_config(config)
            
            # Process in parallel
            with ThreadPoolExecutor() as executor:
                # Analyze market conditions
                market_analysis = executor.submit(
                    self._analyze_market, market_data
                )
                
                # Generate indicators
                indicators = executor.submit(
                    self._generate_indicators, config.indicators, market_data
                )
                
                # Optimize parameters
                parameters = executor.submit(
                    self._optimize_parameters, config, user_preferences
                )
                
                # Wait for results
                market_conditions = market_analysis.result()
                strategy_indicators = indicators.result()
                optimized_params = parameters.result()

            # Build strategy components
            entry_rules = await self._build_entry_rules(
                config.entry_conditions,
                strategy_indicators,
                market_conditions
            )
            
            exit_rules = await self._build_exit_rules(
                config.exit_conditions,
                strategy_indicators,
                market_conditions
            )
            
            position_sizing = await self._build_position_sizing(
                config.position_sizing,
                optimized_params
            )
            
            risk_management = await self._build_risk_management(
                config.risk_management,
                market_conditions
            )

            # Combine components
            strategy = {
                "name": config.name,
                "description": config.description,
                "entry_rules": entry_rules,
                "exit_rules": exit_rules,
                "position_sizing": position_sizing,
                "risk_management": risk_management,
                "indicators": strategy_indicators,
                "parameters": optimized_params,
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "risk_level": config.risk_level,
                    "time_horizon": config.time_horizon,
                    "capital_required": config.capital_required
                }
            }

            # Validate strategy
            if not self._validate_strategy(strategy):
                raise ValueError("Strategy validation failed")

            return strategy

        except Exception as e:
            print(f"Error creating strategy: {e}")
            return {}

    async def _build_entry_rules(
        self,
        conditions: List[Dict],
        indicators: Dict,
        market_conditions: Dict
    ) -> List[Dict]:
        """Build strategy entry rules"""
        try:
            rules = []
            
            for condition in conditions:
                # Process each condition
                rule = await self._process_condition(
                    condition,
                    indicators,
                    market_conditions,
                    "entry"
                )
                
                if rule:
                    rules.append(rule)

            return rules

        except Exception as e:
            print(f"Error building entry rules: {e}")
            return []

    async def _build_exit_rules(
        self,
        conditions: List[Dict],
        indicators: Dict,
        market_conditions: Dict
    ) -> List[Dict]:
        """Build strategy exit rules"""
        try:
            rules = []
            
            for condition in conditions:
                # Process each condition
                rule = await self._process_condition(
                    condition,
                    indicators,
                    market_conditions,
                    "exit"
                )
                
                if rule:
                    rules.append(rule)

            return rules

        except Exception as e:
            print(f"Error building exit rules: {e}")
            return []

    async def _build_position_sizing(
        self,
        config: Dict,
        parameters: Dict
    ) -> Dict:
        """Build position sizing rules"""
        try:
            return {
                "method": config.get("method", "fixed"),
                "size": config.get("size", 1.0),
                "max_position": config.get("max_position", 0.1),
                "sizing_factors": {
                    "volatility": parameters.get("volatility_factor", 1.0),
                    "confidence": parameters.get("confidence_factor", 1.0),
                    "risk_factor": parameters.get("risk_factor", 0.02)
                }
            }

        except Exception as e:
            print(f"Error building position sizing: {e}")
            return {}

    async def _build_risk_management(
        self,
        config: Dict,
        market_conditions: Dict
    ) -> Dict:
        """Build risk management rules"""
        try:
            return {
                "stop_loss": {
                    "type": config.get("stop_loss_type", "fixed"),
                    "value": config.get("stop_loss_value", 0.02),
                    "trailing": config.get("trailing_stop", False)
                },
                "take_profit": {
                    "type": config.get("take_profit_type", "fixed"),
                    "value": config.get("take_profit_value", 0.03),
                    "trailing": config.get("trailing_profit", False)
                },
                "max_drawdown": config.get("max_drawdown", 0.1),
                "position_limits": {
                    "max_positions": config.get("max_positions", 5),
                    "max_correlation": config.get("max_correlation", 0.7)
                },
                "market_conditions": {
                    "volatility_threshold": market_conditions.get("volatility", 0.0),
                    "liquidity_threshold": market_conditions.get("liquidity", 0.0)
                }
            }

        except Exception as e:
            print(f"Error building risk management: {e}")
            return {}

    def _validate_config(self, config: StrategyConfig) -> bool:
        """Validate strategy configuration"""
        try:
            required_fields = [
                'name', 'description', 'risk_level', 'time_horizon',
                'capital_required', 'indicators', 'entry_conditions',
                'exit_conditions', 'position_sizing', 'risk_management'
            ]
            
            # Check required fields
            for field in required_fields:
                if not hasattr(config, field):
                    raise ValueError(f"Missing required field: {field}")

            # Validate risk level
            if config.risk_level not in ['low', 'medium', 'high']:
                raise ValueError("Invalid risk level")

            # Validate time horizon
            if config.time_horizon not in ['short', 'medium', 'long']:
                raise ValueError("Invalid time horizon")

            # Validate capital
            if config.capital_required <= 0:
                raise ValueError("Invalid capital requirement")

            return True

        except Exception as e:
            print(f"Configuration validation failed: {e}")
            return False

    def _validate_strategy(self, strategy: Dict) -> bool:
        """Validate complete strategy"""
        try:
            required_components = [
                'entry_rules', 'exit_rules', 'position_sizing',
                'risk_management', 'indicators', 'parameters'
            ]
            
            # Check required components
            for component in required_components:
                if component not in strategy:
                    raise ValueError(f"Missing required component: {component}")

            # Validate rules
            if not strategy['entry_rules'] or not strategy['exit_rules']:
                raise ValueError("Strategy must have both entry and exit rules")

            # Validate position sizing
            if not strategy['position_sizing'].get('method'):
                raise ValueError("Invalid position sizing configuration")

            # Validate risk management
            risk_mgmt = strategy['risk_management']
            if not risk_mgmt.get('stop_loss') or not risk_mgmt.get('take_profit'):
                raise ValueError("Invalid risk management configuration")

            return True

        except Exception as e:
            print(f"Strategy validation failed: {e}")
            return False

    async def _process_condition(
        self,
        condition: Dict,
        indicators: Dict,
        market_conditions: Dict,
        rule_type: str
    ) -> Dict:
        """Process trading condition"""
        try:
            processed = {
                "type": condition.get("type", "simple"),
                "indicator": condition.get("indicator"),
                "operator": condition.get("operator"),
                "value": condition.get("value"),
                "timeframe": condition.get("timeframe", "1d"),
                "confidence": self._calculate_confidence(
                    condition, indicators, market_conditions
                )
            }
            
            # Add rule-specific parameters
            if rule_type == "entry":
                processed.update({
                    "min_volume": condition.get("min_volume", 0),
                    "max_spread": condition.get("max_spread", float('inf')),
                    "market_condition": condition.get("market_condition", "any")
                })
            else:  # exit
                processed.update({
                    "timeout": condition.get("timeout", float('inf')),
                    "profit_target": condition.get("profit_target"),
                    "stop_loss": condition.get("stop_loss")
                })

            return processed

        except Exception as e:
            print(f"Error processing condition: {e}")
            return {}

    def _calculate_confidence(
        self,
        condition: Dict,
        indicators: Dict,
        market_conditions: Dict
    ) -> float:
        """Calculate confidence score for a condition"""
        try:
            # Base confidence
            confidence = 0.5
            
            # Adjust based on indicator strength
            if condition["indicator"] in indicators:
                indicator_value = indicators[condition["indicator"]]
                confidence += self._adjust_for_indicator(indicator_value)
            
            # Adjust based on market conditions
            confidence *= self._adjust_for_market_conditions(market_conditions)
            
            # Ensure confidence is between 0 and 1
            return max(0.0, min(1.0, confidence))

        except Exception as e:
            print(f"Error calculating confidence: {e}")
            return 0.5

    @staticmethod
    def _adjust_for_indicator(value: float) -> float:
        """Adjust confidence based on indicator value"""
        try:
            # Normalize value between -1 and 1
            normalized = np.tanh(value)
            
            # Convert to confidence adjustment
            return (normalized + 1) / 4  # Results in [-0.25, 0.25]

        except Exception as e:
            print(f"Error adjusting for indicator: {e}")
            return 0.0

    @staticmethod
    def _adjust_for_market_conditions(conditions: Dict) -> float:
        """Adjust confidence based on market conditions"""
        try:
            # Start with neutral adjustment
            adjustment = 1.0
            
            # Adjust for volatility
            volatility = conditions.get("volatility", 0.0)
            adjustment *= 1.0 - (volatility / 2)  # Higher volatility reduces confidence
            
            # Adjust for liquidity
            liquidity = conditions.get("liquidity", 0.0)
            adjustment *= liquidity  # Lower liquidity reduces confidence
            
            # Ensure adjustment is between 0.5 and 1.5
            return max(0.5, min(1.5, adjustment))

        except Exception as e:
            print(f"Error adjusting for market conditions: {e}")
            return 1.0

# Initialize strategy builder
strategy_builder = AdvancedStrategyBuilder()
