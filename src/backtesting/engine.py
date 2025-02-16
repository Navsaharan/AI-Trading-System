from typing import Dict, List, Optional, Union, Callable
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import asyncio
from ..utils.market_data import MarketData
from ..core.trading_engine import TradingEngine
from ..core.risk_manager import RiskManager
from ..strategies.strategy_builder import AIStrategyBuilder

class BacktestEngine:
    """Advanced backtesting engine with AI strategy optimization."""
    
    def __init__(self):
        self.market_data = MarketData()
        self.strategy_builder = AIStrategyBuilder()
        self.commission_rate = 0.001  # 0.1%
        self.slippage_model = "basic"  # basic, advanced, or custom
        
    async def run_backtest(self, strategy: Union[Dict, str],
                          symbols: List[str],
                          start_date: datetime,
                          end_date: datetime,
                          initial_capital: float = 100000,
                          position_size: Optional[float] = None,
                          risk_params: Optional[Dict] = None) -> Dict:
        """Run comprehensive backtest of a trading strategy."""
        try:
            # Initialize backtest parameters
            self.capital = initial_capital
            self.positions = {}
            self.trades = []
            self.equity_curve = []
            
            # Get historical data
            data = await self._get_historical_data(symbols, start_date, end_date)
            
            # Convert string strategy to executable
            if isinstance(strategy, str):
                strategy = await self.strategy_builder.build_strategy(strategy)
            
            # Run simulation
            for timestamp, prices in data.iterrows():
                # Update positions
                self._update_positions(prices)
                
                # Get strategy signals
                signals = await self._get_strategy_signals(
                    strategy, prices, timestamp
                )
                
                # Execute trades
                for signal in signals:
                    await self._execute_trade(
                        signal,
                        prices[signal["symbol"]],
                        timestamp,
                        position_size
                    )
                
                # Record equity
                self.equity_curve.append({
                    "timestamp": timestamp,
                    "equity": self._calculate_equity(prices),
                    "cash": self.capital
                })
            
            # Calculate performance metrics
            metrics = self._calculate_performance_metrics()
            
            # Generate detailed report
            report = self._generate_backtest_report(metrics)
            
            return {
                "metrics": metrics,
                "trades": self.trades,
                "equity_curve": self.equity_curve,
                "report": report,
                "optimization": await self._optimize_strategy(
                    strategy, data, metrics
                )
            }
        except Exception as e:
            print(f"Error running backtest: {str(e)}")
            return {}
    
    async def optimize_parameters(self, strategy: Dict,
                                param_ranges: Dict,
                                optimization_metric: str = "sharpe_ratio",
                                num_iterations: int = 100) -> Dict:
        """Optimize strategy parameters using AI and genetic algorithms."""
        try:
            # Initialize optimization
            best_params = None
            best_metric = float("-inf")
            results = []
            
            # Generate parameter combinations
            param_combinations = self._generate_param_combinations(
                param_ranges,
                num_iterations
            )
            
            # Test each combination
            for params in param_combinations:
                # Update strategy parameters
                test_strategy = self._update_strategy_params(strategy, params)
                
                # Run backtest with parameters
                backtest_result = await self.run_backtest(
                    test_strategy,
                    strategy["symbols"],
                    strategy["start_date"],
                    strategy["end_date"]
                )
                
                # Record results
                metric_value = backtest_result["metrics"][optimization_metric]
                results.append({
                    "parameters": params,
                    "metric": metric_value,
                    "metrics": backtest_result["metrics"]
                })
                
                # Update best parameters
                if metric_value > best_metric:
                    best_metric = metric_value
                    best_params = params
            
            # Analyze parameter sensitivity
            sensitivity = self._analyze_parameter_sensitivity(results)
            
            return {
                "best_parameters": best_params,
                "best_metric": best_metric,
                "all_results": results,
                "parameter_sensitivity": sensitivity,
                "optimization_metric": optimization_metric
            }
        except Exception as e:
            print(f"Error optimizing parameters: {str(e)}")
            return {}
    
    async def run_monte_carlo(self, strategy: Dict,
                            num_simulations: int = 1000) -> Dict:
        """Run Monte Carlo simulation to analyze strategy robustness."""
        try:
            simulations = []
            metrics = []
            
            # Run multiple simulations
            for i in range(num_simulations):
                # Add random noise to prices
                noisy_data = self._add_price_noise(strategy["historical_data"])
                
                # Run backtest with noisy data
                result = await self.run_backtest(
                    strategy,
                    strategy["symbols"],
                    strategy["start_date"],
                    strategy["end_date"],
                    data=noisy_data
                )
                
                simulations.append(result["equity_curve"])
                metrics.append(result["metrics"])
            
            # Calculate confidence intervals
            confidence_intervals = self._calculate_confidence_intervals(
                simulations
            )
            
            # Analyze risk metrics
            risk_analysis = self._analyze_simulation_risk(metrics)
            
            return {
                "confidence_intervals": confidence_intervals,
                "risk_analysis": risk_analysis,
                "worst_case": self._get_worst_case_scenario(simulations),
                "best_case": self._get_best_case_scenario(simulations),
                "probability_analysis": self._analyze_probability_distribution(
                    metrics
                )
            }
        except Exception as e:
            print(f"Error running Monte Carlo simulation: {str(e)}")
            return {}
    
    async def analyze_strategy(self, strategy: Dict) -> Dict:
        """Perform comprehensive strategy analysis."""
        try:
            # Run basic backtest
            backtest_result = await self.run_backtest(strategy)
            
            # Analyze strategy characteristics
            characteristics = self._analyze_strategy_characteristics(
                strategy,
                backtest_result
            )
            
            # Analyze market regimes
            regime_analysis = await self._analyze_market_regimes(
                strategy,
                backtest_result
            )
            
            # Analyze risk factors
            risk_analysis = self._analyze_risk_factors(backtest_result)
            
            return {
                "backtest_result": backtest_result,
                "characteristics": characteristics,
                "regime_analysis": regime_analysis,
                "risk_analysis": risk_analysis,
                "recommendations": self._generate_strategy_recommendations(
                    characteristics,
                    regime_analysis,
                    risk_analysis
                )
            }
        except Exception as e:
            print(f"Error analyzing strategy: {str(e)}")
            return {}
    
    async def _get_historical_data(self, symbols: List[str],
                                 start_date: datetime,
                                 end_date: datetime) -> pd.DataFrame:
        """Get historical price data for backtesting."""
        data = {}
        for symbol in symbols:
            hist_data = await self.market_data.get_historical_data(
                symbol,
                start_date=start_date,
                end_date=end_date
            )
            data[symbol] = hist_data["Close"]
        return pd.DataFrame(data)
    
    async def _get_strategy_signals(self, strategy: Dict,
                                  prices: pd.Series,
                                  timestamp: datetime) -> List[Dict]:
        """Get trading signals from strategy."""
        try:
            if callable(strategy.get("generate_signals")):
                return strategy["generate_signals"](prices, timestamp)
            
            # Default signal generation
            signals = []
            for symbol in prices.index:
                if self._should_enter_long(strategy, prices, symbol):
                    signals.append({
                        "symbol": symbol,
                        "side": "BUY",
                        "type": "MARKET"
                    })
                elif self._should_exit_long(strategy, prices, symbol):
                    signals.append({
                        "symbol": symbol,
                        "side": "SELL",
                        "type": "MARKET"
                    })
            
            return signals
        except Exception:
            return []
    
    async def _execute_trade(self, signal: Dict, price: float,
                           timestamp: datetime,
                           position_size: Optional[float] = None) -> None:
        """Execute trade in backtest."""
        try:
            symbol = signal["symbol"]
            side = signal["side"]
            
            # Calculate position size
            if position_size:
                size = position_size
            else:
                size = self.capital * 0.1  # 10% of capital
            
            # Apply slippage
            executed_price = self._apply_slippage(price, side)
            
            # Calculate commission
            commission = size * self.commission_rate
            
            # Update positions and capital
            if side == "BUY":
                self.positions[symbol] = {
                    "size": size / executed_price,
                    "entry_price": executed_price
                }
                self.capital -= (size + commission)
            else:
                position = self.positions.pop(symbol, None)
                if position:
                    self.capital += (position["size"] * executed_price - commission)
            
            # Record trade
            self.trades.append({
                "timestamp": timestamp,
                "symbol": symbol,
                "side": side,
                "price": executed_price,
                "size": size,
                "commission": commission
            })
        except Exception as e:
            print(f"Error executing trade: {str(e)}")
    
    def _calculate_equity(self, prices: pd.Series) -> float:
        """Calculate current portfolio equity."""
        try:
            position_value = sum(
                pos["size"] * prices[symbol]
                for symbol, pos in self.positions.items()
            )
            return self.capital + position_value
        except Exception:
            return self.capital
    
    def _calculate_performance_metrics(self) -> Dict:
        """Calculate comprehensive performance metrics."""
        try:
            equity_series = pd.Series(
                [e["equity"] for e in self.equity_curve],
                index=[e["timestamp"] for e in self.equity_curve]
            )
            
            returns = equity_series.pct_change()
            
            return {
                "total_return": (equity_series.iloc[-1] / equity_series.iloc[0]) - 1,
                "annualized_return": self._calculate_annualized_return(returns),
                "sharpe_ratio": self._calculate_sharpe_ratio(returns),
                "max_drawdown": self._calculate_max_drawdown(equity_series),
                "win_rate": self._calculate_win_rate(),
                "profit_factor": self._calculate_profit_factor(),
                "alpha": self._calculate_alpha(returns),
                "beta": self._calculate_beta(returns),
                "sortino_ratio": self._calculate_sortino_ratio(returns),
                "calmar_ratio": self._calculate_calmar_ratio(returns, equity_series),
                "trades_analysis": self._analyze_trades()
            }
        except Exception:
            return {}
    
    def _generate_backtest_report(self, metrics: Dict) -> Dict:
        """Generate detailed backtest report."""
        try:
            return {
                "summary": {
                    "total_trades": len(self.trades),
                    "profitable_trades": sum(1 for t in self.trades if t["side"] == "SELL" and t["price"] > t["entry_price"]),
                    "losing_trades": sum(1 for t in self.trades if t["side"] == "SELL" and t["price"] < t["entry_price"]),
                    "total_commission": sum(t["commission"] for t in self.trades),
                    "largest_win": self._get_largest_win(),
                    "largest_loss": self._get_largest_loss(),
                    "average_win": self._get_average_win(),
                    "average_loss": self._get_average_loss(),
                    "max_consecutive_wins": self._get_max_consecutive_wins(),
                    "max_consecutive_losses": self._get_max_consecutive_losses()
                },
                "metrics": metrics,
                "monthly_returns": self._calculate_monthly_returns(),
                "drawdown_analysis": self._analyze_drawdowns(),
                "risk_metrics": self._calculate_risk_metrics(),
                "position_analysis": self._analyze_positions()
            }
        except Exception:
            return {}
    
    async def _optimize_strategy(self, strategy: Dict,
                               data: pd.DataFrame,
                               metrics: Dict) -> Dict:
        """Optimize strategy using AI."""
        try:
            # Identify areas for improvement
            improvements = self._identify_improvements(metrics)
            
            # Generate optimization suggestions
            suggestions = []
            for improvement in improvements:
                if improvement["type"] == "parameter":
                    suggestion = await self._optimize_parameters(
                        strategy,
                        improvement["parameter"]
                    )
                elif improvement["type"] == "rule":
                    suggestion = await self._optimize_rules(
                        strategy,
                        improvement["rule"]
                    )
                suggestions.append(suggestion)
            
            return {
                "improvements": improvements,
                "suggestions": suggestions,
                "estimated_impact": self._estimate_optimization_impact(
                    suggestions
                )
            }
        except Exception:
            return {}
    
    def _apply_slippage(self, price: float, side: str) -> float:
        """Apply slippage model to price."""
        try:
            if self.slippage_model == "basic":
                slippage = price * 0.0001  # 0.01% basic slippage
            elif self.slippage_model == "advanced":
                slippage = self._calculate_advanced_slippage(price, side)
            else:
                slippage = 0
            
            return price * (1 + slippage) if side == "BUY" else price * (1 - slippage)
        except Exception:
            return price
    
    def _calculate_advanced_slippage(self, price: float, side: str) -> float:
        """Calculate advanced slippage based on volatility and volume."""
        # Implementation for advanced slippage model
        return 0.0002  # 0.02% advanced slippage
    
    def _generate_param_combinations(self, param_ranges: Dict,
                                   num_iterations: int) -> List[Dict]:
        """Generate parameter combinations for optimization."""
        combinations = []
        for _ in range(num_iterations):
            params = {}
            for param, range_values in param_ranges.items():
                if isinstance(range_values, list):
                    params[param] = np.random.choice(range_values)
                elif isinstance(range_values, tuple):
                    params[param] = np.random.uniform(*range_values)
            combinations.append(params)
        return combinations
    
    def _analyze_parameter_sensitivity(self, results: List[Dict]) -> Dict:
        """Analyze parameter sensitivity to performance."""
        try:
            sensitivity = {}
            for result in results:
                for param, value in result["parameters"].items():
                    if param not in sensitivity:
                        sensitivity[param] = []
                    sensitivity[param].append({
                        "value": value,
                        "metric": result["metric"]
                    })
            
            # Calculate correlation for each parameter
            correlations = {}
            for param, values in sensitivity.items():
                param_values = [v["value"] for v in values]
                metric_values = [v["metric"] for v in values]
                correlations[param] = np.corrcoef(param_values, metric_values)[0, 1]
            
            return {
                "correlations": correlations,
                "most_sensitive": max(correlations.items(), key=lambda x: abs(x[1]))[0]
            }
        except Exception:
            return {}
