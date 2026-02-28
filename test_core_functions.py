#!/usr/bin/env python3
"""
VnPy 核心功能测试 - 修复版

测试内容:
1. 核心框架
2. CTP 网关连接
3. 数据查询
4. 行情订阅
5. CTA 策略引擎
"""
import sys
import time
from datetime import datetime
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("VnPy 核心功能测试")
print("=" * 80)
print()

# ==============================================================================
# 导入
# ==============================================================================

from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.object import (
    TickData, BarData, OrderData, TradeData, PositionData,
    ContractData, SubscribeRequest
)
from vnpy.trader.constant import (
    Interval, Exchange, Direction, OrderType, Offset, Status
)
from vnpy.trader.event import (
    EVENT_TICK, EVENT_LOG
)
from vnpy_ctp.gateway import CtpGateway
from vnpy_ctastrategy import CtaEngine

# ==============================================================================
# 测试结果记录
# ==============================================================================

test_results = {}

def record_result(test_name, passed, details=""):
    """记录测试结果"""
    test_results[test_name] = {
        "passed": passed,
        "details": details,
        "timestamp": datetime.now().isoformat()
    }
    status = "✅ 通过" if passed else "❌ 失败"
    print(f"{status} - {test_name}")
    if details:
        print(f"  详情: {details}")
    print()

# ==============================================================================
# 第一阶段：核心框架
# ==============================================================================

print("1.1 创建事件引擎和主引擎...")
try:
    event_engine = EventEngine()
    main_engine = MainEngine(event_engine)
    print("✅ 引擎创建成功\n")
    record_result("核心框架", True, "EventEngine + MainEngine 创建成功")
except Exception as e:
    print(f"❌ 引擎创建失败: {e}\n")
    record_result("核心框架", False, str(e))
    sys.exit(1)

# ==============================================================================
# 第二阶段：CTP 连接
# ==============================================================================

print("1.2 添加 CTP 网关...")
try:
    main_engine.add_gateway(CtpGateway, gateway_name="CTP")
    print("✅ CTP 网关添加成功\n")
except Exception as e:
    print(f"❌ CTP 网关添加失败: {e}\n")
    record_result("CTP 网关", False, str(e))
    sys.exit(1)

print("1.3 连接 OpenCTP...")
log_events = []

def on_log(event):
    log = event.data
    log_events.append(log)

event_engine.register(EVENT_LOG, on_log)

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

try:
    start = time.time()
    main_engine.connect(gateway_setting, "CTP")
    print("等待连接完成...")

    connected = False
    for i in range(20):
        time.sleep(1)
        if any("登录成功" in log.msg for log in log_events):
            connected = True
            elapsed = time.time() - start
            print(f"✅ 连接成功！耗时: {elapsed:.2f}秒\n")
            record_result("CTP 连接", True, f"连接成功，耗时 {elapsed:.2f} 秒")
            break

    if not connected:
        print("❌ 连接超时\n")
        record_result("CTP 连接", False, "20 秒内未连接成功")

except Exception as e:
    print(f"❌ 连接失败: {e}\n")
    record_result("CTP 连接", False, str(e))

# ==============================================================================
# 第三阶段：数据查询
# ==============================================================================

print("2.1 账户查询...")
try:
    oms_engine = main_engine.get_engine("oms")
    if not oms_engine:
        raise RuntimeError("OmsEngine 未初始化")

    print("等待账户数据...")
    start = time.time()

    for i in range(100):
        time.sleep(0.1)
        accounts = oms_engine.get_all_accounts()
        if accounts:
            elapsed = time.time() - start
            account = accounts[0]
            print(f"✅ 账户查询成功！")
            print(f"  响应时间: {elapsed:.2f}秒")
            print(f"  账号: {account.accountid}")
            print(f"  余额: {account.balance:,.2f}")
            print(f"  可用: {account.available:,.2f}")
            print(f"  冻结: {account.frozen:,.2f}\n")
            record_result("账户查询", True, f"响应时间 {elapsed:.2f}秒，余额 {account.balance:,.2f}")
            break
    else:
        print("❌ 10 秒内未收到账户数据\n")
        record_result("账户查询", False, "超时")

