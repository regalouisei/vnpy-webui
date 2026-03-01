# 合约 API

from fastapi import APIRouter, HTTPException, status
from typing import List

# 创建路由器
router = APIRouter(
    prefix="/contracts",
    tags=["合约"]
)

# TODO: 集成 VnPy 引擎
# from app.core.vnpy_engine import VnPyEngine
# vnpy_engine = VnPyEngine()

# 临时数据存储
contracts_db = {}

@router.get("/")
async def get_all_contracts():
    """获取所有合约"""
    # TODO: 从 VnPy 引擎获取合约数据
    return {
        "contracts": list(contracts_db.values())
    }

@router.get("/{symbol}")
async def get_contract(symbol: str):
    """获取合约详情"""
    # TODO: 从 VnPy 引擎获取合约详情
    contract = contracts_db.get(symbol)
    if not contract:
        raise HTTPException(
            status_code=404,
            detail=f"合约 {symbol} 不存在"
        )
    return {
        "contract": contract
    }

@router.get("/{symbol}/tick")
async def get_contract_tick(symbol: str):
    """获取合约最新 tick"""
    # TODO: 从 VnPy 引擎获取最新 tick
    contract = contracts_db.get(symbol)
    if not contract:
        raise HTTPException(
            status_code=404,
            detail=f"合约 {symbol} 不存在"
        )
    # TODO: 返回实际 tick 数据
    return {
        "symbol": symbol,
        "tick": None,
        "message": "暂无 tick 数据"
    }
