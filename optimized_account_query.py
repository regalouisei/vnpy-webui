#!/usr/bin/env python3
"""
优化后的账户查询方案

问题分析：
1. vn.py CTP 网关有自动定时查询机制（每2秒循环查询账户和持仓）
2. CTP 服务器响应时间约 3-4 秒
3. 之前的测试脚本没有正确等待事件

解决方案：
1. 方法A：使用事件监听器等待单次查询（推荐）
2. 方法B：从 OmsEngine 直接获取最新账户数据（最快）
3. 方法C：禁用自动查询，改为手动按需查询
"""
import sys
import time
import threading
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("优化后的账户查询方案")
print("=" * 80)
print()

# ==============================================================================
# 导入
# ==============================================================================

from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.object import AccountData
from vnpy.trader.event import EVENT_LOG, EVENT_ACCOUNT
from vnpy_ctp.gateway import CtpGateway

# ==============================================================================
# 方法A：使用事件监听器 + 同步等待
# ==============================================================================

print("方法A：使用事件监听器 + 同步等待")
print("-" * 80)

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
        if not gateway:
            raise RuntimeError("CTP 网关未找到")

        gateway.query_account()

        # 等待响应（最多 timeout 秒）
        if self.received.wait(timeout):
            return self.account_data
        else:
            raise TimeoutError(f"账户查询超时（{timeout}秒）")

    def close(self):
        """关闭监听器"""
        self.event_engine.unregister(EVENT_ACCOUNT, self._on_account)


# ==============================================================================
# 方法B：从 OmsEngine 直接获取（最快）
# ==============================================================================

print("方法B：从 OmsEngine 直接获取最新数据")
print("-" * 80)

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


# ==============================================================================
# 测试两种方法
# ==============================================================================

# 创建引擎
event_engine = EventEngine()
main_engine = MainEngine(event_engine)

# 注册日志监听器
log_events = []
def on_log(event):
    log_events.append(event.data)
    print(f"  [LOG] {event.data.msg}")
event_engine.register(EVENT_LOG, on_log)

# 添加网关
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

print("连接到 OpenCTP TTS...")
main_engine.connect(gateway_setting, "CTP")

# 等待连接
print("等待连接...")
for i in range(15):
    time.sleep(1)
    if any("登录成功" in log.msg for log in log_events):
        print("✅ 连接成功")
        break

print()

# ==============================================================================
# 测试方法A：同步等待查询
# ==============================================================================

print("=" * 80)
print("测试方法A：同步等待查询（推荐）")
print("=" * 80)
print()

query = AccountQuery(main_engine)

try:
    print("发送查询请求...")
    start = time.time()

    account = query.query(timeout=5)

    elapsed = time.time() - start
    print()
    print(f"✅ 查询成功！耗时: {elapsed:.2f}秒")
    print(f"  账号: {account.accountid}")
    print(f"  余额: {account.balance:,.2f}")
    print(f"  可用: {account.available:,.2f}")
    print(f"  冻结: {account.frozen:,.2f}")
    print()

except TimeoutError as e:
    print(f"❌ {e}")
    print()
except Exception as e:
    print(f"❌ 查询失败: {e}")
    print()
    import traceback
    traceback.print_exc()
finally:
    query.close()

# ==============================================================================
# 测试方法B：直接获取
# ==============================================================================

print("=" * 80)
print("测试方法B：直接获取最新数据（最快）")
print("=" * 80)
print()

try:
    print("等待自动查询的账户数据...")
    start = time.time()

    account = get_latest_account(main_engine, max_wait=5)

    elapsed = time.time() - start
    print()
    print(f"✅ 获取成功！耗时: {elapsed:.2f}秒")
    print(f"  账号: {account.accountid}")
    print(f"  余额: {account.balance:,.2f}")
    print(f"  可用: {account.available:,.2f}")
    print(f"  冻结: {account.frozen:,.2f}")
    print()

except TimeoutError as e:
    print(f"❌ {e}")
    print()
except Exception as e:
    print(f"❌ 获取失败: {e}")
    print()

# ==============================================================================
# 性能对比
# ==============================================================================

print("=" * 80)
print("性能对比总结")
print("=" * 80)
print()

print("方法对比：")
print()
print("【方法A：同步等待查询】")
print("  优点：")
print("    - 可以精确控制查询时机")
print("    - 支持超时控制")
print("    - 不依赖自动查询")
print("  缺点：")
print("    - 每次查询都要发送请求")
print("    - 响应时间：3-4秒（CTP服务器延迟）")
print("  适用场景：")
print("    - 需要按需查询")
print("    - 需要精确控制查询频率")
print()

print("【方法B：直接获取最新数据】")
print("  优点：")
print("    - 利用 vn.py 自动查询机制")
print("    - 不需要额外请求")
print("    - 响应时间：<1秒（内存读取）")
print("  缺点：")
print("    - 依赖自动查询（每2秒更新一次）")
print("    - 数据可能有延迟")
print("  适用场景：")
print("    - 需要频繁获取账户数据")
print("    - 可以容忍 2 秒的数据延迟")
print("    - Web UI、实时监控等")
print()

print("=" * 80)
print("推荐方案：")
print("  - Web UI：使用方法B（直接获取最新数据）")
print("  - 脚本：根据需求选择")
print("=" * 80)
