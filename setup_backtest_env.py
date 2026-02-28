#!/usr/bin/env python3
"""
vn.py VeighNa Station 配置和简单策略示例
"""
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("🎉 vn.py VeighNa Station 配置示例")
print("=" * 80)
print()

# ==============================================================================
# 一、创建策略目录
# ==============================================================================

print("【步骤 1：创建策略目录】")
print("-" * 80)
print()

# 策略目录
strategies_dir = "/root/.openclaw/workspace/quant-factory/strategies"
os.makedirs(strategies_dir, exist_ok=True)

print(f"策略目录: {strategies_dir}")
print("✅ 策略目录创建成功")
print()

# ==============================================================================
# 二、创建简单的 CTA 策略
# ==============================================================================

print("【步骤 2：创建简单 CTA 策略】")
print("-" * 80)
print()

strategy_file = os.path.join(strategies_dir, "simple_double_ma_strategy.py")

strategy_code = """
# -*- coding: utf-8 -*-
"""
简单双均线策略（Simple Double MA）
"""

from vnpy_ctastrategy.base import CtaTemplate
from vnpy.trader.object import BarData, TickData, OrderData, TradeData
from vnpy.trader.constant import Interval


class SimpleDoubleMaStrategy(CtaTemplate):
    """简单双均线策略"""

    fast_window = 10
    slow_window = 30
    fixed_size = 1

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        print(f"策略初始化: {strategy_name}")

        self.cta_engine = cta_engine
        self.strategy_name = strategy_name
        self.vt_symbol = vt_symbol
        self.fast_data = []
        self.slow_data = []

    def on_init(self, cta_engine, strategy_name, vt_symbol, setting):
        \"\"\"策略初始化\"\"\"
        print(f"  快线窗口: {self.fast_window}")
        print(f"  慢线窗口: {self.slow_window}")

        # 从 setting 中读取参数
        if "fast_window" in setting:
            self.fast_window = setting["fast_window"]
            print(f"  修改快线窗口: {self.fast_window}")
        if "slow_window" in setting:
            self.slow_window = setting["slow_window"]
            print(f"  修改慢线窗口: {self.slow_window}")

    def on_start(self):
        \"\"\"策略启动\"\"\"
        print(f"策略启动: {self.strategy_name}")

    def on_stop(self):
        \"\"\"策略停止\"\"\"
        print(f"策略停止: {self.strategy_name}")

    def on_tick(self, cta_engine, cta_tick):
        \"\"\"Tick 回调\"\"\"
        pass

    def on_bar(self, cta_engine, cta_bar):
        \"\"\"K 线回调\"\"\"

        # 更新均线数据
        self.fast_data.append(cta_bar.close_price)
        self.slow_data.append(cta_bar.close_price)

        # 保持窗口长度
        if len(self.fast_data) > self.fast_window:
            self.fast_data.pop(0)
        if len(self.slow_data) > self.slow_window:
            self.slow_data.pop(0)

        # 计算均线
        if len(self.fast_data) >= self.fast_window:
            fast_ma = sum(self.fast_data[-self.fast_window:]) / self.fast_window

            if len(self.slow_data) >= self.slow_window:
                slow_ma = sum(self.slow_data[-self.slow_window:]) / self.slow_window

                # 金叉做多，死叉平仓
                if fast_ma > slow_ma and self.pos == 0:
                    self.buy(cta_bar.close_price, self.fixed_size)
                    print(f"    金叉做多 @ {cta_bar.close_price} ({cta_bar.datetime})")
                elif fast_ma < slow_ma and self.pos > 0:
                    self.sell(cta_bar.close_price, self.fixed_size)
                    print(f"    死叉平仓 @ {cta_bar.close_price} ({cta_bar.datetime})")

    def on_order(self, cta_engine, cta_order):
        \"\"\"委托回调\"\"\"
        pass

    def on_trade(self, cta_engine, cta_trade):
        \"\"\"成交回调\"\"\"
        print(f"    成交: {cta_trade.vt_symbol} {cta_trade.direction} {cta_trade.price}")

    def on_position(self, cta_engine, cta_position):
        \"\"\"持仓回调\"\"\"
        print(f"    持仓: {cta_position.vt_symbol} {cta_position.direction} {cta_position.volume}")

    def on_order_traded(self, cta_engine, cta_order):
        \"\"\"委托状态更新回调\"\"\"
        pass
"""

with open(strategy_file, 'w', encoding='utf-8') as f:
    f.write(strategy_code)

print(f"策略文件创建成功: {strategy_file}")
print(f"策略类: SimpleDoubleMaStrategy")
print("✅ 策略创建成功")
print()

# ==============================================================================
# 三、创建 VeighNa Station 配置
# ==============================================================================

print("【步骤 3：创建 VeighNa Station 配置】")
print("-" * 80)
print()

# VeighNa Station 配置目录
station_dir = "/root/.openclaw/workspace/quant-factory/veighna_station"
os.makedirs(station_dir, exist_ok=True)

# 配置文件
config_file = os.path.join(station_dir, "vnpy_setting.json")

config_code = """
{
  "log.active": true,
  "log.level": "INFO",
  "log.console": true,
  "log.file": false
}
"""

with open(config_file, 'w', encoding='utf-8') as f:
    f.write(config_code)

print(f"配置文件创建成功: {config_file}")
print("✅ 配置创建成功")
print()

# ==============================================================================
# 四、总结
# ==============================================================================

print("=" * 80)
print("【总结】")
print("=" * 80)
print()

print("✅ 策略目录创建完成")
print(f"  位置: {strategies_dir}")
print(f"  策略文件: {strategy_file}")
print(f"  策略类: SimpleDoubleMaStrategy")
print()

print("✅ VeighNa Station 配置创建完成")
print(f"  位置: {station_dir}")
print(f"  配置文件: {config_file}")
print()

print("下一步:")
print("  1. 使用 VeighNa Station 图形化界面")
print("  2. 加载策略")
print("  3. 下载历史数据")
print("  4. 运行回测")
print("  5. 分析结果")
print()

print("=" * 80)
print("🎉 vn.py 回测环境配置完成！")
print("=" * 80)
