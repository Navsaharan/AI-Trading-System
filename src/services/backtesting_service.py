from typing import Dict, List, Optional, Union
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import asyncio
import aiohttp
import json
import logging
from pathlib import Path
import ray
from concurrent.futures import ThreadPoolExecutor
import pyfolio as pf
import empyrical as emp
from scipy import stats
import torch
import tensorflow as tf
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import matplotlib.pyplot as plt
import seaborn as sns

class BacktestingService:
    def __init__(self, config_path: str = "config/backtesting_config.json"):
        self.initialize_service(config_path)
        self.setup_logging()
        self.initialize_metrics()
        
    def initialize_service(self, config_path: str):
        """Initialize backtesting service with configuration"""
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
                
            # Initialize Ray for parallel processing
            ray.init(
                address='auto',
                ignore_reinit_error=True,
                logging_level=logging.WARNING
            )
            
            self.setup_data_sources()
            logging.info("Backtesting service initialized")
            
        except Exception as e:
            logging.error(f"Error initializing backtesting service: {e}")
            raise

    def setup_data_sources(self):
        """Setup connections to various data sources"""
        self.data_sources = {
            "historical": {
                "oracle": self._connect_oracle_storage,
                "aws_s3": self._connect_aws_s3
            },
            "real_time": {
                "websocket": self._setup_websocket_connection,
                "api": self._setup_api_connection
            }
        }

    @ray.remote
    class BacktestWorker:
        """Distributed backtesting worker"""
        def __init__(self, strategy_config: Dict):
            self.strategy = self._initialize_strategy(strategy_config)
            self.metrics = self._initialize_metrics()

        def _initialize_strategy(self, config: Dict):
            """Initialize trading strategy"""
            return {
                "entry_rules": config.get("entry_rules", []),
                "exit_rules": config.get("exit_rules", []),
                "position_sizing": config.get("position_sizing", {}),
                "risk_management": config.get("risk_management", {})
            }

        def run_backtest(self, data: pd.DataFrame) -> Dict:
            """Run backtest on given data"""
            try:
                positions = []
                portfolio_value = []
                initial_capital = 100000

                for i in range(len(data)):
                    # Apply strategy rules
                    signal = self._apply_strategy_rules(data.iloc[i])
                    
                    # Calculate position size
                    position = self._calculate_position_size(signal, data.iloc[i])
                    
                    # Apply risk management
                    position = self._apply_risk_management(position, portfolio_value)
                    
                    positions.append(position)
                    
                    # Update portfolio value
                    pnl = self._calculate_pnl(position, data.iloc[i])
                    portfolio_value.append(initial_capital + sum(pnl))

                return {
                    "positions": positions,
                    "portfolio_value": portfolio_value,
                    "metrics": self._calculate_metrics(portfolio_value)
                }

            except Exception as e:
                logging.error(f"Error in backtest: {e}")
                return None

    async def run_parallel_backtests(self, strategies: List[Dict], data: pd.DataFrame) -> List[Dict]:
        """Run multiple backtests in parallel"""
        try:
            # Create workers for each strategy
            workers = [
                self.BacktestWorker.remote(strategy)
                for strategy in strategies
            ]
            
            # Run backtests in parallel
            futures = [
                worker.run_backtest.remote(data)
                for worker in workers
            ]
            
            # Get results
            results = await asyncio.gather(*[
                self._process_backtest_result(f)
                for f in futures
            ])
            
            return results
            
        except Exception as e:
            logging.error(f"Error in parallel backtests: {e}")
            return []

    async def optimize_strategy(self, strategy: Dict, data: pd.DataFrame) -> Dict:
        """Optimize strategy parameters"""
        try:
            # Define parameter space
            param_space = self._define_parameter_space(strategy)
            
            # Run parallel optimizations
            results = []
            for params in param_space:
                modified_strategy = self._update_strategy_params(strategy, params)
                result = await self.run_backtest(modified_strategy, data)
                results.append((params, result))
            
            # Find best parameters
            best_params = self._find_best_parameters(results)
            
            return best_params
            
        except Exception as e:
            logging.error(f"Error in strategy optimization: {e}")
            return {}

    def analyze_results(self, results: Dict) -> Dict:
        """Analyze backtest results"""
        try:
            analysis = {}
            
            # Performance metrics
            returns = self._calculate_returns(results['portfolio_value'])
            analysis['metrics'] = {
                'sharpe_ratio': emp.sharpe_ratio(returns),
                'sortino_ratio': emp.sortino_ratio(returns),
                'max_drawdown': emp.max_drawdown(returns),
                'annual_return': emp.annual_return(returns),
                'win_rate': self._calculate_win_rate(returns)
            }
            
            # Risk metrics
            analysis['risk'] = {
                'var_95': self._calculate_var(returns, 0.95),
                'cvar_95': self._calculate_cvar(returns, 0.95),
                'volatility': emp.annual_volatility(returns)
            }
            
            # Generate plots
            analysis['plots'] = self._generate_analysis_plots(results)
            
            return analysis
            
        except Exception as e:
            logging.error(f"Error in results analysis: {e}")
            return {}

    def _calculate_var(self, returns: pd.Series, confidence: float) -> float:
        """Calculate Value at Risk"""
        return np.percentile(returns, (1 - confidence) * 100)

    def _calculate_cvar(self, returns: pd.Series, confidence: float) -> float:
        """Calculate Conditional Value at Risk"""
        var = self._calculate_var(returns, confidence)
        return returns[returns <= var].mean()

    def _generate_analysis_plots(self, results: Dict) -> Dict:
        """Generate analysis plots"""
        plots = {}
        
        # Equity curve
        plt.figure(figsize=(12, 6))
        plt.plot(results['portfolio_value'])
        plt.title('Equity Curve')
        plots['equity_curve'] = plt.gcf()
        plt.close()
        
        # Returns distribution
        returns = np.diff(results['portfolio_value']) / results['portfolio_value'][:-1]
        plt.figure(figsize=(12, 6))
        sns.histplot(returns, kde=True)
        plt.title('Returns Distribution')
        plots['returns_dist'] = plt.gcf()
        plt.close()
        
        # Drawdown
        drawdown = self._calculate_drawdown(results['portfolio_value'])
        plt.figure(figsize=(12, 6))
        plt.plot(drawdown)
        plt.title('Drawdown')
        plots['drawdown'] = plt.gcf()
        plt.close()
        
        return plots

    def _calculate_drawdown(self, portfolio_value: List[float]) -> np.array:
        """Calculate drawdown series"""
        peak = np.maximum.accumulate(portfolio_value)
        drawdown = (portfolio_value - peak) / peak
        return drawdown

    def save_results(self, results: Dict, path: str):
        """Save backtest results"""
        try:
            # Save metrics
            metrics_path = Path(path) / 'metrics.json'
            with open(metrics_path, 'w') as f:
                json.dump(results['metrics'], f, indent=4)
            
            # Save plots
            plots_path = Path(path) / 'plots'
            plots_path.mkdir(exist_ok=True)
            for name, plot in results['plots'].items():
                plot.savefig(plots_path / f'{name}.png')
            
            # Save detailed results
            results_path = Path(path) / 'detailed_results.csv'
            pd.DataFrame({
                'portfolio_value': results['portfolio_value'],
                'positions': results['positions']
            }).to_csv(results_path)
            
            logging.info(f"Results saved to {path}")
            
        except Exception as e:
            logging.error(f"Error saving results: {e}")

    @staticmethod
    def _calculate_win_rate(returns: pd.Series) -> float:
        """Calculate win rate"""
        return (returns > 0).mean()

# Initialize backtesting service
backtester = BacktestingService()
