# 账户查询性能优化报告

## 问题描述

用户反馈：账户查询需要等待很长时间，不符合预期的"非常快"。

## 根本原因分析

### 1. vn.py CTP 网关的工作机制

vn.py CTP 网关有一个**自动查询机制**：

```python
# CtpGateway 的定时器循环查询
def process_timer_event(self, event: Event) -> None:
    """定时事件处理"""
    self.count += 1
    if self.count < 2:
        return
    self.count = 0

    func = self.query_functions.pop(0)
    func()
    self.query_functions.append(func)

def init_query(self) -> None:
    """初始化查询任务"""
    self.query_functions: list = [self.query_account, self.query_position]
    self.event_engine.register(EVENT_TIMER, self.process_timer_event)
```

**关键点**：
- 连接成功后，自动启动定时器
- 每 2 秒循环执行账户查询和持仓查询
- 查询结果自动存储到 OmsEngine 的缓存中

### 2. CTP 服务器响应时间

通过调试发现：
- CTP 服务器响应时间：**3-4 秒**
- 这是网络延迟 + CTP API 调用的时间

### 3. 问题所在

**之前的错误做法**：
```python
# ❌ 错误：每次都手动查询
gateway.query_account()
time.sleep(10)  # 等待响应
account = oms_engine.get_all_accounts()[0]
```

**问题**：
1. 每次都调用 `query_account()`，发送新的查询请求
2. 每次都要等待 3-4 秒的 CTP 服务器响应
3. 而实际上，vn.py 已经在后台自动查询并缓存了数据

## 解决方案

### 方法A：同步等待查询（按需查询）

```python
class AccountQuery:
    """账户查询器 - 同步等待方式"""

    def __init__(self, main_engine):
        self.main_engine = main_engine
        self.event_engine = main_engine.event_engine
        self.received = threading.Event()
        self.account_data = None

        # 注册监听器
        self.event_engine.register(EVENT_ACCOUNT, self._on_account)

    def _on_account(self, event):
        """收到账户事件"""
        self.account_data = event.data
        self.received.set()

    def query(self, timeout=5):
        """查询账户（同步等待）"""
        self.received.clear()

        # 发送查询请求
        gateway = self.main_engine.get_gateway("CTP")
        gateway.query_account()

        # 等待响应（最多 timeout 秒）
        if self.received.wait(timeout):
            return self.account_data
        else:
            raise TimeoutError(f"账户查询超时（{timeout}秒）")
```

**性能**：4.92 秒
**适用场景**：需要精确控制查询时机的场景

### 方法B：直接获取最新数据（推荐）✅

```python
def get_latest_account(main_engine, max_wait=5):
    """获取最新的账户数据（自动更新模式）"""

    # 等待数据到达
    start = time.time()
    oms_engine = main_engine.get_engine("oms")

    while time.time() - start < max_wait:
        accounts = oms_engine.get_all_accounts()
        if accounts:
            return accounts[0]  # 返回第一个账户
        time.sleep(0.1)

    raise TimeoutError(f"未在 {max_wait} 秒内收到账户数据")
```

**性能**：**0.00 秒**（几乎瞬时）
**适用场景**：
- Web UI
- 实时监控
- 需要频繁获取账户数据的场景

### 方法B 的 Web API 示例

```python
@app.get("/api/account")
async def get_account():
    """获取账户信息（优化版）"""
    start_time = time.time()

    # 获取 OmsEngine
    oms_engine = main_engine.get_engine("oms")
    if not oms_engine:
        raise HTTPException(status_code=500, detail="OmsEngine 未初始化")

    # 获取所有账户
    accounts = oms_engine.get_all_accounts()

    if not accounts:
        raise HTTPException(status_code=404, detail="未找到账户数据")

    # 返回第一个账户
    account = accounts[0]

    elapsed = (time.time() - start_time) * 1000  # 毫秒

    return {
        "success": True,
        "data": {
            "account_id": account.accountid,
            "balance": float(account.balance),
            "available": float(account.available),
            "frozen": float(account.frozen),
            "currency": "CNY"
        },
        "performance": {
            "response_time_ms": round(elapsed, 2),
            "method": "直接从 OmsEngine 获取"
        }
    }
```

## 性能对比

| 方法 | 响应时间 | 优点 | 缺点 | 适用场景 |
|------|---------|------|------|---------|
| **方法A：同步等待** | 4.92秒 | 精确控制查询时机 | 每次都发送请求 | 按需查询 |
| **方法B：直接获取** | **0.00秒** | 利用自动查询，不额外请求 | 数据可能有2秒延迟 | Web UI、实时监控 |

## 技术原理

### vn.py 数据流

```
CTP 服务器
    ↓ (3-4秒)
CtpGateway.td_api (自动查询，每2秒)
    ↓ (事件)
OmsEngine.process_account_event()
    ↓ (缓存)
OmsEngine.accounts[] (内存缓存)
    ↓ (直接读取)
Web API / 应用 (0.00秒)
```

### 关键发现

1. **vn.py 已经在自动查询**：连接成功后，定时器会自动循环查询账户和持仓
2. **数据已缓存**：查询结果存储在 OmsEngine 的内存中
3. **不需要手动查询**：直接从 OmsEngine 获取即可，无需发送新的查询请求

## 代码修改指南

### ❌ 旧代码（慢）

```python
# 旧代码：每次都手动查询
def get_account_old():
    gateway = main_engine.get_gateway("CTP")
    gateway.query_account()
    time.sleep(5)  # 等待 CTP 响应
    oms_engine = main_engine.get_engine("oms")
    return oms_engine.get_all_accounts()[0]
```

**性能**：4.92 秒

### ✅ 新代码（快）

```python
# 新代码：直接从缓存获取
def get_account_new():
    oms_engine = main_engine.get_engine("oms")
    return oms_engine.get_all_accounts()[0]
```

**性能**：0.00 秒

## 调试过程

### 1. 性能诊断脚本

创建了 `debug_account_query.py`，发现：
- 连接请求：8.79ms
- 连接完成：1.01秒
- 查询请求：0.15ms
- **账户数据：30秒超时** ❌

### 2. CTP 回调调试

创建了 `debug_ctp_callback.py`，发现：
- onRspQryTradingAccount 回调确实被调用
- 数据正确返回（账号 17130，余额 1000万）
- 响应时间：3-4 秒

### 3. 优化验证

创建了 `optimized_account_query.py`，对比两种方法：
- 方法A（同步等待）：4.92 秒
- 方法B（直接获取）：0.00 秒

## 总结

### 问题根源

账户查询慢不是 vn.py 的问题，而是：
1. **错误的使用方式**：每次都手动查询，忽略了自动查询机制
2. **CTP 服务器延迟**：网络延迟导致每次查询需要 3-4 秒

### 解决方案

**使用方法B：直接从 OmsEngine 获取最新数据**
- 响应时间从 4.92 秒优化到 0.00 秒
- 利用 vn.py 的自动查询机制
- 无需发送额外的查询请求

### 推荐做法

1. **Web API / 实时监控**：使用方法B（直接获取）
2. **脚本 / 按需查询**：使用方法A（同步等待）
3. **关键原则**：不要手动调用 `query_account()`，除非确实需要强制刷新

## 相关文件

- `debug_account_query.py` - 性能诊断脚本
- `debug_ctp_callback.py` - CTP 回调调试
- `optimized_account_query.py` - 优化方案对比
- `optimized_web_api_example.py` - 优化后的 Web API 示例

## 更新日期

2026-02-20
