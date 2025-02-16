from flask import render_template, send_from_directory, jsonify, request
from functools import wraps
import jwt
import os

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            token = token.split(' ')[1]  # Remove 'Bearer ' prefix
            data = jwt.decode(token, os.getenv('JWT_SECRET_KEY'), algorithms=['HS256'])
            current_user = data['user_id']
        except:
            return jsonify({'message': 'Token is invalid'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

def init_routes(app):
    # Serve static files
    @app.route('/static/<path:path>')
    def send_static(path):
        return send_from_directory('frontend/static', path)

    # Main routes
    @app.route('/')
    def index():
        return render_template('user/user_dashboard.html')

    @app.route('/admin')
    @token_required
    def admin_dashboard(current_user):
        # Check if user is admin
        if not is_admin(current_user):
            return jsonify({'message': 'Unauthorized'}), 403
        return render_template('admin/dashboard.html')

    # API Routes
    @app.route('/api/market-data')
    @token_required
    def get_market_data(current_user):
        return jsonify({
            'nifty': {
                'last_price': 19750.25,
                'change': 125.50,
                'change_percent': 0.64
            },
            'banknifty': {
                'last_price': 44320.15,
                'change': 280.75,
                'change_percent': 0.63
            }
        })

    @app.route('/api/portfolio')
    @token_required
    def get_portfolio(current_user):
        return jsonify({
            'total_value': 523450,
            'pnl': 12350,
            'available_margin': 150000,
            'positions': [
                {
                    'symbol': 'RELIANCE',
                    'quantity': 100,
                    'average_price': 2450.75,
                    'ltp': 2480.50,
                    'pnl': 2975
                }
            ]
        })

    @app.route('/api/orders')
    @token_required
    def get_orders(current_user):
        return jsonify([
            {
                'time': '2025-02-16T10:30:00',
                'symbol': 'RELIANCE',
                'type': 'BUY',
                'quantity': 100,
                'price': 2450.75,
                'status': 'COMPLETE'
            }
        ])

    # Admin API Routes
    @app.route('/api/admin/stats')
    @token_required
    def get_admin_stats(current_user):
        if not is_admin(current_user):
            return jsonify({'message': 'Unauthorized'}), 403
            
        return jsonify({
            'users': {
                'total': 1250,
                'growth': 12.5,
                'chart_data': [1150, 1180, 1200, 1220, 1240, 1250]
            },
            'trades': {
                'total': 856,
                'change': -3.2,
                'chart_data': [900, 880, 870, 865, 860, 856]
            },
            'revenue': {
                'total': 15200000,
                'growth': 8.1,
                'chart_data': [14000000, 14300000, 14600000, 14800000, 15000000, 15200000]
            },
            'system': {
                'cpu': 28,
                'memory': 64
            }
        })

    @app.route('/api/admin/recent-trades')
    @token_required
    def get_recent_trades(current_user):
        if not is_admin(current_user):
            return jsonify({'message': 'Unauthorized'}), 403
            
        return jsonify({
            'data': [
                {
                    'user': 'john.doe@example.com',
                    'symbol': 'RELIANCE',
                    'type': 'BUY',
                    'amount': 245075,
                    'status': 'COMPLETE'
                },
                {
                    'user': 'jane.smith@example.com',
                    'symbol': 'INFY',
                    'type': 'SELL',
                    'amount': 156800,
                    'status': 'PENDING'
                }
            ]
        })

def is_admin(user_id):
    # TODO: Implement actual admin check from database
    return True  # Temporary for testing
