# 行情 API

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import json
import asyncio

# 创建路由器
router = APIRouter(
    prefix="/quotes",
    tags=["行情"]
)

# TODO: 集成 VnPy 引擎
# from app.core.vnpy_engine import VnPyEngine
# vnpy_engine = VnPyEngine()

# WebSocket 连接管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

manager = ConnectionManager()

@router.get("/")
async def get_all_quotes():
    """获取所有订阅的行情"""
    # TODO: 从 VnPy 引擎获取订阅的行情
    return {
        "quotes": []
    }

@router.get("/{symbol}")
async def get_quote(symbol: str):
    """获取指定合约的行情"""
    # TODO: 从 VnPy 引擎获取最新行情
    return {
        "symbol": symbol,
        "last_price": None,
        "bid_price": None,
        "ask_price": None,
        "volume": None
    }

@router.post("/subscribe")
async def subscribe_quote(request: dict):
    """订阅行情"""
    symbol = request.get("symbol")
    exchange = request.get("exchange")

    # TODO: 实现订阅逻辑
    # vnpy_engine.subscribe(symbol, exchange)

    return {
        "message": f"已订阅 {symbol} 行情",
        "symbol": symbol,
        "exchange": exchange
    }

@router.post("/unsubscribe")
async def unsubscribe_quote(request: dict):
    """取消订阅行情"""
    symbol = request.get("symbol")

    # TODO: 实现取消订阅逻辑
    # vnpy_engine.unsubscribe(symbol)

    return {
        "message": f"已取消订阅 {symbol} 行情",
        "symbol": symbol
    }

@router.websocket("/stream")
async def quote_stream(websocket: WebSocket):
    """实时行情流"""
    await manager.connect(websocket)

    try:
        while True:
            # TODO: 获取最新行情数据
            # ticks = vnpy_engine.get_latest_ticks()
            ticks = []

            if ticks:
                await websocket.send_json({
                    "type": "quotes",
                    "data": ticks,
                    "timestamp": asyncio.get_event_loop().time()
                })

            await asyncio.sleep(1)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket 错误: {e}")
        manager.disconnect(websocket)
