from typing import Dict, List, Optional
import asyncio
from datetime import datetime, timedelta
import aiohttp
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import yfinance as yf
from ..utils.api_client import APIClient

class IndianMarketAnalyzer:
    def __init__(self):
        self.api_client = APIClient()
        
        # Initialize news sources
        self.news_sources = {
            "nse": "https://www.nseindia.com/api/news",
            "bse": "https://api.bseindia.com/news",
            "moneycontrol": "https://www.moneycontrol.com/news/business/markets",
            "economic_times": "https://economictimes.indiatimes.com/markets",
            "zee_business": "https://www.zeebiz.com/markets",
            "cnbc_awaaz": "https://www.cnbctv18.com/hindi/market"
        }
        
        # Initialize regulatory sources
        self.regulatory_sources = {
            "rbi": "https://www.rbi.org.in/Scripts/NotificationUser.aspx",
            "sebi": "https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes"
        }
        
        # Initialize sector mapping
        self.sector_mapping = {
            "IT": ["TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS"],
            "Banking": ["HDFCBANK.NS", "SBIN.NS", "ICICIBANK.NS", "AXISBANK.NS"],
            "Pharma": ["SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS"],
            "Auto": ["TATAMOTORS.NS", "M&M.NS", "MARUTI.NS"],
            "PSU": ["COALINDIA.NS", "ONGC.NS", "NTPC.NS"]
        }
        
        # Initialize cache
        self.cache = {}
        self.cache_duration = timedelta(minutes=5)

    async def get_market_overview(self) -> Dict:
        """Get comprehensive Indian market overview"""
        try:
            # Get various market components
            news = await self.get_latest_news()
            sentiment = await self.calculate_market_sentiment()
            fii_dii = await self.track_institutional_flow()
            sector_strength = await self.calculate_sector_strength()
            ipo_status = await self.get_ipo_status()
            
            return {
                "market_sentiment": sentiment,
                "latest_news": news[:5],
                "institutional_flow": fii_dii,
                "sector_strength": sector_strength,
                "ipo_updates": ipo_status,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error getting market overview: {str(e)}")
            return {"error": str(e)}

    async def get_latest_news(self) -> List[Dict]:
        """Get latest news from all Indian sources"""
        try:
            all_news = []
            
            # Fetch from NSE
            nse_news = await self._fetch_nse_news()
            all_news.extend(nse_news)
            
            # Fetch from BSE
            bse_news = await self._fetch_bse_news()
            all_news.extend(bse_news)
            
            # Fetch from MoneyControl
            mc_news = await self._fetch_moneycontrol_news()
            all_news.extend(mc_news)
            
            # Fetch from Economic Times
            et_news = await self._fetch_et_news()
            all_news.extend(et_news)
            
            # Sort by timestamp
            all_news.sort(key=lambda x: x["timestamp"], reverse=True)
            
            # Add sentiment scores
            for news in all_news:
                news["sentiment_score"] = await self._calculate_news_sentiment(news["title"], news["content"])
            
            return all_news
            
        except Exception as e:
            print(f"Error fetching news: {str(e)}")
            return []

    async def track_institutional_flow(self) -> Dict:
        """Track FII and DII investments"""
        try:
            # Fetch FII data
            fii_data = await self._fetch_fii_data()
            
            # Fetch DII data
            dii_data = await self._fetch_dii_data()
            
            # Calculate net flows
            net_fii = sum(fii_data["buy_value"]) - sum(fii_data["sell_value"])
            net_dii = sum(dii_data["buy_value"]) - sum(dii_data["sell_value"])
            
            return {
                "fii": {
                    "net_flow": net_fii,
                    "trend": "bullish" if net_fii > 0 else "bearish",
                    "details": fii_data
                },
                "dii": {
                    "net_flow": net_dii,
                    "trend": "bullish" if net_dii > 0 else "bearish",
                    "details": dii_data
                }
            }
            
        except Exception as e:
            print(f"Error tracking institutional flow: {str(e)}")
            return {}

    async def calculate_sector_strength(self) -> Dict:
        """Calculate sector-wise strength index"""
        try:
            sector_strength = {}
            
            for sector, symbols in self.sector_mapping.items():
                # Get stock data
                stocks_data = []
                for symbol in symbols:
                    stock = yf.Ticker(symbol)
                    hist = stock.history(period="5d")
                    stocks_data.append({
                        "symbol": symbol,
                        "returns": hist["Close"].pct_change().mean(),
                        "volume": hist["Volume"].mean(),
                        "volatility": hist["Close"].pct_change().std()
                    })
                
                # Calculate sector strength
                sector_strength[sector] = {
                    "strength_index": self._calculate_strength_index(stocks_data),
                    "top_performers": sorted(stocks_data, key=lambda x: x["returns"], reverse=True)[:2],
                    "trend": self._determine_sector_trend(stocks_data)
                }
            
            return sector_strength
            
        except Exception as e:
            print(f"Error calculating sector strength: {str(e)}")
            return {}

    async def get_ipo_status(self) -> List[Dict]:
        """Get IPO subscription and analysis"""
        try:
            ipos = await self._fetch_ipo_data()
            
            for ipo in ipos:
                # Calculate subscription ratios
                ipo["subscription_status"] = {
                    "qib": ipo["qib_subscription"],
                    "hni": ipo["hni_subscription"],
                    "retail": ipo["retail_subscription"],
                    "total": ipo["total_subscription"]
                }
                
                # Add AI analysis
                ipo["analysis"] = self._analyze_ipo(ipo)
                
                # Add sentiment from grey market
                ipo["grey_market_premium"] = await self._fetch_grey_market_premium(ipo["symbol"])
            
            return ipos
            
        except Exception as e:
            print(f"Error getting IPO status: {str(e)}")
            return []

    async def analyze_policy_impact(self, policy_text: str) -> Dict:
        """Analyze impact of government policies and RBI announcements"""
        try:
            # Extract key points
            key_points = self._extract_policy_points(policy_text)
            
            # Analyze sector-wise impact
            sector_impact = {}
            for sector in self.sector_mapping.keys():
                impact_score = self._calculate_policy_impact(key_points, sector)
                sector_impact[sector] = {
                    "score": impact_score,
                    "sentiment": "positive" if impact_score > 0.2 else "negative" if impact_score < -0.2 else "neutral",
                    "key_factors": self._get_impact_factors(key_points, sector)
                }
            
            return {
                "overall_impact": sum(s["score"] for s in sector_impact.values()) / len(sector_impact),
                "sector_impact": sector_impact,
                "key_points": key_points,
                "recommendations": self._generate_policy_recommendations(sector_impact)
            }
            
        except Exception as e:
            print(f"Error analyzing policy impact: {str(e)}")
            return {}

    def _calculate_strength_index(self, stocks_data: List[Dict]) -> float:
        """Calculate sector strength index"""
        weights = {
            "returns": 0.4,
            "volume": 0.3,
            "volatility": 0.3
        }
        
        # Normalize data
        normalized_data = []
        for stock in stocks_data:
            normalized_data.append({
                "returns": stock["returns"] / max(abs(s["returns"]) for s in stocks_data),
                "volume": stock["volume"] / max(s["volume"] for s in stocks_data),
                "volatility": 1 - (stock["volatility"] / max(s["volatility"] for s in stocks_data))
            })
        
        # Calculate weighted average
        strength_scores = []
        for data in normalized_data:
            score = sum(data[key] * weights[key] for key in weights)
            strength_scores.append(score)
        
        return np.mean(strength_scores)

    def _determine_sector_trend(self, stocks_data: List[Dict]) -> str:
        """Determine sector trend"""
        avg_return = np.mean([stock["returns"] for stock in stocks_data])
        avg_volume = np.mean([stock["volume"] for stock in stocks_data])
        
        if avg_return > 0.02 and avg_volume > 0:
            return "strongly_bullish"
        elif avg_return > 0:
            return "bullish"
        elif avg_return < -0.02:
            return "strongly_bearish"
        elif avg_return < 0:
            return "bearish"
        return "neutral"

    def _analyze_ipo(self, ipo_data: Dict) -> Dict:
        """Analyze IPO potential"""
        # Calculate subscription strength
        subscription_strength = (
            ipo_data["qib_subscription"] * 0.4 +
            ipo_data["hni_subscription"] * 0.3 +
            ipo_data["retail_subscription"] * 0.3
        )
        
        # Analyze financials
        financial_strength = self._analyze_financials(ipo_data)
        
        # Generate recommendation
        if subscription_strength > 50 and financial_strength > 0.7:
            recommendation = "strong_buy"
        elif subscription_strength > 30 and financial_strength > 0.5:
            recommendation = "buy"
        elif subscription_strength < 10 or financial_strength < 0.3:
            recommendation = "avoid"
        else:
            recommendation = "neutral"
        
        return {
            "subscription_strength": subscription_strength,
            "financial_strength": financial_strength,
            "recommendation": recommendation,
            "key_points": self._get_ipo_key_points(ipo_data)
        }

    def _analyze_financials(self, data: Dict) -> float:
        """Analyze company financials"""
        # Implement financial analysis logic
        return 0.7  # Placeholder

    def _get_ipo_key_points(self, data: Dict) -> List[str]:
        """Get key points about IPO"""
        # Implement key points extraction
        return ["Strong subscription from QIBs", "Healthy financials"]  # Placeholder

    async def _calculate_news_sentiment(self, title: str, content: str) -> Dict:
        """Calculate sentiment score for news"""
        # Implement sentiment analysis
        return {
            "score": 0.5,
            "confidence": 0.8,
            "impact": "medium"
        }

    def _extract_policy_points(self, text: str) -> List[str]:
        """Extract key points from policy text"""
        # Implement policy text analysis
        return ["Interest rate change", "Regulatory update"]  # Placeholder

    def _calculate_policy_impact(self, points: List[str], sector: str) -> float:
        """Calculate policy impact on sector"""
        # Implement impact calculation
        return 0.3  # Placeholder

    def _get_impact_factors(self, points: List[str], sector: str) -> List[str]:
        """Get factors affecting sector impact"""
        # Implement factor analysis
        return ["Factor 1", "Factor 2"]  # Placeholder

    def _generate_policy_recommendations(self, impacts: Dict) -> List[str]:
        """Generate recommendations based on policy impact"""
        # Implement recommendation generation
        return ["Recommendation 1", "Recommendation 2"]  # Placeholder

# Initialize global Indian market analyzer
indian_market_analyzer = IndianMarketAnalyzer()
