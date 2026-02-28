# VnPy 测试经验总结与最佳实践

**文档版本**: 1.0
**创建时间**: 2026-02-20
**目的**: 总结测试过程中的经验教训，提供最佳实践指导

---

## 一、测试策略

### 1.1 测试优先级

```
优先级 1 (最高): 核心功能
- 事件驱动引擎
- MainEngine
- CTP 连接
- 账户查询
- 持仓查询
- 合约查询
- 行情订阅

优先级 2: 策略和回测
- CTA 策略引擎
- 策略生命周期
- 回测引擎
- 回测执行

优先级 3: 数据管理
- 数据库连接
- 数据存储
- 数据查询
- 数据导出

优先级 4: 高级功能 (可选)
- 组合策略
- 期权交易
- 算法交易
- 脚本策略
- AI 量化
```

### 1.2 测试方法

#### 方法 1: 单元测试

**适用场景**: 测试单个功能模块

**示例**:
```python
def test_event_engine():
    """测试事件引擎"""
    event_engine = EventEngine()
    assert event_engine is not None
    print("✅ 事件引擎测试通过")
```

**优点**:
- 快速
- 隔离
- 便于调试

**缺点**:
- 不测试集成
- 可能遗漏边界情况

#### 方法 2: 集成测试

**适用场景**: 测试多个模块协作

**示例**:
```python
def test_ctp_integration():
    """测试 CTP 集成"""
    event_engine = EventEngine()
    main_engine = MainEngine(event_engine)
    main_engine.add_gateway(CtpGateway, "CTP")
    main_engine.connect(gateway_setting, "CTP")
    # 验证连接、查询、行情等
```

**优点**:
- 测试真实场景
- 发现集成问题

**缺点**:
- 较慢
- 依赖外部资源

#### 方法 3: 端到端测试

**适用场景**: 测试完整流程

**示例**:
```python
def test_e2e_trading():
    """测试完整交易流程"""
    # 连接 → 订阅 → 策略 → 交易 → 监控
    pass
```

**优点**:
- 最接近实际使用
- 发现系统级问题

**缺点**:
- 最慢
- 最复杂

### 1.3 测试原则

1. **从简单到复杂**: 先测核心，再测集成
2. **快速反馈**: 每个测试都应该快速完成
3. **独立运行**: 测试之间不应该有依赖
4. **可重复**: 同样的输入应该得到同样的输出
5. **有意义的失败**: 失败时提供清晰的错误信息

---

## 二、调试技巧

### 2.1 使用 print 调试

**快速定位问题**:
```python
def test_something():
    print("步骤 1: 开始")
    result1 = step1()
    print(f"步骤 1 完成: {result1}")

    print("步骤 2: 开始")
    result2 = step2(result1)
    print(f"步骤 2 完成: {result2}")
```

**优点**:
- 简单
- 直观

**缺点**:
- 不够详细
- 需要手动清理

### 2.2 使用 logging

**记录详细信息**:
```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_something():
    logging.debug("开始测试")
    try:
        result = do_something()
        logging.info(f"测试成功: {result}")
    except Exception as e:
        logging.error(f"测试失败: {e}", exc_info=True)
```

**优点**:
- 详细
- 可配置
- 可持久化

### 2.3 使用 traceback

**捕获完整错误信息**:
```python
import traceback

def test_something():
    try:
        do_something()
    except Exception as e:
        print(f"错误: {e}")
        print("=" * 80)
        traceback.print_exc()
        print("=" * 80)
```

**优点**:
- 完整的堆栈跟踪
- 便于定位问题

### 2.4 使用 assert

**验证预期**:
```python
def test_account_query():
    accounts = oms_engine.get_all_accounts()
    assert accounts is not None, "账户数据为空"
    assert len(accounts) > 0, "账户数量为 0"
    assert accounts[0].balance > 0, "账户余额为 0"
    print("✅ 账户查询测试通过")
```

**优点**:
- 明确验证预期
- 快速失败

### 2.5 使用 try-except

