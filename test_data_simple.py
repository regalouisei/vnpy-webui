#!/usr/bin/env python3
"""
VnPy 数据管理功能测试 - 简化版
"""
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("VnPy 数据管理功能测试")
print("=" * 80)
print()

try:
    from vnpy.trader.object import BarData, TickData
    from vnpy.trader.constant import Interval, Exchange
    from vnpy.trader.database import get_database, BaseDatabase
    import numpy as np
    import pandas as pd
    print("✅ 所有模块导入成功\n")
except Exception as e:
    print(f"❌ 模块导入失败: {e}")
    sys.exit(1)

# ==============================================================================
# 测试结果记录
# ==============================================================================

test_results = {}

def record_result(test_name, passed, details=""):
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
# 第一阶段：数据库连接
# ==============================================================================

print("1.1 检查数据库配置...")
try:
    from vnpy.trader.setting import SETTINGS
    database_config = SETTINGS.get("database", {})
    print("当前数据库配置:")
    print(f"  数据库类型: {database_config.get('database', '未配置')}")
    print()
except Exception as e:
    print(f"❌ 数据库配置检查失败: {e}\n")

print("1.2 连接数据库...")
try:
    database = get_database()
    if database:
        print(f"✅ 数据库连接成功")
        print(f"  数据库类: {database.__class__.__name__}")
        print(f"  数据库类型: {database.__class__.__module__}")
        print()
        record_result("数据库连接", True, f"连接成功: {database.__class__.__name__}")
    else:
        print("⚠️  数据库未连接")
        print()
        record_result("数据库连接", False, "未连接")
except Exception as e:
    print(f"❌ 数据库连接失败: {e}\n")
    record_result("数据库连接", False, str(e))

# ==============================================================================
# 第二阶段：数据存储
# ==============================================================================

print("2.1 创建测试数据...")
try:
    test_symbol = "TEST0001"
    test_exchange = Exchange.SSE
    test_interval = Interval.MINUTE

    test_bars = []
    base_price = 100.0
    start_time = datetime(2025, 1, 1)

    for i in range(100):
        bar_datetime = start_time + timedelta(minutes=i)
        price_change = np.random.normal(0, 0.5)
        close_price = base_price + price_change

        bar = BarData(
            symbol=test_symbol,
            exchange=test_exchange,
            datetime=bar_datetime,
            interval=test_interval,
            open_price=close_price - np.random.uniform(-0.3, 0.3),
            high_price=close_price + np.random.uniform(0, 0.3),
            low_price=close_price - np.random.uniform(0, 0.3),
            close_price=close_price,
            volume=np.random.randint(1000, 5000),
            open_interest=np.random.randint(10000, 20000),
            gateway_name="TEST"
        )
        test_bars.append(bar)
        base_price = close_price

    print(f"✅ 测试数据创建成功: {len(test_bars)} 条K线")
    print(f"  合约: {test_symbol}")
    print(f"  交易所: {test_exchange.value}")
    print(f"  周期: {test_interval.value}")
    print(f"  时间范围: {test_bars[0].datetime} ~ {test_bars[-1].datetime}")
    print()
    record_result("测试数据创建", True, f"创建 {len(test_bars)} 条数据")
except Exception as e:
    print(f"❌ 测试数据创建失败: {e}\n")
    record_result("测试数据创建", False, str(e))

print("2.2 保存K线数据...")
try:
    database = get_database()
    if not database:
        raise RuntimeError("数据库未连接")

    # 删除旧数据
    try:
        database.delete_bar_data(
            symbol=test_symbol,
            exchange=test_exchange,
            interval=test_interval
        )
    except:
        pass

    # 保存新数据
    database.save_bar_data(test_bars)
    print(f"✅ K线数据保存成功: {len(test_bars)} 条")
    print()
    record_result("K线数据保存", True, f"保存 {len(test_bars)} 条数据")
except Exception as e:
    print(f"❌ K线数据保存失败: {e}")
    import traceback
    traceback.print_exc()
    print()
    record_result("K线数据保存", False, str(e))

# ==============================================================================
# 第三阶段：数据查询
# ==============================================================================

