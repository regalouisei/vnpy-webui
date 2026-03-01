# 持仓 API

from fastapi import APIRouter, HTTPException, status
from typing import List
import json

# 创建路由器
router = APIRouter(
    prefix="/positions",
    tags=["持仓"]
)

# TODO: 集成 VnPy 引擎
# from app.core.vnpy_engine import VnPyEngine
# vnpy_engine = VnPyEngine()

# 临时数据存储
positions_db = {}

@router.get("/")
async def get_all_positions():
    """获取所有持仓"""
    return {
        "positions": list(positions_db.values())
    }

@router.get("/{symbol}")
async def get_position(symbol: str):
    """获取持仓详情"""
    position = positions_db.get(symbol)
    if not position:
        raise HTTPException(
            status_code=404,
            detail=f"持仓 {symbol} 不存在"
        )
    return {
        "position": position
    }

@router.get("/{symbol}/pnl")
async def get_position_pnl(symbol: str):
    """获取持仓盈亏"""
    position = positions_db.get(symbol)
    if not position:
        raise HTTPException(
            status_code=404,
            detail=f"持仓 {symbol} 不存在"
        )
    
    # TODO: 计算实际盈亏
    return {
        "symbol": symbol,
        "unrealized_pnl": position.get("unrealized_pnl", 0),
        "realized_pnl": position.get("realized_pnl", 0),
        "total_pnl": position.get("unrealized_pnl", 0) + position.get("realized_pnl", 0)
    }

@router.post("/refresh")
async def refresh_position(symbol: str):
    """刷新持仓数据"""
    # TODO: 从 VnPy 引擎刷新持仓数据
    position = positions_db.get(symbol)
    if not position:
        raise HTTPException(
            status_code=404,
            detail=f"持仓 {symbol} 不存在"
        )
    
    # TODO: 实际刷新逻辑
    return {
        "message": f"持仓 {symbol} 数据已刷新",
        "position": position
    }
