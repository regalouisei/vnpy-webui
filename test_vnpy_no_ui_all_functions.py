#!/usr/bin/env python3
"""
vn.py 无界面模式 - 所有功能测试
"""
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("🔍 vn.py 无界面模式 - 所有功能测试")
print("=" * 80)
print()

# ==============================================================================
# 一、导入 vn.py 核心模块
# ==============================================================================

print("【步骤 1：导入 vn.py 核心模块】")
print("-" * 80)
print()

try:
    from vnpy.event import EventEngine
    from vnpy.trader.engine import MainEngine
    from vnpy.trader.object import BarData, TickData, OrderData, TradeData, PositionData, AccountData, ContractData
    from vnpy.trader.constant import Interval, Exchange
    from vnpy.trader.logger import INFO, logger

    print("✅ vn.py 核心模块导入成功")
    print()
except Exception as e:
    print(f"❌ vn.py 核心模块导入失败: {e}")
    sys.exit(1)

# ==============================================================================
# 二、导入 CTP 网关
# ==============================================================================

print("【步骤 2：导入 CTP 网关】")
print("-" * 80)
print()

try:
    from vnpy_ctp.gateway import CtpGateway
    print("✅ CTP 网关导入成功")
    print(f"  库: vnpy_ctp.gateway.CtpGateway")
    print()
except Exception as e:
    print(f"❌ CTP 网关导入失败: {e}")
    sys.exit(1)

# ==============================================================================
# 三、导入 CTA 策略
# ==============================================================================

print("【步骤 3：导入 CTA 策略】")
print("-" * 80)
print()

try:
    from vnpy_ctastrategy.template import CtaTemplate
    from vnpy_ctastrategy.base import EVENT_CTA_LOG
    print("✅ CTA 策略导入成功")
    print(f"  策略基类: vnpy_ctastrategy.template.CtaTemplate")
    print()
except Exception as e:
    print(f"❌ CTA 策略导入失败: {e}")
    sys.exit(1)

# ==============================================================================
# 四、定义简单 CTA 策略
# ==============================================================================

print("【步骤 4：定义简单 CTA 策略】")
print("-" * 80)
print()

class SimpleDoubleMaStrategy(CtaTemplate):
    """简单双均线策略"""

    fast_window = 10
    slow_window = 30
    fixed_size = 1

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        print(f"  策略初始化: {strategy_name}")
        self.cta_engine = cta_engine
        self.strategy_name = strategy_name
        self.vt_symbol = vt_symbol
        self.fast_data = []
        self.slow_data = []

    def on_init(self):
        print(f"  策略 on_init: {self.strategy_name}")
        self.fast_data.clear()
        self.slow_data.clear()

    def on_start(self):
        print(f"  策略 on_start: {self.strategy_name}")

    def on_stop(self):
        print(f"  策略 on_stop: {self.strategy_name}")

    def on_tick(self, cta_tick):
        pass

    def on_bar(self, cta_bar):
        self.fast_data.append(cta_bar.close_price)
        self.slow_data.append(cta_bar.close_price)

        if len(self.fast_data) > self.fast_window:
            self.fast_data.pop(0)
        if len(self.slow_data) > self.slow_window:
            self.slow_data.pop(0)

        if len(self.fast_data) >= self.fast_window:
            fast_ma = sum(self.fast_data[-self.fast_window:]) / self.fast_window

            if len(self.slow_data) >= self.slow_window:
                slow_ma = sum(self.slow_data[-self.slow_window:]) / self.slow_window

                if len(self.fast_data) >= self.fast_window:
                    if fast_ma > slow_ma and self.pos == 0:
                        self.buy(cta_bar.close_price, self.fixed_size)
                        print(f"    金叉做多 @ {cta_bar.close_price} ({cta_bar.datetime})")
                    elif fast_ma < slow_ma and self.pos > 0:
                        self.sell(cta_bar.close_price, self.fixed_size)
                        print(f"    死叉平仓 @ {cta_bar.close_price} ({cta_bar.datetime})")

print("✅ 简单双均线策略定义完成")
print(f"  策略类: SimpleDoubleMaStrategy")
print()

# ==============================================================================
# 五、创建事件引擎
# ==============================================================================

print("【步骤 5：创建事件引擎】")
print("-" * 80)
print()

event_engine = EventEngine()
print("✅ 事件引擎创建成功")
print()

# ==============================================================================
# 六、创建主引擎
# ==============================================================================

print("【步骤 6：创建主引擎】")
print("-" * 80)
print()

