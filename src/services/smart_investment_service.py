from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import numpy as np
from enum import Enum

from .ai_scoring_service import AIScoringService
from .technical_analysis_service import TechnicalAnalysisService

class InvestmentMode(Enum):
    INTRADAY = "intraday"
    SWING = "swing"
    LONG_TERM = "long_term"

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

@dataclass
class SmartHoldAnalysis:
    symbol: str
    current_loss: float
    recovery_probability: float
    long_term_potential: float
    market_conditions: float
    hold_recommendation: bool
    reasons: List[str]
    expected_recovery_time: Optional[str]
    confidence_score: float

@dataclass
class InvestmentAllocation:
    intraday_amount: float
    swing_amount: float
    long_term_amount: float
    risk_level: RiskLevel
    profit_reinvestment_percentage: float
    auto_compound: bool

class SmartInvestmentService:
    def __init__(self):
        self.ai_service = AIScoringService()
        self.technical_service = TechnicalAnalysisService()
        self.min_recovery_probability = 0.7  # 70% minimum for hold recommendation
        self.min_confidence_score = 0.65  # 65% minimum confidence

    async def analyze_smart_hold(self, 
                               symbol: str,
                               position_data: Dict,
                               market_data: Dict) -> SmartHoldAnalysis:
        """Analyze whether to hold a loss-making position"""
        try:
            # Calculate current loss
            current_loss = (position_data['current_price'] - position_data['entry_price']) / position_data['entry_price']

            # Get AI analysis
            ai_analysis = await self.ai_service.calculate_stock_score(
                symbol=symbol,
                company_data=market_data['company'],
                stock_data=market_data['stock'],
                news_data=market_data['news'],
                market_data=market_data['market']
            )

            # Calculate recovery probability
            recovery_prob = await self._calculate_recovery_probability(
                symbol, position_data, market_data, ai_analysis
            )

            # Analyze long-term potential
            long_term_potential = await self._analyze_long_term_potential(
                symbol, market_data, ai_analysis
            )

            # Analyze market conditions
            market_conditions = await self._analyze_market_conditions(
                symbol, market_data, ai_analysis
            )

            # Make hold/sell decision
            hold_recommendation, reasons = self._make_hold_decision(
                recovery_prob, long_term_potential, market_conditions, current_loss
            )

            # Calculate confidence score
            confidence = self._calculate_confidence_score(
                recovery_prob, long_term_potential, market_conditions, ai_analysis
            )

            return SmartHoldAnalysis(
                symbol=symbol,
                current_loss=current_loss,
                recovery_probability=recovery_prob,
                long_term_potential=long_term_potential,
                market_conditions=market_conditions,
                hold_recommendation=hold_recommendation,
                reasons=reasons,
                expected_recovery_time=self._estimate_recovery_time(current_loss, recovery_prob),
                confidence_score=confidence
            )

        except Exception as e:
            print(f"Error in smart hold analysis: {e}")
            return None

    async def get_recommended_allocation(self,
                                      user_profile: Dict,
                                      market_conditions: Dict) -> InvestmentAllocation:
        """Get recommended investment allocation based on user profile and market conditions"""
        try:
            # Analyze user risk profile
            risk_level = self._analyze_risk_profile(user_profile)

            # Calculate recommended allocations
            allocations = await self._calculate_recommended_allocations(
                user_profile['total_investment'],
                risk_level,
                market_conditions
            )

            # Get recommended profit reinvestment percentage
            reinvestment_pct = await self._get_recommended_reinvestment_percentage(
                risk_level,
                market_conditions
            )

            return InvestmentAllocation(
                intraday_amount=allocations['intraday'],
                swing_amount=allocations['swing'],
                long_term_amount=allocations['long_term'],
                risk_level=risk_level,
                profit_reinvestment_percentage=reinvestment_pct,
                auto_compound=True
            )

        except Exception as e:
            print(f"Error getting recommended allocation: {e}")
            return None

    async def update_investment_allocation(self,
                                        user_id: str,
                                        new_allocation: InvestmentAllocation) -> bool:
        """Update user's investment allocation preferences"""
        try:
            # Validate allocation
            if not self._validate_allocation(new_allocation):
                return False

            # Store in database
            await self._store_user_allocation(user_id, new_allocation)

            return True

        except Exception as e:
            print(f"Error updating investment allocation: {e}")
            return False

    async def _calculate_recovery_probability(self,
                                           symbol: str,
                                           position_data: Dict,
                                           market_data: Dict,
                                           ai_analysis: Dict) -> float:
        """Calculate probability of position recovery"""
        factors = {
            'technical_recovery': await self._analyze_technical_recovery(symbol, market_data),
            'fundamental_strength': ai_analysis['company_score'] / 100,
            'market_sentiment': ai_analysis['news_score'] / 100,
            'sector_performance': await self._analyze_sector_performance(symbol, market_data),
            'historical_recovery': await self._analyze_historical_recovery(symbol, market_data)
        }

        weights = {
            'technical_recovery': 0.3,
            'fundamental_strength': 0.25,
            'market_sentiment': 0.15,
            'sector_performance': 0.15,
            'historical_recovery': 0.15
        }

        return sum(factors[k] * weights[k] for k in factors)

    async def _analyze_long_term_potential(self,
                                         symbol: str,
                                         market_data: Dict,
                                         ai_analysis: Dict) -> float:
        """Analyze long-term potential of the stock"""
        factors = {
            'company_growth': market_data['company']['revenue_growth'],
            'industry_growth': market_data['sector']['growth_rate'],
            'competitive_position': market_data['company']['market_share'],
            'innovation_score': market_data['company']['rd_investment'],
            'ai_prediction': ai_analysis['predictions']['long_term']
        }

        weights = {
            'company_growth': 0.25,
            'industry_growth': 0.20,
            'competitive_position': 0.20,
            'innovation_score': 0.15,
            'ai_prediction': 0.20
        }

        return sum(self._normalize_factor(factors[k]) * weights[k] for k in factors)

    async def _analyze_market_conditions(self,
                                       symbol: str,
                                       market_data: Dict,
                                       ai_analysis: Dict) -> float:
        """Analyze current market conditions"""
        factors = {
            'market_trend': market_data['market']['trend_score'],
            'sector_health': market_data['sector']['health_score'],
            'volatility': market_data['market']['volatility_score'],
            'liquidity': market_data['stock']['liquidity_score'],
            'sentiment': ai_analysis['news_score']
        }

        weights = {
            'market_trend': 0.25,
            'sector_health': 0.20,
            'volatility': 0.20,
            'liquidity': 0.15,
            'sentiment': 0.20
        }

        return sum(self._normalize_factor(factors[k]) * weights[k] for k in factors)

    def _make_hold_decision(self,
                           recovery_prob: float,
                           long_term_potential: float,
                           market_conditions: float,
                           current_loss: float) -> Tuple[bool, List[str]]:
        """Make decision whether to hold or sell"""
        reasons = []
        hold_score = 0

        # Check recovery probability
        if recovery_prob >= self.min_recovery_probability:
            reasons.append(f"High recovery probability: {recovery_prob:.1%}")
            hold_score += 1

        # Check long-term potential
        if long_term_potential >= 0.7:
            reasons.append(f"Strong long-term potential: {long_term_potential:.1%}")
            hold_score += 1

        # Check market conditions
        if market_conditions >= 0.6:
            reasons.append(f"Favorable market conditions: {market_conditions:.1%}")
            hold_score += 1

        # Consider loss magnitude
        if abs(current_loss) < 0.15:  # Less than 15% loss
            reasons.append(f"Manageable loss level: {current_loss:.1%}")
            hold_score += 1

        return hold_score >= 3, reasons

    def _calculate_confidence_score(self,
                                  recovery_prob: float,
                                  long_term_potential: float,
                                  market_conditions: float,
                                  ai_analysis: Dict) -> float:
        """Calculate confidence score in the recommendation"""
        factors = {
            'recovery_probability': recovery_prob,
            'long_term_potential': long_term_potential,
            'market_conditions': market_conditions,
            'ai_confidence': ai_analysis['confidence'] / 100,
            'data_quality': ai_analysis['metrics']['data_quality'] / 100
        }

        weights = {
            'recovery_probability': 0.3,
            'long_term_potential': 0.2,
            'market_conditions': 0.2,
            'ai_confidence': 0.15,
            'data_quality': 0.15
        }

        return sum(factors[k] * weights[k] for k in factors)

    def _estimate_recovery_time(self,
                              current_loss: float,
                              recovery_prob: float) -> Optional[str]:
        """Estimate time needed for position recovery"""
        if recovery_prob < 0.5:
            return "Uncertain"

        loss_magnitude = abs(current_loss)
        if loss_magnitude < 0.05:
            return "1-2 weeks"
        elif loss_magnitude < 0.10:
            return "2-4 weeks"
        elif loss_magnitude < 0.20:
            return "1-3 months"
        elif loss_magnitude < 0.30:
            return "3-6 months"
        else:
            return "6+ months"

    def _analyze_risk_profile(self, user_profile: Dict) -> RiskLevel:
        """Analyze user's risk profile"""
        risk_score = 0
        
        # Age factor
        age = user_profile.get('age', 35)
        risk_score += (60 - age) / 40  # Higher score for younger users

        # Investment experience
        experience = user_profile.get('trading_experience_years', 0)
        risk_score += min(experience / 10, 1)  # Max 1 point for 10+ years

        # Income stability
        if user_profile.get('income_type') == 'stable':
            risk_score += 1

        # Investment knowledge
        knowledge_level = user_profile.get('investment_knowledge', 'medium')
        knowledge_scores = {'low': 0, 'medium': 0.5, 'high': 1}
        risk_score += knowledge_scores[knowledge_level]

        # Risk tolerance
        risk_tolerance = user_profile.get('risk_tolerance', 'medium')
        tolerance_scores = {'low': 0, 'medium': 0.5, 'high': 1}
        risk_score += tolerance_scores[risk_tolerance]

        # Determine risk level
        avg_score = risk_score / 5
        if avg_score < 0.4:
            return RiskLevel.LOW
        elif avg_score < 0.7:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.HIGH

    async def _calculate_recommended_allocations(self,
                                              total_investment: float,
                                              risk_level: RiskLevel,
                                              market_conditions: Dict) -> Dict[str, float]:
        """Calculate recommended investment allocations"""
        # Base allocations by risk level
        base_allocations = {
            RiskLevel.LOW: {'intraday': 0.1, 'swing': 0.3, 'long_term': 0.6},
            RiskLevel.MEDIUM: {'intraday': 0.2, 'swing': 0.4, 'long_term': 0.4},
            RiskLevel.HIGH: {'intraday': 0.3, 'swing': 0.4, 'long_term': 0.3}
        }

        # Adjust based on market conditions
        market_score = await self._analyze_market_conditions_for_allocation(market_conditions)
        
        allocations = base_allocations[risk_level].copy()
        
        # Adjust allocations based on market conditions
        if market_score > 0.7:  # Very good market conditions
            allocations['intraday'] += 0.1
            allocations['swing'] += 0.05
            allocations['long_term'] -= 0.15
        elif market_score < 0.3:  # Poor market conditions
            allocations['intraday'] -= 0.1
            allocations['swing'] -= 0.05
            allocations['long_term'] += 0.15

        # Normalize allocations
        total = sum(allocations.values())
        allocations = {k: v/total for k, v in allocations.items()}

        # Convert to absolute amounts
        return {k: v * total_investment for k, v in allocations.items()}

    async def _get_recommended_reinvestment_percentage(self,
                                                     risk_level: RiskLevel,
                                                     market_conditions: Dict) -> float:
        """Get recommended profit reinvestment percentage"""
        # Base reinvestment by risk level
        base_reinvestment = {
            RiskLevel.LOW: 0.3,
            RiskLevel.MEDIUM: 0.5,
            RiskLevel.HIGH: 0.7
        }

        # Adjust based on market conditions
        market_score = await self._analyze_market_conditions_for_allocation(market_conditions)
        
        reinvestment = base_reinvestment[risk_level]
        
        # Adjust based on market conditions
        if market_score > 0.7:
            reinvestment += 0.1
        elif market_score < 0.3:
            reinvestment -= 0.1

        return max(0.1, min(0.9, reinvestment))  # Keep between 10% and 90%

    def _normalize_factor(self, value: float) -> float:
        """Normalize a factor to 0-1 range"""
        return max(0, min(1, value))
