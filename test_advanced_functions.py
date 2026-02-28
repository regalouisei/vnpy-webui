#!/usr/bin/env python3
"""
VnPy 高级功能测试

测试内容:
1. 组合策略
2. 期权交易
3. 算法交易
4. 脚本策略
5. AI 量化
6. 风险管理
"""
import sys
import time
from datetime import datetime
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("VnPy 高级功能测试")
print("=" * 80)
print()

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
# 第一阶段：组合策略测试
# ==============================================================================

print("=" * 80)
print("第一阶段：组合策略测试")
print("=" * 80)
print()

print("1.1 导入组合策略模块...")
try:
    from vnpy_portfoliostrategy import PortfolioStrategy
    print("✅ 组合策略模块导入成功")
    print()
    record_result("组合策略模块导入", True, "vnpy_portfoliostrategy 导入成功")
except ImportError as e:
    print(f"⚠️  组合策略模块未安装: {e}")
    print()
    record_result("组合策略模块导入", False, f"未安装: {e}")
except Exception as e:
    print(f"❌ 组合策略模块导入失败: {e}")
    print()
    record_result("组合策略模块导入", False, str(e))

print("1.2 检查组合策略功能...")
try:
    from vnpy_portfoliostrategy import PortfolioStrategy

    # 检查可用方法
    methods = [m for m in dir(PortfolioStrategy) if not m.startswith('_')]
    print(f"✅ PortfolioStrategy 类可用")
    print(f"  公共方法: {len(methods)} 个")

    # 显示前 10 个方法
    if methods:
        print(f"  前10个方法: {', '.join(methods[:10])}")

    print()
    record_result("组合策略功能检查", True, f"找到 {len(methods)} 个方法")
except Exception as e:
    print(f"❌ 组合策略功能检查失败: {e}")
    print()
    record_result("组合策略功能检查", False, str(e))

# ==============================================================================
# 第二阶段：期权交易测试
# ==============================================================================

print("=" * 80)
print("第二阶段：期权交易测试")
print("=" * 80)
print()

print("2.1 导入期权交易模块...")
try:
    from vnpy_optionmaster import OptionMasterApp
    print("✅ 期权交易模块导入成功")
    print()
    record_result("期权交易模块导入", True, "vnpy_optionmaster 导入成功")
except ImportError as e:
    print(f"⚠️  期权交易模块未安装: {e}")
    print()
    record_result("期权交易模块导入", False, f"未安装: {e}")
except Exception as e:
    print(f"❌ 期权交易模块导入失败: {e}")
    print()
    record_result("期权交易模块导入", False, str(e))

print("2.2 检查期权交易功能...")
try:
    from vnpy_optionmaster import OptionMasterApp

    # 检查可用方法
    methods = [m for m in dir(OptionMasterApp) if not m.startswith('_')]
    print(f"✅ OptionMasterApp 类可用")
    print(f"  公共方法: {len(methods)} 个")

    if methods:
        print(f"  前10个方法: {', '.join(methods[:10])}")

    print()
    record_result("期权交易功能检查", True, f"找到 {len(methods)} 个方法")
except Exception as e:
    print(f"❌ 期权交易功能检查失败: {e}")
    print()
    record_result("期权交易功能检查", False, str(e))

# ==============================================================================
# 第三阶段：算法交易测试
# ==============================================================================

print("=" * 80)
print("第三阶段：算法交易测试")
print("=" * 80)
print()

print("3.1 导入算法交易模块...")
try:
    from vnpy_algotrading import AlgoTradingApp
    print("✅ 算法交易模块导入成功")
    print()
    record_result("算法交易模块导入", True, "vnpy_algotrading 导入成功")
except ImportError as e:
    print(f"⚠️  算法交易模块未安装: {e}")
    print()
    record_result("算法交易模块导入", False, f"未安装: {e}")
except Exception as e:
    print(f"❌ 算法交易模块导入失败: {e}")
    print()
    record_result("算法交易模块导入", False, str(e))

print("3.2 检查算法交易功能...")
try:
    from vnpy_algotrading import AlgoTradingApp

    # 检查可用方法
    methods = [m for m in dir(AlgoTradingApp) if not m.startswith('_')]
    print(f"✅ AlgoTradingApp 类可用")
    print(f"  公共方法: {len(methods)} 个")

    if methods:
        print(f"  前10个方法: {', '.join(methods[:10])}")

    print()
    record_result("算法交易功能检查", True, f"找到 {len(methods)} 个方法")
except Exception as e:
    print(f"❌ 算法交易功能检查失败: {e}")
    print()
    record_result("算法交易功能检查", False, str(e))

# ==============================================================================
# 第四阶段：脚本策略测试
# ==============================================================================

