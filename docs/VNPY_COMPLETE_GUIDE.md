# VnPy 完整安装与使用指南

**版本**: VnPy 3.x
**更新时间**: 2026-02-20
**适用平台**: Linux / Windows / macOS

---

## 目录

1. [系统要求](#1-系统要求)
2. [快速开始](#2-快速开始)
3. [详细安装](#3-详细安装)
4. [配置指南](#4-配置指南)
5. [基本使用](#5-基本使用)
6. [CTP网关配置](#6-ctp网关配置)
7. [策略开发](#7-策略开发)
8. [回测功能](#8-回测功能)
9. [实盘交易](#9-实盘交易)
10. [数据管理](#10-数据管理)
11. [API参考](#11-api参考)
12. [常见问题](#12-常见问题)
13. [最佳实践](#13-最佳实践)

---

## 1. 系统要求

### 1.1 操作系统
- ✅ Linux (推荐 Ubuntu 20.04+ / CentOS 8+)
- ✅ Windows 10/11
- ✅ macOS 10.15+

### 1.2 Python环境
- Python 3.8 - 3.12 (推荐 3.10 或 3.11)
- pip 包管理器

### 1.3 硬件要求
- CPU: 2核心以上
- 内存: 4GB以上 (推荐 8GB+)
- 硬盘: 10GB以上可用空间

### 1.4 网络要求
- 稳定的互联网连接
- 可访问 CTP 服务器端口 (默认: 30001/30011)

---

## 2. 快速开始

### 2.1 安装VnPy (推荐方式)

```bash
# 创建虚拟环境 (可选但推荐)
python -m venv vnvpy_env
source vnvpy_env/bin/activate  # Linux/macOS
# 或
venvpy_env\Scripts\activate  # Windows

# 安装VnPy核心
pip install vnpy

# 安装CTP网关
pip install vnpy_ctp

# 安装CTA策略模块
pip install vnpy_ctastrategy

# 安装SQLite数据库
pip install vnpy_sqlite
```

### 2.2 验证安装

```python
# 验证安装
from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy_ctp.gateway import CtpGateway
from vnpy_ctastrategy import CtaEngine

print("✅ VnPy 安装成功!")
```

---

## 3. 详细安装

### 3.1 从源码安装

```bash
# 克隆仓库
git clone https://github.com/vnpy/vnpy.git
cd vnpy

# 安装依赖
pip install -r requirements.txt

# 安装VnPy
pip install -e .
```

### 3.2 分模块安装

VnPy采用模块化设计，可以按需安装:

#### 核心模块
```bash
pip install vnpy
```

#### 网关模块
```bash
# CTP网关 (国内期货)
pip install vnpy_ctp

# 其他网关 (按需)
pip install vnpy_ib  #  Interactive Brokers
pip install vnpy_oes  # 期权
pip install vnpy_binance  #  数字货币
pip install vnpy_okx
```

#### 策略模块
```bash
# CTA策略
pip install vnpy_ctastrategy

# 组合策略
pip install vnpy_portfoliostrategy

# 价差套利
pip install vnpy_spreadtrading

# 期权策略
pip install vnpy_optionmaster

# 算法交易
pip install vnpy_algotrading

# 脚本策略
pip install vnpy_scripttrader

# AI量化
pip install vnpy_alpha
```

#### 数据库模块
```bash
# SQLite (默认，轻量级)
pip install vnpy_sqlite

# MySQL (企业级)
pip install vnpy_mysql

# PostgreSQL (企业级)
pip install vnpy_postgresql
```

### 3.3 可选依赖

```bash
# 数据分析
pip install pandas numpy

# 图表绘制
pip install matplotlib plotly

# 技术指标
pip install ta-lib

# Web界面
pip install fastapi uvicorn
```

---

## 4. 配置指南

### 4.1 配置文件位置

配置文件默认位置:
- Linux: `~/.vntrader/`
- Windows: `C:/Users/<用户名>/.vntrader/`
- macOS: `~/.vntrader/`

### 4.2 数据库配置

编辑 `~/.vntrader/vt_setting.json`:

```json
{
  "database": {
    "database": "sqlite",
    "database.db_path": "/path/to/database.db"
  }
}
```

#### MySQL配置示例

```json
{
  "database": {
    "database": "mysql",
    "host": "localhost",
    "port": 3306,
    "username": "vnpy",
    "password": "password",
    "database": "vnpy"
  }
}
```

#### PostgreSQL配置示例

```json
{
  "database": {
    "database": "postgresql",
    "host": "localhost",
    "port": 5432,
    "username": "vnpy",
    "password": "password",
    "database": "vnpy"
  }
}
```

### 4.3 网关配置

编辑 `~/.vntrader/gateway_name_setting.json` (例如 `ctp_setting.json`):

```json
{
  "用户名": "your_username",
  "密码": "your_password",
  "经纪商代码": "9999",
  "交易服务器": "tcp://180.168.146.187:10130",
  "行情服务器": "tcp://180.168.146.187:10131",
  "产品名称": "",
  "授权编码": "",
  "柜台环境": "实盘"
}
```

### 4.4 OpenCTP测试环境配置

```json
{
  "用户名": "17130",
  "密码": "123456",
  "经纪商代码": "9999",
  "交易服务器": "tcp://trading.openctp.cn:30001",
  "行情服务器": "tcp://trading.openctp.cn:30011",
  "产品名称": "",
  "授权编码": "",
  "柜台环境": "测试"
}
```

---

## 5. 基本使用

### 5.1 创建第一个VnPy应用

```python
from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy_ctp.gateway import CtpGateway

# 创建事件引擎
event_engine = EventEngine()

# 创建主引擎
main_engine = MainEngine(event_engine)

# 添加CTP网关
main_engine.add_gateway(CtpGateway, gateway_name="CTP")

# 连接
gateway_setting = {
    "用户名": "17130",
    "密码": "123456",
    "经纪商代码": "9999",
    "交易服务器": "tcp://trading.openctp.cn:30001",
    "行情服务器": "tcp://trading.openctp.cn:30011",
    "产品名称": "",
    "授权编码": "",
    "柜台环境": "测试"
}

main_engine.connect(gateway_setting, "CTP")

# 等待连接
import time
time.sleep(5)
```

### 5.2 查询账户信息

```python
# 从OmsEngine获取账户信息
oms_engine = main_engine.get_engine("oms")
accounts = oms_engine.get_all_accounts()

for account in accounts:
    print(f"账号: {account.accountid}")
    print(f"余额: {account.balance:,.2f}")
    print(f"可用: {account.available:,.2f}")
    print(f"冻结: {account.frozen:,.2f}")
```

### 5.3 订阅行情

```python
from vnpy.trader.object import SubscribeRequest

# 查询合约
contracts = oms_engine.get_all_contracts()

# 找到需要的合约
for contract in contracts:
    if "IF2602" in contract.symbol:
        # 订阅行情
        req = SubscribeRequest(
            symbol=contract.symbol,
            exchange=contract.exchange
        )
        main_engine.subscribe(req, "CTP")
        break
```

### 5.4 监听行情事件

```python
from vnpy.trader.event import EVENT_TICK
from vnpy.trader.object import TickData

def on_tick(event: Event):
    tick: TickData = event.data
    print(f"Tick: {tick.symbol} {tick.last_price}")

event_engine.register(EVENT_TICK, on_tick)
```

---

## 6. CTP网关配置

### 6.1 CTP API文件

VnPy CTP网关需要CTP API动态链接库:

**Windows**: 放在项目根目录或 `C:/Windows/System32/`
- `thostmduserapi_se.dll` (行情)
- `thosttraderapi_se.dll` (交易)

**Linux**: 放在 `/usr/local/lib/` 或项目根目录
- `libthostmduserapi_se.so` (行情)
- `libthosttraderapi_se.so` (交易)

**macOS**: 放在 `/usr/local/lib/` 或项目根目录
- `libthostmduserapi_se.dylib` (行情)
- `libthosttraderapi_se.dylib` (交易)

### 6.2 OpenCTP测试环境

OpenCTP提供免费的测试环境，适合开发和测试:

- **注册地址**: http://openctp.cn
- **测试账号**: 17130
- **测试密码**: 123456
- **经纪商代码**: 9999

### 6.3 连接测试

```python
import time
from vnpy.event import EventEngine, Event
from vnpy.trader.engine import MainEngine
from vnpy_ctp.gateway import CtpGateway
from vnpy.trader.event import EVENT_LOG

# 创建引擎
event_engine = EventEngine()
main_engine = MainEngine(event_engine)
main_engine.add_gateway(CtpGateway, gateway_name="CTP")

# 日志回调
log_events = []
def on_log(event: Event):
    log = event.data
    log_events.append(log)
    print(f"[LOG] {log.msg}")

event_engine.register(EVENT_LOG, on_log)

# 连接
gateway_setting = {
    "用户名": "17130",
    "密码": "123456",
    "经纪商代码": "9999",
    "交易服务器": "tcp://trading.openctp.cn:30001",
    "行情服务器": "tcp://trading.openctp.cn:30011",
    "产品名称": "",
    "授权编码": "",
    "柜台环境": "测试"
}

main_engine.connect(gateway_setting, "CTP")

# 等待连接
for i in range(20):
    time.sleep(1)
    if any("登录成功" in log.msg for log in log_events):
        print("✅ 连接成功!")
        break
```

---

## 7. 策略开发

### 7.1 CTA策略模板

```python
from vnpy_ctastrategy.template import CtaTemplate
from vnpy.trader.object import TickData, BarData, OrderData, TradeData
from vnpy.trader.constant import Interval

class MyStrategy(CtaTemplate):
    """"我的策略"""

    # 策略参数
    fast_window: int = 10
    slow_window: int = 30
    fixed_size: int = 1

    # 策略变量
    bars: list = []

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

    def on_init(self):
        """策略初始化"""
        self.write_log("策略初始化")
        self.load_bar(10)  # 加载历史数据

    def on_start(self):
        """策略启动"""
        self.write_log("策略启动")

    def on_stop(self):
        """策略停止"""
        self.write_log("策略停止")

    def on_tick(self, tick: TickData):
        """Tick事件"""
        pass

    def on_bar(self, bar: BarData):
        """K线事件"""
        self.bars.append(bar)

        # 计算均线
        if len(self.bars) >= self.slow_window:
            fast_ma = sum(b.close_price for b in self.bars[-self.fast_window:]) / self.fast_window
            slow_ma = sum(b.close_price for b in self.bars[-self.slow_window:]) / self.slow_window

            # 金叉买入
            if fast_ma > slow_ma and self.pos == 0:
                self.buy(bar.close_price, self.fixed_size)

            # 死叉卖出
            elif fast_ma < slow_ma and self.pos > 0:
                self.sell(bar.close_price, self.fixed_size)

    def on_order(self, order: OrderData):
        """订单事件"""
        pass

    def on_trade(self, trade: TradeData):
        """成交事件"""
        pass
```

### 7.2 添加和运行策略

```python
from vnpy_ctastrategy import CtaEngine

# 添加CTA引擎
cta_engine = main_engine.add_engine(CtaEngine)
cta_engine.init_engine()

# 添加策略
cta_engine.add_strategy(
    MyStrategy,
    strategy_name="my_strategy",
    vt_symbol="IF2602.CFFEX",
    setting={
        "fast_window": 10,
        "slow_window": 30,
        "fixed_size": 1
    }
)

# 初始化策略
cta_engine.init_strategy("my_strategy")

# 启动策略
cta_engine.start_strategy("my_strategy")
```

### 7.3 内置策略

VnPy提供9个内置策略:

1. **MultiTimeframeStrategy** - 多时间框架策略
2. **DualThrustStrategy** - 双通道策略
3. **DoubleMaStrategy** - 双均线策略
4. **TurtleSignalStrategy** - 海龟交易策略
5. **AtrRsiStrategy** - ATR+RSI策略
6. **BollChannelStrategy** - 布林通道策略
7. **TestStrategy** - 测试策略
8. **MultiSignalStrategy** - 多信号策略
9. **KingKeltnerStrategy** - 金肯特纳通道策略

---

## 8. 回测功能

### 8.1 创建回测引擎

```python
from vnpy_ctastrategy.backtesting import BacktestingEngine
from datetime import datetime

# 创建回测引擎
backtesting_engine = BacktestingEngine()

# 设置回测参数
backtesting_engine.set_parameters(
    vt_symbol="IF2602.CFFEX",
    interval=Interval.MINUTE,
    start=datetime(2024, 1, 1),
    end=datetime(2024, 12, 31),
    rate=0.3/10000,      # 手续费率 (万分之三)
    slippage=0.2,         # 滑点
    size=300,             # 合约乘数
    pricetick=0.2,        # 最小价格变动
    capital=1_000_000,    # 初始资金
)
```

### 8.2 加载历史数据

```python
from vnpy.trader.database import get_database

# 获取数据库
database = get_database()

# 加载历史数据
bars = database.get_bar_data(
    symbol="IF2602",
    exchange=Exchange.CFFEX,
    interval=Interval.MINUTE,
    start=datetime(2024, 1, 1),
    end=datetime(2024, 12, 31)
)

# 设置数据
backtesting_engine.set_data(bars)
```

### 8.3 添加策略并运行

```python
# 添加策略
backtesting_engine.add_strategy(
    DoubleMaStrategy,
    strategy_name="test_backtest",
    vt_symbol="IF2602.CFFEX",
    setting={
        "fast_window": 10,
        "slow_window": 30,
        "fixed_size": 1
    }
)

# 运行回测
backtesting_engine.run_backtesting()

# 计算结果
backtesting_engine.calculate_result()

# 获取结果
result = backtesting_engine.get_result()

print(f"总收益: {result.total_return:.2f}%")
print(f"最大回撤: {result.max_drawdown:.2f}%")
print(f"夏普比率: {result.sharpe_ratio:.2f}")
print(f"胜率: {result.win_rate:.2f}%")
```

### 8.4 参数优化

```python
from vnpy_ctastrategy.backtesting import OptimizationSetting

# 创建优化设置
optimization_setting = OptimizationSetting()

# 添加优化参数
optimization_setting.add_parameter("fast_window", 5, 20, 5)  # 5, 10, 15, 20
optimization_setting.add_parameter("slow_window", 20, 60, 10)  # 20, 30, 40, 50, 60

# 运行优化
results = backtesting_engine.run_optimization(optimization_setting)

# 查看最优参数
best_result = results[0]
print(f"最优参数: {best_result}")
```

---

## 9. 实盘交易

### 9.1 下单

```python
from vnpy.trader.object import OrderRequest, OrderType
from vnpy.trader.constant import Direction, Offset

# 创建订单
req = OrderRequest(
    symbol="IF2602",
    exchange=Exchange.CFFEX,
    direction=Direction.LONG,  # 买入
    type=OrderType.LIMIT,      # 限价单
    volume=1,                   # 手数
    price=4000.0,               # 价格
    offset=Offset.OPEN,         # 开仓
    reference="TEST001"
)

# 发送订单
orderid = main_engine.send_order(req, "CTP")
print(f"订单ID: {orderid}")
```

### 9.2 撤单

```python
from vnpy.trader.object import CancelRequest

# 创建撤单请求
cancel_req = CancelRequest(
    orderid=orderid,
    symbol="IF2602",
    exchange=Exchange.CFFEX
)

# 发送撤单
main_engine.cancel_order(cancel_req, "CTP")
```

### 9.3 查询订单和成交

```python
# 查询所有订单
orders = oms_engine.get_all_orders()

for order in orders:
    print(f"订单: {order.orderid}")
    print(f"  方向: {order.direction.value}")
    print(f"  开平: {order.offset.value}")
    print(f"  状态: {order.status.value}")
    print(f"  数量: {order.volume}")
    print(f"  成交: {order.traded}")
    print(f"  价格: {order.price}")

# 查询所有成交
trades = oms_engine.get_all_trades()

for trade in trades:
    print(f"成交: {trade.tradeid}")
    print(f"  合约: {trade.symbol}")
    print(f"  方向: {trade.direction.value}")
    print(f"  开平: {trade.offset.value}")
    print(f"  价格: {trade.price}")
    print(f"  数量: {trade.volume}")
```

---

## 10. 数据管理

### 10.1 保存数据

```python
from vnpy.trader.database import get_database

# 获取数据库
database = get_database()

# 保存K线数据
database.save_bar_data(bars)

# 保存Tick数据
database.save_tick_data(ticks)
```

### 10.2 查询数据

```python
# 查询K线数据
bars = database.get_bar_data(
    symbol="IF2602",
    exchange=Exchange.CFFEX,
    interval=Interval.MINUTE,
    start=datetime(2024, 1, 1),
    end=datetime(2024, 12, 31)
)

# 查询Tick数据
ticks = database.get_tick_data(
    symbol="IF2602",
    exchange=Exchange.CFFEX,
    start=datetime(2024, 1, 1),
    end=datetime(2024, 12, 31)
)

# 查询可用数据
available = database.get_bar_data_available()
for symbol, exchange, interval in available:
    print(f"{symbol} {exchange.value} {interval.value}")
```

### 10.3 删除数据

```python
# 删除K线数据
database.delete_bar_data(
    symbol="IF2602",
    exchange=Exchange.CFFEX,
    interval=Interval.MINUTE,
    start=datetime(2024, 1, 1),
    end=datetime(2024, 12, 31)
)

# 删除Tick数据
database.delete_tick_data(
    symbol="IF2602",
    exchange=Exchange.CFFEX
)
```

### 10.4 数据导入导出

```python
import pandas as pd

# 导出为CSV
data = []
for bar in bars:
    data.append({
        "datetime": bar.datetime,
        "open": bar.open_price,
        "high": bar.high_price,
        "low": bar.low_price,
        "close": bar.close_price,
        "volume": bar.volume
    })

df = pd.DataFrame(data)
df.to_csv("data.csv", index=False)

# 从CSV导入
df = pd.read_csv("data.csv")
bars = []
for _, row in df.iterrows():
    bar = BarData(
        symbol="IF2602",
        exchange=Exchange.CFFEX,
        datetime=pd.to_datetime(row['datetime']),
        interval=Interval.MINUTE,
        open_price=row['open'],
        high_price=row['high'],
        low_price=row['low'],
        close_price=row['close'],
        volume=row['volume']
    )
    bars.append(bar)

# 保存到数据库
database.save_bar_data(bars)
```

---

## 11. API参考

### 11.1 核心对象

#### EventEngine (事件引擎)
```python
from vnpy.event import EventEngine

event_engine = EventEngine()
event_engine.start()  # 启动事件引擎
event_engine.stop()   # 停止事件引擎
```

#### MainEngine (主引擎)
```python
from vnpy.trader.engine import MainEngine

main_engine = MainEngine(event_engine)

# 添加网关
main_engine.add_gateway(gateway_class, gateway_name="GATEWAY")

# 连接
main_engine.connect(setting, gateway_name)

# 订阅
main_engine.subscribe(req, gateway_name)

# 下单
orderid = main_engine.send_order(req, gateway_name)

# 撤单
main_engine.cancel_order(req, gateway_name)

# 查询
oms_engine = main_engine.get_engine("oms")
accounts = oms_engine.get_all_accounts()
positions = oms_engine.get_all_positions()
contracts = oms_engine.get_all_contracts()
orders = oms_engine.get_all_orders()
trades = oms_engine.get_all_trades()
```

### 11.2 数据对象

#### BarData (K线数据)
```python
from vnpy.trader.object import BarData

bar = BarData(
    symbol="IF2602",
    exchange=Exchange.CFFEX,
    datetime=datetime.now(),
    interval=Interval.MINUTE,
    open_price=4000.0,
    high_price=4010.0,
    low_price=3990.0,
    close_price=4005.0,
    volume=1000,
    open_interest=5000,
    gateway_name="CTP"
)
```

#### TickData (Tick数据)
```python
from vnpy.trader.object import TickData

tick = TickData(
    symbol="IF2602",
    exchange=Exchange.CFFEX,
    datetime=datetime.now(),
    gateway_name="CTP",
    last_price=4000.0,
    volume=1000,
    open_interest=5000,
    bid_price_1=3999.5,
    ask_price_1=4000.5,
    bid_volume_1=100,
    ask_volume_1=100
)
```

### 11.3 常量

#### Exchange (交易所)
```python
from vnpy.trader.constant import Exchange

Exchange.SSE      # 上交所
Exchange.SZSE     # 深交所
Exchange.CFFEX    # 中金所
Exchange.SHFE     # 上期所
Exchange.DCE      # 大商所
Exchange.CZCE     # 郑商所
Exchange.INE      # 能源中心
```

#### Interval (周期)
```python
from vnpy.trader.constant import Interval

Interval.TICK     # Tick
Interval.MINUTE   # 1分钟
Interval.HOUR     # 1小时
Interval.DAILY    # 1日
Interval.WEEKLY   # 1周
```

#### Direction (方向)
```python
from vnpy.trader.constant import Direction

Direction.LONG    # 多头
Direction.SHORT   # 空头
```

#### Offset (开平)
```python
from vnpy.trader.constant import Offset

Offset.OPEN      # 开仓
Offset.CLOSE     # 平仓
Offset.CLOSETODAY# 平今
Offset.CLOSEYESTERDAY# 平昨
```

#### OrderType (订单类型)
```python
from vnpy.trader.constant import OrderType

OrderType.LIMIT   # 限价单
OrderType.MARKET  # 市价单
OrderType.STOP    # 止损单
```

---

## 12. 常见问题

### 12.1 安装问题

**Q: pip安装速度慢**
A: 使用国内镜像
```bash
pip install vnpy -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**Q: 缺少CTP API文件**
A: 从SimNow下载CTP API
- 地址: http://www.simnow.com.cn
- 下载: CTP API (6.6.1及以上)

**Q: 数据库连接失败**
A: 检查配置文件
```bash
# 查看配置位置
echo $HOME/.vntrader/vt_setting.json
```

### 12.2 连接问题

**Q: CTP连接超时**
A: 检查网络和配置
```python
# 测试网络
ping trading.openctp.cn
telnet trading.openctp.cn 30001
```

**Q: 登录失败**
A: 检查账号密码和服务器地址
- 确认账号密码正确
- 确认服务器地址和端口
- 确认经纪商代码

### 12.3 策略问题

**Q: 策略不启动**
A: 检查策略状态
```python
strategy = cta_engine.get_strategy("strategy_name")
print(f"初始化: {strategy.inited}")
print(f"交易中: {strategy.trading}")
```

**Q: 策略没有信号**
A: 检查历史数据
```python
# 确保加载了足够的历史数据
cta_engine.init_strategy("strategy_name")
```

### 12.4 回测问题

**Q: 回测结果为空**
A: 检查历史数据
```python
# 确认有历史数据
database = get_database()
bars = database.get_bar_data(...)
print(f"数据量: {len(bars)}")
```

**Q: 回测速度慢**
A: 优化回测参数
- 减少数据量
- 使用更快的数据库
- 减少优化参数组合

---

## 13. 最佳实践

### 13.1 代码结构

```
project/
├── strategies/           # 策略目录
│   ├── __init__.py
│   ├── my_strategy.py
│   └── ...
├── data/                # 数据目录
│   ├── exports/
│   └── backups/
├── logs/                # 日志目录
├── config/              # 配置目录
├── main.py             # 主程序
└── requirements.txt   # 依赖列表
```

### 13.2 配置管理

```python
# config/settings.py
from vnpy.trader.setting import SETTINGS

# 网关配置
GATEWAY_SETTING = {
    "用户名": "your_username",
    "密码": "your_password",
    "经纪商代码": "9999",
    "交易服务器": "tcp://...",
    "行情服务器": "tcp://...",
}

# 策略配置
STRATEGY_SETTING = {
    "fast_window": 10,
    "slow_window": 30,
    "fixed_size": 1
}
```

### 13.3 日志管理

```python
import logging
from datetime import datetime

# 配置日志
log_file = f"logs/vnpy_{datetime.now().strftime('%Y%m%d')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
```

### 13.4 异常处理

```python
try:
    # 连接网关
    main_engine.connect(setting, gateway_name)

except Exception as e:
    logging.error(f"连接失败: {e}")
    # 处理异常
```

### 13.5 性能优化

```python
# 使用缓存
from functools import lru_cache

@lru_cache(maxsize=128)
def get_contract(symbol):
    """缓存合约信息"""
    return oms_engine.get_contract(symbol)

# 批量处理
bars = []
for bar in bar_data_list:
    bars.append(bar)
database.save_bar_data(bars)  # 批量保存
```

### 13.6 安全建议

1. **密码加密**
   - 不要在代码中硬编码密码
   - 使用环境变量或配置文件

2. **权限控制**
   - 限制API访问权限
   - 使用专用的交易账号

3. **数据备份**
   - 定期备份数据库
   - 备份配置文件

4. **风险控制**
   - 设置止损止盈
   - 限制最大持仓
   - 限制最大亏损

---

## 附录

### A. 完整示例

```python
#!/usr/bin/env python3
"""VnPy完整示例"""

from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.object import BarData, OrderRequest, SubscribeRequest
from vnpy.trader.constant import Interval, Exchange, Direction, Offset, OrderType
from vnpy.trader.event import EVENT_TICK, EVENT_BAR, EVENT_LOG
from vnpy.trader.database import get_database
from vnpy_ctp.gateway import CtpGateway
from vnpy_ctastrategy import CtaEngine
from vnpy_ctastrategy.template import CtaTemplate
import time

# 1. 创建引擎
event_engine = EventEngine()
main_engine = MainEngine(event_engine)

# 2. 添加网关
main_engine.add_gateway(CtpGateway, gateway_name="CTP")

# 3. 连接
gateway_setting = {
    "用户名": "17130",
    "密码": "123456",
    "经纪商代码": "9999",
    "交易服务器": "tcp://trading.openctp.cn:30001",
    "行情服务器": "tcp://trading.openctp.cn:30011",
    "产品名称": "",
    "授权编码": "",
    "柜台环境": "测试"
}
main_engine.connect(gateway_setting, "CTP")

# 4. 等待连接
time.sleep(5)

# 5. 查询账户
oms_engine = main_engine.get_engine("oms")
accounts = oms_engine.get_all_accounts()
for account in accounts:
    print(f"余额: {account.balance:,.2f}")

# 6. 订阅行情
contracts = oms_engine.get_all_contracts()
for contract in contracts[:10]:
    req = SubscribeRequest(
        symbol=contract.symbol,
        exchange=contract.exchange
    )
    main_engine.subscribe(req, "CTP")

# 7. 运行策略
cta_engine = main_engine.add_engine(CtaEngine)
cta_engine.init_engine()
# ... 添加策略

# 8. 保持运行
while True:
    time.sleep(1)
```

### B. 资源链接

- **VnPy官网**: https://www.vnpy.com
- **VnPy文档**: https://docs.vnpy.com
- **VnPy社区**: https://www.vnpy.com/forum
- **OpenCTP**: http://openctp.cn
- **SimNow**: http://www.simnow.com.cn

### C. 版本历史

- **VnPy 3.0** (2024): 重构架构，支持异步
- **VnPy 2.0** (2019): 功能完善，多网关支持
- **VnPy 1.0** (2015): 初始版本

---

**文档结束**

如有问题，请访问: https://www.vnpy.com/forum
