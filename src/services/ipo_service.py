import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models.ipo_models import IPO, IPOStatus, IPORiskLevel, GreyMarketPrice, IPONews, InstitutionalInvestment
from ..ai.sentiment_analyzer import SentimentAnalyzer
from ..data.market_data import MarketDataProvider

class IPOService:
    def __init__(self, db: Session, market_data: MarketDataProvider):
        self.db = db
        self.market_data = market_data
        self.sentiment_analyzer = SentimentAnalyzer()
        self.logger = logging.getLogger(__name__)

    async def get_upcoming_ipos(self) -> List[Dict]:
        """Get list of upcoming IPOs with details"""
        ipos = self.db.query(IPO).filter(
            IPO.status == IPOStatus.UPCOMING
        ).order_by(IPO.open_date).all()
        
        return [self._format_ipo_details(ipo) for ipo in ipos]

    async def get_ongoing_ipos(self) -> List[Dict]:
        """Get list of ongoing IPOs with live subscription data"""
        ipos = self.db.query(IPO).filter(
            IPO.status == IPOStatus.ONGOING
        ).order_by(IPO.close_date).all()
        
        for ipo in ipos:
            # Update subscription data
            await self._update_subscription_data(ipo)
        
        return [self._format_ipo_details(ipo) for ipo in ipos]

    async def get_ipo_details(self, ipo_id: int) -> Dict:
        """Get detailed information about an IPO"""
        ipo = self.db.query(IPO).filter(IPO.id == ipo_id).first()
        if not ipo:
            raise ValueError(f"IPO with id {ipo_id} not found")
            
        # Get latest GMP
        latest_gmp = self.db.query(GreyMarketPrice).filter(
            GreyMarketPrice.ipo_id == ipo_id
        ).order_by(GreyMarketPrice.timestamp.desc()).first()
        
        # Get recent news
        recent_news = self.db.query(IPONews).filter(
            IPONews.ipo_id == ipo_id
        ).order_by(IPONews.published_at.desc()).limit(5).all()
        
        # Get institutional investments
        investments = self.db.query(InstitutionalInvestment).filter(
            InstitutionalInvestment.ipo_id == ipo_id
        ).all()
        
        details = self._format_ipo_details(ipo)
        details.update({
            'grey_market_premium': latest_gmp.premium if latest_gmp else None,
            'recent_news': [self._format_news(news) for news in recent_news],
            'institutional_investments': [self._format_investment(inv) for inv in investments]
        })
        
        return details

    async def analyze_ipo(self, ipo_id: int) -> Dict:
        """Perform AI analysis on IPO"""
        ipo = self.db.query(IPO).filter(IPO.id == ipo_id).first()
        if not ipo:
            raise ValueError(f"IPO with id {ipo_id} not found")
        
        # Analyze news sentiment
        news_items = self.db.query(IPONews).filter(
            IPONews.ipo_id == ipo_id,
            IPONews.published_at >= datetime.utcnow() - timedelta(days=30)
        ).all()
        
        sentiment_scores = [news.sentiment_score for news in news_items if news.sentiment_score]
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.5
        
        # Calculate hype level
        hype_factors = [
            avg_sentiment,
            min(1.0, ipo.total_subscription / 10) if ipo.total_subscription else 0,
            min(1.0, len(news_items) / 50)  # Normalize news volume
        ]
        hype_level = sum(hype_factors) / len(hype_factors)
        
        # Determine risk level
        risk_factors = {
            'sentiment': avg_sentiment < 0.4,
            'subscription': ipo.total_subscription and ipo.total_subscription < 1,
            'market_cap': ipo.issue_size and ipo.issue_size < 500,  # Small cap < 500 cr
            'pricing': ipo.issue_price_max / ipo.issue_price_min > 1.2  # Wide price band
        }
        risk_level = IPORiskLevel.HIGH if sum(risk_factors.values()) >= 2 else \
                    IPORiskLevel.MEDIUM if sum(risk_factors.values()) == 1 else \
                    IPORiskLevel.LOW
        
        # Predict listing gain
        expected_gain = await self._predict_listing_gain(ipo)
        
        # Calculate allotment probability
        allotment_prob = await self._calculate_allotment_probability(ipo)
        
        # Update IPO analysis
        ipo.sentiment_score = avg_sentiment
        ipo.hype_level = hype_level
        ipo.risk_level = risk_level
        ipo.expected_listing_gain = expected_gain
        ipo.allotment_probability = allotment_prob
        
        self.db.commit()
        
        return {
            'sentiment_score': avg_sentiment,
            'hype_level': hype_level,
            'risk_level': risk_level.value,
            'expected_listing_gain': expected_gain,
            'allotment_probability': allotment_prob,
            'risk_factors': risk_factors
        }

    async def _update_subscription_data(self, ipo: IPO) -> None:
        """Update live subscription data for ongoing IPO"""
        try:
            data = await self.market_data.get_ipo_subscription(ipo.symbol)
            ipo.subscription_retail = data.get('retail', 0)
            ipo.subscription_hni = data.get('hni', 0)
            ipo.subscription_qib = data.get('qib', 0)
            ipo.total_subscription = data.get('total', 0)
            self.db.commit()
        except Exception as e:
            self.logger.error(f"Error updating subscription data for {ipo.company_name}: {str(e)}")

    async def _predict_listing_gain(self, ipo: IPO) -> float:
        """Predict expected listing gain percentage"""
        # TODO: Implement ML model for prediction
        # For now, using a simple heuristic
        base_expectation = 15.0  # Base 15% listing gain
        
        # Adjust based on subscription
        if ipo.total_subscription:
            base_expectation *= min(2.0, 1 + (ipo.total_subscription / 20))
            
        # Adjust based on sentiment
        if ipo.sentiment_score:
            base_expectation *= (0.5 + ipo.sentiment_score)
            
        # Cap at reasonable limits
        return min(100.0, max(-20.0, base_expectation))

    async def _calculate_allotment_probability(self, ipo: IPO) -> float:
        """Calculate probability of getting allotment"""
        if not ipo.subscription_retail:
            return 0.5
            
        # Basic probability = 1/subscription_ratio
        prob = 1 / ipo.subscription_retail
        
        # Adjust for lot size (higher lots = lower probability)
        if ipo.lot_size > 100:
            prob *= 0.8
            
        return min(1.0, max(0.0, prob))

    def _format_ipo_details(self, ipo: IPO) -> Dict:
        """Format IPO details for API response"""
        return {
            'id': ipo.id,
            'company_name': ipo.company_name,
            'symbol': ipo.symbol,
            'industry': ipo.industry,
            'price_band': f"₹{ipo.issue_price_min} - ₹{ipo.issue_price_max}",
            'lot_size': ipo.lot_size,
            'issue_size': f"₹{ipo.issue_size} Cr",
            'dates': {
                'open': ipo.open_date.strftime('%Y-%m-%d') if ipo.open_date else None,
                'close': ipo.close_date.strftime('%Y-%m-%d') if ipo.close_date else None,
                'listing': ipo.listing_date.strftime('%Y-%m-%d') if ipo.listing_date else None
            },
            'status': ipo.status.value,
            'exchange': ipo.exchange,
            'subscription': {
                'retail': f"{ipo.subscription_retail:.2f}x" if ipo.subscription_retail else "N/A",
                'hni': f"{ipo.subscription_hni:.2f}x" if ipo.subscription_hni else "N/A",
                'qib': f"{ipo.subscription_qib:.2f}x" if ipo.subscription_qib else "N/A",
                'total': f"{ipo.total_subscription:.2f}x" if ipo.total_subscription else "N/A"
            },
            'analysis': {
                'sentiment_score': ipo.sentiment_score,
                'hype_level': ipo.hype_level,
                'risk_level': ipo.risk_level.value if ipo.risk_level else None,
                'expected_listing_gain': f"{ipo.expected_listing_gain:.1f}%" if ipo.expected_listing_gain else None,
                'allotment_probability': f"{ipo.allotment_probability*100:.1f}%" if ipo.allotment_probability else None
            } if any([ipo.sentiment_score, ipo.hype_level, ipo.risk_level, 
                     ipo.expected_listing_gain, ipo.allotment_probability]) else None
        }

    def _format_news(self, news: IPONews) -> Dict:
        """Format news item for API response"""
        return {
            'title': news.title,
            'source': news.source,
            'url': news.url,
            'sentiment': 'Positive' if news.sentiment_score > 0.6 else 
                        'Negative' if news.sentiment_score < 0.4 else 'Neutral',
            'published_at': news.published_at.strftime('%Y-%m-%d %H:%M')
        }

    def _format_investment(self, inv: InstitutionalInvestment) -> Dict:
        """Format institutional investment for API response"""
        return {
            'institution': inv.institution_name,
            'category': inv.category,
            'amount': f"₹{inv.investment_amount} Cr",
            'date': inv.timestamp.strftime('%Y-%m-%d')
        }
