# WebSocket 处理

from fastapi import WebSocket, WebSocketDisconnect
from typing import List
import asyncio
import json
from datetime import datetime

# 存储 WebSocket 连接
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """接受连接"""
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        """断开连接"""
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        """广播消息"""
        if self.active_connections:
            for connection in self.active_connections:
                try:
                    await connection.send_json(message)
                except:
                    self.active_connections.remove(connection)

manager = ConnectionManager()

async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 端点"""
    await manager.connect(websocket)
    
    try:
        while True:
            # 等待客户端消息
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # 处理消息
            if message["type"] == "subscribe_quote":
                # 订阅行情
                await handle_subscribe_quote(websocket, message)
            elif message["type"] == "unsubscribe_quote":
                # 取消订阅行情
                await handle_unsubscribe_quote(websocket, message)
            else:
                # 未知消息类型
                await websocket.send_json({
                    "type": "error",
                    "message": f"未知消息类型: {message['type']}"
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket 错误: {e}")
        manager.disconnect(websocket)

async def handle_subscribe_quote(websocket: WebSocket, message: dict):
    """处理行情订阅"""
    symbol = message.get("symbol")
    exchange = message.get("exchange")
    
    # TODO: 实现订阅逻辑
    await websocket.send_json({
        "type": "quote_subscribed",
        "symbol": symbol,
        "exchange": exchange,
        "message": f"已订阅 {symbol} 行情"
    })

async def handle_unsubscribe_quote(websocket: WebSocket, message: dict):
    """处理取消订阅"""
    symbol = message.get("symbol")
    exchange = message.get("exchange")
    
    # TODO: 实现取消订阅逻辑
    await websocket.send_json({
        "type": "quote_unsubscribed",
        "symbol": symbol,
        "exchange": exchange,
        "message": f"已取消订阅 {symbol} 行情"
    })

async def broadcast_tick(tick: dict):
    """广播 Tick 数据"""
    message = {
        "type": "tick",
        "data": tick,
        "timestamp": datetime.now().isoformat()
    }
    await manager.broadcast(message)

async def broadcast_trade(trade: dict):
    """广播成交数据"""
    message = {
        "type": "trade",
        "data": trade,
        "timestamp": datetime.now().isoformat()
    }
    await manager.broadcast(message)

async def broadcast_position(position: dict):
    """广播持仓数据"""
    message = {
        "type": "position",
        "data": position,
        "timestamp": datetime.now().isoformat()
    }
    await manager.broadcast(message)

async def broadcast_account(account: dict):
    """广播账户数据"""
    message = {
        "type": "account",
        "data": account,
        "timestamp": datetime.now().isoformat()
    }
    await manager.broadcast(message)
