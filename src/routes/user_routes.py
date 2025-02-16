from flask import Blueprint, render_template, jsonify, request
from functools import wraps
from firebase_admin import auth
from ..trading.portfolio_manager import PortfolioManager
from ..trading.order_manager import OrderManager
from ..trading.fund_manager import FundManager
from ..database import get_db

user = Blueprint('user', __name__)
portfolio_manager = PortfolioManager()
order_manager = OrderManager()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('token')
        try:
            decoded_token = auth.verify_id_token(token)
            request.user = decoded_token
        except:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

# User Pages
@user.route('/')
@login_required
def dashboard():
    """User trading dashboard"""
    return render_template('user/dashboard.html')

@user.route('/portfolio')
@login_required
def portfolio():
    """Portfolio overview"""
    return render_template('user/portfolio.html')

@user.route('/orders')
@login_required
def orders():
    """Order history and active orders"""
    return render_template('user/orders.html')

@user.route('/watchlist')
@login_required
def watchlist():
    """User's watchlist"""
    return render_template('user/watchlist.html')

@user.route('/reports')
@login_required
def reports():
    """User reports and analytics"""
    return render_template('user/reports.html')

@user.route('/settings')
@login_required
def settings():
    """User settings"""
    return render_template('user/settings.html')

@user.route('/alerts')
@login_required
def alerts():
    """Price alerts and notifications"""
    return render_template('user/alerts.html')

# API Routes for Users
@user.route('/api/portfolio')
@login_required
def get_portfolio():
    """Get user's portfolio data"""
    return jsonify(portfolio_manager.get_portfolio(request.user['uid']))

@user.route('/api/orders')
@login_required
def get_orders():
    """Get user's orders"""
    return jsonify(order_manager.get_orders(request.user['uid']))

@user.route('/api/place-order', methods=['POST'])
@login_required
def place_order():
    """Place a new order"""
    data = request.json
    return jsonify(order_manager.place_order(request.user['uid'], data))

@user.route('/api/watchlist', methods=['GET', 'POST', 'DELETE'])
@login_required
def manage_watchlist():
    """Manage user's watchlist"""
    if request.method == 'POST':
        data = request.json
        return jsonify(portfolio_manager.add_to_watchlist(request.user['uid'], data['symbol']))
    elif request.method == 'DELETE':
        data = request.json
        return jsonify(portfolio_manager.remove_from_watchlist(request.user['uid'], data['symbol']))
    return jsonify(portfolio_manager.get_watchlist(request.user['uid']))

@user.route('/api/alerts', methods=['GET', 'POST', 'DELETE'])
@login_required
def manage_alerts():
    """Manage price alerts"""
    if request.method == 'POST':
        data = request.json
        return jsonify(portfolio_manager.create_alert(request.user['uid'], data))
    elif request.method == 'DELETE':
        data = request.json
        return jsonify(portfolio_manager.delete_alert(request.user['uid'], data['alert_id']))
    return jsonify(portfolio_manager.get_alerts(request.user['uid']))

# Fund Allocation Routes
@user.route('/fund-allocation', methods=['GET'])
@login_required
def get_user_allocation():
    """Get user's fund allocation"""
    db = get_db()
    fund_manager = FundManager(db)
    allocation = fund_manager.get_allocation(request.user['uid'])
    
    if not allocation:
        return jsonify({'error': 'No allocation found'}), 404
        
    return jsonify({
        'allocation': {
            'total_amount': allocation.total_amount,
            'stocks_allocation': allocation.stocks_allocation,
            'fo_allocation': allocation.fo_allocation,
            'crypto_allocation': allocation.crypto_allocation,
            'forex_allocation': allocation.forex_allocation,
            'commodities_allocation': allocation.commodities_allocation,
            'risk_mode': allocation.risk_mode,
            'max_trade_size': allocation.max_trade_size,
            'max_daily_trades': allocation.max_daily_trades
        },
        'performance': fund_manager.get_performance_metrics(allocation.id),
        'risk_status': fund_manager.check_risk_management(allocation.id)
    })

