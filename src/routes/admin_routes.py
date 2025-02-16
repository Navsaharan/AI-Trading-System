from flask import Blueprint, render_template, jsonify, request
from functools import wraps
from firebase_admin import auth
from ..admin.charge_manager import ChargeManager
from ..admin.trading_rules import TradingManager
from flask import Blueprint, jsonify, request
from ..trading.platform_manager import platform_manager, PlatformType, BrokerType
from ..admin.fund_manager import FundManager
from ..models import FundAllocation, TradeHistory
from ..database import get_db
import os
from ..code_editor import CodeEditor

admin = Blueprint('admin', __name__, url_prefix='/admin')
charge_manager = ChargeManager()
trading_manager = TradingManager(charge_manager)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('token')
        try:
            decoded_token = auth.verify_id_token(token)
            user_claims = decoded_token.get('admin', False)
            if not user_claims:
                return jsonify({'error': 'Admin access required'}), 403
        except:
            return jsonify({'error': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Admin Dashboard Routes
@admin.route('/')
@admin_required
def dashboard():
    """Admin main dashboard"""
    return render_template('admin/dashboard.html')

@admin.route('/charges')
@admin_required
def charges():
    """Charge management page"""
    return render_template('admin/charges.html')

@admin.route('/trading-rules')
@admin_required
def trading_rules():
    """Trading rules configuration"""
    return render_template('admin/trading_rules.html')

@admin.route('/users')
@admin_required
def users():
    """User management"""
    return render_template('admin/users.html')

@admin.route('/reports')
@admin_required
def reports():
    """Admin reports"""
    return render_template('admin/reports.html')

@admin.route('/ai-settings')
@admin_required
def ai_settings():
    """AI configuration"""
    return render_template('admin/ai_settings.html')

# API Routes for Admin
@admin.route('/api/charges', methods=['GET', 'POST'])
@admin_required
def manage_charges():
    if request.method == 'POST':
        data = request.json
        charge_manager.update_charge_rate(data['charge_type'], data['rate'])
        return jsonify({'success': True})
    return jsonify(charge_manager.get_charge_summary())

@admin.route('/api/trading-rules', methods=['GET', 'POST'])
@admin_required
def manage_trading_rules():
    if request.method == 'POST':
        data = request.json
        trading_manager.update_rule(data['rule_name'], data['value'])
        return jsonify({'success': True})
    return jsonify(trading_manager.get_trading_summary())

# API Routes for Admin Platform Management
@admin.route('/api/admin/platforms', methods=['GET'])
async def get_platforms():
    """Get status of all trading platforms"""
    platforms = await platform_manager.get_platform_status()
    return jsonify(platforms)

@admin.route('/api/admin/platforms/add', methods=['POST'])
async def add_platform():
    """Add new trading platform"""
    data = request.json
    success = await platform_manager.add_platform(
        name=data['name'],
        platform_type=PlatformType(data['platform_type']),
        broker_type=BrokerType(data['broker_type']),
        credentials=data.get('credentials')
    )
    return jsonify({'success': success})

@admin.route('/api/admin/platforms/activate', methods=['POST'])
async def activate_platform():
    """Activate a trading platform"""
    data = request.json
    success = await platform_manager.activate_platform(data['name'])
    return jsonify({'success': success})

@admin.route('/api/admin/platforms/active', methods=['GET'])
async def get_active_platforms():
    """Get currently active platforms"""
    active = await platform_manager.get_active_platforms()
    return jsonify({k.value: v for k, v in active.items()})

# Code Editor Routes
@admin.route('/code-editor/files', methods=['GET'])
@admin_required
def list_editable_files():
    """List all editable files"""
    editor = CodeEditor(current_app.config['REPO_PATH'])
    files = []
    for root, _, filenames in os.walk(current_app.config['REPO_PATH']):
        for filename in filenames:
            if filename.endswith(('.py', '.js', '.html', '.css', '.json')):
                rel_path = os.path.relpath(
                    os.path.join(root, filename),
                    current_app.config['REPO_PATH']
                )
                files.append({
                    'path': rel_path,
                    'type': editor._get_file_type(rel_path)
                })
    return jsonify(files)

@admin.route('/code-editor/file', methods=['GET'])
@admin_required
def get_file_content():
    """Get file content"""
    file_path = request.args.get('path')
    if not file_path:
        return jsonify({'error': 'File path required'}), 400
        
    editor = CodeEditor(current_app.config['REPO_PATH'])
    try:
        content = editor.get_file_content(file_path)
        return jsonify(content)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404

@admin.route('/code-editor/file', methods=['POST'])
@admin_required
def update_file_content():
    """Update file content"""
    data = request.get_json()
    if not all(k in data for k in ['path', 'content', 'message']):
        return jsonify({'error': 'Missing required fields'}), 400
        
    editor = CodeEditor(current_app.config['REPO_PATH'])
    try:
        result = editor.update_file(
            data['path'],
            data['content'],
            request.user['name'],
            data['message']
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin.route('/code-editor/preview', methods=['POST'])
@admin_required
def preview_file_changes():
    """Preview file changes"""
    data = request.get_json()
    if not all(k in data for k in ['path', 'content']):
        return jsonify({'error': 'Missing required fields'}), 400
        
    editor = CodeEditor(current_app.config['REPO_PATH'])
    result = editor.preview_changes(data['path'], data['content'])
    return jsonify(result)

@admin.route('/code-editor/history', methods=['GET'])
@admin_required
def get_file_history():
    """Get file version history"""
    file_path = request.args.get('path')
    if not file_path:
        return jsonify({'error': 'File path required'}), 400
        
    editor = CodeEditor(current_app.config['REPO_PATH'])
    history = editor.get_file_history(file_path)
    return jsonify(history)

@admin.route('/code-editor/rollback', methods=['POST'])
@admin_required
def rollback_file():
    """Rollback file to previous version"""
    data = request.get_json()
    if not all(k in data for k in ['path', 'commit_hash']):
        return jsonify({'error': 'Missing required fields'}), 400
        
    editor = CodeEditor(current_app.config['REPO_PATH'])
    result = editor.rollback_changes(data['path'], data['commit_hash'])
    return jsonify(result)

# Fund Allocation Routes
@admin.route('/fund-allocations', methods=['GET'])
@admin_required
def list_fund_allocations():
    """List all fund allocations"""
    db = get_db()
    fund_manager = FundManager(db)
    allocations = db.query(FundAllocation).all()
    return jsonify([{
        'id': a.id,
        'user_id': a.user_id,
        'total_amount': a.total_amount,
        'risk_mode': a.risk_mode,
        'performance': fund_manager.get_performance_metrics(a.id)
    } for a in allocations])

@admin.route('/fund-allocations/<int:allocation_id>', methods=['GET'])
@admin_required
def get_fund_allocation(allocation_id):
    """Get specific fund allocation details"""
    db = get_db()
    fund_manager = FundManager(db)
    allocation = db.query(FundAllocation).filter(FundAllocation.id == allocation_id).first()
    if not allocation:
        return jsonify({'error': 'Allocation not found'}), 404
        
    return jsonify({
        'allocation': {
            'id': allocation.id,
            'user_id': allocation.user_id,
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
        'risk_management': fund_manager.check_risk_management(allocation.id)
    })

@admin.route('/fund-allocations/<int:allocation_id>', methods=['PUT'])
@admin_required
def update_fund_allocation(allocation_id):
    """Update fund allocation settings"""
    db = get_db()
    fund_manager = FundManager(db)
    data = request.get_json()
    
    try:
        allocation = fund_manager.update_allocation(allocation_id, data)
        return jsonify({
            'message': 'Allocation updated successfully',
            'allocation': {
                'id': allocation.id,
                'total_amount': allocation.total_amount,
                'risk_mode': allocation.risk_mode
            }
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@admin.route('/fund-allocations/<int:allocation_id>/trades', methods=['GET'])
@admin_required
def get_allocation_trades(allocation_id):
    """Get trade history for specific allocation"""
    db = get_db()
    trades = db.query(TradeHistory).filter(TradeHistory.fund_allocation_id == allocation_id).all()
    return jsonify([{
        'id': t.id,
        'category': t.category,
        'amount': t.trade_amount,
        'type': t.trade_type,
        'profit_loss': t.profit_loss,
        'timestamp': t.timestamp.isoformat()
    } for t in trades])