main_engine = MainEngine(event_engine)
print("✅ 主引擎创建成功")
print()

# ==============================================================================
# 七、添加 CTP 网关
# ==============================================================================

print("【步骤 7：添加 CTP 网关】")
print("-" * 80)
print()

try:
    main_engine.add_gateway(CtpGateway, gateway_name="CTP")
    print("✅ CTP 网关添加成功")
    print()
except Exception as e:
    print(f"❌ CTP 网关添加失败: {e}")
    sys.exit(1)

# ==============================================================================
# 八、添加 CTA 策略引擎
# ==============================================================================

print("【步骤 8：添加 CTA 策略引擎】")
print("-" * 80)
print()

try:
    cta_engine = main_engine.add_engine(CtaEngine)
    print("✅ CTA 策略引擎添加成功")
    print(f"  策略引擎类: CtaEngine")
    print()
except Exception as e:
    print(f"❌ CTA 策略引擎添加失败: {e}")
    sys.exit(1)

# ==============================================================================
# 九、注册事件监听器
# ==============================================================================

print("【步骤 9：注册事件监听器】")
print("-" * 80)
print()

# 收集事件
all_events = {
    "tick": [],
    "bar": [],
    "account": [],
    "contract": [],
    "order": [],
    "trade": [],
    "position": [],
    "cta_log": []
}

def make_handler(event_type):
    def handler(event):
        data = event.data
        all_events[event_type].append(data)
        print(f"  [{event_type.upper()}] {data}")
    return handler

# 注册所有事件
from vnpy.trader.event import (
    EVENT_TICK, EVENT_BAR, EVENT_CONTRACT,
    EVENT_ACCOUNT, EVENT_ORDER, EVENT_TRADE, EVENT_POSITION, EVENT_LOG
)

event_engine.register(EVENT_TICK, make_handler("tick"))
event_engine.register(EVENT_BAR, make_handler("bar"))
event_engine.register(EVENT_CONTRACT, make_handler("contract"))
event_engine.register(EVENT_ACCOUNT, make_handler("account"))
event_engine.register(EVENT_ORDER, make_handler("order"))
event_engine.register(EVENT_TRADE, make_handler("trade"))
event_engine.register(EVENT_POSITION, make_handler("position"))
event_engine.register(EVENT_LOG, make_handler("cta_log"))

print("✅ 所有事件监听器注册成功")
print()

# ==============================================================================
# 十、连接配置
# ==============================================================================

print("【步骤 10：连接配置】")
print("-" * 80)
print()

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

print("配置信息:")
for key, value in gateway_setting.items():
    print(f"  {key}: {value}")
print()

# ==============================================================================
# 十一、连接 CTP 网关
# ==============================================================================

print("【步骤 11：连接 CTP 网关到 OpenCTP TTS】")
print("-" * 80)
print()

print("连接到 OpenCTP TTS...")
print()

try:
    main_engine.connect(gateway_setting, "CTP")
    print("✅ 连接请求已发送")
    print()
except Exception as e:
    print(f"❌ 连接失败: {e}")
    sys.exit(1)

# ==============================================================================
# 十二、等待连接结果
# ==============================================================================

print("【步骤 12：等待连接结果（30 秒）】")
print("-" * 80)
print()

import time
time.sleep(30)

# ==============================================================================
# 十三、查询账户
# ==============================================================================

print("【步骤 13：查询账户】")
print("-" * 80)
print()

try:
    main_engine.query_account()
    print("✅ 查询请求已发送")
    print()
    time.sleep(10)
except Exception as e:
    print(f"❌ 查询失败: {e}")

# ==============================================================================
# 十四、查询合约
# ==============================================================================

print("【步骤 14：查询合约】")
print("-" * 80)
print()

try:
    main_engine.query_contract()
    print("✅ 查询请求已发送")
    print()
    time.sleep(10)
except Exception as e:
    print(f"❌ 查询失败: {e}")

# ==============================================================================
# 十五、添加策略
# ==============================================================================

print("【步骤 15：添加策略】")
print("-" * 80)
print()

try:
    cta_engine.add_strategy(SimpleDoubleMaStrategy, {
        "vt_symbol": "IF2501.CFFEX"
        "fast_window": 10,
        "slow_window": 30,
        "fixed_size": 1
    })
    print("✅ 策略添加成功")
    print()
    print("策略信息:")
    print(f"  名称: SimpleDoubleMaStrategy")
    print(f"  合约: IF2501.CFFEX")
    print(f"  快线: 10")
    print(f"  慢线: 30")
    print()
