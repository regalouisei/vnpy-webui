# 量化工厂快速使用指南

**版本**: 1.0
**更新日期**: 2026-02-21

---

## 📋 目录

1. [项目简介](#1-项目简介)
2. [快速安装](#2-快速安装)
3. [核心功能使用](#3-核心功能使用)
4. [回测功能](#4-回测功能)
5. [数据管理](#5-数据管理)
6. [Web API 使用](#6-web-api-使用)
7. [常见问题](#7-常见问题)

---

## 1. 项目简介

量化工厂是基于 **VnPy 量化交易框架** 的完整测试与开发项目，提供：

- ✅ 完整的 VnPy 功能测试
- ✅ 详细的开发文档
- ✅ 示例策略代码
- ✅ 回测与实盘交易支持
- ⏸️ Web UI（开发中）

---

## 2. 快速安装

### 2.1 环境要求

- Python 3.10+
- Linux / macOS / Windows

### 2.2 安装 VnPy

```bash
# 方式 1：pip 安装（推荐）
pip install vnpy

# 方式 2：从源码安装
git clone https://github.com/vnpy/vnpy.git
cd vnpy
pip install -e .
```

### 2.3 安装依赖

```bash
# 进入项目目录
cd /root/.openclaw/workspace/quant-factory

# 安装测试依赖
pip install pytest
```

---

## 3. 核心功能使用

### 3.1 运行测试

```bash
# 运行核心功能测试
python3 complete_test_suite.py

# 运行所有测试
python3 run_all_tests.py

# 运行 CTA 策略测试
python3 test_cta_strategy_comprehensive.py

# 运行回测测试
python3 test_backtest_comprehensive.py

# 运行数据管理测试
python3 test_data_manager_comprehensive.py
```

### 3.2 连接 CTP（测试环境）

```python
from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.gateway.ctp import CtpGateway

# 创建主引擎
event_engine = EventEngine()
main_engine = MainEngine(event_engine)

# 添加 CTP 网关
main_engine.add_gateway(CtpGateway)

# 连接
main_engine.connect("CTP")
```

**测试环境配置**：
```
用户名: 17130
密码: 123456
经纪商代码: 9999
```

---

## 4. 回测功能

### 4.1 基础回测

```python
from vnpy_ctastrategy.backtesting import BacktestingEngine
from datetime import datetime
from vnpy.trader.constant import Interval

# 创建回测引擎
engine = BacktestingEngine()

# 设置参数
engine.set_parameters(
    vt_symbol="IF2602.CFFEX",
    interval=Interval.MINUTE,
    start=datetime(2024, 1, 1),
    end=datetime(2024, 12, 31),
    rate=0.3/10000,      # 手续费率
    slippage=0.2,        # 滑点
    size=300,            # 合约乘数
    capital=1_000_000,   # 初始资金
)

# 添加策略
from strategies.simple_double_ma_strategy import DualMaStrategy
engine.add_strategy(DualMaStrategy, {
    "fast_window": 10,
    "slow_window": 20,
    "fixed_size": 1
})

# 加载数据并运行
engine.load_data()
engine.run_backtesting()

# 计算结果
df = engine.calculate_result()
stats = engine.calculate_statistics()

# 显示结果
print(f"夏普比率: {stats['sharpe_ratio']:.2f}")
print(f"年化收益率: {stats['annual_return']:.2f}%")
print(f"最大回撤: {stats['max_ddpercent']:.2f}%")
```

### 4.2 参数优化

```python
from vnpy_ctastrategy.backtesting import OptimizationSetting

# 创建优化设置
optimization_setting = OptimizationSetting()

# 添加优化参数
optimization_setting.add_parameter("fast_window", 5, 20, 5)   # 5, 10, 15, 20
optimization_setting.add_parameter("slow_window", 20, 60, 10) # 20, 30, 40, 50, 60

# 暴力搜索优化
results = engine.run_optimization(
    optimization_setting,
    target_name="sharpe_ratio",
    max_workers=4,
    output=True
)

# 排序结果
results.sort(key=lambda x: x[1], reverse=True)
best_setting, best_value, best_stats = results[0]
print(f"最优参数: {best_setting}")
print(f"夏普比率: {best_value:.2f}")
```

---

## 5. 数据管理

### 5.1 数据存储

```python
from vnpy.trader.database import get_database
from vnpy.trader.object import BarData

# 获取数据库实例
database = get_database()

# 保存数据
database.save_bar_data(bars)
```

### 5.2 数据查询

```python
from datetime import datetime
from vnpy.trader.constant import Exchange, Interval

# 查询数据
bars = database.load_bar_data(
    symbol="IF2602",
    exchange=Exchange.CFFEX,
    interval=Interval.MINUTE,
    start=datetime(2024, 1, 1),
    end=datetime(2024, 12, 31)
)

# 显示数据概览
overviews = database.get_bar_overview()
for overview in overviews:
    print(f"{overview.symbol} {overview.exchange.value} {overview.interval.value}: "
          f"{overview.count} 条")
```

### 5.3 数据导入导出

**导出为 CSV**：
```python
import pandas as pd

# 转换为 DataFrame
data = [{
    'datetime': bar.datetime,
    'open': bar.open_price,
    'high': bar.high_price,
    'low': bar.low_price,
    'close': bar.close_price,
    'volume': bar.volume
} for bar in bars]

df = pd.DataFrame(data)
df.to_csv("data.csv", index=False)
```

**从 CSV 导入**：
```python
import pandas as pd

# 读取 CSV
df = pd.read_csv("data.csv")

# 转换为 BarData
bars = []
for _, row in df.iterrows():
    bar = BarData(
        symbol="IF2602",
        exchange=Exchange.CFFEX,
        interval=Interval.MINUTE,
        datetime=pd.to_datetime(row['datetime']),
        open_price=row['open'],
        high_price=row['high'],
        low_price=row['low'],
        close_price=row['close'],
        volume=row['volume'],
        gateway_name="CSV"
    )
    bars.append(bar)

# 保存到数据库
database.save_bar_data(bars)
```

---

## 6. Web API 使用

### 6.1 获取 Token

```python
import requests

url = "http://127.0.0.1:8000/"

# 登录获取 Token
r = requests.post(
    url + "token",
    data={"username": "vnpy", "password": "vnpy"}
)
token = r.json()["access_token"]
print(f"Token: {token}")
```

### 6.2 查询账户

```python
# 查询账户信息
headers = {"Authorization": f"Bearer {token}"}
r = requests.get(f"{url}account", headers=headers)
account = r.json()
print(f"账户资金: {account['data']['balance']}")
```

### 6.3 查询持仓

```python
# 查询持仓
r = requests.get(f"{url}position", headers=headers)
positions = r.json()
for pos in positions['data']:
    print(f"{pos['symbol']} 持仓: {pos['volume']}")
```

### 6.4 发送订单

```python
# 发送限价单
order_req = {
    "symbol": "IF2602",
    "exchange": "CFFEX",
    "direction": "多",
    "type": "限价",
    "volume": 1,
    "price": 4000.0,
    "offset": "开",
    "reference": "WebTrader"
}

r = requests.post(
    f"{url}order",
    json=order_req,
    headers=headers
)
vt_orderid = r.json()["data"]
print(f"订单ID: {vt_orderid}")
```

### 6.5 WebSocket 实时推送

```python
from websocket import create_connection
import json

# 建立 WebSocket 连接
ws = create_connection(f"ws://127.0.0.1:8000/ws/?token={token}")

# 接收消息
while True:
    message = ws.recv()
    msg_obj = json.loads(message)
    msg_type = msg_obj.get("type")
    data = msg_obj.get("data")

    if msg_type == "tick":
        print(f"行情: {data['symbol']} @ {data['last_price']}")
    elif msg_type == "order":
        print(f"订单: {data['orderid']} - {data['status']}")
    elif msg_type == "trade":
        print(f"成交: {data['symbol']} @ {data['price']}")
```

---

## 7. 常见问题

### Q1: 如何切换数据库？

**切换到 MySQL**：

```python
# 修改 vnpy.trader.setting.json
{
  "database.name": "mysql",
  "database.host": "localhost",
  "database.port": 3306,
  "database.username": "your_username",
  "database.password": "your_password",
  "database.database": "vnpy"
}
```

**切换到 PostgreSQL**：

```python
{
  "database.name": "postgresql",
  "database.host": "localhost",
  "database.port": 5432,
  "database.username": "your_username",
  "database.password": "your_password",
  "database.database": "vnpy"
}
```

### Q2: 回测太慢怎么办？

**优化方法**：

1. 使用 K 线模式（BAR）而非 Tick 模式
2. 减少回测时间范围
3. 使用多进程参数优化
4. 优化策略代码（使用 NumPy、滑动窗口）

### Q3: 实盘交易需要注意什么？

**注意事项**：

1. 在测试环境充分测试
2. 设置合理的止损
3. 控制仓位大小
4. 监控系统稳定性
5. 做好风险控制

### Q4: 如何开发自己的策略？

**开发步骤**：

1. 继承 `CtaTemplate` 类
2. 定义策略参数和变量
3. 实现 `on_init`、`on_start`、`on_stop` 方法
4. 实现 `on_bar` 或 `on_tick` 方法
5. 使用 `send_order` 发送订单
6. 在回测中测试策略
7. 在实盘中验证策略

**参考示例**：
- `strategies/simple_double_ma_strategy.py` - 双均线策略
- VnPy 内置策略（9个）

### Q5: Web API 支持哪些功能？

**当前支持**：
- 账户查询
- 持仓查询
- 订单管理
- 行情订阅
- WebSocket 实时推送

**规划中**：
- 策略管理
- 回测功能
- 数据管理
- 图表展示

---

## 📚 更多文档

- **完整分析报告**: `PROJECT_ANALYSIS_REPORT.md`
- **项目总览**: `README.md`
- **深度解析文档**: `docs/` 目录
- **测试脚本**: `test_*.py` 文件

---

## 🆘 获取帮助

- **VnPy 官网**: https://www.vnpy.com
- **VnPy 文档**: https://docs.vnpy.com
- **VnPy 社区**: https://www.vnpy.com/forum

---

**文档版本**: 1.0
**更新日期**: 2026-02-21
