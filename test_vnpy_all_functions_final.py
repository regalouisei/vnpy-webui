#!/usr/bin/env python3
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("vn.py 无界面模式 - 所有功能测试")
print("=" * 80)
print()

try:
    from vnpy.event import EventEngine
    from vnpy.trader.engine import MainEngine
    from vnpy.trader.object import BarData, TickData, OrderData, TradeData, PositionData, AccountData, ContractData
    from vnpy.trader.constant import Interval, Exchange
    from vnpy.trader.logger import INFO, logger
    print("vn.py 核心模块导入成功")
except Exception as e:
    print(f"vn.py 核心模块导入失败: {e}")
    sys.exit(1)

try:
    from vnpy_ctp.gateway import CtpGateway
    print("CTP 网关导入成功")
except Exception as e:
    print(f"CTP 网关导入失败: {e}")
    sys.exit(1)

try:
    from vnpy_ctastrategy.template import CtaTemplate
    from vnpy_ctastrategy.base import EVENT_CTA_LOG
    print("CTA 策略导入成功")
except Exception as e:
    print(f"CTA 策略导入失败: {e}")
    sys.exit(1)

print()
print("=" * 80)
print("创建引擎")
print("=" * 80)

event_engine = EventEngine()
main_engine = MainEngine(event_engine)

print("事件引擎创建成功")
print("主引擎创建成功")

print()
print("=" * 80)
print("添加网关")
print("=" * 80)

try:
    main_engine.add_gateway(CtpGateway, gateway_name="CTP")
    print("CTP 网关添加成功")
except Exception as e:
    print(f"CTP 网关添加失败: {e}")
    sys.exit(1)

print()
print("=" * 80)
print("添加 CTA 策略引擎")
print("=" * 80)

try:
    cta_engine = main_engine.add_engine(CtaEngine)
    print("CTA 策略引擎添加成功")
except Exception as e:
    print(f"CTA 策略引擎添加失败: {e}")
    sys.exit(1)

print()
print("=" * 80)
print("注册事件监听")
print("=" * 80)

all_events = {
    "log": [],
    "tick": [],
    "bar": [],
    "account": [],
    "contract": [],
    "order": [],
    "trade": [],
    "position": []
}

def make_handler(event_type):
    def handler(event):
        data = event.data
        all_events[event_type].append(data)
        print(f"[{event_type.upper()}] {data}")
    return handler

event_engine.register(EVENT_CTA_LOG, make_handler("cta_log"))

from vnpy.trader.event import (
    EVENT_TICK, EVENT_BAR, EVENT_CONTRACT,
    EVENT_ACCOUNT, EVENT_ORDER, EVENT_TRADE, EVENT_POSITION
)

event_engine.register(EVENT_TICK, make_handler("tick"))
event_engine.register(EVENT_BAR, make_handler("bar"))
event_engine.register(EVENT_CONTRACT, make_handler("contract"))
event_engine.register(EVENT_ACCOUNT, make_handler("account"))
event_engine.register(EVENT_ORDER, make_handler("order"))
event_engine.register(EVENT_TRADE, make_handler("trade"))
event_engine.register(EVENT_POSITION, make_handler("position"))

print("事件监听器注册成功")

print()
print("=" * 80)
print("连接配置")
print("=" * 80)

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

print("账号: 17130")
print("交易: tcp://trading.openctp.cn:30001")
print("行情: tcp://trading.openctp.cn:30011")
print()

print("=" * 80)
print("连接 CTP 网关")
print("=" * 80)

try:
    main_engine.connect(gateway_setting, "CTP")
    print("连接请求已发送")
except Exception as e:
    print(f"连接失败: {e}")
    sys.exit(1)

import time
time.sleep(30)

print()
print("=" * 80)
print("查询账户")
print("=" * 80)

try:
    main_engine.query_account()
    print("查询请求已发送")
    time.sleep(10)
except Exception as e:
    print(f"查询失败: {e}")
    sys.exit(1)

print()
print("=" * 80)
print("查询合约")
print("=" * 80)

try:
    main_engine.query_contract()
    print("查询请求已发送")
    time.sleep(10)
