from typing import List, Dict, Optional
import aiohttp
import asyncio
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from transformers import pipeline
from textblob import TextBlob
import yfinance as yf
from bs4 import BeautifulSoup

class StockAnalysisService:
    def __init__(self):
        self.sentiment_analyzer = pipeline("sentiment-analysis")
        self.news_sources = {
            "moneycontrol": "https://www.moneycontrol.com/news/business/stocks/",
            "economic_times": "https://economictimes.indiatimes.com/markets/stocks/news/",
            "reuters": "https://www.reuters.com/markets/companies/"
        }
        
    async def get_stock_details(self, symbol: str, exchange: str = "NSE") -> Dict:
        """Get comprehensive stock details with AI predictions"""
        # Get basic stock info
        stock_info = await self._fetch_stock_info(symbol, exchange)
        
        # Get AI predictions and analysis
        analysis = await self._analyze_stock(symbol, exchange)
        
        # Get latest news and sentiment
        news = await self._fetch_stock_news(symbol)
        
        return {
            "basic_info": stock_info,
            "ai_analysis": analysis,
            "news": news,
            "timestamp": datetime.now().isoformat()
        }
    
    async def compare_stocks(self, symbol1: str, symbol2: str, exchange: str = "NSE") -> Dict:
        """Compare two stocks with AI analysis"""
        stock1 = await self.get_stock_details(symbol1, exchange)
        stock2 = await self.get_stock_details(symbol2, exchange)
        
        comparison = await self._generate_comparison(stock1, stock2)
        winner = await self._determine_better_stock(stock1, stock2)
        
        return {
            "comparison": comparison,
            "winner": winner,
            "stocks": {
                symbol1: stock1,
                symbol2: stock2
            }
        }
    
    async def _fetch_stock_info(self, symbol: str, exchange: str) -> Dict:
        """Fetch basic stock information"""
        try:
            # Use yfinance for basic info
            stock = yf.Ticker(f"{symbol}.{exchange}")
            info = stock.info
            
            # Get technical indicators
            hist = stock.history(period="1y")
            
            # Calculate key metrics
            rsi = self._calculate_rsi(hist['Close'])
            macd = self._calculate_macd(hist['Close'])
            bollinger = self._calculate_bollinger_bands(hist['Close'])
            
            return {
                "name": info.get('longName', ''),
                "sector": info.get('sector', ''),
                "industry": info.get('industry', ''),
                "market_cap": info.get('marketCap', 0),
                "pe_ratio": info.get('trailingPE', 0),
                "eps": info.get('trailingEps', 0),
                "dividend_yield": info.get('dividendYield', 0),
                "52w_high": info.get('fiftyTwoWeekHigh', 0),
                "52w_low": info.get('fiftyTwoWeekLow', 0),
                "volume": info.get('volume', 0),
                "avg_volume": info.get('averageVolume', 0),
                "technical_indicators": {
                    "rsi": rsi[-1],
                    "macd": macd[-1],
                    "bollinger": bollinger[-1]
                }
            }
        except Exception as e:
            print(f"Error fetching stock info: {e}")
            return {}
    
    async def _analyze_stock(self, symbol: str, exchange: str) -> Dict:
        """Perform AI analysis on the stock"""
        try:
            # Get historical data
            stock = yf.Ticker(f"{symbol}.{exchange}")
            hist = stock.history(period="1y")
            
            # Technical Analysis
            technical_score = await self._calculate_technical_score(hist)
            
            # Fundamental Analysis
            fundamental_score = await self._calculate_fundamental_score(stock.info)
            
            # Risk Analysis
            risk_score = await self._calculate_risk_score(hist)
            
            # Future Price Prediction
            price_prediction = await self._predict_future_price(hist)
            
            # Overall AI Score (0-100)
            ai_score = (technical_score + fundamental_score + (100 - risk_score)) / 3
            
            return {
                "ai_score": round(ai_score, 2),
                "technical_score": round(technical_score, 2),
                "fundamental_score": round(fundamental_score, 2),
                "risk_score": round(risk_score, 2),
                "price_prediction": {
                    "1d": price_prediction["1d"],
                    "1w": price_prediction["1w"],
                    "1m": price_prediction["1m"]
                },
                "recommendation": self._get_recommendation(ai_score),
                "confidence": self._get_confidence_level(ai_score)
            }
        except Exception as e:
            print(f"Error in AI analysis: {e}")
            return {}
    
    async def _fetch_stock_news(self, symbol: str) -> List[Dict]:
        """Fetch and analyze latest news for the stock"""
        news_items = []
        
        async with aiohttp.ClientSession() as session:
            for source, url in self.news_sources.items():
                try:
                    async with session.get(f"{url}{symbol}") as response:
                        if response.status == 200:
                            html = await response.text()
                            soup = BeautifulSoup(html, 'html.parser')
                            
                            # Extract news (implementation depends on source HTML structure)
                            articles = self._extract_news_articles(soup, source)
                            
                            for article in articles:
                                # Analyze sentiment
                                sentiment = self._analyze_news_sentiment(article["title"])
                                article["sentiment"] = sentiment
                                news_items.append(article)
                except Exception as e:
                    print(f"Error fetching news from {source}: {e}")
        
        return sorted(news_items, key=lambda x: x["date"], reverse=True)[:10]
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def _calculate_macd(self, prices: pd.Series) -> pd.Series:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        exp1 = prices.ewm(span=12, adjust=False).mean()
        exp2 = prices.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        return macd - signal
    
    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20) -> pd.Series:
        """Calculate Bollinger Bands"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper_band = sma + (std * 2)
        lower_band = sma - (std * 2)
        return (prices - lower_band) / (upper_band - lower_band)
    
    async def _calculate_technical_score(self, hist: pd.DataFrame) -> float:
        """Calculate technical analysis score"""
        try:
            close_prices = hist['Close']
            
            # RSI Score (0-100)
            rsi = self._calculate_rsi(close_prices)
            rsi_score = 100 - abs(rsi.iloc[-1] - 50) * 2
            
            # Trend Score
            sma_20 = close_prices.rolling(window=20).mean()
            sma_50 = close_prices.rolling(window=50).mean()
            trend_score = 100 if sma_20.iloc[-1] > sma_50.iloc[-1] else 0
            
            # Volatility Score
            volatility = close_prices.pct_change().std() * np.sqrt(252)
            volatility_score = 100 * (1 - min(volatility, 1))
            
            # Volume Score
            volume_ratio = hist['Volume'].iloc[-1] / hist['Volume'].rolling(window=20).mean().iloc[-1]
            volume_score = min(100, volume_ratio * 50)
            
            return (rsi_score + trend_score + volatility_score + volume_score) / 4
        except Exception as e:
            print(f"Error calculating technical score: {e}")
            return 50
    
    async def _calculate_fundamental_score(self, info: Dict) -> float:
        """Calculate fundamental analysis score"""
        try:
            scores = []
            
            # P/E Score
            pe = info.get('trailingPE', 0)
            if pe > 0:
                pe_score = 100 * (1 - min(pe/50, 1))
                scores.append(pe_score)
            
            # Profit Margin Score
            margin = info.get('profitMargins', 0)
            margin_score = min(100, margin * 100)
            scores.append(margin_score)
            
            # Debt to Equity Score
            de_ratio = info.get('debtToEquity', 0)
            de_score = 100 * (1 - min(de_ratio/200, 1))
            scores.append(de_score)
            
            # Return on Equity Score
            roe = info.get('returnOnEquity', 0)
            roe_score = min(100, roe * 100)
            scores.append(roe_score)
            
            return sum(scores) / len(scores) if scores else 50
        except Exception as e:
            print(f"Error calculating fundamental score: {e}")
            return 50
    
    async def _calculate_risk_score(self, hist: pd.DataFrame) -> float:
        """Calculate risk score (higher score = higher risk)"""
        try:
            # Volatility Risk
            returns = hist['Close'].pct_change()
            volatility = returns.std() * np.sqrt(252)
            volatility_risk = min(100, volatility * 100)
            
            # Drawdown Risk
            rolling_max = hist['Close'].rolling(window=252, min_periods=1).max()
            drawdown = (hist['Close'] - rolling_max) / rolling_max
            max_drawdown = abs(drawdown.min())
            drawdown_risk = min(100, max_drawdown * 200)
            
            # Beta Risk (relative to market)
            market = yf.download('^NSEI', start=hist.index[0], end=hist.index[-1])['Close']
            if len(market) > 0:
                market_returns = market.pct_change()
                beta = returns.cov(market_returns) / market_returns.var()
                beta_risk = min(100, abs(beta) * 50)
            else:
                beta_risk = 50
            
            return (volatility_risk + drawdown_risk + beta_risk) / 3
        except Exception as e:
            print(f"Error calculating risk score: {e}")
            return 50
    
    async def _predict_future_price(self, hist: pd.DataFrame) -> Dict:
        """Predict future price movements"""
        try:
            close_prices = hist['Close']
            returns = close_prices.pct_change()
            volatility = returns.std()
            
            current_price = close_prices.iloc[-1]
            
            # Simple prediction based on trend and volatility
            trend = (close_prices.iloc[-1] / close_prices.iloc[-20] - 1) * 100
            
            predictions = {
                "1d": current_price * (1 + trend/100 + np.random.normal(0, volatility)),
                "1w": current_price * (1 + trend/20 + np.random.normal(0, volatility * np.sqrt(5))),
                "1m": current_price * (1 + trend/4 + np.random.normal(0, volatility * np.sqrt(21)))
            }
            
            return {k: round(v, 2) for k, v in predictions.items()}
        except Exception as e:
            print(f"Error predicting prices: {e}")
            return {"1d": 0, "1w": 0, "1m": 0}
    
    def _get_recommendation(self, ai_score: float) -> str:
        """Get investment recommendation based on AI score"""
        if ai_score >= 80:
            return "Strong Buy"
        elif ai_score >= 60:
            return "Buy"
        elif ai_score >= 40:
            return "Hold"
        elif ai_score >= 20:
            return "Sell"
        else:
            return "Strong Sell"
    
    def _get_confidence_level(self, ai_score: float) -> str:
        """Get confidence level in the prediction"""
        score_diff = abs(ai_score - 50)
        if score_diff >= 40:
            return "Very High"
        elif score_diff >= 30:
            return "High"
        elif score_diff >= 20:
            return "Moderate"
        else:
            return "Low"
    
    def _analyze_news_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of news article"""
        try:
            # Use TextBlob for sentiment analysis
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            # Use transformers for more accurate sentiment
            sentiment = self.sentiment_analyzer(text)[0]
            
            return {
                "score": round((polarity + 1) * 50, 2),  # Convert to 0-100 scale
                "label": sentiment["label"],
                "confidence": round(sentiment["score"] * 100, 2)
            }
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return {"score": 50, "label": "NEUTRAL", "confidence": 0}
    
    async def _generate_comparison(self, stock1: Dict, stock2: Dict) -> Dict:
        """Generate detailed comparison between two stocks"""
        metrics = [
            "market_cap", "pe_ratio", "eps", "dividend_yield",
            "volume", "technical_indicators"
        ]
        
        comparison = {}
        for metric in metrics:
            val1 = stock1["basic_info"].get(metric)
            val2 = stock2["basic_info"].get(metric)
            
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                better = 1 if val1 > val2 else 2 if val2 > val1 else 0
                comparison[metric] = {
                    "stock1": val1,
                    "stock2": val2,
                    "better": better
                }
        
        # Compare AI scores
        comparison["ai_analysis"] = {
            "stock1": stock1["ai_analysis"],
            "stock2": stock2["ai_analysis"],
            "better": 1 if stock1["ai_analysis"]["ai_score"] > stock2["ai_analysis"]["ai_score"] else 2
        }
        
        return comparison
    
    async def _determine_better_stock(self, stock1: Dict, stock2: Dict) -> Dict:
        """Determine which stock is better and why"""
        s1_score = stock1["ai_analysis"]["ai_score"]
        s2_score = stock2["ai_analysis"]["ai_score"]
        
        reasons = []
        
        # Compare fundamental metrics
        if stock1["basic_info"]["pe_ratio"] < stock2["basic_info"]["pe_ratio"]:
            reasons.append("Better P/E ratio")
        if stock1["basic_info"]["eps"] > stock2["basic_info"]["eps"]:
            reasons.append("Higher EPS")
            
        # Compare technical indicators
        if stock1["ai_analysis"]["technical_score"] > stock2["ai_analysis"]["technical_score"]:
            reasons.append("Stronger technical indicators")
            
        # Compare risk scores
        if stock1["ai_analysis"]["risk_score"] < stock2["ai_analysis"]["risk_score"]:
            reasons.append("Lower risk profile")
        
        return {
            "winner": 1 if s1_score > s2_score else 2,
            "score_difference": abs(s1_score - s2_score),
            "reasons": reasons[:3]  # Top 3 reasons
        }
