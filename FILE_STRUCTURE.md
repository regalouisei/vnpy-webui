# 项目文件结构说明

## 📁 完整文件列表

### 📘 文档文件

**根目录文档**
```
quant-factory/
├── README.md                          # 📋 项目总览（必读）
├── TEST_SUMMARY.md                    # 📊 之前的测试结果
└── vnpy_function_test_guide.md       # 📖 功能测试指南
```

**docs/ 目录**
```
docs/
├── VNPY_COMPREHENSIVE_TEST_PLAN.md   # 📋 完整测试计划（20个模块）
├── VNPY_COMPLETE_GUIDE.md           # 📖 安装与使用指南（13章）
└── TEST_PROGRESS.md                  # 📊 测试进度追踪（实时更新）
```

### 🔧 测试脚本（根目录）

**主要测试脚本**
```
quant-factory/
├── run_all_tests.py                  # 🚀 主测试脚本（自动化运行所有测试）
├── complete_test_suite.py            # ✅ 核心功能测试（8/8 通过）
├── test_cta_strategy_comprehensive.py  # 🔄 CTA策略完整测试
├── test_backtest_comprehensive.py     # ⏸️ 回测功能完整测试
└── test_data_manager_comprehensive.py # ⏸️ 数据管理完整测试
```

**其他测试脚本**
```
├── test_cta_fixed.py               # CTA 策略固定测试
├── test_cta_strategy.py            # CTA 策略测试
├── test_vnpy_all_functions_final.py # VnPy 所有功能测试
├── test_vnpy_core.py              # 核心功能测试
├── test_vnpy_no_ui_all_functions.py # 无 GUI 功能测试
├── vnpy_complete_test_no_ui.py     # 无 GUI 完整测试
├── vnpy_ctp_test_correct.py       # CTP 测试（修正版）
├── vnpy_ctp_test_fixed.py         # CTP 测试（固定版）
├── vnpy_ctp_test_simple.py       # CTP 简单测试
├── vnpy_ctp_test_with_log.py      # CTP 测试（带日志）
├── vnpy_function_test_guide.md     # 功能测试指南
├── vnpy_no_ui_test_final.py      # 无 GUI 最终测试
```

### 📁 辅助目录

```
quant-factory/
├── strategies/                   # 📂 策略目录
│   └── simple_double_ma_strategy.py  # 双均线策略示例
├── agents/                      # 📂 代理目录
│   ├── zongzhihui/             # 总指挥代理
│   ├── junshi/                 # 军师代理
│   ├── engineer_a/             # 工程师 A
│   ├── engineer_b/             # 工程师 B
│   └── researcher/             # 研究员代理（当前）
├── shared/                     # 📂 共享目录
│   ├── GOALS.md                # 目标
│   ├── PROJECTS.md             # 项目
│   ├── DECISIONS.md            # 决策
│   ├── ENGINEERS.md            # 工程师
│   └── TEAM-RULEBOOK.md        # 团队规则
└── memory/                     # 📂 记忆目录
    └── 2026-02-*.md           # 每日记忆
```

---

## 🚀 快速开始指南

### 第一步：查看项目总览

```bash
cd /root/.openclaw/workspace/quant-factory
cat README.md
```

### 第二步：查看测试计划

```bash
cat docs/VNPY_COMPREHENSIVE_TEST_PLAN.md
```

### 第三步：查看安装指南

```bash
cat docs/VNPY_COMPLETE_GUIDE.md
```

### 第四步：查看测试进度

```bash
cat docs/TEST_PROGRESS.md
```

### 第五步：运行测试

#### 方式 1：自动运行所有测试（推荐）

```bash
python3 run_all_tests.py
```

这将：
- 自动运行所有测试脚本
- 按优先级排序
- 保存详细日志
- 生成统一报告

#### 方式 2：手动运行单个测试

```bash
# 核心功能测试（已验证通过）
python3 complete_test_suite.py

# CTA 策略完整测试
python3 test_cta_strategy_comprehensive.py

# 回测功能完整测试
python3 test_backtest_comprehensive.py

# 数据管理完整测试
python3 test_data_manager_comprehensive.py
```

---

## 📊 测试状态速查

### ✅ 已完成（100%）

