from flask import Blueprint, jsonify, request
from ..auth.firebase_auth import verify_token
from ..core.trading_engine import TradingEngine
from ..core.risk_manager import RiskManager
from ..services.advanced_ai_features import AITradingService
import logging

logger = logging.getLogger(__name__)
user_panel = Blueprint('user_panel', __name__)

# Initialize services
trading_engine = TradingEngine()
risk_manager = RiskManager()
ai_service = AITradingService()

@user_panel.before_request
def verify_auth():
    """Verify Firebase authentication token."""
    if request.method == 'OPTIONS':
        return

    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'No authorization token provided'}), 401

        token = auth_header.split(' ')[1]
        user_data = verify_token(token)
        request.user = user_data
        
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        return jsonify({'error': 'Invalid authentication token'}), 401

@user_panel.route('/trading/signals', methods=['GET'])
def get_trading_signals():
    """Get FamilyHVSDN trading signals"""
    try:
        # Get parameters
        symbol = request.args.get('symbol')
        timeframe = request.args.get('timeframe', '1d')
        
        if not symbol:
            return jsonify({'error': 'Symbol parameter is required'}), 400
            
        # Get trading signals
        signals = ai_service.get_trading_signals(symbol, timeframe)
        
        return jsonify({
            'status': 'success',
            'data': signals
        })
        
    except Exception as e:
        logger.error(f"Error getting trading signals: {str(e)}")
        return jsonify({'error': 'Failed to get trading signals'}), 500

@user_panel.route('/portfolio/summary', methods=['GET'])
def get_portfolio_summary():
    """Get user's portfolio summary"""
    try:
        user_id = request.user['uid']
        portfolio = trading_engine.get_portfolio_summary(user_id)
        
        return jsonify({
            'status': 'success',
            'data': portfolio
        })
        
    except Exception as e:
        logger.error(f"Error getting portfolio summary: {str(e)}")
        return jsonify({'error': 'Failed to get portfolio summary'}), 500

@user_panel.route('/trading/execute', methods=['POST'])
def execute_trade():
    """Execute a trade"""
    try:
        user_id = request.user['uid']
        data = request.get_json()
        
        # Validate request data
        required_fields = ['symbol', 'side', 'quantity']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
                
        # Check risk limits
        if not risk_manager.check_trade_limits(user_id, data):
            return jsonify({'error': 'Trade exceeds risk limits'}), 403
            
        # Execute trade
        trade_result = trading_engine.execute_trade(user_id, data)
        
        return jsonify({
            'status': 'success',
            'data': trade_result
        })
        
    except Exception as e:
        logger.error(f"Error executing trade: {str(e)}")
        return jsonify({'error': 'Failed to execute trade'}), 500

@user_panel.route('/market/data', methods=['GET'])
def get_market_data():
    """Get market data for a symbol"""
    try:
        symbol = request.args.get('symbol')
        timeframe = request.args.get('timeframe', '1d')
        
        if not symbol:
            return jsonify({'error': 'Symbol parameter is required'}), 400
            
        market_data = trading_engine.get_market_data(symbol, timeframe)
        
        return jsonify({
            'status': 'success',
            'data': market_data
        })
        
    except Exception as e:
        logger.error(f"Error getting market data: {str(e)}")
        return jsonify({'error': 'Failed to get market data'}), 500

@user_panel.route('/trading/positions', methods=['GET'])
def get_positions():
    """Get user's open positions"""
    try:
        user_id = request.user['uid']
        positions = trading_engine.get_positions(user_id)
        
        return jsonify({
            'status': 'success',
            'data': positions
        })
        
    except Exception as e:
        logger.error(f"Error getting positions: {str(e)}")
        return jsonify({'error': 'Failed to get positions'}), 500

@user_panel.route('/trading/orders', methods=['GET'])
def get_orders():
    """Get user's orders"""
    try:
        user_id = request.user['uid']
        status = request.args.get('status', 'all')
        
        orders = trading_engine.get_orders(user_id, status)
        
        return jsonify({
            'status': 'success',
            'data': orders
        })
        
    except Exception as e:
        logger.error(f"Error getting orders: {str(e)}")
        return jsonify({'error': 'Failed to get orders'}), 500
