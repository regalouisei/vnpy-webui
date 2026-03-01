# 交易 API

from fastapi import APIRouter, HTTPException, status
from typing import List

# 创建路由器
router = APIRouter(
    prefix="/trade",
    tags=["交易"]
)

# TODO: 集成 VnPy 引擎
# from app.core.vnpy_engine import VnPyEngine

# 临时数据存储
orders_db = {}
trades_db = {}

@router.get("/orders")
async def get_all_orders():
    """获取所有订单"""
    return {
        "orders": list(orders_db.values())
    }

@router.get("/orders/{orderid}")
async def get_order(orderid: str):
    """获取订单详情"""
    order = orders_db.get(orderid)
    if not order:
        raise HTTPException(
            status_code=404,
            detail=f"订单 {orderid} 不存在"
        )
    return {
        "order": order
    }

@router.post("/orders")
async def create_order(request: dict):
    """下单"""
    symbol = request.get("symbol")
    direction = request.get("direction")
    offset = request.get("offset")
    volume = request.get("volume")
    price = request.get("price")
    order_type = request.get("order_type", "limit")

    # TODO: 从 VnPy 引擎下单
    orderid = f"order_{len(orders_db) + 1}"

    order = {
        "id": orderid,
        "symbol": symbol,
        "direction": direction,
        "offset": offset,
        "volume": volume,
        "price": price,
        "order_type": order_type,
        "status": "submitted",
        "created_at": "2026-02-20T00:00:00Z"
    }

    orders_db[orderid] = order

    return {
        "message": "订单已提交",
        "order": order
    }

@router.delete("/orders/{orderid}")
async def cancel_order(orderid: str):
    """撤单"""
    order = orders_db.get(orderid)
    if not order:
        raise HTTPException(
            status_code=404,
            detail=f"订单 {orderid} 不存在"
        )

    # TODO: 从 VnPy 引擎撤单
    order["status"] = "cancelled"
    order["cancelled_at"] = "2026-02-20T00:00:00Z"

    orders_db[orderid] = order

    return {
        "message": f"订单 {orderid} 已撤消",
        "order": order
    }

@router.get("/trades")
async def get_all_trades():
    """获取所有成交"""
    return {
        "trades": list(trades_db.values())
    }

@router.get("/trades/{tradeid}")
async def get_trade(tradeid: str):
    """获取成交详情"""
    trade = trades_db.get(tradeid)
    if not trade:
        raise HTTPException(
            status_code=404,
            detail=f"成交 {tradeid} 不存在"
        )
    return {
        "trade": trade
    }
