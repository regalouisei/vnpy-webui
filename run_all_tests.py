#!/usr/bin/env python3
"""
VnPy 全功能测试主脚本

自动运行所有测试脚本并生成统一报告
"""
import sys
import subprocess
import time
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("VnPy 全功能测试主脚本")
print("=" * 80)
print()
print("开始时间:", datetime.now().isoformat())
print()

# ==============================================================================
# 测试配置
# ==============================================================================

TESTS = [
    {
        "name": "核心功能测试",
        "file": "complete_test_suite.py",
        "description": "核心框架、CTP连接、数据查询、行情订阅、CTA引擎",
        "priority": 1,
        "estimated_time": 5  # 分钟
    },
    {
        "name": "CTA策略功能测试",
        "file": "test_cta_strategy_comprehensive.py",
        "description": "策略生命周期、事件处理、参数配置、信号测试",
        "priority": 2,
        "estimated_time": 10
    },
    {
        "name": "回测功能测试",
        "file": "test_backtest_comprehensive.py",
        "description": "回测引擎、历史数据、参数优化、报告生成",
        "priority": 2,
        "estimated_time": 8
    },
    {
        "name": "数据管理测试",
        "file": "test_data_manager_comprehensive.py",
        "description": "数据库连接、数据存储、导入导出、备份",
        "priority": 2,
        "estimated_time": 5
    }
]

# ==============================================================================
# 测试结果记录
# ==============================================================================

results = []

def run_test(test_config):
    """运行单个测试"""
    print("=" * 80)
    print(f"测试: {test_config['name']}")
    print("=" * 80)
    print()

    print(f"描述: {test_config['description']}")
    print(f"优先级: {test_config['priority']}")
    print(f"预计时间: {test_config['estimated_time']} 分钟")
    print(f"脚本: {test_config['file']}")
    print()
    print("开始执行...")
    print()

    start_time = time.time()
    success = False
    output = ""
    error = ""

    try:
        # 运行测试脚本
        result = subprocess.run(
            [sys.executable, test_config['file']],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=600  # 10分钟超时
        )

        output = result.stdout
        error = result.stderr
        success = result.returncode == 0

        elapsed = time.time() - start_time

        # 保存输出到日志
        log_file = Path(f"logs/test_{test_config['file'].replace('.py', '')}.log")
        log_file.parent.mkdir(exist_ok=True)

        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"测试: {test_config['name']}\n")
            f.write(f"开始时间: {datetime.now().isoformat()}\n")
            f.write(f"结束时间: {(datetime.now()).isoformat()}\n")
            f.write(f"耗时: {elapsed:.2f} 秒\n")
            f.write(f"状态: {'成功' if success else '失败'}\n")
            f.write("=" * 80 + "\n")
            f.write("STDOUT:\n")
            f.write(output)
            f.write("\n" + "=" * 80 + "\n")
            f.write("STDERR:\n")
            f.write(error)

        # 显示结果
        print("=" * 80)
        print("测试完成")
        print("=" * 80)
        print(f"耗时: {elapsed:.2f} 秒 ({elapsed/60:.2f} 分钟)")
        print(f"状态: {'✅ 成功' if success else '❌ 失败'}")
        print(f"日志: {log_file}")
        print()

        if not success and error:
            print("错误信息:")
            print(error)
            print()

        # 记录结果
        result_record = {
            "name": test_config['name'],
            "file": test_config['file'],
            "description": test_config['description'],
            "priority": test_config['priority'],
            "success": success,
            "elapsed": elapsed,
            "output": output,
            "error": error,
            "log_file": str(log_file),
            "timestamp": datetime.now().isoformat()
        }
        results.append(result_record)

        return success

    except subprocess.TimeoutExpired:
        elapsed = time.time() - start_time
        print("❌ 测试超时（10分钟）")
        print(f"耗时: {elapsed:.2f} 秒")
        print()

        result_record = {
            "name": test_config['name'],
            "file": test_config['file'],
            "description": test_config['description'],
            "priority": test_config['priority'],
            "success": False,
            "elapsed": elapsed,
            "output": "",
            "error": "Timeout",
            "log_file": "",
            "timestamp": datetime.now().isoformat()
        }
        results.append(result_record)

        return False

    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ 测试异常: {e}")
        print(f"耗时: {elapsed:.2f} 秒")
        print()

        result_record = {
            "name": test_config['name'],
            "file": test_config['file'],
            "description": test_config['description'],
            "priority": test_config['priority'],
            "success": False,
            "elapsed": elapsed,
            "output": "",
            "error": str(e),
            "log_file": "",
            "timestamp": datetime.now().isoformat()
        }
        results.append(result_record)

        return False

