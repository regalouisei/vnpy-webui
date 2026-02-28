#!/usr/bin/env python3
"""
vn.py CTP 网关连接测试（正确的事件常量）
"""
import sys
import time
import signal
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("vn.py CTP 网关连接测试")
print("=" * 80)
print()

# ==============================================================================
# 导入
# ==============================================================================

print("导入 vn.py 核心模块...")
try:
    from vnpy.event import EventEngine
    from vnpy.trader.engine import MainEngine
    from vnpy.trader.object import (
        BarData, TickData, OrderData, TradeData,
        PositionData, AccountData, ContractData
    )
    from vnpy.trader.constant import Interval, Exchange
    from vnpy.trader.logger import INFO, logger
    print("✅ vn.py 核心模块导入成功")
    print(f"   vnpy: 4.3.0")
    print()
except Exception as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)

# 导入事件常量
print("导入事件常量...")
try:
    from vnpy.trader.event import (
        EVENT_TICK, EVENT_TRADE, EVENT_ORDER,
        EVENT_POSITION, EVENT_ACCOUNT, EVENT_QUOTE,
        EVENT_CONTRACT, EVENT_LOG, EVENT_TIMER
    )
    print("✅ 事件常量导入成功")
    print(f"   EVENT_TICK: {EVENT_TICK}")
    print(f"   EVENT_TRADE: {EVENT_TRADE}")
    print(f"   EVENT_ORDER: {EVENT_ORDER}")
    print(f"   EVENT_ACCOUNT: {EVENT_ACCOUNT}")
    print(f"   EVENT_CONTRACT: {EVENT_CONTRACT}")
    print(f"   EVENT_LOG: {EVENT_LOG}")
    print()
except Exception as e:
    print(f"❌ 事件常量导入失败: {e}")
    sys.exit(1)

# 导入 CTP 网关
print("导入 CTP 网关...")
try:
    from vnpy_ctp.gateway import CtpGateway
    print("✅ CTP 网关导入成功")
    print(f"   网关类: {CtpGateway}")
    print()
except Exception as e:
    print(f"❌ CTP 网关导入失败: {e}")
    sys.exit(1)

# ==============================================================================
# 创建引擎
# ==============================================================================

print("创建事件引擎...")
event_engine = EventEngine()
print("✅ 事件引擎创建成功")
print()

print("创建主引擎...")
main_engine = MainEngine(event_engine)
print("✅ 主引擎创建成功")
print()

# ==============================================================================
# 注册事件监听器
# ==============================================================================

print("注册事件监听器...")
all_events = {
    "tick": [],
    "trade": [],
    "order": [],
    "position": [],
    "account": [],
    "contract": [],
    "log": []
}

def make_handler(event_type):
    def handler(event):
        data = event.data
        all_events[event_type].append(data)
        print(f"  [{event_type}] {data}")
    return handler

# 注册所有事件
event_engine.register(EVENT_TICK, make_handler("tick"))
event_engine.register(EVENT_TRADE, make_handler("trade"))
event_engine.register(EVENT_ORDER, make_handler("order"))
event_engine.register(EVENT_POSITION, make_handler("position"))
event_engine.register(EVENT_ACCOUNT, make_handler("account"))
event_engine.register(EVENT_CONTRACT, make_handler("contract"))
event_engine.register(EVENT_LOG, make_handler("log"))

print("✅ 事件监听器注册成功")
print(f"   已注册事件: {list(all_events.keys())}")
print()

# ==============================================================================
# 添加 CTP 网关
# ==============================================================================

print("添加 CTP 网关...")
try:
    main_engine.add_gateway(CtpGateway, gateway_name="CTP")
    print("✅ CTP 网关添加成功")
    print()
except Exception as e:
    print(f"❌ CTP 网关添加失败: {e}")
    sys.exit(1)

# ==============================================================================
# 配置连接
# ==============================================================================

print("配置 OpenCTP TTS 连接...")
gateway_setting = {
    "用户名": "17130",
    "密码": "123456",
    "经纪商代码": "9999",
    "交易服务器": "tcp://trading.openctp.cn:30001",
    "行情服务器": "tcp://trading.openctp.cn:30011",
    "产品名称": "",
    "授权编码": ""
}

print("连接配置:")
print(f"  用户名: {gateway_setting['用户名']}")
print(f"  交易: {gateway_setting['交易服务器']}")
print(f"  行情: {gateway_setting['行情服务器']}")
print(f"  CTP 网关: vnpy_ctp.gateway.CtpGateway")
print()

# ==============================================================================
# 连接（带超时）
# ==============================================================================

print("连接到 OpenCTP TTS...")

class TimeoutError(Exception):
    pass

# 设置超时
def timeout_handler(signum, frame):
    raise TimeoutError()

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(30)  # 30 秒超时

try:
    main_engine.connect(gateway_setting, "CTP")
    print("✅ 连接请求已发送")
    print("等待 30 秒...")
    print()

    # 持续等待
    while True:
        time.sleep(1)

except TimeoutError:
    print("⚠️  连接超时（30 秒）")
    print()
except Exception as e:
    print(f"❌ 连接异常: {e}")
    print()
finally:
    signal.alarm(0)  # 取消超时

# ==============================================================================
# 查询账户
# ==============================================================================

print("查询账户...")
try:
    main_engine.query_account()
    print("✅ 查询请求已发送")
    print("等待 10 秒...")
    time.sleep(10)
except Exception as e:
    print(f"❌ 查询失败: {e}")
    print()

# ==============================================================================
# 查询合约
# ==============================================================================

print("查询合约...")
try:
    main_engine.query_contract()
    print("✅ 查询请求已发送")
    print("等待 10 秒...")
    time.sleep(10)
except Exception as e:
    print(f"❌ 查询失败: {e}")
    print()

# ==============================================================================
# 结果汇总
# ==============================================================================

print()
print("=" * 80)
print("测试结果汇总")
print("=" * 80)
print()

print("事件统计:")
for event_type, events in all_events.items():
    count = len(events)
    if count > 0:
        print(f"  ✅ {event_type}: {count} 个")
    else:
        print(f"  {event_type}: {count} 个")

print()

print("功能测试结果:")
has_log = len(all_events["log"]) > 0
has_tick = len(all_events["tick"]) > 0
has_account = len(all_events["account"]) > 0
has_contract = len(all_events["contract"]) > 0

print()
if has_log and any("成功" in str(log) for log in all_events["log"]):
    print("✅ 连接: 正常")
else:
    print("❌ 连接: 异常")

if has_account:
    print("✅ 账户查询: 正常")
else:
    print("❌ 账户查询: 异常")

if has_contract:
    print("✅ 合约查询: 正常")
else:
    print("❌ 合约查询: 异常")

if has_account and has_contract:
    print()
    print("🎉 vn.py CTP 网关连接 OpenCTP TTS 成功！")
    print()
    print("📊 收到的数据:")
    print(f"  - 日志: {len(all_events['log'])} 条")
    print(f"  - Tick: {len(all_events['tick'])} 条")
    print(f"  - 账户: {len(all_events['account'])} 条")
    print(f"  - 合约: {len(all_events['contract'])} 条")
    print()
    print("🚀 可以开始测试其他功能！")
else:
    print()
    print("⚠️  功能部分可用")
    print("可能的原因:")
    print("  1. 认证失败")
    print("  2. 密码不正确")
    print("  3. 需要等待密码生效")

print()
print("=" * 80)
