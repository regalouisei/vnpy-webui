# vn.py AI 量化系统深度解析

**版本**: vn.py 3.x
**文档版本**: 1.0
**更新时间**: 2026-02-20
**作者**: Quant Factory

---

## 目录

1. [AI 量化策略的基本概念和应用](#1-ai-量化策略的基本概念和应用)
2. [vn.py AI 量化系统的架构概述](#2-vnpy-ai-量化系统的架构概述)
3. [Alpha 因子的计算和应用](#3-alpha-因子的计算和应用)
4. [机器学习模型的集成](#4-机器学习模型的集成)
5. [因子挖掘和筛选](#5-因子挖掘和筛选)
6. [策略回测和优化](#6-策略回测和优化)
7. [实盘部署注意事项](#7-实盘部署注意事项)
8. [最佳实践建议](#8-最佳实践建议)
9. [简单的因子示例](#9-简单的因子示例)

---

## 1. AI 量化策略的基本概念和应用

### 1.1 AI 量化策略的定义

AI 量化策略是指利用机器学习、深度学习等人工智能技术，从历史市场数据中发现规律并构建交易策略的方法。与传统基于技术指标的策略相比，AI 量化策略具有以下特点：

**核心特征：**

1. **数据驱动**: 从海量历史数据中自动学习规律，而非依赖人工经验
2. **非线性能力**: 能够捕捉市场中的非线性关系和复杂模式
3. **自适应性强**: 模型可以根据市场变化持续学习和优化
4. **因子丰富**: 可以融合成百上千个因子进行综合判断

**应用场景：**

- **趋势预测**: 预测未来一段时间内价格涨跌方向
- **波动率预测**: 预测市场波动率变化，优化仓位管理
- **因子挖掘**: 自动发现具有预测能力的 Alpha 因子
- **智能择时**: 优化入场和出场时机
- **风险控制**: 动态调整止损止盈水平

### 1.2 AI 量化 vs 传统量化

| 维度 | 传统量化 | AI 量化 |
|------|---------|---------|
| 模型构建 | 人工设定规则 | 自动学习模式 |
| 因子数量 | 通常 10-50 个 | 可达数百上千 |
| 复杂度 | 线性或简单非线性 | 深度神经网络 |
| 可解释性 | 高（逻辑清晰） | 低（黑盒模型） |
| 适应能力 | 较弱 | 强（持续学习） |
| 过拟合风险 | 中等 | 较高 |

---

## 2. vn.py AI 量化系统的架构概述

### 2.1 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                     数据层 (Data Layer)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ 行情数据 │  │ 历史数据 │  │ 基本面   │  │ 另类数据 │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
└───────┼────────────┼────────────┼────────────┼──────────┘
        │            │            │            │
        ▼            ▼            ▼            ▼
┌─────────────────────────────────────────────────────────────┐
│                    因子计算层 (Factor Layer)                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  因子引擎 (Factor Engine)                            │  │
│  │  - 技术因子 (MA, MACD, RSI, ATR, ...)               │  │
│  │  - 量价因子 (成交量, 换手率, 资金流向, ...)         │  │
│  │  - 统计因子 (动量, 反转, 均值回归, ...)            │  │
│  │  - 自定义因子 (行业, 主题, 事件, ...)              │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                  机器学习层 (ML Layer)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ 特征工程     │  │ 模型训练     │  │ 模型预测     │      │
│  │ - 标准化     │  │ - 选择算法   │  │ - 实时推理   │      │
│  │ - 降维       │  │ - 超参优化   │  │ - 信号生成   │      │
│  │ - 滚动窗口   │  │ - 交叉验证   │  │ - 概率输出   │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼──────────────────┼──────────────────┼──────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                  vn.py 交易层 (Trading Layer)                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  CtaEngine (策略引擎)                                │  │
│  │  - 策略管理                                          │  │
│  │  - 订单执行                                          │  │
│  │  - 风险控制                                          │  │
│  │  - 持仓管理                                          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 核心模块设计

**1. 因子计算模块 (Factor Calculator)**

```python
class FactorCalculator:
    """因子计算引擎"""

    def __init__(self, vt_symbol: str, lookback: int = 252):
        self.vt_symbol = vt_symbol
        self.lookback = lookback
        self.data: List[BarData] = []

    def update_bar(self, bar: BarData) -> None:
        """更新K线数据"""
        self.data.append(bar)
        if len(self.data) > self.lookback:
            self.data.pop(0)

    def calculate_ma_factor(self, period: int) -> np.ndarray:
        """计算均线因子"""
        closes = np.array([bar.close_price for bar in self.data])
        return talib.SMA(closes, timeperiod=period)

    def calculate_momentum_factor(self, period: int) -> np.ndarray:
        """计算动量因子"""
        closes = np.array([bar.close_price for bar in self.data])
        return (closes / np.roll(closes, period)) - 1

    def calculate_volatility_factor(self, period: int) -> np.ndarray:
        """计算波动率因子"""
        closes = np.array([bar.close_price for bar in self.data])
        returns = np.diff(np.log(closes))
        return pd.Series(returns).rolling(period).std().values

    def get_all_factors(self) -> pd.DataFrame:
        """获取所有因子"""
        factors = pd.DataFrame()

        factors['ma_5'] = self.calculate_ma_factor(5)
        factors['ma_10'] = self.calculate_ma_factor(10)
        factors['ma_20'] = self.calculate_ma_factor(20)
        factors['momentum_5'] = self.calculate_momentum_factor(5)
        factors['momentum_10'] = self.calculate_momentum_factor(10)
        factors['volatility_10'] = self.calculate_volatility_factor(10)

        return factors
```

**2. ML 策略基类 (ML Strategy Base)**

```python
class MLStrategy(CtaTemplate):
    """机器学习策略基类"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 因子计算器
        self.factor_calculator: FactorCalculator = None

        # ML 模型
        self.model: Any = None

        # 特征数据
        self.features: pd.DataFrame = None

        # 预测概率
        self.predict_prob: float = 0.0

    def on_init(self) -> None:
        """初始化策略"""
        self.write_log("策略初始化")

        # 创建因子计算器
        self.factor_calculator = FactorCalculator(
            self.vt_symbol,
            lookback=self.lookback_window
        )

        # 加载训练好的模型
        self.load_model()

        # 创建 K 线生成器
        self.bg = BarGenerator(self.on_bar, Interval.MINUTE, 1)
        self.am = ArrayManager(size=self.lookback_window)

        # 加载历史数据
        self.load_bar(days=self.lookback_window // 24 + 10)

    def on_bar(self, bar: BarData) -> None:
        """K线回调"""
        self.cancel_all()

        # 更新因子计算器
        self.factor_calculator.update_bar(bar)

        # 获取因子
        features = self.factor_calculator.get_all_factors()

        # 检查数据完整性
        if features.isnull().any().any():
            return

        # ML 模型预测
        self.predict_prob = self.model.predict_proba(
            features.iloc[[-1]]
        )[0][1]

        # 生成交易信号
        self.generate_signal(bar)

    def load_model(self) -> None:
        """加载模型"""
        model_path = f"models/{self.strategy_name}_{self.vt_symbol}.pkl"

        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            self.write_log(f"模型加载成功: {model_path}")
        else:
            self.write_log(f"模型文件不存在: {model_path}")
            raise FileNotFoundError(f"模型文件不存在: {model_path}")
```

---

## 3. Alpha 因子的计算和应用

### 3.1 Alpha 因子的定义

Alpha 因子是指能够预测资产未来收益的量化指标。一个优秀的 Alpha 因子应该具备以下特性：

- **预测能力**: 与未来收益有显著相关性
- **稳定性**: 在不同时期、不同市场环境下表现稳定
- **独立性**: 与其他因子相关性低，提供增量信息
- **可解释性**: 具有一定的经济学逻辑
- **流动性**: 能够承载一定规模的资金量

### 3.2 常见 Alpha 因子分类

**1. 趋势类因子**

```python
def calculate_trend_factors(prices: np.ndarray) -> Dict[str, np.ndarray]:
    """计算趋势类因子"""
    factors = {}

    # 移动平均线
    factors['ma5'] = talib.SMA(prices, timeperiod=5)
    factors['ma10'] = talib.SMA(prices, timeperiod=10)
    factors['ma20'] = talib.SMA(prices, timeperiod=20)

    # 指数移动平均
    factors['ema5'] = talib.EMA(prices, timeperiod=5)
    factors['ema10'] = talib.EMA(prices, timeperiod=10)

    # MACD
    macd, macdsignal, macdhist = talib.MACD(prices)
    factors['macd'] = macd
    factors['macd_signal'] = macdsignal
    factors['macd_hist'] = macdhist

    return factors
```

**2. 动量类因子**

```python
def calculate_momentum_factors(prices: np.ndarray) -> Dict[str, np.ndarray]:
    """计算动量类因子"""
    factors = {}

    # 收益率动量
    factors['momentum_5'] = (prices / np.roll(prices, 5)) - 1
    factors['momentum_10'] = (prices / np.roll(prices, 10)) - 1
    factors['momentum_20'] = (prices / np.roll(prices, 20)) - 1

    # RSI
    factors['rsi_6'] = talib.RSI(prices, timeperiod=6)
    factors['rsi_12'] = talib.RSI(prices, timeperiod=12)
    factors['rsi_24'] = talib.RSI(prices, timeperiod=24)

    # ROC (变动率指标)
    factors['roc_10'] = talib.ROC(prices, timeperiod=10)
    factors['roc_20'] = talib.ROC(prices, timeperiod=20)

    return factors
```

**3. 波动率因子**

```python
def calculate_volatility_factors(prices: np.ndarray) -> Dict[str, np.ndarray]:
    """计算波动率因子"""
    factors = {}

    # 历史波动率
    returns = np.diff(np.log(prices))
    factors['volatility_5'] = pd.Series(returns).rolling(5).std().values
    factors['volatility_10'] = pd.Series(returns).rolling(10).std().values
    factors['volatility_20'] = pd.Series(returns).rolling(20).std().values

    # ATR (平均真实波幅)
    high = prices  # 简化示例
    low = prices
    close = prices

    factors['atr_14'] = talib.ATR(high, low, close, timeperiod=14)

    # 布林带宽度
    upper, middle, lower = talib.BBANDS(prices)
    factors['bb_width'] = (upper - lower) / middle

    return factors
```

**4. 量价因子**

```python
def calculate_volume_price_factors(
    prices: np.ndarray,
    volumes: np.ndarray
) -> Dict[str, np.ndarray]:
    """计算量价因子"""
    factors = {}

    # 量价相关性
    factors['price_volume_corr'] = pd.Series(prices).rolling(10).corr(
        pd.Series(volumes)
    ).values

    # 量比
    avg_volume = pd.Series(volumes).rolling(5).mean().values
    factors['volume_ratio'] = volumes / avg_volume

    # 量价背离
    price_change = np.diff(prices)
    volume_change = np.diff(volumes)
    factors['pv_divergence'] = price_change * volume_change

    # OBV (能量潮指标)
    factors['obv'] = talib.OBV(prices, volumes)

    return factors
```

### 3.3 因子合成与降维

```python
def factor_orthogonalization(
    factors: pd.DataFrame,
    method: str = 'pca'
) -> pd.DataFrame:
    """因子正交化处理"""

    if method == 'pca':
        from sklearn.decomposition import PCA

        # 标准化
        scaler = StandardScaler()
        factors_scaled = scaler.fit_transform(factors)

        # PCA 降维
        pca = PCA(n_components=0.95, random_state=42)
        factors_pca = pca.fit_transform(factors_scaled)

        return pd.DataFrame(
            factors_pca,
            columns=[f'pca_{i}' for i in range(factors_pca.shape[1])]
        )

    elif method == 'ica':
        from sklearn.decomposition import FastICA

        scaler = StandardScaler()
        factors_scaled = scaler.fit_transform(factors)

        ica = FastICA(n_components=min(10, factors.shape[1]), random_state=42)
        factors_ica = ica.fit_transform(factors_scaled)

        return pd.DataFrame(
            factors_ica,
            columns=[f'ica_{i}' for i in range(factors_ica.shape[1])]
        )

    else:
        return factors
```

---

## 4. 机器学习模型的集成

### 4.1 模型训练流程

```python
class ModelTrainer:
    """模型训练器"""

    def __init__(self, vt_symbol: str):
        self.vt_symbol = vt_symbol
        self.model = None
        self.scaler = None

    def prepare_data(
        self,
        bars: List[BarData],
        lookback: int = 20,
        forward_period: int = 5
    ) -> Tuple[pd.DataFrame, np.ndarray]:
        """准备训练数据"""

        data = pd.DataFrame([{
            'datetime': bar.datetime,
            'open': bar.open_price,
            'high': bar.high_price,
            'low': bar.low_price,
            'close': bar.close_price,
            'volume': bar.volume
        } for bar in bars])

        # 计算因子
        features = self.calculate_features(data, lookback)

        # 计算标签 (未来收益)
        data['future_return'] = data['close'].pct_change(forward_period).shift(-forward_period)

        # 标签处理 (涨=1, 跌=0)
        data['label'] = (data['future_return'] > 0).astype(int)

        # 去除空值
        valid_idx = features.notna().all(axis=1) & data['label'].notna()
        features = features[valid_idx]
        labels = data.loc[valid_idx, 'label'].values

        return features, labels

    def calculate_features(self, data: pd.DataFrame, lookback: int) -> pd.DataFrame:
        """计算特征"""
        features = pd.DataFrame(index=data.index)

        # 价格相关
        close = data['close'].values
        features['ma5'] = talib.SMA(close, timeperiod=5)
        features['ma10'] = talib.SMA(close, timeperiod=10)
        features['ma20'] = talib.SMA(close, timeperiod=20)

        # 动量
        features['momentum_5'] = (close / np.roll(close, 5)) - 1
        features['momentum_10'] = (close / np.roll(close, 10)) - 1

        # 波动率
        returns = np.diff(np.log(close))
        features['volatility'] = pd.Series(returns).rolling(10).std().values

        # RSI
        features['rsi'] = talib.RSI(close, timeperiod=14)

        # MACD
        macd, macdsignal, macdhist = talib.MACD(close)
        features['macd'] = macd
        features['macd_hist'] = macdhist

        return features

    def train_model(
        self,
        X_train: pd.DataFrame,
        y_train: np.ndarray,
        model_type: str = 'xgboost'
    ) -> None:
        """训练模型"""

        # 特征标准化
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)

        # 选择模型
        if model_type == 'xgboost':
            import xgboost as xgb
            self.model = xgb.XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                use_label_encoder=False,
                eval_metric='logloss'
            )

        elif model_type == 'lightgbm':
            import lightgbm as lgb
            self.model = lgb.LGBMClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42
            )

        elif model_type == 'random_forest':
            from sklearn.ensemble import RandomForestClassifier
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=10,
                random_state=42
            )

        # 训练模型
        self.model.fit(X_train_scaled, y_train)

        self.write_log(f"模型训练完成: {model_type}")

    def save_model(self, path: str) -> None:
        """保存模型"""
        model_data = {
            'model': self.model,
            'scaler': self.scaler
        }

        with open(path, 'wb') as f:
            pickle.dump(model_data, f)

        self.write_log(f"模型已保存: {path}")

    def load_model(self, path: str) -> None:
        """加载模型"""
        with open(path, 'rb') as f:
            model_data = pickle.load(f)

        self.model = model_data['model']
        self.scaler = model_data['scaler']

        self.write_log(f"模型已加载: {path}")
```

### 4.2 模型集成策略

```python
class EnsembleMLStrategy(MLStrategy):
    """集成学习策略"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 多个模型
        self.models: Dict[str, Any] = {}
        self.model_weights: Dict[str, float] = {}

    def load_models(self) -> None:
        """加载多个模型"""
        models_dir = "models/ensemble"
        model_types = ['xgboost', 'lightgbm', 'random_forest']

        for model_type in model_types:
            model_path = f"{models_dir}/{self.strategy_name}_{self.vt_symbol}_{model_type}.pkl"

            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    model_data = pickle.load(f)
                self.models[model_type] = model_data['model']
                self.models[f'{model_type}_scaler'] = model_data['scaler']

                # 权重 (可调整)
                self.model_weights[model_type] = 1.0

    def predict_ensemble(self, features: pd.DataFrame) -> float:
        """集成预测"""

        # 标准化特征
        predictions = []
        weights = []

        for model_type in ['xgboost', 'lightgbm', 'random_forest']:
            if model_type in self.models:
                scaler = self.models[f'{model_type}_scaler']
                model = self.models[model_type]

                features_scaled = scaler.transform(features)
                prob = model.predict_proba(features_scaled)[0][1]

                predictions.append(prob)
                weights.append(self.model_weights[model_type])

        # 加权平均
        ensemble_prob = np.average(predictions, weights=weights)

        return ensemble_prob
```

---

## 5. 因子挖掘和筛选

### 5.1 因子挖掘流程

```python
class FactorMiner:
    """因子挖掘器"""

    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.factors = pd.DataFrame(index=data.index)

    def mine_trend_factors(self) -> None:
        """挖掘趋势因子"""

        close = self.data['close'].values

        # 多周期均线
        for period in [5, 10, 20, 40, 60]:
            self.factors[f'ma_{period}'] = talib.SMA(close, timeperiod=period)

        # 价格相对均线的位置
        self.factors['price_ma5_ratio'] = close / self.factors['ma_5']
        self.factors['price_ma20_ratio'] = close / self.factors['ma_20']

        # 均线多头排列
        self.factors['ma_alignment'] = (
            (self.factors['ma_5'] > self.factors['ma_10']) &
            (self.factors['ma_10'] > self.factors['ma_20'])
        ).astype(int)

    def mine_momentum_factors(self) -> None:
        """挖掘动量因子"""

        close = self.data['close'].values

        # 多周期动量
        for period in [3, 5, 10, 20]:
            self.factors[f'momentum_{period}'] = (
                close / np.roll(close, period)
            ) - 1

        # 动量加速度 (二阶导数)
        for period in [5, 10]:
            momentum = self.factors[f'momentum_{period}']
            self.factors[f'momentum_accel_{period}'] = momentum - np.roll(momentum, 1)

        # RSI 偏离度
        rsi = talib.RSI(close, timeperiod=14)
        self.factors['rsi_overbought'] = (rsi > 70).astype(int)
        self.factors['rsi_oversold'] = (rsi < 30).astype(int)

    def mine_reversal_factors(self) -> None:
        """挖掘反转因子"""

        close = self.data['close'].values
        high = self.data['high'].values
        low = self.data['low'].values

        # 布林带位置
        upper, middle, lower = talib.BBANDS(close)
        self.factors['bb_position'] = (close - lower) / (upper - lower)

        # 高低点突破
        self.factors['high_breakout'] = (close == high.rolling(20).max()).astype(int)
        self.factors['low_breakout'] = (close == low.rolling(20).min()).astype(int)

        # KDJ 指标
        slowk, slowd = talib.STOCH(high, low, close)
        self.factors['kdj_k'] = slowk
        self.factors['kdj_d'] = slowd
        self.factors['kdj_j'] = 3 * slowk - 2 * slowd

    def mine_volume_factors(self) -> None:
        """挖掘成交量因子"""

        close = self.data['close'].values
        volume = self.data['volume'].values

        # 量价相关性
        self.factors['price_volume_corr'] = pd.Series(close).rolling(10).corr(
            pd.Series(volume)
        )

        # 量比
        avg_volume = volume.rolling(5).mean()
        self.factors['volume_ratio'] = volume / avg_volume

        # 量能突破
        volume_mean20 = volume.rolling(20).mean()
        self.factors['volume_breakout'] = (volume > volume_mean20 * 1.5).astype(int)

    def get_all_factors(self) -> pd.DataFrame:
        """获取所有因子"""
        self.mine_trend_factors()
        self.mine_momentum_factors()
        self.mine_reversal_factors()
        self.mine_volume_factors()

        return self.factors
```

### 5.2 因子筛选方法

```python
class FactorSelector:
    """因子选择器"""

    def __init__(self, features: pd.DataFrame, labels: np.ndarray):
        self.features = features
        self.labels = labels
        self.selected_factors = []

    def calculate_ic(self, factor: np.ndarray, returns: np.ndarray) -> float:
        """计算 IC (Information Coefficient)"""
        valid_idx = ~(np.isnan(factor) | np.isnan(returns))
        factor_valid = factor[valid_idx]
        returns_valid = returns[valid_idx]

        ic, _ = pearsonr(factor_valid, returns_valid)
        return ic

    def calculate_rank_ic(self, factor: np.ndarray, returns: np.ndarray) -> float:
        """计算 Rank IC"""
        valid_idx = ~(np.isnan(factor) | np.isnan(returns))
        factor_valid = factor[valid_idx]
        returns_valid = returns[valid_idx]

        rank_ic, _ = spearmanr(factor_valid, returns_valid)
        return rank_ic

    def factor_ic_analysis(self, returns: np.ndarray) -> pd.DataFrame:
        """因子 IC 分析"""
        results = []

        for column in self.features.columns:
            factor = self.features[column].values

            ic = self.calculate_ic(factor, returns)
            rank_ic = self.calculate_rank_ic(factor, returns)

            results.append({
                'factor': column,
                'ic': ic,
                'rank_ic': rank_ic,
                'abs_ic': abs(ic),
                'abs_rank_ic': abs(rank_ic)
            })

        df_results = pd.DataFrame(results)

        # 按绝对 IC 排序
        df_results = df_results.sort_values('abs_ic', ascending=False)

        return df_results

    def factor_importance_analysis(self, model_type: str = 'random_forest') -> pd.DataFrame:
        """因子重要性分析"""
        from sklearn.model_selection import train_test_split

        # 分割数据
        X_train, X_test, y_train, y_test = train_test_split(
            self.features, self.labels,
            test_size=0.3, random_state=42
        )

        # 训练模型
        if model_type == 'random_forest':
            from sklearn.ensemble import RandomForestClassifier
            model = RandomForestClassifier(n_estimators=100, random_state=42)
        elif model_type == 'xgboost':
            import xgboost as xgb
            model = xgb.XGBClassifier(n_estimators=100, random_state=42)

        model.fit(X_train, y_train)

        # 获取特征重要性
        if model_type == 'random_forest':
            importances = model.feature_importances_
        else:
            importances = model.feature_importances_

        # 构建结果
        df_importance = pd.DataFrame({
            'factor': self.features.columns,
            'importance': importances
        }).sort_values('importance', ascending=False)

        return df_importance

    def select_factors(
        self,
        max_factors: int = 20,
        min_ic: float = 0.02,
        correlation_threshold: float = 0.7
    ) -> List[str]:
        """选择因子"""

        # 1. IC 筛选
        df_ic = self.factor_ic_analysis(self.labels)
        df_ic = df_ic[df_ic['abs_ic'] >= min_ic]

        # 2. 相关性筛选
        selected = []
        for _, row in df_ic.iterrows():
            factor = row['factor']

            # 检查与已选因子的相关性
            if not selected:
                selected.append(factor)
            else:
                # 计算相关性
                correlations = []
                for selected_factor in selected:
                    corr = self.features[factor].corr(self.features[selected_factor])
                    correlations.append(corr)

                # 如果所有相关性都低于阈值，则添加
                if all(abs(c) < correlation_threshold for c in correlations):
                    selected.append(factor)

                # 限制因子数量
                if len(selected) >= max_factors:
                    break

        self.selected_factors = selected

        return selected
```

---

## 6. 策略回测和优化

### 6.1 ML 策略回测

```python
class MLStrategyBacktest:
    """ML 策略回测器"""

    def __init__(self, vt_symbol: str, model_path: str):
        self.vt_symbol = vt_symbol
        self.model_path = model_path
        self.model = None
        self.scaler = None

    def run_backtest(
        self,
        start_date: datetime,
        end_date: datetime,
        interval: Interval = Interval.MINUTE,
        capital: int = 100000
    ) -> pd.DataFrame:
        """运行回测"""

        # 创建回测引擎
        backtest_engine = BacktestEngine()

        # 设置参数
        backtest_engine.set_parameters(
            vt_symbol=self.vt_symbol,
            interval=interval,
            start=start_date,
            end=end_date,
            rate=0.3/10000,  # 手续费
            slippage=0.2,     # 滑点
            size=300,         # 合约乘数
            pricetick=0.2,    # 最小价格单位
            capital=capital
        )

        # 加载模型
        self.load_model()

        # 添加策略
        backtest_engine.add_strategy(
            MLTradingStrategy,
            setting={
                'model_path': self.model_path,
                'threshold_long': 0.6,
                'threshold_short': 0.4,
                'fixed_size': 1
            }
        )

        # 运行回测
        backtest_engine.run_backtesting()

        # 计算结果
        result = backtest_engine.calculate_result()
        df = backtest_engine.calculate_statistics()

        return df

    def load_model(self) -> None:
        """加载模型"""
        with open(self.model_path, 'rb') as f:
            model_data = pickle.load(f)

        self.model = model_data['model']
        self.scaler = model_data['scaler']
```

### 6.2 模型超参数优化

```python
class ModelOptimizer:
    """模型优化器"""

    def __init__(
        self,
        vt_symbol: str,
        train_data: pd.DataFrame,
        test_data: pd.DataFrame
    ):
        self.vt_symbol = vt_symbol
        self.train_data = train_data
        self.test_data = test_data

    def optimize_xgboost(
        self,
        n_trials: int = 50
    ) -> Dict[str, Any]:
        """XGBoost 超参数优化"""

        import optuna
        from sklearn.metrics import roc_auc_score

        def objective(trial):
            # 定义超参数空间
            params = {
                'n_estimators': trial.suggest_int('n_estimators', 50, 300),
                'max_depth': trial.suggest_int('max_depth', 3, 10),
                'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
                'subsample': trial.suggest_float('subsample', 0.6, 1.0),
                'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
                'min_child_weight': trial.suggest_int('min_child_weight', 1, 10),
                'reg_alpha': trial.suggest_float('reg_alpha', 0, 10),
                'reg_lambda': trial.suggest_float('reg_lambda', 0, 10),
                'random_state': 42,
                'use_label_encoder': False,
                'eval_metric': 'logloss'
            }

            # 训练模型
            import xgboost as xgb
            model = xgb.XGBClassifier(**params)

            X_train = self.train_data.drop(['label'], axis=1)
            y_train = self.train_data['label']

            X_test = self.test_data.drop(['label'], axis=1)
            y_test = self.test_data['label']

            # 标准化
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            # 训练
            model.fit(X_train_scaled, y_train)

            # 预测
            y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]

            # 计算 AUC
            auc = roc_auc_score(y_test, y_pred_proba)

            return auc

        # 运行优化
        study = optuna.create_study(direction='maximize')
        study.optimize(objective, n_trials=n_trials)

        # 返回最佳参数
        return {
            'best_params': study.best_params,
            'best_score': study.best_value,
            'best_trial': study.best_trial
        }

    def optimize_strategy_thresholds(
        self,
        model_path: str,
        backtest_engine: BacktestEngine
    ) -> Dict[str, Any]:
        """优化策略阈值"""

        results = []

        for threshold_long in np.arange(0.5, 0.9, 0.05):
            for threshold_short in np.arange(0.1, 0.5, 0.05):

                # 设置策略参数
                setting = {
                    'model_path': model_path,
                    'threshold_long': threshold_long,
                    'threshold_short': threshold_short,
                    'fixed_size': 1
                }

                # 运行回测
                backtest_engine.add_strategy(MLTradingStrategy, setting=setting)
                backtest_engine.run_backtesting()

                # 计算结果
                df_stats = backtest_engine.calculate_statistics()

                results.append({
                    'threshold_long': threshold_long,
                    'threshold_short': threshold_short,
                    'sharpe_ratio': df_stats['sharpe_ratio'].iloc[0],
                    'total_return': df_stats['total_return'].iloc[0],
                    'max_drawdown': df_stats['max_drawdown'].iloc[0]
                })

        df_results = pd.DataFrame(results)

        # 找到最佳参数
        best_idx = df_results['sharpe_ratio'].idxmax()
        best_params = df_results.iloc[best_idx].to_dict()

        return {
            'best_params': best_params,
            'all_results': df_results
        }
```

---

## 7. 实盘部署注意事项

### 7.1 实盘前的检查清单

```python
class PreTradeChecklist:
    """实盘前检查清单"""

    @staticmethod
    def check_model(model_path: str) -> bool:
        """检查模型文件"""
        if not os.path.exists(model_path):
            print(f"❌ 模型文件不存在: {model_path}")
            return False

        try:
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            print(f"✅ 模型文件有效: {model_path}")
            return True
        except Exception as e:
            print(f"❌ 模型文件损坏: {e}")
            return False

    @staticmethod
    def check_data_quality(bars: List[BarData]) -> bool:
        """检查数据质量"""
        if len(bars) < 100:
            print(f"❌ 历史数据不足: {len(bars)} 条")
            return False

        # 检查价格合理性
        prices = [bar.close_price for bar in bars]
        if any(p <= 0 for p in prices):
            print("❌ 存在异常价格")
            return False

        print(f"✅ 数据质量检查通过: {len(bars)} 条 K 线")
        return True

    @staticmethod
    def check_account_balance(main_engine: MainEngine, min_balance: float) -> bool:
        """检查账户余额"""
        account = main_engine.get_account()

        if account.balance < min_balance:
            print(f"❌ 账户余额不足: {account.balance} < {min_balance}")
            return False

        print(f"✅ 账户余额充足: {account.balance}")
        return True

    @staticmethod
    def check_risk_controls(strategy: CtaTemplate) -> bool:
        """检查风险控制"""
        # 检查止损设置
        if not hasattr(strategy, 'stop_loss'):
            print("⚠️  策略未设置止损")
            return False

        # 检查仓位管理
        if not hasattr(strategy, 'position_size'):
            print("⚠️  策略未设置仓位管理")
            return False

        print("✅ 风险控制检查通过")
        return True

    @staticmethod
    def run_all_checks(
        model_path: str,
        bars: List[BarData],
        main_engine: MainEngine,
        strategy: CtaTemplate,
        min_balance: float = 100000
    ) -> bool:
        """运行所有检查"""

        print("=" * 60)
        print("实盘前检查清单")
        print("=" * 60)

        checks = [
            ("模型文件", PreTradeChecklist.check_model(model_path)),
            ("数据质量", PreTradeChecklist.check_data_quality(bars)),
            ("账户余额", PreTradeChecklist.check_account_balance(main_engine, min_balance)),
            ("风险控制", PreTradeChecklist.check_risk_controls(strategy))
        ]

        all_passed = all(result for _, result in checks)

        print("=" * 60)
        if all_passed:
            print("✅ 所有检查通过，可以启动实盘")
        else:
            print("❌ 存在检查未通过，请修复后再启动")
        print("=" * 60)

        return all_passed
```

### 7.2 实盘风险控制

```python
class RealtimeRiskControl:
    """实时风险控制"""

    def __init__(self, strategy: CtaTemplate):
        self.strategy = strategy

        # 风险参数
        self.max_position_value = 500000    # 最大持仓市值
        self.max_daily_loss = 10000        # 最大日亏损
        self.max_trade_count = 20          # 最大交易次数

        # 状态
        self.daily_pnl = 0
        self.trade_count_today = 0
        self.last_trade_date = None

    def check_position_limit(self, price: float, volume: float) -> bool:
        """检查持仓限制"""
        position_value = abs(self.strategy.pos * price)

        if position_value >= self.max_position_value:
            self.strategy.write_log(
                f"⚠️  持仓已达上限: {position_value} >= {self.max_position_value}"
            )
            return False

        return True

    def check_daily_loss_limit(self) -> bool:
        """检查日亏损限制"""
        if self.daily_pnl <= -self.max_daily_loss:
            self.strategy.write_log(
                f"⚠️  日亏损已达上限: {self.daily_pnl} <= -{self.max_daily_loss}"
            )
            return False

        return True

    def check_trade_count(self) -> bool:
        """检查交易次数限制"""
        today = datetime.now().date()

        # 每日重置
        if self.last_trade_date != today:
            self.trade_count_today = 0
            self.last_trade_date = today

        if self.trade_count_today >= self.max_trade_count:
            self.strategy.write_log(
                f"⚠️  今日交易次数已达上限: {self.trade_count_today} >= {self.max_trade_count}"
            )
            return False

        return True

    def update_trade(self, trade: TradeData) -> None:
        """更新交易状态"""
        self.trade_count_today += 1

        # 更新盈亏
        if trade.direction == Direction.LONG:
            self.daily_pnl += trade.volume * trade.price
        else:
            self.daily_pnl -= trade.volume * trade.price
```

---

## 8. 最佳实践建议

### 8.1 模型训练建议

**1. 数据划分**

```python
def split_data_train_val_test(
    data: pd.DataFrame,
    train_ratio: float = 0.6,
    val_ratio: float = 0.2,
    test_ratio: float = 0.2
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """数据划分"""

    n = len(data)
    train_end = int(n * train_ratio)
    val_end = int(n * (train_ratio + val_ratio))

    train_data = data.iloc[:train_end]
    val_data = data.iloc[train_end:val_end]
    test_data = data.iloc[val_end:]

    return train_data, val_data, test_data
```

**2. 交叉验证**

```python
def time_series_cv(
    X: pd.DataFrame,
    y: np.ndarray,
    n_splits: int = 5
) -> Iterator[Tuple[np.ndarray, np.ndarray]]:
    """时间序列交叉验证"""

    n_samples = len(X)
    k_fold_size = n_samples // n_splits

    for i in range(n_splits):
        train_start = 0
        train_end = (i + 1) * k_fold_size
        val_start = train_end
        val_end = min((i + 2) * k_fold_size, n_samples)

        yield (
            X.iloc[train_start:train_end].values,
            X.iloc[val_start:val_end].values,
            y[train_start:train_end],
            y[val_start:val_end]
        )
```

**3. 避免数据泄露**

```python
def prepare_features_without_leakage(
    data: pd.DataFrame,
    lookback: int = 20,
    forward_period: int = 5
) -> Tuple[pd.DataFrame, np.ndarray]:
    """准备无泄露的特征"""

    features = pd.DataFrame(index=data.index)

    # 只使用历史数据计算特征
    for i in range(lookback, len(data) - forward_period):
        # 历史窗口
        window_data = data.iloc[i - lookback:i]

        # 计算特征
        features.loc[data.index[i], 'ma_5'] = window_data['close'].mean()
        features.loc[data.index[i], 'momentum_10'] = (
            window_data['close'].iloc[-1] / window_data['close'].iloc[-10] - 1
        )

    # 标签 (未来收益)
    data['future_return'] = data['close'].pct_change(forward_period).shift(-forward_period)
    labels = (data['future_return'] > 0).astype(int)

    # 对齐
    valid_idx = features.notna().all(axis=1) & labels.notna()
    features = features[valid_idx]
    labels = labels[valid_idx]

    return features, labels
```

### 8.2 因子工程建议

**1. 因子标准化**

```python
def standardize_factor(
    factor: np.ndarray,
    method: str = 'zscore'
) -> np.ndarray:
    """因子标准化"""

    if method == 'zscore':
        return (factor - np.mean(factor)) / np.std(factor)

    elif method == 'minmax':
        return (factor - np.min(factor)) / (np.max(factor) - np.min(factor))

    elif method == 'rank':
        from scipy.stats import rankdata
        return rankdata(factor) / len(factor)

    return factor
```

**2. 因子中性化**

```python
def neutralize_factor(
    factor: pd.Series,
    industry: pd.Series,
    market_cap: pd.Series
) -> pd.Series:
    """因子中性化"""

    from sklearn.linear_model import LinearRegression

    # 构建回归变量
    X = pd.get_dummies(industry)
    X['market_cap'] = market_cap

    # 回归剔除
    reg = LinearRegression()
    reg.fit(X, factor)

    # 残差作为中性化后的因子
    neutralized = factor - reg.predict(X)

    return neutralized
```

**3. 因子正交化**

```python
def orthogonalize_factors(
    factors: pd.DataFrame,
    reference_factors: pd.DataFrame
) -> pd.DataFrame:
    """因子正交化"""

    from sklearn.linear_model import LinearRegression

    orthogonalized = factors.copy()

    for col in factors.columns:
        y = factors[col].values
        X = reference_factors.values

        reg = LinearRegression()
        reg.fit(X, y)

        residuals = y - reg.predict(X)
        orthogonalized[col] = residuals

    return orthogonalized
```

### 8.3 策略监控建议

```python
class StrategyMonitor:
    """策略监控"""

    def __init__(self, strategy_name: str):
        self.strategy_name = strategy_name
        self.metrics = {
            'total_trades': 0,
            'win_trades': 0,
            'loss_trades': 0,
            'total_pnl': 0.0,
            'max_drawdown': 0.0,
            'sharpe_ratio': 0.0
        }

    def update_metrics(self, trade: TradeData, account: AccountData) -> None:
        """更新指标"""

        self.metrics['total_trades'] += 1

        # 计算盈亏
        pnl = trade.volume * trade.price
        if trade.direction == Direction.LONG:
            self.metrics['total_pnl'] += pnl
        else:
            self.metrics['total_pnl'] -= pnl

        # 统计盈亏
        if pnl > 0:
            self.metrics['win_trades'] += 1
        else:
            self.metrics['loss_trades'] += 1

        # 计算回撤
        if account.balance < account.previous_balance:
            drawdown = (account.previous_balance - account.balance) / account.previous_balance
            self.metrics['max_drawdown'] = max(
                self.metrics['max_drawdown'],
                drawdown
            )

    def get_report(self) -> str:
        """获取监控报告"""

        win_rate = (
            self.metrics['win_trades'] / self.metrics['total_trades'] * 100
            if self.metrics['total_trades'] > 0 else 0
        )

        report = f"""
        策略监控报告: {self.strategy_name}
        {'=' * 50}
        总交易次数: {self.metrics['total_trades']}
        盈利次数: {self.metrics['win_trades']}
        亏损次数: {self.metrics['loss_trades']}
        胜率: {win_rate:.2f}%
        总盈亏: {self.metrics['total_pnl']:.2f}
        最大回撤: {self.metrics['max_drawdown']:.2%}
        {'=' * 50}
        """

        return report
```

---

## 9. 简单的因子示例

### 9.1 动量因子示例

```python
class MomentumStrategy(MLStrategy):
    """动量因子策略"""

    author = "Quant Factory"

    # 参数
    lookback_window: int = 252
    momentum_period: int = 20
    threshold_long: float = 0.6
    threshold_short: float = 0.4
    fixed_size: int = 1

    # 变量
    momentum: float = 0.0
    predict_prob: float = 0.0

    parameters = [
        "lookback_window",
        "momentum_period",
        "threshold_long",
        "threshold_short",
        "fixed_size"
    ]
    variables = ["momentum", "predict_prob"]

    def on_init(self) -> None:
        """策略初始化"""
        self.write_log("动量因子策略初始化")

        # 创建因子计算器
        self.factor_calculator = FactorCalculator(
            self.vt_symbol,
            lookback=self.lookback_window
        )

        # 加载模型
        try:
            self.load_model()
        except FileNotFoundError:
            self.write_log("模型未找到，使用规则模式")
            self.model = None

        # 创建 K 线生成器
        self.bg = BarGenerator(self.on_bar, Interval.MINUTE, 1)
        self.am = ArrayManager(size=self.lookback_window)

        # 加载历史数据
        self.load_bar(days=30)

    def on_bar(self, bar: BarData) -> None:
        """K线回调"""
        self.cancel_all()

        # 更新因子计算器
        self.factor_calculator.update_bar(bar)

        # 计算动量因子
        data = self.factor_calculator.data
        if len(data) >= self.momentum_period:
            self.momentum = (
                data[-1].close_price / data[-self.momentum_period].close_price
            ) - 1

            # 生成信号
            if self.model is None:
                # 规则模式
                if self.momentum > 0.02:
                    signal = "LONG"
                elif self.momentum < -0.02:
                    signal = "SHORT"
                else:
                    signal = "HOLD"

                self.execute_signal(bar, signal)

            else:
                # ML 模式
                features = self.factor_calculator.get_all_factors()
                if not features.isnull().any().any():
                    self.predict_prob = self.model.predict_proba(
                        features.iloc[[-1]]
                    )[0][1]

                    # 生成信号
                    if self.predict_prob > self.threshold_long:
                        signal = "LONG"
                    elif self.predict_prob < self.threshold_short:
                        signal = "SHORT"
                    else:
                        signal = "HOLD"

                    self.execute_signal(bar, signal)

        self.put_event()

    def execute_signal(self, bar: BarData, signal: str) -> None:
        """执行交易信号"""
        if not self.trading:
            return

        if signal == "LONG":
            if self.pos == 0:
                self.buy(bar.close_price, self.fixed_size)
            elif self.pos < 0:
                self.cover(bar.close_price, abs(self.pos))
                self.buy(bar.close_price, self.fixed_size)

        elif signal == "SHORT":
            if self.pos == 0:
                self.short(bar.close_price, self.fixed_size)
            elif self.pos > 0:
                self.sell(bar.close_price, abs(self.pos))
                self.short(bar.close_price, self.fixed_size)

        elif signal == "HOLD":
            pass
```

### 9.2 双因子组合策略

```python
class DualFactorStrategy(MLStrategy):
    """双因子组合策略"""

    author = "Quant Factory"

    # 参数
    lookback_window: int = 100
    fast_period: int = 5
    slow_period: int = 20
    vol_period: int = 10
    threshold_long: float = 0.6
    threshold_short: float = 0.4
    fixed_size: int = 1

    # 变量
    ma_factor: float = 0.0
    vol_factor: float = 0.0
    combined_score: float = 0.0

    parameters = [
        "lookback_window",
        "fast_period",
        "slow_period",
        "vol_period",
        "threshold_long",
        "threshold_short",
        "fixed_size"
    ]
    variables = ["ma_factor", "vol_factor", "combined_score"]

    def on_init(self) -> None:
        """策略初始化"""
        self.write_log("双因子组合策略初始化")

        self.bg = BarGenerator(self.on_bar, Interval.MINUTE, 1)
        self.am = ArrayManager(size=self.lookback_window)

        self.load_bar(days=30)

    def on_bar(self, bar: BarData) -> None:
        """K线回调"""
        self.cancel_all()

        self.am.update_bar(bar)
        if not self.am.inited:
            return

        # 计算均线因子
        ma_fast = self.am.sma(self.fast_period)
        ma_slow = self.am.sma(self.slow_period)
        self.ma_factor = (ma_fast - ma_slow) / ma_slow

        # 计算波动率因子
        atr = self.am.atr(14)
        self.vol_factor = atr / self.am.close

        # 组合得分
        self.combined_score = 0.6 * self.ma_factor - 0.4 * self.vol_factor

        # 生成信号
        if self.combined_score > 0.02:
            signal = "LONG"
        elif self.combined_score < -0.02:
            signal = "SHORT"
        else:
            signal = "HOLD"

        self.execute_signal(bar, signal)

        self.put_event()

    def execute_signal(self, bar: BarData, signal: str) -> None:
        """执行交易信号"""
        if not self.trading:
            return

        if signal == "LONG":
            if self.pos == 0:
                self.buy(bar.close_price, self.fixed_size)
            elif self.pos < 0:
                self.cover(bar.close_price, abs(self.pos))
                self.buy(bar.close_price, self.fixed_size)

        elif signal == "SHORT":
            if self.pos == 0:
                self.short(bar.close_price, self.fixed_size)
            elif self.pos > 0:
                self.sell(bar.close_price, abs(self.pos))
                self.short(bar.close_price, self.fixed_size)

        elif signal == "HOLD":
            pass
```

---

## 总结

本文档全面介绍了 vn.py AI 量化系统的核心概念和实现方法，包括：

1. **AI 量化策略基础**: 从概念到应用场景的全面介绍
2. **系统架构**: 数据层、因子层、ML 层、交易层的分层设计
3. **Alpha 因子**: 趋势、动量、波动率、量价等各类因子的计算方法
4. **模型集成**: XGBoost、LightGBM、随机森林等模型的训练和应用
5. **因子挖掘**: 自动化因子发现和筛选流程
6. **回测优化**: 完整的策略回测和超参数优化方法
7. **实盘部署**: 实盘前检查和风险控制机制
8. **最佳实践**: 数据处理、因子工程、监控建议
9. **实战示例**: 动量策略和双因子策略的完整实现

通过本指南，您可以快速掌握在 vn.py 中构建 AI 量化系统的核心技能，实现从因子挖掘到实盘交易的完整流程。