**优雅处理错误**:
```python
def test_with_protection():
    try:
        # 尝试连接
        main_engine.connect(setting, "CTP")
    except ConnectionError as e:
        print(f"连接失败: {e}")
        return False
    except TimeoutError as e:
        print(f"连接超时: {e}")
        return False
    except Exception as e:
        print(f"未知错误: {e}")
        return False

    print("✅ 连接成功")
    return True
```

---

## 三、性能优化

### 3.1 账户查询优化

**问题**: 手动调用 `query_account()` 很慢

**优化前**:
```python
# ❌ 慢: 4.92 秒
main_engine.query_account()
time.sleep(5)
accounts = oms_engine.get_all_accounts()
```

**优化后**:
```python
# ✅ 快: <0.01 秒
accounts = oms_engine.get_all_accounts()
```

**提升**: >99%

### 3.2 批量操作优化

**问题**: 单条插入数据很慢

**优化前**:
```python
# ❌ 慢: 逐条插入
for bar in bars:
    database.save_bar_data([bar])
```

**优化后**:
```python
# ✅ 快: 批量插入
database.save_bar_data(bars)
```

**提升**: 显著

### 3.3 缓存策略

**利用 VnPy 的缓存机制**:
```python
# ✅ 利用缓存，不要重复查询
accounts = oms_engine.get_all_accounts()  # 第一次
positions = oms_engine.get_all_positions()  # 缓存读取
contracts = oms_engine.get_all_contracts()   # 缓存读取
```

### 3.4 异步处理

**使用事件驱动**:
```python
# ✅ 使用事件监听，避免轮询
def on_tick(event):
    tick = event.data
    # 处理 tick

event_engine.register(EVENT_TICK, on_tick)
```

---

## 四、代码组织

### 4.1 测试脚本结构

```python
#!/usr/bin/env python3
"""
测试脚本标题

测试内容:
1. 测试项 1
2. 测试项 2
"""

# 导入
import sys
import time
from datetime import datetime

# 配置
sys.stdout.reconfigure(encoding='utf-8')

# 测试结果记录
test_results = {}

def record_result(test_name, passed, details=""):
    """记录测试结果"""
    test_results[test_name] = {
        "passed": passed,
        "details": details,
        "timestamp": datetime.now().isoformat()
    }
    # 打印结果

# 测试阶段
def test_phase_1():
    """测试阶段 1"""
    pass

def test_phase_2():
    """测试阶段 2"""
    pass

# 主函数
def main():
    """主函数"""
    test_phase_1()
    test_phase_2()

    # 汇总结果
    print_summary()

if __name__ == "__main__":
    main()
```

### 4.2 策略文件结构

```python
# my_strategy.py
from vnpy_ctastrategy.template import CtaTemplate

class MyStrategy(CtaTemplate):
    """"策略描述"""

    # 策略参数
    fast_window: int = 10
    slow_window: int = 30

    # 策略变量
    bars: list = []

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

    # 策略生命周期
    def on_init(self):
        """初始化"""
        pass

    def on_start(self):
        """启动"""
        pass

    def on_stop(self):
        """停止"""
        pass

    # 事件处理
    def on_tick(self, tick):
        """Tick 事件"""
        pass

    def on_bar(self, bar):
        """K 线事件"""
        pass

    def on_order(self, order):
        """订单事件"""
        pass

    def on_trade(self, trade):
        """成交事件"""
        pass

    def on_position(self, position):
        """持仓事件"""
        pass
```

### 4.3 配置文件结构

```json
// ~/.vntrader/vt_setting.json
{
  "database": {
    "database": "sqlite",
    "database.db_path": "/path/to/database.db"
  },
  "datafeed": {
    "name": "database",
    "database": {
      "name": "sqlite",
      "database.db_path": "/path/to/database.db"
    }
  }
}
```

---

## 五、最佳实践

### 5.1 测试最佳实践

1. **测试命名**: `test_<功能名>.py`
2. **文档字符串**: 描述测试目的
3. **测试分组**: 使用测试阶段
4. **结果记录**: 使用统一格式
5. **超时保护**: 避免无限等待

### 5.2 策略开发最佳实践

