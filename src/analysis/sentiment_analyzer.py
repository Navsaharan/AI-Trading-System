from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime, timedelta
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from transformers import pipeline
import tweepy
import praw
from textblob import TextBlob
import numpy as np
import yfinance as yf

class SentimentAnalyzer:
    """AI-powered sentiment analysis for market prediction."""
    
    def __init__(self, twitter_api_key: Optional[str] = None,
                 reddit_client_id: Optional[str] = None):
        # Initialize sentiment analysis model
        self.sentiment_model = pipeline("sentiment-analysis",
                                      model="ProsusAI/finbert")
        
        # Initialize social media APIs
        self.twitter_api = self._init_twitter(twitter_api_key) if twitter_api_key else None
        self.reddit_api = self._init_reddit(reddit_client_id) if reddit_client_id else None
        
        # News sources
        self.news_sources = {
            "google_news": "https://news.google.com/rss/search?q={}",
            "yahoo_finance": "https://finance.yahoo.com/quote/{}/news",
            "economic_times": "https://economictimes.indiatimes.com/markets/stocks/news",
            "moneycontrol": "https://www.moneycontrol.com/news/business/stocks/"
        }
        
        # Indian market specific subreddits and keywords
        self.indian_subreddits = [
            'IndiaInvestments',
            'DalalStreetTalks',
            'IndianStockMarket',
            'IndianTraders',
            'IndianStreetBets'
        ]
        
        # Major Indian financial institutions
        self.institutions = [
            'Morgan Stanley India',
            'Goldman Sachs India',
            'HDFC Securities',
            'ICICI Securities',
            'Motilal Oswal',
            'Zerodha',
            'Upstox'
        ]
        
        # Initialize sentiment cache
        self.sentiment_cache = {}
        self.cache_duration = timedelta(minutes=15)
        
        # Initialize event tracker
        self.upcoming_events = []
        self.load_upcoming_events()

    async def analyze_stock_sentiment(self, symbol: str,
                                    lookback_days: int = 7) -> Dict:
        """Analyze overall sentiment for a stock from multiple sources."""
        try:
            # Gather data from all sources concurrently
            tasks = [
                self._get_news_sentiment(symbol, lookback_days),
                self._get_social_media_sentiment(symbol, lookback_days),
                self._get_trading_view_sentiment(symbol),
                self._get_analyst_ratings(symbol)
            ]
            
            results = await asyncio.gather(*tasks)
            
            # Combine all sentiment scores
            news_sentiment = results[0]
            social_sentiment = results[1]
            trading_view = results[2]
            analyst_ratings = results[3]
            
            # Calculate weighted sentiment score
            weights = {
                "news": 0.4,
                "social": 0.2,
                "trading_view": 0.2,
                "analyst": 0.2
            }
            
            composite_score = (
                news_sentiment["score"] * weights["news"] +
                social_sentiment["score"] * weights["social"] +
                trading_view["score"] * weights["trading_view"] +
                analyst_ratings["score"] * weights["analyst"]
            )
            
            return {
                "symbol": symbol,
                "composite_score": composite_score,
                "sentiment": self._get_sentiment_label(composite_score),
                "confidence": self._calculate_confidence(results),
                "sources": {
                    "news": news_sentiment,
                    "social_media": social_sentiment,
                    "trading_view": trading_view,
                    "analyst_ratings": analyst_ratings
                },
                "timestamp": datetime.now(),
                "lookback_days": lookback_days
            }
        except Exception as e:
            print(f"Error analyzing sentiment: {str(e)}")
            return {}
    
    async def detect_market_manipulation(self, symbol: str,
                                      timeframe: str = "1d") -> Dict:
        """Detect potential market manipulation through sentiment analysis."""
        try:
            # Get historical price data
            price_data = await self._get_price_data(symbol, timeframe)
            
            # Get sentiment data
            sentiment_data = await self.analyze_stock_sentiment(symbol)
            
            # Analyze patterns
            manipulation_signals = []
            
            # Check for unusual social media activity
            if sentiment_data["sources"]["social_media"]["volume"] > 200:  # threshold
                manipulation_signals.append("High social media activity")
            
            # Check for coordinated posting patterns
            if await self._detect_coordinated_posts(symbol):
                manipulation_signals.append("Coordinated posting pattern detected")
            
            # Check for sentiment-price divergence
            if await self._check_sentiment_price_divergence(
                sentiment_data, price_data
            ):
                manipulation_signals.append("Sentiment-price divergence detected")
            
            return {
                "symbol": symbol,
                "manipulation_detected": len(manipulation_signals) > 0,
                "signals": manipulation_signals,
                "confidence": self._calculate_manipulation_confidence(
                    manipulation_signals
                ),
                "timestamp": datetime.now()
            }
        except Exception as e:
            print(f"Error detecting manipulation: {str(e)}")
            return {}
    
    async def get_market_sentiment(self) -> Dict:
        """Get overall market sentiment."""
        try:
            # Analyze major indices
            indices = ["^GSPC", "^DJI", "^IXIC", "^NSEI", "^BSESN"]
            index_sentiments = []
            
            for index in indices:
                sentiment = await self.analyze_stock_sentiment(index, lookback_days=1)
                index_sentiments.append(sentiment)
            
            # Analyze global news
            global_news = await self._get_global_market_news()
            
            # Calculate market sentiment
            market_score = np.mean([s["composite_score"] for s in index_sentiments])
            
            return {
                "market_sentiment": self._get_sentiment_label(market_score),
                "score": market_score,
                "confidence": np.mean([s["confidence"] for s in index_sentiments]),
                "indices": {idx: sent for idx, sent in zip(indices, index_sentiments)},
                "global_news": global_news,
                "timestamp": datetime.now()
            }
        except Exception as e:
            print(f"Error getting market sentiment: {str(e)}")
            return {}
    
    async def _get_news_sentiment(self, symbol: str, lookback_days: int) -> Dict:
        """Get sentiment from news articles."""
        try:
            articles = []
            
            # Gather news from all sources
            for source, url in self.news_sources.items():
                source_articles = await self._scrape_news(
                    url.format(symbol), lookback_days
                )
                articles.extend(source_articles)
            
            if not articles:
                return {"score": 0, "articles": []}
            
            # Analyze sentiment for each article
            sentiments = []
            for article in articles:
                sentiment = self.sentiment_model(article["title"])[0]
                sentiments.append({
                    "score": self._normalize_sentiment_score(
                        sentiment["score"], sentiment["label"]
                    ),
                    "title": article["title"],
                    "source": article["source"],
                    "url": article["url"],
                    "timestamp": article["timestamp"]
                })
            
            # Calculate aggregate sentiment
            avg_sentiment = np.mean([s["score"] for s in sentiments])
            
            return {
                "score": avg_sentiment,
                "articles": sentiments[:10],  # Return top 10 articles
                "total_articles": len(articles)
            }
        except Exception as e:
            print(f"Error getting news sentiment: {str(e)}")
            return {"score": 0, "articles": []}
    
    async def _get_social_media_sentiment(self, symbol: str,
                                        lookback_days: int) -> Dict:
        """Get sentiment from social media."""
        try:
            # Get Twitter sentiment
            tweets = await self._get_twitter_sentiment(symbol, lookback_days)
            
            # Get Reddit sentiment
            reddit_posts = await self._get_reddit_sentiment(symbol, lookback_days)
            
            # Combine sentiments
            all_posts = tweets["posts"] + reddit_posts["posts"]
            
            if not all_posts:
                return {"score": 0, "posts": []}
            
            # Calculate weighted average
            twitter_weight = 0.6
            reddit_weight = 0.4
            
            combined_score = (
                tweets["score"] * twitter_weight +
                reddit_posts["score"] * reddit_weight
            )
            
            return {
                "score": combined_score,
                "posts": sorted(all_posts, key=lambda x: x["timestamp"])[:10],
                "volume": len(all_posts),
                "sources": {
                    "twitter": tweets["volume"],
                    "reddit": reddit_posts["volume"]
                }
            }
        except Exception as e:
            print(f"Error getting social media sentiment: {str(e)}")
            return {"score": 0, "posts": []}
    
    async def _get_trading_view_sentiment(self, symbol: str) -> Dict:
        """Get sentiment from TradingView."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://www.tradingview.com/symbols/{symbol}"
                async with session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, "html.parser")
                        
                        # Extract technical analysis indicators
                        buy_signals = len(soup.find_all(class_="buy-signal"))
                        sell_signals = len(soup.find_all(class_="sell-signal"))
                        
                        total_signals = buy_signals + sell_signals
                        if total_signals == 0:
                            return {"score": 0}
                        
                        score = (buy_signals - sell_signals) / total_signals
                        
                        return {
                            "score": score,
                            "buy_signals": buy_signals,
                            "sell_signals": sell_signals,
                            "total_signals": total_signals
                        }
            return {"score": 0}
        except Exception:
            return {"score": 0}
    
    async def _get_analyst_ratings(self, symbol: str) -> Dict:
        """Get analyst ratings and recommendations."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://finance.yahoo.com/quote/{symbol}/analysis"
                async with session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, "html.parser")
                        
                        # Extract analyst recommendations
                        buy_count = 0
                        sell_count = 0
                        hold_count = 0
                        
                        # Parse the recommendation table
                        table = soup.find("table", {"class": "W(100%) M(0) BdB Bdc($seperatorColor)"})
                        if table:
                            rows = table.find_all("tr")
                            for row in rows[1:]:  # Skip header
                                cols = row.find_all("td")
                                if len(cols) >= 2:
                                    rating = cols[1].text.strip().lower()
                                    if "buy" in rating:
                                        buy_count += 1
                                    elif "sell" in rating:
                                        sell_count += 1
                                    elif "hold" in rating:
                                        hold_count += 1
                        
                        total = buy_count + sell_count + hold_count
                        if total == 0:
                            return {"score": 0}
                        
                        # Calculate score (-1 to 1)
                        score = (buy_count - sell_count) / total
                        
                        return {
                            "score": score,
                            "buy": buy_count,
                            "sell": sell_count,
                            "hold": hold_count,
                            "total_ratings": total
                        }
            return {"score": 0}
        except Exception:
            return {"score": 0}
    
    def _init_twitter(self, api_key: str) -> tweepy.API:
        """Initialize Twitter API."""
        auth = tweepy.OAuthHandler(api_key, "")
        return tweepy.API(auth)
    
    def _init_reddit(self, client_id: str) -> praw.Reddit:
        """Initialize Reddit API."""
        return praw.Reddit(
            client_id=client_id,
            client_secret="",
            user_agent="SentimentAnalyzer/1.0"
        )
    
    def _normalize_sentiment_score(self, score: float, label: str) -> float:
        """Normalize sentiment score to range [-1, 1]."""
        if label == "POSITIVE":
            return score
        elif label == "NEGATIVE":
            return -score
        return 0
    
    def _get_sentiment_label(self, score: float) -> str:
        """Convert sentiment score to label."""
        if score > 0.2:
            return "bullish"
        elif score < -0.2:
            return "bearish"
        return "neutral"
    
    def _calculate_confidence(self, results: List[Dict]) -> float:
        """Calculate confidence level of sentiment analysis."""
        # Implementation depends on specific confidence metrics
        return 0.8  # Placeholder
    
    async def _detect_coordinated_posts(self, symbol: str) -> bool:
        """Detect coordinated posting patterns."""
        # Implementation for detecting coordination
        return False  # Placeholder
    
    async def _check_sentiment_price_divergence(self, sentiment: Dict,
                                              price_data: pd.DataFrame) -> bool:
        """Check for divergence between sentiment and price."""
        # Implementation for divergence detection
        return False  # Placeholder
    
    def _calculate_manipulation_confidence(self, signals: List[str]) -> float:
        """Calculate confidence in manipulation detection."""
        return len(signals) / 5  # Simple scaling

    async def get_market_sentiment_india(self, symbol: str) -> Dict:
        """Get comprehensive market sentiment for a symbol"""
        try:
            # Check cache
            if self._check_cache(symbol):
                return self.sentiment_cache[symbol]
            
            # Gather data from all sources
            news_sentiment = await self.analyze_news(symbol)
            reddit_sentiment = await self.analyze_reddit(symbol)
            twitter_sentiment = await self.analyze_twitter(symbol)
            institutional_moves = await self.track_institutional_moves(symbol)
            
            # Calculate combined sentiment
            sentiment = self._calculate_combined_sentiment(
                news_sentiment,
                reddit_sentiment,
                twitter_sentiment,
                institutional_moves
            )
            
            # Cache results
            self._cache_sentiment(symbol, sentiment)
            
            return sentiment
            
        except Exception as e:
            print(f"Error getting sentiment for {symbol}: {str(e)}")
            return {"error": str(e)}

    async def analyze_news(self, symbol: str) -> Dict:
        """Analyze news from multiple sources"""
        try:
            news_data = []
            
            # Google Finance
            google_news = await self._fetch_google_finance_news(symbol)
            news_data.extend(google_news)
            
            # Yahoo Finance
            yahoo_news = await self._fetch_yahoo_finance_news(symbol)
            news_data.extend(yahoo_news)
            
            # NewsAPI
            newsapi_news = await self._fetch_newsapi_news(symbol)
            news_data.extend(newsapi_news)
            
            # Filter Indian market specific news
            news_data = self._filter_indian_market_news(news_data)
            
            # Analyze sentiment
            sentiment_scores = [
                self._analyze_text_sentiment(news["title"] + " " + news["description"])
                for news in news_data
            ]
            
            return {
                "overall_score": np.mean([score["score"] for score in sentiment_scores]),
                "articles": len(news_data),
                "bullish": len([s for s in sentiment_scores if s["score"] > 0.2]),
                "bearish": len([s for s in sentiment_scores if s["score"] < -0.2]),
                "neutral": len([s for s in sentiment_scores if -0.2 <= s["score"] <= 0.2]),
                "latest_news": news_data[:5]  # Return 5 latest news items
            }
            
        except Exception as e:
            print(f"News analysis error for {symbol}: {str(e)}")
            return {}

    async def analyze_reddit(self, symbol: str) -> Dict:
        """Analyze Reddit sentiment"""
        try:
            posts_data = []
            
            # Gather posts from Indian subreddits
            for subreddit_name in self.indian_subreddits:
                subreddit = self.reddit_api.subreddit(subreddit_name)
                posts = subreddit.search(symbol, limit=50, time_filter="day")
                
                for post in posts:
                    # Check for spam/fake signals
                    if not self._is_spam_post(post):
                        posts_data.append({
                            "title": post.title,
                            "body": post.selftext,
                            "score": post.score,
                            "comments": post.num_comments,
                            "created_utc": post.created_utc
                        })
            
            # Analyze sentiment
            sentiment_scores = [
                self._analyze_text_sentiment(post["title"] + " " + post["body"])
                for post in posts_data
            ]
            
            # Weight by post score and comments
            weighted_scores = [
                score["score"] * (1 + np.log1p(post["score"] + post["comments"]))
                for score, post in zip(sentiment_scores, posts_data)
            ]
            
            return {
                "overall_score": np.mean(weighted_scores) if weighted_scores else 0,
                "posts": len(posts_data),
                "total_score": sum(post["score"] for post in posts_data),
                "total_comments": sum(post["comments"] for post in posts_data),
                "trending_score": self._calculate_trending_score(posts_data)
            }
            
        except Exception as e:
            print(f"Reddit analysis error for {symbol}: {str(e)}")
            return {}

    async def analyze_twitter(self, symbol: str) -> Dict:
        """Analyze Twitter sentiment"""
        try:
            tweets_data = []
            
            # Search tweets
            query = f"{symbol} (stock OR market OR trading) lang:en"
            tweets = self.twitter_api.search_recent_tweets(
                query=query,
                max_results=100,
                tweet_fields=["created_at", "public_metrics"]
            )
            
            for tweet in tweets.data:
                # Check for spam/fake signals
                if not self._is_spam_tweet(tweet):
                    tweets_data.append({
                        "text": tweet.text,
                        "likes": tweet.public_metrics["like_count"],
                        "retweets": tweet.public_metrics["retweet_count"],
                        "created_at": tweet.created_at
                    })
            
            # Analyze sentiment
            sentiment_scores = [
                self._analyze_text_sentiment(tweet["text"])
                for tweet in tweets_data
            ]
            
            # Weight by engagement
            weighted_scores = [
                score["score"] * (1 + np.log1p(tweet["likes"] + tweet["retweets"]))
                for score, tweet in zip(sentiment_scores, tweets_data)
            ]
            
            return {
                "overall_score": np.mean(weighted_scores) if weighted_scores else 0,
                "tweets": len(tweets_data),
                "total_likes": sum(tweet["likes"] for tweet in tweets_data),
                "total_retweets": sum(tweet["retweets"] for tweet in tweets_data),
                "trending_score": self._calculate_trending_score(tweets_data)
            }
            
        except Exception as e:
            print(f"Twitter analysis error for {symbol}: {str(e)}")
            return {}

    async def track_institutional_moves(self, symbol: str) -> Dict:
        """Track institutional trading moves"""
        try:
            moves_data = []
            
            # Track institutional holdings
            stock = yf.Ticker(symbol)
            institutional_holders = stock.institutional_holders
            
            # Track recent institutional news
            for institution in self.institutions:
                news = await self._fetch_institution_news(institution, symbol)
                moves_data.extend(news)
            
            return {
                "institutional_holders": len(institutional_holders) if institutional_holders is not None else 0,
                "total_holdings": institutional_holders["Shares"].sum() if institutional_holders is not None else 0,
                "recent_moves": moves_data[:5]  # Return 5 latest moves
            }
            
        except Exception as e:
            print(f"Institutional tracking error for {symbol}: {str(e)}")
            return {}

    def _analyze_text_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of text using TextBlob"""
        try:
            analysis = TextBlob(text)
            return {
                "score": analysis.sentiment.polarity,
                "subjectivity": analysis.sentiment.subjectivity
            }
        except:
            return {"score": 0, "subjectivity": 0}

    def _is_spam_post(self, post) -> bool:
        """Detect spam/fake signals in Reddit posts"""
        # Implement spam detection logic
        spam_keywords = [
            "guaranteed returns",
            "100% profit",
            "cant lose",
            "join my group",
            "paid signals"
        ]
        
        text = (post.title + " " + post.selftext).lower()
        return any(keyword in text for keyword in spam_keywords)

    def _is_spam_tweet(self, tweet) -> bool:
        """Detect spam/fake signals in tweets"""
        # Implement spam detection logic
        spam_keywords = [
            "guaranteed returns",
            "100% profit",
            "cant lose",
            "join my group",
            "paid signals"
        ]
        
        return any(keyword in tweet.text.lower() for keyword in spam_keywords)

    def _calculate_trending_score(self, data: List[Dict]) -> float:
        """Calculate how trending a topic is"""
        if not data:
            return 0
            
        # Calculate score based on recency and engagement
        now = datetime.now().timestamp()
        scores = []
        
        for item in data:
            time_diff = now - item.get("created_utc", now)
            engagement = item.get("score", 0) + item.get("comments", 0)
            
            # Higher score for recent posts with high engagement
            score = engagement * np.exp(-time_diff / (24 * 3600))
            scores.append(score)
            
        return np.mean(scores)

    def _calculate_combined_sentiment(self, 
                                   news: Dict,
                                   reddit: Dict,
                                   twitter: Dict,
                                   institutional: Dict) -> Dict:
        """Calculate combined sentiment from all sources"""
        # Weight different sources
        weights = {
            "news": 0.4,
            "reddit": 0.2,
            "twitter": 0.2,
            "institutional": 0.2
        }
        
        overall_score = (
            news.get("overall_score", 0) * weights["news"] +
            reddit.get("overall_score", 0) * weights["reddit"] +
            twitter.get("overall_score", 0) * weights["twitter"]
        )
        
        # Determine sentiment category
        sentiment = "neutral"
        if overall_score > 0.2:
            sentiment = "bullish"
        elif overall_score < -0.2:
            sentiment = "bearish"
        
        return {
            "overall_score": overall_score,
            "sentiment": sentiment,
            "news": news,
            "reddit": reddit,
            "twitter": twitter,
            "institutional": institutional,
            "trending_score": (
                reddit.get("trending_score", 0) +
                twitter.get("trending_score", 0)
            ) / 2
        }

    def _check_cache(self, symbol: str) -> bool:
        """Check if cached sentiment is still valid"""
        if symbol not in self.sentiment_cache:
            return False
            
        cache_time = self.sentiment_cache[symbol]["timestamp"]
        return datetime.now() - cache_time < self.cache_duration

    def _cache_sentiment(self, symbol: str, sentiment: Dict):
        """Cache sentiment analysis results"""
        self.sentiment_cache[symbol] = {
            "data": sentiment,
            "timestamp": datetime.now()
        }

    def load_upcoming_events(self):
        """Load upcoming market events"""
        # Implement event loading logic
        self.upcoming_events = [
            {
                "date": "2024-02-20",
                "event": "RBI Policy Meeting",
                "type": "monetary_policy"
            },
            {
                "date": "2024-02-25",
                "event": "Quarterly Results - Major Companies",
                "type": "earnings"
            }
        ]

    async def get_alerts(self, symbol: str) -> List[Dict]:
        """Get custom alerts for major events"""
        alerts = []
        
        # Check upcoming events
        for event in self.upcoming_events:
            if datetime.strptime(event["date"], "%Y-%m-%d").date() == datetime.now().date():
                alerts.append({
                    "type": "event",
                    "title": event["event"],
                    "description": f"Major market event today: {event['event']}"
                })
        
        # Check sentiment changes
        if symbol in self.sentiment_cache:
            old_sentiment = self.sentiment_cache[symbol]["data"]["sentiment"]
            current_sentiment = (await self.get_market_sentiment_india(symbol))["sentiment"]
            
            if old_sentiment != current_sentiment:
                alerts.append({
                    "type": "sentiment_change",
                    "title": f"Sentiment Change for {symbol}",
                    "description": f"Market sentiment changed from {old_sentiment} to {current_sentiment}"
                })
        
        return alerts

# Initialize global sentiment analyzer
sentiment_analyzer = SentimentAnalyzer()
