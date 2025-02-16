from flask_socketio import SocketIO, emit, join_room, leave_room
import json
from functools import wraps
import jwt
import os

socketio = SocketIO()

def ws_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = args[0].get('token')
        if not token:
            emit('error', {'message': 'Token is missing'})
            return
        
        try:
            data = jwt.decode(token, os.getenv('JWT_SECRET_KEY'), algorithms=['HS256'])
            current_user = data['user_id']
        except:
            emit('error', {'message': 'Token is invalid'})
            return
        
        return f(current_user, *args, **kwargs)
    return decorated

def init_websocket(app):
    socketio.init_app(app, cors_allowed_origins="*")
    
    @socketio.on('connect')
    def handle_connect():
        emit('connected', {'status': 'connected'})

    @socketio.on('join')
    @ws_token_required
    def handle_join(current_user, data):
        room = data.get('room')
        if room:
            join_room(room)
            emit('joined', {'room': room}, room=room)

    @socketio.on('leave')
    @ws_token_required
    def handle_leave(current_user, data):
        room = data.get('room')
        if room:
            leave_room(room)
            emit('left', {'room': room}, room=room)

    @socketio.on('market_data_request')
    @ws_token_required
    def handle_market_data_request(current_user, data):
        # Here you would fetch real market data
        market_data = {
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
        }
        emit('market_data', market_data)

    @socketio.on('portfolio_request')
    @ws_token_required
    def handle_portfolio_request(current_user, data):
        # Here you would fetch real portfolio data
        portfolio_data = {
            'total_value': 523450,
            'pnl': 12350,
            'available_margin': 150000
        }
        emit('portfolio_update', portfolio_data)

    @socketio.on('admin_stats_request')
    @ws_token_required
    def handle_admin_stats_request(current_user, data):
        # Here you would fetch real admin stats
        admin_stats = {
            'users': {
                'total': 1250,
                'growth': 12.5
            },
            'trades': {
                'total': 856,
                'change': -3.2
            },
            'revenue': {
                'total': 15200000,
                'growth': 8.1
            }
        }
        emit('admin_stats', admin_stats)

    return socketio
