from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from model import FakeNewsDetector, fetch_recent_news
from news_fetcher import NewsFetcher
import threading
import time

app = Flask(__name__)
CORS(app)

# Initialize the detector
detector = FakeNewsDetector()

# Initialize the news fetcher
news_fetcher = NewsFetcher()

# Store recent news for real-time updates
recent_news = []

def update_news_feed():
    """Background task to update news feed"""
    global recent_news
    while True:
        try:
            articles = news_fetcher.fetch_latest_news()[:10]
            recent_news = []
            for article in articles:
                # Use title for prediction
                result = detector.predict(article.get('title', ''))
                # Merge prediction with article metadata
                merged = {**article, **result}
                recent_news.append(merged)
        except Exception as e:
            print(f"Error updating news feed: {e}")
        
        time.sleep(300)  # Update every 5 minutes

# Start background news update
news_thread = threading.Thread(target=update_news_feed, daemon=True)
news_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict_headline():
    try:
        data = request.get_json()
        headline = data.get('headline', '').strip()
        
        if not headline:
            return jsonify({'error': 'Please provide a headline'}), 400
        
        result = detector.predict(headline)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/recent-news')
def get_recent_news():
    """Get recent analyzed news"""
    return jsonify({'news': recent_news[:10]})

@app.route('/analyze-live')
def analyze_live_news():
    """Fetch and analyze live news"""
    try:
        articles = news_fetcher.fetch_latest_news()[:5]
        results = []
        for article in articles:
            result = detector.predict(article.get('title', ''))
            merged = {**article, **result}
            results.append(merged)
        return jsonify({'results': results})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)