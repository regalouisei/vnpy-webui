# Web UI 开发计划

**项目名称**: VnPy Web UI
**开始时间**: 2026-02-20 08:48:00 UTC
**预计时间**: 1-2 周

---

## 🎯 项目目标

开发一个功能完整的 Web UI，覆盖 VnPy 的所有功能，达到甚至超过 VeighNa Studio 的水平。

---

## 🏗️ 技术栈

### 后端技术

- **框架**: FastAPI (Python)
- **数据库**: SQLite / MySQL / PostgreSQL
- **实时通信**: WebSocket
- **API 文档**: Swagger/OpenAPI

### 前端技术

- **框架**: React / Vue.js
- **UI 组件库**: Ant Design / Element Plus
- **图表库**: Plotly.js / ECharts
- **状态管理**: Redux / Pinia
- **实时通信**: WebSocket

### 数据可视化

- **K 线图表**: Plotly / ECharts
- **深度图**: Plotly
- **分时图**: Plotly / ECharts
- **成交量**: 柱状图

---

## 📁 项目结构

```
vnpy-webui/
├── backend/              # 后端代码
│   ├── app/            # FastAPI 应用
│   │   ├── api/        # API 路由
│   │   ├── core/       # 核心逻辑
│   │   ├── models/     # 数据模型
│   │   ├── schemas/    # Pydantic 模式
│   │   └── utils/      # 工具函数
│   ├── database/       # 数据库配置
│   ├── vnpy/           # VnPy 集成
│   └── main.py         # 应用入口
├── frontend/            # 前端代码
│   ├── src/
│   │   ├── assets/     # 静态资源
│   │   ├── components/ # React 组件
│   │   ├── pages/      # 页面组件
│   │   ├── api/        # API 客户端
│   │   ├── hooks/      # React Hooks
│   │   ├── store/      # Redux store
│   │   ├── styles/     # 样式文件
│   │   └── App.tsx      # 应用入口
│   ├── public/         # 公共资源
│   └── package.json
├── docs/               # 文档
│   ├── API.md         # API 文档
│   ├── UI.md          # UI 设计文档
│   └── ARCHITECTURE.md # 架构设计
└── README.md           # 项目说明
```

---

## 🔧 开发环境

### 后端依赖

```bash
# FastAPI
pip install fastapi uvicorn

# 数据库
pip install sqlalchemy pymysql psycopg2-binary

# 数据验证
pip install pydantic

# CORS 支持
pip install python-multipart

# WebSocket
pip install websockets
```

### 前端依赖

```bash
# Create React App
npm create react-app frontend

# 安装依赖
cd frontend
npm install antd @ant-design/icons
npm install react-router-dom
npm install axios
npm install recharts
npm install @reduxjs/toolkit
npm install react-redux
npm install socket.io-client
```

---

## 📋 功能列表

### 第一阶段：基础功能

1. **账户管理界面**
   - 账户信息显示
   - 资金曲线
   - 持仓明细

2. **持仓管理界面**
   - 持仓列表
   - 持仓详情
   - 持仓盈亏

3. **行情显示界面**
   - 实时行情
   - 行情订阅
   - 多合约行情

### 第二阶段：高级功能

4. **K 线图表界面**
   - K 线显示
   - 技术指标
   - 图表缩放

5. **策略管理界面**
   - 策略列表
   - 策略配置
   - 策略状态
   - 策略日志

6. **回测界面**
   - 参数设置
   - 回测执行
   - 回测报告
   - 图表显示

### 第三阶段：交易功能

7. **交易界面**
   - 下单界面
   - 持仓监控
   - 成交明细
   - 订单管理

8. **数据管理界面**
   - 数据导入
   - 数据导出
   - 数据清洗
   - 数据备份

### 第四阶段：高级功能

9. **报表分析界面**
   - 收益分析
   - 风险分析
   - 放大图
   - 月度报表

10. **实时推送**
    - 实时行情推送
    - 订单状态推送
    - 持仓变化推送

---

## 🚀 开发阶段

### 阶段 1: 项目初始化

- [ ] 创建项目结构
- [ ] 配置开发环境
- [ ] 初始化后端项目
- [ ] 初始化前端项目
- [ ] 配置 Git 仓库

### 阶段 2: 后端开发

- [ ] 创建 FastAPI 应用
- [ ] 集成 VnPy
- [ ] 实现 WebSocket
- [ ] 实现数据库连接
- [ ] 实现 API 路由

### 阶段 3: 前端开发

- [ ] 创建 React 应用
- [ ] 实现基础布局
- [ ] 实现 API 客户端
- [ ] 实现 WebSocket 客户端
- [ ] 实现组件库

### 阶段 4: 功能开发

- [ ] 账户管理功能
- [ ] 持仓管理功能
- [ ] 行情显示功能
- [ ] K 线图表功能
- [ ] 策略管理功能
- [ ] 回测功能
- [ ] 交易功能
- [ ] 数据管理功能
- [ ] 报表分析功能

### 阶段 5: 集成和优化

- [ ] 前后端集成
- [ ] 性能优化
- [ ] 安全加固
- [ ] 部署上线

---

## 📄 文档规划

1. **API.md** - API 文档
2. **UI.md** - UI 设计文档
3. **ARCHITECTURE.md** - 架构设计
4. **DEVELOPMENT.md** - 开发指南
5. **DEPLOYMENT.md** - 部署指南

---

## 🎯 下一步

立即开始项目初始化！

---

**计划创建时间**: 2026-02-20 08:48:00 UTC
**计划状态**: 准备执行
