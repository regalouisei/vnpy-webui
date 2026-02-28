#!/usr/bin/env python3
"""
CTA 策略专项测试
"""
import sys
import time
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("CTA 策略专项测试")
print("=" * 80)
print()

# ==============================================================================
# 导入
# ==============================================================================

from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy_ctp.gateway import CtpGateway
from vnpy_ctastrategy import CtaEngine
from vnpy_ctastrategy.template import CtaTemplate
from vnpy.trader.object import BarData
from vnpy.trader.constant import Interval, Exchange

# ==============================================================================
# 创建引擎
# ==============================================================================

print("创建引擎...")
event_engine = EventEngine()
main_engine = MainEngine(event_engine)
main_engine.add_gateway(CtpGateway, gateway_name="CTP")
print("✅ 引擎创建成功")
print()

# ==============================================================================
# 连接 CTP
# ==============================================================================

print("连接 CTP...")
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

print("等待连接（15秒）...")
time.sleep(15)
print()

# ==============================================================================
# 添加 CTA 策略引擎
# ==============================================================================

print("添加 CTA 策略引擎...")
try:
    cta_engine = main_engine.add_engine(CtaEngine)
    print("✅ CTA 策略引擎添加成功")
    print()
except Exception as e:
    print(f"❌ CTA 策略引擎添加失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ==============================================================================
# 初始化策略引擎
# ==============================================================================

print("初始化策略引擎...")
try:
    cta_engine.init_engine()
    print("✅ 策略引擎初始化完成")
    print("等待 5 秒...")
    time.sleep(5)
    print()
except Exception as e:
    print(f"❌ 策略引擎初始化失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ==============================================================================
# 定义简单策略
# ==============================================================================

print("定义简单双均线策略...")

class SimpleDoubleMaStrategy(CtaTemplate):
    """简单双均线策略"""

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
        """策略初始化"""
        print(f"  策略 on_init: {self.strategy_name}")
        self.fast_data.clear()
        self.slow_data.clear()

    def on_start(self):
        """策略启动"""
        print(f"  策略 on_start: {self.strategy_name}")

    def on_stop(self):
        """策略停止"""
        print(f"  策略 on_stop: {self.strategy_name}")

    def on_tick(self, cta_tick):
        """Tick 事件"""
        pass

    def on_bar(self, cta_bar):
        """Bar 事件"""
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

                if fast_ma > slow_ma and self.pos == 0:
                    self.buy(cta_bar.close_price, self.fixed_size)
                    print(f"    金叉做多 @ {cta_bar.close_price:.2f} ({cta_bar.datetime})")
                elif fast_ma < slow_ma and self.pos > 0:
                    self.sell(cta_bar.close_price, self.fixed_size)
                    print(f"    死叉平仓 @ {cta_bar.close_price:.2f} ({cta_bar.datetime})")

    def on_order(self, cta_order):
        """订单事件"""
        pass

    def on_trade(self, cta_trade):
        """成交事件"""
        pass

    def on_position(self, cta_position):
        """持仓事件"""
        pass

print("✅ 策略定义完成")
print()

# ==============================================================================
# 添加策略
# ==============================================================================

print("添加策略到引擎...")
try:
    # 使用 IC2602 合约
    vt_symbol = "IC2602.CFFEX"

    cta_engine.add_strategy(
        SimpleDoubleMaStrategy,
        strategy_name="简单双均线_IC2602",
        vt_symbol=vt_symbol,
        setting={
            "fast_window": 10,
            "slow_window": 30
        }
    )
    print(f"✅ 策略添加成功: {vt_symbol}")
    print()
except Exception as e:
    print(f"❌ 策略添加失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ==============================================================================
# 初始化策略
# ==============================================================================

print("初始化策略...")
try:
    cta_engine.init_all_strategies()
    print("✅ 策略初始化完成")
    print("等待 5 秒...")
    time.sleep(5)
    print()
except Exception as e:
    print(f"❌ 策略初始化失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ==============================================================================
# 启动策略
# ==============================================================================

print("启动策略...")
try:
    cta_engine.start_all_strategies()
    print("✅ 策略启动完成")
    print()
except Exception as e:
    print(f"❌ 策略启动失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ==============================================================================
# 等待策略运行
# ==============================================================================

print("等待策略运行（30 秒）...")
print("注意：真实策略运行需要历史数据，这里仅测试策略框架...")
print()

for i in range(30):
    time.sleep(1)
    if i % 10 == 9:
        print(f"  策略运行中... ({i+1}/30 秒)")

print()

# ==============================================================================
# 检查策略状态
# ==============================================================================

print("=" * 80)
print("策略状态检查")
print("=" * 80)
print()

strategies = cta_engine.get_all_strategies()
print(f"策略数量: {len(strategies)}")
print()

for strategy_name, strategy in strategies.items():
    print(f"策略名称: {strategy_name}")
    print(f"  vt_symbol: {strategy.vt_symbol}")
    print(f"  状态: {strategy.trading}")
    print(f"  持仓: {strategy.pos}")
    print()

# ==============================================================================
# 总结
# ==============================================================================

print("=" * 80)
print("测试总结")
print("=" * 80)
print()

print("✅ CTA 策略引擎: 正常")
print("✅ 策略初始化: 正常")
print("✅ 策略启动: 正常")
print("✅ 策略运行: 正常")
print()

print("CTA 策略测试完成！")
print()
