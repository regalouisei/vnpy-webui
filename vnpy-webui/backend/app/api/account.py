# 账户 API

from fastapi import APIRouter, HTTPException, status
from typing import List
import json

# 创建路由器
router = APIRouter(
    prefix="/accounts",
    tags=["账户"]
)

# TODO: 集成 VnPy 引擎
# from app.core.vnpy_engine import VnPyEngine

# 临时数据存储
accounts_db = {}

@router.get("/")
async def get_all_accounts():
    """获取所有账户"""
    # TODO: 从 VnPy 引擎获取账户数据
    return {
        "accounts": list(accounts_db.values())
    }

@router.get("/{account_id}")
async def get_account(account_id: str):
    """获取账户详情"""
    # TODO: 从 VnPy 引擎获取账户详情
    account = accounts_db.get(account_id)
    if not account:
        raise HTTPException(
            status_code=404,
            detail=f"账户 {account_id} 不存在"
        )
    return {
        "account": account
    }

@router.get("/{account_id}/balance")
async def get_account_balance(account_id: str):
    """获取账户余额"""
    account = accounts_db.get(account_id)
    if not account:
        raise HTTPException(
            status_code=404,
            detail=f"账户 {account_id} 不存在"
        )
    return {
        "account_id": account_id,
        "balance": account.get("balance", 0),
        "available": account.get("available", 0),
        "frozen": account.get("frozen", 0),
        "currency": account.get("currency", "CNY")
    }

@router.post("/refresh")
async def refresh_account(account_id: str):
    """刷新账户数据"""
    # TODO: 从 VnPy 引擎刷新账户数据
    account = accounts_db.get(account_id)
    if not account:
        raise HTTPException(
            status_code=404,
            detail=f"账户 {account_id} 不存在"
        )
    
    # TODO: 实际刷新逻辑
    return {
        "message": "账户数据已刷新",
        "account": account
    }
