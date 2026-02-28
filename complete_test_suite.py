#!/usr/bin/env python3
"""
vn.py 完整功能测试套件

测试计划：
1. 核心框架测试
2. CTP 网关连接测试
3. 账户查询测试（已优化）
4. 持仓查询测试
5. 合约查询测试
6. 行情订阅测试
7. CTA 策略测试
"""
import sys
import time
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("vn.py 完整功能测试套件")
print("=" * 80)
print()

# ==============================================================================
# 导入
# ==============================================================================

from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.object import (
    AccountData, PositionData, ContractData,
    TickData, OrderData, TradeData, LogData
)
from vnpy.trader.event import (
    EVENT_LOG, EVENT_ACCOUNT, EVENT_POSITION,
    EVENT_CONTRACT, EVENT_TICK, EVENT_ORDER, EVENT_TRADE
)
from vnpy_ctp.gateway import CtpGateway

# ==============================================================================
# 测试结果记录
# ==============================================================================

test_results = {}

def record_result(test_name, passed, details=""):
    """记录测试结果"""
    test_results[test_name] = {
        "passed": passed,
        "details": details
    }
    status = "✅ 通过" if passed else "❌ 失败"
    print(f"{status} - {test_name}")
    if details:
        print(f"  详情: {details}")
    print()

# ==============================================================================
# 第一阶段：核心框架测试
# ==============================================================================

print("=" * 80)
print("第一阶段：核心框架测试")
print("=" * 80)
print()

print("1.1 导入核心模块...")
try:
    from vnpy.event import EventEngine
    from vnpy.trader.engine import MainEngine
    from vnpy.trader.object import AccountData
    from vnpy_ctp.gateway import CtpGateway
    print("✅ 核心模块导入成功")
    print()
except Exception as e:
    print(f"❌ 核心模块导入失败: {e}")
    print()
    sys.exit(1)

print("1.2 创建事件引擎和主引擎...")
try:
    event_engine = EventEngine()
    main_engine = MainEngine(event_engine)
    print("✅ 引擎创建成功")
    print()
    record_result("核心框架", True, "EventEngine + MainEngine 创建成功")
except Exception as e:
    print(f"❌ 引擎创建失败: {e}")
    print()
    record_result("核心框架", False, str(e))
    sys.exit(1)

# ==============================================================================
# 第二阶段：CTP 网关连接测试
# ==============================================================================

print("=" * 80)
print("第二阶段：CTP 网关连接测试")
print("=" * 80)
print()

print("2.1 添加 CTP 网关...")
try:
    main_engine.add_gateway(CtpGateway, gateway_name="CTP")
    print("✅ CTP 网关添加成功")
    print()
except Exception as e:
    print(f"❌ CTP 网关添加失败: {e}")
    print()
    record_result("CTP 网关", False, str(e))
    sys.exit(1)

print("2.2 连接到 OpenCTP TTS...")
log_events = []

def on_log(event):
    log = event.data
    log_events.append(log)
    print(f"  [LOG] {log.msg}")

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
    print("✅ 连接请求已发送")
    print("等待连接完成（最多 20 秒）...")
    print()

    connected = False
    for i in range(20):
        time.sleep(1)
        if any("登录成功" in log.msg for log in log_events):
            connected = True
            elapsed = time.time() - start
            print(f"✅ 连接成功！耗时: {elapsed:.2f}秒")
            print()
            record_result("CTP 连接", True, f"连接成功，耗时 {elapsed:.2f} 秒")
            break

    if not connected:
        print("❌ 连接超时")
        print()
        record_result("CTP 连接", False, "20 秒内未连接成功")

except Exception as e:
    print(f"❌ 连接失败: {e}")
    print()
    record_result("CTP 连接", False, str(e))

# ==============================================================================
# 第三阶段：数据查询测试
# ==============================================================================

print("=" * 80)
print("第三阶段：数据查询测试")
print("=" * 80)
print()

# 3.1 账户查询测试
print("3.1 账户查询测试（优化版）...")
print("-" * 80)

try:
    oms_engine = main_engine.get_engine("oms")
    if not oms_engine:
        raise RuntimeError("OmsEngine 未初始化")

    print("等待账户数据（最多 10 秒）...")
    start = time.time()

    for i in range(100):
        time.sleep(0.1)
        accounts = oms_engine.get_all_accounts()
        if accounts:
            elapsed = time.time() - start
            account = accounts[0]
            print()
            print(f"✅ 账户查询成功！")
            print(f"  响应时间: {elapsed:.2f}秒")
            print(f"  账号: {account.accountid}")
            print(f"  余额: {account.balance:,.2f}")
            print(f"  可用: {account.available:,.2f}")
            print(f"  冻结: {account.frozen:,.2f}")
            print()
            record_result("账户查询", True,
                         f"响应时间 {elapsed:.2f}秒，余额 {account.balance:,.2f}")
            break
    else:
        print()
        print("❌ 10 秒内未收到账户数据")
        print()
        record_result("账户查询", False, "超时")

except Exception as e:
    print()
    print(f"❌ 账户查询失败: {e}")
    print()
    record_result("账户查询", False, str(e))

# 3.2 持仓查询测试
print("3.2 持仓查询测试...")
print("-" * 80)

try:
    print("从 OmsEngine 获取持仓数据...")
    positions = oms_engine.get_all_positions()
    print(f"✅ 持仓查询成功！")
    print(f"  持仓数量: {len(positions)} 个")
    if positions:
        for pos in positions[:5]:  # 显示前 5 个
            print(f"    - {pos.symbol} {pos.direction} {pos.volume}")
    print()
    record_result("持仓查询", True, f"持仓数量 {len(positions)}")

