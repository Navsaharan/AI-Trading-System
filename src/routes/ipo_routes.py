from flask import Blueprint, jsonify, request
from ..services.ipo_service import IPOService
from ..data.market_data import MarketDataProvider
from ..database import get_db
from ..auth.decorators import login_required

ipo = Blueprint('ipo', __name__, url_prefix='/api/ipo')
market_data = MarketDataProvider()

@ipo.route('/upcoming', methods=['GET'])
@login_required
async def get_upcoming_ipos():
    """Get list of upcoming IPOs"""
    db = get_db()
    ipo_service = IPOService(db, market_data)
    ipos = await ipo_service.get_upcoming_ipos()
    return jsonify(ipos)

@ipo.route('/ongoing', methods=['GET'])
@login_required
async def get_ongoing_ipos():
    """Get list of ongoing IPOs with live subscription data"""
    db = get_db()
    ipo_service = IPOService(db, market_data)
    ipos = await ipo_service.get_ongoing_ipos()
    return jsonify(ipos)

@ipo.route('/<int:ipo_id>', methods=['GET'])
@login_required
async def get_ipo_details(ipo_id: int):
    """Get detailed information about an IPO"""
    db = get_db()
    ipo_service = IPOService(db, market_data)
    try:
        details = await ipo_service.get_ipo_details(ipo_id)
        return jsonify(details)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404

@ipo.route('/<int:ipo_id>/analysis', methods=['GET'])
@login_required
async def get_ipo_analysis(ipo_id: int):
    """Get AI analysis of an IPO"""
    db = get_db()
    ipo_service = IPOService(db, market_data)
    try:
        analysis = await ipo_service.analyze_ipo(ipo_id)
        return jsonify(analysis)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
