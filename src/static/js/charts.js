// FamilyHVSDN Charts JavaScript

function initializeCharts() {
    // Initialize all charts
    createMarketChart();
    createPortfolioChart();
    createRiskChart();
    createAIChart();
}

function createMarketChart() {
    const trace = {
        x: [], // Time
        y: [], // Price
        type: 'scatter',
        mode: 'lines',
        name: 'NIFTY 50',
        line: {
            color: '#00ff1a',
            width: 2
        }
    };

    const layout = {
        title: 'Market Overview',
        paper_bgcolor: '#1e1e1e',
        plot_bgcolor: '#1e1e1e',
        font: {
            color: '#ffffff'
        },
        xaxis: {
            title: 'Time',
            gridcolor: '#333333'
        },
        yaxis: {
            title: 'Price',
            gridcolor: '#333333'
        },
        showlegend: true,
        legend: {
            x: 0,
            y: 1
        }
    };

    Plotly.newPlot('market-chart', [trace], layout);
}

function createPortfolioChart() {
    const trace = {
        values: [30, 20, 15, 10, 25],
        labels: ['Stocks', 'Mutual Funds', 'ETFs', 'Bonds', 'Cash'],
        type: 'pie',
        marker: {
            colors: ['#00ff1a', '#00cc15', '#009910', '#00660b', '#003306']
        }
    };

    const layout = {
        title: 'Portfolio Allocation',
        paper_bgcolor: '#1e1e1e',
        plot_bgcolor: '#1e1e1e',
        font: {
            color: '#ffffff'
        },
        showlegend: true,
        legend: {
            x: 0,
            y: 1
        }
    };

    Plotly.newPlot('portfolio-chart', [trace], layout);
}

function createRiskChart() {
    const trace1 = {
        x: [], // Time
        y: [], // VaR
        type: 'scatter',
        mode: 'lines',
        name: 'Value at Risk',
        line: {
            color: '#ff355e',
            width: 2
        }
    };

    const trace2 = {
        x: [], // Time
        y: [], // Beta
        type: 'scatter',
        mode: 'lines',
        name: 'Beta',
        line: {
            color: '#ffd700',
            width: 2
        }
    };

    const layout = {
        title: 'Risk Metrics',
        paper_bgcolor: '#1e1e1e',
        plot_bgcolor: '#1e1e1e',
        font: {
            color: '#ffffff'
        },
        xaxis: {
            title: 'Time',
            gridcolor: '#333333'
        },
        yaxis: {
            title: 'Value',
            gridcolor: '#333333'
        },
        showlegend: true,
        legend: {
            x: 0,
            y: 1
        }
    };

    Plotly.newPlot('risk-chart', [trace1, trace2], layout);
}

function createAIChart() {
    const trace1 = {
        x: [], // Time
        y: [], // Actual Price
        type: 'scatter',
        mode: 'lines',
        name: 'Actual',
        line: {
            color: '#00ff1a',
            width: 2
        }
    };

    const trace2 = {
        x: [], // Time
        y: [], // Predicted Price
        type: 'scatter',
        mode: 'lines',
        name: 'AI Prediction',
        line: {
            color: '#ffd700',
            width: 2,
            dash: 'dash'
        }
    };

    const layout = {
        title: 'AI Price Predictions',
        paper_bgcolor: '#1e1e1e',
        plot_bgcolor: '#1e1e1e',
        font: {
            color: '#ffffff'
        },
        xaxis: {
            title: 'Time',
            gridcolor: '#333333'
        },
        yaxis: {
            title: 'Price',
            gridcolor: '#333333'
        },
        showlegend: true,
        legend: {
            x: 0,
            y: 1
        }
    };

    Plotly.newPlot('ai-chart', [trace1, trace2], layout);
}

function updateMarketChart(data) {
    const update = {
        x: [data.time],
        y: [data.price]
    };

    Plotly.extendTraces('market-chart', update, [0]);
}

function updatePortfolioChart(data) {
    const update = {
        values: [data.stocks, data.mutualFunds, data.etfs, data.bonds, data.cash],
        labels: ['Stocks', 'Mutual Funds', 'ETFs', 'Bonds', 'Cash']
    };

    Plotly.update('portfolio-chart', update);
}

function updateRiskChart(data) {
    const update = {
        x: [[data.time], [data.time]],
        y: [[data.var], [data.beta]]
    };

    Plotly.extendTraces('risk-chart', update, [0, 1]);
}

function updateAIChart(data) {
    const update = {
        x: [[data.time], [data.time]],
        y: [[data.actualPrice], [data.predictedPrice]]
    };

    Plotly.extendTraces('ai-chart', update, [0, 1]);
}