1. **继承 CtaTemplate**: 不要从头开始
2. **实现生命周期**: `on_init`, `on_start`, `on_stop`
3. **处理事件**: `on_tick`, `on_bar`, `on_order`, `on_trade`
4. **使用日志**: `self.write_log()` 记录关键操作
5. **参数化**: 使用策略参数，便于优化

### 5.3 数据管理最佳实践

1. **批量操作**: 一次性保存/查询多条数据
2. **使用索引**: 提高查询速度
3. **定期备份**: 避免数据丢失
4. **数据清理**: 定期清理过期数据
5. **数据验证**: 保存前验证数据完整性

### 5.4 性能优化最佳实践

1. **利用缓存**: 不要重复查询
2. **批量操作**: 减少数据库访问次数
3. **异步处理**: 使用事件驱动
4. **避免轮询**: 使用事件监听
5. **定期清理**: 清理无用的缓存

---

## 六、常见错误和解决方案

### 6.1 导入错误

**错误**: `ModuleNotFoundError`

**原因**: 模块未安装

**解决**:
```bash
pip install vnpy_ctp  # 安装 CTP 网关
pip install vnpy_ctastrategy  # 安装 CTA 策略
```

### 6.2 连接错误

**错误**: 连接超时

**原因**: 网络问题或配置错误

**解决**:
1. 检查网络连接
2. 验证服务器地址和端口
3. 确认账号密码正确
4. 增加超时时间

### 6.3 查询错误

**错误**: 查询结果为空

**原因**: 查询参数错误或数据不存在

**解决**:
1. 检查查询参数
2. 验证数据是否存在
3. 增加等待时间（首次查询）
4. 检查日志

### 6.4 策略错误

**错误**: 策略不启动

**原因**: 策略未初始化或参数错误

**解决**:
1. 确保策略已初始化
2. 检查策略参数
3. 查看策略日志
4. 验证历史数据

---

## 七、工具和资源

### 7.1 Python 工具

```bash
# 检查模块
pip list | grep vnpy

# 检查模块信息
pip show vnpy

# 检查模块版本
python3 -c "import vnpy; print(vnpy.__version__)"

# 检查模块路径
python3 -c "import vnpy; print(vnpy.__file__)"
```

### 7.2 检查 API

```python
# 检查可用方法
from vnpy.trader.engine import MainEngine
engine = MainEngine()
print([m for m in dir(engine) if not m.startswith('_')])

# 检查可用事件
from vnpy.trader import event
print([e for e in dir(event) if e.startswith('EVENT_')])

# 检查可用常量
from vnpy.trader.constant import Exchange
print([e for e in dir(Exchange) if not e.startswith('_')])
```

### 7.3 官方资源

- **VnPy 官网**: https://www.vnpy.com
- **VnPy 文档**: https://docs.vnpy.com
- **VnPy 社区**: https://www.vnpy.com/forum
- **GitHub**: https://github.com/vnpy/vnpy

### 7.4 测试环境

- **OpenCTP**: http://openctp.cn
- **SimNow**: http://www.simnow.com.cn

---

## 八、总结

### 8.1 关键经验

1. **以实际代码为准**: 文档可能过时
2. **检查 API 可用性**: 使用 `dir()` 检查
3. **理解架构设计**: 不要绕过设计
4. **利用缓存机制**: 提升性能
5. **模块化设计**: 按需安装模块

### 8.2 避免的坑

1. ❌ 不要手动调用 `query_account()`
2. ❌ 不要假设数据结构
3. ❌ 不要在函数内定义策略类
4. ❌ 不要依赖不存在的 `EVENT_BAR`
5. ❌ 不要使用过时的 API

### 8.3 最佳实践

1. ✅ 分阶段测试: 从核心到高级
2. ✅ 设置超时保护: 避免无限等待
3. ✅ 保存测试日志: 便于分析
4. ✅ 使用 assert 验证: 明确预期
5. ✅ 优化查询性能: 利用缓存

---

**文档创建时间**: 2026-02-20
**文档版本**: 1.0
**状态**: 完成 ✅