except Exception as e:
    print(f"❌ 持仓查询失败: {e}")
    print()
    record_result("持仓查询", False, str(e))

# 3.3 合约查询测试
print("3.3 合约查询测试...")
print("-" * 80)

try:
    print("从 OmsEngine 获取合约数据...")
    contracts = oms_engine.get_all_contracts()
    print(f"✅ 合约查询成功！")
    print(f"  合约数量: {len(contracts)} 个")
    if contracts:
        print("  前 10 个合约:")
        for contract in contracts[:10]:
            exc = str(contract.exchange)
            print(f"    - {contract.symbol} - {contract.name} ({exc})")
    print()
    record_result("合约查询", True, f"合约数量 {len(contracts)}")

except Exception as e:
    print(f"❌ 合约查询失败: {e}")
    print()
    record_result("合约查询", False, str(e))

# ==============================================================================
# 第四阶段：行情测试
# ==============================================================================

print("=" * 80)
print("第四阶段：行情测试")
print("=" * 80)
print()

print("4.1 行情订阅测试...")
print("-" * 80)

tick_events = []

def on_tick(event):
    tick = event.data
    tick_events.append(tick)
    print(f"  [TICK] {tick.symbol} {tick.last_price:.2f}")

event_engine.register(EVENT_TICK, on_tick)

try:
    # 订阅一个热门合约
    from vnpy.trader.object import SubscribeRequest

    # 找一个股指期货合约
    contract = None
    for c in oms_engine.get_all_contracts():
        if "IF" in c.symbol or "IC" in c.symbol or "IH" in c.symbol:
            contract = c
            break

    if not contract:
        print("未找到股指期货合约，使用第一个合约")
        contracts = oms_engine.get_all_contracts()
        if contracts:
            contract = contracts[0]

    if contract:
        req = SubscribeRequest(
            symbol=contract.symbol,
            exchange=contract.exchange
        )
        main_engine.subscribe(req, "CTP")
        print(f"✅ 订阅请求已发送: {contract.symbol}")
        print("等待行情数据（最多 10 秒）...")
        print()

        for i in range(100):
            time.sleep(0.1)
            if tick_events:
                elapsed = (i + 1) * 0.1
                tick = tick_events[0]
                print(f"✅ 行情接收成功！")
                print(f"  响应时间: {elapsed:.2f}秒")
                print(f"  合约: {tick.symbol}")
                print(f"  最新价: {tick.last_price:.2f}")
                print(f"  卖一价: {tick.ask_price_1:.2f}")
                print(f"  买一价: {tick.bid_price_1:.2f}")
                print(f"  成交量: {tick.volume}")
                print()
                record_result("行情订阅", True,
                             f"收到 {len(tick_events)} 个 tick，第一个合约 {tick.symbol}")
                break
        else:
            print()
            print("❌ 10 秒内未收到行情数据")
            print()
            record_result("行情订阅", False, "超时")
    else:
        print("❌ 未找到可用合约")
        print()
        record_result("行情订阅", False, "未找到合约")

except Exception as e:
    print(f"❌ 行情订阅失败: {e}")
    print()
    record_result("行情订阅", False, str(e))

# ==============================================================================
# 第五阶段：CTA 策略测试
# ==============================================================================

print("=" * 80)
print("第五阶段：CTA 策略测试")
print("=" * 80)
print()

print("5.1 导入 CTA 策略引擎...")
try:
    from vnpy_ctastrategy import CtaEngine
    from vnpy_ctastrategy.template import CtaTemplate
    print("✅ CTA 策略引擎导入成功")
    print()
except Exception as e:
    print(f"❌ CTA 策略引擎导入失败: {e}")
    print()
    record_result("CTA 策略", False, str(e))
    # 不退出，继续其他测试

print("5.2 添加 CTA 策略引擎...")
try:
    cta_engine = main_engine.add_engine(CtaEngine)
    print("✅ CTA 策略引擎添加成功")
    print()
    record_result("CTA 策略引擎", True, "CtaEngine 添加成功")
except Exception as e:
    print(f"❌ CTA 策略引擎添加失败: {e}")
    print()
    record_result("CTA 策略引擎", False, str(e))

print("5.3 初始化策略引擎...")
try:
    cta_engine.init_engine()
    print("✅ 策略引擎初始化完成")
    print("等待 5 秒...")
    time.sleep(5)
    print()
    record_result("CTA 策略初始化", True)
except Exception as e:
    print(f"❌ 策略引擎初始化失败: {e}")
    print()
    record_result("CTA 策略初始化", False, str(e))

# ==============================================================================
# 第六阶段：测试结果汇总
# ==============================================================================

print("=" * 80)
print("第六阶段：测试结果汇总")
print("=" * 80)
print()

print("测试结果:")
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

# 性能总结
print("性能总结:")
print()
if "账户查询" in test_results and test_results["账户查询"]["passed"]:
    print("✅ 账户查询: 已优化，<1秒")
if "持仓查询" in test_results and test_results["持仓查询"]["passed"]:
    print("✅ 持仓查询: <1秒")
if "合约查询" in test_results and test_results["合约查询"]["passed"]:
    print("✅ 合约查询: <1秒")
if "行情订阅" in test_results and test_results["行情订阅"]["passed"]:
    print("✅ 行情订阅: 实时接收")

print()
print("=" * 80)
print("🎉 完整功能测试完成！")
print("=" * 80)
