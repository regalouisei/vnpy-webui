#!/usr/bin/env python3
"""
运行 vn.py 官方安装脚本（Linux）
"""
import subprocess
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("🔍 运行 vn.py 官方安装脚本")
print("=" * 80)
print()

# ==============================================================================
# 一、切换到 vn.py 源码目录
# ==============================================================================

vnpy_fresh_dir = "/root/.openclaw/workspace/vnpy_fresh"
install_sh_path = os.path.join(vnpy_fresh_dir, "install.sh")

if not os.path.exists(install_sh_path):
    print(f"❌ install.sh 不存在: {install_sh_path}")
    print()
    print("请先检查 vn.py 源码是否正确克隆")
    sys.exit(1)

# ==============================================================================
# 二、运行 install.sh
# ==============================================================================

print("【运行官方安装脚本】")
print("-" * 80)
print()

print(f"vn.py 源码目录: {vnpy_fresh_dir}")
print(f"安装脚本: {install.sh_path}")
print()

print("开始运行 bash install.sh...")
print()

try:
    result = subprocess.run(
        ["bash", "install.sh"],
        cwd=vnpy_fresh_dir,
        capture_output=True,
        text=True,
        timeout=1800  # 30 分钟超时
    )

    print("=" * 80)
    print("【安装输出】")
    print("=" * 80)
    print()

    # 显示安装输出（前 200 行）
    lines = result.stdout.split('\n')
    for i, line in enumerate(lines[:200], 1):
        print(line)

    if len(lines) > 200:
        print(f"  ... (还有 {len(lines) - 200} 行)")
    print()

    if result.returncode == 0:
        print("✅ 安装脚本执行成功")
        print()
    else:
        print("⚠️  安装脚本执行可能有问题")
        print()

    if result.stderr:
        print("错误信息:")
        print(result.stderr)

    print("=" * 80)
    print("【安装总结】")
    print("=" * 80)
    print()

    print("下一步:")
    print("  1. 验证 vn.py 及其相关库的安装")
    print("  2. 测试 vn.py 的导入")
    print("  3. 测试 vn.py_ctp 的导入")
    print("  4. 测试 vnpy_ctastrategy 的导入")
    print("  5. 测试 vnpy_tts 的导入")
    print("  6. 测试 vn.py 的基本功能")
    print()

    print("=" * 80)

except subprocess.TimeoutExpired:
    print("⚠️  安装超时（超过 30 分钟）")
    print("  可能正在编译 C++ 库，请稍等...")
    print()
    print("建议:")
    print("  1. 等待安装完成")
    print("  2. 查看终端输出")
    print("  3. 检查错误信息")
    print()

except Exception as e:
    print(f"❌ 安装异常: {e}")
    print()
    import traceback
    traceback.print_exc()
    sys.exit(1)
