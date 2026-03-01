# FastAPI 主应用

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

# 创建应用实例
app = FastAPI(
    title="VnPy Web API",
    description="VnPy 量化交易平台 Web API",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 导入路由
from app.api import account, position, contract, quote, strategy, backtest, trade, data, report

# 注册路由
app.include_router(account.router, prefix="/api/accounts", tags=["账户"])
app.include_router(position.router, prefix="/api/positions", tags=["持仓"])
app.include_router(contract.router, prefix="/api/contracts", tags=["合约"])
app.include_router(quote.router, prefix="/api/quotes", tags=["行情"])
app.include_router(strategy.router, prefix="/api/strategies", tags=["策略"])
app.include_router(backtest.router, prefix="/api/backtest", tags=["回测"])
app.include_router(trade.router, prefix="/api/trade", tags=["交易"])
app.include_router(data.router, prefix="/api/data", tags=["数据"])
app.include_router(report.router, prefix="/api/reports", tags=["报表"])

# 根路由
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "VnPy Web API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    """健康检查"""
    return {
        "status": "ok",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
