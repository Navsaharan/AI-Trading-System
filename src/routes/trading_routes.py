from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from typing import List, Optional
from datetime import datetime, timedelta
import asyncio
import json

from ..models.trading_models import (
    Order, OrderType, OrderSide, PriceType,
    Position, Trade, Stock, MarketDepth,
    WatchlistItem, GTTOrder
)
from ..services.trading_service import TradingService
from ..services.stock_service import StockService
from ..services.analysis_service import AnalysisService
from ..auth.auth_service import get_current_user
from ..websocket.connection_manager import ConnectionManager

router = APIRouter(prefix="/api")
manager = ConnectionManager()

@router.get("/stocks/search")
async def search_stocks(
    q: str,
    service: StockService = Depends(StockService),
    current_user = Depends(get_current_user)
):
    """Search for stocks based on name or symbol"""
    return await service.search_stocks(q)

@router.get("/stocks/{symbol}/info")
async def get_stock_info(
    symbol: str,
    service: StockService = Depends(StockService),
    current_user = Depends(get_current_user)
):
    """Get detailed information about a stock"""
    return await service.get_stock_info(symbol)

@router.get("/stocks/{symbol}/ohlc")
async def get_stock_ohlc(
    symbol: str,
    timeframe: str = "1D",
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    service: StockService = Depends(StockService),
    current_user = Depends(get_current_user)
):
    """Get OHLC data for a stock"""
    if not from_date:
        if timeframe == "1D":
            from_date = datetime.now() - timedelta(days=1)
        elif timeframe == "1W":
            from_date = datetime.now() - timedelta(weeks=1)
        elif timeframe == "1M":
            from_date = datetime.now() - timedelta(days=30)
        elif timeframe == "1Y":
            from_date = datetime.now() - timedelta(days=365)
        else:
            from_date = datetime.now() - timedelta(days=365*5)

    return await service.get_ohlc_data(symbol, timeframe, from_date, to_date)

@router.get("/stocks/{symbol}/depth")
async def get_market_depth(
    symbol: str,
    service: StockService = Depends(StockService),
    current_user = Depends(get_current_user)
):
    """Get market depth for a stock"""
    return await service.get_market_depth(symbol)

@router.get("/watchlist")
async def get_watchlist(
    service: TradingService = Depends(TradingService),
    current_user = Depends(get_current_user)
):
    """Get user's watchlist"""
    return await service.get_watchlist(current_user.id)

@router.post("/watchlist/{symbol}")
async def add_to_watchlist(
    symbol: str,
    service: TradingService = Depends(TradingService),
    current_user = Depends(get_current_user)
):
    """Add a stock to watchlist"""
    return await service.add_to_watchlist(current_user.id, symbol)

@router.delete("/watchlist/{symbol}")
async def remove_from_watchlist(
    symbol: str,
    service: TradingService = Depends(TradingService),
    current_user = Depends(get_current_user)
):
    """Remove a stock from watchlist"""
    return await service.remove_from_watchlist(current_user.id, symbol)

@router.get("/orders")
async def get_orders(
    service: TradingService = Depends(TradingService),
    current_user = Depends(get_current_user)
):
    """Get user's orders"""
    return await service.get_orders(current_user.id)

@router.post("/orders")
async def place_order(
    order: Order,
    service: TradingService = Depends(TradingService),
    current_user = Depends(get_current_user)
):
    """Place a new order"""
    return await service.place_order(current_user.id, order)

@router.put("/orders/{order_id}")
async def modify_order(
    order_id: str,
    order: Order,
    service: TradingService = Depends(TradingService),
    current_user = Depends(get_current_user)
):
    """Modify an existing order"""
    return await service.modify_order(current_user.id, order_id, order)

@router.delete("/orders/{order_id}")
async def cancel_order(
    order_id: str,
    service: TradingService = Depends(TradingService),
    current_user = Depends(get_current_user)
):
    """Cancel an order"""
    return await service.cancel_order(current_user.id, order_id)

@router.get("/positions")
async def get_positions(
    service: TradingService = Depends(TradingService),
    current_user = Depends(get_current_user)
):
    """Get user's positions"""
    return await service.get_positions(current_user.id)

@router.post("/positions/{position_id}/exit")
async def exit_position(
    position_id: str,
    service: TradingService = Depends(TradingService),
    current_user = Depends(get_current_user)
):
    """Exit a position"""
    return await service.exit_position(current_user.id, position_id)

@router.get("/gtt")
async def get_gtt_orders(
    service: TradingService = Depends(TradingService),
    current_user = Depends(get_current_user)
):
    """Get user's GTT orders"""
    return await service.get_gtt_orders(current_user.id)

@router.post("/gtt")
async def place_gtt_order(
    order: GTTOrder,
    service: TradingService = Depends(TradingService),
    current_user = Depends(get_current_user)
):
    """Place a new GTT order"""
    return await service.place_gtt_order(current_user.id, order)

@router.delete("/gtt/{order_id}")
async def cancel_gtt_order(
    order_id: str,
    service: TradingService = Depends(TradingService),
    current_user = Depends(get_current_user)
):
    """Cancel a GTT order"""
    return await service.cancel_gtt_order(current_user.id, order_id)

@router.websocket("/ws/trading")
async def trading_websocket(
    websocket: WebSocket,
    token: str,
    service: TradingService = Depends(TradingService)
):
    """WebSocket endpoint for real-time trading updates"""
    try:
        # Authenticate user
        current_user = await get_current_user(token)
        await manager.connect(websocket, current_user.id)
        
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                if message["type"] == "subscribe":
                    symbols = message["symbols"]
                    await service.subscribe_market_data(current_user.id, symbols)
                elif message["type"] == "unsubscribe":
                    symbols = message["symbols"]
                    await service.unsubscribe_market_data(current_user.id, symbols)
                
        except WebSocketDisconnect:
            await manager.disconnect(websocket, current_user.id)
            await service.unsubscribe_all(current_user.id)
            
    except Exception as e:
        await websocket.close(code=1008, reason=str(e))

# Background task to send market data updates
async def send_market_updates():
    while True:
        try:
            updates = await TradingService.get_market_updates()
            for user_id, update in updates:
                await manager.send_personal_message(
                    json.dumps(update),
                    user_id
                )
        except Exception as e:
            print(f"Error sending market updates: {e}")
        await asyncio.sleep(1)  # Send updates every second

# Start the background task
@router.on_event("startup")
async def startup_event():
    asyncio.create_task(send_market_updates())
