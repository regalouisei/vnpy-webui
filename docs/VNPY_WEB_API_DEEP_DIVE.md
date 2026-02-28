# VnPy Web Trader API 深度解析

**版本**: VnPy 3.x
**更新时间**: 2026-02-20

---

## 1. Web API 的基本概念和功能

WebTrader 是 VnPy 框架的 Web 应用后端服务模块，让用户可以通过浏览器（而非 PyQt 桌面端）运行和管理 VeighNa 量化策略交易。

**核心功能**：
- **远程交易管理**：通过浏览器进行手动交易（下单、撤单、查询）
- **实时行情订阅**：订阅和接收市场行情数据的实时推送
- **账户信息查询**：查询账户资金、持仓、委托和成交数据
- **策略交易支持**：为未来的策略交易管理提供接口基础

**技术优势**：
- 零部署成本，只需浏览器即可访问
- 支持桌面、平板、手机等多设备
- 可方便地嵌入到现有 Web 应用中

---

## 2. vn.py Web API 系统架构概述

### 2.1 双进程架构

WebTrader 采用独特的双进程架构，将策略交易和 Web 服务分离：

```
┌─────────────┐    REST/WS    ┌─────────────┐    RPC     ┌─────────────┐
│  浏览器      │ ────────────► │  Web 进程    │ ─────────► │  策略进程    │
│  (Browser)  │◄──────────── │ (FastAPI)    │◄───────── │ (Trading)    │
└─────────────┘               └─────────────┘            └─────────────┘
```

**策略交易进程**：
- 运行完整的 VeighNa Trader 系统
- 启动 RPC Server 接受调用
- 负责所有交易功能执行

**Web 服务进程**：
- 运行 FastAPI Web 服务器
- 管理 WebSocket 长连接
- 启动 RPC Client 调用策略进程

### 2.2 通信模式

**主动请求调用**（Request-Response）：
```
浏览器 → REST API → Web 进程 → RPC → 策略进程 → RPC 响应 → Web 进程 → HTTP 响应 → 浏览器
```

**被动数据推送**（Publish-Subscribe）：
```
策略进程 → RPC 推送 → Web 进程 → WebSocket → 浏览器
```

---

## 3. RESTful 接口设计

### 3.1 技术栈

WebTrader 基于 **FastAPI** 构建，具有高性能、自动文档、类型验证等特点。

### 3.2 核心接口

**认证接口**：
- `POST /token` - 获取访问令牌

**行情接口**：
- `POST /tick/{symbol}` - 订阅合约行情
- `GET /tick` - 查询所有行情数据
- `GET /contract` - 查询合约信息

**交易接口**：
- `POST /order` - 发送委托订单
- `DELETE /order/{vt_orderid}` - 撤销委托订单
- `GET /order` - 查询所有委托

**账户接口**：
- `GET /account` - 查询账户资金
- `GET /position` - 查询持仓信息
- `GET /trade` - 查询成交记录

### 3.3 接口示例

**获取令牌**：

```python
import requests

url = "http://127.0.0.1:8000/"
r = requests.post(
    url + "token",
    data={"username": "vnpy", "password": "vnpy"}
)
token = r.json()["access_token"]
```

**发送订单**：

```python
order_req = {
    "symbol": "cu2112",
    "exchange": "SHFE",
    "direction": "多",
    "type": "限价",
    "volume": 1,
    "price": 71030.0,
    "offset": "开",
    "reference": "WebTrader"
}

r = requests.post(
    url + "order",
    json=order_req,
    headers={"Authorization": f"Bearer {token}"}
)
vt_orderid = r.json()["data"]
```

---

## 4. WebSocket 实时推送

### 4.1 连接建立

```python
from websocket import create_connection

ws = create_connection(f"ws://127.0.0.1:8000/ws/?token={token}")
```

### 4.2 消息格式

WebSocket 消息采用 JSON 格式：

```json
{
  "type": "tick|order|trade|account|position",
  "data": {
    "symbol": "cu2112.SHFE",
    "last_price": 71030.0,
    ...
  }
}
```

### 4.3 接收示例

```python
import json

while True:
    message = ws.recv()
    msg_obj = json.loads(message)
    msg_type = msg_obj.get("type")
    data = msg_obj.get("data")

    if msg_type == "tick":
        print(f"行情: {data['symbol']} @ {data['last_price']}")
    elif msg_type == "order":
        print(f"订单: {data['orderid']} - {data['status']}")
```

---

## 5. 认证和授权机制

### 5.1 认证流程

WebTrader 采用 **Bearer Token** 认证机制，基于 JWT 标准：

```python
# 步骤 1：发送认证请求
r = requests.post(
    "http://127.0.0.1:8000/token",
    data={"username": "vnpy", "password": "vnpy"}
)

# 步骤 2：获取 Token
token = r.json()["access_token"]

# 步骤 3：使用 Token
headers = {"Authorization": f"Bearer {token}"}
r = requests.get("http://127.0.0.1:8000/account", headers=headers)
```

### 5.2 配置文件

**web_trader_setting.json**：

```json
{
  "username": "vnpy",
  "password": "vnpy",
  "req_address": "tcp://127.0.0.1:20100",
  "sub_address": "tcp://127.0.0.1:20101",
  "token_expire_hours": 24
}
```