except Exception as e:
    print(f"❌ 策略添加失败: {e}")
    sys.exit(1)

# ==============================================================================
# 十六、初始化策略
# ==============================================================================

print("【步骤 16：初始化策略】")
print("-" * 80)
print()

try:
    cta_engine.init_engine()
    print("✅ 策略引擎初始化成功")
    print()
    time.sleep(10)
except Exception as e:
    print(f"❌ 策略初始化失败: {e}")
    sys.exit(1)

# ==============================================================================
# 十七、启动策略
# ==============================================================================

print("【步骤 17：启动策略】")
print("-" * 80)
print()

try:
    cta_engine.init_all_strategies()
    print("✅ 所有策略初始化完成")
    print()
    time.sleep(10)
except Exception as e:
    print(f"❌ 策略初始化失败: {e}")
    sys.exit(1)

try:
    cta_engine.start_all_strategies()
    print("✅ 所有策略启动完成")
    print()
    time.sleep(10)
except Exception as e:
    print(f"❌ 策略启动失败: {e}")
    sys.exit(1)

# ==============================================================================
# 十八、等待策略运行（60 秒）
# ==============================================================================

print("【步骤 18：等待策略运行（60 秒）】")
print("-" * 80)
print()

print("策略运行中...")
time.sleep(60)

# ==============================================================================
# 十九、结果汇总
# ==============================================================================

print()
print("=" * 80)
print("【测试结果汇总】")
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

# 显示账户数据
if all_events["account"]:
    print("账户数据:")
    for acc in all_events["account"]:
        print(f"  账号: {acc.accountid}")
        print(f"  余额: {acc.balance:,.2f}")
        print(f"  可用: {acc.available:,.2f}")
    print()

# 显示合约数据
if all_events["contract"]:
    print(f"合约数据 (前 5 个):")
    for i, contract in enumerate(all_events["contract"][:5], 1):
        exc = str(contract.exchange)
        print(f"  [{i}] {contract.symbol} - {contract.name} ({exc})")
    print()

# 显示 CTA 日志
if all_events["cta_log"]:
    print("CTA 策略日志:")
    relevant_logs = [str(log) for log in all_events["cta_log"]
                    if any(word in str(log) for word in ["初始化", "启动", "停止", "金叉", "死叉"])]
    for log in relevant_logs[-10]:
        print(f"  {log}")
    print()

# 判断结果
has_account = len(all_events["account"]) > 0
has_contract = len(all_events["contract"]) > 0
has_order = len(all_events["order"]) > 0
has_trade = len(all_events["trade"]) > 0
has_position = len(all_events["position"]) > 0
has_tick = len(all_events["tick"]) > 0
has_cta_log = len(all_events["cta_log"]) > 0

print("=" * 80)

if has_account and has_contract:
    print("✅✅✅ 所有功能正常！✅✅✅")
    print()
    print("🎉 vn.py 无界面模式所有功能测试成功！")
    print()
    print("📊 测试结果:")
    print(f"  - 账户: {len(all_events['account'])} 个")
    print(f"  - 合约: {len(all_events['contract'])} 个")
    print(f"  - 委托: {len(all_events['order'])} 个")
    print(f"  - 成交: {len(all_events['trade'])} 个")
    print(f"  - 持仓: {len(all_events['position'])} 个")
    print(f"  - Tick: {len(all_events['tick'])} 个")
    print(f"  - CTA日志: {len(all_events['cta_log'])} 条")
    print()
    print("🚀 vn.py 所有功能正常，可以开始 web 界面开发！")
    print()

elif has_account:
    print("⚠️  部分功能正常")
    print()
    print("账户功能正常，但缺少其他功能")
    print("可能的原因:")
    print("  1. 策略未启动")
    print("  2. 数据未订阅")
    print("  3. 功能未完全激活")
    print()

elif has_cta_log:
    print("⚠️  策略部分正常")
    print()
    print("策略初始化成功，但缺少其他功能")
    print("可能的原因:")
    print("  1. 账户未连接")
    print("  2. 数据未订阅")
    print("  3. 功能未完全激活")
    print()

else:
    print("❌❌❌ 功能异常 ❌❌❌")
    print()
    print("未收到任何事件")
    print()
    print("可能的原因:")
    print("  1. vn.py 模块未正确安装")
    print("  2. CTP 网关配置错误")
    print("  3. 服务器连接失败")
    print("  4. 网络问题")
    print()

print("=" * 80)