@user.route('/fund-allocation', methods=['POST'])
@login_required
def create_fund_allocation():
    """Create new fund allocation"""
    db = get_db()
    fund_manager = FundManager(db)
    data = request.get_json()
    
    # Validate total allocations
    total_allocated = sum([
        data.get('stocks_allocation', 0),
        data.get('fo_allocation', 0),
        data.get('crypto_allocation', 0),
        data.get('forex_allocation', 0),
        data.get('commodities_allocation', 0)
    ])
    
    if total_allocated > data['total_amount']:
        return jsonify({'error': 'Total allocations exceed total amount'}), 400
        
    try:
        allocation = fund_manager.create_allocation(request.user['uid'], data)
        return jsonify({
            'message': 'Allocation created successfully',
            'allocation': {
                'id': allocation.id,
                'total_amount': allocation.total_amount,
                'risk_mode': allocation.risk_mode
            }
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@user.route('/fund-allocation/trades', methods=['GET'])
@login_required
def get_user_trades():
    """Get user's trade history"""
    db = get_db()
    allocation = db.query(FundAllocation).filter(FundAllocation.user_id == request.user['uid']).first()
    if not allocation:
        return jsonify({'error': 'No allocation found'}), 404
        
    trades = db.query(TradeHistory).filter(TradeHistory.fund_allocation_id == allocation.id).all()
    return jsonify([{
        'category': t.category,
        'amount': t.trade_amount,
        'type': t.trade_type,
        'profit_loss': t.profit_loss,
        'timestamp': t.timestamp.isoformat()
    } for t in trades])

@user.route('/fund-allocation/performance', methods=['GET'])
@login_required
def get_performance():
    """Get user's trading performance"""
    db = get_db()
    fund_manager = FundManager(db)
    allocation = db.query(FundAllocation).filter(FundAllocation.user_id == request.user['uid']).first()
    
    if not allocation:
        return jsonify({'error': 'No allocation found'}), 404
        
    metrics = fund_manager.get_performance_metrics(allocation.id)
    risk_status = fund_manager.check_risk_management(allocation.id)
    
    return jsonify({
        'performance': metrics,
        'risk_management': risk_status
    })

@user.route('/fund-allocation/risk-modes', methods=['GET'])
@login_required
def get_risk_modes():
    """Get risk mode configurations"""
    db = get_db()
    fund_manager = FundManager(db)
    allocation = db.query(FundAllocation).filter(FundAllocation.user_id == request.user['uid']).first()
    
    if not allocation:
        return jsonify({'error': 'No allocation found'}), 404
        
    configs = fund_manager.get_risk_mode_configs(allocation.id)
    return jsonify([{
        'id': c.id,
        'risk_level': c.risk_level,
        'allocated_amount': c.allocated_amount,
        'max_trade_size': c.max_trade_size,
        'max_daily_trades': c.max_daily_trades,
        'stop_loss_percentage': c.stop_loss_percentage,
        'description': fund_manager.get_risk_mode_description(c.risk_level)
    } for c in configs])

@user.route('/fund-allocation/risk-modes', methods=['POST'])
@login_required
def create_risk_mode():
    """Create new risk mode configuration"""
    db = get_db()
    fund_manager = FundManager(db)
    allocation = db.query(FundAllocation).filter(FundAllocation.user_id == request.user['uid']).first()
    
    if not allocation:
        return jsonify({'error': 'No allocation found'}), 404
        
    data = request.get_json()
    
    # Validate total risk allocations
    existing_configs = fund_manager.get_risk_mode_configs(allocation.id)
    total_allocated = sum(c.allocated_amount for c in existing_configs)
    if total_allocated + data['allocated_amount'] > allocation.total_amount:
        return jsonify({'error': 'Total risk allocations exceed total amount'}), 400
        
    try:
        config = fund_manager.create_risk_mode_config(allocation.id, data)
        return jsonify({
            'message': 'Risk mode configuration created',
            'config': {
                'id': config.id,
                'risk_level': config.risk_level,
                'allocated_amount': config.allocated_amount
            }
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@user.route('/fund-allocation/risk-modes/<int:config_id>', methods=['PUT'])
@login_required
def update_risk_mode(config_id):
    """Update risk mode configuration"""
    db = get_db()
    fund_manager = FundManager(db)
    data = request.get_json()
    
    try:
        config = fund_manager.update_risk_mode_config(config_id, data)
        return jsonify({
            'message': 'Risk mode configuration updated',
            'config': {
                'id': config.id,
                'risk_level': config.risk_level,
                'allocated_amount': config.allocated_amount
            }
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@user.route('/fund-allocation/auto-adjust', methods=['POST'])
@login_required
def toggle_auto_adjust():
    """Toggle auto-adjust feature"""
    db = get_db()
    allocation = db.query(FundAllocation).filter(FundAllocation.user_id == request.user['uid']).first()
    
    if not allocation:
        return jsonify({'error': 'No allocation found'}), 404
        
    data = request.get_json()
    allocation.auto_adjust_enabled = data.get('enabled', False)
    db.commit()
    
    if allocation.auto_adjust_enabled:
        fund_manager = FundManager(db)
        adjustments = fund_manager.auto_adjust_risk_levels(allocation.id)
        return jsonify({
            'message': 'Auto-adjust enabled and initial adjustments made',
            'adjustments': adjustments
        })
    
    return jsonify({'message': 'Auto-adjust disabled'})
