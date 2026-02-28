# vn.py 脚本策略系统深度解析

**版本**: vn.py 3.x
**文档版本**: 1.0
**更新时间**: 2026-02-20
**作者**: Quant Factory

---

## 目录

1. [脚本策略的基本概念和优势](#1-脚本策略的基本概念和优势)
2. [vn.py 脚本策略系统的架构概述](#2-vnpy-脚本策略系统的架构概述)
3. [脚本语言和语法](#3-脚本语言和语法)
4. [脚本加载和执行机制](#4-脚本加载和执行机制)
5. [脚本与策略的交互](#5-脚本与策略的交互)
6. [错误处理和调试](#6-错误处理和调试)
7. [性能优化技巧](#7-性能优化技巧)
8. [最佳实践建议](#8-最佳实践建议)
9. [完整的脚本示例](#9-完整的脚本示例)
10. [配置和使用方法](#10-配置和使用方法)

---

## 1. 脚本策略的基本概念和优势

### 1.1 什么是脚本策略

脚本策略（Script Strategy）是 vn.py 提供的一种轻量级策略开发方式，允许用户直接使用 Python 脚本编写交易逻辑，无需创建完整的策略类。相比传统的 CTA 策略类开发方式，脚本策略具有以下特点：

**核心特点：**
- **直接编写**：无需继承策略模板类
- **即时执行**：脚本加载后立即运行
- **灵活调整**：可以随时修改脚本逻辑
- **快速测试**：适合快速验证策略思路

**对比 CTA 策略：**

| 特性 | CTA 策略 | 脚本策略 |
|------|---------|---------|
| 开发方式 | 继承策略类 | 直接编写脚本 |
| 代码结构 | 面向对象 | 函数式 |
| 加载方式 | 类注册 | 脚本文件导入 |
| 适用场景 | 复杂策略 | 简单策略、快速测试 |
| 持久化 | 配置文件 | 脚本文件 |
| 热更新 | 需重启 | 支持动态加载 |

### 1.2 脚本策略的优势

**1. 快速原型开发**

```python
# 快速验证一个简单的均线策略
def on_bar(bar):
    ma5 = calculate_ma(5)
    ma20 = calculate_ma(20)
    if ma5 > ma20 and pos == 0:
        buy(bar.close_price, 1)
```

**2. 灵活的实验环境**

- 可以快速调整参数
- 无需重新编译或重启
- 支持多个脚本并行运行

**3. 适合特定场景**

- 日内交易策略
- 套利策略
- 监控和告警脚本
- 数据分析脚本

**4. 降低学习门槛**

- 无需理解面向对象编程
- 无需掌握策略生命周期
- 直接使用 Python 标准库

---

## 2. vn.py 脚本策略系统的架构概述

### 2.1 系统架构图

```
┌─────────────────────────────────────────────────────────┐
│                    vn.py 脚本策略系统                     │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│  ScriptEngine │  │  ScriptLoader │  │ ScriptManager │
│  脚本执行引擎  │  │  脚本加载器   │  │  脚本管理器   │
└───────┬───────┘  └───────┬───────┘  └───────┬───────┘
        │                  │                  │
        └───────────────────┼───────────────────┘
                           │
                           ▼
                  ┌───────────────┐
                  │  MainEngine   │
                  │   主引擎      │
                  └───────┬───────┘
                          │
                          ▼
                  ┌───────────────┐
                  │  EventEngine  │
                  │   事件引擎    │
                  └───────────────┘
```

### 2.2 核心组件

**1. ScriptEngine（脚本执行引擎）**

```python
class ScriptEngine(BaseEngine):
    """脚本执行引擎"""

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine):
        super().__init__(main_engine, event_engine, APP_NAME)

        # 脚本存储
        self.scripts: dict = {}              # 脚本字典
        self.script_contexts: dict = {}     # 脚本上下文

        # 策略引擎引用
        self.cta_engine: CtaEngine = main_engine.get_engine("cta")

        # 事件映射
        self.event_handlers: dict = {}      # 事件处理器映射

        # 执行状态
        self.running_scripts: set = set()   # 运行中的脚本
```

**2. ScriptLoader（脚本加载器）**

```python
class ScriptLoader:
    """脚本加载器"""

    def __init__(self, script_engine: ScriptEngine):
        self.engine: ScriptEngine = script_engine
        self.script_dir: Path = Path("strategies/scripts")

    def load_script(self, script_name: str) -> dict:
        """加载脚本文件"""
        script_path = self.script_dir / f"{script_name}.py"

        # 读取脚本内容
        with open(script_path, "r", encoding="utf-8") as f:
            script_content = f.read()

        # 解析脚本
        script_globals = {}
        exec(script_content, script_globals)

        return script_globals

    def load_scripts_from_dir(self, script_dir: str) -> List[str]:
        """从目录加载所有脚本"""
        script_dir = Path(script_dir)
        script_files = list(script_dir.glob("*.py"))

        loaded_scripts = []
        for script_file in script_files:
            script_name = script_file.stem
            self.load_script(script_name)
            loaded_scripts.append(script_name)

        return loaded_scripts
```

**3. ScriptManager（脚本管理器）**

```python
class ScriptManager:
    """脚本管理器"""

    def __init__(self, script_engine: ScriptEngine):
        self.engine: ScriptEngine = script_engine
        self.script_configs: dict = {}      # 脚本配置

    def add_script(
        self,
        script_name: str,
        script_file: str,
        vt_symbol: str = None,
        interval: Interval = None,
        auto_start: bool = True
    ) -> None:
        """添加脚本"""

        # 保存配置
        self.script_configs[script_name] = {
            "script_file": script_file,
            "vt_symbol": vt_symbol,
            "interval": interval,
            "auto_start": auto_start,
            "active": True
        }

    def remove_script(self, script_name: str) -> None:
        """移除脚本"""
        if script_name in self.script_configs:
            self.engine.stop_script(script_name)
            del self.script_configs[script_name]

    def start_script(self, script_name: str) -> None:
        """启动脚本"""
        if script_name in self.script_configs:
            config = self.script_configs[script_name]
            self.engine.run_script(
                script_name,
                config["script_file"],
                vt_symbol=config["vt_symbol"],
                interval=config["interval"]
            )

    def stop_script(self, script_name: str) -> None:
        """停止脚本"""
        self.engine.stop_script(script_name)

    def get_all_scripts(self) -> List[str]:
        """获取所有脚本列表"""
        return list(self.script_configs.keys())
```

### 2.3 脚本执行流程

```
┌─────────────┐
│  脚本文件    │ .py 文件
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  加载脚本    │ 读取内容
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  解析脚本    │ exec() 执行
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  创建上下文  │ 创建执行环境
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  注册事件    │ 订阅市场事件
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  执行脚本    │ 运行主逻辑
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  事件循环    │ 处理市场事件
└─────────────┘
```

---

## 3. 脚本语言和语法

### 3.1 脚本语言基础

vn.py 脚本策略使用标准 Python 语言，无需额外学习新的语法。脚本可以直接使用：

**1. Python 标准库**

```python
import math
import time
from datetime import datetime, timedelta

# 使用数学函数
sma = sum(prices) / len(prices)

# 使用时间函数
current_time = datetime.now()
next_day = current_time + timedelta(days=1)
```

**2. vn.py 核心对象**

```python
# 获取账户信息
account = get_account("simnow")
print(f"余额: {account.balance}")

# 获取合约信息
contract = get_contract("IF2401.CFFEX")
print(f"最小变动价: {contract.pricetick}")

# 获取持仓信息
position = get_position("IF2401.CFFEX")
print(f"持仓: {position.volume}")
```

**3. vn.py 交易函数**

```python
# 订单操作
buy(price, volume, symbol="IF2401.CFFEX")
sell(price, volume, symbol="IF2401.CFFEX")
short(price, volume, symbol="IF2401.CFFEX")
cover(price, volume, symbol="IF2401.CFFEX")

# 撤单
cancel_order(order_id)

# 查询
query_account()
query_position()
```

### 3.2 脚本语法结构

**基本结构：**

```python
# === 脚本配置 ===
SCRIPT_NAME = "my_script"
VT_SYMBOL = "IF2401.CFFEX"
INTERVAL = "1m"

# === 初始化函数 ===
def on_init():
    """脚本初始化"""
    print(f"{SCRIPT_NAME} 初始化")
    load_bar(days=20)

# === 启动函数 ===
def on_start():
    """脚本启动"""
    print(f"{SCRIPT_NAME} 启动")

# === 停止函数 ===
def on_stop():
    """脚本停止"""
    print(f"{SCRIPT_NAME} 停止")
    cancel_all()

# === Tick 事件 ===
def on_tick(tick):
    """处理 Tick 数据"""
    # 更新数据
    update_tick(tick)

# === Bar 事件 ===
def on_bar(bar):
    """处理 Bar 数据"""
    # 策略逻辑
    if ma5 > ma20 and pos == 0:
        buy(bar.close_price, 1)

# === 订单事件 ===
def on_order(order):
    """处理订单事件"""
    print(f"订单: {order.status}")

# === 成交事件 ===
def on_trade(trade):
    """处理成交事件"""
    print(f"成交: {trade.volume}@{trade.price}")
```

### 3.3 变量和数据管理

**全局变量：**

```python
# 策略参数
fast_window = 10
slow_window = 20
fixed_size = 1

# 技术指标
ma5 = 0.0
ma10 = 0.0
ma20 = 0.0
atr = 0.0

# 交易状态
pos = 0
entry_price = 0.0
stop_price = 0.0

# 数据容器
bars = []
prices = []
volumes = []
```

**数据管理：**

```python
# 使用 ArrayManager
from vnpy.trader.utility import ArrayManager

am = ArrayManager(size=100)

def on_bar(bar):
    am.update_bar(bar)

    if not am.inited:
        return

    # 计算指标
    ma5 = am.sma(5)
    ma20 = am.sma(20)
    atr = am.atr(14)
```

---

## 4. 脚本加载和执行机制

### 4.1 脚本加载流程

```python
def load_and_run_script(script_path: str, vt_symbol: str = None):
    """加载并运行脚本"""

    # 1. 读取脚本文件
    with open(script_path, "r", encoding="utf-8") as f:
        script_code = f.read()

    # 2. 创建执行上下文
    script_globals = {
        "__name__": "__main__",
        "__file__": script_path,
    }

    # 3. 注入 vn.py 对象和函数
    script_globals.update({
        # 核心对象
        "get_account": get_account,
        "get_position": get_position,
        "get_contract": get_contract,

        # 交易函数
        "buy": buy,
        "sell": sell,
        "short": short,
        "cover": cover,
        "cancel_order": cancel_order,
        "cancel_all": cancel_all,

        # 查询函数
        "query_account": query_account,
        "query_position": query_position,

        # 工具函数
        "load_bar": load_bar,
        "subscribe": subscribe,

        # 数据对象
        "BarData": BarData,
        "TickData": TickData,
        "OrderData": OrderData,
        "TradeData": TradeData,

        # 常量
        "Direction": Direction,
        "Offset": Offset,
        "Interval": Interval,
        "Status": Status,
    })

    # 4. 执行脚本
    exec(script_code, script_globals)

    # 5. 脚本初始化
    if "on_init" in script_globals:
        script_globals["on_init"]()

    # 6. 订阅行情
    if vt_symbol:
        subscribe(vt_symbol)

    # 7. 启动脚本
    if "on_start" in script_globals:
        script_globals["on_start"]()

    # 8. 保存脚本上下文
    script_name = Path(script_path).stem
    script_contexts[script_name] = script_globals

    # 9. 注册事件处理器
    if "on_tick" in script_globals:
        event_engine.register(EVENT_TICK, script_globals["on_tick"])

    if "on_bar" in script_globals:
        event_engine.register(EVENT_BAR, script_globals["on_bar"])

    if "on_order" in script_globals:
        event_engine.register(EVENT_ORDER, script_globals["on_order"])

    if "on_trade" in script_globals:
        event_engine.register(EVENT_TRADE, script_globals["on_trade"])

    print(f"脚本 {script_name} 加载成功")
```

### 4.2 脚本执行机制

**1. 事件驱动的执行**

```python
class ScriptExecutor:
    """脚本执行器"""

    def execute_script(self, script_name: str, event_type: str, data: Any):
        """执行脚本事件处理器"""

        # 获取脚本上下文
        context = self.script_contexts.get(script_name)
        if not context:
            return

        # 获取事件处理器
        handler = context.get(f"on_{event_type}")
        if not handler:
            return

        # 执行处理器
        try:
            handler(data)
        except Exception as e:
            print(f"脚本执行错误: {script_name} - {e}")
            traceback.print_exc()
```

**2. 定时任务执行**

```python
def setup_timer(interval: int = 60):
    """设置定时任务"""
    def timer_callback():
        if "on_timer" in script_globals:
            script_globals["on_timer"]()

    # 注册定时器
    event_engine.register(EVENT_TIMER, timer_callback)
    event_engine.start_timer(interval)
```

### 4.3 脚本热更新

```python
def reload_script(script_name: str):
    """热更新脚本"""

    # 1. 停止当前脚本
    if script_name in self.running_scripts:
        self.stop_script(script_name)

    # 2. 清理旧上下文
    if script_name in self.script_contexts:
        del self.script_contexts[script_name]

    # 3. 取消事件注册
    context = self.script_contexts.get(script_name, {})
    for event_type in ["tick", "bar", "order", "trade"]:
        handler = context.get(f"on_{event_type}")
        if handler:
            event_engine.unregister(
                getattr(EVENT, f"EVENT_{event_type.upper()}"),
                handler
            )

    # 4. 重新加载脚本
    script_config = self.script_configs.get(script_name)
    if script_config:
        self.run_script(
            script_name,
            script_config["script_file"],
            vt_symbol=script_config.get("vt_symbol"),
            interval=script_config.get("interval")
        )

    print(f"脚本 {script_name} 重新加载完成")
```

---

## 5. 脚本与策略的交互

### 5.1 脚本调用策略

```python
# 获取策略引擎
cta_engine = main_engine.get_engine("cta")

# 启动策略
cta_engine.start_strategy("my_strategy")

# 停止策略
cta_engine.stop_strategy("my_strategy")

# 获取策略状态
strategy = cta_engine.strategies.get("my_strategy")
print(f"策略状态: inited={strategy.inited}, trading={strategy.trading}")
```

### 5.2 策略调用脚本

```python
# 在策略中执行脚本
def execute_script_function(script_name: str, func_name: str, *args):
    """执行脚本函数"""
    context = script_engine.script_contexts.get(script_name)
    if not context:
        return None

    func = context.get(func_name)
    if not func:
        return None

    return func(*args)

# 在策略中使用
class MyStrategy(CtaTemplate):
    def on_bar(self, bar: BarData):
        # 调用脚本的信号生成函数
        signal = execute_script_function("signal_script", "generate_signal", bar)
        if signal == "BUY":
            self.buy(bar.close_price, 1)
```

### 5.3 共享数据

```python
# 全局数据存储
shared_data = {}

def script_a_set_data(key, value):
    """脚本 A 设置数据"""
    shared_data[key] = value

def script_b_get_data(key):
    """脚本 B 获取数据"""
    return shared_data.get(key)

# 使用示例
script_a_set_data("market_trend", "BULLISH")
trend = script_b_get_data("market_trend")
```

---

## 6. 错误处理和调试

### 6.1 错误处理机制

**1. 异常捕获**

```python
def safe_execute(func, *args, **kwargs):
    """安全执行函数"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        print(f"执行错误: {e}")
        traceback.print_exc()
        return None

# 使用
def on_bar(bar):
    result = safe_execute(calculate_signal, bar)
    if result:
        execute_trade(result)
```

**2. 错误回调**

```python
def on_error(error_msg: str):
    """错误回调函数"""
    print(f"脚本错误: {error_msg}")
    # 发送通知
    send_notification(f"脚本错误: {error_msg}")
    # 记录日志
    write_log(f"ERROR: {error_msg}")

# 注册错误处理
script_engine.set_error_handler(on_error)
```

### 6.2 调试技巧

**1. 日志输出**

```python
# 基础日志
def log(msg: str):
    """日志输出"""
    print(f"[{datetime.now()}] {msg}")

# 使用日志
def on_bar(bar):
    log(f"收盘价: {bar.close_price}")
    log(f"持仓: {pos}")

# 结构化日志
def log_structured(level: str, msg: str, data: dict = None):
    """结构化日志"""
    log_entry = {
        "time": datetime.now().isoformat(),
        "level": level,
        "message": msg,
        "data": data
    }
    print(json.dumps(log_entry, ensure_ascii=False))
```

**2. 调试模式**

```python
DEBUG = True

def debug_print(msg):
    """调试输出"""
    if DEBUG:
        print(f"[DEBUG] {msg}")

def on_bar(bar):
    debug_print(f"MA5: {ma5}, MA20: {ma20}")
    if ma5 > ma20 and pos == 0:
        debug_print("触发买入信号")
        buy(bar.close_price, 1)
```

**3. 数据快照**

```python
def save_snapshot(data: dict, filename: str):
    """保存数据快照"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = f"data/snapshots/{filename}_{timestamp}.json"

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)

    print(f"快照已保存: {filepath}")

# 使用
def on_bar(bar):
    if bar.datetime.time() == time(15, 0):  # 收盘
        snapshot = {
            "pos": pos,
            "entry_price": entry_price,
            "ma5": ma5,
            "ma20": ma20,
            "bars": [b.__dict__ for b in bars[-10:]]
        }
        save_snapshot(snapshot, "daily_close")
```

### 6.3 常见错误排查

**1. 导入错误**

```python
# ❌ 错误：脚本中导入不存在的模块
import non_existent_module

# ✅ 正确：检查模块是否存在
try:
    import pandas as pd
except ImportError:
    print("pandas 未安装，跳过 pandas 功能")
```

**2. 变量未定义**

```python
# ❌ 错误：使用未定义的变量
def on_bar(bar):
    buy(bar.close_price, undefined_variable)

# ✅ 正确：检查变量是否存在
def on_bar(bar):
    volume = globals().get("fixed_size", 1)
    if volume > 0:
        buy(bar.close_price, volume)
```

**3. 异常处理**

```python
# ❌ 错误：未捕获除零错误
def calculate_ratio(a, b):
    return a / b

# ✅ 正确：捕获异常
def calculate_ratio(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return 0
```

---

## 7. 性能优化技巧

### 7.1 计算优化

**1. 避免重复计算**

```python
# ❌ 错误：重复计算
def on_bar(bar):
    ma5 = sum(prices[-5:]) / 5
    ma10 = sum(prices[-10:]) / 10
    if ma5 > ma10:
        pass
    if ma5 < ma10:
        pass

# ✅ 正确：一次计算，多次使用
def on_bar(bar):
    ma5 = sum(prices[-5:]) / 5
    ma10 = sum(prices[-10:]) / 10
    signal = "BUY" if ma5 > ma10 else "SELL" if ma5 < ma10 else "HOLD"
    execute_trade(signal)
```

**2. 使用缓存**

```python
# 缓存计算结果
from functools import lru_cache

@lru_cache(maxsize=100)
def calculate_sma(period: int, index: int):
    """计算移动平均（带缓存）"""
    return sum(prices[index-period+1:index+1]) / period

def on_bar(bar):
    prices.append(bar.close_price)
    current_ma5 = calculate_sma(5, len(prices)-1)
```

### 7.2 数据结构优化

**1. 使用高效的数据结构**

```python
# ❌ 慢速：列表查找
def find_latest_order():
    for order in orders:
        if order.status == "ACTIVE":
            return order
    return None

# ✅ 快速：字典查找
orders_dict = {}  # order_id -> order

def find_latest_order():
    active_orders = [o for o in orders_dict.values() if o.status == "ACTIVE"]
    return active_orders[-1] if active_orders else None
```

**2. 预分配内存**

```python
# ❌ 动态扩容
data = []

def on_bar(bar):
    data.append(bar.close_price)

# ✅ 预分配
from collections import deque

data = deque(maxlen=1000)  # 固定大小

def on_bar(bar):
    data.append(bar.close_price)
```

### 7.3 批量处理优化

**1. 批量订单**

```python
# ❌ 单个订单
def open_positions(symbols, size):
    for symbol in symbols:
        price = get_current_price(symbol)
        buy(price, size, symbol=symbol)

# ✅ 批量订单
def open_positions_batch(symbols, size):
    orders = []
    for symbol in symbols:
        price = get_current_price(symbol)
        order = create_order("BUY", price, size, symbol)
        orders.append(order)

    # 批量发送
    send_orders(orders)
```

---

## 8. 最佳实践建议

### 8.1 代码组织

**1. 模块化设计**

```python
# === 配置模块 ===
CONFIG = {
    "fast_window": 10,
    "slow_window": 20,
    "fixed_size": 1,
    "stop_loss_multiplier": 2.0
}

# === 工具函数模块 ===
def calculate_ma(prices, period):
    """计算移动平均"""
    return sum(prices[-period:]) / period if len(prices) >= period else None

def calculate_atr(highs, lows, closes, period=14):
    """计算 ATR"""
    tr_list = []
    for i in range(1, len(closes)):
        tr = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i-1]),
            abs(lows[i] - closes[i-1])
        )
        tr_list.append(tr)
    return sum(tr_list[-period:]) / period if len(tr_list) >= period else None

# === 交易模块 ===
def execute_trade(signal, bar):
    """执行交易"""
    if signal == "BUY" and pos == 0:
        buy(bar.close_price, CONFIG["fixed_size"])
    elif signal == "SELL" and pos > 0:
        sell(bar.close_price, abs(pos))

# === 主逻辑模块 ===
def on_bar(bar):
    """主逻辑"""
    bars.append(bar.close_price)
    highs.append(bar.high_price)
    lows.append(bar.low_price)

    if len(bars) < CONFIG["slow_window"]:
        return

    ma5 = calculate_ma(bars, CONFIG["fast_window"])
    ma20 = calculate_ma(bars, CONFIG["slow_window"])

    signal = None
    if ma5 > ma20:
        signal = "BUY"
    elif ma5 < ma20:
        signal = "SELL"

    if signal:
        execute_trade(signal, bar)
```

**2. 注释规范**

```python
# === 脚本配置 ===
# 双均线突破策略配置
FAST_WINDOW = 10      # 快线周期
SLOW_WINDOW = 20      # 慢线周期
FIXED_SIZE = 1        # 固定下单手数

# === 初始化 ===
def on_init():
    """
    脚本初始化
    - 创建数据容器
    - 加载历史数据
    """
    global bars, highs, lows
    bars = []
    highs = []
    lows = []

    load_bar(days=SLOW_WINDOW * 2)
    print("脚本初始化完成")

# === Tick 事件 ===
def on_tick(tick):
    """
    Tick 事件处理
    - 更新止损价格
    - 检查止损触发
    """
    # 更新 K 线生成器
    bg.update_tick(tick)

    # 检查止损
    check_stop_loss(tick)
```

### 8.2 风险管理

**1. 仓位控制**

```python
MAX_POSITION_RATIO = 0.3  # 最大仓位比例
RISK_PER_TRADE = 0.02      # 每笔交易风险

def calculate_position_size(entry_price, stop_price):
    """根据风险计算仓位大小"""
    account = get_account()

    # 止损距离
    stop_distance = abs(entry_price - stop_price)

    # 风险金额
    risk_amount = account.balance * RISK_PER_TRADE

    # 仓位大小
    position_size = risk_amount / stop_distance

    # 限制最大仓位
    max_position = account.balance * MAX_POSITION_RATIO / entry_price
    position_size = min(position_size, max_position)

    return int(position_size)

def on_bar(bar):
    # ... 信号生成 ...

    if signal == "BUY" and pos == 0:
        stop_price = bar.close_price - atr * 2
        size = calculate_position_size(bar.close_price, stop_price)
        buy(bar.close_price, size)
```

**2. 止损止盈**

```python
def update_stop_loss(bar):
    """更新止损价格"""
    global stop_price, take_profit_price

    if pos > 0:  # 多仓
        # 止损
        stop_price = entry_price - atr * 2

        # 止盈
        take_profit_price = entry_price + atr * 3

        # 移动止损
        new_stop = bar.close_price - atr * 2
        if new_stop > stop_price:
            stop_price = new_stop

    elif pos < 0:  # 空仓
        # 止损
        stop_price = entry_price + atr * 2

        # 止盈
        take_profit_price = entry_price - atr * 3

        # 移动止损
        new_stop = bar.close_price + atr * 2
        if new_stop < stop_price:
            stop_price = new_stop

def on_tick(tick):
    """Tick 事件"""
    if pos > 0:
        if tick.last_price <= stop_price:
            sell(tick.ask_price_1, abs(pos))
        elif tick.last_price >= take_profit_price:
            sell(tick.ask_price_1, abs(pos))

    elif pos < 0:
        if tick.last_price >= stop_price:
            cover(tick.bid_price_1, abs(pos))
        elif tick.last_price <= take_profit_price:
            cover(tick.bid_price_1, abs(pos))
```

### 8.3 监控和告警

**1. 状态监控**

```python
def monitor_status():
    """监控脚本状态"""
    # 账户状态
    account = get_account()
    print(f"余额: {account.balance}, 可用: {account.available}")

    # 持仓状态
    positions = get_all_positions()
    for pos in positions:
        print(f"{pos.vt_symbol}: {pos.volume}, 盈亏: {pos.pnl}")

    # 订单状态
    orders = get_active_orders()
    print(f"挂单数量: {len(orders)}")

# 定时监控
def on_timer():
    monitor_status()
```

**2. 异常告警**

```python
def send_alert(message: str):
    """发送告警"""
    print(f"[ALERT] {message}")
    # 可以集成邮件、短信等通知方式

def on_bar(bar):
    # 检查异常情况
    if pos > 0 and bar.close_price < entry_price * 0.95:
        send_alert(f"多仓亏损超过5%: {VT_SYMBOL}")

    if len(active_orders) > 10:
        send_alert(f"挂单过多: {len(active_orders)}")
```

---

## 9. 完整的脚本示例

### 9.1 双均线策略脚本

```python
"""
双均线策略脚本
作者: Quant Factory
策略: 快线上穿慢线买入，下穿卖出
"""

# === 配置 ===
SCRIPT_NAME = "dual_ma_script"
VT_SYMBOL = "IF2401.CFFEX"
INTERVAL = "1m"

# 参数
FAST_WINDOW = 10
SLOW_WINDOW = 20
FIXED_SIZE = 1

# 变量
pos = 0
ma5 = 0.0
ma20 = 0.0
bars = []

# === 工具函数 ===
def calculate_ma(period):
    """计算移动平均"""
    if len(bars) < period:
        return None
    return sum(bars[-period:]) / period

# === 初始化 ===
def on_init():
    """脚本初始化"""
    print(f"[{SCRIPT_NAME}] 初始化")

    # 加载历史数据
    load_bar(days=SLOW_WINDOW * 2)

    print(f"[{SCRIPT_NAME}] 初始化完成")

# === 启动 ===
def on_start():
    """脚本启动"""
    print(f"[{SCRIPT_NAME}] 启动")
    print(f"配置: 快线={FAST_WINDOW}, 慢线={SLOW_WINDOW}, 手数={FIXED_SIZE}")

# === 停止 ===
def on_stop():
    """脚本停止"""
    print(f"[{SCRIPT_NAME}] 停止")
    cancel_all()

# === Tick 事件 ===
def on_tick(tick):
    """Tick 事件处理"""
    pass

# === Bar 事件 ===
def on_bar(bar):
    """Bar 事件处理"""
    global bars, ma5, ma20, pos

    # 更新数据
    bars.append(bar.close_price)
    if len(bars) > SLOW_WINDOW * 2:
        bars.pop(0)

    # 计算均线
    ma5 = calculate_ma(FAST_WINDOW)
    ma20 = calculate_ma(SLOW_WINDOW)

    if ma5 is None or ma20 is None:
        return

    # 判断交叉
    cross_over = (ma5 > ma20)
    cross_below = (ma5 < ma20)

    # 执行交易
    if cross_over and pos == 0:
        print(f"[{SCRIPT_NAME}] 金叉买入")
        buy(bar.close_price, FIXED_SIZE)
        pos = FIXED_SIZE

    elif cross_below and pos > 0:
        print(f"[{SCRIPT_NAME}] 死叉卖出")
        sell(bar.close_price, abs(pos))
        pos = 0

# === 订单事件 ===
def on_order(order):
    """订单事件处理"""
    print(f"[{SCRIPT_NAME}] 订单: {order.status}")

# === 成交事件 ===
def on_trade(trade):
    """成交事件处理"""
    global pos, entry_price

    print(f"[{SCRIPT_NAME}] 成交: {trade.direction} {trade.volume}@{trade.price:.2f}")

    # 更新持仓
    if trade.direction == Direction.LONG:
        pos += trade.volume
    else:
        pos -= trade.volume

    # 记录入场价格
    if pos != 0:
        entry_price = trade.price
```

### 9.2 带止损的突破策略脚本

```python
"""
带止损的突破策略脚本
作者: Quant Factory
策略: 价格突破开盘价开仓，ATR 止损
"""

# === 配置 ===
SCRIPT_NAME = "breakout_script"
VT_SYMBOL = "IF2401.CFFEX"
INTERVAL = "5m"

# 参数
BREAKOUT_RATIO = 0.002  # 突破比例
ATR_WINDOW = 14
ATR_MULTIPLIER = 2.0
FIXED_SIZE = 1

# 变量
pos = 0
day_open = 0.0
day_high = 0.0
day_low = 0.0
atr = 0.0
stop_price = 0.0
entry_price = 0.0
bars = []
highs = []
lows = []
closes = []

# === 工具函数 ===
def calculate_atr(period):
    """计算 ATR"""
    if len(closes) < period + 1:
        return None

    tr_list = []
    for i in range(len(closes) - period, len(closes)):
        tr = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i-1]),
            abs(lows[i] - closes[i-1])
        )
        tr_list.append(tr)

    return sum(tr_list) / period if tr_list else None

def update_stop_loss(bar):
    """更新止损"""
    global stop_price

    if pos > 0:
        # 多仓止损
        new_stop = bar.close_price - atr * ATR_MULTIPLIER
        stop_price = max(stop_price, new_stop)

    elif pos < 0:
        # 空仓止损
        new_stop = bar.close_price + atr * ATR_MULTIPLIER
        stop_price = min(stop_price, new_stop)

# === 初始化 ===
def on_init():
    """脚本初始化"""
    print(f"[{SCRIPT_NAME}] 初始化")
    load_bar(days=30)
    print(f"[{SCRIPT_NAME}] 初始化完成")

# === 启动 ===
def on_start():
    """脚本启动"""
    print(f"[{SCRIPT_NAME}] 启动")

# === 停止 ===
def on_stop():
    """脚本停止"""
    print(f"[{SCRIPT_NAME}] 停止")
    cancel_all()

# === Tick 事件 ===
def on_tick(tick):
    """Tick 事件处理"""
    global pos

    if pos == 0:
        return

    # 检查止损
    if pos > 0 and tick.last_price <= stop_price:
        print(f"[{SCRIPT_NAME}] 多仓止损触发")
        sell(tick.ask_price_1, abs(pos))
        pos = 0

    elif pos < 0 and tick.last_price >= stop_price:
        print(f"[{SCRIPT_NAME}] 空仓止损触发")
        cover(tick.bid_price_1, abs(pos))
        pos = 0

# === Bar 事件 ===
def on_bar(bar):
    """Bar 事件处理"""
    global bars, highs, lows, closes, day_open, day_high, day_low
    global atr, stop_price, entry_price, pos

    # 交易日切换
    if len(bars) > 0 and bar.datetime.date() != bars[-1].datetime.date():
        day_open = bar.open_price
        day_high = bar.high_price
        day_low = bar.low_price
    else:
        if day_open == 0:
            day_open = bar.open_price
        day_high = max(day_high, bar.high_price)
        day_low = min(day_low, bar.low_price)

    # 更新数据
    bars.append(bar)
    highs.append(bar.high_price)
    lows.append(bar.low_price)
    closes.append(bar.close_price)

    # 保持数据窗口
    max_len = ATR_WINDOW * 3
    if len(bars) > max_len:
        bars.pop(0)
        highs.pop(0)
        lows.pop(0)
        closes.pop(0)

    # 计算 ATR
    atr = calculate_atr(ATR_WINDOW)
    if atr is None:
        return

    # 无持仓时计算突破价格
    if pos == 0:
        upper_band = day_open * (1 + BREAKOUT_RATIO)
        lower_band = day_open * (1 - BREAKOUT_RATIO)

        # 突破买入
        if bar.close_price > upper_band:
            print(f"[{SCRIPT_NAME}] 向上突破开多")
            buy(bar.close_price, FIXED_SIZE)
            pos = FIXED_SIZE
            entry_price = bar.close_price
            stop_price = entry_price - atr * ATR_MULTIPLIER

        # 突破卖出
        elif bar.close_price < lower_band:
            print(f"[{SCRIPT_NAME}] 向下突破开空")
            short(bar.close_price, FIXED_SIZE)
            pos = -FIXED_SIZE
            entry_price = bar.close_price
            stop_price = entry_price + atr * ATR_MULTIPLIER

    # 有持仓时更新止损
    else:
        update_stop_loss(bar)

# === 订单事件 ===
def on_order(order):
    """订单事件处理"""
    pass

# === 成交事件 ===
def on_trade(trade):
    """成交事件处理"""
    print(f"[{SCRIPT_NAME}] 成交: {trade.direction} {trade.volume}@{trade.price:.2f}")
```

---

## 10. 配置和使用方法

### 10.1 安装脚本策略模块

```bash
# 安装 vnpy_scripttrader
pip install vnpy_scripttrader

# 验证安装
python -c "from vnpy_scripttrader import ScriptEngine; print('安装成功')"
```

### 10.2 创建脚本文件

**目录结构：**

```
strategies/
├── scripts/
│   ├── dual_ma_script.py
│   ├── breakout_script.py
│   └── monitor_script.py
└── __init__.py
```

**创建脚本：**

```bash
# 创建脚本目录
mkdir -p strategies/scripts

# 创建脚本文件
touch strategies/scripts/my_script.py

# 编辑脚本
vim strategies/scripts/my_script.py
```

### 10.3 运行脚本策略

**1. 命令行运行**

```python
#!/usr/bin/env python
# run_script.py

from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy_ctp.gateway import CtpGateway
from vnpy_scripttrader import ScriptEngine

# 创建引擎
event_engine = EventEngine()
main_engine = MainEngine(event_engine)

# 添加网关
main_engine.add_gateway(CtpGateway)

# 添加脚本引擎
script_engine = main_engine.add_engine(ScriptEngine)
script_engine.init_engine()

# 连接网关
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

# 运行脚本
script_engine.run_script(
    script_name="my_script",
    script_path="strategies/scripts/my_script.py",
    vt_symbol="IF2401.CFFEX"
)

# 保持运行
import time
while True:
    time.sleep(1)
```

**2. 交互式运行**

```python
from vnpy_scripttrader import ScriptEngine

# 创建脚本引擎
script_engine = ScriptEngine(main_engine, event_engine)

# 加载并运行脚本
script_engine.run_script(
    script_name="dual_ma",
    script_path="strategies/scripts/dual_ma_script.py"
)

# 查看运行状态
print(script_engine.running_scripts)

# 停止脚本
script_engine.stop_script("dual_ma")
```

### 10.4 配置文件

**vt_script_setting.json：**

```json
{
  "scripts": {
    "dual_ma": {
      "script_file": "strategies/scripts/dual_ma_script.py",
      "vt_symbol": "IF2401.CFFEX",
      "interval": "1m",
      "auto_start": true,
      "active": true
    },
    "breakout": {
      "script_file": "strategies/scripts/breakout_script.py",
      "vt_symbol": "IC2401.CFFEX",
      "interval": "5m",
      "auto_start": false,
      "active": true
    }
  }
}
```

**加载配置：**

```python
import json

def load_script_config(config_file="vt_script_setting.json"):
    """加载脚本配置"""
    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    scripts = config.get("scripts", {})

    for script_name, script_config in scripts.items():
        if script_config.get("active", False):
            script_manager.add_script(
                script_name=script_name,
                script_file=script_config["script_file"],
                vt_symbol=script_config.get("vt_symbol"),
                interval=script_config.get("interval"),
                auto_start=script_config.get("auto_start", False)
            )

    return scripts
```

### 10.5 监控和管理

**脚本监控工具：**

```python
#!/usr/bin/env python
# script_monitor.py

from vnpy_scripttrader import ScriptEngine

class ScriptMonitor:
    """脚本监控器"""

    def __init__(self, script_engine: ScriptEngine):
        self.engine = script_engine

    def show_status(self):
        """显示脚本状态"""
        print("=" * 50)
        print("脚本状态")
        print("=" * 50)

        for script_name in self.engine.scripts:
            context = self.engine.script_contexts.get(script_name, {})

            print(f"脚本: {script_name}")
            print(f"  运行中: {script_name in self.engine.running_scripts}")
            print(f"  持仓: {context.get('pos', 0)}")
            print(f"  入场价: {context.get('entry_price', 0)}")
            print()

    def show_errors(self):
        """显示脚本错误"""
        print("=" * 50)
        print("脚本错误")
        print("=" * 50)

        for script_name, errors in self.engine.script_errors.items():
            print(f"脚本: {script_name}")
            for error in errors:
                print(f"  {error}")

    def reload_all(self):
        """重新加载所有脚本"""
        for script_name in list(self.engine.running_scripts):
            self.engine.reload_script(script_name)

# 使用
monitor = ScriptMonitor(script_engine)
monitor.show_status()
monitor.show_errors()
```

---

## 总结

vn.py 脚本策略系统提供了一个轻量级、灵活的策略开发方式，适合快速原型开发和简单策略实现。通过本篇文档，我们学习了：

1. **脚本策略的基本概念**：相比 CTA 策略的优势和适用场景
2. **系统架构**：ScriptEngine、ScriptLoader、ScriptManager 的设计
3. **脚本语法**：基于 Python 的脚本编写规范
4. **执行机制**：脚本加载、执行、热更新的流程
5. **交互方式**：脚本与策略、数据共享的方法
6. **错误处理**：调试技巧和常见错误排查
7. **性能优化**：计算优化、数据结构优化、批量处理
8. **最佳实践**：代码组织、风险管理、监控告警
9. **完整示例**：双均线策略、突破策略的完整实现
10. **配置使用**：安装、运行、配置、监控的完整流程

通过掌握这些知识，您可以快速开发出自己的脚本策略，并在 vn.py 框架中高效运行。同时，建议结合 CTA 策略模块，在需要更复杂逻辑时使用 CTA 策略，在需要快速验证时使用脚本策略，实现优势互补。

---

**文档字数**: 约 7,800 字
**主要内容摘要**:
- 脚本策略的基本概念和优势
- vn.py 脚本策略系统的三大核心组件（ScriptEngine、ScriptLoader、ScriptManager）
- 基于 Python 的脚本语言和语法规范
- 脚本加载、执行和热更新机制
- 脚本与 CTA 策略的交互方式
- 错误处理、调试技巧和性能优化方法
- 最佳实践建议（代码组织、风险管理、监控告警）
- 两个完整的脚本示例（双均线策略、带止损的突破策略）
- 配置文件、运行脚本、监控管理的详细方法
