# VnPy 回测引擎性能优化技巧

**版本**: VnPy 3.x
**更新时间**: 2026-02-20

---

## 目录

1. [回测速度优化](#1-回测速度优化)
2. [内存优化方法](#2-内存优化方法)
3. [数据加载优化](#3-数据加载优化)
4. [具体优化建议](#4-具体优化建议)

---

## 1. 回测速度优化

### 1.1 减少事件处理开销

回测引擎的核心是事件驱动架构，优化事件处理可以显著提升速度。

**优化前**：
```python
def on_bar(self, bar: BarData):
    # 每次都重新计算所有指标
    self.ma5 = self.calculate_ma(5)
    self.ma10 = self.calculate_ma(10)
    self.ma20 = self.calculate_ma(20)
    self.ma30 = self.calculate_ma(30)
```

**优化后**：
```python
def on_bar(self, bar: BarData):
    # 使用滑动窗口，只更新最新值
    self.bars.append(bar)
    if len(self.bars) > 30:
        self.bars.pop(0)
    
    # 只计算必要的指标
    if len(self.bars) >= 5:
        self.ma5 = sum(b.close_price for b in self.bars[-5:]) / 5
    if len(self.bars) >= 10:
        self.ma10 = sum(b.close_price for b in self.bars[-10:]) / 10
```

### 1.2 使用 NumPy 加速计算

NumPy 的向量化操作比纯 Python 循环快 10-100 倍。

```python
import numpy as np

class OptimizedStrategy(CtaTemplate):
    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.close_prices = np.array([])
    
    def on_bar(self, bar: BarData):
        # 使用 NumPy 数组存储价格
        self.close_prices = np.append(self.close_prices, bar.close_price)
        
        # 向量化计算
        if len(self.close_prices) >= 20:
            ma20 = np.mean(self.close_prices[-20:])
            std20 = np.std(self.close_prices[-20:])
            upper = ma20 + 2 * std20
            lower = ma20 - 2 * std20
```

### 1.3 减少日志输出

日志 I/O 是性能瓶颈之一，生产环境应减少日志。

```python
class OptimizedStrategy(CtaTemplate):
    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.bar_count = 0
    
    def on_bar(self, bar: BarData):
        self.bar_count += 1
        
        # 只在关键节点输出日志
        if self.bar_count % 100 == 0:
            self.write_log(f"已处理 {self.bar_count} 根K线")
        
        # 避免频繁的调试日志
        # self.write_log(f"当前价格: {bar.close_price}")  # 删除
```

### 1.4 使用缓存避免重复计算

```python
from functools import lru_cache

class OptimizedStrategy(CtaTemplate):
    @lru_cache(maxsize=1000)
    def calculate_atr(self, period: int) -> float:
        """缓存 ATR 计算结果"""
        if len(self.bars) < period + 1:
            return 0.0
        
        tr_list = []
        for i in range(len(self.bars) - period, len(self.bars)):
            bar = self.bars[i]
            prev_bar = self.bars[i - 1]
            tr = max(
                bar.high_price - bar.low_price,
                abs(bar.high_price - prev_bar.close_price),
                abs(bar.low_price - prev_bar.close_price)
            )
            tr_list.append(tr)
        
        return sum(tr_list) / period
```

---

## 2. 内存优化方法

### 2.1 限制历史数据存储

避免在策略中存储过多历史数据。

**优化前**：
```python
class MemoryHeavyStrategy(CtaTemplate):
    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.all_bars = []  # 存储所有历史K线
    
    def on_bar(self, bar: BarData):
        self.all_bars.append(bar)  # 内存持续增长
```

**优化后**：
```python
class MemoryOptimizedStrategy(CtaTemplate):
    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.window_size = 100  # 只保留最近100根K线
        self.bars = []
    
    def on_bar(self, bar: BarData):
        self.bars.append(bar)
        if len(self.bars) > self.window_size:
            self.bars.pop(0)  # 删除旧数据
```

### 2.2 使用生成器处理数据

```python
def bar_generator(bars, window_size):
    """生成器模式，减少内存占用"""
    window = []
    for bar in bars:
        window.append(bar)
        if len(window) > window_size:
            window.pop(0)
        yield window

# 使用示例
for window in bar_generator(all_bars, 100):
    # 处理窗口数据
    pass
```

### 2.3 及时释放大对象

```python
class OptimizedStrategy(CtaTemplate):
    def on_stop(self):
        """策略停止时释放资源"""
        # 清空大对象
        self.bars.clear()
        self.indicators.clear()
        
        # 手动触发垃圾回收
        import gc
        gc.collect()
```

### 2.4 使用更高效的数据结构

```python
from collections import deque

class OptimizedStrategy(CtaTemplate):
    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        # deque 的 append/pop 操作是 O(1)，比 list 更快
        self.bars = deque(maxlen=100)
    
    def on_bar(self, bar: BarData):
        self.bars.append(bar)  # 自动删除最旧的数据
```

---

## 3. 数据加载优化

### 3.1 批量加载数据

避免频繁的小批量数据查询。

**优化前**：
```python
# 每次查询少量数据
for day in range(1, 32):
    bars = database.get_bar_data(
        symbol="IF2602",
        exchange=Exchange.CFFEX,
        interval=Interval.MINUTE,
        start=datetime(2024, 1, day),
        end=datetime(2024, 1, day, 23, 59)
    )
    process_bars(bars)
```

**优化后**：
```python
# 一次性加载所有数据
bars = database.get_bar_data(
    symbol="IF2602",
    exchange=Exchange.CFFEX,
    interval=Interval.MINUTE,
    start=datetime(2024, 1, 1),
    end=datetime(2024, 1, 31, 23, 59)
)
process_bars(bars)
```

### 3.2 使用更快的数据库

SQLite 适合小数据量，MySQL/PostgreSQL 适合大数据量。

```python
# 配置 MySQL 数据库
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

### 3.3 预加载必要数据

```python
class OptimizedStrategy(CtaTemplate):
    def on_init(self):
        """初始化时预加载数据"""
        # 加载足够的历史数据用于计算指标
        self.load_bar(100)  # 加载最近100根K线
        
        # 预计算指标
        self.pre_calculate_indicators()
    
    def pre_calculate_indicators(self):
        """预计算指标，避免运行时计算"""
        for bar in self.bars:
            # 预计算所有需要的指标
            pass
```

### 3.4 使用数据压缩

```python
import pandas as pd

# 使用 Parquet 格式（比 CSV 小 5-10 倍）
df = pd.DataFrame([{
    "datetime": bar.datetime,
    "open": bar.open_price,
    "high": bar.high_price,
    "low": bar.low_price,
    "close": bar.close_price,
    "volume": bar.volume
} for bar in bars])

# 保存为 Parquet
df.to_parquet("data.parquet", compression="snappy")

# 读取
df = pd.read_parquet("data.parquet")
```

---

## 4. 具体优化建议

### 4.1 回测引擎配置优化

```python
from vnpy_ctastrategy.backtesting import BacktestingEngine

backtesting_engine = BacktestingEngine()

# 优化配置
backtesting_engine.set_parameters(
    vt_symbol="IF2602.CFFEX",
    interval=Interval.MINUTE,
    start=datetime(2024, 1, 1),
    end=datetime(2024, 12, 31),
    rate=0.3/10000,
    slippage=0.2,
    size=300,
    pricetick=0.2,
    capital=1_000_000,
    mode=BacktestingMode.BAR,  # 使用 BAR 模式而非 TICK 模式
)
```

### 4.2 参数优化优化

```python
from vnpy_ctastrategy.backtesting import OptimizationSetting

optimization_setting = OptimizationSetting()

# 减少参数组合数量
optimization_setting.add_parameter("fast_window", 5, 20, 5)  # 4个值
optimization_setting.add_parameter("slow_window", 20, 60, 10)  # 5个值

# 总共 4*5=20 个组合，而非 16*41=656 个组合

# 使用多进程加速
results = backtesting_engine.run_optimization(
    optimization_setting,
    process=True,  # 启用多进程
    max_workers=4  # 使用4个进程
)
```

### 4.3 策略代码优化清单

- [ ] 避免在 `on_bar` 中进行复杂计算
- [ ] 使用滑动窗口而非存储所有历史数据
- [ ] 使用 NumPy 进行数值计算
- [ ] 减少日志输出
- [ ] 使用缓存避免重复计算
- [ ] 及时释放不再使用的对象
- [ ] 使用 deque 替代 list（需要频繁 pop 时）
- [ ] 预计算指标而非实时计算

### 4.4 性能监控

```python
import time
import psutil

class PerformanceMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.start_memory = psutil.Process().memory_info().rss
    
    def report(self):
        elapsed = time.time() - self.start_time
        memory_used = (psutil.Process().memory_info().rss - self.start_memory) / 1024 / 1024
        
        print(f"耗时: {elapsed:.2f} 秒")
        print(f"内存: {memory_used:.2f} MB")
        print(f"速度: {len(bars) / elapsed:.2f} K线/秒")

# 使用示例
monitor = PerformanceMonitor()
backtesting_engine.run_backtesting()
monitor.report()
```

### 4.5 完整优化示例

```python
import numpy as np
from collections import deque
from functools import lru_cache

class FullyOptimizedStrategy(CtaTemplate):
    """完全优化的策略示例"""
    
    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        
        # 使用 deque 优化内存
        self.bars = deque(maxlen=100)
        
        # 使用 NumPy 数组加速计算
        self.close_prices = np.zeros(100)
        self.index = 0
        
        # 缓存计算结果
        self.ma_cache = {}
    
    def on_bar(self, bar: BarData):
        # 更新数据结构
        self.bars.append(bar)
        self.close_prices[self.index % 100] = bar.close_price
        self.index += 1
        
        # 只在数据足够时计算
        if len(self.bars) >= 20:
            # 使用 NumPy 向量化计算
            prices = self.close_prices[:len(self.bars)]
            ma20 = np.mean(prices[-20:])
            
            # 使用缓存
            cache_key = f"ma20_{self.index}"
            if cache_key not in self.ma_cache:
                self.ma_cache[cache_key] = ma20
            
            # 交易逻辑
            if bar.close_price > ma20 and self.pos == 0:
                self.buy(bar.close_price, self.fixed_size)
            elif bar.close_price < ma20 and self.pos > 0:
                self.sell(bar.close_price, self.fixed_size)
    
    def on_stop(self):
        """清理资源"""
        self.bars.clear()
        self.ma_cache.clear()
        import gc
        gc.collect()
```

---

## 总结

VnPy 回测引擎性能优化的关键点：

1. **速度优化**：减少事件处理开销、使用 NumPy、减少日志、使用缓存
2. **内存优化**：限制历史数据存储、使用生成器、及时释放对象、使用高效数据结构
3. **数据优化**：批量加载、使用快速数据库、预加载数据、使用数据压缩

通过以上优化，回测速度可提升 5-10 倍，内存占用可降低 50-80%。

---

**文档结束**