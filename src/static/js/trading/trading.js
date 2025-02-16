class TradingDashboard {
    constructor() {
        this.initializeCharts();
        this.setupEventListeners();
        this.initializeWebSocket();
        this.loadWatchlist();
    }

    initializeCharts() {
        // Stock Price Chart
        this.stockChart = new ApexCharts(document.getElementById('stock-chart'), {
            chart: {
                type: 'candlestick',
                height: 400,
                animations: {
                    enabled: true,
                    easing: 'easeinout',
                    dynamicAnimation: {
                        speed: 1000
                    }
                },
                toolbar: {
                    show: true,
                    tools: {
                        download: true,
                        selection: true,
                        zoom: true,
                        zoomin: true,
                        zoomout: true,
                        pan: true,
                        reset: true
                    }
                }
            },
            xaxis: {
                type: 'datetime',
                labels: {
                    datetimeUTC: false,
                    style: {
                        colors: '#ffffff'
                    }
                }
            },
            yaxis: {
                tooltip: {
                    enabled: true
                },
                labels: {
                    style: {
                        colors: '#ffffff'
                    }
                }
            },
            grid: {
                borderColor: '#404040'
            },
            plotOptions: {
                candlestick: {
                    colors: {
                        upward: '#00E396',
                        downward: '#FF4560'
                    },
                    wick: {
                        useFillColor: true
                    }
                }
            },
            tooltip: {
                theme: 'dark',
                x: {
                    format: 'dd MMM HH:mm'
                }
            },
            series: [{
                data: [] // Will be populated with OHLC data
            }]
        });

        // Volume Chart
        this.volumeChart = new ApexCharts(document.getElementById('volume-chart'), {
            chart: {
                type: 'bar',
                height: 100,
                brush: {
                    enabled: true,
                    target: 'stock-chart'
                }
            },
            dataLabels: {
                enabled: false
            },
            xaxis: {
                type: 'datetime',
                labels: {
                    datetimeUTC: false,
                    style: {
                        colors: '#ffffff'
                    }
                }
            },
            yaxis: {
                labels: {
                    style: {
                        colors: '#ffffff'
                    },
                    formatter: (value) => {
                        return this.formatVolume(value);
                    }
                }
            },
            series: [{
                name: 'Volume',
                data: [] // Will be populated with volume data
            }],
            colors: ['#0066cc']
        });

        this.stockChart.render();
        this.volumeChart.render();
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', () => this.switchSection(btn.dataset.section));
        });

        // Stock Search
        const searchInput = document.getElementById('stock-search');
        let searchTimeout;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => this.searchStocks(e.target.value), 300);
        });

        // Order Type Tabs
        document.querySelectorAll('.order-tabs .tab-btn').forEach(btn => {
            btn.addEventListener('click', () => this.switchOrderForm(btn.dataset.tab));
        });

        // Buy/Sell Buttons
        document.querySelectorAll('.buy-sell-btns button').forEach(btn => {
            btn.addEventListener('click', () => this.toggleBuySell(btn));
        });

        // Price Type Change
        document.querySelector('#regular-order select').addEventListener('change', (e) => {
            this.updatePriceInputs(e.target.value);
        });

        // Place Order Button
        document.querySelector('.place-order-btn').addEventListener('click', () => {
            this.placeOrder();
        });

        // Chart Time Controls
        document.querySelectorAll('.time-btn').forEach(btn => {
            btn.addEventListener('click', () => this.updateTimeframe(btn));
        });
    }

    initializeWebSocket() {
        this.ws = new WebSocket('wss://your-websocket-server/trading');
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            switch(data.type) {
                case 'tick':
                    this.updateStockPrice(data);
                    break;
                case 'depth':
                    this.updateMarketDepth(data);
                    break;
                case 'order_update':
                    this.updateOrder(data);
                    break;
                case 'position_update':
                    this.updatePosition(data);
                    break;
            }
        };

        this.ws.onclose = () => {
            console.log('WebSocket connection closed. Attempting to reconnect...');
            setTimeout(() => this.initializeWebSocket(), 5000);
        };
    }

    async loadWatchlist() {
        try {
            const response = await fetch('/api/watchlist');
            const watchlist = await response.json();
            this.renderWatchlist(watchlist);
        } catch (error) {
            console.error('Error loading watchlist:', error);
            this.showError('Failed to load watchlist');
        }
    }

    async searchStocks(query) {
        if (!query) return;
        
        try {
            const response = await fetch(`/api/stocks/search?q=${encodeURIComponent(query)}`);
            const results = await response.json();
            this.renderSearchResults(results);
        } catch (error) {
            console.error('Error searching stocks:', error);
        }
    }

    async loadStockData(symbol, timeframe = '1D') {
        try {
            const response = await fetch(`/api/stocks/${symbol}/ohlc?timeframe=${timeframe}`);
            const data = await response.json();
            this.updateCharts(data);
        } catch (error) {
            console.error('Error loading stock data:', error);
            this.showError('Failed to load stock data');
        }
    }

    updateCharts(data) {
        // Update OHLC chart
        const ohlcData = data.candles.map(candle => ({
            x: new Date(candle.timestamp).getTime(),
            y: [candle.open, candle.high, candle.low, candle.close]
        }));

        // Update Volume chart
        const volumeData = data.candles.map(candle => ({
            x: new Date(candle.timestamp).getTime(),
            y: candle.volume
        }));

        this.stockChart.updateSeries([{
            data: ohlcData
        }]);

        this.volumeChart.updateSeries([{
            data: volumeData
        }]);
    }

    async placeOrder() {
        const orderForm = document.querySelector('.order-form:not(.hidden)');
        const orderType = orderForm.id.replace('-order', '');
        
        try {
            const orderData = this.getOrderData(orderType);
            const response = await fetch('/api/orders', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(orderData)
            });

            const result = await response.json();
            if (result.success) {
                this.showSuccess('Order placed successfully');
                this.resetOrderForm();
            } else {
                this.showError(result.message || 'Failed to place order');
            }
        } catch (error) {
            console.error('Error placing order:', error);
            this.showError('Failed to place order');
        }
    }

    getOrderData(orderType) {
        const form = document.getElementById(`${orderType}-order`);
        const data = {
            type: orderType,
            symbol: document.querySelector('.stock-name').textContent,
            side: form.querySelector('.buy-btn').classList.contains('active') ? 'BUY' : 'SELL',
            quantity: parseInt(form.querySelector('input[type="number"]').value),
            priceType: form.querySelector('select').value
        };

        // Add price for limit orders
        if (data.priceType === 'LIMIT') {
            data.price = parseFloat(form.querySelector('.price-input input').value);
        }

        // Add trigger price for stop loss orders
        if (data.priceType.startsWith('SL')) {
            data.triggerPrice = parseFloat(form.querySelector('.trigger-input input').value);
        }

        // Add target and stoploss for bracket orders
        if (orderType === 'bracket') {
            data.target = parseFloat(form.querySelector('.target-input input').value);
            data.stopLoss = parseFloat(form.querySelector('.stoploss-input input').value);
        }

        return data;
    }

    switchSection(section) {
        document.querySelectorAll('.dashboard-section').forEach(s => {
            s.classList.add('hidden');
        });
        document.getElementById(`${section}-section`).classList.remove('hidden');
        
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-section="${section}"]`).classList.add('active');
    }

    switchOrderForm(formId) {
        document.querySelectorAll('.order-form').forEach(form => {
            form.classList.add('hidden');
        });
        document.getElementById(`${formId}-order`).classList.remove('hidden');
        
        document.querySelectorAll('.order-tabs .tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${formId}"]`).classList.add('active');
    }

    toggleBuySell(button) {
        const isBuy = button.classList.contains('buy-btn');
        const form = button.closest('.order-form');
        
        form.querySelector('.buy-btn').classList.toggle('active', isBuy);
        form.querySelector('.sell-btn').classList.toggle('active', !isBuy);
    }

    updatePriceInputs(priceType) {
        const form = document.querySelector('.order-form:not(.hidden)');
        const priceInput = form.querySelector('.price-input');
        const triggerInput = form.querySelector('.trigger-input');

        priceInput.classList.toggle('hidden', priceType === 'MARKET');
        triggerInput.classList.toggle('hidden', !priceType.startsWith('SL'));
    }

    updateTimeframe(button) {
        document.querySelectorAll('.time-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        button.classList.add('active');

        const symbol = document.querySelector('.stock-name').textContent;
        this.loadStockData(symbol, button.textContent);
    }

    formatVolume(value) {
        if (value >= 10000000) return (value / 10000000).toFixed(2) + ' Cr';
        if (value >= 100000) return (value / 100000).toFixed(2) + ' L';
        if (value >= 1000) return (value / 1000).toFixed(2) + ' K';
        return value;
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 3000);
    }

    resetOrderForm() {
        const form = document.querySelector('.order-form:not(.hidden)');
        form.querySelector('input[type="number"]').value = 1;
        form.querySelector('select').value = 'MARKET';
        this.updatePriceInputs('MARKET');
    }
}

// Initialize dashboard
const tradingDashboard = new TradingDashboard();
