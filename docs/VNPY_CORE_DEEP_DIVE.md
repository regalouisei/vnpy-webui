# VnPy 核心架构深度解析

**模块**: vnpy (核心)
**版本**: VnPy 3.x
**更新时间**: 2026-02-20
**难度**: ⭐⭐⭐⭐⭐

---

## 目录

1. [架构概述](#1-架构概述)
2. [事件驱动引擎](#2-事件驱动引擎)
3. [主引擎 MainEngine](#3-主引擎-mainengine)
4. [订单管理系统 OmsEngine](#4-订单管理系统-omsengine)
5. [核心对象模型](#5-核心对象模型)
6. [事件系统](#6-事件系统)
7. [网关系统](#7-网关系统)
8. [配置管理](#8-配置管理)
9. [性能优化](#9-性能优化)
10. [最佳实践](#10-最佳实践)

---

## 1. 架构概述

### 1.1 设计理念

VnPy 采用**事件驱动架构**（Event-Driven Architecture），这是整个系统的基础。

**核心思想**:
- **解耦**: 各模块通过事件通信，降低耦合度
- **异步**: 事件处理是非阻塞的，提高并发能力
- **可扩展**: 新功能通过事件监听器添加，无需修改核心代码

### 1.2 架构层次

```
┌─────────────────────────────────────────────┐
│          应用层 (Application Layer)          │
│   (策略、脚本、Web UI、CLI 等)                │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│          引擎层 (Engine Layer)               │
│   ┌─────────────┐  ┌─────────────┐          │
│   │ MainEngine  │  │ CtaEngine   │          │
│   │   (核心)     │  │  (策略)     │          │
│   └─────────────┘  └─────────────┘          │
│   ┌─────────────┐  ┌─────────────┐          │
│   │ OmsEngine   │  │ Backtesting │          │
│   │  (订单管理)  │  │  (回测)     │          │
│   └─────────────┘  └─────────────┘          │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│         网关层 (Gateway Layer)              │
│   ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐     │
│   │ CTP  │ │ IB   │ │ BNB  │ │ ...  │     │
│   └──────┘ └──────┘ └──────┘ └──────┘     │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│         数据层 (Data Layer)                 │
│   ┌───────┐ ┌───────┐ ┌───────┐           │
│   │SQLite │ │ MySQL │ │  PG   │           │
│   └───────┘ └───────┘ └───────┘           │
└─────────────────────────────────────────────┘
```

### 1.3 核心模块

| 模块 | 路径 | 职责 |
|------|------|------|
| **EventEngine** | `vnpy.event` | 事件驱动引擎 |
| **MainEngine** | `vnpy.trader.engine` | 主引擎，协调所有功能 |
| **OmsEngine** | `vnpy.trader.object` | 订单管理系统 |
| **Object** | `vnpy.trader.object` | 数据对象模型 |
| **Constant** | `vnpy.trader.constant` | 常量定义 |
| **Setting** | `vnpy.trader.setting` | 配置管理 |

---

## 2. 事件驱动引擎

### 2.1 EventEngine 原理

**核心功能**:
- 事件注册和分发
- 定时器管理
- 线程安全的事件队列

**源码分析**:

```python
class EventEngine:
    """事件驱动引擎"""

    def __init__(self):
        """初始化"""
        self._active = False
        self._thread = threading.Thread(target=self._run)
        self._queue = Queue()           # 事件队列
        self._handlers: defaultdict = defaultdict(list)  # 事件处理器
        self._timer = threading.Thread(target=self._run_timer)  # 定时器线程
        self._active = True
        self._thread.start()
        self._timer.start()
```

**工作流程**:
1. **注册事件处理器**: `event_engine.register(EVENT_TYPE, callback)`
2. **发布事件**: `event_engine.put(Event(EVENT_TYPE, data))`
3. **事件分发**: EventEngine 从队列取出事件，调用对应的处理器
4. **定时器触发**: 每 1 秒触发 `EVENT_TIMER` 事件

### 2.2 事件类型定义

所有事件定义在 `vnpy.trader.event`:

```python
# 基础事件
EVENT_TICK = "eTick"                    # Tick 行情
EVENT_TRADE = "eTrade"                  # 成交回报
EVENT_ORDER = "eOrder"                  # 订单状态
EVENT_POSITION = "ePosition"            # 持仓变动
EVENT_ACCOUNT = "eAccount"              # 账户变动
EVENT_CONTRACT = "eContract"            # 合约信息

# 系统事件
EVENT_LOG = "eLog"                      # 日志
EVENT_TIMER = "eTimer"                  # 定时器
EVENT_ENGINE = "eEngine"                # 引擎状态
```

### 2.3 事件处理器最佳实践

```python
# ✅ 正确: 使用弱引用
from weakref import WeakMethod

class Strategy:
    def __init__(self, event_engine):
        self.event_engine = event_engine
        # 使用 WeakMethod 防止内存泄漏
        self.event_engine.register(EVENT_TICK, WeakMethod(self.on_tick))

    def on_tick(self, event):
        tick = event.data
        # 处理 tick
        pass

# ❌ 错误: 直接绑定方法会导致内存泄漏
class BadStrategy:
    def __init__(self, event_engine):
        self.event_engine = event_engine
        self.event_engine.register(EVENT_TICK, self.on_tick)  # 内存泄漏!
```

---

## 3. 主引擎 MainEngine

### 3.1 MainEngine 职责

**MainEngine 是 VnPy 的核心协调器**，负责:

1. **网关管理**: 添加/删除/连接网关
2. **订单管理**: 下单/撤单/查询
3. **行情管理**: 订阅/取消订阅
4. **数据查询**: 账户/持仓/合约/订单/成交
5. **引擎管理**: 添加/删除子引擎（CtaEngine、OmsEngine 等）

### 3.2 MainEngine 初始化

```python
from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine

# 创建事件引擎
event_engine = EventEngine()

# 创建主引擎
main_engine = MainEngine(event_engine)

# MainEngine 内部会自动:
# 1. 注册系统事件处理器
# 2. 创建 OmsEngine (订单管理系统)
# 3. 初始化数据结构
```

### 3.3 网关管理

#### 添加网关

```python
from vnpy_ctp.gateway import CtpGateway

# 添加 CTP 网关
main_engine.add_gateway(CtpGateway, gateway_name="CTP")
```

**源码分析**:

```python
def add_gateway(self, gateway_class: Type[BaseGateway], gateway_name: str):
    """添加网关"""
    # 创建网关实例
    gateway = gateway_class(self, gateway_name)

    # 注册事件处理器
    self.event_engine.register(EVENT_TICK, gateway.on_tick)
    self.event_engine.register(EVENT_TRADE, gateway.on_trade)
    self.event_engine.register(EVENT_ORDER, gateway.on_order)
    # ... 更多事件

    # 添加到网关字典
    self.gateways[gateway_name] = gateway

    return gateway
```

#### 连接网关

```python
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
```

#### 获取网关

```python
gateway = main_engine.get_gateway("CTP")
```

### 3.4 订单管理

#### 下单

```python
from vnpy.trader.object import OrderRequest
from vnpy.trader.constant import Direction, Offset, OrderType

# 创建订单请求
req = OrderRequest(
    symbol="IF2602",
    exchange=Exchange.CFFEX,
    direction=Direction.LONG,      # 买入
    type=OrderType.LIMIT,          # 限价单
    volume=1,                       # 手数
    price=4000.0,                   # 价格
    offset=Offset.OPEN,             # 开仓
    reference="TEST001"             # 自定义引用
)

# 发送订单
orderid = main_engine.send_order(req, "CTP")
```

**源码分析**:

```python
def send_order(self, req: OrderRequest, gateway_name: str):
    """发送订单"""
    gateway = self.get_gateway(gateway_name)
    if not gateway:
        return ""

    # 生成订单 ID (本地唯一)
    orderid = self.orderid_generator.generate()

    # 创建订单对象
    order = req.create_order_data(orderid, gateway_name)

    # 添加到 OmsEngine
    self.oms_engine.add_order(order)

    # 发送到网关
    gateway.send_order(req, orderid)

    return orderid
```

#### 撤单

```python
from vnpy.trader.object import CancelRequest

cancel_req = CancelRequest(
    orderid=orderid,
    symbol="IF2602",
    exchange=Exchange.CFFEX
)

main_engine.cancel_order(cancel_req, "CTP")
```

### 3.5 行情管理

#### 订阅行情

```python
from vnpy.trader.object import SubscribeRequest

req = SubscribeRequest(
    symbol="IF2602",
    exchange=Exchange.CFFEX
)

main_engine.subscribe(req, "CTP")
```

#### 监听行情

```python
from vnpy.trader.event import EVENT_TICK

def on_tick(event):
    tick = event.data
    print(f"Tick: {tick.symbol} {tick.last_price}")

event_engine.register(EVENT_TICK, on_tick)
```

### 3.6 数据查询

#### 查询账户

```python
# ✅ 推荐: 从 OmsEngine 直接获取
oms_engine = main_engine.get_engine("oms")
accounts = oms_engine.get_all_accounts()

for account in accounts:
    print(f"账号: {account.accountid}")
    print(f"余额: {account.balance}")
    print(f"可用: {account.available}")
```

**性能优化**:

```python
# ❌ 错误: 每次都手动查询（慢）
gateway = main_engine.get_gateway("CTP")
gateway.query_account()
time.sleep(5)  # 等待响应
accounts = oms_engine.get_all_accounts()

# ✅ 正确: 直接从缓存获取（快）
accounts = oms_engine.get_all_accounts()
```

#### 查询持仓

```python
positions = oms_engine.get_all_positions()

for position in positions:
    print(f"合约: {position.symbol}")
    print(f"方向: {position.direction.value}")
    print(f"数量: {position.volume}")
    print(f"可用: {position.available}")
    print(f"盈亏: {position.pnl}")
```

#### 查询合约

```python
contracts = oms_engine.get_all_contracts()

for contract in contracts:
    print(f"合约: {contract.symbol}")
    print(f"名称: {contract.name}")
    print(f"交易所: {contract.exchange.value}")
    print(f"最小价位: {contract.pricetick}")
    print(f"合约乘数: {contract.size}")
```

#### 查询订单

```python
orders = oms_engine.get_all_orders()

for order in orders:
    print(f"订单: {order.orderid}")
    print(f"状态: {order.status.value}")
    print(f"成交: {order.traded}/{order.volume}")
```

#### 查询成交

```python
trades = oms_engine.get_all_trades()

for trade in trades:
    print(f"成交: {trade.tradeid}")
    print(f"价格: {trade.price}")
    print(f"数量: {trade.volume}")
```

---

## 4. 订单管理系统 OmsEngine

### 4.1 OmsEngine 职责

**OmsEngine (Order Management System Engine)** 负责:

1. **订单状态管理**: 维护所有订单的最新状态
2. **成交记录**: 记录所有成交
3. **账户管理**: 维护账户资金信息
4. **持仓管理**: 维护持仓信息
5. **合约管理**: 缓存合约信息

### 4.2 数据缓存机制

**OmsEngine 使用内存缓存**，所有数据都缓存在内存中:

```python
class OmsEngine(BaseEngine):
    """订单管理系统"""

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine):
        super().__init__(main_engine, event_engine, "oms")

        # 内存缓存
        self.accounts: Dict[str, AccountData] = {}  # 账户缓存
        self.positions: Dict[str, PositionData] = {}  # 持仓缓存
        self.contracts: Dict[str, ContractData] = {}  # 合约缓存
        self.orders: Dict[str, OrderData] = {}  # 订单缓存
        self.trades: Dict[str, TradeData] = {}  # 成交缓存

        # 订单 ID 生成器
        self.orderid_generator: OrderIdGenerator = OrderIdGenerator()
```

### 4.3 账户管理

#### 账户数据结构

```python
@dataclass
class AccountData(BaseData):
    """账户数据"""

    accountid: str                      # 账号
    balance: float                      # 余额
    available: float                    # 可用资金

    frozen: float = 0.0                 # 冻结资金
    currency: str = "CNY"               # 币种

    # 每日统计
    pre_balance: float = 0.0            # 昨日余额
    settlement_price: float = 0.0      # 结算价
    close_profit: float = 0.0           # 平仓盈亏
    position_profit: float = 0.0        # 持仓盈亏
    commission: float = 0.0             # 手续费
```

#### 账户事件处理

```python
def on_event(self, event):
    """事件处理"""
    if event.type == EVENT_ACCOUNT:
        self.on_account(event.data)
    # ... 其他事件

def on_account(self, account: AccountData):
    """账户事件"""
    # 更新缓存
    self.accounts[account.accountid] = account

    # 广播事件
    self.event_engine.put(Event(EVENT_ACCOUNT, account))
```

### 4.4 持仓管理

#### 持仓数据结构

```python
@dataclass
class PositionData(BaseData):
    """持仓数据"""

    symbol: str                         # 合约代码
    exchange: Exchange                  # 交易所
    direction: Direction                # 方向

    # 数量
    volume: int = 0                     # 持仓量
    frozen: int = 0                     # 冻结量
    available: int = 0                 # 可用量
    volume_today: int = 0              # 今仓
    volume_ytd: int = 0                 # 昨仓

    # 价格
    open_price: float = 0.0             # 开仓价
    price: float = 0.0                  # 最新价
    pnl: float = 0.0                    # 盈亏
    yd_pnl: float = 0.0                 # 昨日盈亏
    unrealized_pnl: float = 0.0         # 浮动盈亏

    # 其他
    leverage: float = 1.0               # 杠杆
    margin: float = 0.0                 # 占用保证金
```

#### 持仓计算逻辑

**OmsEngine 会自动计算持仓盈亏**:

```python
def update_position(self, position: PositionData):
    """更新持仓"""
    # 获取最新价
    tick = self.get_tick(position.symbol)
    if not tick:
        return

    # 计算浮动盈亏
    if position.direction == Direction.LONG:
        # 多头: (最新价 - 开仓价) * 持仓量 * 合约乘数
        position.unrealized_pnl = (
            (tick.last_price - position.open_price)
            * position.volume
            * self.get_contract_size(position.symbol)
        )
    else:
        # 空头: (开仓价 - 最新价) * 持仓量 * 合约乘数
        position.unrealized_pnl = (
            (position.open_price - tick.last_price)
            * position.volume
            * self.get_contract_size(position.symbol)
        )

    # 计算总盈亏
    position.pnl = position.close_profit + position.unrealized_pnl
```

### 4.5 订单管理

#### 订单数据结构

```python
@dataclass
class OrderData(BaseData):
    """订单数据"""

    orderid: str                        # 订单 ID
    symbol: str                         # 合约代码
    exchange: Exchange                  # 交易所

    # 订单信息
    direction: Direction                # 方向
    offset: Offset                      # 开平
    type: OrderType                     # 订单类型
    volume: int                         # 数量
    traded: int = 0                    # 已成交数量
    price: float = 0.0                  # 价格

    # 状态
    status: Status = Status.NOTTRADED   # 状态
    time: str = ""                      # 创建时间
    reference: str = ""                 # 自定义引用

    # 其他
    frontid: str = ""                   # 前置 ID
    sessionid: str = ""                 # 会话 ID
```

#### 订单状态流转

```
NOTTRADED (未成交)
    ↓
PARTTRADED (部分成交)
    ↓
ALLTRADED (全部成交)

NOTTRADED (未成交)
    ↓
CANCELLED (已撤销)
```

### 4.6 合约管理

#### 合约数据结构

```python
@dataclass
class ContractData(BaseData):
    """合约数据"""

    symbol: str                         # 合约代码
    exchange: Exchange                  # 交易所
    name: str                           # 合约名称

    # 合约属性
    product: Product                    # 产品类型
    size: int                           # 合约乘数
    pricetick: float                    # 最小价位

    # 交易时间
    min_volume: int = 1                 # 最小下单量
    strike_price: float = 0.0           # 执行价 (期权)
    underlying_symbol: str = ""         # 标的代码 (期权)

    # 其他
    list_date: str = ""                 # 上市日期
    expire_date: str = ""                # 到期日期
    option_portfolio: str = ""           # 期权组合
    option_type: OptionType = None      # 期权类型
```

---

## 5. 核心对象模型

### 5.1 数据对象继承体系

```
BaseData (基础数据)
├── BarData (K线数据)
├── TickData (Tick数据)
├── OrderData (订单数据)
├── TradeData (成交数据)
├── PositionData (持仓数据)
├── AccountData (账户数据)
├── ContractData (合约数据)
└── ...
```

### 5.2 BarData (K线数据)

```python
@dataclass
class BarData(BaseData):
    """K线数据"""

    symbol: str                         # 合约代码
    exchange: Exchange                  # 交易所
    interval: Interval                  # 周期
    datetime: datetime                  # 时间

    # OHLCV
    open_price: float                   # 开盘价
    high_price: float                   # 最高价
    low_price: float                    # 最低价
    close_price: float                  # 收盘价
    volume: float                       # 成交量
    turnover: float = 0.0               # 成交额

    # 持仓
    open_interest: float = 0.0          # 持仓量

    # 其他
    gateway_name: str = ""              # 网关名称
```

**使用示例**:

```python
from vnpy.trader.object import BarData
from vnpy.trader.constant import Interval, Exchange

# 创建 1 分钟 K 线
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
    gateway_name="CTP"
)
```

### 5.3 TickData (Tick数据)

```python
@dataclass
class TickData(BaseData):
    """Tick 数据"""

    symbol: str                         # 合约代码
    exchange: Exchange                  # 交易所
    datetime: datetime                  # 时间

    # 最新价
    last_price: float                   # 最新价
    last_volume: float                  # 成交量
    open_interest: float               # 持仓量

    # 卖一
    ask_price_1: float = 0.0            # 卖一价
    ask_volume_1: float = 0.0           # 卖一量

    # 卖二
    ask_price_2: float = 0.0
    ask_volume_2: float = 0.0

    # ... 卖三、四、五

    # 买一
    bid_price_1: float = 0.0            # 买一价
    bid_volume_1: float = 0.0           # 买一量

    # 买二
    bid_price_2: float = 0.0
    bid_volume_2: float = 0.0

    # ... 买三、四、五

    # 其他
    gateway_name: str = ""              # 网关名称
```

**使用示例**:

```python
def on_tick(event):
    tick = event.data

    # 计算买卖价差
    spread = tick.ask_price_1 - tick.bid_price_1

    # 计算买卖不平衡
    imbalance = tick.bid_volume_1 / (tick.ask_volume_1 + 1)

    # 决策
    if imbalance > 2.0:
        print("买方力量强")
```

---

## 6. 事件系统

### 6.1 事件数据结构

```python
@dataclass
class Event:
    """事件"""

    type: str                           # 事件类型
    data: Any                           # 事件数据
    source: str = ""                    # 事件源
```

### 6.2 事件注册

```python
# 注册单个处理器
event_engine.register(EVENT_TICK, on_tick)

# 注册多个处理器
event_engine.register(EVENT_TICK, on_tick_handler_1)
event_engine.register(EVENT_TICK, on_tick_handler_2)

# 取消注册
event_engine.unregister(EVENT_TICK, on_tick)
```

### 6.3 事件发布

```python
# 发布事件
event_engine.put(Event(EVENT_TICK, tick))

# 发布自定义事件
event_engine.put(Event("MY_EVENT", custom_data))
```

### 6.4 事件处理流程

```
1. 网关收到数据
   ↓
2. 网关处理数据，创建对象
   ↓
3. 网关发布事件
   event_engine.put(Event(EVENT_TICK, tick))
   ↓
4. EventEngine 从队列取出事件
   ↓
5. 查找事件处理器
   handlers = self._handlers[EVENT_TICK]
   ↓
6. 调用所有处理器
   for handler in handlers:
       handler(event)
   ↓
7. MainEngine/OmsEngine 接收事件
   ↓
8. 更新缓存
   ↓
9. 广播给其他监听器
```

---

## 7. 网关系统

### 7.1 网关职责

**网关 (Gateway)** 负责:

1. **连接管理**: 连接/断开交易所接口
2. **数据转换**: 将交易所数据转换为 VnPy 对象
3. **指令发送**: 发送订单/查询请求到交易所
4. **事件发布**: 将交易所数据发布为事件

### 7.2 网关类型

| 网关 | 模块 | 支持市场 |
|------|------|---------|
| **CTP** | `vnpy_ctp` | 国内期货 |
| **IB** | `vnpy_ib` | 全球期货/股票 |
| **Binance** | `vnpy_binance` | 数字货币 |
| **OKX** | `vnpy_okx` | 数字货币 |

### 7.3 网关接口

所有网关必须实现 `BaseGateway` 接口:

```python
class BaseGateway(ABC):
    """网关基类"""

    def __init__(self, main_engine: MainEngine, gateway_name: str):
        self.main_engine = main_engine
        self.gateway_name = gateway_name

    @abstractmethod
    def connect(self, setting: dict):
        """连接"""
        pass

    @abstractmethod
    def send_order(self, req: OrderRequest, orderid: str):
        """发送订单"""
        pass

    @abstractmethod
    def cancel_order(self, req: CancelRequest):
        """撤销订单"""
        pass

    @abstractmethod
    def subscribe(self, req: SubscribeRequest):
        """订阅行情"""
        pass

    # ... 更多抽象方法
```

### 7.4 CTP 网关详解

#### CTP 网关架构

```
CtpGateway
├── CtpTdApi (交易 API)
│   ├── onFrontConnected()         # 前置连接
│   ├── onRspUserLogin()           # 登录响应
│   ├── onRspOrderInsert()         # 报单响应
│   ├── onRtnTrade()               # 成交回报
│   └── ...
│
└── CtpMdApi (行情 API)
    ├── onFrontConnected()         # 前置连接
    ├── onRspUserLogin()           # 登录响应
    ├── onRtnDepthMarketData()      # 行情回报
    └── ...
```

#### CTP 网关连接流程

```python
# 1. 连接请求
main_engine.connect(gateway_setting, "CTP")

# 2. CtpGateway.connect()
#   ├─ CtpTdApi.connect()          # 连接交易服务器
#   └─ CtpMdApi.connect()          # 连级行情服务器

# 3. CTP API 回调
#   ├─ onFrontConnected()          # 连接成功
#   ├─ onRspUserLogin()            # 登录成功
#   └─ ...

# 4. CtpGateway 发布事件
#   ├─ event_engine.put(Event(EVENT_LOG, log))
#   └─ ...

# 5. MainEngine 接收事件
#   ├─ OmsEngine 更新缓存
#   └─ ...
```

#### CTP 网关自动查询

**CTP 网关有定时查询机制**:

```python
def init_query(self):
    """初始化查询任务"""
    self.query_functions: list = [
        self.query_account,    # 查询账户
        self.query_position    # 查询持仓
    ]
    self.event_engine.register(EVENT_TIMER, self.process_timer_event)

def process_timer_event(self, event: Event):
    """定时事件处理"""
    self.count += 1
    if self.count < 2:
        return
    self.count = 0

    # 循环执行查询
    func = self.query_functions.pop(0)
    func()
    self.query_functions.append(func)
```

**查询频率**: 每 2 秒循环查询一次账户和持仓

---

## 8. 配置管理

### 8.1 配置文件位置

**默认位置**: `~/.vntrader/`

### 8.2 配置文件

#### vt_setting.json (主配置)

```json
{
  "database": {
    "database": "sqlite",
    "database.db_path": "~/.vntrader/database.db"
  }
}
```

#### ctp_setting.json (CTP 配置)

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

### 8.3 配置读取

```python
from vnpy.trader.setting import SETTINGS

# 读取配置
db_type = SETTINGS["database"]["database"]
db_path = SETTINGS["database"]["database.db_path"]

# 修改配置
SETTINGS["database"]["database"] = "mysql"
SETTINGS.save()
```

---

## 9. 性能优化

### 9.1 账户查询优化

**问题**: 每次查询需要 4-5 秒

**原因**: 错误地每次都手动调用 `query_account()`

**解决方案**:

```python
# ❌ 错误: 每次都手动查询
gateway.query_account()
time.sleep(5)
account = oms_engine.get_all_accounts()[0]

# ✅ 正确: 直接从缓存获取
account = oms_engine.get_all_accounts()[0]
```

**效果**: 从 4.92 秒优化到 0.00 秒

### 9.2 事件处理器优化

**使用弱引用防止内存泄漏**:

```python
from weakref import WeakMethod

class Strategy:
    def __init__(self, event_engine):
        self.event_engine = event_engine
        # 使用 WeakMethod
        self.event_engine.register(EVENT_TICK, WeakMethod(self.on_tick))
```

### 9.3 批量操作优化

```python
# ✅ 批量保存
bars = []
for bar in bar_data_list:
    bars.append(bar)
database.save_bar_data(bars)  # 一次保存

# ❌ 单条保存
for bar in bar_data_list:
    database.save_bar_data(bar)  # 多次保存，慢
```

---

## 10. 最佳实践

### 10.1 代码结构

```
project/
├── strategies/           # 策略目录
│   ├── __init__.py
│   ├── my_strategy.py
│   └── ...
├── data/                # 数据目录
├── logs/                # 日志目录
├── config/              # 配置目录
└── main.py             # 主程序
```

### 10.2 错误处理

```python
try:
    main_engine.connect(gateway_setting, "CTP")
except Exception as e:
    logging.error(f"连接失败: {e}")
    # 处理异常
```

### 10.3 日志管理

```python
import logging
from datetime import datetime

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

### 10.4 安全建议

1. **密码加密**: 不要在代码中硬编码密码
2. **权限控制**: 限制 API 访问权限
3. **数据备份**: 定期备份数据库
4. **风险控制**: 设置止损止盈

---

## 附录

### A. 完整示例

```python
#!/usr/bin/env python3
"""VnPy 核心功能完整示例"""

from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.object import SubscribeRequest
from vnpy.trader.event import EVENT_TICK, EVENT_ACCOUNT
from vnpy_ctp.gateway import CtpGateway
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
time.sleep(5)

# 4. 监听账户
def on_account(event):
    account = event.data
    print(f"账户: {account.accountid} 余额: {account.balance}")

event_engine.register(EVENT_ACCOUNT, on_account)

# 5. 监听行情
def on_tick(event):
    tick = event.data
    print(f"行情: {tick.symbol} 价格: {tick.last_price}")

event_engine.register(EVENT_TICK, on_tick)

# 6. 订阅行情
oms_engine = main_engine.get_engine("oms")
contracts = oms_engine.get_all_contracts()
for contract in contracts[:10]:
    req = SubscribeRequest(
        symbol=contract.symbol,
        exchange=contract.exchange
    )
    main_engine.subscribe(req, "CTP")

# 7. 保持运行
while True:
    time.sleep(1)
```

### B. 资源链接

- **VnPy 文档**: https://docs.vnpy.com
- **VnPy 源码**: https://github.com/vnpy/vnpy
- **OpenCTP**: http://openctp.cn

---

**文档结束**
