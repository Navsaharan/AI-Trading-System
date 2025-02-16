class IPODashboard {
    constructor() {
        this.initializeCharts();
        this.setupEventListeners();
        this.loadData();
    }

    initializeCharts() {
        // 1. Subscription Trends Chart (Area Stacked)
        this.subscriptionChart = new ApexCharts(document.getElementById('subscription-chart'), {
            chart: {
                type: 'area',
                height: 350,
                stacked: true,
                animations: {
                    enabled: true,
                    easing: 'easeinout',
                    speed: 800
                }
            },
            dataLabels: { enabled: false },
            series: [
                { name: 'Retail (RII)', data: [] },
                { name: 'HNI', data: [] },
                { name: 'QIB', data: [] }
            ],
            xaxis: {
                type: 'datetime',
                labels: { datetimeUTC: false }
            },
            yaxis: {
                title: { text: 'Subscription (x times)' },
                labels: {
                    formatter: (val) => `${val.toFixed(2)}x`
                }
            },
            fill: {
                type: 'gradient',
                gradient: {
                    opacityFrom: 0.6,
                    opacityTo: 0.1
                }
            },
            colors: ['#00E396', '#FEB019', '#008FFB'],
            tooltip: {
                y: {
                    formatter: (val) => `${val.toFixed(2)}x subscribed`
                }
            }
        });

        // 2. GMP Movement Chart (Line with Annotations)
        this.gmpTrendChart = new ApexCharts(document.getElementById('gmp-trend-chart'), {
            chart: {
                type: 'line',
                height: 350,
                animations: {
                    enabled: true,
                    easing: 'linear',
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
                        pan: true
                    }
                }
            },
            stroke: {
                curve: 'smooth',
                width: 3
            },
            series: [{
                name: 'Grey Market Premium',
                data: []
            }],
            annotations: {
                points: []  // Will be populated with news events
            },
            xaxis: {
                type: 'datetime',
                labels: { datetimeUTC: false }
            },
            yaxis: {
                title: { text: 'Premium (₹)' },
                labels: {
                    formatter: (val) => `₹${val.toFixed(2)}`
                }
            },
            markers: {
                size: 4,
                strokeWidth: 2
            },
            colors: ['#00E396']
        });

        // 3. Listing Performance Comparison Chart
        this.listingPerformanceChart = new ApexCharts(document.getElementById('listing-performance-chart'), {
            chart: {
                type: 'bar',
                height: 350,
                toolbar: { show: false }
            },
            plotOptions: {
                bar: {
                    horizontal: false,
                    columnWidth: '55%',
                    borderRadius: 5
                }
            },
            series: [
                { name: 'Expected', data: [] },
                { name: 'Actual', data: [] }
            ],
            dataLabels: {
                enabled: true,
                formatter: (val) => `${val.toFixed(1)}%`
            },
            xaxis: {
                categories: [],
                labels: { rotate: -45 }
            },
            yaxis: {
                title: { text: 'Listing Gain (%)' },
                labels: {
                    formatter: (val) => `${val.toFixed(1)}%`
                }
            },
            colors: ['#008FFB', '#00E396'],
            legend: {
                position: 'top'
            }
        });

        // 4. Sector Performance Heatmap
        this.sectorPerformanceChart = new ApexCharts(document.getElementById('sector-performance-chart'), {
            chart: {
                type: 'heatmap',
                height: 350,
                toolbar: { show: false }
            },
            plotOptions: {
                heatmap: {
                    shadeIntensity: 0.5,
                    radius: 0,
                    colorScale: {
                        ranges: [
                            { from: -50, to: 0, name: 'Loss', color: '#FF4560' },
                            { from: 0, to: 25, name: 'Low Gain', color: '#FEB019' },
                            { from: 25, to: 50, name: 'Medium Gain', color: '#00E396' },
                            { from: 50, to: 100, name: 'High Gain', color: '#008FFB' }
                        ]
                    }
                }
            },
            dataLabels: {
                enabled: true,
                formatter: (val) => `${val.toFixed(1)}%`
            },
            series: [],  // Will be populated with sector data
            title: {
                text: 'Sector-wise IPO Performance (Last 12 Months)'
            }
        });

        // 5. Risk & Allotment Probability Charts
        this.riskGaugeChart = new ApexCharts(document.getElementById('risk-gauge-chart'), {
            chart: {
                type: 'radialBar',
                height: 250
            },
            plotOptions: {
                radialBar: {
                    startAngle: -135,
                    endAngle: 135,
                    hollow: {
                        size: '70%'
                    },
                    track: {
                        background: '#333',
                        startAngle: -135,
                        endAngle: 135,
                    },
                    dataLabels: {
                        name: {
                            show: true,
                            fontSize: '16px',
                            offsetY: -10
                        },
                        value: {
                            formatter: function(val) {
                                return val + "%"
                            },
                            color: "#fff",
                            fontSize: "30px",
                            show: true,
                        }
                    }
                }
            },
            fill: {
                type: "gradient",
                gradient: {
                    shade: "dark",
                    type: "horizontal",
                    gradientToColors: ["#00E396"],
                    stops: [0, 100]
                }
            },
            series: [75],  // Risk percentage
            labels: ['Risk Level']
        });

        this.allotmentProbabilityChart = new ApexCharts(document.getElementById('allotment-probability-chart'), {
            chart: {
                type: 'donut',
                height: 250
            },
            series: [],  // Probability percentage
            labels: ['Allotment Chance', 'No Allotment'],
            colors: ['#00E396', '#333'],
            plotOptions: {
                pie: {
                    donut: {
                        size: '70%',
                        labels: {
                            show: true,
                            name: {
                                show: true,
                                fontSize: '16px'
                            },
                            value: {
                                show: true,
                                fontSize: '20px',
                                formatter: function(val) {
                                    return val + "%"
                                }
                            },
                            total: {
                                show: true,
                                label: 'Total Chance',
                                formatter: function(w) {
                                    return w.globals.seriesTotals[0] + "%"
                                }
                            }
                        }
                    }
                }
            }
        });

        // Render all charts
        this.subscriptionChart.render();
        this.gmpTrendChart.render();
        this.listingPerformanceChart.render();
        this.sectorPerformanceChart.render();
        this.riskGaugeChart.render();
        this.allotmentProbabilityChart.render();
    }

    setupEventListeners() {
        // IPO Selection
        document.getElementById('ipo-selector').addEventListener('change', (e) => {
            this.loadIPODetails(e.target.value);
        });

        // Tab Switching
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', () => {
                this.switchTab(button.dataset.tab);
            });
        });

        // Refresh Button
        document.getElementById('refresh-btn').addEventListener('click', () => {
            this.loadData();
        });
    }

    async loadData() {
        try {
            // Load Upcoming IPOs
            const upcomingResponse = await fetch('/api/ipo/upcoming');
            const upcomingIPOs = await upcomingResponse.json();
            this.renderUpcomingIPOs(upcomingIPOs);

            // Load Ongoing IPOs
            const ongoingResponse = await fetch('/api/ipo/ongoing');
            const ongoingIPOs = await ongoingResponse.json();
            this.renderOngoingIPOs(ongoingIPOs);

            // Update IPO Selector
            this.updateIPOSelector([...upcomingIPOs, ...ongoingIPOs]);
        } catch (error) {
            console.error('Error loading IPO data:', error);
            this.showError('Failed to load IPO data');
        }
    }

    async loadIPODetails(ipoId) {
        try {
            // Fetch all required data
            const [ipoDetails, analysisData, subscriptionData, gmpData, performanceData, sectorData] = await Promise.all([
                this.fetchIPODetails(ipoId),
                this.fetchRiskAnalysis(ipoId),
                this.fetchSubscriptionTrends(ipoId),
                this.fetchGMPTrends(ipoId),
                this.fetchListingPerformance(ipoId),
                this.fetchSectorPerformance()
            ]);

            // Render IPO details
            this.renderIPODetails(ipoDetails);

            // Update charts
            this.updateCharts(subscriptionData, gmpData, performanceData, sectorData, analysisData);
        } catch (error) {
            console.error('Error loading IPO details:', error);
            this.showError('Failed to load IPO details');
        }
    }

    updateCharts(subscriptionData, gmpData, performanceData, sectorData, analysisData) {
        // Update Subscription Chart
        this.updateSubscriptionChart(subscriptionData);

        // Update GMP Chart with news annotations
        this.updateGMPChart(gmpData);

        // Update Listing Performance Chart
        this.updateListingPerformanceChart(performanceData);

        // Update Sector Performance Heatmap
        this.updateSectorPerformanceChart(sectorData);

        // Update Risk & Probability Charts
        this.updateRiskCharts(analysisData);
    }

    updateSubscriptionChart(data) {
        const series = [
            {
                name: 'Retail (RII)',
                data: data.retail.map(point => ({
                    x: new Date(point.timestamp).getTime(),
                    y: point.value
                }))
            },
            {
                name: 'HNI',
                data: data.hni.map(point => ({
                    x: new Date(point.timestamp).getTime(),
                    y: point.value
                }))
            },
            {
                name: 'QIB',
                data: data.qib.map(point => ({
                    x: new Date(point.timestamp).getTime(),
                    y: point.value
                }))
            }
        ];
        this.subscriptionChart.updateSeries(series);
    }

    updateGMPChart(data) {
        const series = [{
            name: 'Grey Market Premium',
            data: data.gmp.map(point => ({
                x: new Date(point.timestamp).getTime(),
                y: point.premium
            }))
        }];

        // Add news annotations
        const annotations = {
            points: data.news.map(news => ({
                x: new Date(news.timestamp).getTime(),
                y: news.gmp_value,
                marker: {
                    size: 6,
                    fillColor: '#fff',
                    strokeColor: news.sentiment > 0 ? '#00E396' : '#FF4560',
                    radius: 2
                },
                label: {
                    borderColor: news.sentiment > 0 ? '#00E396' : '#FF4560',
                    text: news.title
                }
            }))
        };

        this.gmpTrendChart.updateOptions({ annotations });
        this.gmpTrendChart.updateSeries(series);
    }

    updateListingPerformanceChart(data) {
        const series = [
            {
                name: 'Expected',
                data: data.map(ipo => ipo.expected_gain)
            },
            {
                name: 'Actual',
                data: data.map(ipo => ipo.actual_gain)
            }
        ];
        const categories = data.map(ipo => ipo.company_name);

        this.listingPerformanceChart.updateOptions({ xaxis: { categories } });
        this.listingPerformanceChart.updateSeries(series);
    }

    updateSectorPerformanceChart(data) {
        const series = Object.entries(data).map(([sector, months]) => ({
            name: sector,
            data: months.map(m => m.performance)
        }));

        this.sectorPerformanceChart.updateSeries(series);
    }

    updateRiskCharts(data) {
        // Update Risk Gauge
        this.riskGaugeChart.updateSeries([data.risk_percentage]);

        // Update Allotment Probability
        this.allotmentProbabilityChart.updateSeries([
            data.allotment_probability,
            100 - data.allotment_probability
        ]);
    }

    renderUpcomingIPOs(ipos) {
        const container = document.getElementById('upcoming-ipos');
        container.innerHTML = ipos.map(ipo => `
            <div class="ipo-card">
                <div class="ipo-header">
                    <h3>${ipo.company_name}</h3>
                    <span class="industry-tag">${ipo.industry}</span>
                </div>
                <div class="ipo-details">
                    <div class="detail-row">
                        <span>Price Band:</span>
                        <span>${ipo.price_band}</span>
                    </div>
                    <div class="detail-row">
                        <span>Lot Size:</span>
                        <span>${ipo.lot_size} shares</span>
                    </div>
                    <div class="detail-row">
                        <span>Issue Size:</span>
                        <span>${ipo.issue_size}</span>
                    </div>
                    <div class="detail-row">
                        <span>Opens:</span>
                        <span>${ipo.dates.open}</span>
                    </div>
                </div>
                <div class="ipo-analysis">
                    ${this.renderAnalysisBadges(ipo.analysis)}
                </div>
                <button class="view-details-btn" onclick="ipoDashboard.loadIPODetails(${ipo.id})">
                    View Details
                </button>
            </div>
        `).join('');
    }

    renderOngoingIPOs(ipos) {
        const container = document.getElementById('ongoing-ipos');
        container.innerHTML = ipos.map(ipo => `
            <div class="ipo-card active">
                <div class="ipo-header">
                    <h3>${ipo.company_name}</h3>
                    <span class="industry-tag">${ipo.industry}</span>
                </div>
                <div class="subscription-status">
                    <div class="progress-container">
                        <div class="progress-bar" style="width: ${Math.min(100, ipo.subscription.total * 100)}%"></div>
                        <span class="subscription-text">${ipo.subscription.total}</span>
                    </div>
                </div>
                <div class="ipo-details">
                    <div class="detail-row">
                        <span>Retail:</span>
                        <span>${ipo.subscription.retail}</span>
                    </div>
                    <div class="detail-row">
                        <span>HNI:</span>
                        <span>${ipo.subscription.hni}</span>
                    </div>
                    <div class="detail-row">
                        <span>QIB:</span>
                        <span>${ipo.subscription.qib}</span>
                    </div>
                    <div class="detail-row">
                        <span>Closes:</span>
                        <span>${ipo.dates.close}</span>
                    </div>
                </div>
                <div class="ipo-analysis">
                    ${this.renderAnalysisBadges(ipo.analysis)}
                </div>
                <button class="view-details-btn" onclick="ipoDashboard.loadIPODetails(${ipo.id})">
                    View Details
                </button>
            </div>
        `).join('');
    }

    renderIPODetails(details) {
        document.getElementById('ipo-details').innerHTML = `
            <div class="detail-section">
                <h2>${details.company_name}</h2>
                <div class="company-info">
                    <span class="industry-tag">${details.industry}</span>
                    <span class="exchange-tag">${details.exchange}</span>
                </div>
                <div class="price-info">
                    <div class="price-band">
                        <h4>Price Band</h4>
                        <span>${details.price_band}</span>
                    </div>
                    <div class="lot-size">
                        <h4>Lot Size</h4>
                        <span>${details.lot_size} shares</span>
                    </div>
                    <div class="issue-size">
                        <h4>Issue Size</h4>
                        <span>${details.issue_size}</span>
                    </div>
                </div>
                <div class="dates-info">
                    <div class="date-item">
                        <i class="fas fa-calendar-plus"></i>
                        <span>Opens: ${details.dates.open}</span>
                    </div>
                    <div class="date-item">
                        <i class="fas fa-calendar-minus"></i>
                        <span>Closes: ${details.dates.close}</span>
                    </div>
                    <div class="date-item">
                        <i class="fas fa-calendar-check"></i>
                        <span>Listing: ${details.dates.listing || 'TBA'}</span>
                    </div>
                </div>
            </div>
            <div class="news-section">
                <h3>Recent News</h3>
                ${this.renderNewsItems(details.recent_news)}
            </div>
            <div class="investments-section">
                <h3>Institutional Investments</h3>
                ${this.renderInvestments(details.institutional_investments)}
            </div>
        `;
    }

    renderAnalysisBadges(analysis) {
        if (!analysis) return '';
        return `
            <div class="analysis-badges">
                <span class="badge risk-${analysis.risk_level.toLowerCase()}">
                    ${analysis.risk_level} Risk
                </span>
                <span class="badge">
                    ${analysis.expected_listing_gain} Expected Gain
                </span>
                <span class="badge">
                    ${analysis.allotment_probability} Allotment Chance
                </span>
            </div>
        `;
    }

    renderNewsItems(news) {
        return news.map(item => `
            <div class="news-item ${item.sentiment.toLowerCase()}">
                <div class="news-header">
                    <span class="news-source">${item.source}</span>
                    <span class="news-date">${item.published_at}</span>
                </div>
                <h4 class="news-title">${item.title}</h4>
                <a href="${item.url}" target="_blank" class="news-link">Read More</a>
            </div>
        `).join('');
    }

    renderInvestments(investments) {
        return investments.map(inv => `
            <div class="investment-item">
                <div class="institution-info">
                    <span class="institution-name">${inv.institution}</span>
                    <span class="institution-category">${inv.category}</span>
                </div>
                <div class="investment-amount">${inv.amount}</div>
                <div class="investment-date">${inv.date}</div>
            </div>
        `).join('');
    }

    updateIPOSelector(ipos) {
        const selector = document.getElementById('ipo-selector');
        selector.innerHTML = `
            <option value="">Select an IPO</option>
            ${ipos.map(ipo => `
                <option value="${ipo.id}">${ipo.company_name}</option>
            `).join('')}
        `;
    }

    switchTab(tabId) {
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.style.display = 'none';
        });
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('active');
        });
        document.getElementById(tabId).style.display = 'block';
        document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');
    }

    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        document.body.appendChild(errorDiv);
        setTimeout(() => errorDiv.remove(), 3000);
    }

    async fetchIPODetails(ipoId) {
        try {
            const response = await fetch(`/api/ipo/${ipoId}`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching IPO details:', error);
            throw error;
        }
    }

    async fetchRiskAnalysis(ipoId) {
        try {
            const response = await fetch(`/api/ipo/${ipoId}/analysis`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching risk analysis:', error);
            throw error;
        }
    }

    async fetchSubscriptionTrends(ipoId) {
        try {
            const response = await fetch(`/api/ipo/${ipoId}/subscription`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching subscription trends:', error);
            throw error;
        }
    }

    async fetchGMPTrends(ipoId) {
        try {
            const response = await fetch(`/api/ipo/${ipoId}/gmp`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching GMP trends:', error);
            throw error;
        }
    }

    async fetchListingPerformance(ipoId) {
        try {
            const response = await fetch(`/api/ipo/${ipoId}/listing-performance`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching listing performance:', error);
            throw error;
        }
    }

    async fetchSectorPerformance() {
        try {
            const response = await fetch('/api/sector-performance');
            return await response.json();
        } catch (error) {
            console.error('Error fetching sector performance:', error);
            throw error;
        }
    }
}

// Initialize dashboard
const ipoDashboard = new IPODashboard();
