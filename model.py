import re
import requests
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import numpy as np
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import pickle
import os

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

class FakeNewsDetector:
    def __init__(self):
        model_path = os.path.join('models', 'model.pkl')
        vectorizer_path = os.path.join('models', 'vectorizer.pkl')
        if os.path.exists(model_path) and os.path.exists(vectorizer_path):
            with open(vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            self.stop_words = set(stopwords.words('english'))
            self.lemmatizer = WordNetLemmatizer()
        else:
            # Fallback to demo training if no model is found
            self.vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
            self.model = LogisticRegression()
            self.stop_words = set(stopwords.words('english'))
            self.lemmatizer = WordNetLemmatizer()
            self._train_model()
    
    def _train_model(self):
        # Expanded demo training data - for real use, load a large labeled dataset
        fake_headlines = [
            "Scientists discover aliens living among us",
            "Celebrity dies in fake car crash hoax",
            "Government secretly controls weather with machines",
            "Miracle cure discovered that doctors don't want you to know",
            "Breaking: World ending tomorrow according to ancient prophecy",
            "Local man discovers this one weird trick billionaires hate",
            "Shocking truth about vaccines that will surprise you",
            "Celebrity spotted with three-headed baby",
            "Government admits to hiding alien technology for decades",
            "New study proves chocolate cures all diseases",
            # Added more fake-style headlines
            "You won't believe what this dog did to save its owner!",
            "Doctors hate her for this one simple trick",
            "Lose 20 pounds in a week with this miracle fruit",
            "Aliens built the pyramids, new evidence suggests",
            "Secret society controls the world economy"
        ]
        
        real_headlines = [
            "Stock market closes higher amid economic recovery",
            "New climate change report released by scientists",
            "Local school receives funding for new programs",
            "Technology company announces quarterly earnings",
            "City council approves new infrastructure project",
            "Research shows benefits of regular exercise",
            "Weather forecast predicts rain for weekend",
            "University launches new scholarship program",
            "Hospital opens new treatment facility",
            "Transportation authority updates bus schedules",
            # Added more real-style headlines
            "President addresses the nation on economic policy",
            "Scientists publish new findings on COVID-19",
            "Local elections see record voter turnout",
            "UN holds summit on climate change",
            "FDA approves new treatment for diabetes"
        ]
        
        # Combine and label data
        headlines = fake_headlines + real_headlines
        labels = [0] * len(fake_headlines) + [1] * len(real_headlines)  # 0=fake, 1=real
        
        # Preprocess all headlines
        processed_headlines = [self.preprocess_text(h) for h in headlines]
        
        # Train the model
        X = self.vectorizer.fit_transform(processed_headlines)
        self.model.fit(X, labels)
    
    def preprocess_text(self, text):
        # Clean and preprocess text with tokenization and lemmatization
        text = text.lower()
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        tokens = nltk.word_tokenize(text)
        tokens = [self.lemmatizer.lemmatize(word) for word in tokens if word not in self.stop_words]
        return ' '.join(tokens)
    
    def predict(self, headline):
        try:
            # Preprocess the headline
            processed = self.preprocess_text(headline)
            
            # Vectorize and predict
            X = self.vectorizer.transform([processed])
            prediction = self.model.predict(X)[0]
            probability = self.model.predict_proba(X)[0]
            
            # Get confidence score
            confidence = max(probability) * 100
            
            return {
                'prediction': 'Real' if prediction == 1 else 'Fake',
                'confidence': round(confidence, 2),
                'is_real': bool(prediction),
                'headline': headline
            }
        except Exception as e:
            return {
                'prediction': 'Error',
                'confidence': 0,
                'is_real': False,
                'headline': headline,
                'error': str(e)
            }

def fetch_recent_news(query="latest news", num_articles=5):
    """Fetch recent news headlines"""
    try:
        # Using a simple news API alternative - RSS feeds
        urls = [
            "https://rss.cnn.com/rss/edition.rss",
            "https://feeds.bbci.co.uk/news/rss.xml",
            "https://www.reuters.com/rssfeed/topNews"
        ]
        
        headlines = []
        for url in urls:
            if len(headlines) >= num_articles:
                break
            try:
                response = requests.get(url, timeout=5)
                soup = BeautifulSoup(response.content, 'xml')
                items = soup.find_all('item')
                for item in items:
                    if len(headlines) >= num_articles:
                        break
                    title = item.find('title')
                    if title:
                        headlines.append(title.text.strip())
            except Exception:
                continue
        return headlines[:num_articles]
    except Exception:
        return ["Unable to fetch news at this time"]