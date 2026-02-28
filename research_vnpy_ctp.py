#!/usr/bin/env python3
"""
研究 vn.py_ctp 的 CtpGateway 实现
"""
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("🔍 研究 vn.py_ctp 的 CtpGateway 实现")
print("=" * 80)
print()

# ==============================================================================
# 一、查找 CtpGateway 的实现
# ==============================================================================

print("【步骤 1：查找 CtpGateway 实现】")
print("-" * 80)
print()

ctp_gateway_file = "/root/.openclaw/workspace/vnpy_trading/venv/lib/python3.12/site-packages/vnpy_ctp/gateway/ctp_gateway.py"

if os.path.exists(ctp_gateway_file):
    print(f"文件: {ctp_gateway_file}")
    print(f"大小: {os.path.getsize(ctp_gateway_file)} 字节")
    print()

    # 显示前 100 行
    print("前 100 行:")
    print()

    with open(ctp_gateway_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for i, line in enumerate(lines[:100], 1):
            print(f"  {i:3d}: {line.rstrip()}")

    print(f"  ... (还有 {len(lines) - 100} 行)")
    print()
else:
    print(f"❌ CtpGateway 文件不存在: {ctp_gateway_file}")
    print()

# ==============================================================================
# 二、查找 vnpy_ctp 的 API 实现
# ==============================================================================

print("【步骤 2：查找 vnpy_ctp 的 API 实现】")
print("-" * 80)
print()

ctp_api_dir = "/root/.openclaw/workspace/vnpy_trading/venv/lib/python3.12/site-packages/vnpy_ctp/api"

if os.path.exists(ctp_api_dir):
    print(f"目录: {ctp_api_dir}")
    print()

    print("API 文件:")
    for file in os.listdir(ctp_api_dir):
        filepath = os.path.join(ctp_api_dir, file)
        if os.path.isfile(filepath):
            size = os.path.getsize(filepath)
            print(f"  - {file}: {size:,} 字节")
    print()

    # 查找 API 模块
    api_modules = [f for f in os.listdir(ctp_api_dir) if f.endswith('.py')]

    print("API 模块:")
    for module in api_modules:
        filepath = os.path.join(ctp_api_dir, module)
        print(f"  - {module}")
    print()
else:
    print(f"❌ vnpy_ctp API 目录不存在: {ctp_api_dir}")
    print()

# ==============================================================================
# 三、查找 vnpy_ctp 的 __init__ 文件
# ==============================================================================

print("【步骤 3：查找 vnpy_ctp 的 __init__ 文件】")
print("-" * 80)
print()

vnpy_ctp_init = "/root/.openclaw/workspace/vnpy_trading/venv/lib/python3.12/site-packages/vnpy_ctp/__init__.py"

if os.path.exists(vnpy_ctp_init):
    print(f"文件: {vnpy_ctp_init}")
    print(f"大小: {os.path.getsize(vnpy_ctp_init)} 字节")
    print()

    # 显示前 50 行
    print("前 50 行:")
    print()

    with open(vnpy_ctp_init, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for i, line in enumerate(lines[:50], 1):
            print(f"  {i:2d}: {line.rstrip()}")

    print()
else:
    print(f"❌ vnpy_ctp __init__ 文件不存在: {vnpy_ctp_init}")
    print()

# ==============================================================================
# 四、总结
# ==============================================================================

print("=" * 80)
print("【总结】")
print("=" * 80)
print()

print("vn.py_ctp 结构:")
print("  ✅ CtpGateway 实现")
print("  ✅ API 模块")
print("  ✅ __init__ 文件")
print()

print("下一步:")
print("  1. 深入研究 CtpGateway 的连接流程")
print("  2. 研究事件分发机制")
print("  3. 找到连接问题的根源")
print("  4. 修复连接问题")

print()
print("=" * 80)
print("🔍 vn.py_ctp 研究完成！")
print("=" * 80)
