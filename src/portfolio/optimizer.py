from typing import Dict, List, Optional
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from datetime import datetime, timedelta
from ..utils.market_data import MarketData
from ..analysis.sentiment_analyzer import SentimentAnalyzer

class PortfolioOptimizer:
    """AI-powered portfolio optimization and rebalancing system."""
    
    def __init__(self):
        self.market_data = MarketData()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.risk_free_rate = 0.05  # 5% annual risk-free rate
        
    async def optimize_portfolio(self, symbols: List[str],
                               investment_amount: float,
                               risk_tolerance: float = 0.5,
                               constraints: Optional[Dict] = None) -> Dict:
        """Optimize portfolio allocation using modern portfolio theory and AI."""
        try:
            # Get historical data
            historical_data = await self._get_historical_data(symbols)
            
            # Calculate returns and covariance
            returns = historical_data.pct_change()
            mean_returns = returns.mean()
            cov_matrix = returns.cov()
            
            # Get sentiment scores
            sentiment_scores = await self._get_sentiment_scores(symbols)
            
            # Adjust returns based on sentiment
            adjusted_returns = self._adjust_returns_with_sentiment(
                mean_returns, sentiment_scores
            )
            
            # Optimize portfolio
            weights = await self._optimize_weights(
                adjusted_returns,
                cov_matrix,
                risk_tolerance,
                constraints
            )
            
            # Calculate portfolio metrics
            metrics = self._calculate_portfolio_metrics(
                weights,
                adjusted_returns,
                cov_matrix
            )
            
            # Generate allocation plan
            allocation = self._generate_allocation_plan(
                weights,
                investment_amount,
                symbols
            )
            
            return {
                "weights": dict(zip(symbols, weights)),
                "metrics": metrics,
                "allocation": allocation,
                "rebalancing_needed": await self._check_rebalancing_need(
                    symbols, weights
                ),
                "risk_analysis": await self._analyze_portfolio_risk(
                    symbols, weights
                ),
                "timestamp": datetime.now()
            }
        except Exception as e:
            print(f"Error optimizing portfolio: {str(e)}")
            return {}
    
    async def rebalance_portfolio(self, current_portfolio: Dict,
                                target_weights: Dict) -> Dict:
        """Generate rebalancing trades to match target allocation."""
        try:
            rebalancing_trades = []
            total_value = sum(
                holding["quantity"] * await self._get_current_price(symbol)
                for symbol, holding in current_portfolio.items()
            )
            
            for symbol, target_weight in target_weights.items():
                current_holding = current_portfolio.get(symbol, {"quantity": 0})
                current_price = await self._get_current_price(symbol)
                
                current_value = current_holding["quantity"] * current_price
                current_weight = current_value / total_value
                
                target_value = total_value * target_weight
                value_difference = target_value - current_value
                
                if abs(value_difference) > total_value * 0.01:  # 1% threshold
                    quantity = abs(value_difference) / current_price
                    side = "BUY" if value_difference > 0 else "SELL"
                    
                    rebalancing_trades.append({
                        "symbol": symbol,
                        "side": side,
                        "quantity": quantity,
                        "estimated_value": abs(value_difference)
                    })
            
            return {
                "trades": rebalancing_trades,
                "total_value": total_value,
                "estimated_cost": sum(t["estimated_value"] * 0.001  # 0.1% commission
                                   for t in rebalancing_trades),
                "timestamp": datetime.now()
            }
        except Exception as e:
            print(f"Error generating rebalancing trades: {str(e)}")
            return {}
    
    async def optimize_for_tax_efficiency(self, portfolio: Dict,
                                        tax_rates: Dict) -> Dict:
        """Optimize portfolio for tax efficiency."""
        try:
            tax_efficient_trades = []
            
            for symbol, holding in portfolio.items():
                current_price = await self._get_current_price(symbol)
                unrealized_gain = (current_price - holding["avg_price"]) * \
                                holding["quantity"]
                
                if unrealized_gain > 0:
                    # Check for tax-loss harvesting opportunities
                    correlated_symbols = await self._find_correlated_symbols(symbol)
                    
                    for corr_symbol in correlated_symbols:
                        corr_performance = await self._get_performance(corr_symbol)
                        
                        if corr_performance["return"] < 0:
                            tax_efficient_trades.append({
                                "type": "tax_loss_harvest",
                                "sell_symbol": symbol,
                                "buy_symbol": corr_symbol,
                                "quantity": holding["quantity"],
                                "estimated_tax_saving": unrealized_gain * \
                                                      tax_rates["capital_gains"]
                            })
                
                # Check holding period for long-term capital gains
                days_held = (datetime.now() - holding["purchase_date"]).days
                if days_held < 365:  # Less than 1 year
                    days_to_long_term = 365 - days_held
                    tax_saving = unrealized_gain * \
                               (tax_rates["short_term"] - tax_rates["long_term"])
                    
                    if tax_saving > 100:  # Minimum tax saving threshold
                        tax_efficient_trades.append({
                            "type": "hold_for_long_term",
                            "symbol": symbol,
                            "days_remaining": days_to_long_term,
                            "estimated_tax_saving": tax_saving
                        })
            
            return {
                "trades": tax_efficient_trades,
                "estimated_savings": sum(t["estimated_tax_saving"]
                                      for t in tax_efficient_trades),
                "timestamp": datetime.now()
            }
        except Exception as e:
            print(f"Error optimizing tax efficiency: {str(e)}")
            return {}
    
    async def generate_investment_plan(self, investment_amount: float,
                                     time_horizon: int,
                                     risk_profile: str) -> Dict:
        """Generate long-term investment plan with periodic rebalancing."""
        try:
            # Define asset allocation based on risk profile
            allocation = self._get_risk_based_allocation(risk_profile)
            
            # Get recommended symbols for each asset class
            recommended_symbols = await self._get_recommended_symbols(allocation)
            
            # Optimize portfolio for each asset class
            optimized_portfolios = {}
            for asset_class, weight in allocation.items():
                symbols = recommended_symbols[asset_class]
                portfolio = await self.optimize_portfolio(
                    symbols,
                    investment_amount * weight,
                    self._get_risk_tolerance(risk_profile)
                )
                optimized_portfolios[asset_class] = portfolio
            
            # Generate investment schedule
            schedule = self._generate_investment_schedule(
                investment_amount,
                time_horizon
            )
            
            return {
                "allocation": allocation,
                "portfolios": optimized_portfolios,
                "schedule": schedule,
                "rebalancing_frequency": self._get_rebalancing_frequency(
                    risk_profile
                ),
                "expected_returns": self._calculate_expected_returns(
                    optimized_portfolios
                ),
                "risk_metrics": self._calculate_risk_metrics(optimized_portfolios),
                "timestamp": datetime.now()
            }
        except Exception as e:
            print(f"Error generating investment plan: {str(e)}")
            return {}
    
    async def _get_historical_data(self, symbols: List[str]) -> pd.DataFrame:
        """Get historical price data for symbols."""
        data = {}
        for symbol in symbols:
            hist_data = await self.market_data.get_historical_data(
                symbol,
                interval="1d",
                limit=252  # One year of trading days
            )
            data[symbol] = hist_data["Close"]
        return pd.DataFrame(data)
    
    async def _get_sentiment_scores(self, symbols: List[str]) -> Dict[str, float]:
        """Get sentiment scores for symbols."""
        scores = {}
        for symbol in symbols:
            sentiment = await self.sentiment_analyzer.analyze_stock_sentiment(
                symbol
            )
            scores[symbol] = sentiment["composite_score"]
        return scores
    
    def _adjust_returns_with_sentiment(self, returns: pd.Series,
                                     sentiment_scores: Dict[str, float]) -> pd.Series:
        """Adjust expected returns based on sentiment scores."""
        sentiment_adjustment = pd.Series(sentiment_scores)
        return returns + (sentiment_adjustment * 0.002)  # 0.2% adjustment per unit
    
    async def _optimize_weights(self, returns: pd.Series, cov_matrix: pd.DataFrame,
                              risk_tolerance: float,
                              constraints: Optional[Dict] = None) -> np.ndarray:
        """Optimize portfolio weights using efficient frontier."""
        num_assets = len(returns)
        
        # Define constraints
        bounds = [(0, 1) for _ in range(num_assets)]
        if constraints:
            bounds = [constraints.get(i, (0, 1)) for i in range(num_assets)]
        
        # Define objective function (negative Sharpe ratio)
        def objective(weights):
            portfolio_return = np.sum(returns * weights)
            portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_std
            return -sharpe_ratio
        
        # Optimize
        constraints = [
            {"type": "eq", "fun": lambda x: np.sum(x) - 1}  # Weights sum to 1
        ]
        
        result = minimize(
            objective,
            num_assets * [1./num_assets],  # Equal weight start
            method="SLSQP",
            bounds=bounds,
            constraints=constraints
        )
        
        return result.x
    
    def _calculate_portfolio_metrics(self, weights: np.ndarray,
                                   returns: pd.Series,
                                   cov_matrix: pd.DataFrame) -> Dict:
        """Calculate portfolio performance metrics."""
        portfolio_return = np.sum(returns * weights)
        portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_std
        
        # Calculate other risk metrics
        var_95 = -portfolio_std * 1.645  # 95% VaR
        cvar_95 = -portfolio_std * 2.063  # 95% CVaR
        
        return {
            "expected_return": portfolio_return,
            "volatility": portfolio_std,
            "sharpe_ratio": sharpe_ratio,
            "var_95": var_95,
            "cvar_95": cvar_95
        }
    
    def _generate_allocation_plan(self, weights: np.ndarray,
                                investment_amount: float,
                                symbols: List[str]) -> List[Dict]:
        """Generate detailed allocation plan."""
        return [
            {
                "symbol": symbol,
                "weight": weight,
                "amount": investment_amount * weight,
                "estimated_shares": (investment_amount * weight) / 100  # Placeholder price
            }
            for symbol, weight in zip(symbols, weights)
        ]
    
    async def _check_rebalancing_need(self, symbols: List[str],
                                    target_weights: np.ndarray) -> bool:
        """Check if portfolio needs rebalancing."""
        current_prices = {}
        for symbol in symbols:
            price = await self._get_current_price(symbol)
            current_prices[symbol] = price
        
        total_value = sum(current_prices.values())
        current_weights = np.array([p/total_value for p in current_prices.values()])
        
        return np.any(np.abs(current_weights - target_weights) > 0.05)  # 5% threshold
    
    async def _analyze_portfolio_risk(self, symbols: List[str],
                                    weights: np.ndarray) -> Dict:
        """Analyze portfolio risk factors."""
        try:
            risk_factors = {}
            
            # Analyze sector concentration
            sectors = await self._get_sectors(symbols)
            sector_weights = {}
            for symbol, weight, sector in zip(symbols, weights, sectors):
                sector_weights[sector] = sector_weights.get(sector, 0) + weight
            
            # Analyze geographic exposure
            geo_exposure = await self._get_geographic_exposure(symbols, weights)
            
            # Analyze correlation with market
            market_correlation = await self._calculate_market_correlation(
                symbols, weights
            )
            
            return {
                "sector_concentration": sector_weights,
                "geographic_exposure": geo_exposure,
                "market_correlation": market_correlation,
                "risk_factors": risk_factors
            }
        except Exception:
            return {}
    
    async def _get_current_price(self, symbol: str) -> float:
        """Get current price for a symbol."""
        price_data = await self.market_data.get_real_time_price(symbol)
        return price_data.get("price", 0)
    
    def _get_risk_based_allocation(self, risk_profile: str) -> Dict[str, float]:
        """Get asset allocation based on risk profile."""
        allocations = {
            "conservative": {
                "bonds": 0.6,
                "stocks": 0.3,
                "cash": 0.1
            },
            "moderate": {
                "bonds": 0.4,
                "stocks": 0.5,
                "alternatives": 0.1
            },
            "aggressive": {
                "stocks": 0.7,
                "alternatives": 0.2,
                "bonds": 0.1
            }
        }
        return allocations.get(risk_profile.lower(), allocations["moderate"])
    
    def _get_risk_tolerance(self, risk_profile: str) -> float:
        """Get risk tolerance level based on risk profile."""
        tolerances = {
            "conservative": 0.3,
            "moderate": 0.5,
            "aggressive": 0.8
        }
        return tolerances.get(risk_profile.lower(), 0.5)
    
    def _get_rebalancing_frequency(self, risk_profile: str) -> str:
        """Get recommended rebalancing frequency."""
        frequencies = {
            "conservative": "quarterly",
            "moderate": "semi-annually",
            "aggressive": "annually"
        }
        return frequencies.get(risk_profile.lower(), "quarterly")
    
    def _generate_investment_schedule(self, amount: float,
                                    time_horizon: int) -> List[Dict]:
        """Generate investment schedule with periodic investments."""
        monthly_investment = amount / (time_horizon * 12)
        
        schedule = []
        current_date = datetime.now()
        
        for month in range(time_horizon * 12):
            schedule.append({
                "date": current_date + timedelta(days=30*month),
                "amount": monthly_investment
            })
        
        return schedule
    
    def _calculate_expected_returns(self, portfolios: Dict) -> Dict:
        """Calculate expected returns for different time horizons."""
        returns = {}
        for horizon in [1, 3, 5, 10]:
            returns[f"{horizon}y"] = sum(
                p["metrics"]["expected_return"] * w
                for asset, p in portfolios.items()
                for w in p["weights"].values()
            ) * horizon
        return returns
    
    def _calculate_risk_metrics(self, portfolios: Dict) -> Dict:
        """Calculate comprehensive risk metrics."""
        total_var = 0
        total_cvar = 0
        
        for portfolio in portfolios.values():
            total_var += portfolio["metrics"]["var_95"]
            total_cvar += portfolio["metrics"]["cvar_95"]
        
        return {
            "var_95": total_var,
            "cvar_95": total_cvar,
            "max_drawdown": self._estimate_max_drawdown(portfolios)
        }
    
    def _estimate_max_drawdown(self, portfolios: Dict) -> float:
        """Estimate maximum drawdown based on historical data."""
        # Placeholder implementation
        return 0.2  # 20% estimated max drawdown
