# MEMORY.md - 记忆配置

## 长期记忆
- 存储位置: /root/.openclaw/workspace/quant-factory/memory/
- 包含: 历史项目、策略模板、代码片段、学习笔记

## 短期记忆
- 每个代理维护自己的会话历史
- 代理间不共享短期记忆（完全隔离）

## 上下文
- 读取 shared/GOALS.md 获取当前目标
- 读取 shared/DECISIONS.md 获取历史决策
- 读取 shared/PROJECTS.md 获取项目进度

## 代理私有记忆
- agents/zongzhihui/ - 总指挥的协调笔记
- agents/junshi/ - 军师的分析笔记
- agents/engineer_a/ - 工程师A的技术笔记
- agents/engineer_b/ - 工程师B的测试笔记
- agents/zhiku/ - 智库的审核笔记
