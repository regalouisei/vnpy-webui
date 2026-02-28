# vn.py 期权交易系统深度解析

**版本**: vn.py 3.x
**文档版本**: 1.0
**更新时间**: 2026-02-20
**作者**: Quant Factory

---

## 目录

1. [期权交易基础](#1-期权交易基础)
2. [vn.py 期权架构概述](#2-vnpy-期权架构概述)
3. [期权合约管理](#3-期权合约管理)
4. [期权定价模型](#4-期权定价模型)
5. [期权策略体系](#5-期权策略体系)
6. [希腊字母应用](#6-希腊字母应用)
7. [风险管理与对冲](#7-风险管理与对冲)
8. [最佳实践](#8-最佳实践)
9. [配置示例](#9-配置示例)

---

## 1. 期权交易基础

### 1.1 期权基本概念

期权是一种衍生金融工具，赋予持有者在特定日期或之前以约定价格买入或卖出标的资产的权利，而非义务。

**期权类型：**
- **看涨期权（Call Option）**：赋予买入权
- **看跌期权（Put Option）**：赋予卖出权

**关键要素：**
- **标的资产**：期权对应的股票、指数、期货等
- **执行价格（行权价）**：约定的交易价格
- **到期日**：期权失效日期
- **权利金**：期权价格

**美式期权 vs 欧式期权：**
- 美式期权：到期日前任何时间都可行权
- 欧式期权：只能在到期日行权

### 1.2 应用场景

**1. 投机交易**
- 方向性押注：预测标的资产上涨或下跌
- 波动率交易：押注波动率的变化
- 事件交易：财报发布、重大政策等

**2. 风险对冲**
- 保护性看跌期权：保护多头持仓
- 备兑看涨期权：增强收益
- 领口策略：限制风险和收益

**3. 套利交易**
- 价差套利：利用价格不合理偏离
- 波动率套利：不同期限波动率差异
- 跨市场套利：现货-期权价差

**4. 收益增强**
- 出售期权获取权利金
- 时间价值利用
- 隐含波动率捕获

---

## 2. vn.py 期权架构概述

### 2.1 系统架构

vn.py 期权交易系统基于通用交易引擎框架，在 CTA 策略引擎基础上扩展期权特定功能。

```
┌─────────────────────────────────────────────┐
│          MainEngine（主引擎）                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Gateway  │  │  Database│  │ Datafeed │  │
│  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│      OptionEngine（期权引擎）                │
│  ┌──────────────┐  ┌──────────────┐        │
│  │ OptionAlgo  │  │OptionHedging│        │
│  │   算法交易   │  │   对冲管理    │        │
│  └──────────────┘  └──────────────┘        │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│    OptionTemplate（期权策略模板）             │
│  ┌──────────────┐  ┌──────────────┐        │
│  │ Greeks计算   │  │  策略逻辑    │        │
│  │  合约管理    │  │  订单执行    │        │
│  └──────────────┘  └──────────────┘        │
└─────────────────────────────────────────────┘
```

### 2.2 核心组件

**1. OptionTemplate 策略基类**

```python
class OptionTemplate(BaseTemplate):
    """期权策略基类"""

    # 期权特定参数
    option_symbol: str = ""          # 期权合约代码
    underlying_symbol: str = ""      # 标的资产代码
    option_type: OptionType = None   # 期权类型
    strike_price: float = 0.0        # 执行价格
    expiry_date: date = None         # 到期日

    # 希腊字母
    delta: float = 0.0               # Delta值
    gamma: float = 0.0               # Gamma值
    theta: float = 0.0               # Theta值
    vega: float = 0.0                # Vega值
    rho: float = 0.0                 # Rho值

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 初始化希腊字母计算器
        self.greeks_calculator = GreeksCalculator()

        # 初始化定价模型
        self.pricing_model = BlackScholesModel()
```

**2. GreeksCalculator 希腊字母计算器**

```python
class GreeksCalculator:
    """希腊字母计算器"""

    def calculate_greeks(
        self,
        spot_price: float,
        strike_price: float,
        time_to_expiry: float,
        risk_free_rate: float,
        volatility: float,
        option_type: OptionType
    ) -> dict:
        """计算所有希腊字母"""
        # 使用 Black-Scholes 公式计算
        d1 = self._calculate_d1(spot_price, strike_price,
                               time_to_expiry, risk_free_rate, volatility)
        d2 = d1 - volatility * np.sqrt(time_to_expiry)

        # Delta
        delta = self._calculate_delta(d1, option_type)

        # Gamma
        gamma = self._calculate_gamma(d1, spot_price,
                                      volatility, time_to_expiry)

        # Theta
        theta = self._calculate_theta(d1, d2, spot_price, strike_price,
                                     time_to_expiry, risk_free_rate,
                                     volatility, option_type)

        # Vega
        vega = self._calculate_vega(d1, spot_price, time_to_expiry)

        # Rho
        rho = self._calculate_rho(d2, strike_price, time_to_expiry,
                                 risk_free_rate, option_type)

        return {
            "delta": delta,
            "gamma": gamma,
            "theta": theta,
            "vega": vega,
            "rho": rho
        }
```

**3. 事件驱动机制**

vn.py 期权系统使用统一的事件引擎处理期权交易事件：

- `EVENT_TICK`：标的资产行情更新
- `EVENT_OPTION_TICK`：期权合约行情更新
- `EVENT_ORDER`：订单状态更新
- `EVENT_TRADE`：成交回报
- `EVENT_POSITION`：持仓变化
- `EVENT_GREEKS_UPDATE`：希腊字母更新事件

---

## 3. 期权合约管理

### 3.1 合约查询

```python
def query_option_contracts(
    self,
    underlying_symbol: str,
    expiry_date: date = None,
    option_type: OptionType = None
) -> list[OptionContract]:
    """查询期权合约"""
    contracts = []

    # 从数据库查询期权合约
    all_contracts = self.database.query_all_option_contracts()

    # 过滤条件
    for contract in all_contracts:
        if contract.underlying_symbol != underlying_symbol:
            continue

        if expiry_date and contract.expiry_date != expiry_date:
            continue

        if option_type and contract.option_type != option_type:
            continue

        contracts.append(contract)

    return contracts
```

### 3.2 合约数据结构

```python
@dataclass
class OptionContract:
    """期权合约数据类"""

    # 基本信息
    symbol: str                    # 合约代码
    underlying_symbol: str         # 标的代码
    option_type: OptionType       # 期权类型（看涨/看跌）
    strike_price: float           # 执行价格
    expiry_date: date             # 到期日

    # 交易信息
    multiplier: float              # 合约乘数
    min_volume: int               # 最小下单量
    pricetick: float             # 最小价格变动
    trading_hours: dict           # 交易时段

    # 希腊字母（实时更新）
    delta: float = 0.0
    gamma: float = 0.0
    theta: float = 0.0
    vega: float = 0.0
    rho: float = 0.0

    # 隐含波动率
    implied_volatility: float = 0.0
```

### 3.3 合约筛选策略

```python
class ContractSelector:
    """合约选择器"""

    def select_best_contract(
        self,
        underlying_symbol: str,
        target_days: int = 30,
        delta_target: float = 0.5,
        option_type: OptionType = OptionType.CALL
    ) -> OptionContract:
        """选择最佳期权合约"""

        # 1. 查询所有期权合约
        all_contracts = self.query_option_contracts(underlying_symbol)

        # 2. 筛选到期日
        target_expiry = datetime.now() + timedelta(days=target_days)
        expiry_filtered = [
            c for c in all_contracts
            if abs((c.expiry_date - target_expiry).days) <= 7
        ]

        # 3. 计算每个合约的 Delta
        for contract in expiry_filtered:
            contract.delta = self._calculate_delta(
                underlying_symbol,
                contract.strike_price,
                contract.expiry_date
            )

        # 4. 选择最接近目标 Delta 的合约
        best_contract = min(
            expiry_filtered,
            key=lambda c: abs(c.delta - delta_target)
        )

        return best_contract
```

---

## 4. 期权定价模型

### 4.1 Black-Scholes 模型

Black-Scholes 模型是最常用的期权定价模型，适用于欧式期权。

**核心公式：**

对于看涨期权：
```
C = S * N(d1) - K * e^(-rT) * N(d2)
```

对于看跌期权：
```
P = K * e^(-rT) * N(-d2) - S * N(-d1)
```

其中：
```
d1 = [ln(S/K) + (r + σ²/2) * T] / (σ * √T)
d2 = d1 - σ * √T
```

参数说明：
- S = 标的资产当前价格
- K = 执行价格
- r = 无风险利率
- σ = 波动率
- T = 到期时间（年）
- N(x) = 标准正态分布累积分布函数

### 4.2 vn.py 实现

```python
class BlackScholesModel:
    """Black-Scholes 定价模型"""

    def __init__(self):
        self.norm_dist = norm()

    def calculate_price(
        self,
        spot_price: float,
        strike_price: float,
        time_to_expiry: float,
        risk_free_rate: float,
        volatility: float,
        option_type: OptionType
    ) -> float:
        """计算期权价格"""

        # 计算 d1 和 d2
        d1 = self._calculate_d1(
            spot_price, strike_price,
            time_to_expiry, risk_free_rate, volatility
        )
        d2 = d1 - volatility * np.sqrt(time_to_expiry)

        # 计算 N(d1) 和 N(d2)
        nd1 = self.norm_dist.cdf(d1)
        nd2 = self.norm_dist.cdf(d2)
        nnd1 = self.norm_dist.cdf(-d1)
        nnd2 = self.norm_dist.cdf(-d2)

        # 计算期权价格
        if option_type == OptionType.CALL:
            price = (
                spot_price * nd1 -
                strike_price * np.exp(-risk_free_rate * time_to_expiry) * nd2
            )
        else:
            price = (
                strike_price * np.exp(-risk_free_rate * time_to_expiry) * nnd2 -
                spot_price * nnd1
            )

        return max(price, 0.0)  # 期权价格不能为负

    def _calculate_d1(
        self,
        spot_price: float,
        strike_price: float,
        time_to_expiry: float,
        risk_free_rate: float,
        volatility: float
    ) -> float:
        """计算 d1 参数"""
        return (
            np.log(spot_price / strike_price) +
            (risk_free_rate + volatility ** 2 / 2) * time_to_expiry
        ) / (volatility * np.sqrt(time_to_expiry))
```

### 4.3 隐含波动率计算

隐含波动率（IV）是通过期权市场价格反推的波动率。

```python
def calculate_implied_volatility(
    self,
    market_price: float,
    spot_price: float,
    strike_price: float,
    time_to_expiry: float,
    risk_free_rate: float,
    option_type: OptionType,
    initial_guess: float = 0.2,
    max_iterations: int = 100,
    tolerance: float = 1e-6
) -> float:
    """使用牛顿法计算隐含波动率"""

    volatility = initial_guess

    for _ in range(max_iterations):
        # 计算模型价格
        model_price = self.calculate_price(
            spot_price, strike_price, time_to_expiry,
            risk_free_rate, volatility, option_type
        )

        # 计算价格差异
        price_diff = model_price - market_price

        # 如果差异足够小，返回结果
        if abs(price_diff) < tolerance:
            return volatility

        # 计算 Vega（期权价格对波动率的偏导数）
        vega = self._calculate_vega(
            spot_price, strike_price,
            time_to_expiry, volatility
        )

        # 避免除以零
        if vega < tolerance:
            break

        # 牛顿法更新波动率
        volatility = volatility - price_diff / vega

        # 确保波动率为正
        volatility = max(volatility, 0.001)

    return volatility
```

---

## 5. 期权策略体系

### 5.1 单腿策略

**1. 买入看涨期权（Long Call）**

```python
class LongCallStrategy(OptionTemplate):
    """买入看涨期权策略"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_profit: float = float('inf')
        self.max_loss: float = self.fixed_size * self.entry_price
        self.break_even: float = self.strike_price + self.entry_price

    def generate_signal(self, spot_price: float) -> Signal:
        """生成交易信号"""
        if spot_price > self.break_even:
            return Signal.LONG
        elif spot_price < self.strike_price * 0.95:
            return Signal.EXIT
        else:
            return Signal.HOLD
```

**2. 买入看跌期权（Long Put）**

```python
class LongPutStrategy(OptionTemplate):
    """买入看跌期权策略"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_profit: float = self.strike_price * self.fixed_size
        self.max_loss: float = self.fixed_size * self.entry_price
        self.break_even: float = self.strike_price - self.entry_price

    def generate_signal(self, spot_price: float) -> Signal:
        """生成交易信号"""
        if spot_price < self.break_even:
            return Signal.SHORT
        elif spot_price > self.strike_price * 1.05:
            return Signal.EXIT
        else:
            return Signal.HOLD
```

### 5.2 价差策略

**1. 牛市价差（Bull Call Spread）**

```python
class BullCallSpread(OptionTemplate):
    """牛市看涨价差"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.low_strike: float = 0.0    # 低行权价（买入）
        self.high_strike: float = 0.0   # 高行权价（卖出）

    def create_spread(
        self,
        low_strike: float,
        high_strike: float,
        expiry_date: date
    ) -> None:
        """构建牛市价差"""
        # 买入低行权价看涨期权
        long_call = self.query_option_contracts(
            self.underlying_symbol,
            expiry_date,
            OptionType.CALL
        )
        self.long_call_contract = [
            c for c in long_call if c.strike_price == low_strike
        ][0]

        # 卖出高行权价看涨期权
        short_call = self.query_option_contracts(
            self.underlying_symbol,
            expiry_date,
            OptionType.CALL
        )
        self.short_call_contract = [
            c for c in short_call if c.strike_price == high_strike
        ][0]

        # 计算盈亏平衡点
        net_debit = (
            self.long_call_contract.last_price -
            self.short_call_contract.last_price
        )
        self.break_even = low_strike + net_debit

        self.max_profit = (
            high_strike - low_strike - net_debit
        ) * self.fixed_size
        self.max_loss = net_debit * self.fixed_size
```

**2. 熊市价差（Bear Put Spread）**

```python
class BearPutSpread(OptionTemplate):
    """熊市看跌价差"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.high_strike: float = 0.0   # 高行权价（买入）
        self.low_strike: float = 0.0    # 低行权价（卖出）

    def create_spread(
        self,
        high_strike: float,
        low_strike: float,
        expiry_date: date
    ) -> None:
        """构建熊市价差"""
        # 买入高行权价看跌期权
        long_put = self.query_option_contracts(
            self.underlying_symbol,
            expiry_date,
            OptionType.PUT
        )
        self.long_put_contract = [
            c for c in long_put if c.strike_price == high_strike
        ][0]

        # 卖出低行权价看跌期权
        short_put = self.query_option_contracts(
            self.underlying_symbol,
            expiry_date,
            OptionType.PUT
        )
        self.short_put_contract = [
            c for c in short_put if c.strike_price == low_strike
        ][0]

        # 计算盈亏平衡点
        net_debit = (
            self.long_put_contract.last_price -
            self.short_put_contract.last_price
        )
        self.break_even = high_strike - net_debit

        self.max_profit = (
            high_strike - low_strike - net_debit
        ) * self.fixed_size
        self.max_loss = net_debit * self.fixed_size
```

**3. 跨式策略（Straddle）**

```python
class StraddleStrategy(OptionTemplate):
    """跨式策略（买入看涨+看跌）"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.strike: float = 0.0
        self.call_contract: OptionContract = None
        self.put_contract: OptionContract = None

    def create_straddle(
        self,
        strike: float,
        expiry_date: date
    ) -> None:
        """构建跨式策略"""
        # 查询看涨期权
        calls = self.query_option_contracts(
            self.underlying_symbol,
            expiry_date,
            OptionType.CALL
        )
        self.call_contract = [
            c for c in calls if c.strike_price == strike
        ][0]

        # 查询看跌期权
        puts = self.query_option_contracts(
            self.underlying_symbol,
            expiry_date,
            OptionType.PUT
        )
        self.put_contract = [
            c for c in puts if c.strike_price == strike
        ][0]

        # 计算盈亏平衡点
        total_premium = (
            self.call_contract.last_price +
            self.put_contract.last_price
        )
        self.upper_break_even = strike + total_premium
        self.lower_break_even = strike - total_premium

        self.max_loss = total_premium * self.fixed_size
        self.max_profit = float('inf')
```

---

## 6. 希腊字母应用

### 6.1 Delta（Δ）

**定义**：期权价格对标的资产价格的敏感度

**含义**：
- Delta ∈ [0, 1] 表示看涨期权
- Delta ∈ [-1, 0] 表示看跌期权
- Delta ≈ 0.5 表示平值看涨期权

**应用场景**：

```python
def delta_hedging(self, spot_price: float) -> None:
    """Delta 对冲策略"""
    # 1. 计算当前组合 Delta
    portfolio_delta = self.calculate_portfolio_delta(spot_price)

    # 2. 计算需要对冲的数量
    hedge_ratio = -portfolio_delta * self.position_size

    # 3. 执行对冲交易
    if hedge_ratio > 0:
        # 需要买入标的资产
        self.buy(self.underlying_symbol, abs(hedge_ratio))
    elif hedge_ratio < 0:
        # 需要卖出标的资产
        self.sell(self.underlying_symbol, abs(hedge_ratio))
```

### 6.2 Gamma（Γ）

**定义**：Delta 对标的资产价格变化的敏感度

**含义**：
- Gamma 越大，Delta 变化越快
- 平值期权 Gamma 最大
- 到期临近时 Gamma 增加

**应用场景**：

```python
def gamma_scalping(self, spot_price: float) -> None:
    """Gamma 剥头皮策略"""
    # 1. 维持 Delta 中性
    current_delta = self.calculate_portfolio_delta(spot_price)

    # 2. 当 Delta 偏离阈值时对冲
    if abs(current_delta) > self.delta_threshold:
        hedge_quantity = -current_delta * self.position_size

        # 3. 执行对冲，并记录对冲价格
        if hedge_quantity > 0:
            self.buy(self.underlying_symbol, abs(hedge_quantity))
        elif hedge_quantity < 0:
            self.sell(self.underlying_symbol, abs(hedge_quantity))
```

### 6.3 Theta（Θ）

**定义**：期权价格对时间流逝的敏感度

**含义**：
- Theta 通常为负（时间价值衰减）
- 平值期权 Theta 衰减最快
- 距离到期越近，Theta 衰减越快

**应用场景**：

```python
def theta_positive_strategy(self) -> None:
    """Theta 正收益策略（卖出期权）"""
    # 1. 选择高 Theta 的期权
    short_dte_options = self.query_short_dte_options(min_dte=7, max_dte=30)

    # 2. 计算 Theta 收益
    for option in short_dte_options:
        theta_income = option.theta * self.fixed_size

        # 3. 如果 Theta 收益满足条件，构建策略
        if theta_income > self.min_theta_income:
            self.sell_option(option.symbol, self.fixed_size)
```

### 6.4 Vega（ν）

**定义**：期权价格对波动率变化的敏感度

**含义**：
- Vega > 0 表示从波动率上升中受益
- 平值期权 Vega 最大
- 到期时间越长，Vega 越大

**应用场景**：

```python
def volatility_trading(self, implied_vol: float, realized_vol: float) -> None:
    """波动率交易策略"""
    # 1. 判断波动率水平
    vol_premium = implied_vol - realized_vol

    # 2. 如果隐含波动率过高，做空波动率
    if vol_premium > self.vol_threshold:
        # 选择平值期权
        atm_option = self.query_atm_option()

        # 卖出跨式策略
        self.sell_option(atm_option.call_symbol, self.fixed_size)
        self.sell_option(atm_option.put_symbol, self.fixed_size)

    # 3. 如果隐含波动率过低，做多波动率
    elif vol_premium < -self.vol_threshold:
        # 选择平值期权
        atm_option = self.query_atm_option()

        # 买入跨式策略
        self.buy_option(atm_option.call_symbol, self.fixed_size)
        self.buy_option(atm_option.put_symbol, self.fixed_size)
```

---

## 7. 风险管理与对冲

### 7.1 Delta 对冲

```python
class DeltaHedger:
    """Delta 对冲器"""

    def __init__(self, option_engine):
        self.option_engine = option_engine
        self.hedge_frequency: int = 60  # 对冲频率（秒）
        self.last_hedge_time: datetime = None

    def check_and_hedge(self, spot_price: float) -> None:
        """检查并执行 Delta 对冲"""
        current_time = datetime.now()

        # 检查是否到达对冲时间
        if (self.last_hedge_time and
            (current_time - self.last_hedge_time).seconds < self.hedge_frequency):
            return

        # 计算当前 Delta
        portfolio_delta = self.calculate_portfolio_delta(spot_price)

        # Delta 中性阈值
        if abs(portfolio_delta) > self.delta_threshold:
            self.execute_hedge(spot_price, portfolio_delta)
            self.last_hedge_time = current_time

    def calculate_portfolio_delta(self, spot_price: float) -> float:
        """计算组合 Delta"""
        total_delta = 0.0

        # 遍历所有期权持仓
        for position in self.option_engine.positions.values():
            option = self.option_engine.get_option_contract(position.symbol)
            delta = self.option_engine.greeks_calculator.calculate_delta(
                spot_price, option.strike_price,
                option.time_to_expiry, option.volatility,
                option.option_type
            )
            total_delta += delta * position.volume

        return total_delta
```

### 7.2 Gamma 限制

```python
def check_gamma_limit(self) -> bool:
    """检查 Gamma 风险"""
    total_gamma = 0.0

    for position in self.positions.values():
        option = self.get_option_contract(position.symbol)
        gamma = self.greeks_calculator.calculate_gamma(
            option.spot_price, option.strike_price,
            option.time_to_expiry, option.volatility
        )
        total_gamma += gamma * position.volume

    # Gamma 风险检查
    if abs(total_gamma) > self.max_gamma:
        self.write_log(f"Gamma 风险超限: {total_gamma:.4f}")
        return False

    return True
```

### 7.3 Vega 风险控制

```python
def check_vega_exposure(self) -> bool:
    """检查 Vega 暴露"""
    total_vega = 0.0

    for position in self.positions.values():
        option = self.get_option_contract(position.symbol)
        vega = self.greeks_calculator.calculate_vega(
            option.spot_price, option.strike_price,
            option.time_to_expiry, option.volatility
        )
        total_vega += vega * position.volume

    # Vega 暴露检查
    if abs(total_vega) > self.max_vega:
        self.write_log(f"Vega 暴露超限: {total_vega:.4f}")
        return False

    return True
```

### 7.4 仓位管理

```python
def check_position_limit(self, option_symbol: str, volume: float) -> bool:
    """检查仓位限制"""
    # 1. 单个合约限制
    current_position = self.positions.get(option_symbol, 0)
    if abs(current_position + volume) > self.max_single_position:
        self.write_log(f"单合约仓位超限: {option_symbol}")
        return False

    # 2. 总体 Delta 限制
    total_delta = self.calculate_total_delta()
    if abs(total_delta) > self.max_portfolio_delta:
        self.write_log(f"组合 Delta 超限: {total_delta:.2f}")
        return False

    # 3. 资金使用率
    margin_required = self.calculate_margin_requirement(option_symbol, volume)
    if margin_required > self.available_margin:
        self.write_log("保证金不足")
        return False

    return True
```

---

## 8. 最佳实践

### 8.1 策略开发规范

**1. 明确策略目标**

```python
class MyOptionStrategy(OptionTemplate):
    """策略文档说明"""

    strategy_name: str = "Delta对冲策略"
    strategy_description: str = """
    策略目标：通过 Delta 中性对冲降低方向性风险
    适用市场：波动率较高的期权市场
    风险等级：中等
    预期收益：年化 10-15%
    最大回撤：控制在 20% 以内
    """
```

**2. 参数管理**

```python
class MyOptionStrategy(OptionTemplate):
    """参数管理最佳实践"""

    # 策略参数（可配置）
    hedge_frequency: int = 300       # 对冲频率（秒）
    delta_threshold: float = 0.1     # Delta 对冲阈值
    max_gamma: float = 0.05         # 最大 Gamma
    max_vega: float = 0.5            # 最大 Vega
    max_position: int = 100          # 最大持仓量

    # 风险参数
    max_loss_per_trade: float = 0.02 # 单笔最大亏损比例
    max_daily_loss: float = 0.05     # 每日最大亏损比例

    parameters = [
        "hedge_frequency",
        "delta_threshold",
        "max_gamma",
        "max_vega",
        "max_position"
    ]
```

**3. 错误处理**

```python
def on_tick(self, tick: TickData) -> None:
    """Tick 回调 - 带异常处理"""
    try:
        # 1. 更新数据
        self.update_market_data(tick)

        # 2. 检查风险限制
        if not self.check_risk_limits():
            return

        # 3. 执行策略逻辑
        self.execute_strategy()

    except Exception as e:
        self.write_log(f"策略异常: {str(e)}")
        self.write_log(traceback.format_exc())

        # 记录异常
        self.log_exception(e)

        # 必要时停止策略
        if self.is_critical_error(e):
            self.stop_strategy()
```

### 8.2 监控与日志

```python
class OptionMonitor:
    """期权策略监控器"""

    def __init__(self, strategy: OptionTemplate):
        self.strategy = strategy

    def log_greeks(self) -> None:
        """记录希腊字母"""
        greeks = self.strategy.get_current_greeks()

        self.strategy.write_log(
            f"Greeks更新 - "
            f"Delta:{greeks['delta']:.4f} "
            f"Gamma:{greeks['gamma']:.4f} "
            f"Theta:{greeks['theta']:.4f} "
            f"Vega:{greeks['vega']:.4f}"
        )

    def log_pnl(self) -> None:
        """记录盈亏"""
        total_pnl = self.strategy.calculate_total_pnl()

        self.strategy.write_log(
            f"盈亏更新 - "
            f"总盈亏:{total_pnl:.2f} "
            f"已实现:{self.strategy.realized_pnl:.2f} "
            f"未实现:{self.strategy.unrealized_pnl:.2f}"
        )
```

### 8.3 性能优化

```python
def optimize_greeks_calculation(self) -> None:
    """优化希腊字母计算"""

    # 1. 批量计算而非逐个计算
    if self.need_update_greeks:
        all_contracts = self.get_all_contracts()
        greeks_batch = self.greeks_calculator.calculate_batch(all_contracts)

        # 2. 更新所有合约
        for contract, greeks in zip(all_contracts, greeks_batch):
            contract.delta = greeks['delta']
            contract.gamma = greeks['gamma']
            contract.theta = greeks['theta']
            contract.vega = greeks['vega']

        self.need_update_greeks = False

    # 3. 使用缓存
    @lru_cache(maxsize=1000)
    def get_cached_greeks(self, contract_id: str) -> dict:
        """获取缓存的希腊字母"""
        contract = self.get_contract(contract_id)
        return {
            'delta': contract.delta,
            'gamma': contract.gamma,
            'theta': contract.theta,
            'vega': contract.vega
        }
```

---

## 9. 配置示例

### 9.1 策略配置文件

**config_vt_setting.json**（交易配置）

```json
{
  "gateway_name": "IB",
  "gateway_module": "vnpy_ib",
  "gateway_setting": {
    "TWS_HOST": "127.0.0.1",
    "TWS_PORT": 7497,
    "clientId": 1
  }
}
```

**option_strategy_setting.json**（策略配置）

```json
{
  "strategies": [
    {
      "class_name": "DeltaHedgingStrategy",
      "strategy_name": "DeltaHedging_1",
      "vt_symbol": "AAPL",
      "setting": {
        "underlying_symbol": "AAPL",
        "option_type": "CALL",
        "strike_price": 150.0,
        "expiry_date": "2026-03-20",
        "fixed_size": 10,
        "hedge_frequency": 300,
        "delta_threshold": 0.1,
        "max_gamma": 0.05,
        "max_vega": 0.5,
        "max_position": 100,
        "max_loss_per_trade": 0.02,
        "max_daily_loss": 0.05
      }
    }
  ]
}
```

### 9.2 完整配置示例

**main_option_trading.py**（启动脚本）

```python
from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.ui import MainWindow, create_qapp

from vnpy_ib import IbGateway
from vnpy_optionmaster import OptionEngine, OptionTemplate
from vnpy_optionmaster.strategies import DeltaHedgingStrategy


def main():
    """启动期权交易系统"""

    # 1. 创建事件引擎
    event_engine = EventEngine()

    # 2. 创建主引擎
    main_engine = MainEngine(event_engine)

    # 3. 添加网关
    main_engine.add_gateway(IbGateway)

    # 4. 创建期权引擎
    option_engine = OptionEngine(main_engine, event_engine)

    # 5. 加载策略配置
    option_engine.load_strategy_setting("option_strategy_setting.json")

    # 6. 初始化所有策略
    for strategy_name in option_engine.strategies:
        option_engine.init_strategy(strategy_name)

    # 7. 启动所有策略
    for strategy_name in option_engine.strategies:
        option_engine.start_strategy(strategy_name)

    # 8. 连接网关
    main_engine.connect("IB", setting={
        "TWS_HOST": "127.0.0.1",
        "TWS_PORT": 7497,
        "clientId": 1
    })

    # 9. 创建主窗口（可选）
    app = create_qapp()
    window = MainWindow(main_engine, event_engine)
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
```

### 9.3 简单策略配置示例

**simple_call_option_strategy.json**

```json
{
  "strategy_name": "SimpleCall_1",
  "class_name": "SimpleCallStrategy",
  "vt_symbol": "SPY",
  "setting": {
    "underlying_symbol": "SPY",
    "option_type": "CALL",
    "strike_price": 450.0,
    "expiry_date": "2026-04-17",
    "fixed_size": 5,
    "entry_price": 5.0,
    "stop_loss": 2.5,
    "take_profit": 10.0
  }
}
```

**对应的策略代码：**

```python
class SimpleCallStrategy(OptionTemplate):
    """简单看涨期权策略"""

    # 策略参数
    underlying_symbol: str = "SPY"
    option_type: OptionType = OptionType.CALL
    strike_price: float = 450.0
    expiry_date: date = None
    fixed_size: int = 5
    entry_price: float = 5.0
    stop_loss: float = 2.5
    take_profit: float = 10.0

    # 策略变量
    current_price: float = 0.0
    pnl: float = 0.0

    parameters = [
        "underlying_symbol",
        "option_type",
        "strike_price",
        "expiry_date",
        "fixed_size",
        "entry_price",
        "stop_loss",
        "take_profit"
    ]

    variables = ["current_price", "pnl"]

    def on_tick(self, tick: TickData) -> None:
        """Tick 回调"""
        self.current_price = tick.last_price
        self.pnl = (self.current_price - self.entry_price) * self.fixed_size

        # 止损
        if self.current_price <= self.stop_loss:
            self.write_log(f"触发止损，当前价格:{self.current_price}")
            self.close_position()

        # 止盈
        if self.current_price >= self.take_profit:
            self.write_log(f"触发止盈，当前价格:{self.current_price}")
            self.close_position()

        self.put_event()

    def close_position(self) -> None:
        """平仓"""
        if self.pos > 0:
            self.sell(self.current_price, abs(self.pos))
        elif self.pos < 0:
            self.cover(self.current_price, abs(self.pos))
```

---

## 总结

vn.py 期权交易系统提供了完整的期权交易框架，包括：

1. **完善的期权数据管理**：支持期权合约查询、行情订阅、希腊字母计算
2. **灵活的定价模型**：内置 Black-Scholes 模型，支持隐含波动率计算
3. **丰富的策略体系**：支持单腿策略、价差策略、组合策略等
4. **专业的风险管理**：Delta 对冲、Gamma 限制、Vega 控制
5. **规范的配置体系**：JSON 配置文件，支持策略热加载

通过合理运用这些功能，可以构建稳定、高效的期权交易系统。实际应用中，需要根据市场环境和策略目标，选择合适的期权策略和对冲方案。

---

**相关文档：**
- [风险管理指南](./RISK_MANAGEMENT_GUIDE.md)
- [CTA策略深度解析](./VNPY_CTA_STRATEGY_DEEP_DIVE.md)
- [vn.py 官方文档](https://www.vnpy.com/)