print("3.1 查询K线数据...")
try:
    database = get_database()
    if not database:
        raise RuntimeError("数据库未连接")

    bars = database.load_bar_data(
        symbol=test_symbol,
        exchange=test_exchange,
        interval=test_interval,
        start=datetime(2025, 1, 1),
        end=datetime(2025, 12, 31)
    )

    print(f"✅ K线数据查询成功: {len(bars)} 条")
    if bars:
        print(f"  时间范围: {bars[0].datetime} ~ {bars[-1].datetime}")
        print(f"  开盘: {bars[0].open_price:.2f}, 收盘: {bars[-1].close_price:.2f}")
        print(f"  最高: {max(b.high_price for b in bars):.2f}")
        print(f"  最低: {min(b.low_price for b in bars):.2f}")
    print()
    record_result("K线数据查询", True, f"查询到 {len(bars)} 条数据")
except Exception as e:
    print(f"❌ K线数据查询失败: {e}")
    import traceback
    traceback.print_exc()
    print()
    record_result("K线数据查询", False, str(e))

print("3.2 查询可用数据...")
try:
    database = get_database()
    if not database:
        raise RuntimeError("数据库未连接")

    try:
        available = database.get_bar_overview()
        print(f"✅ 可用数据查询成功")
        print(f"  数据条目: {len(available)} 个")

        if available:
            print()
            print(f"前10个数据条目:")
            for i, (symbol, exchange, interval) in enumerate(available[:10], 1):
                print(f"  {i}. {symbol} {exchange.value} {interval.value}")

        print()
        record_result("可用数据查询", True, f"找到 {len(available)} 个数据条目")
    except AttributeError:
        print("⚠️  get_bar_data_available 方法不存在")
        print()
        record_result("可用数据查询", False, "方法不存在")
except Exception as e:
    print(f"❌ 可用数据查询失败: {e}")
    print()
    record_result("可用数据查询", False, str(e))

# ==============================================================================
# 第四阶段：数据导出
# ==============================================================================

print("4.1 导出为CSV格式...")
try:
    database = get_database()
    if not database:
        raise RuntimeError("数据库未连接")

    bars = database.load_bar_data(
        symbol=test_symbol,
        exchange=test_exchange,
        interval=test_interval,
        start=datetime(2025, 1, 1),
        end=datetime(2025, 12, 31)
    )

    if bars:
        data = []
        for bar in bars:
            data.append({
                "datetime": bar.datetime,
                "symbol": bar.symbol,
                "exchange": bar.exchange.value,
                "interval": bar.interval.value,
                "open": bar.open_price,
                "high": bar.high_price,
                "low": bar.low_price,
                "close": bar.close_price,
                "volume": bar.volume,
                "open_interest": bar.open_interest
            })

        df = pd.DataFrame(data)

        output_dir = Path("/root/.openclaw/workspace/quant-factory/data/exports")
        output_dir.mkdir(parents=True, exist_ok=True)

        csv_file = output_dir / f"{test_symbol}_export.csv"
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')

        file_size = csv_file.stat().st_size
        print(f"✅ CSV导出成功")
        print(f"  文件: {csv_file}")
        print(f"  大小: {file_size:,} 字节")
        print(f"  记录数: {len(df)} 条")
        print()
        record_result("CSV导出", True, f"导出 {len(df)} 条数据")
    else:
        print("⚠️  无数据可导出")
        print()
        record_result("CSV导出", False, "无数据")
except Exception as e:
    print(f"❌ CSV导出失败: {e}")
    import traceback
    traceback.print_exc()
    print()
    record_result("CSV导出", False, str(e))

# ==============================================================================
# 第五阶段：数据删除
# ==============================================================================

print("5.1 删除测试数据...")
try:
    database = get_database()
    if not database:
        raise RuntimeError("数据库未连接")

    database.delete_bar_data(
        symbol=test_symbol,
        exchange=test_exchange,
        interval=test_interval
    )

    bars = database.load_bar_data(
        symbol=test_symbol,
        exchange=test_exchange,
        interval=test_interval,
        start=datetime(2025, 1, 1),
        end=datetime(2025, 12, 31)
    )

    if len(bars) == 0:
        print("✅ 测试数据删除成功")
        print()
        record_result("数据删除", True, "所有测试数据已删除")
    else:
        print(f"⚠️  仍有 {len(bars)} 条数据未删除")
        print()
        record_result("数据删除", False, f"剩余 {len(bars)} 条数据")
except Exception as e:
    print(f"❌ 数据删除失败: {e}")
    print()
    record_result("数据删除", False, str(e))

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