except Exception as e:
    print(f"查询失败: {e}")
    sys.exit(1)

print()
print("=" * 80)
print("添加策略")
print("=" * 80)

class SimpleDoubleMaStrategy(CtaTemplate):
    fast_window = 10
    slow_window = 30
    fixed_size = 1

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        self.cta_engine = cta_engine
        self.strategy_name = strategy_name
        self.vt_symbol = vt_symbol
        self.fast_data = []
        self.slow_data = []

    def on_init(self):
        print(f"策略初始化: {self.strategy_name}")

    def on_start(self):
        print(f"策略启动: {self.strategy_name}")

    def on_stop(self):
        print(f"策略停止: {self.strategy_name}")

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
                        print(f"金叉做多 @ {cta_bar.close_price} ({cta_bar.datetime})")
                    elif fast_ma < slow_ma and self.pos > 0:
                        self.sell(cta_bar.close_price, self.fixed_size)
                        print(f"死叉平仓 @ {cta_bar.close_price} ({cta_bar.datetime})")

    def on_order(self, cta_order):
        pass

    def on_trade(self, cta_trade):
        pass

    def on_position(self, cta_position):
        pass

try:
    cta_engine.add_strategy(SimpleDoubleMaStrategy, {
        "vt_symbol": "IF2501.CFFEX",
        "fast_window": 10,
        "slow_window": 30
    })
    print("策略添加成功")
except Exception as e:
    print(f"策略添加失败: {e}")
    sys.exit(1)

print()
print("=" * 80)
print("初始化策略")
print("=" * 80)

try:
    cta_engine.init_engine()
    print("策略引擎初始化成功")
    time.sleep(10)
except Exception as e:
    print(f"策略初始化失败: {e}")
    sys.exit(1)

try:
    cta_engine.init_all_strategies()
    print("所有策略初始化完成")
    time.sleep(10)
except Exception as e:
    print(f"所有策略初始化失败: {e}")
    sys.exit(1)

try:
    cta_engine.start_all_strategies()
    print("所有策略启动完成")
    time.sleep(10)
except Exception as e:
    print(f"所有策略启动失败: {e}")
    sys.exit(1)

print()
print("=" * 80)
print("等待策略运行 (60 秒)")
print("=" * 80)

time.sleep(60)

print()
print("=" * 80)
print("测试结果汇总")
print("=" * 80)

print("事件统计:")
for event_type, events in all_events.items():
    count = len(events)
    if count > 0:
        print(f"  {event_type}: {count} 个")
    else:
        print(f"  {event_type}: {count} 个")

print()
print("账户数据:")
if all_events["account"]:
    for acc in all_events["account"]:
        print(f"  账号: {acc.accountid}")
        print(f"  余额: {acc.balance:,.2f}")
        print(f"  可用: {acc.available:,.2f}")
else:
    print("  未收到账户数据")

print()
print("合约数据:")
if all_events["contract"]:
    print(f"  合约数量: {len(all_events['contract'])} 个")
    for i, contract in enumerate(all_events["contract"][:5], 1):
        exc = str(contract.exchange)
        print(f"  [{i}] {contract.symbol} - {contract.name} ({exc})")
else:
    print("  未收到合约数据")

print()
print("CTA 日志:")
if all_events["cta_log"]:
    print(f"  CTA 日志数量: {len(all_events['cta_log'])} 条")
    relevant_logs = [str(log) for log in all_events["cta_log"]
                    if any(word in str(log) for word in ["初始化", "启动", "停止", "金叉", "死叉"])]
    for log in relevant_logs[-10]:
        print(f"  {log}")
else:
    print("  未收到 CTA 日志")

print()
print("=" * 80)

has_account = len(all_events["account"]) > 0
has_contract = len(all_events["contract"]) > 0
has_cta_log = len(all_events["cta_log"]) > 0

if has_account and has_contract:
    print("所有功能正常！")
    print("可以开始 Web 界面开发")
elif has_account or has_contract:
    print("部分功能正常")
    print("需要检查网络或配置")
else:
    print("功能异常")
    print("需要检查 vn.py 安装或配置")

print("=" * 80)
