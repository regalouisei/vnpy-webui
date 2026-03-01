# 回测 API

from fastapi import APIRouter, HTTPException, status
from typing import List
import json
from datetime import datetime

# 创建路由器
router = APIRouter(
    prefix="/backtest",
    tags=["回测"]
)

# TODO: 集成 VnPy 回测引擎
# from app.core.vnpy_engine import VnPyEngine

# 临时数据存储
backtests_db = {}

@router.get("/")
async def get_all_backtests():
    """获取所有回测"""
    return {
        "backtests": list(backtests_db.values())
    }

@router.get("/{backtest_id}")
async def get_backtest(backtest_id: str):
    """获取回测详情"""
    backtest = backtests_db.get(backtest_id)
    if not backtest:
        raise HTTPException(
            status_code=404,
            detail=f"回测 {backtest_id} 不存在"
        )
    return {
        "backtest": backtest
    }

@router.get("/{backtest_id}/chart")
async def get_backtest_chart(backtest_id: str):
    """获取回测图表"""
    backtest = backtests_db.get(backtest_id)
    if not backtest:
        raise HTTPException(
            status_code=404,
            detail=f"回测 {backtest_id} 不存在"
        )
    # TODO: 返回实际图表数据
    return {
        "backtest_id": backtest_id,
        "chart": {
            "equity": [],
            "drawdown": []
        }
    }

@router.post("/run")
async def run_backtest(request: dict):
    """运行回测"""
    strategy_name = request.get("strategy_name")
    symbol = request.get("symbol")
    start_date = request.get("start_date")
    end_date = request.get("end_date")
    parameters = request.get("parameters", {})

    # TODO: 从 VnPy 引擎运行回测
    backtest_id = f"backtest_{len(backtests_db) + 1}"

    backtest = {
        "id": backtest_id,
        "strategy_name": strategy_name,
        "symbol": symbol,
        "start_date": start_date,
        "end_date": end_date,
        "parameters": parameters,
        "status": "running",
        "created_at": datetime.now().isoformat(),
        "results": {}
    }

    backtests_db[backtest_id] = backtest

    return {
        "message": "回测开始运行",
        "backtest": backtest
    }

@router.post("/{backtest_id}/stop")
async def stop_backtest(backtest_id: str):
    """停止回测"""
    # TODO: 从 VnPy 引擎停止回测
    backtest = backtests_db.get(backtest_id)
    if not backtest:
        raise HTTPException(
            status_code=404,
            detail=f"回测 {backtest_id} 不存在"
        )

    backtest["status"] = "stopped"
    backtest["stopped_at"] = datetime.now().isoformat()

    return {
        "message": f"回测 {backtest_id} 已停止",
        "backtest": backtest
    }

@router.get("/{backtest_id}/results")
async def get_backtest_results(backtest_id: str):
    """获取回测结果"""
    backtest = backtests_db.get(backtest_id)
    if not backtest:
        raise HTTPException(
            status_code=404,
            detail=f"回测 {backtest_id} 不存在"
        )
    # TODO: 从 VnPy 引擎获取回测结果
    return {
        "backtest_id": backtest_id,
        "results": backtest.get("results", {})
    }
