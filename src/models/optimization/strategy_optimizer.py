import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import optuna
from sklearn.metrics import sharpe_ratio, max_drawdown
import ray
from ray import tune
import mlflow

class StrategyOptimizer:
    """Optimizes trading strategies using AI and machine learning techniques."""
    
    def __init__(self, risk_free_rate: float = 0.02):
        self.risk_free_rate = risk_free_rate
        ray.init(ignore_reinit_error=True)
    
    async def optimize_strategy(self, strategy_config: Dict,
                              historical_data: pd.DataFrame,
                              optimization_target: str = "sharpe_ratio",
                              n_trials: int = 100) -> Dict:
        """
        Optimize strategy parameters for maximum performance.
        
        Args:
            strategy_config: Initial strategy configuration
            historical_data: Historical market data for backtesting
            optimization_target: Metric to optimize ('sharpe_ratio', 'returns', 'drawdown')
            n_trials: Number of optimization trials
        """
        def objective(trial):
            # Define parameter search space
            params = {
                "entry_threshold": trial.suggest_float("entry_threshold", 0.1, 0.9),
                "exit_threshold": trial.suggest_float("exit_threshold", 0.1, 0.9),
                "stop_loss": trial.suggest_float("stop_loss", 0.01, 0.1),
                "take_profit": trial.suggest_float("take_profit", 0.02, 0.2),
                "lookback_period": trial.suggest_int("lookback_period", 5, 100),
                "position_size": trial.suggest_float("position_size", 0.1, 1.0),
                "max_positions": trial.suggest_int("max_positions", 1, 10),
            }
            
            # Add strategy-specific parameters
            if strategy_config.get("type") == "trend_following":
                params.update({
                    "trend_period": trial.suggest_int("trend_period", 10, 200),
                    "momentum_period": trial.suggest_int("momentum_period", 5, 50),
                })
            elif strategy_config.get("type") == "mean_reversion":
                params.update({
                    "mean_period": trial.suggest_int("mean_period", 10, 100),
                    "std_multiplier": trial.suggest_float("std_multiplier", 1.0, 3.0),
                })
            
            # Run backtest with parameters
            returns, metrics = await self.backtest_strategy(
                historical_data, {**strategy_config, **params}
            )
            
            # Calculate optimization metric
            if optimization_target == "sharpe_ratio":
                score = metrics["sharpe_ratio"]
            elif optimization_target == "returns":
                score = metrics["total_returns"]
            else:  # drawdown
                score = -metrics["max_drawdown"]  # Negative because we want to minimize drawdown
            
            # Log metrics to MLflow
            mlflow.log_metrics({
                "sharpe_ratio": metrics["sharpe_ratio"],
                "total_returns": metrics["total_returns"],
                "max_drawdown": metrics["max_drawdown"],
                "win_rate": metrics["win_rate"]
            })
            
            return score
        
        try:
            # Create study for hyperparameter optimization
            study = optuna.create_study(direction="maximize")
            study.optimize(objective, n_trials=n_trials)
            
            # Get best parameters and metrics
            best_params = study.best_params
            best_value = study.best_value
            
            # Run final backtest with best parameters
            returns, metrics = await self.backtest_strategy(
                historical_data, {**strategy_config, **best_params}
            )
            
            return {
                "optimized_params": best_params,
                "performance_metrics": metrics,
                "optimization_score": best_value
            }
        except Exception as e:
            print(f"Error in strategy optimization: {str(e)}")
            return {}
    
    async def backtest_strategy(self, data: pd.DataFrame,
                              strategy_params: Dict) -> Tuple[pd.Series, Dict]:
        """Run strategy backtest and calculate performance metrics."""
        try:
            # Initialize variables
            position = 0
            positions = []
            returns = []
            equity = 100000  # Initial capital
            trades = []
            
            # Apply strategy rules
            for i in range(len(data)):
                if i < strategy_params.get("lookback_period", 20):
                    positions.append(position)
                    returns.append(0)
                    continue
                
                # Get signals based on strategy type
                if strategy_params["type"] == "trend_following":
                    signal = self._get_trend_signal(data, i, strategy_params)
                elif strategy_params["type"] == "mean_reversion":
                    signal = self._get_reversion_signal(data, i, strategy_params)
                else:
                    signal = 0
                
                # Apply position sizing and risk management
                if signal != 0 and position == 0:
                    # Enter position
                    position = signal
                    entry_price = data.iloc[i]["close"]
                    position_size = equity * strategy_params["position_size"]
                    shares = position_size / entry_price
                    trades.append({
                        "type": "entry",
                        "price": entry_price,
                        "shares": shares,
                        "timestamp": data.index[i]
                    })
                
                elif position != 0:
                    # Check exit conditions
                    exit_signal = self._check_exit_conditions(
                        data, i, position, entry_price, strategy_params
                    )
                    
                    if exit_signal:
                        # Exit position
                        exit_price = data.iloc[i]["close"]
                        trade_return = (exit_price - entry_price) / entry_price * position
                        returns.append(trade_return)
                        equity *= (1 + trade_return)
                        position = 0
                        trades.append({
                            "type": "exit",
                            "price": exit_price,
                            "shares": shares,
                            "timestamp": data.index[i],
                            "return": trade_return
                        })
                
                positions.append(position)
                returns.append(0 if position == 0 else 
                             (data.iloc[i]["close"] - data.iloc[i-1]["close"]) / 
                             data.iloc[i-1]["close"] * position)
            
            # Calculate performance metrics
            returns_series = pd.Series(returns, index=data.index)
            metrics = self._calculate_metrics(returns_series, trades)
            
            return returns_series, metrics
        
        except Exception as e:
            print(f"Error in strategy backtest: {str(e)}")
            return pd.Series(), {}
    
    def _get_trend_signal(self, data: pd.DataFrame, i: int,
                         params: Dict) -> int:
        """Calculate trend following signal."""
        try:
            trend_period = params["trend_period"]
            momentum_period = params["momentum_period"]
            
            # Calculate trend
            trend = data.iloc[i-trend_period:i]["close"].mean()
            short_trend = data.iloc[i-momentum_period:i]["close"].mean()
            
            # Calculate momentum
            momentum = (data.iloc[i]["close"] - data.iloc[i-momentum_period]["close"]) / \
                      data.iloc[i-momentum_period]["close"]
            
            # Generate signal
            if short_trend > trend and momentum > params["entry_threshold"]:
                return 1  # Long signal
            elif short_trend < trend and momentum < -params["entry_threshold"]:
                return -1  # Short signal
            
            return 0
        except Exception as e:
            print(f"Error calculating trend signal: {str(e)}")
            return 0
    
    def _get_reversion_signal(self, data: pd.DataFrame, i: int,
                            params: Dict) -> int:
        """Calculate mean reversion signal."""
        try:
            mean_period = params["mean_period"]
            std_multiplier = params["std_multiplier"]
            
            # Calculate mean and standard deviation
            mean = data.iloc[i-mean_period:i]["close"].mean()
            std = data.iloc[i-mean_period:i]["close"].std()
            current_price = data.iloc[i]["close"]
            
            # Generate signal
            if current_price < mean - std * std_multiplier:
                return 1  # Long signal (oversold)
            elif current_price > mean + std * std_multiplier:
                return -1  # Short signal (overbought)
            
            return 0
        except Exception as e:
            print(f"Error calculating reversion signal: {str(e)}")
            return 0
    
    def _check_exit_conditions(self, data: pd.DataFrame, i: int,
                             position: int, entry_price: float,
                             params: Dict) -> bool:
        """Check if position should be exited."""
        current_price = data.iloc[i]["close"]
        price_change = (current_price - entry_price) / entry_price
        
        # Check stop loss
        if price_change * position < -params["stop_loss"]:
            return True
        
        # Check take profit
        if price_change * position > params["take_profit"]:
            return True
        
        # Check exit threshold
        if position == 1 and price_change < -params["exit_threshold"]:
            return True
        elif position == -1 and price_change > params["exit_threshold"]:
            return True
        
        return False
    
    def _calculate_metrics(self, returns: pd.Series, trades: List[Dict]) -> Dict:
        """Calculate strategy performance metrics."""
        try:
            total_returns = (1 + returns).prod() - 1
            sharpe = self._calculate_sharpe_ratio(returns)
            drawdown = self._calculate_max_drawdown(returns)
            
            # Calculate win rate
            winning_trades = sum(1 for t in trades if t.get("return", 0) > 0)
            total_trades = len([t for t in trades if t.get("return") is not None])
            win_rate = winning_trades / total_trades if total_trades > 0 else 0
            
            return {
                "total_returns": total_returns,
                "sharpe_ratio": sharpe,
                "max_drawdown": drawdown,
                "win_rate": win_rate,
                "total_trades": total_trades
            }
        except Exception as e:
            print(f"Error calculating metrics: {str(e)}")
            return {}
    
    def _calculate_sharpe_ratio(self, returns: pd.Series) -> float:
        """Calculate annualized Sharpe ratio."""
        if len(returns) == 0:
            return 0
        
        excess_returns = returns - self.risk_free_rate / 252  # Daily risk-free rate
        if excess_returns.std() == 0:
            return 0
        
        sharpe = np.sqrt(252) * excess_returns.mean() / excess_returns.std()
        return sharpe
    
    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """Calculate maximum drawdown."""
        if len(returns) == 0:
            return 0
        
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return abs(drawdown.min())
