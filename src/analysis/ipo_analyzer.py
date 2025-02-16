from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import aiohttp
from bs4 import BeautifulSoup
from .sentiment_analyzer import SentimentAnalyzer

class IPOAnalyzer:
    """AI-powered IPO analysis and prediction system."""
    
    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()
        self.data_sources = {
            "nse": "https://www.nseindia.com/companies-listing/public-issues-ipo",
            "bse": "https://www.bseindia.com/markets/PublicIssues/IPOs.aspx",
            "moneycontrol": "https://www.moneycontrol.com/ipo/",
            "economic_times": "https://economictimes.indiatimes.com/markets/ipos"
        }
    
    async def analyze_upcoming_ipo(self, company: str) -> Dict:
        """Analyze upcoming IPO and predict performance."""
        try:
            # Gather IPO details
            ipo_details = await self._get_ipo_details(company)
            if not ipo_details:
                return {}
            
            # Analyze company fundamentals
            fundamentals = await self._analyze_fundamentals(company)
            
            # Get industry analysis
            industry_analysis = await self._analyze_industry(ipo_details["industry"])
            
            # Get market sentiment
            market_sentiment = await self.sentiment_analyzer.get_market_sentiment()
            
            # Get company sentiment
            company_sentiment = await self.sentiment_analyzer.analyze_stock_sentiment(
                company
            )
            
            # Calculate subscription probability
            subscription_prob = self._calculate_subscription_probability(
                ipo_details, fundamentals, industry_analysis
            )
            
            # Predict listing price
            listing_prediction = self._predict_listing_price(
                ipo_details, fundamentals, market_sentiment
            )
            
            # Calculate overall score
            overall_score = self._calculate_ipo_score(
                ipo_details,
                fundamentals,
                industry_analysis,
                market_sentiment,
                company_sentiment
            )
            
            return {
                "company": company,
                "ipo_details": ipo_details,
                "analysis": {
                    "fundamentals": fundamentals,
                    "industry": industry_analysis,
                    "market_sentiment": market_sentiment["market_sentiment"],
                    "company_sentiment": company_sentiment["sentiment"]
                },
                "predictions": {
                    "subscription_probability": subscription_prob,
                    "listing_price": listing_prediction,
                    "expected_return": self._calculate_expected_return(
                        ipo_details["price_band"], listing_prediction
                    )
                },
                "scores": {
                    "fundamental_score": fundamentals["score"],
                    "industry_score": industry_analysis["score"],
                    "sentiment_score": company_sentiment["composite_score"],
                    "overall_score": overall_score
                },
                "recommendation": self._get_recommendation(overall_score),
                "risk_level": self._assess_risk_level(
                    fundamentals, industry_analysis, market_sentiment
                ),
                "timestamp": datetime.now()
            }
        except Exception as e:
            print(f"Error analyzing IPO: {str(e)}")
            return {}
    
    async def get_ipo_calendar(self) -> List[Dict]:
        """Get calendar of upcoming IPOs."""
        try:
            upcoming_ipos = []
            
            # Gather IPOs from all sources
            for source, url in self.data_sources.items():
                ipos = await self._scrape_ipo_calendar(url)
                upcoming_ipos.extend(ipos)
            
            # Remove duplicates and sort by date
            unique_ipos = self._deduplicate_ipos(upcoming_ipos)
            sorted_ipos = sorted(unique_ipos,
                               key=lambda x: x["open_date"])
            
            # Add quick analysis for each IPO
            for ipo in sorted_ipos:
                ipo["quick_analysis"] = await self._get_quick_analysis(ipo)
            
            return sorted_ipos
        except Exception as e:
            print(f"Error getting IPO calendar: {str(e)}")
            return []
    
    async def calculate_allotment_chance(self, ipo: Dict,
                                       investment_amount: float) -> Dict:
        """Calculate probability of getting IPO allotment."""
        try:
            # Get subscription data
            subscription_data = await self._get_subscription_data(ipo)
            
            # Calculate number of lots
            lot_size = ipo["lot_size"]
            num_lots = investment_amount // (lot_size * ipo["price_band"][1])
            
            # Calculate probabilities for different categories
            retail_prob = self._calculate_category_probability(
                subscription_data["retail"],
                num_lots
            )
            
            hni_prob = self._calculate_category_probability(
                subscription_data["hni"],
                num_lots
            ) if investment_amount >= 200000 else 0
            
            return {
                "company": ipo["company"],
                "investment_amount": investment_amount,
                "num_lots": num_lots,
                "probabilities": {
                    "retail": retail_prob,
                    "hni": hni_prob
                },
                "best_category": "HNI" if hni_prob > retail_prob else "Retail",
                "subscription_data": subscription_data,
                "timestamp": datetime.now()
            }
        except Exception as e:
            print(f"Error calculating allotment chance: {str(e)}")
            return {}
    
    async def _get_ipo_details(self, company: str) -> Dict:
        """Get detailed IPO information."""
        try:
            # Implement web scraping for IPO details
            return {
                "company": company,
                "price_band": [300, 320],  # Example values
                "lot_size": 100,
                "issue_size": 1000000000,
                "fresh_issue": 800000000,
                "offer_for_sale": 200000000,
                "industry": "Technology",
                "open_date": datetime.now() + timedelta(days=7),
                "close_date": datetime.now() + timedelta(days=10)
            }
        except Exception:
            return {}
    
    async def _analyze_fundamentals(self, company: str) -> Dict:
        """Analyze company fundamentals."""
        try:
            # Implement fundamental analysis
            return {
                "revenue_growth": 25.5,
                "profit_growth": 18.2,
                "debt_equity": 0.8,
                "roce": 15.5,
                "promoter_holding": 65.0,
                "score": 0.75
            }
        except Exception:
            return {"score": 0}
    
    async def _analyze_industry(self, industry: str) -> Dict:
        """Analyze industry performance and trends."""
        try:
            # Implement industry analysis
            return {
                "growth_rate": 12.5,
                "market_size": 50000000000,
                "competition_level": "medium",
                "barriers_to_entry": "high",
                "score": 0.8
            }
        except Exception:
            return {"score": 0}
    
    def _calculate_subscription_probability(self, ipo: Dict, fundamentals: Dict,
                                         industry: Dict) -> float:
        """Calculate probability of IPO subscription."""
        try:
            # Implement subscription probability calculation
            weights = {
                "fundamentals": 0.4,
                "industry": 0.3,
                "issue_size": 0.3
            }
            
            # Normalize issue size score
            size_score = min(ipo["issue_size"] / 10000000000, 1)
            
            weighted_score = (
                fundamentals["score"] * weights["fundamentals"] +
                industry["score"] * weights["industry"] +
                size_score * weights["issue_size"]
            )
            
            return min(weighted_score * 1.2, 1)  # Add 20% optimism factor
        except Exception:
            return 0
    
    def _predict_listing_price(self, ipo: Dict, fundamentals: Dict,
                             market_sentiment: Dict) -> Dict:
        """Predict IPO listing price range."""
        try:
            base_price = ipo["price_band"][1]
            
            # Calculate multiplier based on various factors
            sentiment_mult = 1.2 if market_sentiment["market_sentiment"] == "bullish" else \
                           0.8 if market_sentiment["market_sentiment"] == "bearish" else 1
            
            fundamental_mult = 1 + (fundamentals["score"] - 0.5)
            
            # Calculate expected range
            expected_return = base_price * sentiment_mult * fundamental_mult
            
            return {
                "lower": round(expected_return * 0.9, 2),
                "expected": round(expected_return, 2),
                "upper": round(expected_return * 1.1, 2)
            }
        except Exception:
            return {"lower": 0, "expected": 0, "upper": 0}
    
    def _calculate_ipo_score(self, ipo: Dict, fundamentals: Dict,
                           industry: Dict, market_sentiment: Dict,
                           company_sentiment: Dict) -> float:
        """Calculate overall IPO score."""
        try:
            weights = {
                "fundamentals": 0.35,
                "industry": 0.25,
                "market_sentiment": 0.20,
                "company_sentiment": 0.20
            }
            
            # Convert market sentiment to score
            market_score = 1 if market_sentiment["market_sentiment"] == "bullish" else \
                         0 if market_sentiment["market_sentiment"] == "bearish" else 0.5
            
            weighted_score = (
                fundamentals["score"] * weights["fundamentals"] +
                industry["score"] * weights["industry"] +
                market_score * weights["market_sentiment"] +
                company_sentiment["composite_score"] * weights["company_sentiment"]
            )
            
            return min(max(weighted_score, 0), 1)
        except Exception:
            return 0
    
    def _get_recommendation(self, score: float) -> str:
        """Get IPO recommendation based on score."""
        if score >= 0.8:
            return "Strong Subscribe"
        elif score >= 0.6:
            return "Subscribe"
        elif score >= 0.4:
            return "Neutral"
        elif score >= 0.2:
            return "Avoid"
        return "Strong Avoid"
    
    def _assess_risk_level(self, fundamentals: Dict, industry: Dict,
                          market_sentiment: Dict) -> str:
        """Assess IPO risk level."""
        try:
            risk_factors = []
            
            # Check fundamental risks
            if fundamentals["debt_equity"] > 1:
                risk_factors.append("High Debt")
            if fundamentals["profit_growth"] < 10:
                risk_factors.append("Low Profit Growth")
            
            # Check industry risks
            if industry["competition_level"] == "high":
                risk_factors.append("High Competition")
            
            # Check market risks
            if market_sentiment["market_sentiment"] == "bearish":
                risk_factors.append("Bearish Market")
            
            # Determine risk level
            if len(risk_factors) >= 3:
                return "High"
            elif len(risk_factors) >= 1:
                return "Medium"
            return "Low"
        except Exception:
            return "Medium"
    
    def _calculate_expected_return(self, price_band: List[float],
                                 listing_prediction: Dict) -> Dict:
        """Calculate expected returns including charges."""
        try:
            issue_price = price_band[1]
            expected_price = listing_prediction["expected"]
            
            # Calculate returns
            gross_return = (expected_price - issue_price) / issue_price * 100
            
            # Calculate charges
            brokerage = min(expected_price * 0.0003, 20)  # 0.03% or max ₹20
            stt = expected_price * 0.001  # 0.1% STT
            exchange_charges = expected_price * 0.0001  # 0.01%
            gst = (brokerage + exchange_charges) * 0.18  # 18% GST
            
            total_charges = brokerage + stt + exchange_charges + gst
            
            # Calculate net return
            net_return = gross_return - (total_charges / issue_price * 100)
            
            return {
                "gross_return_percent": round(gross_return, 2),
                "net_return_percent": round(net_return, 2),
                "charges": {
                    "brokerage": round(brokerage, 2),
                    "stt": round(stt, 2),
                    "exchange_charges": round(exchange_charges, 2),
                    "gst": round(gst, 2),
                    "total_charges": round(total_charges, 2)
                }
            }
        except Exception:
            return {"gross_return_percent": 0, "net_return_percent": 0, "charges": {}}
    
    async def _get_subscription_data(self, ipo: Dict) -> Dict:
        """Get real-time IPO subscription data."""
        try:
            # Implement subscription data scraping
            return {
                "retail": 2.5,  # 2.5x subscribed
                "hni": 3.8,
                "qib": 4.2,
                "total": 3.5,
                "timestamp": datetime.now()
            }
        except Exception:
            return {}
    
    def _calculate_category_probability(self, subscription: float,
                                     num_lots: int) -> float:
        """Calculate probability of allotment for a category."""
        try:
            if subscription <= 1:
                return 1
            
            # Basic probability calculation
            base_prob = 1 / subscription
            
            # Adjust for number of lots
            lot_factor = 1 / (1 + np.log(num_lots))
            
            return min(base_prob * lot_factor, 1)
        except Exception:
            return 0
    
    async def _scrape_ipo_calendar(self, url: str) -> List[Dict]:
        """Scrape IPO calendar from a source."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        # Implement source-specific scraping
                        return []
            return []
        except Exception:
            return []
    
    def _deduplicate_ipos(self, ipos: List[Dict]) -> List[Dict]:
        """Remove duplicate IPO entries."""
        seen = set()
        unique_ipos = []
        
        for ipo in ipos:
            if ipo["company"] not in seen:
                seen.add(ipo["company"])
                unique_ipos.append(ipo)
        
        return unique_ipos
    
    async def _get_quick_analysis(self, ipo: Dict) -> Dict:
        """Get quick analysis for IPO calendar listing."""
        try:
            return {
                "hype_score": await self._calculate_hype_score(ipo["company"]),
                "risk_level": self._assess_risk_level({}, {}, {}),
                "recommendation": "Analyze Further"
            }
        except Exception:
            return {}
