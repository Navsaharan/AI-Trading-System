import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd
from textblob import TextBlob
from concurrent.futures import ThreadPoolExecutor
import asyncio
from dataclasses import dataclass
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

@dataclass
class AIScore:
    company_score: float
    stock_score: float
    past_score: float
    current_score: float
    news_score: float
    final_score: float
    confidence: float
    timestamp: datetime
    execution_time: float
    metrics: Dict[str, float]
    predictions: Dict[str, float]

class AIScoringService:
    def __init__(self, fast_mode: bool = False):
        self.fast_mode = fast_mode
        self.scaler = StandardScaler()
        self.model = RandomForestRegressor(n_estimators=100)
        self.score_weights = {
            'company': 0.25,
            'stock': 0.25,
            'past': 0.15,
            'current': 0.20,
            'news': 0.15
        }
        self.score_history = {}
        self.max_threads = 4

    async def calculate_stock_score(self, 
                                  symbol: str,
                                  company_data: Dict,
                                  stock_data: Dict,
                                  news_data: List[Dict],
                                  market_data: Dict) -> AIScore:
        """Calculate comprehensive AI score for a stock"""
        start_time = datetime.now()

        try:
            if self.fast_mode:
                # Fast mode for millisecond trading
                scores = await self._calculate_fast_scores(symbol, stock_data, market_data)
            else:
                # Full analysis mode
                scores = await self._calculate_full_scores(
                    symbol, company_data, stock_data, news_data, market_data
                )

            final_score = self._calculate_final_score(scores)
            confidence = self._calculate_confidence(scores)
            execution_time = (datetime.now() - start_time).total_seconds()

            ai_score = AIScore(
                company_score=scores['company'],
                stock_score=scores['stock'],
                past_score=scores['past'],
                current_score=scores['current'],
                news_score=scores['news'],
                final_score=final_score,
                confidence=confidence,
                timestamp=datetime.now(),
                execution_time=execution_time,
                metrics=self._get_key_metrics(scores),
                predictions=self._get_predictions(scores)
            )

            # Store score history
            self._update_score_history(symbol, ai_score)

            return ai_score

        except Exception as e:
            print(f"Error calculating AI score: {e}")
            return None

    async def _calculate_full_scores(self,
                                   symbol: str,
                                   company_data: Dict,
                                   stock_data: Dict,
                                   news_data: List[Dict],
                                   market_data: Dict) -> Dict[str, float]:
        """Calculate detailed scores using all available data"""
        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = {
                'company': executor.submit(self._analyze_company, company_data),
                'stock': executor.submit(self._analyze_stock, stock_data),
                'past': executor.submit(self._analyze_past_performance, symbol),
                'current': executor.submit(self._analyze_current_market, stock_data, market_data),
                'news': executor.submit(self._analyze_news, news_data)
            }

            return {k: future.result() for k, future in futures.items()}

    async def _calculate_fast_scores(self,
                                   symbol: str,
                                   stock_data: Dict,
                                   market_data: Dict) -> Dict[str, float]:
        """Calculate simplified scores for high-frequency trading"""
        return {
            'company': self._get_cached_score(symbol, 'company'),
            'stock': self._analyze_stock_fast(stock_data),
            'past': self._get_cached_score(symbol, 'past'),
            'current': self._analyze_current_market_fast(stock_data, market_data),
            'news': self._get_cached_score(symbol, 'news')
        }

    def _analyze_company(self, company_data: Dict) -> float:
        """Analyze company fundamentals"""
        metrics = {
            'pe_ratio': self._normalize_metric(company_data.get('pe_ratio', 0), 0, 50),
            'profit_margin': self._normalize_metric(company_data.get('profit_margin', 0), 0, 1),
            'debt_equity': self._normalize_metric(company_data.get('debt_to_equity', 0), 0, 2),
            'current_ratio': self._normalize_metric(company_data.get('current_ratio', 0), 0, 3),
            'roe': self._normalize_metric(company_data.get('return_on_equity', 0), 0, 1),
            'revenue_growth': self._normalize_metric(company_data.get('revenue_growth', 0), -1, 1)
        }

        weights = {
            'pe_ratio': 0.2,
            'profit_margin': 0.2,
            'debt_equity': 0.15,
            'current_ratio': 0.15,
            'roe': 0.15,
            'revenue_growth': 0.15
        }

        return sum(metrics[k] * weights[k] for k in metrics) * 100

    def _analyze_stock(self, stock_data: Dict) -> float:
        """Analyze stock performance and technical indicators"""
        metrics = {
            'trend': self._analyze_trend(stock_data['price_history']),
            'volatility': self._analyze_volatility(stock_data['price_history']),
            'momentum': self._analyze_momentum(stock_data['price_history']),
            'volume': self._analyze_volume(stock_data['volume_history']),
            'technical': self._analyze_technical_indicators(stock_data)
        }

        weights = {
            'trend': 0.25,
            'volatility': 0.20,
            'momentum': 0.20,
            'volume': 0.15,
            'technical': 0.20
        }

        return sum(metrics[k] * weights[k] for k in metrics) * 100

    def _analyze_stock_fast(self, stock_data: Dict) -> float:
        """Quick analysis of stock for high-frequency trading"""
        recent_prices = stock_data['price_history'][-10:]
        recent_volumes = stock_data['volume_history'][-10:]

        metrics = {
            'price_change': (recent_prices[-1] / recent_prices[0] - 1) * 100,
            'volume_change': (recent_volumes[-1] / np.mean(recent_volumes) - 1) * 100,
            'price_volatility': np.std(recent_prices) / np.mean(recent_prices) * 100
        }

        return self._normalize_fast_metrics(metrics)

    def _analyze_past_performance(self, symbol: str) -> float:
        """Analyze historical AI prediction accuracy"""
        if symbol not in self.score_history:
            return 50.0  # Default score for new stocks

        history = self.score_history[symbol]
        if len(history) < 2:
            return 50.0

        # Calculate prediction accuracy
        predictions = [score.predictions for score in history[:-1]]
        actuals = [self._get_actual_values(score) for score in history[1:]]
        
        accuracy = self._calculate_prediction_accuracy(predictions, actuals)
        return accuracy * 100

    def _analyze_current_market(self, stock_data: Dict, market_data: Dict) -> float:
        """Analyze current market conditions"""
        metrics = {
            'market_trend': self._analyze_market_trend(market_data),
            'sector_performance': self._analyze_sector_performance(market_data),
            'correlation': self._analyze_market_correlation(stock_data, market_data),
            'liquidity': self._analyze_liquidity(stock_data),
            'sentiment': self._analyze_market_sentiment(market_data)
        }

        weights = {
            'market_trend': 0.25,
            'sector_performance': 0.20,
            'correlation': 0.20,
            'liquidity': 0.15,
            'sentiment': 0.20
        }

        return sum(metrics[k] * weights[k] for k in metrics) * 100

    def _analyze_current_market_fast(self, stock_data: Dict, market_data: Dict) -> float:
        """Quick analysis of current market conditions"""
        recent_market = market_data['index_values'][-5:]
        recent_stock = stock_data['price_history'][-5:]

        metrics = {
            'market_direction': (recent_market[-1] / recent_market[0] - 1) * 100,
            'stock_correlation': np.corrcoef(recent_market, recent_stock)[0, 1]
        }

        return self._normalize_fast_metrics(metrics)

    def _analyze_news(self, news_data: List[Dict]) -> float:
        """Analyze news sentiment and impact"""
        if not news_data:
            return 50.0

        sentiments = []
        for news in news_data:
            sentiment = self._analyze_news_sentiment(news['title'] + ' ' + news['content'])
            impact = self._analyze_news_impact(news)
            sentiments.append(sentiment * impact)

        return np.mean(sentiments) * 100

    def _analyze_news_sentiment(self, text: str) -> float:
        """Analyze sentiment of news text"""
        blob = TextBlob(text)
        return (blob.sentiment.polarity + 1) / 2  # Normalize to 0-1

    def _analyze_news_impact(self, news: Dict) -> float:
        """Analyze potential impact of news"""
        impact_factors = {
            'source_reliability': 0.3,
            'recency': 0.3,
            'relevance': 0.4
        }

        scores = {
            'source_reliability': self._get_source_reliability(news['source']),
            'recency': self._calculate_recency_score(news['timestamp']),
            'relevance': self._calculate_relevance_score(news['categories'])
        }

        return sum(scores[k] * impact_factors[k] for k in scores)

    def _calculate_final_score(self, scores: Dict[str, float]) -> float:
        """Calculate final weighted AI score"""
        return sum(scores[k] * self.score_weights[k] for k in scores)

    def _calculate_confidence(self, scores: Dict[str, float]) -> float:
        """Calculate confidence level in the AI score"""
        score_std = np.std(list(scores.values()))
        consistency = 1 - (score_std / 100)  # Higher consistency = lower std dev
        
        # Consider historical accuracy
        historical_accuracy = np.mean([s.confidence for s in self.score_history.get(symbol, [])] or [0.5])
        
        return (consistency * 0.7 + historical_accuracy * 0.3) * 100

    def _normalize_metric(self, value: float, min_val: float, max_val: float) -> float:
        """Normalize a metric to 0-1 range"""
        if value is None:
            return 0.5
        return max(0, min(1, (value - min_val) / (max_val - min_val)))

    def _normalize_fast_metrics(self, metrics: Dict[str, float]) -> float:
        """Normalize metrics for fast scoring"""
        values = np.array(list(metrics.values()))
        return np.mean(np.clip(values, -100, 100)) + 50

    def _get_cached_score(self, symbol: str, score_type: str) -> float:
        """Get cached score for fast mode"""
        if symbol in self.score_history:
            latest_score = self.score_history[symbol][-1]
            return getattr(latest_score, f"{score_type}_score")
        return 50.0

    def _update_score_history(self, symbol: str, score: AIScore):
        """Update score history"""
        if symbol not in self.score_history:
            self.score_history[symbol] = []
        
        self.score_history[symbol].append(score)
        # Keep last 100 scores
        self.score_history[symbol] = self.score_history[symbol][-100:]

    def _get_key_metrics(self, scores: Dict[str, float]) -> Dict[str, float]:
        """Get key metrics for the score"""
        return {
            'volatility': scores.get('stock', 0) * 0.4,
            'momentum': scores.get('current', 0) * 0.3,
            'sentiment': scores.get('news', 0) * 0.3
        }

    def _get_predictions(self, scores: Dict[str, float]) -> Dict[str, float]:
        """Generate price predictions"""
        return {
            'short_term': self._predict_price(scores, 'short'),
            'medium_term': self._predict_price(scores, 'medium'),
            'long_term': self._predict_price(scores, 'long')
        }

    def _predict_price(self, scores: Dict[str, float], term: str) -> float:
        """Predict price movement"""
        weights = {
            'short': {'current': 0.4, 'news': 0.3, 'stock': 0.3},
            'medium': {'stock': 0.4, 'company': 0.3, 'current': 0.3},
            'long': {'company': 0.4, 'past': 0.3, 'stock': 0.3}
        }

        term_weights = weights[term]
        prediction = sum(scores[k] * term_weights[k] for k in term_weights)
        return (prediction - 50) / 50  # Convert to percentage change
