# VnPy Web UI 后端

**框架**: FastAPI
**Python 版本**: 3.10+
**数据库**: SQLite / MySQL / PostgreSQL

---

## 📦 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用
│   ├── api/                 # API 路由
│   │   ├── __init__.py
│   │   ├── account.py        # 账户 API
│   │   ├── position.py       # 持仓 API
│   │   ├── contract.py       # 合约 API
│   │   ├── quote.py          # 行情 API
│   │   ├── strategy.py        # 策略 API
│   │   ├── backtest.py        # 回测 API
│   │   ├── trade.py           # 交易 API
│   │   ├── data.py            # 数据 API
│   │   └── report.py          # 报表 API
│   ├── core/                # 核心逻辑
│   │   ├── __init__.py
│   │   ├── vnpy_engine.py    # VnPy 引擎封装
│   │   ├── websocket.py      # WebSocket 处理
│   │   └── scheduler.py       # 定时任务
│   ├── models/              # Pydantic 模型
│   │   ├── __init__.py
│   │   ├── account.py
│   │   ├── position.py
│   │   ├── contract.py
│   │   ├── tick.py
│   │   ├── bar.py
│   │   ├── order.py
│   │   ├── trade.py
│   │   ├── strategy.py
│   │   └── backtest.py
│   ├── schemas/             # 数据库模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── record.py
│   └── utils/               # 工具函数
│       ├── __init__.py
│       ├── config.py       # 配置
│       ├── database.py      # 数据库
│       └── logger.py        # 日志
├── database/              # 数据库文件
│   └── vnpy.db
├── vnpy/                  # VnPy 集成
│   ├── __init__.py
│   ├── engine.py          # VnPy 引擎
│   ├── strategy.py        # 策略
│   └── backtest.py        # 回测
└── main.py                # 应用入口
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd backend

pip install fastapi uvicorn[standard]
pip install sqlalchemy pymysql psycopg2-binary
pip install pydantic
pip install python-multipart
pip install websockets
pip install vnpy vnpy_ctp vnpy_ctastrategy vnpy_sqlite
```

### 2. 配置环境

创建 `.env` 文件:

```env
# 数据库配置
DATABASE_URL=sqlite:///./database/vnpy.db

# VnPy 配置
VNPY_SETTING_PATH=~/.vntrader/vt_setting.json

# CTP 网关配置
CTP_USERNAME=17130
CTP_PASSWORD=123456
CTP_BROKERID=9999
CTP_TD_ADDRESS=tcp://trading.openctp.cn:30001
CTP_MD_ADDRESS=tcp://trading.openctp.cn:30011

# WebSocket 配置
WS_HOST=0.0.0.0
WS_PORT=8000
```

### 3. 启动服务器

```bash
# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 启动生产服务器
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 📋 API 路由

### 账户 API

- `GET /api/accounts` - 获取所有账户
- `GET /api/accounts/{accountid}` - 获取账户详情
- `GET /api/accounts/{accountid}/balance` - 获取账户余额

### 持仓 API

- `GET /api/positions` - 获取所有持仓
- `GET /api/positions/{symbol}` - 获取持仓详情
- `GET /api/positions/{symbol}/pnl` - 获取持仓盈亏

### 合约 API

- `GET /api/contracts` - 获取所有合约
- `GET /api/contracts/{symbol}` - 获取合约详情
- `GET /api/contracts/{symbol}/tick` - 获取合约 tick

### 行情 API

- `POST /api/quotes/subscribe` - 订阅行情
- `POST /api/quotes/unsubscribe` - 取消订阅
- `WS /api/quotes/stream` - 行情流

### 策略 API

- `GET /api/strategies` - 获取所有策略
- `POST /api/strategies` - 创建策略
- `DELETE /api/strategies/{strategy_id}` - 删除策略
- `POST /api/strategies/{strategy_id}/start` - 启动策略
- `POST /api/strategies/{strategy_id}/stop` - 停止策略

### 回测 API

- `POST /api/backtest/run` - 运行回测
- `GET /api/backtest/results/{backtest_id}` - 获取回测结果
- `GET /api/backtest/results/{backtest_id}/chart` - 获取回测图表

### 交易 API

- `POST /api/trade/orders` - 下单
- `DELETE /api/trade/orders/{orderid}` - 撤单
- `GET /api/trade/orders` - 获取所有订单
- `GET /api/trade/trades` - 获取所有成交

### 数据 API

- `POST /api/data/import` - 导入数据
- `POST /api/data/export` - 导出数据
- `GET /api/data/bars` - 获取 K 线数据
- `GET /api/data/ticks` - 获取 Tick 数据

### 报表 API

- `GET /api/reports/performance` - 获取性能报告
- `GET /api/reports/risk` - 获取风险报告
- `GET /api/reports/monthly` - 获取月度报告

---

## 🔧 核心功能

### VnPy 引擎封装

```python
from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.ctp.gateway import CtpGateway
from vnpy_ctastrategy import CtaEngine

class VnPyEngine:
    def __init__(self):
        self.event_engine = EventEngine()
        self.main_engine = MainEngine(self.event_engine)
        self.cta_engine = None

    def connect(self, setting: dict, gateway_name: str):
        self.main_engine.add_gateway(CtpGateway, gateway_name)
        self.main_engine.connect(setting, gateway_name)

    def add_cta_engine(self):
        self.cta_engine = self.main_engine.add_engine(CtaEngine)
        self.cta_engine.init_engine()
```

### WebSocket 行情推送

```python
from fastapi import WebSocket
from typing import List

async def quote_stream(websocket: WebSocket):
    """实时行情推送"""
    while True:
        ticks = get_latest_ticks()
        await websocket.send_json(ticks)
        await asyncio.sleep(1)
```

---

## 📝 开发指南

### 添加新的 API 路由

1. 在 `app/api/` 中创建新的路由文件
2. 定义 FastAPI 路由
3. 实现业务逻辑
4. 在 `app/main.py` 中注册路由

### 添加新的数据模型

1. 在 `app/models/` 中创建新的模型文件
2. 定义 Pydantic 模型
3. 在 API 中使用模型

---

## 🚀 部署

### Docker 部署

```dockerfile
FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./database:/app/database
      - ~/.vntrader:/root/.vntrader
```

---

**文档创建时间**: 2026-02-20 08:50:00 UTC
**文档版本**: 1.0
