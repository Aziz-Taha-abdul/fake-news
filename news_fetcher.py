import requests
import json
from datetime import datetime, timedelta
import logging
import time

logger = logging.getLogger(__name__)

class NewsFetcher:
    def __init__(self):
        # You can get free API keys from these services
        self.news_apis = {
            'newsapi': {
                'url': 'https://newsapi.org/v2/top-headlines',
                'key': 'YOUR_NEWSAPI_KEY',  # Get from https://newsapi.org/
                'enabled': False  # Set to True when you have API key
            }
        }
        
        # RSS feeds as fallback (no API key required)
        self.rss_feeds = [
            'https://rss.cnn.com/rss/edition.rss',
            'https://feeds.bbci.co.uk/news/rss.xml',
            'https://rss.reuters.com/reuters/topNews',
            'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml'
        ]
        
        # Sample news data for demo purposes
        self.sample_news = [
            {
                'title': 'Local Government Announces New Infrastructure Development Plan',
                'url': 'https://example.com/news1',
                'source': 'City News',
                'published_at': datetime.now().isoformat()
            },
            {
                'title': 'SHOCKING: Miracle Weight Loss Secret Doctors Don\'t Want You to Know!',
                'url': 'https://example.com/news2',
                'source': 'Health Blog',
                'published_at': (datetime.now() - timedelta(hours=1)).isoformat()
            },
            {
                'title': 'Study Shows Benefits of Regular Exercise on Mental Health',
                'url': 'https://example.com/news3',
                'source': 'Medical Journal',
                'published_at': (datetime.now() - timedelta(hours=2)).isoformat()
            },
            {
                'title': 'BREAKING: Celebrity Spotted with Secret Twin Nobody Knew About!',
                'url': 'https://example.com/news4',
                'source': 'Entertainment Weekly',
                'published_at': (datetime.now() - timedelta(hours=3)).isoformat()
            },
            {
                'title': 'Economic Report Shows Steady Growth in Technology Sector',
                'url': 'https://example.com/news5',
                'source': 'Financial Times',
                'published_at': (datetime.now() - timedelta(hours=4)).isoformat()
            },
            {
                'title': 'You Won\'t Believe This One Weird Trick to Make Money Fast!',
                'url': 'https://example.com/news6',
                'source': 'Money Tips',
                'published_at': (datetime.now() - timedelta(hours=5)).isoformat()
            },
            {
                'title': 'Research Team Publishes Findings on Climate Change Impact',
                'url': 'https://example.com/news7',
                'source': 'Science Daily',
                'published_at': (datetime.now() - timedelta(hours=6)).isoformat()
            },
            {
                'title': 'EXCLUSIVE: Government Cover-up Exposed by Whistleblower!',
                'url': 'https://example.com/news8',
                'source': 'Truth Seekers',
                'published_at': (datetime.now() - timedelta(hours=7)).isoformat()
            },
            {
                'title': 'University Announces New Scholarship Program for Students',
                'url': 'https://example.com/news9',
                'source': 'Education News',
                'published_at': (datetime.now() - timedelta(hours=8)).isoformat()
            },
            {
                'title': 'AMAZING Discovery: Ancient Aliens Built the Pyramids!',
                'url': 'https://example.com/news10',
                'source': 'Mystery Blog',
                'published_at': (datetime.now() - timedelta(hours=9)).isoformat()
            }
        ]

    def fetch_from_newsapi(self):
        """Fetch news from NewsAPI"""
        try:
            if not self.news_apis['newsapi']['enabled']:
                return []
                
            api_key = self.news_apis['newsapi']['key']
            if api_key == 'YOUR_NEWSAPI_KEY':
                return []
            
            url = self.news_apis['newsapi']['url']
            params = {
                'apiKey': api_key,
                'country': 'us',
                'pageSize': 20,
                'sortBy': 'publishedAt'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            articles = []
            
            for article in data.get('articles', []):
                if article.get('title') and article.get('title') != '[Removed]':
                    articles.append({
                        'title': article['title'],
                        'url': article.get('url', ''),
                        'source': article.get('source', {}).get('name', 'Unknown'),
                        'published_at': article.get('publishedAt', '')
                    })
            
            logger.info(f"Fetched {len(articles)} articles from NewsAPI")
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching from NewsAPI: {str(e)}")
            return []

    def fetch_from_rss(self, feed_url):
        """Fetch news from RSS feed"""
        try:
            import feedparser
            
            feed = feedparser.parse(feed_url)
            articles = []
            
            for entry in feed.entries[:5]:  # Limit to 5 per feed
                title = entry.get('title', '').strip()
                if title:
                    articles.append({
                        'title': title,
                        'url': entry.get('link', ''),
                        'source': feed.feed.get('title', 'RSS Feed'),
                        'published_at': entry.get('published', '')
                    })
            
            return articles
            
        except ImportError:
            logger.warning("feedparser not installed, skipping RSS feeds")
            return []
        except Exception as e:
            logger.error(f"Error fetching RSS from {feed_url}: {str(e)}")
            return []

    def fetch_all_rss(self):
        """Fetch news from all RSS feeds"""
        all_articles = []
        
        for feed_url in self.rss_feeds:
            articles = self.fetch_from_rss(feed_url)
            all_articles.extend(articles)
            time.sleep(0.5)  # Be nice to servers
        
        logger.info(f"Fetched {len(all_articles)} articles from RSS feeds")
        return all_articles

    def fetch_latest_news(self):
        """Fetch latest news from available sources"""
        try:
            articles = []
            
            # Try NewsAPI first
            newsapi_articles = self.fetch_from_newsapi()
            articles.extend(newsapi_articles)
            
            # If no articles from NewsAPI or not configured, try RSS
            if not articles:
                rss_articles = self.fetch_all_rss()
                articles.extend(rss_articles)
            
            # If still no articles, use sample data for demo
            if not articles:
                logger.info("Using sample news data for demonstration")
                articles = self.sample_news.copy()
            
            # Sort by published date (newest first)
            articles = sorted(articles, 
                            key=lambda x: x.get('published_at', ''), 
                            reverse=True)
            
            logger.info(f"Total articles fetched: {len(articles)}")
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching news: {str(e)}")
            # Return sample data as fallback
            return self.sample_news.copy()

    def search_news(self, query):
        """Search for news articles containing specific keywords"""
        try:
            # For demo, filter sample news by query
            filtered_articles = []
            query_lower = query.lower()
            
            for article in self.sample_news:
                if query_lower in article['title'].lower():
                    filtered_articles.append(article)
            
            return filtered_articles
            
        except Exception as e:
            logger.error(f"Error searching news: {str(e)}")
            return []