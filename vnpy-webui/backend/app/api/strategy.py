# 策略 API

from fastapi import APIRouter, HTTPException, status
from typing import List

# 创建路由器
router = APIRouter(
    prefix="/strategies",
    tags=["策略"]
)

# TODO: 集成 VnPy 引擎
# from app.core.vnpy_engine import VnPyEngine

# 临时数据存储
strategies_db = {}

@router.get("/")
async def get_all_strategies():
    """获取所有策略"""
    return {
        "strategies": list(strategies_db.values())
    }

@router.get("/{strategy_id}")
async def get_strategy(strategy_id: str):
    """获取策略详情"""
    strategy = strategies_db.get(strategy_id)
    if not strategy:
        raise HTTPException(
            status_code=404,
            detail=f"策略 {strategy_id} 不存在"
        )
    return {
        "strategy": strategy
    }

@router.post("/")
async def create_strategy(request: dict):
    """创建策略"""
    # TODO: 从 VnPy 引擎创建策略
    strategy_id = f"strategy_{len(strategies_db) + 1}"

    strategy = {
        "id": strategy_id,
        "name": request.get("name"),
        "class_name": request.get("class_name"),
        "parameters": request.get("parameters", {}),
        "status": "created",
        "created_at": "2026-02-20T00:00:00Z"
    }

    strategies_db[strategy_id] = strategy

    return {
        "message": "策略创建成功",
        "strategy": strategy
    }

@router.delete("/{strategy_id}")
async def delete_strategy(strategy_id: str):
    """删除策略"""
    # TODO: 从 VnPy 引擎删除策略
    strategy = strategies_db.get(strategy_id)
    if not strategy:
        raise HTTPException(
            status_code=404,
            detail=f"策略 {strategy_id} 不存在"
        )

    del strategies_db[strategy_id]

    return {
        "message": f"策略 {strategy_id} 已删除"
    }

@router.post("/{strategy_id}/start")
async def start_strategy(strategy_id: str):
    """启动策略"""
    # TODO: 从 VnPy 引擎启动策略
    strategy = strategies_db.get(strategy_id)
    if not strategy:
        raise HTTPException(
            status_code=404,
            detail=f"策略 {strategy_id} 不存在"
        )

    strategy["status"] = "running"
    strategy["started_at"] = "2026-02-20T00:00:00Z"

    return {
        "message": f"策略 {strategy_id} 已启动",
        "strategy": strategy
    }

@router.post("/{strategy_id}/stop")
async def stop_strategy(strategy_id: str):
    """停止策略"""
    # TODO: 从 VnPy 引擎停止策略
    strategy = strategies_db.get(strategy_id)
    if not strategy:
        raise HTTPException(
            status_code=404,
            detail=f"策略 {strategy_id} 不存在"
        )

    strategy["status"] = "stopped"
    strategy["stopped_at"] = "2026-02-20T00:00:00Z"

    return {
        "message": f"策略 {strategy_id} 已停止",
        "strategy": strategy
    }

@router.get("/{strategy_id}/log")
async def get_strategy_log(strategy_id: str):
    """获取策略日志"""
    # TODO: 从 VnPy 引擎获取策略日志
    strategy = strategies_db.get(strategy_id)
    if not strategy:
        raise HTTPException(
            status_code=404,
            detail=f"策略 {strategy_id} 不存在"
        )

    return {
        "strategy_id": strategy_id,
        "logs": []
    }