---

## 6. API 使用示例

### 6.1 完整交易流程

```python
import requests
import json
from websocket import create_connection

class VnPyTrader:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.token = None
        self.ws = None

    def login(self, username, password):
        r = requests.post(
            f"{self.base_url}/token",
            data={"username": username, "password": password}
        )
        if r.status_code == 200:
            self.token = r.json()["access_token"]
            return True
        return False

    def send_order(self, order_req):
        r = requests.post(
            f"{self.base_url}/order",
            json=order_req,
            headers={"Authorization": f"Bearer {self.token}"}
        )
        if r.status_code == 200:
            return r.json()["data"]
        return None

    def connect_ws(self):
        ws_url = f"ws://127.0.0.1:8000/ws/?token={self.token}"
        self.ws = create_connection(ws_url)

# 使用
trader = VnPyTrader()
trader.login("vnpy", "vnpy")

order_req = {
    "symbol": "cu2112",
    "exchange": "SHFE",
    "direction": "多",
    "type": "限价",
    "volume": 1,
    "price": 71030.0,
    "offset": "开"
}
vt_orderid = trader.send_order(order_req)

trader.connect_ws()
while True:
    message = trader.ws.recv()
    print(json.loads(message))
```

---

## 7. 性能优化技巧

### 7.1 连接池优化

使用 `requests.Session` 复用连接：

```python
session = requests.Session()
for i in range(100):
    response = session.get("http://127.0.0.1:8000/account")
```

### 7.2 批量操作

使用多线程并发处理：

```python
import concurrent.futures

def subscribe_symbol(symbol):
    requests.post(
        f"http://127.0.0.1:8000/tick/{symbol}",
        headers={"Authorization": f"Bearer {token}"}
    )

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    executor.map(subscribe_symbol, symbols)
```

### 7.3 WebSocket 消息处理优化

使用队列处理消息：

```python
import queue
import threading

message_queue = queue.Queue()

def receive_loop():
    while True:
        message = ws.recv()
        message_queue.put(message)

def process_loop():
    while True:
        message = message_queue.get()
        # 处理消息
        pass

# 启动线程
threading.Thread(target=receive_loop, daemon=True).start()
threading.Thread(target=process_loop, daemon=True).start()
```

---

## 8. 安全性考虑

### 8.1 网络安全

- **加密通信**：生产环境使用 HTTPS 和 WSS
- **证书验证**：启用 SSL 证书验证

```python
response = requests.get(
    "https://your-server.com/account",
    verify=True,  # 启用证书验证
    headers={"Authorization": f"Bearer {token}"}
)
```

### 8.2 身份认证

- **环境变量**：不要硬编码凭证

```python
import os
USERNAME = os.getenv("VNPY_USERNAME")
PASSWORD = os.getenv("VNPY_PASSWORD")
```

### 8.3 授权控制

实现权限分级（只读、交易、管理员），并记录操作审计日志。

### 8.4 速率限制

防止滥用和 DDoS 攻击，在服务端实现 API 调用频率限制。

---

## 9. 最佳实践建议

### 9.1 错误处理

统一异常处理和重试机制：

```python
from functools import wraps
import time

def retry(max_attempts=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    if attempt < max_attempts - 1:
                        time.sleep(delay * (attempt + 1))
        return wrapper
    return decorator

@retry(max_attempts=3)
def send_order_with_retry(order_req):
    return send_order(order_req)
```

### 9.2 日志记录

配置结构化日志：

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("vnpy_web")
logger.info("订单已发送")
```

### 9.3 代码组织

推荐的项目结构：

```
vnpy_web_project/
├── config/          # 配置文件
├── services/        # 业务服务
├── models/          # 数据模型
├── utils/           # 工具函数
├── tests/           # 测试
└── main.py          # 主程序
```

---

## 10. 部署和运维指南

### 10.1 启动服务

**策略交易进程**：

```bash
source venv/bin/activate
python trading_main.py &
```

**Web 服务进程**：

```bash
uvicorn web_main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 10.2 systemd 管理

创建 systemd 服务文件实现自动启动和重启：

```ini
# /etc/systemd/system/vnpy-trading.service
[Unit]
Description=VnPy Trading Service
After=network.target

[Service]
Type=simple
User=vnpy
ExecStart=/path/to/venv/bin/python trading_main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### 10.3 反向代理

使用 Nginx 配置 HTTPS 和负载均衡：

```nginx
upstream vnpy_backend {
    server 127.0.0.1:8000;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/ssl/certs/vnpy.crt;
    ssl_certificate_key /etc/ssl/private/vnpy.key;

    location / {
        proxy_pass http://vnpy_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 10.4 监控维护

**健康检查**：

```python
def health_check():
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False
```

**日志管理**：

配置日志轮转，定期清理旧日志。

---

## 附录

### A. API 文档

启动 Web 服务后，访问以下地址查看完整 API 文档：

- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

### B. 相关资源

- **VnPy 官网**: https://www.vnpy.com
- **VnPy 文档**: https://docs.vnpy.com
- **FastAPI 文档**: https://fastapi.tiangolo.com

---

**文档结束**

如有问题，请访问 VnPy 社区: https://www.vnpy.com/forum