# ==============================================================================
# 生成报告
# ==============================================================================

def generate_report():
    """生成测试报告"""
    print("=" * 80)
    print("生成测试报告")
    print("=" * 80)
    print()

    # 汇总统计
    total = len(results)
    passed = sum(1 for r in results if r['success'])
    failed = total - passed
    total_time = sum(r['elapsed'] for r in results)

    print("=" * 80)
    print("测试汇总")
    print("=" * 80)
    print()
    print(f"总测试数: {total}")
    print(f"通过: {passed} ({passed/total*100:.1f}%)")
    print(f"失败: {failed} ({failed/total*100:.1f}%)")
    print(f"总耗时: {total_time:.2f} 秒 ({total_time/60:.2f} 分钟)")
    print()

    # 详细结果
    print("=" * 80)
    print("详细结果")
    print("=" * 80)
    print()

    for i, result in enumerate(results, 1):
        print(f"{i}. {result['name']}")
        print(f"   状态: {'✅ 通过' if result['success'] else '❌ 失败'}")
        print(f"   耗时: {result['elapsed']:.2f} 秒")
        print(f"   优先级: {result['priority']}")
        if result['log_file']:
            print(f"   日志: {result['log_file']}")
        print()

    # 保存到文件
    report_file = Path("logs/test_summary.md")
    report_file.parent.mkdir(exist_ok=True)

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# VnPy 功能测试报告\n\n")
        f.write(f"**生成时间**: {datetime.now().isoformat()}\n\n")
        f.write(f"## 测试汇总\n\n")
        f.write(f"- 总测试数: {total}\n")
        f.write(f"- 通过: {passed} ({passed/total*100:.1f}%)\n")
        f.write(f"- 失败: {failed} ({failed/total*100:.1f}%)\n")
        f.write(f"- 总耗时: {total_time:.2f} 秒 ({total_time/60:.2f} 分钟)\n\n")

        f.write(f"## 详细结果\n\n")
        for i, result in enumerate(results, 1):
            status = "✅ 通过" if result['success'] else "❌ 失败"
            f.write(f"### {i}. {result['name']}\n\n")
            f.write(f"- 状态: {status}\n")
            f.write(f"- 耗时: {result['elapsed']:.2f} 秒\n")
            f.write(f"- 优先级: {result['priority']}\n")
            f.write(f"- 描述: {result['description']}\n")
            if result['log_file']:
                f.write(f"- 日志: {result['log_file']}\n")
            if result['error']:
                f.write(f"- 错误: {result['error']}\n")
            f.write("\n")

    print(f"报告已保存: {report_file}")
    print()

# ==============================================================================
# 主函数
# ==============================================================================

def main():
    """主函数"""
    print("测试列表:")
    print()

    for i, test in enumerate(TESTS, 1):
        print(f"{i}. {test['name']}")
        print(f"   描述: {test['description']}")
        print(f"   优先级: {test['priority']}")
        print(f"   预计时间: {test['estimated_time']} 分钟")
        print()

    # 按优先级排序
    TESTS.sort(key=lambda x: x['priority'])

    total_estimated = sum(t['estimated_time'] for t in TESTS)
    print(f"总预计时间: {total_estimated} 分钟 ({total_estimated/60:.2f} 小时)")
    print()

    # 询问是否继续
    print("=" * 80)
    print("准备开始测试")
    print("=" * 80)
    print()
    print("按 Enter 开始测试，或按 Ctrl+C 取消...")

    try:
        input()
    except KeyboardInterrupt:
        print()
        print("测试已取消")
        return

    print()
    print("开始测试...")
    print()

    # 运行所有测试
    for i, test in enumerate(TESTS, 1):
        print(f"\n[{i}/{len(TESTS)}] 运行: {test['name']}")
        run_test(test)

        # 短暂休息
        if i < len(TESTS):
            print()
            print("休息 5 秒...")
            time.sleep(5)

    print()
    print("=" * 80)
    print("所有测试完成")
    print("=" * 80)
    print()

    # 生成报告
    generate_report()

    print("测试结束时间:", datetime.now().isoformat())
    print()

if __name__ == "__main__":
    main()
