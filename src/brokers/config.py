"""
Configuration for broker APIs
Add your broker API keys and secrets here
"""

ZERODHA_CONFIG = {
    'api_key': 'your_zerodha_api_key',
    'api_secret': 'your_zerodha_api_secret',
    'user_id': 'your_zerodha_user_id',
    'password': 'your_zerodha_password',  # Be careful with passwords
    'totp_key': 'your_totp_key'  # For 2FA
}

UPSTOX_CONFIG = {
    'api_key': 'your_upstox_api_key',
    'api_secret': 'your_upstox_api_secret',
    'redirect_uri': 'your_redirect_uri',
    'user_id': 'your_upstox_user_id'
}

# Add more broker configurations as needed

# Default broker to use
DEFAULT_BROKER = 'ZERODHA'  # or 'UPSTOX'

# Broker API endpoints
ENDPOINTS = {
    'ZERODHA': {
        'base_url': 'https://api.kite.trade',
        'login': '/session/token',
        'trades': '/trades',
        'orders': '/orders',
        'positions': '/positions',
        'holdings': '/holdings'
    },
    'UPSTOX': {
        'base_url': 'https://api.upstox.com/v2',
        'login': '/login',
        'trades': '/history',
        'orders': '/orders',
        'positions': '/positions',
        'holdings': '/portfolio/holdings'
    }
}