- ✅ 核心框架测试
- ✅ CTP 网关连接
- ✅ 账户查询（优化后）
- ✅ 持仓查询
- ✅ 合约查询
- ✅ 行情订阅
- ✅ CTA 策略引擎初始化
- ✅ 测试计划文档
- ✅ 安装与使用指南
- ✅ 测试进度追踪
- ✅ 项目总览文档

### 🔄 进行中（40%）

- 🔄 CTA 策略完整测试
  - ✅ 引擎初始化
  - ✅ 策略模板加载
  - 🔄 生命周期测试（进行中）
  - ⏸️ 事件处理（待完成）
  - ⏸️ 信号测试（待完成）

### ⏸️ 待开始（0%）

- ⏸️ 回测功能测试
- ⏸️ 数据管理测试
- ⏸️ 风险管理
- ⏸️ 组合策略
- ⏸️ 期权交易
- ⏸️ 算法交易
- ⏸️ 脚本策略
- ⏸️ AI 量化
- ⏸️ Web UI 开发

---

## 📝 文件大小统计

| 文件 | 大小 | 说明 |
|------|------|------|
| README.md | 6.6 KB | 项目总览 |
| VNPY_COMPREHENSIVE_TEST_PLAN.md | 6.0 KB | 测试计划 |
| VNPY_COMPLETE_GUIDE.md | 21.1 KB | 使用指南 |
| TEST_PROGRESS.md | 7.3 KB | 进度追踪 |
| complete_test_suite.py | 12.7 KB | 核心测试 |
| test_cta_strategy_comprehensive.py | 17.9 KB | CTA 测试 |
| test_backtest_comprehensive.py | 23.5 KB | 回测测试 |
| test_data_manager_comprehensive.py | 26.3 KB | 数据测试 |
| run_all_tests.py | 8.9 KB | 主测试脚本 |

**总计**: 约 130 KB

---

## 🎯 关键文件说明

### 必读文档

1. **README.md**
   - 项目总览
   - 快速开始
   - 测试状态
   - 技术栈
   - 时间估算

2. **VNPY_COMPREHENSIVE_TEST_PLAN.md**
   - 20 个测试模块
   - 详细测试步骤
   - 成功标准
   - 测试工具

3. **VNPY_COMPLETE_GUIDE.md**
   - 完整安装流程
   - 配置指南
   - API 参考
   - 最佳实践

4. **TEST_PROGRESS.md**
   - 实时进度
   - 问题记录
   - 里程碑

### 核心测试脚本

1. **run_all_tests.py** (🚀 推荐使用)
   - 自动化测试脚本
   - 运行所有测试
   - 生成统一报告

2. **complete_test_suite.py** (✅ 已验证)
   - 核心功能测试
   - 8/8 通过
   - 性能优化验证

3. **test_cta_strategy_comprehensive.py** (🔄 进行中)
   - CTA 策略完整测试
   - 8 个测试阶段
   - 50+ 测试项

4. **test_backtest_comprehensive.py** (⏸️ 待测试)
   - 回测功能测试
   - 10 个测试阶段
   - 参数优化

5. **test_data_manager_comprehensive.py** (⏸️ 待测试)
   - 数据管理测试
   - 10 个测试阶段
   - 多数据库支持

---

## 🔍 日志和报告

测试运行后，日志和报告将保存在：

```
logs/
├── test_complete_test_suite.log              # 核心功能测试日志
├── test_test_cta_strategy_comprehensive.log  # CTA 策略测试日志
├── test_test_backtest_comprehensive.log     # 回测测试日志
├── test_test_data_manager_comprehensive.log # 数据管理测试日志
└── test_summary.md                         # 统一测试报告
```

---

## 💡 使用建议

### 开发环境

1. **查看文档** → README.md
2. **查看计划** → VNPY_COMPREHENSIVE_TEST_PLAN.md
3. **查看指南** → VNPY_COMPLETE_GUIDE.md
4. **运行测试** → run_all_tests.py
5. **查看进度** → TEST_PROGRESS.md

### 测试流程

1. 运行 `run_all_tests.py`
2. 查看 `logs/test_summary.md`
3. 查看 `docs/TEST_PROGRESS.md`
4. 更新进度和问题记录

### Web UI 开发（所有测试完成后）

1. 技术选型
2. 后端 API 开发
3. 前端 UI 开发
4. 集成测试
5. 部署上线

---

**最后更新**: 2026-02-20
**文档版本**: 1.0