print("=" * 80)
print("第四阶段：脚本策略测试")
print("=" * 80)
print()

print("4.1 导入脚本策略模块...")
try:
    from vnpy_scripttrader import ScriptEngine
    print("✅ 脚本策略模块导入成功")
    print()
    record_result("脚本策略模块导入", True, "vnpy_scripttrader 导入成功")
except ImportError as e:
    print(f"⚠️  脚本策略模块未安装: {e}")
    print()
    record_result("脚本策略模块导入", False, f"未安装: {e}")
except Exception as e:
    print(f"❌ 脚本策略模块导入失败: {e}")
    print()
    record_result("脚本策略模块导入", False, str(e))

print("4.2 检查脚本策略功能...")
try:
    from vnpy_scripttrader import ScriptEngine

    # 检查可用方法
    methods = [m for m in dir(ScriptEngine) if not m.startswith('_')]
    print(f"✅ ScriptEngine 类可用")
    print(f"  公共方法: {len(methods)} 个")

    if methods:
        print(f"  前10个方法: {', '.join(methods[:10])}")

    print()
    record_result("脚本策略功能检查", True, f"找到 {len(methods)} 个方法")
except Exception as e:
    print(f"❌ 脚本策略功能检查失败: {e}")
    print()
    record_result("脚本策略功能检查", False, str(e))

# ==============================================================================
# 第五阶段：AI 量化测试
# ==============================================================================

print("=" * 80)
print("第五阶段：AI 量化测试")
print("=" * 80)
print()

print("5.1 导入 AI 量化模块...")
try:
    from vnpy.alpha import AlphaDatabase
    print("✅ AI 量化模块导入成功")
    print()
    record_result("AI 量化模块导入", True, "vnpy.alpha 导入成功")
except ImportError as e:
    print(f"⚠️  AI 量化模块未安装: {e}")
    print()
    record_result("AI 量化模块导入", False, f"未安装: {e}")
except Exception as e:
    print(f"❌ AI 量化模块导入失败: {e}")
    print()
    record_result("AI 量化模块导入", False, str(e))

print("5.2 检查 AI 量化功能...")
try:
    from vnpy.alpha import AlphaDatabase

    # 检查可用方法
    methods = [m for m in dir(AlphaDatabase) if not m.startswith('_')]
    print(f"✅ AlphaDatabase 类可用")
    print(f"  公共方法: {len(methods)} 个")

    if methods:
        print(f"  前10个方法: {', '.join(methods[:10])}")

    print()
    record_result("AI 量化功能检查", True, f"找到 {len(methods)} 个方法")
except Exception as e:
    print(f"❌ AI 量化功能检查失败: {e}")
    print()
    record_result("AI 量化功能检查", False, str(e))

# ==============================================================================
# 第六阶段：风险管理测试
# ==============================================================================

print("=" * 80)
print("第六阶段：风险管理测试")
print("=" * 80)
print()

print("6.1 检查风险管理功能...")
try:
    from vnpy.trader.engine import MainEngine

    # 创建主引擎
    from vnpy.event import EventEngine
    event_engine = EventEngine()
    main_engine = MainEngine(event_engine)

    # 检查风控相关功能
    oms_engine = main_engine.get_engine("oms")

    if oms_engine:
        methods = [m for m in dir(oms_engine) if not m.startswith('_')]
        print(f"✅ OmsEngine 类可用")
        print(f"  公共方法: {len(methods)} 个")

        # 查找风控相关方法
        risk_methods = [m for m in methods if 'risk' in m.lower() or 'check' in m.lower()]
        if risk_methods:
            print(f"  风控方法: {', '.join(risk_methods)}")
        else:
            print(f"  注意: 未找到明确的风控方法")

        print()
        record_result("风险管理功能检查", True, f"找到 {len(methods)} 个方法，{len(risk_methods)} 个风控方法")
    else:
        print("❌ OmsEngine 未初始化")
        print()
        record_result("风险管理功能检查", False, "OmsEngine 未初始化")
except Exception as e:
    print(f"❌ 风险管理功能检查失败: {e}")
    print()
    record_result("风险管理功能检查", False, str(e))

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

# 分析结果
if failed_count > 0:
    print("注意事项:")
    print("- 部分高级功能模块未安装")
    print("- 这些是可选模块，不影响核心功能")
    print("- 可通过 pip install 安装对应模块")
    print()
    print("安装命令:")
    print("  pip install vnpy_portfoliostrategy  # 组合策略")
    print("  pip install vnpy_optionmaster        # 期权交易")
    print("  pip install vnpy_algotrading          # 算法交易")
    print("  pip install vnpy_scripttrader         # 脚本策略")
    print("  pip install vnpy_alpha                # AI 量化")
    print()

print("测试完成时间:", datetime.now().isoformat())
print()
