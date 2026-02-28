# MEMORY.md - Long-term Memory

## 用户概况

- **名称**: 社会主义 信仰
- **Telegram**: @tianxinfeng (id: 744751080)
- **时区**: UTC (当前时间显示为 UTC)

## 模型配置

### 当前配置（2026-02-21 优化后）
- **提供商**: 智谱AI开放平台 (bigmodel.cn) - 官方 API
- **模型分级**（按质量和成本）:
  - `glm-4.7`: ⭐⭐⭐⭐ 最强 - 💰 付费
  - `glm-4.6`: ⭐⭐⭐ 次强 - 💰 付费
  - `glm-4.7-Flash`: ⭐⭐ 简单 - 🆓 免费
  - `glm-4.6V-Flash`: ⭐ 最简单 - 🆓 免费

### 配置文件
- **位置**: `~/.openclaw/openclaw.json`
- **自定义提供商名称**: `glm`（用户手动修改后）
- **API 端点**: `https://open.bigmodel.cn/api/coding/paas/v4`

### API Key
- 已配置在 `BIGMODEL_API_KEY` 环境变量中
- Key: `63c8b255a3fd48168a8dc5329f27c41c.jPgGCTA1yX1u9eEa`

---

## 项目架构

### 量化工厂 Agent 列表
1. **研究员** (researcher) 🔬 - 任务调度者 + 高级研究
2. **工程师** (coder) 💻 - 编码开发
3. **测试员** (tester) 🧪 - 测试
4. **文档师** (writer) 📝 - 文档
5. **数据工程师** (data) 📊 - 数据处理
6. **分析师** (analyst) 📈 - 分析
7. **总指挥** (zongzhihui) 🎯 - 备用指挥
8. **军师** (junshi) 🧠 - 策略
9. **智库** (zhiku) 📚 - 知识库

### 工作空间
- 主工作区: `/root/.openclaw/workspace`
- 量化工厂: `/root/.openclaw/workspace/quant-factory/agents/`

---

## 2026-02-21 配置优化决策

### 问题
用户发现 OpenClaw 成本过高（$35-40/天），需要优化配置。

### 解决方案
根据 @PrajwalTomar_ 的推文建议，实施模型分层策略：

#### 1. Agent 模型分配
| Agent | 模型 | 理由 |
|--------|------|------|
| 研究员 | `glm-4.7` | 调度需要强推理 |
| 工程师 | `glm-4.7` | 复杂编码任务 |
| 军师 | `glm-4.6` | 策略推理 |
| 分析师 | `glm-4.6` | 数据分析 |
| 智库 | `glm-4.6` | 知识整理 |
| 文档师 | `glm-4.7-Flash` | 简单文档（免费） |
| 测试员 | `glm-4.7-Flash` | 简单测试（免费） |
| 数据工程师 | `glm-4.7-Flash` | 简单数据处理（免费） |
| 总指挥 | `glm-4.7-Flash` | 备用/特定场景（降低成本） |

#### 2. 全局优化
- **子任务模型**: `glm/glm-4.7-Flash`（免费）
- **所有 Heartbeats**: `glm/glm-4.6V-Flash`（最便宜）

#### 3. 研究员角色升级
- **新增功能**: 任务调度者
- **职责**: 评估任务、分配给最佳 agent、协调整合
- **文档**: `DISPATCH.md` - 详细调度规则

### 预期节省
- Heartbeats: 从付费模型 → 免费模型（显著节省）
- 简单任务: 使用免费模型（文档、测试、数据）
- 子任务: 所有使用免费模型
- 复杂任务: 保留付费模型保证质量

---

## 技术决策

### MCP 协议
- 智谱AI提供 MCP web-reader 服务，但 OpenClaw 不支持标准 MCP 协议
- 替代方案：使用 OpenClaw 内置的 `web_fetch` 工具

### x-tweet-fetcher
- **位置**: `/root/.nvm/versions/node/v22.22.0/lib/node_modules/openclaw/skills/x-tweet-fetcher`
- **功能**: 抓取 X/Twitter/微博/B站/CSDN/微信公众号
- **Camofox**: 已安装用于需要 JS 渲染的平台

### Camofox
- **安装位置**: `/root/.openclaw/extensions/camofox-browser`
- **端口**: 9377
- **状态**: 已安装并运行

---

## 注意事项

- 配置敏感信息（如 API Key）记录在环境变量中，不要直接硬编码
- 用户喜欢自己手动修改配置文件
- OpenClaw 不支持 `model.tiers` 字段，直接在每个 agent 级别设置模型
- 研究员担任调度者角色，读取 `DISPATCH.md` 了解规则
