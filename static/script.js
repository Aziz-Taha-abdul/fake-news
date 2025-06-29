// Frontend JavaScript for Fake News Detector

class FakeNewsDetector {
    constructor() {
        this.initializeElements();
        this.bindEvents();
        this.fetchNewsOnLoad();
    }

    initializeElements() {
        // Main elements
        this.headlineInput = document.getElementById('headlineInput');
        this.analyzeBtn = document.getElementById('analyzeBtn');
        this.fetchNewsBtn = document.getElementById('fetchNewsBtn');
        this.analysisResult = document.getElementById('analysisResult');
        this.newsContainer = document.getElementById('newsContainer');
        this.newsList = document.getElementById('newsList');
        this.newsLoading = document.getElementById('newsLoading');
        this.loadingOverlay = document.getElementById('loadingOverlay');
        this.toastContainer = document.getElementById('toastContainer');
        this.newsCount = document.getElementById('newsCount');

        // Result elements
        this.predictionBadge = document.getElementById('predictionBadge');
        this.confidenceScore = document.getElementById('confidenceScore');
        this.analyzedHeadline = document.getElementById('analyzedHeadline');
        this.confidenceFill = document.getElementById('confidenceFill');

        // API base URL
        this.apiBase = '';
    }

    bindEvents() {
        // Analyze button click
        this.analyzeBtn.addEventListener('click', () => this.analyzeHeadline());
        
        // Fetch news button click
        this.fetchNewsBtn.addEventListener('click', () => this.fetchRealTimeNews());
        
        // Enter key in textarea
        this.headlineInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.analyzeHeadline();
            }
        });

        // Auto-resize textarea
        this.headlineInput.addEventListener('input', () => {
            this.headlineInput.style.height = 'auto';
            this.headlineInput.style.height = this.headlineInput.scrollHeight + 'px';
        });
    }

    // Show loading overlay
    showLoading() {
        this.loadingOverlay.style.display = 'flex';
    }

    // Hide loading overlay
    hideLoading() {
        this.loadingOverlay.style.display = 'none';
    }

    // Show toast notification
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <i class="fas fa-${type === 'error' ? 'exclamation-circle' : type === 'success' ? 'check-circle' : 'info-circle'}"></i>
                <span>${message}</span>
            </div>
        `;

        this.toastContainer.appendChild(toast);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.style.animation = 'slideOut 0.3s ease-out forwards';
                setTimeout(() => {
                    if (toast.parentNode) {
                        this.toastContainer.removeChild(toast);
                    }
                }, 300);
            }
        }, 5000);
    }

    // Analyze headline
    async analyzeHeadline() {
        const headline = this.headlineInput.value.trim();
        
        if (!headline) {
            this.showToast('Please enter a headline to analyze', 'error');
            return;
        }

        try {
            this.analyzeBtn.disabled = true;
            this.analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';

            const response = await fetch(`${this.apiBase}/predict`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ headline: headline })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            this.displayAnalysisResult(data);
            this.showToast('Analysis completed successfully', 'success');

        } catch (error) {
            console.error('Error analyzing headline:', error);
            this.showToast('Error analyzing headline. Please try again.', 'error');
        } finally {
            this.analyzeBtn.disabled = false;
            this.analyzeBtn.innerHTML = '<i class="fas fa-search"></i> Analyze Headline';
        }
    }

    // Display analysis result
    displayAnalysisResult(data) {
        // Show result container
        this.analysisResult.style.display = 'block';
        
        // Set prediction badge
        const isFake = data.prediction.toLowerCase() === 'fake';
        this.predictionBadge.textContent = data.prediction;
        this.predictionBadge.className = `badge ${isFake ? 'fake' : 'real'}`;
        
        // Set confidence score
        this.confidenceScore.textContent = `${data.confidence}% confidence`;
        
        // Set analyzed headline
        this.analyzedHeadline.textContent = data.headline;
        
        // Set confidence bar
        this.confidenceFill.style.width = `${data.confidence}%`;
        this.confidenceFill.style.background = isFake 
            ? 'linear-gradient(90deg, #ff6b6b, #ee5a24)' 
            : 'linear-gradient(90deg, #51cf66, #40c057)';

        // Scroll to result
        this.analysisResult.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    // Fetch real-time news
    async fetchRealTimeNews() {
        try {
            this.fetchNewsBtn.disabled = true;
            this.fetchNewsBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Fetching...';
            this.newsLoading.style.display = 'block';
            this.newsList.innerHTML = '';

            // Updated endpoint to match Flask backend
            const response = await fetch(`${this.apiBase}/analyze-live`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            // Flask returns { results: [...] }
            this.displayNews(data.results);
            this.updateNewsCount(data.results.length);
            this.showToast(`Fetched and analyzed ${data.results.length} news articles`, 'success');

        } catch (error) {
            console.error('Error fetching news:', error);
            this.showToast('Error fetching news. Please try again.', 'error');
            this.newsList.innerHTML = '<div class="loading"><p>Failed to load news articles</p></div>';
        } finally {
            this.newsLoading.style.display = 'none';
            this.fetchNewsBtn.disabled = false;
            this.fetchNewsBtn.innerHTML = '<i class="fas fa-refresh"></i> Fetch Latest News';
        }
    }

    // Display news articles
    displayNews(articles) {
        if (!articles || articles.length === 0) {
            this.newsList.innerHTML = '<div class="loading"><p>No news articles available</p></div>';
            return;
        }

        this.newsList.innerHTML = articles.map(article => this.createNewsItem(article)).join('');
    }

    // Create news item HTML
    createNewsItem(article) {
        const isFake = article.prediction.toLowerCase() === 'fake';
        // Use timeAgo for published_at if available
        const publishedDate = article.published_at ? this.timeAgo(article.published_at) : 'Unknown time';
        // Use article.headline if title is missing
        const title = article.title || article.headline || '';
        return `
            <div class="news-item ${isFake ? 'fake' : 'real'}">
                <div class="news-header">
                    <h3 class="news-title">${this.escapeHtml(title)}</h3>
                    <div class="news-prediction">
                        <span class="badge ${isFake ? 'fake' : 'real'}">${article.prediction}</span>
                        <span class="confidence">${article.confidence}%</span>
                    </div>
                </div>
                <div class="news-meta">
                    <span class="news-source">
                        <i class="fas fa-newspaper"></i> ${this.escapeHtml(article.source || '')}
                    </span>
                    <span class="news-time">
                        <i class="fas fa-clock"></i> ${publishedDate}
                    </span>
                </div>
                ${article.url ? `
                    <div style="margin-top: 0.5rem;">
                        <a href="${this.escapeHtml(article.url)}" target="_blank" rel="noopener noreferrer" style="color: #667eea; text-decoration: none; font-size: 0.9rem;">
                            <i class="fas fa-external-link-alt"></i> Read full article
                        </a>
                    </div>
                ` : ''}
            </div>
        `;
    }

    // Update news count
    updateNewsCount(count) {
        this.newsCount.textContent = `${count} articles analyzed`;
    }

    // Escape HTML to prevent XSS
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Fetch news on page load
    async fetchNewsOnLoad() {
        // Wait a bit for the page to settle
        setTimeout(() => {
            this.fetchRealTimeNews();
        }, 1000);
    }

    // Format time ago
    timeAgo(date) {
        const now = new Date();
        const diffInSeconds = Math.floor((now - new Date(date)) / 1000);
        
        if (diffInSeconds < 60) return 'Just now';
        if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
        if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
        return `${Math.floor(diffInSeconds / 86400)} days ago`;
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const app = new FakeNewsDetector();
    
    // Add CSS for slideOut animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideOut {
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
    
    // Add some sample headlines for testing
    const sampleHeadlines = [
        "SHOCKING: Scientists Discover Cure for Aging That Doctors Don't Want You to Know!",
        "Local Government Announces New Infrastructure Development Plan",
        "You Won't Believe This One Weird Trick to Lose Weight Fast!",
        "Study Shows Benefits of Regular Exercise on Mental Health",
        "BREAKING: Celebrity Spotted with Secret Twin Nobody Knew About!",
        "Research Team Publishes Findings on Climate Change Impact"
    ];
    
    // Add quick test functionality (for development)
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        console.log('Development mode: Sample headlines available');
        console.log('Sample headlines:', sampleHeadlines);
        
        // Add sample headline buttons for quick testing
        const testContainer = document.createElement('div');
        testContainer.style.cssText = `
            position: fixed;
            bottom: 20px;
            left: 20px;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 10px;
            border-radius: 8px;
            font-size: 12px;
            z-index: 1000;
            max-width: 300px;
        `;
        testContainer.innerHTML = `
            <div style="margin-bottom: 5px; font-weight: bold;">Quick Test (Dev Mode)</div>
            ${sampleHeadlines.slice(0, 3).map((headline, i) => 
                `<button onclick="document.getElementById('headlineInput').value='${headline}'; document.getElementById('analyzeBtn').click();" 
                 style="display: block; width: 100%; margin: 2px 0; padding: 4px; border: none; border-radius: 4px; cursor: pointer; font-size: 10px;">
                 Test ${i + 1}
                </button>`
            ).join('')}
        `;
        document.body.appendChild(testContainer);
    }
});

// Service worker registration for PWA (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // Uncomment to enable service worker
        // navigator.serviceWorker.register('/sw.js')
        //     .then(registration => console.log('SW registered'))
        //     .catch(error => console.log('SW registration failed'));
    });
}