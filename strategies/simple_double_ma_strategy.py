
# -*- coding: utf-8 -*-
from vnpy_ctastrategy.base import CtaTemplate
from vnpy.trader.object import BarData, TickData, OrderData, TradeData
from vnpy.trader.constant import Interval

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

    def on_init(self, cta_engine, strategy_name, vt_symbol, setting):
        print(f"策略初始化: {strategy_name}")
        self.cta_engine = cta_engine
        self.strategy_name = strategy_name
        self.vt_symbol = vt_symbol

    def on_start(self):
        print(f"策略启动: {self.strategy_name}")

    def on_stop(self):
        print(f"策略停止: {self.strategy_name}")

    def on_tick(self, cta_engine, cta_tick):
        pass

    def on_bar(self, cta_engine, cta_bar):
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
                elif fast_ma < slow_ma and self.pos > 0:
                    self.sell(cta_bar.close_price, self.fixed_size)

    def on_order(self, cta_engine, cta_order):
        pass

    def on_trade(self, cta_engine, cta_trade):
        pass

    def on_position(self, cta_engine, cta_position):
        pass