except Exception as e:
    print(f"❌ 账户查询失败: {e}\n")
    record_result("账户查询", False, str(e))

print("2.2 持仓查询...")
try:
    positions = oms_engine.get_all_positions()
    print(f"✅ 持仓查询成功！")
    print(f"  持仓数量: {len(positions)} 个\n")
    record_result("持仓查询", True, f"持仓数量 {len(positions)}")
except Exception as e:
    print(f"❌ 持仓查询失败: {e}\n")
    record_result("持仓查询", False, str(e))

print("2.3 合约查询...")
try:
    contracts = oms_engine.get_all_contracts()
    print(f"✅ 合约查询成功！")
    print(f"  合约数量: {len(contracts)} 个\n")
    record_result("合约查询", True, f"合约数量 {len(contracts)}")
except Exception as e:
    print(f"❌ 合约查询失败: {e}\n")
    record_result("合约查询", False, str(e))

# ==============================================================================
# 第四阶段：行情订阅
# ==============================================================================

print("3.1 行情订阅...")
tick_events = []

def on_tick(event):
    tick = event.data
    tick_events.append(tick)

event_engine.register(EVENT_TICK, on_tick)

try:
    # 找一个热门合约
    contract = None
    for c in contracts:
        if "IF" in c.symbol or "IC" in c.symbol or "IH" in c.symbol:
            contract = c
            break

    if not contract:
        contract = contracts[0]

    req = SubscribeRequest(
        symbol=contract.symbol,
        exchange=contract.exchange
    )
    main_engine.subscribe(req, "CTP")
    print(f"✅ 订阅 {contract.symbol} 行情")
    print("等待行情数据...")

    for i in range(10):
        time.sleep(1)
        if tick_events:
            tick = tick_events[0]
            print(f"✅ 行情接收成功！")
            print(f"  合约: {tick.symbol}")
            print(f"  最新价: {tick.last_price:.2f}")
            print(f"  卖一: {tick.ask_price_1:.2f}")
            print(f"  买一: {tick.bid_price_1:.2f}")
            print(f"  成交量: {tick.volume}\n")
            record_result("行情订阅", True, f"收到 {len(tick_events)} 个 tick")
            break
    else:
        print("❌ 10 秒内未收到行情数据\n")
        record_result("行情订阅", False, "超时")

except Exception as e:
    print(f"❌ 行情订阅失败: {e}\n")
    record_result("行情订阅", False, str(e))

# ==============================================================================
# 第五阶段：CTA 引擎
# ==============================================================================

print("4.1 添加 CTA 策略引擎...")
try:
    cta_engine = main_engine.add_engine(CtaEngine)
    print("✅ CTA 策略引擎添加成功\n")
    record_result("CTA 引擎添加", True)
except Exception as e:
    print(f"❌ CTA 策略引擎添加失败: {e}\n")
    record_result("CTA 引擎添加", False, str(e))

print("4.2 初始化 CTA 引擎...")
try:
    cta_engine.init_engine()
    print("✅ 策略引擎初始化完成")
    print("等待 5 秒...")
    time.sleep(5)
    print()
    record_result("CTA 引擎初始化", True)
except Exception as e:
    print(f"❌ 策略引擎初始化失败: {e}\n")
    record_result("CTA 引擎初始化", False, str(e))

# ==============================================================================
# 测试结果汇总
# ==============================================================================

print("=" * 80)
print("测试结果汇总")
print("=" * 80)
print()

passed_count = 0
failed_count = 0

for test_name, result in test_results.items():
    status = "✅" if result["passed"] else "❌"
    print(f"{status} {test_name}")
    if result["details"]:
        print(f"   {result['details']}")

    if result["passed"]:
        passed_count += 1
    else:
        failed_count += 1

print()
print("=" * 80)
print(f"测试完成: {passed_count} 通过 / {failed_count} 失败 / {len(test_results)} 总计")
print("=" * 80)
print()
print("测试完成时间:", datetime.now().isoformat())
print()
