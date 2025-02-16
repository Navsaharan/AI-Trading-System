from typing import Dict, List, Optional, Tuple
import json
import os
from datetime import datetime, timedelta
import numpy as np
from textblob import TextBlob
import aiohttp
from bs4 import BeautifulSoup
import re

class NewsVerificationUtil:
    def __init__(self):
        self.config = self._load_config()
        self.source_cache = {}
        self.verification_cache = {}
        self.manipulation_patterns = self.config['manipulation_detection']['patterns']
        self.thresholds = self.config['manipulation_detection']['thresholds']

    def _load_config(self) -> Dict:
        """Load news sources configuration"""
        config_path = os.path.join(os.path.dirname(__file__), 
                                 '..', 'config', 'news_sources.json')
        with open(config_path, 'r') as f:
            return json.load(f)

    async def verify_news(self, news_item: Dict) -> Tuple[bool, List[str], float]:
        """Verify news authenticity and return verification sources"""
        try:
            # Check cache first
            cache_key = f"{news_item['source']}_{news_item['title']}"
            if cache_key in self.verification_cache:
                return self.verification_cache[cache_key]

            verification_sources = []
            manipulation_prob = 0.0

            # Check source credibility
            source_score = self._get_source_trust_score(news_item['source'])
            if source_score < self.thresholds['minimum_trust_score']:
                return False, [], 1.0

            # Find verification sources
            verification_sources = await self._find_verification_sources(news_item)
            
            # Check for manipulation patterns
            manipulation_prob = await self._check_manipulation_patterns(news_item)
            
            # Determine if news is verified
            is_verified = (
                len(verification_sources) >= self.thresholds['minimum_verification_sources'] and
                manipulation_prob <= self.thresholds['maximum_manipulation_probability']
            )

            # Cache results
            result = (is_verified, verification_sources, manipulation_prob)
            self.verification_cache[cache_key] = result
            
            return result

        except Exception as e:
            print(f"Error verifying news: {e}")
            return False, [], 1.0

    async def _find_verification_sources(self, news_item: Dict) -> List[str]:
        """Find other sources that verify the news"""
        verification_sources = []
        
        # Get keywords from news
        keywords = self._extract_keywords(news_item['title'] + ' ' + news_item['content'])
        
        # Check premium sources
        for source in self.config['premium_sources'].values():
            if await self._check_source_for_verification(source, keywords, news_item):
                verification_sources.append(source['name'])

        # Check Indian sources
        for source in self.config['indian_sources'].values():
            if await self._check_source_for_verification(source, keywords, news_item):
                verification_sources.append(source['name'])

        # Check regulatory sources if relevant
        if self._is_regulatory_relevant(news_item):
            for source in self.config['regulatory_sources'].values():
                if await self._check_source_for_verification(source, keywords, news_item):
                    verification_sources.append(source['name'])

        return verification_sources

    async def _check_manipulation_patterns(self, news_item: Dict) -> float:
        """Check for various manipulation patterns in the news"""
        pattern_scores = []
        
        # Check pump and dump patterns
        if await self._check_pump_and_dump_patterns(news_item):
            pattern_scores.append(self.manipulation_patterns['pump_and_dump']['threshold'])
        
        # Check fake news patterns
        if await self._check_fake_news_patterns(news_item):
            pattern_scores.append(self.manipulation_patterns['fake_news']['threshold'])
        
        # Check artificial hype patterns
        if await self._check_artificial_hype_patterns(news_item):
            pattern_scores.append(self.manipulation_patterns['artificial_hype']['threshold'])
        
        return max(pattern_scores) if pattern_scores else 0.0

    async def _check_pump_and_dump_patterns(self, news_item: Dict) -> bool:
        """Check for pump and dump manipulation patterns"""
        indicators = self.manipulation_patterns['pump_and_dump']['indicators']
        matches = 0
        
        # Check volume spike
        if 'sudden_volume_spike' in indicators:
            if await self._check_volume_spike(news_item):
                matches += 1
        
        # Check coordinated posts
        if 'coordinated_positive_posts' in indicators:
            if await self._check_coordinated_posts(news_item):
                matches += 1
        
        # Check price targets
        if 'unrealistic_price_targets' in indicators:
            if self._check_unrealistic_targets(news_item):
                matches += 1
        
        # Check excessive promotion
        if 'excessive_promotion' in indicators:
            if await self._check_excessive_promotion(news_item):
                matches += 1
        
        threshold = len(indicators) * 0.75  # 75% of indicators need to match
        return matches >= threshold

    async def _check_fake_news_patterns(self, news_item: Dict) -> bool:
        """Check for fake news patterns"""
        indicators = self.manipulation_patterns['fake_news']['indicators']
        matches = 0
        
        # Check unverified claims
        if 'unverified_claims' in indicators:
            if self._check_unverified_claims(news_item):
                matches += 1
        
        # Check anonymous sources
        if 'anonymous_sources' in indicators:
            if self._check_anonymous_sources(news_item):
                matches += 1
        
        # Check exaggerated headlines
        if 'exaggerated_headlines' in indicators:
            if self._check_exaggerated_headlines(news_item):
                matches += 1
        
        # Check missing context
        if 'missing_context' in indicators:
            if self._check_missing_context(news_item):
                matches += 1
        
        threshold = len(indicators) * 0.7  # 70% of indicators need to match
        return matches >= threshold

    async def _check_artificial_hype_patterns(self, news_item: Dict) -> bool:
        """Check for artificial hype patterns"""
        indicators = self.manipulation_patterns['artificial_hype']['indicators']
        matches = 0
        
        # Check bot activity
        if 'bot_activity' in indicators:
            if await self._check_bot_activity(news_item):
                matches += 1
        
        # Check coordinated posting
        if 'coordinated_posting' in indicators:
            if await self._check_coordinated_posting(news_item):
                matches += 1
        
        # Check repetitive messages
        if 'repetitive_messages' in indicators:
            if self._check_repetitive_messages(news_item):
                matches += 1
        
        # Check suspicious accounts
        if 'suspicious_accounts' in indicators:
            if await self._check_suspicious_accounts(news_item):
                matches += 1
        
        threshold = len(indicators) * 0.8  # 80% of indicators need to match
        return matches >= threshold

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        # Remove common words and get important terms
        blob = TextBlob(text.lower())
        return [word for word, pos in blob.tags 
                if pos.startswith(('NN', 'VB', 'JJ')) 
                and len(word) > 3]

    def _get_source_trust_score(self, source_name: str) -> float:
        """Get trust score for a news source"""
        for category in ['premium_sources', 'indian_sources', 'regulatory_sources']:
            if source_name in self.config[category]:
                return self.config[category][source_name]['trust_score']
        return 0.0

    def _is_regulatory_relevant(self, news_item: Dict) -> bool:
        """Check if news might have regulatory relevance"""
        regulatory_keywords = [
            'sebi', 'rbi', 'regulation', 'policy', 'circular', 
            'compliance', 'regulatory', 'guidelines', 'framework'
        ]
        text = (news_item['title'] + ' ' + news_item['content']).lower()
        return any(keyword in text for keyword in regulatory_keywords)

    async def _check_source_for_verification(self,
                                           source: Dict,
                                           keywords: List[str],
                                           original_news: Dict) -> bool:
        """Check if source verifies the news"""
        try:
            # Avoid checking the original source
            if source['name'].lower() == original_news['source'].lower():
                return False

            # Search for similar news
            async with aiohttp.ClientSession() as session:
                search_url = f"{source['base_url']}{source['api_endpoint']}"
                params = {'keywords': ' '.join(keywords)}
                
                async with session.get(search_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._verify_similar_news(data, original_news)
                    
            return False

        except Exception as e:
            print(f"Error checking source {source['name']}: {e}")
            return False

    def _verify_similar_news(self, source_data: Dict, original_news: Dict) -> bool:
        """Verify if source data contains similar news"""
        # Implementation for similarity checking
        pass

    async def _check_volume_spike(self, news_item: Dict) -> bool:
        """Check for unusual volume patterns"""
        # Implementation for volume spike detection
        pass

    async def _check_coordinated_posts(self, news_item: Dict) -> bool:
        """Check for coordinated posting patterns"""
        # Implementation for coordinated posts detection
        pass

    def _check_unrealistic_targets(self, news_item: Dict) -> bool:
        """Check for unrealistic price targets"""
        # Implementation for unrealistic targets detection
        pass

    async def _check_excessive_promotion(self, news_item: Dict) -> bool:
        """Check for excessive promotion patterns"""
        # Implementation for excessive promotion detection
        pass

    def _check_unverified_claims(self, news_item: Dict) -> bool:
        """Check for unverified claims"""
        # Implementation for unverified claims detection
        pass

    def _check_anonymous_sources(self, news_item: Dict) -> bool:
        """Check for anonymous sources"""
        # Implementation for anonymous sources detection
        pass

    def _check_exaggerated_headlines(self, news_item: Dict) -> bool:
        """Check for exaggerated headlines"""
        # Implementation for exaggerated headlines detection
        pass

    def _check_missing_context(self, news_item: Dict) -> bool:
        """Check for missing context"""
        # Implementation for missing context detection
        pass

    async def _check_bot_activity(self, news_item: Dict) -> bool:
        """Check for bot activity"""
        # Implementation for bot activity detection
        pass

    async def _check_coordinated_posting(self, news_item: Dict) -> bool:
        """Check for coordinated posting"""
        # Implementation for coordinated posting detection
        pass

    def _check_repetitive_messages(self, news_item: Dict) -> bool:
        """Check for repetitive messages"""
        # Implementation for repetitive messages detection
        pass

    async def _check_suspicious_accounts(self, news_item: Dict) -> bool:
        """Check for suspicious accounts"""
        # Implementation for suspicious accounts detection
        pass
