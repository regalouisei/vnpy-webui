# VnPy CTP 网关深度解析

**模块**: vnpy_ctp
**版本**: VnPy 3.x
**更新时间**: 2026-02-20
**难度**: ⭐⭐⭐⭐

---

## 目录

1. [CTP 概述](#1-ctp-概述)
2. [CTP API 架构](#2-ctp-api-架构)
3. [CtpGateway 网关](#3-ctpgateway-网关)
4. [交易接口 CtpTdApi](#4-交易接口-ctptdapi)
5. [行情接口 CtpMdApi](#5-行情接口-ctpmdapi)
6. [连接流程](#6-连接流程)
7. [自动查询机制](#7-自动查询机制)
8. [数据转换](#8-数据转换)
9. [事件发布](#9-事件发布)
10. [故障排查](#10-故障排查)

---

## 1. CTP 概述

### 1.1 什么是 CTP

**CTP (Comprehensive Transaction Platform)** 是上海期货信息技术有限公司（上期技术）推出的综合交易平台。

**特点**:
- 国内期货市场标准接口
- 提供交易和行情 API
- 支持国内主要期货交易所

### 1.2 CTP API 版本

| 版本 | 发布时间 | 特点 |
|------|---------|------|
| 6.3.0 | 2018 | 经典版本 |
| 6.5.1 | 2020 | 稳定版本 |
| 6.6.1 | 2021 | 推荐版本 |
| 6.6.1_P1_20210927 | 2021 | 最新稳定版 |

### 1.3 CTP 测试环境

**SimNow** (上期所模拟环境):
- 地址: http://www.simnow.com.cn
- 特点: 官方测试环境，行情为实盘行情

**OpenCTP** (第三方测试环境):
- 地址: http://openctp.cn
- 特点: 免费开放，无时间限制
- 账号: 17130 / 密码: 123456

---

## 2. CTP API 架构

### 2.1 CTP API 组成

```
CTP API
├── 交易 API (thosttraderapi_se.dll/so)
│   ├── CThostFtdcTraderApi          # 交易 API 基类
│   ├── CThostFtdcTraderSpi          # 交易回调基类
│   └── 相关结构体
│
└── 行情 API (thostmduserapi_se.dll/so)
    ├── CThostFtdcMdApi              # 行情 API 基类
    ├── CThostFtdcMdSpi              # 行情回调基类
    └── 相关结构体
```

### 2.2 CTP API 文件

**Windows**:
```
thosttraderapi_se.dll    # 交易 API (32/64位)
thostmduserapi_se.dll    # 行情 API (32/64位)
```

**Linux**:
```
libthosttraderapi_se.so  # 交易 API
libthostmduserapi_se.so  # 行情 API
```

**macOS**:
```
libthosttraderapi_se.dylib  # 交易 API
libthostmduserapi_se.dylib  # 行情 API
```

### 2.3 CTP API 安装

```bash
# Linux: 复制到系统库目录
sudo cp libthosttraderapi_se.so /usr/local/lib/
sudo cp libthostmduserapi_se.so /usr/local/lib/
sudo ldconfig

# 或放在项目根目录（推荐）
cp libthosttraderapi_se.so /path/to/project/
cp libthostmduserapi_se.so /path/to/project/
```

---

## 3. CtpGateway 网关

### 3.1 CtpGateway 职责

**CtpGateway** 负责:

1. **API 封装**: 封装 CTP API 调用
2. **连接管理**: 管理与 CTP 服务器的连接
3. **数据转换**: 将 CTP 结构体转换为 VnPy 对象
4. **事件发布**: 发布交易和行情事件
5. **定时查询**: 定时查询账户和持仓

### 3.2 CtpGateway 初始化

```python
class CtpGateway(BaseGateway):
    """CTP 网关"""

    def __init__(self, main_engine: MainEngine, gateway_name: str):
        """初始化"""
        super().__init__(main_engine, event_engine, gateway_name)

        # 交易 API
        self.td_api = CtpTdApi(self)

        # 行情 API
        self.md_api = CtpMdApi(self)

        # 订单映射 (本地 ID -> CTP ID)
        self.orders: Dict[str, OrderData] = {}
        self.sysid_orderid_map: Dict[str, str] = {}

        # 合约缓存
        self.contracts: Dict[str, ContractData] = {}

        # 自动查询
        self.count = 0
        self.query_functions: list = []
```

### 3.3 CtpGateway.connect()

**连接流程**:

```python
def connect(self, setting: dict):
    """连接 CTP 服务器"""

    # 1. 连接交易 API
    self.td_api.connect(
        setting.get("交易服务器", ""),
        setting.get("用户名", ""),
        setting.get("密码", ""),
        setting.get("经纪商代码", ""),
        setting.get("产品名称", ""),
        setting.get("授权编码", ""),
        setting.get("柜台环境", "")
    )

    # 2. 连接行情 API
    self.md_api.connect(
        setting.get("行情服务器", ""),
        setting.get("用户名", ""),
        setting.get("密码", ""),
        setting.get("经纪商代码", "")
    )

    # 3. 启动定时查询
    self.init_query()
```

---

## 4. 交易接口 CtpTdApi

### 4.1 CtpTdApi 职责

**CtpTdApi** 负责:

1. **连接管理**: 连接交易服务器
2. **认证登录**: 用户登录和认证
3. **报单撤单**: 发送订单和撤单请求
4. **查询操作**: 查询账户/持仓/订单/成交
5. **回调处理**: 处理交易相关回调

### 4.2 CtpTdApi 连接

```python
def connect(
    self,
    td_address: str,
    userid: str,
    password: str,
    brokerid: str,
    appid: str,
    auth_code: str,
    product_info: str
):
    """连接交易服务器"""

    # 1. 创建 CTP API 实例
    self.api = CThostFtdcTraderApi.CreateFtdcTraderApi(
        self.gateway_name + "_td"
    )

    # 2. 注册回调
    self.api.RegisterSpi(self)

    # 3. 订阅公共流
    self.api.SubscribePublicTopic(THOST_TERT_RESTART)

    # 4. 连接前端
    self.api.RegisterFront(td_address)
    self.api.Init()

    # 5. 保存登录信息
    self.userid = userid
    self.password = password
    self.brokerid = brokerid
    self.appid = appid
    self.auth_code = auth_code
    self.product_info = product_info
```

### 4.3 CtpTdApi 回调

#### onFrontConnected() - 连接成功

```python
def onFrontConnected(self):
    """连接成功回调"""
    self.gateway.write_log("交易服务器连接成功")

    # 准备认证请求
    req = {
        "UserID": self.userid,
        "Password": self.password,
        "BrokerID": self.brokerid,
        "AppID": self.appid,
        "AuthCode": self.auth_code,
        "ProductInfo": self.product_info,
    }

    # 发送认证请求
    self.reqid += 1
    self.api.ReqAuthenticate(req, self.reqid)
```

#### onRspAuthenticate() - 认证响应

```python
def onRspAuthenticate(self, data: dict, error: dict, reqid: int, last: bool):
    """认证响应"""
    if error["ErrorID"] != 0:
        self.gateway.write_log(f"认证失败: {error['ErrorMsg']}")
        return

    self.gateway.write_log("认证成功，正在登录...")

    # 准备登录请求
    req = {
        "UserID": self.userid,
        "Password": self.password,
        "BrokerID": self.brokerid,
        "AppID": self.appid,
        "AuthCode": self.auth_code,
        "ProductInfo": self.product_info,
    }

    # 发送登录请求
    self.reqid += 1
    self.api.ReqUserLogin(req, self.reqid)
```

#### onRspUserLogin() - 登录响应

```python
def onRspUserLogin(self, data: dict, error: dict, reqid: int, last: bool):
    """登录响应"""
    if error["ErrorID"] != 0:
        self.gateway.write_log(f"登录失败: {error['ErrorMsg']}")
        return

    self.gateway.write_log("登录成功")
    self.login_status = True

    # 保存会话信息
    self.frontid = data["FrontID"]
    self.sessionid = data["SessionID"]

    # 确认结算单
    self.reqid += 1
    self.api.ReqSettlementInfoConfirm({}, self.reqid)

    # 查询合约
    self.query_contract()
```

### 4.4 CtpTdApi 查询

#### query_account() - 查询账户

```python
def query_account(self):
    """查询账户"""
    if not self.login_status:
        return

    req = {
        "BrokerID": self.brokerid,
        "InvestorID": self.userid,
    }

    self.reqid += 1
    self.api.ReqQryTradingAccount(req, self.reqid)
```

#### onRspQryTradingAccount() - 账户响应

```python
def onRspQryTradingAccount(self, data: dict, error: dict, reqid: int, last: bool):
    """账户响应"""
    if error["ErrorID"] != 0:
        return

    # 创建账户对象
    account = AccountData(
        accountid=data["AccountID"],
        balance=data["Balance"],
        available=data["Available"],
        frozen=data["CurrMargin"] + data["FrozenMargin"],
        currency="CNY",
        gateway_name=self.gateway_name
    )

    # 发布账户事件
    self.gateway.on_account(account)
```

#### query_position() - 查询持仓

```python
def query_position(self):
    """查询持仓"""
    if not self.login_status:
        return

    req = {
        "BrokerID": self.brokerid,
        "InvestorID": self.userid,
    }

    self.reqid += 1
    self.api.ReqQryInvestorPosition(req, self.reqid)
```

#### onRspQryInvestorPosition() - 持仓响应

```python
def onRspQryInvestorPosition(self, data: dict, error: dict, reqid: int, last: bool):
    """持仓响应"""
    if error["ErrorID"] != 0:
        return

    # 查询合约信息
    contract = self.gateway.contracts.get(data["InstrumentID"])
    if not contract:
        return

    # 创建持仓对象
    position = PositionData(
        symbol=data["InstrumentID"],
        exchange=contract.exchange,
        direction=DIRECTION_CTP2VT[data["PosiDirection"]],
        volume=data["Position"],
        frozen=data["ShortFrozen"],
        open_price=data["OpenPrice"],
        pnl=data["PositionProfit"],
        gateway_name=self.gateway_name
    )

    # 发布持仓事件
    self.gateway.on_position(position)
```

#### query_order() - 查询订单

```python
def query_order(self):
    """查询订单"""
    if not self.login_status:
        return

    req = {
        "BrokerID": self.brokerid,
        "InvestorID": self.userid,
    }

    self.reqid += 1
    self.api.ReqQryOrder(req, self.reqid)
```

#### query_trade() - 查询成交

```python
def query_trade(self):
    """查询成交"""
    if not self.login_status:
        return

    req = {
        "BrokerID": self.brokerid,
        "InvestorID": self.userid,
    }

    self.reqid += 1
    self.api.ReqQryTrade(req, self.reqid)
```

### 4.5 CtpTdApi 报单

#### send_order() - 发送订单

```python
def send_order(self, req: OrderRequest):
    """发送订单"""
    # 查询合约
    contract = self.gateway.contracts.get(req.symbol)
    if not contract:
        return ""

    # 创建订单请求
    ctp_req = {
        "InstrumentID": contract.symbol,
        "LimitPrice": req.price,
        "VolumeTotalOriginal": req.volume,
        "OrderPriceType": ORDERTYPE_VT2CTP.get(req.type, ""),
        "Direction": DIRECTION_VT2CTP.get(req.direction, ""),
        "CombOffsetFlag": OFFSET_VT2CTP.get(req.offset, ""),
        "HedgeFlag": THOST_FTDC_HF_Speculation,  # 投机
        "BrokerID": self.brokerid,
        "InvestorID": self.userid,
        "UserID": self.userid,
    }

    # 发送订单
    self.reqid += 1
    self.api.ReqOrderInsert(ctp_req, self.reqid)

    return self.orderid
```

#### onRspOrderInsert() - 报单响应

```python
def onRspOrderInsert(self, data: dict, error: dict, reqid: int, last: bool):
    """报单响应"""
    if error["ErrorID"] != 0:
        self.gateway.write_log(f"报单失败: {error['ErrorMsg']}")
        return

    # 创建订单对象
    order = OrderData(
        orderid=self.orderid,
        symbol=data["InstrumentID"],
        exchange=self.gateway.contracts[data["InstrumentID"]].exchange,
        direction=DIRECTION_CTP2VT.get(data["Direction"], Direction.LONG),
        offset=OFFSET_CTP2VT.get(data["CombOffsetFlag"], Offset.OPEN),
        type=ORDERTYPE_CTP2VT.get(data["OrderPriceType"], OrderType.LIMIT),
        volume=data["VolumeTotalOriginal"],
        traded=0,
        price=data["LimitPrice"],
        status=Status.SUBMITTING,
        gateway_name=self.gateway_name
    )

    # 发布订单事件
    self.gateway.on_order(order)
```

#### onRtnOrder() - 订单回报

```python
def onRtnOrder(self, data: dict):
    """订单回报"""
    # 查找订单
    sysid = data["OrderSysID"]
    order = self.gateway.sysid_orderid_map.get(sysid)

    if order:
        # 更新订单状态
        order.status = STATUS_CTP2VT.get(
            data["OrderStatus"],
            Status.SUBMITTING
        )
        order.traded = data["VolumeTraded"]

        # 发布订单事件
        self.gateway.on_order(order)
```

#### onRtnTrade() - 成交回报

```python
def onRtnTrade(self, data: dict):
    """成交回报"""
    # 查找订单
    sysid = data["OrderSysID"]
    order = self.gateway.sysid_orderid_map.get(sysid)

    if order:
        # 更新订单成交数量
        order.traded += data["Volume"]

        # 创建成交对象
        trade = TradeData(
            tradeid=data["TradeID"],
            symbol=order.symbol,
            exchange=order.exchange,
            orderid=order.orderid,
            direction=order.direction,
            offset=order.offset,
            price=data["Price"],
            volume=data["Volume"],
            datetime=datetime.now(),
            gateway_name=self.gateway_name
        )

        # 发布成交事件
        self.gateway.on_trade(trade)
```

### 4.6 CtpTdApi 撤单

#### cancel_order() - 撤销订单

```python
def cancel_order(self, req: CancelRequest):
    """撤销订单"""
    # 查找订单
    order = self.gateway.get_order(req.orderid)
    if not order:
        return

    # 创建撤单请求
    ctp_req = {
        "InstrumentID": order.symbol,
        "OrderRef": order.orderid,
        "FrontID": self.frontid,
        "SessionID": self.sessionid,
        "ActionFlag": THOST_FTDC_AF_Delete,
        "BrokerID": self.brokerid,
        "InvestorID": self.userid,
    }

    # 发送撤单
    self.reqid += 1
    self.api.ReqOrderAction(ctp_req, self.reqid)
```

#### onRspOrderAction() - 撤单响应

```python
def onRspOrderAction(self, data: dict, error: dict, reqid: int, last: bool):
    """撤单响应"""
    if error["ErrorID"] != 0:
        self.gateway.write_log(f"撤单失败: {error['ErrorMsg']}")
        return

    self.gateway.write_log("撤单成功")
```

---

## 5. 行情接口 CtpMdApi

### 5.1 CtpMdApi 职责

**CtpMdApi** 负责:

1. **连接管理**: 连接行情服务器
2. **认证登录**: 用户登录和认证
3. **行情订阅**: 订阅和取消订阅行情
4. **行情接收**: 接收实时行情数据
5. **回调处理**: 处理行情相关回调

### 5.2 CtpMdApi 连接

```python
def connect(
    self,
    md_address: str,
    userid: str,
    password: str,
    brokerid: str
):
    """连接行情服务器"""

    # 1. 创建 CTP 行情 API 实例
    self.api = CThostFtdcMdApi.CreateFtdcMdApi(
        self.gateway_name + "_md"
    )

    # 2. 注册回调
    self.api.RegisterSpi(self)

    # 3. 连接前端
    self.api.RegisterFront(md_address)
    self.api.Init()

    # 4. 保存登录信息
    self.userid = userid
    self.password = password
    self.brokerid = brokerid
```

### 5.3 CtpMdApi 回调

#### onFrontConnected() - 连接成功

```python
def onFrontConnected(self):
    """连接成功回调"""
    self.gateway.write_log("行情服务器连接成功")

    # 准备登录请求
    req = {
        "UserID": self.userid,
        "Password": self.password,
        "BrokerID": self.brokerid,
    }

    # 发送登录请求
    self.reqid += 1
    self.api.ReqUserLogin(req, self.reqid)
```

#### onRspUserLogin() - 登录响应

```python
def onRspUserLogin(self, data: dict, error: dict, reqid: int, last: bool):
    """登录响应"""
    if error["ErrorID"] != 0:
        self.gateway.write_log(f"行情登录失败: {error['ErrorMsg']}")
        return

    self.gateway.write_log("行情登录成功")
    self.login_status = True

    # 查询合约
    self.query_contract()
```

### 5.4 CtpMdApi 行情订阅

#### subscribe() - 订阅行情

```python
def subscribe(self, req: SubscribeRequest):
    """订阅行情"""
    # 查询合约
    contract = self.gateway.contracts.get(req.symbol)
    if not contract:
        return

    # 订阅行情
    self.api.SubscribeMarketData([contract.symbol])

    self.gateway.write_log(f"订阅行情: {contract.symbol}")
```

#### onRtnDepthMarketData() - 行情回报

```python
def onRtnDepthMarketData(self, data: dict):
    """行情回报"""
    # 创建 Tick 对象
    tick = TickData(
        symbol=data["InstrumentID"],
        exchange=self.gateway.contracts[data["InstrumentID"]].exchange,
        datetime=datetime.now(),
        gateway_name=self.gateway_name,
        name=data["InstrumentName"],

        # 最新价
        last_price=data["LastPrice"],
        volume=data["Volume"],
        open_interest=data["OpenInterest"],

        # 卖一
        ask_price_1=data["AskPrice1"],
        ask_volume_1=data["AskVolume1"],

        # 卖二
        ask_price_2=data["AskPrice2"],
        ask_volume_2=data["AskVolume2"],

        # ... 卖三、四、五

        # 买一
        bid_price_1=data["BidPrice1"],
        bid_volume_1=data["BidVolume1"],

        # 买二
        bid_price_2=data["BidPrice2"],
        bid_volume_2=data["BidVolume2"],

        # ... 买三、四、五

        # 其他
        upper_limit=data["UpperLimitPrice"],
        lower_limit=data["LowerLimitPrice"],
        pre_close=data["PreClosePrice"],
    )

    # 发布 Tick 事件
    self.gateway.on_tick(tick)
```

### 5.5 CtpMdApi 查询

#### query_contract() - 查询合约

```python
def query_contract(self):
    """查询合约"""
    if not self.login_status:
        return

    req = {
        "BrokerID": self.brokerid,
        "InvestorID": self.userid,
    }

    self.reqid += 1
    self.api.ReqQryInstrument(req, self.reqid)
```

#### onRspQryInstrument() - 合约响应

```python
def onRspQryInstrument(self, data: dict, error: dict, reqid: int, last: bool):
    """合约响应"""
    if error["ErrorID"] != 0:
        return

    # 转换交易所
    exchange = EXCHANGE_CTP2VT.get(
        data["ExchangeID"],
        Exchange.SSE
    )

    # 创建合约对象
    contract = ContractData(
        symbol=data["InstrumentID"],
        exchange=exchange,
        name=data["InstrumentName"],
        product=PRODUCT_CTP2VT.get(
            data["ProductClass"],
            Product.EQUITY
        ),
        size=data["VolumeMultiple"],
        pricetick=data["PriceTick"],
        gateway_name=self.gateway_name
    )

    # 添加到合约缓存
    self.gateway.on_contract(contract)
```

---

## 6. 连接流程

### 6.1 完整连接流程

```
1. MainEngine.connect()
   ↓
2. CtpGateway.connect()
   ↓
3. CtpTdApi.connect()         # 连接交易服务器
   ↓
4. CtpTdApi.onFrontConnected()
   ↓
5. CtpTdApi.ReqAuthenticate()  # 认证
   ↓
6. CtpTdApi.onRspAuthenticate()
   ↓
7. CtpTdApi.ReqUserLogin()     # 登录
   ↓
8. CtpTdApi.onRspUserLogin()
   ↓
9. CtpTdApi.ReqSettlementInfoConfirm()  # 确认结算单
   ↓
10. CtpMdApi.connect()         # 连接行情服务器
    ↓
11. CtpMdApi.onFrontConnected()
    ↓
12. CtpMdApi.ReqUserLogin()    # 登录
    ↓
13. CtpMdApi.onRspUserLogin()
    ↓
14. CtpTdApi.query_contract()  # 查询合约
15. CtpMdApi.query_contract()  # 查询合约
    ↓
16. 连接完成 ✅
```

### 6.2 连接时间分析

| 步骤 | 耗时 | 说明 |
|------|------|------|
| 连接交易服务器 | 0.5-1秒 | TCP 连接 |
| 认证 | 0.1-0.3秒 | API 调用 |
| 登录 | 0.2-0.5秒 | API 调用 |
| 确认结算单 | 0.1-0.2秒 | API 调用 |
| 查询合约 | 2-3秒 | 大量数据 |
| 连接行情服务器 | 0.5-1秒 | TCP 连接 |
| 行情登录 | 0.2-0.5秒 | API 调用 |
| **总计** | **3-6秒** |  |

---

## 7. 自动查询机制

### 7.1 自动查询原理

**CTP 网关有定时查询机制**，每 2 秒自动查询账户和持仓:

```python
def init_query(self):
    """初始化查询任务"""
    self.query_functions: list = [
        self.td_api.query_account,
        self.td_api.query_position,
    ]
    self.event_engine.register(EVENT_TIMER, self.process_timer_event)

def process_timer_event(self, event: Event):
    """定时事件处理"""
    self.count += 1
    if self.count < 2:
        return
    self.count = 0

    # 循环执行查询
    func = self.query_functions.pop(0)
    func()
    self.query_functions.append(func)
```

### 7.2 查询频率

| 查询类型 | 频率 | 延迟 |
|---------|------|------|
| 账户查询 | 每 2 秒 | <1 秒 |
| 持仓查询 | 每 2 秒 | <1 秒 |

### 7.3 性能优化

**关键原则**: 不要手动查询，直接从缓存获取

```python
# ❌ 错误: 每次都手动查询（慢）
gateway.query_account()
time.sleep(5)
account = oms_engine.get_all_accounts()[0]

# ✅ 正确: 直接从缓存获取（快）
account = oms_engine.get_all_accounts()[0]
```

**优化效果**: 从 4.92 秒优化到 0.00 秒

---

## 8. 数据转换

### 8.1 方向转换

```python
# VnPy -> CTP
DIRECTION_VT2CTP = {
    Direction.LONG: THOST_FTDC_D_Buy,
    Direction.SHORT: THOST_FTDC_D_Sell,
}

# CTP -> VnPy
DIRECTION_CTP2VT = {
    THOST_FTDC_D_Buy: Direction.LONG,
    THOST_FTDC_D_Sell: Direction.SHORT,
}
```

### 8.2 开平转换

```python
# VnPy -> CTP
OFFSET_VT2CTP = {
    Offset.OPEN: THOST_FTDC_OF_Open,
    Offset.CLOSE: THOST_FTDC_OF_Close,
    Offset.CLOSETODAY: THOST_FTDC_OF_CloseToday,
    Offset.CLOSEYESTERDAY: THOST_FTDC_OF_CloseYesterday,
}

# CTP -> VnPy
OFFSET_CTP2VT = {
    THOST_FTDC_OF_Open: Offset.OPEN,
    THOST_FTDC_OF_Close: Offset.CLOSE,
    THOST_FTDC_OF_CloseToday: Offset.CLOSETODAY,
    THOST_FTDC_OF_CloseYesterday: Offset.CLOSEYESTERDAY,
}
```

### 8.3 订单类型转换

```python
# VnPy -> CTP
ORDERTYPE_VT2CTP = {
    OrderType.LIMIT: THOST_FTDC_OPT_LimitPrice,
    OrderType.MARKET: THOST_FTDC_OPT_AnyPrice,
    OrderType.STOP: THOST_FTDC_OPT_LimitPrice,
}

# CTP -> VnPy
ORDERTYPE_CTP2VT = {
    THOST_FTDC_OPT_LimitPrice: OrderType.LIMIT,
    THOST_FTDC_OPT_AnyPrice: OrderType.MARKET,
}
```

### 8.4 状态转换

```python
# CTP -> VnPy
STATUS_CTP2VT = {
    THOST_FTDC_OST_NoTradeQueueing: Status.NOTTRADED,
    THOST_FTDC_OST_PartTradedQueueing: Status.PARTTRADED,
    THOST_FTDC_OST_AllTraded: Status.ALLTRADED,
    THOST_FTDC_OST_Canceled: Status.CANCELLED,
}
```

### 8.5 交易所转换

```python
# CTP -> VnPy
EXCHANGE_CTP2VT = {
    "SSE": Exchange.SSE,
    "SZSE": Exchange.SZSE,
    "CFFEX": Exchange.CFFEX,
    "SHFE": Exchange.SHFE,
    "DCE": Exchange.DCE,
    "CZCE": Exchange.CZCE,
    "INE": Exchange.INE,
}
```

---

## 9. 事件发布

### 9.1 订单事件

```python
def on_order(self, order: OrderData):
    """订单事件"""
    # 添加到订单映射
    self.orders[order.orderid] = order

    # 发布订单事件
    event = Event(EVENT_ORDER, order)
    self.event_engine.put(event)
```

### 9.2 成交事件

```python
def on_trade(self, trade: TradeData):
    """成交事件"""
    # 查找订单
    order = self.orders.get(trade.orderid)
    if order:
        order.traded += trade.volume

    # 发布成交事件
    event = Event(EVENT_TRADE, trade)
    self.event_engine.put(event)
```

### 9.3 账户事件

```python
def on_account(self, account: AccountData):
    """账户事件"""
    # 发布账户事件
    event = Event(EVENT_ACCOUNT, account)
    self.event_engine.put(event)
```

### 9.4 持仓事件

```python
def on_position(self, position: PositionData):
    """持仓事件"""
    # 发布持仓事件
    event = Event(EVENT_POSITION, position)
    self.event_engine.put(event)
```

### 9.5 行情事件

```python
def on_tick(self, tick: TickData):
    """行情事件"""
    # 发布行情事件
    event = Event(EVENT_TICK, tick)
    self.event_engine.put(event)
```

### 9.6 合约事件

```python
def on_contract(self, contract: ContractData):
    """合约事件"""
    # 添加到合约缓存
    self.contracts[contract.symbol] = contract

    # 发布合约事件
    event = Event(EVENT_CONTRACT, contract)
    self.event_engine.put(event)
```

---

## 10. 故障排查

### 10.1 连接失败

**问题**: 连接超时

**检查**:
```python
# 1. 检查网络
ping trading.openctp.cn
telnet trading.openctp.cn 30001

# 2. 检查配置
gateway_setting = {
    "交易服务器": "tcp://trading.openctp.cn:30001",
    "行情服务器": "tcp://trading.openctp.cn:30011",
}
```

**解决**:
- 确保网络通畅
- 确认服务器地址正确
- 检查防火墙设置

### 10.2 登录失败

**问题**: 登录失败

**检查**:
```python
# 1. 检查账号密码
gateway_setting = {
    "用户名": "17130",
    "密码": "123456",
}

# 2. 检查经纪商代码
gateway_setting = {
    "经纪商代码": "9999",
}
```

**解决**:
- 确认账号密码正确
- 确认经纪商代码正确

### 10.3 订单失败

**问题**: 订单插入失败

**检查**:
```python
# 1. 检查合约
contract = oms_engine.get_contract("IF2602")
if not contract:
    print("合约不存在")

# 2. 检查价格
order = OrderRequest(
    price=4000.0,  # 必须在涨跌停范围内
)
```

**解决**:
- 确认合约存在
- 确认价格在涨跌停范围内
- 检查账户资金充足

### 10.4 行情未收到

**问题**: 订阅后未收到行情

**检查**:
```python
# 1. 检查订阅
main_engine.subscribe(req, "CTP")

# 2. 检查合约
contract = oms_engine.get_contract("IF2602")
if not contract:
    print("合约不存在")

# 3. 检查事件监听
event_engine.register(EVENT_TICK, on_tick)
```

**解决**:
- 确认已订阅行情
- 确认合约存在
- 确认事件监听器已注册

---

## 附录

### A. 完整连接示例

```python
from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy_ctp.gateway import CtpGateway
import time

# 创建引擎
event_engine = EventEngine()
main_engine = MainEngine(event_engine)
main_engine.add_gateway(CtpGateway, gateway_name="CTP")

# 连接
gateway_setting = {
    "用户名": "17130",
    "密码": "123456",
    "经纪商代码": "9999",
    "交易服务器": "tcp://trading.openctp.cn:30001",
    "行情服务器": "tcp://trading.openctp.cn:30011",
    "产品名称": "",
    "授权编码": "",
    "柜台环境": "测试"
}

main_engine.connect(gateway_setting, "CTP")
time.sleep(5)

print("连接完成")
```

### B. 资源链接

- **CTP 文档**: http://www.sfit.com.cn
- **SimNow**: http://www.simnow.com.cn
- **OpenCTP**: http://openctp.cn

---

**文档结束**
