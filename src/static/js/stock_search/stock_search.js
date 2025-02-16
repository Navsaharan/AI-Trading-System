class StockSearchUI {
    constructor() {
        this.initializeUI();
        this.setupEventListeners();
        this.currentStock = null;
        this.comparisonStock = null;
    }

    initializeUI() {
        // Initialize search components
        this.searchInput = document.getElementById('stock-search-input');
        this.searchResults = document.getElementById('search-results');
        this.stockDetails = document.getElementById('stock-details');
        this.comparisonTable = document.getElementById('stock-comparison');
        
        // Initialize charts
        this.priceChart = new ApexCharts(document.getElementById('price-chart'), {
            chart: {
                type: 'candlestick',
                height: 400,
                animations: {
                    enabled: true,
                    dynamicAnimation: {
                        speed: 1000
                    }
                }
            },
            xaxis: {
                type: 'datetime'
            },
            yaxis: {
                tooltip: {
                    enabled: true
                }
            }
        });
        
        this.volumeChart = new ApexCharts(document.getElementById('volume-chart'), {
            chart: {
                type: 'bar',
                height: 160,
                brush: {
                    enabled: true,
                    target: 'price-chart'
                }
            },
            xaxis: {
                type: 'datetime'
            }
        });
        
        this.priceChart.render();
        this.volumeChart.render();
        
        // Initialize news slider
        this.newsSlider = new Swiper('.news-slider', {
            slidesPerView: 1,
            spaceBetween: 30,
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev'
            },
            pagination: {
                el: '.swiper-pagination',
                clickable: true
            }
        });
    }

    setupEventListeners() {
        // Search input handler
        let searchTimeout;
        this.searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => this.searchStocks(e.target.value), 300);
        });
        
        // Compare button handler
        document.getElementById('compare-btn').addEventListener('click', () => {
            if (this.currentStock) {
                this.showCompareSearch();
            }
        });
        
        // Time period selector
        document.querySelectorAll('.time-period').forEach(btn => {
            btn.addEventListener('click', () => this.updateChartPeriod(btn.dataset.period));
        });
        
        // Exchange selector
        document.querySelectorAll('.exchange-selector').forEach(btn => {
            btn.addEventListener('click', () => this.switchExchange(btn.dataset.exchange));
        });
    }

    async searchStocks(query) {
        if (!query) {
            this.searchResults.innerHTML = '';
            return;
        }

        try {
            const response = await fetch(`/api/stocks/search?q=${encodeURIComponent(query)}`);
            const results = await response.json();
            this.renderSearchResults(results);
        } catch (error) {
            console.error('Search failed:', error);
            this.showError('Failed to search stocks');
        }
    }

    renderSearchResults(results) {
        this.searchResults.innerHTML = results.map(stock => `
            <div class="stock-result" data-symbol="${stock.symbol}" data-exchange="${stock.exchange}">
                <div class="stock-basic">
                    <span class="stock-symbol">${stock.symbol}</span>
                    <span class="stock-name">${stock.name}</span>
                </div>
                <div class="stock-price">
                    <span class="current-price">${stock.lastPrice}</span>
                    <span class="price-change ${stock.change >= 0 ? 'positive' : 'negative'}">
                        ${stock.change}%
                    </span>
                </div>
            </div>
        `).join('');

        // Add click handlers
        document.querySelectorAll('.stock-result').forEach(elem => {
            elem.addEventListener('click', () => {
                this.loadStockDetails(elem.dataset.symbol, elem.dataset.exchange);
            });
        });
    }

    async loadStockDetails(symbol, exchange) {
        try {
            const response = await fetch(`/api/stocks/details/${symbol}?exchange=${exchange}`);
            const details = await response.json();
            this.currentStock = details;
            this.renderStockDetails(details);
        } catch (error) {
            console.error('Failed to load stock details:', error);
            this.showError('Failed to load stock details');
        }
    }

    renderStockDetails(details) {
        // Update stock info section
        document.getElementById('stock-info').innerHTML = `
            <div class="stock-header">
                <h2>${details.basic_info.name} (${details.basic_info.symbol})</h2>
                <div class="stock-price-large">
                    <span class="current-price">${details.basic_info.lastPrice}</span>
                    <span class="price-change ${details.basic_info.change >= 0 ? 'positive' : 'negative'}">
                        ${details.basic_info.change}%
                    </span>
                </div>
            </div>
            
            <div class="stock-metrics">
                <div class="metric">
                    <span class="label">Market Cap</span>
                    <span class="value">${this.formatMarketCap(details.basic_info.market_cap)}</span>
                </div>
                <div class="metric">
                    <span class="label">P/E Ratio</span>
                    <span class="value">${details.basic_info.pe_ratio.toFixed(2)}</span>
                </div>
                <div class="metric">
                    <span class="label">EPS</span>
                    <span class="value">${details.basic_info.eps.toFixed(2)}</span>
                </div>
                <div class="metric">
                    <span class="label">Volume</span>
                    <span class="value">${this.formatVolume(details.basic_info.volume)}</span>
                </div>
            </div>
            
            <div class="ai-prediction">
                <h3>AI Analysis</h3>
                <div class="ai-score">
                    <div class="score-circle" style="--score: ${details.ai_analysis.ai_score}%">
                        <span class="score-value">${details.ai_analysis.ai_score}</span>
                    </div>
                    <div class="score-details">
                        <div class="recommendation ${this.getRecommendationClass(details.ai_analysis.recommendation)}">
                            ${details.ai_analysis.recommendation}
                        </div>
                        <div class="confidence">
                            Confidence: ${details.ai_analysis.confidence}
                        </div>
                    </div>
                </div>
                
                <div class="prediction-metrics">
                    <div class="metric">
                        <span class="label">Technical Score</span>
                        <span class="value">${details.ai_analysis.technical_score}</span>
                    </div>
                    <div class="metric">
                        <span class="label">Fundamental Score</span>
                        <span class="value">${details.ai_analysis.fundamental_score}</span>
                    </div>
                    <div class="metric">
                        <span class="label">Risk Score</span>
                        <span class="value">${details.ai_analysis.risk_score}</span>
                    </div>
                </div>
                
                <div class="price-predictions">
                    <h4>Price Predictions</h4>
                    <div class="prediction">
                        <span class="period">1 Day</span>
                        <span class="predicted-price">${details.ai_analysis.price_prediction["1d"]}</span>
                    </div>
                    <div class="prediction">
                        <span class="period">1 Week</span>
                        <span class="predicted-price">${details.ai_analysis.price_prediction["1w"]}</span>
                    </div>
                    <div class="prediction">
                        <span class="period">1 Month</span>
                        <span class="predicted-price">${details.ai_analysis.price_prediction["1m"]}</span>
                    </div>
                </div>
            </div>
        `;

        // Update news section
        this.updateNewsSlider(details.news);
        
        // Update charts
        this.updateCharts(details.basic_info.historical_data);
    }

    updateNewsSlider(news) {
        const newsSlides = news.map(item => `
            <div class="swiper-slide">
                <div class="news-card ${this.getSentimentClass(item.sentiment)}">
                    <h4>${item.title}</h4>
                    <p>${item.summary}</p>
                    <div class="news-meta">
                        <span class="source">${item.source}</span>
                        <span class="time">${this.formatTime(item.date)}</span>
                    </div>
                    <div class="sentiment-badge">
                        Impact: ${item.sentiment.score}%
                    </div>
                </div>
            </div>
        `).join('');

        this.newsSlider.wrapperEl.innerHTML = newsSlides;
        this.newsSlider.update();
    }

    async compareStocks(symbol1, symbol2) {
        try {
            const response = await fetch(`/api/stocks/compare?symbol1=${symbol1}&symbol2=${symbol2}`);
            const comparison = await response.json();
            this.renderComparison(comparison);
        } catch (error) {
            console.error('Comparison failed:', error);
            this.showError('Failed to compare stocks');
        }
    }

    renderComparison(comparison) {
        const { stocks, comparison: metrics, winner } = comparison;
        
        document.getElementById('comparison-table').innerHTML = `
            <table class="comparison-table">
                <thead>
                    <tr>
                        <th>Metric</th>
                        <th>${stocks[Object.keys(stocks)[0]].basic_info.symbol}</th>
                        <th>${stocks[Object.keys(stocks)[1]].basic_info.symbol}</th>
                    </tr>
                </thead>
                <tbody>
                    ${this.generateComparisonRows(metrics)}
                </tbody>
            </table>
            
            <div class="comparison-summary">
                <h3>AI Analysis</h3>
                <div class="winner-card">
                    <div class="winner-header">
                        Recommended Stock:
                        <span class="winner-symbol">
                            ${stocks[`symbol${winner.winner}`].basic_info.symbol}
                        </span>
                    </div>
                    <div class="winner-reasons">
                        <h4>Key Advantages:</h4>
                        <ul>
                            ${winner.reasons.map(reason => `<li>${reason}</li>`).join('')}
                        </ul>
                    </div>
                    <div class="score-difference">
                        Score Difference: ${winner.score_difference.toFixed(2)}%
                    </div>
                </div>
            </div>
        `;
    }

    generateComparisonRows(metrics) {
        return Object.entries(metrics).map(([metric, values]) => `
            <tr>
                <td>${this.formatMetricName(metric)}</td>
                <td class="${values.better === 1 ? 'better' : ''}">${this.formatMetricValue(metric, values.stock1)}</td>
                <td class="${values.better === 2 ? 'better' : ''}">${this.formatMetricValue(metric, values.stock2)}</td>
            </tr>
        `).join('');
    }

    formatMetricName(metric) {
        return metric.split('_').map(word => 
            word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ');
    }

    formatMetricValue(metric, value) {
        switch(metric) {
            case 'market_cap':
                return this.formatMarketCap(value);
            case 'volume':
                return this.formatVolume(value);
            case 'pe_ratio':
            case 'eps':
                return value.toFixed(2);
            default:
                return value;
        }
    }

    formatMarketCap(value) {
        if (value >= 1e12) return (value / 1e12).toFixed(2) + 'T';
        if (value >= 1e9) return (value / 1e9).toFixed(2) + 'B';
        if (value >= 1e6) return (value / 1e6).toFixed(2) + 'M';
        return value.toFixed(2);
    }

    formatVolume(value) {
        if (value >= 1e7) return (value / 1e7).toFixed(2) + 'Cr';
        if (value >= 1e5) return (value / 1e5).toFixed(2) + 'L';
        if (value >= 1e3) return (value / 1e3).toFixed(2) + 'K';
        return value;
    }

    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = (now - date) / 1000; // difference in seconds

        if (diff < 60) return 'Just now';
        if (diff < 3600) return Math.floor(diff / 60) + 'm ago';
        if (diff < 86400) return Math.floor(diff / 3600) + 'h ago';
        return date.toLocaleDateString();
    }

    getRecommendationClass(recommendation) {
        switch(recommendation.toLowerCase()) {
            case 'strong buy': return 'strong-buy';
            case 'buy': return 'buy';
            case 'hold': return 'hold';
            case 'sell': return 'sell';
            case 'strong sell': return 'strong-sell';
            default: return '';
        }
    }

    getSentimentClass(sentiment) {
        if (sentiment.score >= 70) return 'very-positive';
        if (sentiment.score >= 55) return 'positive';
        if (sentiment.score >= 45) return 'neutral';
        if (sentiment.score >= 30) return 'negative';
        return 'very-negative';
    }

    showError(message) {
        const notification = document.createElement('div');
        notification.className = 'notification error';
        notification.textContent = message;
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 3000);
    }
}

// Initialize the UI
const stockSearch = new StockSearchUI();
