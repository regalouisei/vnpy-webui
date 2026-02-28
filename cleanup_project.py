#!/usr/bin/env python3
"""
量化工厂项目清理脚本
清理临时文件、调试文件、重复测试文件
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

# 项目根目录
PROJECT_ROOT = Path("/root/.openclaw/workspace/quant-factory")

# 需要删除的文件列表（临时文件、调试文件、重复测试）
FILES_TO_DELETE = [
    # 调试文件
    "debug_account_query.py",
    "debug_ctp_callback.py",
    "fix_account_query.py",

    # 临时修复文件
    "test_backtest_fixed.py",
    "test_backtest_simple.py",
    "test_cta_fixed.py",
    "vnpy_ctp_test_fixed.py",

    # 简单测试文件（已有完整测试）
    "vnpy_ctp_test_simple.py",
    "vnpy_simple_test.py",
    "vnpy_ctp_test_with_log.py",

    # 旧版本文件
    "zongzhihui_v2.py",
    "zongzhihui_v3.py",
    "zongzhihui_v3_fixed.py",

    # 重复测试文件（已有完整测试）
    "vnpy_no_ui_complete_test.py",
    "vnpy_complete_test_no_ui.py",
    "vnpy_no_ui_test_final.py",
    "vnpy_complete_documentation.py",
    "vnpy_function_test_guide.md",

    # 旧环境设置文件
    "setup_backtest_env_v2.py",
    "setup_backtest_env_final.py",

    # 研究脚本（已完成研究）
    "study_vnpy_backtest.py",
    "deep_study_vnpy_entries.py",
    "research_backtest_libs.py",
    "research_vnpy_ctp_gateway.py",

    # 检查脚本（临时）
    "check_network.py",
    "check_vnpy_status.py",
    "test_vnpy_core.py",

    # 版本分析报告（已整合）
    "vnpy_version_analysis_report.md",

    # 团队介绍（已有 AGENTS.md）
    "team_introduction.py",

    # 卸载脚本
    "uninstall_vnpy.py",

    # 克隆安装脚本
    "clone_and_install_vnpy.py",
]

# 需要移动到 archive 的文件（保留但归档）
FILES_TO_ARCHIVE = [
    # 最终报告（归档）
    "FINAL_REPORT.md",
    "TEST_SUMMARY.md",
    "README_FINAL.md",
    "ACCOUNT_QUERY_OPTIMIZATION.md",

    # 旧系统文件
    "SYSTEM_OPTIMIZATION_v3.0.md",
    "TASK_DECOMPOSITION_AND_EXECUTION_STRATEGY.md",

    # 旧 zongzhihui 系统文件
    "zongzhihui_system.py",
]

def main():
    print("=" * 60)
    print("量化工厂项目清理工具")
    print("=" * 60)
    print(f"项目目录: {PROJECT_ROOT}")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 1. 删除无用文件
    print("\n[1/3] 删除无用文件...")
    deleted_count = 0
    deleted_size = 0

    for filename in FILES_TO_DELETE:
        file_path = PROJECT_ROOT / filename

        if file_path.exists():
            size = file_path.stat().st_size
            deleted_size += size

            # 删除文件
            os.remove(file_path)
            deleted_count += 1

            print(f"  ✓ 删除: {filename} ({size:,} bytes)")

    if deleted_count == 0:
        print("  (没有文件需要删除)")
    else:
        print(f"\n  共删除 {deleted_count} 个文件，释放空间 {deleted_size:,} bytes")

    # 2. 归档旧文件
    print("\n[2/3] 归档旧文件...")

    # 创建归档目录
    archive_dir = PROJECT_ROOT / "archive"
    archive_dir.mkdir(exist_ok=True)

    archived_count = 0

    for filename in FILES_TO_ARCHIVE:
        src_path = PROJECT_ROOT / filename

        if src_path.exists():
            # 目标路径
            dst_path = archive_dir / filename

            # 移动文件
            shutil.move(str(src_path), str(dst_path))
            archived_count += 1

            print(f"  ✓ 归档: {filename} -> archive/")

    if archived_count == 0:
        print("  (没有文件需要归档)")
    else:
        print(f"\n  共归档 {archived_count} 个文件")

    # 3. 清理 __pycache__
    print("\n[3/3] 清理 __pycache__...")
    pycache_count = 0

    for pycache_path in PROJECT_ROOT.rglob("__pycache__"):
        if pycache_path.is_dir():
            shutil.rmtree(pycache_path)
            pycache_count += 1
            print(f"  ✓ 删除: {pycache_path.relative_to(PROJECT_ROOT)}")

    if pycache_count == 0:
        print("  (没有 __pycache__ 需要清理)")
    else:
        print(f"\n  共清理 {pycache_count} 个 __pycache__ 目录")

    # 4. 清理 .pyc 文件
    print("\n[4/4] 清理 .pyc 文件...")
    pyc_count = 0

    for pyc_path in PROJECT_ROOT.rglob("*.pyc"):
        os.remove(pyc_path)
        pyc_count += 1

    if pyc_count == 0:
        print("  (没有 .pyc 文件需要清理)")
    else:
        print(f"\n  共清理 {pyc_count} 个 .pyc 文件")

    # 总结
    print("\n" + "=" * 60)
    print("清理完成！")
    print("=" * 60)
    print(f"删除文件: {deleted_count}")
    print(f"归档文件: {archived_count}")
    print(f"清理缓存: {pycache_count} 个 __pycache__, {pyc_count} 个 .pyc")
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 5. 显示清理后的项目结构
    print("\n" + "=" * 60)
    print("清理后的项目结构")
    print("=" * 60)

    # 统计文件数量
    py_files = list(PROJECT_ROOT.rglob("*.py"))
    md_files = list(PROJECT_ROOT.rglob("*.md"))
    log_files = list((PROJECT_ROOT / "logs").glob("*.log")) if (PROJECT_ROOT / "logs").exists() else []

    print(f"\nPython 文件: {len(py_files)}")
    print(f"Markdown 文件: {len(md_files)}")
    print(f"日志文件: {len(log_files)}")

    # 显示主要目录
    print(f"\n主要目录:")
    for item in sorted(PROJECT_ROOT.iterdir()):
        if item.is_dir() and not item.name.startswith('.'):
            file_count = len(list(item.rglob("*")))
            print(f"  📁 {item.name}/ ({file_count} 个文件)")

    # 显示根目录文件
    print(f"\n根目录文件:")
    for item in sorted(PROJECT_ROOT.iterdir()):
        if item.is_file() and not item.name.startswith('.'):
            size_kb = item.stat().st_size / 1024
            print(f"  📄 {item.name} ({size_kb:.1f} KB)")

    print("\n" + "=" * 60)
    print("清理工具运行结束")
    print("=" * 60)


if __name__ == "__main__":
    main()
