function initializeTradingViewWidgets() {
    // NIFTY Widget
    new TradingView.widget({
        "width": "100%",
        "height": "100%",
        "symbol": "NSE:NIFTY",
        "interval": "D",
        "timezone": "Asia/Kolkata",
        "theme": "light",
        "style": "1",
        "locale": "in",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "hide_side_toolbar": false,
        "allow_symbol_change": true,
        "container_id": "nifty-widget"
    });

    // BANKNIFTY Widget
    new TradingView.widget({
        "width": "100%",
        "height": "100%",
        "symbol": "NSE:BANKNIFTY",
        "interval": "D",
        "timezone": "Asia/Kolkata",
        "theme": "light",
        "style": "1",
        "locale": "in",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "hide_side_toolbar": false,
        "allow_symbol_change": true,
        "container_id": "banknifty-widget"
    });
}

// Export the initialization function
window.initializeTradingViewWidgets = initializeTradingViewWidgets;
