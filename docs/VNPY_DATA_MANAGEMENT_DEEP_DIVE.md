# vn.py 数据管理模块深度解析

**版本**: vn.py 3.x/4.x
**更新时间**: 2026-02-20

---

## 目录

1. [数据库抽象层设计](#1-数据库抽象层设计)
2. [多数据库支持详解](#2-多数据库支持详解)
3. [数据存储机制深度剖析](#3-数据存储机制深度剖析)
4. [数据查询优化策略](#4-数据查询优化策略)
5. [数据导入导出完整方案](#5-数据导入导出完整方案)
6. [数据备份与恢复策略](#6-数据备份与恢复策略)
7. [大数据处理高级技巧](#7-大数据处理高级技巧)
8. [数据同步机制设计](#8-数据同步机制设计)
9. [完整代码示例集合](#9-完整代码示例集合)

---

## 1. 数据库抽象层设计

### 1.1 BaseDatabase 抽象类架构

vn.py 数据管理模块的核心是 `BaseDatabase` 抽象基类，它定义了所有数据库后端必须实现的标准接口。这种设计遵循了**依赖倒置原则**，允许上层应用代码与具体数据库实现解耦。

#### 源码分析

```python
class BaseDatabase(ABC):
    """
    抽象数据库类，用于连接不同数据库系统。
    
    设计模式：
    - 策略模式：不同数据库实现不同策略
    - 工厂模式：通过 get_database() 工厂方法创建实例
    - 模板方法模式：定义算法骨架，子类实现具体步骤
    """
    
    @abstractmethod
    def save_bar_data(self, bars: list[BarData], stream: bool = False) -> bool:
        """
        保存 K 线数据到数据库。
        
        参数:
            bars: BarData 对象列表
            stream: 是否为流式数据（增量更新）
        
        返回:
            bool: 保存是否成功
        """
        pass

    @abstractmethod
    def save_tick_data(self, ticks: list[TickData], stream: bool = False) -> bool:
        """
        保存 Tick 数据到数据库。
        """
        pass

    @abstractmethod
    def load_bar_data(
        self,
        symbol: str,
        exchange: Exchange,
        interval: Interval,
        start: datetime,
        end: datetime
    ) -> list[BarData]:
        """
        从数据库加载 K 线数据。
        """
        pass

    @abstractmethod
    def load_tick_data(
        self,
        symbol: str,
        exchange: Exchange,
        start: datetime,
        end: datetime
    ) -> list[TickData]:
        """
        从数据库加载 Tick 数据。
        """
        pass

    @abstractmethod
    def delete_bar_data(
        self,
        symbol: str,
        exchange: Exchange,
        interval: Interval
    ) -> int:
        """
        删除指定 K 线数据。
        
        返回:
            int: 删除的记录数
        """
        pass

    @abstractmethod
    def delete_tick_data(
        self,
        symbol: str,
        exchange: Exchange
    ) -> int:
        """
        删除指定 Tick 数据。
        """
        pass

    @abstractmethod
    def get_bar_overview(self) -> list[BarOverview]:
        """
        获取数据库中 K 线数据的概览信息。
        """
        pass

    @abstractmethod
    def get_tick_overview(self) -> list[TickOverview]:
        """
        获取数据库中 Tick 数据的概览信息。
        """
        pass
```

### 1.2 工厂模式实现

vn.py 使用工厂模式动态创建数据库实例，通过配置文件决定使用哪种数据库。

```python
database: BaseDatabase | None = None

def get_database() -> BaseDatabase:
    """
    获取数据库实例的工厂方法。
    
    工作流程：
    1. 检查是否已初始化数据库实例
    2. 从配置读取数据库名称
    3. 动态导入对应的数据库模块
    4. 创建数据库对象并缓存
    
    优点：
    - 延迟初始化：只在需要时创建连接
    - 单例模式：确保全局只有一个数据库实例
    - 可扩展性：新增数据库只需添加模块，无需修改核心代码
    """
    global database
    if database:
        return database

    # 读取配置
    database_name: str = SETTINGS["database.name"]
    module_name: str = f"vnpy_{database_name}"

    # 动态导入模块
    try:
        module: ModuleType = import_module(module_name)
    except ModuleNotFoundError:
        print(_("找不到数据库驱动{}，使用默认的SQLite数据库").format(module_name))
        module = import_module("vnpy_sqlite")

    # 创建数据库对象
    database = module.Database()
    return database
```

### 1.3 自定义数据库实现示例

如需支持新的数据库（如 MongoDB），只需继承 `BaseDatabase` 并实现所有抽象方法。

```python
from vnpy.trader.database import BaseDatabase, convert_tz, DB_TZ
from vnpy.trader.object import BarData, TickData, BarOverview, TickOverview
from vnpy.trader.constant import Exchange, Interval

class MongoDatabase(BaseDatabase):
    """MongoDB 数据库实现示例"""
    
    def __init__(self) -> None:
        from pymongo import MongoClient
        from vnpy.trader.setting import SETTINGS
        
        self.client = MongoClient(
            host=SETTINGS.get("database.host", "localhost"),
            port=SETTINGS.get("database.port", 27017),
            username=SETTINGS.get("database.username"),
            password=SETTINGS.get("database.password"),
            database=SETTINGS.get("database.database", "vnpy")
        )
        self.db = self.client[SETTINGS.get("database.database", "vnpy")]
        
    def save_bar_data(self, bars: list[BarData], stream: bool = False) -> bool:
        """保存 K 线数据"""
        if not bars:
            return False
            
        bar = bars[0]
        collection = self.db[f"bar_data_{bar.interval.value}"]
        
        data_list = []
        for bar in bars:
            bar.datetime = convert_tz(bar.datetime)
            data = {
                "symbol": bar.symbol,
                "exchange": bar.exchange.value,
                "datetime": bar.datetime,
                "open_price": bar.open_price,
                "high_price": bar.high_price,
                "low_price": bar.low_price,
                "close_price": bar.close_price,
                "volume": bar.volume,
                "turnover": bar.turnover,
                "open_interest": bar.open_interest,
            }
            data_list.append(data)
        
        # 批量插入，使用 upsert 避免重复
        for data in data_list:
            collection.update_one(
                {"symbol": data["symbol"], "exchange": data["exchange"], "datetime": data["datetime"]},
                {"$set": data},
                upsert=True
            )
        
        return True
    
    def save_tick_data(self, ticks: list[TickData], stream: bool = False) -> bool:
        """保存 Tick 数据"""
        if not ticks:
            return False
            
        collection = self.db["tick_data"]
        
        data_list = []
        for tick in ticks:
            tick.datetime = convert_tz(tick.datetime)
            data = {
                "symbol": tick.symbol,
                "exchange": tick.exchange.value,
                "datetime": tick.datetime,
                "last_price": tick.last_price,
                "volume": tick.volume,
                "turnover": tick.turnover,
                # ... 其他字段
            }
            data_list.append(data)
        
        for data in data_list:
            collection.update_one(
                {"symbol": data["symbol"], "exchange": data["exchange"], "datetime": data["datetime"]},
                {"$set": data},
                upsert=True
            )
        
        return True
    
    def load_bar_data(
        self,
        symbol: str,
        exchange: Exchange,
        interval: Interval,
        start: datetime,
        end: datetime
    ) -> list[BarData]:
        """加载 K 线数据"""
        collection = self.db[f"bar_data_{interval.value}"]
        
        cursor = collection.find({
            "symbol": symbol,
            "exchange": exchange.value,
            "datetime": {"$gte": start, "$lte": end}
        }).sort("datetime", 1)
        
        bars = []
        for item in cursor:
            bar = BarData(
                symbol=item["symbol"],
                exchange=Exchange(item["exchange"]),
                interval=interval,
                datetime=datetime.fromtimestamp(
                    item["datetime"].timestamp(), DB_TZ
                ),
                open_price=item["open_price"],
                high_price=item["high_price"],
                low_price=item["low_price"],
                close_price=item["close_price"],
                volume=item["volume"],
                turnover=item["turnover"],
                open_interest=item["open_interest"],
                gateway_name="DB"
            )
            bars.append(bar)
        
        return bars
    
    def load_tick_data(
        self,
        symbol: str,
        exchange: Exchange,
        start: datetime,
        end: datetime
    ) -> list[TickData]:
        """加载 Tick 数据"""
        # 实现类似 load_bar_data
        pass
    
    def delete_bar_data(
        self,
        symbol: str,
        exchange: Exchange,
        interval: Interval
    ) -> int:
        """删除 K 线数据"""
        collection = self.db[f"bar_data_{interval.value}"]
        result = collection.delete_many({
            "symbol": symbol,
            "exchange": exchange.value
        })
        return result.deleted_count
    
    def delete_tick_data(
        self,
        symbol: str,
        exchange: Exchange
    ) -> int:
        """删除 Tick 数据"""
        collection = self.db["tick_data"]
        result = collection.delete_many({
            "symbol": symbol,
            "exchange": exchange.value
        })
        return result.deleted_count
    
    def get_bar_overview(self) -> list[BarOverview]:
        """获取 K 线概览"""
        overviews = []
        for collection_name in self.db.list_collection_names():
            if collection_name.startswith("bar_data_"):
                interval = collection_name.replace("bar_data_", "")
                pipeline = [
                    {"$group": {
                        "_id": {"symbol": "$symbol", "exchange": "$exchange"},
                        "count": {"$sum": 1},
                        "start": {"$min": "$datetime"},
                        "end": {"$max": "$datetime"}
                    }}
                ]
                results = self.db[collection_name].aggregate(pipeline)
                for r in results:
                    overview = BarOverview(
                        symbol=r["_id"]["symbol"],
                        exchange=Exchange(r["_id"]["exchange"]),
                        interval=Interval(interval),
                        count=r["count"],
                        start=r["start"],
                        end=r["end"]
                    )
                    overviews.append(overview)
        return overviews
    
    def get_tick_overview(self) -> list[TickOverview]:
        """获取 Tick 概览"""
        # 实现类似 get_bar_overview
        pass
```

---

## 2. 多数据库支持详解

### 2.1 SQLite 实现（Peewee ORM）

vn.py 的默认数据库实现使用 **Peewee ORM**，它是一个轻量级的 Python ORM，非常适合快速开发。

#### 表结构设计

```python
from peewee import (
    AutoField, CharField, DateTimeField, FloatField, 
    IntegerField, Model, SqliteDatabase, ModelSelect
)
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.setting import SETTINGS

# 数据库连接
filename: str = SETTINGS["database.database"] or "database.db"
db: SqliteDatabase = SqliteDatabase(filename)

class DbBarData(Model):
    """K线数据表映射对象"""
    
    id: AutoField = AutoField()
    
    symbol: CharField = CharField()
    exchange: CharField = CharField()
    datetime: DateTimeField = DateTimeField()
    interval: CharField = CharField()
    
    volume: FloatField = FloatField()
    turnover: FloatField = FloatField()
    open_interest: FloatField = FloatField()
    open_price: FloatField = FloatField()
    high_price: FloatField = FloatField()
    low_price: FloatField = FloatField()
    close_price: FloatField = FloatField()
    
    class Meta:
        database: SqliteDatabase = db
        # 复合索引：symbol + exchange + interval + datetime
        indexes: tuple = ((("symbol", "exchange", "interval", "datetime"), True),)

class DbTickData(Model):
    """Tick数据表映射对象"""
    
    id: AutoField = AutoField()
    
    symbol: CharField = CharField()
    exchange: CharField = CharField()
    datetime: DateTimeField = DateTimeField()
    
    name: CharField = CharField()
    volume: FloatField = FloatField()
    turnover: FloatField = FloatField()
    open_interest: FloatField = FloatField()
    last_price: FloatField = FloatField()
    last_volume: FloatField = FloatField()
    limit_up: FloatField = FloatField()
    limit_down: FloatField = FloatField()
    
    open_price: FloatField = FloatField()
    high_price: FloatField = FloatField()
    low_price: FloatField = FloatField()
    pre_close: FloatField = FloatField()
    
    # 5档买卖盘
    bid_price_1: FloatField = FloatField()
    bid_price_2: FloatField = FloatField(null=True)
    bid_price_3: FloatField = FloatField(null=True)
    bid_price_4: FloatField = FloatField(null=True)
    bid_price_5: FloatField = FloatField(null=True)
    
    ask_price_1: FloatField = FloatField()
    ask_price_2: FloatField = FloatField(null=True)
    ask_price_3: FloatField = FloatField(null=True)
    ask_price_4: FloatField = FloatField(null=True)
    ask_price_5: FloatField = FloatField(null=True)
    
    bid_volume_1: FloatField = FloatField()
    bid_volume_2: FloatField = FloatField(null=True)
    bid_volume_3: FloatField = FloatField(null=True)
    bid_volume_4: FloatField = FloatField(null=True)
    bid_volume_5: FloatField = FloatField(null=True)
    
    ask_volume_1: FloatField = FloatField()
    ask_volume_2: FloatField = FloatField(null=True)
    ask_volume_3: FloatField = FloatField(null=True)
    ask_volume_4: FloatField = FloatField(null=True)
    ask_volume_5: FloatField = FloatField(null=True)
    
    localtime: DateTimeField = DateTimeField(null=True)
    
    class Meta:
        database: SqliteDatabase = db
        # 复合索引：symbol + exchange + datetime
        indexes: tuple = ((("symbol", "exchange", "datetime"), True),)

class DbBarOverview(Model):
    """K线汇总数据表（元数据）"""
    
    id: AutoField = AutoField()
    
    symbol: CharField = CharField()
    exchange: CharField = CharField()
    interval: CharField = CharField()
    count: int = IntegerField()
    start: DateTimeField = DateTimeField()
    end: DateTimeField = DateTimeField()
    
    class Meta:
        database: SqliteDatabase = db
        indexes: tuple = ((("symbol", "exchange", "interval"), True),)

class DbTickOverview(Model):
    """Tick汇总数据表（元数据）"""
    
    id: AutoField = AutoField()
    
    symbol: CharField = CharField()
    exchange: CharField = CharField()
    count: int = IntegerField()
    start: DateTimeField = DateTimeField()
    end: DateTimeField = DateTimeField()
    
    class Meta:
        database: SqliteDatabase = db
        indexes: tuple = ((("symbol", "exchange"), True),)
```

### 2.2 MySQL 实现方案

MySQL 适合生产环境和多用户并发场景。以下是使用 **SQLAlchemy** 的实现示例。

```python
from sqlalchemy import (
    create_engine, Column, String, DateTime, Float, 
    Integer, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from vnpy.trader.setting import SETTINGS

Base = declarative_base()

class MysqlBarData(Base):
    """MySQL K线数据表"""
    __tablename__ = "bar_data"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20))
    exchange = Column(String(20))
    datetime = Column(DateTime)
    interval = Column(String(20))
    
    volume = Column(Float)
    turnover = Column(Float)
    open_interest = Column(Float)
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    close_price = Column(Float)
    
    # 复合索引
    __table_args__ = (
        Index('idx_symbol_exchange_interval_datetime', 
              'symbol', 'exchange', 'interval', 'datetime'),
    )

class MysqlDatabase(BaseDatabase):
    """MySQL 数据库实现"""
    
    def __init__(self) -> None:
        # 创建连接引擎
        db_url = (
            f"mysql+pymysql://{SETTINGS['database.username']}:"
            f"{SETTINGS['database.password']}@"
            f"{SETTINGS['database.host']}:{SETTINGS['database.port']}/"
            f"{SETTINGS['database.database']}"
        )
        
        # 连接池配置
        self.engine = create_engine(
            db_url,
            pool_size=10,
            max_overflow=20,
            pool_timeout=30,
            pool_recycle=3600,
            echo=False
        )
        
        # 创建会话工厂
        self.Session = sessionmaker(bind=self.engine)
        
        # 创建表
        Base.metadata.create_all(self.engine)
    
    def save_bar_data(self, bars: list[BarData], stream: bool = False) -> bool:
        """批量保存 K 线数据"""
        if not bars:
            return False
        
        session = self.Session()
        try:
            # 转换为字典列表
            data_dicts = []
            for bar in bars:
                bar.datetime = convert_tz(bar.datetime)
                data = {
                    "symbol": bar.symbol,
                    "exchange": bar.exchange.value,
                    "datetime": bar.datetime,
                    "interval": bar.interval.value,
                    "volume": bar.volume,
                    "turnover": bar.turnover,
                    "open_interest": bar.open_interest,
                    "open_price": bar.open_price,
                    "high_price": bar.high_price,
                    "low_price": bar.low_price,
                    "close_price": bar.close_price,
                }
                data_dicts.append(data)
            
            # 批量插入（使用 merge 实现去重）
            for data in data_dicts:
                session.merge(MysqlBarData(**data))
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"保存失败: {e}")
            return False
        finally:
            session.close()
    
    def load_bar_data(
        self,
        symbol: str,
        exchange: Exchange,
        interval: Interval,
        start: datetime,
        end: datetime
    ) -> list[BarData]:
        """加载 K 线数据"""
        session = self.Session()
        try:
            query = session.query(MysqlBarData).filter(
                MysqlBarData.symbol == symbol,
                MysqlBarData.exchange == exchange.value,
                MysqlBarData.interval == interval.value,
                MysqlBarData.datetime >= start,
                MysqlBarData.datetime <= end
            ).order_by(MysqlBarData.datetime)
            
            bars = []
            for db_bar in query:
                bar = BarData(
                    symbol=db_bar.symbol,
                    exchange=Exchange(db_bar.exchange),
                    datetime=datetime.fromtimestamp(
                        db_bar.datetime.timestamp(), DB_TZ
                    ),
                    interval=Interval(db_bar.interval),
                    volume=db_bar.volume,
                    turnover=db_bar.turnover,
                    open_interest=db_bar.open_interest,
                    open_price=db_bar.open_price,
                    high_price=db_bar.high_price,
                    low_price=db_bar.low_price,
                    close_price=db_bar.close_price,
                    gateway_name="DB"
                )
                bars.append(bar)
            
            return bars
        finally:
            session.close()
    
    # ... 其他方法实现类似
```

### 2.3 PostgreSQL 实现方案

PostgreSQL 提供更强大的功能和更好的并发性能，支持更复杂的数据类型和索引。

```python
from sqlalchemy.dialects.postgresql import (
    UUID, JSONB, insert as pg_insert
)
from sqlalchemy.sql import select, func
import uuid

class PostgresBarData(Base):
    """PostgreSQL K线数据表"""
    __tablename__ = "bar_data"
    
    # 使用 UUID 作为主键（高并发下性能更好）
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(20))
    exchange = Column(String(20))
    datetime = Column(DateTime)
    interval = Column(String(20))
    
    volume = Column(Float)
    turnover = Column(Float)
    open_interest = Column(Float)
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    close_price = Column(Float)
    
    # JSONB 字段存储额外信息
    extra = Column(JSONB, nullable=True)
    
    # 部分索引（只对特定 interval 创建索引）
    __table_args__ = (
        Index('idx_bar_symbol_exchange_interval', 
              'symbol', 'exchange', 'interval'),
        Index('idx_bar_datetime', 'datetime'),
    )

class PostgresDatabase(BaseDatabase):
    """PostgreSQL 数据库实现"""
    
    def __init__(self) -> None:
        # 创建连接引擎
        db_url = (
            f"postgresql+psycopg2://{SETTINGS['database.username']}:"
            f"{SETTINGS['database.password']}@"
            f"{SETTINGS['database.host']}:{SETTINGS['database.port']}/"
            f"{SETTINGS['database.database']}"
        )
        
        self.engine = create_engine(
            db_url,
            pool_size=20,
            max_overflow=40,
            pool_pre_ping=True,  # 自动检测连接健康
            echo=False
        )
        
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)
    
    def save_bar_data(self, bars: list[BarData], stream: bool = False) -> bool:
        """使用 PostgreSQL 的 UPSERT 语法"""
        if not bars:
            return False
        
        session = self.Session()
        try:
            data_dicts = []
            for bar in bars:
                bar.datetime = convert_tz(bar.datetime)
                data = {
                    "symbol": bar.symbol,
                    "exchange": bar.exchange.value,
                    "datetime": bar.datetime,
                    "interval": bar.interval.value,
                    "volume": bar.volume,
                    "turnover": bar.turnover,
                    "open_interest": bar.open_interest,
                    "open_price": bar.open_price,
                    "high_price": bar.high_price,
                    "low_price": bar.low_price,
                    "close_price": bar.close_price,
                    "extra": bar.extra
                }
                data_dicts.append(data)
            
            # 使用 INSERT ... ON CONFLICT 实现去重
            stmt = pg_insert(MysqlBarData).values(data_dicts)
            stmt = stmt.on_conflict_do_update(
                index_elements=['symbol', 'exchange', 'interval', 'datetime'],
                set_={
                    'volume': stmt.excluded.volume,
                    'turnover': stmt.excluded.turnover,
                    'open_interest': stmt.excluded.open_interest,
                    'open_price': stmt.excluded.open_price,
                    'high_price': stmt.excluded.high_price,
                    'low_price': stmt.excluded.low_price,
                    'close_price': stmt.excluded.close_price,
                }
            )
            session.execute(stmt)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"保存失败: {e}")
            return False
        finally:
            session.close()
    
    def get_bar_overview(self) -> list[BarOverview]:
        """使用 PostgreSQL 的 GROUP BY 和聚合函数"""
        session = self.Session()
        try:
            query = session.query(
                PostgresBarData.symbol,
                PostgresBarData.exchange,
                PostgresBarData.interval,
                func.count(PostgresBarData.id).label('count'),
                func.min(PostgresBarData.datetime).label('start'),
                func.max(PostgresBarData.datetime).label('end')
            ).group_by(
                PostgresBarData.symbol,
                PostgresBarData.exchange,
                PostgresBarData.interval
            )
            
            overviews = []
            for row in query:
                overview = BarOverview(
                    symbol=row.symbol,
                    exchange=Exchange(row.exchange),
                    interval=Interval(row.interval),
                    count=row.count,
                    start=row.start,
                    end=row.end
                )
                overviews.append(overview)
            
            return overviews
        finally:
            session.close()
```

### 2.4 数据库性能对比

| 特性 | SQLite | MySQL | PostgreSQL |
|------|--------|-------|------------|
| **适用场景** | 单机、开发、测试 | 中小规模、多用户 | 大规模、高并发 |
| **并发性能** | 低（写操作串行） | 中等（支持多连接） | 高（MVCC机制） |
| **数据类型** | 基础类型 | 丰富 | 非常丰富（JSONB、数组等） |
| **索引支持** | 基础索引 | 全文索引、空间索引 | 全文、GiST、GIN等 |
| **备份恢复** | 文件复制 | mysqldump、二进制日志 | pg_dump、WAL归档 |
| **配置复杂度** | 简单（零配置） | 中等 | 较复杂 |
| **内存占用** | 低 | 中等 | 较高 |

---

## 3. 数据存储机制深度剖析

### 3.1 时区处理机制

vn.py 统一使用 UTC 存储时间戳，在读取时转换为用户配置的时区。

```python
from vnpy.trader.utility import ZoneInfo

# 从配置读取时区
DB_TZ = ZoneInfo(SETTINGS["database.timezone"])

def convert_tz(dt: datetime) -> datetime:
    """
    将 datetime 转换为数据库时区（UTC）。
    
    存储流程：
    1. 接收带时区的时间（如 Asia/Shanghai）
    2. 转换为 UTC
    3. 去除时区信息存储
    
    读取流程：
    1. 从数据库读取 UTC 时间
    2. 转换为配置的时区
    3. 返回给应用层
    """
    dt = dt.astimezone(DB_TZ)
    return dt.replace(tzinfo=None)

# 使用示例
from datetime import datetime
from zoneinfo import ZoneInfo

# 创建上海时区的时间
dt_shanghai = datetime(2024, 1, 1, 9, 30, tzinfo=ZoneInfo("Asia/Shanghai"))

# 转换为 UTC 存储
dt_utc = convert_tz(dt_shanghai)
# dt_utc = datetime(2024, 1, 1, 1, 30)  # UTC 时间

# 从数据库读取时转换回来
dt_read = datetime.fromtimestamp(dt_utc.timestamp(), DB_TZ)
```

### 3.2 数据去重机制

vn.py 使用 **upsert**（更新或插入）机制确保数据的唯一性，避免重复存储。

```python
# Peewee 的 upsert 实现
with self.db.atomic():
    for c in chunked(data, 50):  # 每批50条
        DbBarData.insert_many(c).on_conflict_replace().execute()

# 等效的 SQL 语句
"""
INSERT INTO bar_data (symbol, exchange, datetime, ...)
VALUES (?, ?, ?, ...)
ON CONFLICT(symbol, exchange, datetime) DO UPDATE SET
    volume = EXCLUDED.volume,
    turnover = EXCLUDED.turnover,
    ...
"""
```

### 3.3 数据汇总机制

vn.py 维护独立的汇总表（Overview），记录每个标的的数据统计信息，避免频繁查询主表。

```python
def init_bar_overview(self) -> None:
    """初始化或重建 K 线汇总表"""
    s: ModelSelect = (
        DbBarData.select(
            DbBarData.symbol,
            DbBarData.exchange,
            DbBarData.interval,
            fn.COUNT(DbBarData.id).alias("count")
        ).group_by(
            DbBarData.symbol,
            DbBarData.exchange,
            DbBarData.interval
        )
    )
    
    for data in s:
        overview: DbBarOverview = DbBarOverview()
        overview.symbol = data.symbol
        overview.exchange = data.exchange
        overview.interval = data.interval
        overview.count = data.count
        
        # 查找最早和最晚的数据时间
        start_bar: DbBarData = (
            DbBarData.select()
            .where(
                (DbBarData.symbol == data.symbol)
                & (DbBarData.exchange == data.exchange)
                & (DbBarData.interval == data.interval)
            )
            .order_by(DbBarData.datetime.asc())
            .first()
        )
        overview.start = start_bar.datetime
        
        end_bar: DbBarData = (
            DbBarData.select()
            .where(
                (DbBarData.symbol == data.symbol)
                & (DbBarData.exchange == data.exchange)
                & (DbBarData.interval == data.interval)
            )
            .order_by(DbBarData.datetime.desc())
            .first()
        )
        overview.end = end_bar.datetime
        
        overview.save()
```

### 3.4 流式数据更新

对于实时流式数据，vn.py 优化了汇总表的更新策略。

```python
def save_bar_data(self, bars: list[BarData], stream: bool = False) -> bool:
    """保存 K 线数据，支持流式更新"""
    # ... 保存主表数据 ...
    
    # 更新汇总表
    overview: DbBarOverview = DbBarOverview.get_or_none(
        DbBarOverview.symbol == symbol,
        DbBarOverview.exchange == exchange.value,
        DbBarOverview.interval == interval.value,
    )
    
    if not overview:
        # 首次保存，创建新记录
        overview = DbBarOverview()
        overview.symbol = symbol
        overview.exchange = exchange.value
        overview.interval = interval.value
        overview.start = bars[0].datetime
        overview.end = bars[-1].datetime
        overview.count = len(bars)
    elif stream:
        # 流式更新：只更新结束时间和计数
        overview.end = bars[-1].datetime
        overview.count += len(bars)
    else:
        # 批量更新：重新计算统计信息
        overview.start = min(bars[0].datetime, overview.start)
        overview.end = max(bars[-1].datetime, overview.end)
        
        # 统计总数
        s: ModelSelect = DbBarData.select().where(
            (DbBarData.symbol == symbol)
            & (DbBarData.exchange == exchange.value)
            & (DbBarData.interval == interval.value)
        )
        overview.count = s.count()
    
    overview.save()
    return True
```

---

## 4. 数据查询优化策略

### 4.1 索引优化

合理的索引设计是提升查询性能的关键。

#### 4.1.1 复合索引设计

```python
# K线数据表的复合索引
class DbBarData(Model):
    # ... 字段定义 ...
    
    class Meta:
        database: SqliteDatabase = db
        # 复合索引：symbol + exchange + interval + datetime
        indexes: tuple = ((("symbol", "exchange", "interval", "datetime"), True),)

# 为什么这样设计？
# 1. symbol、exchange、interval 是等值查询条件，放在前面
# 2. datetime 是范围查询条件，放在最后
# 3. True 表示唯一索引，防止重复数据

# 查询示例（能充分利用索引）
DbBarData.select().where(
    (DbBarData.symbol == "IF2602") &      # 等值查询
    (DbBarData.exchange == "CFFEX") &      # 等值查询
    (DbBarData.interval == "1m") &         # 等值查询
    (DbBarData.datetime >= start) &       # 范围查询
    (DbBarData.datetime <= end)           # 范围查询
)

# 错误示例（无法充分利用索引）
DbBarData.select().where(
    (DbBarData.datetime >= start) &       # 范围查询在前面，索引失效
    (DbBarData.symbol == "IF2602")
)
```

#### 4.1.2 部分索引

对于大量数据，可以只对活跃数据创建索引。

```python
# PostgreSQL 部分索引示例
class PostgresBarData(Base):
    # ... 字段定义 ...
    
    __table_args__ = (
        # 只对最近一年的数据创建索引
        Index(
            'idx_bar_recent',
            'symbol', 'exchange', 'datetime',
            postgresql_where="datetime > now() - interval '1 year'"
        ),
    )
```

#### 4.1.3 索引维护

```python
def rebuild_indexes(self):
    """重建索引（适用于数据大量更新后）"""
    session = self.Session()
    try:
        # SQLite
        session.execute("REINDEX")
        
        # MySQL
        session.execute("OPTIMIZE TABLE bar_data")
        
        # PostgreSQL
        session.execute("REINDEX TABLE bar_data")
        
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"重建索引失败: {e}")
    finally:
        session.close()
```

### 4.2 查询优化技巧

#### 4.2.1 只查询必要字段

```python
# 优化前：查询所有字段
bars = DbBarData.select().where(
    (DbBarData.symbol == symbol) &
    (DbBarData.datetime >= start)
)

# 优化后：只查询需要的字段
bars = DbBarData.select(
    DbBarData.symbol,
    DbBarData.datetime,
    DbBarData.close_price
).where(
    (DbBarData.symbol == symbol) &
    (DbBarData.datetime >= start)
)
```

#### 4.2.2 分页查询

```python
def load_bar_data_paginated(
    self,
    symbol: str,
    exchange: Exchange,
    interval: Interval,
    start: datetime,
    end: datetime,
    page_size: int = 1000
) -> list[BarData]:
    """分页加载 K 线数据"""
    all_bars = []
    offset = 0
    
    while True:
        s: ModelSelect = (
            DbBarData.select()
            .where(
                (DbBarData.symbol == symbol) &
                (DbBarData.exchange == exchange.value) &
                (DbBarData.interval == interval.value) &
                (DbBarData.datetime >= start) &
                (DbBarData.datetime <= end)
            )
            .order_by(DbBarData.datetime)
            .limit(page_size)
            .offset(offset)
        )
        
        batch = list(s)
        if not batch:
            break
        
        all_bars.extend(batch)
        offset += page_size
        
        # 如果返回的数据少于页大小，说明已经是最后一页
        if len(batch) < page_size:
            break
    
    return [self._convert_to_bar_data(b) for b in all_bars]
```

#### 4.2.3 聚合查询优化

```python
def get_bar_statistics(
    self,
    symbol: str,
    exchange: Exchange,
    interval: Interval,
    start: datetime,
    end: datetime
) -> dict:
    """获取 K 线统计数据"""
    s: ModelSelect = (
        DbBarData.select(
            fn.COUNT(DbBarData.id).alias("count"),
            fn.AVG(DbBarData.close_price).alias("avg_close"),
            fn.MIN(DbBarData.low_price).alias("min_low"),
            fn.MAX(DbBarData.high_price).alias("max_high"),
            fn.SUM(DbBarData.volume).alias("total_volume")
        )
        .where(
            (DbBarData.symbol == symbol) &
            (DbBarData.exchange == exchange.value) &
            (DbBarData.interval == interval.value) &
            (DbBarData.datetime >= start) &
            (DbBarData.datetime <= end)
        )
    )
    
    result = s.first()
    return {
        "count": result.count,
        "avg_close": result.avg_close,
        "min_low": result.min_low,
        "max_high": result.max_high,
        "total_volume": result.total_volume,
    }
```

### 4.3 缓存策略

#### 4.3.1 应用层缓存

```python
from functools import lru_cache
from datetime import timedelta
import time

class CachedDatabase(BaseDatabase):
    """带缓存的数据库实现"""
    
    def __init__(self, database: BaseDatabase):
        self.database = database
        self._cache = {}
        self._cache_ttl = {}
    
    def load_bar_data(
        self,
        symbol: str,
        exchange: Exchange,
        interval: Interval,
        start: datetime,
        end: datetime
    ) -> list[BarData]:
        """带缓存的 K 线数据加载"""
        cache_key = f"{symbol}_{exchange}_{interval}_{start}_{end}"
        
        # 检查缓存
        if cache_key in self._cache:
            cache_time = self._cache_ttl[cache_key]
            if time.time() - cache_time < 3600:  # 缓存1小时
                return self._cache[cache_key]
        
        # 从数据库加载
        bars = self.database.load_bar_data(
            symbol, exchange, interval, start, end
        )
        
        # 更新缓存
        self._cache[cache_key] = bars
        self._cache_ttl[cache_key] = time.time()
        
        # 限制缓存大小
        if len(self._cache) > 100:
            oldest_key = min(self._cache_ttl, key=self._cache_ttl.get)
            del self._cache[oldest_key]
            del self._cache_ttl[oldest_key]
        
        return bars
    
    def save_bar_data(self, bars: list[BarData], stream: bool = False) -> bool:
        """保存数据时清除相关缓存"""
        if not bars:
            return False
        
        bar = bars[0]
        cache_key = f"{bar.symbol}_{bar.exchange}_{bar.interval}_*"
        
        # 清除匹配的缓存
        keys_to_delete = [
            k for k in self._cache.keys()
            if k.startswith(cache_key.rsplit('_', 2)[0])
        ]
        for key in keys_to_delete:
            del self._cache[key]
            del self._cache_ttl[key]
        
        return self.database.save_bar_data(bars, stream)
```

#### 4.3.2 Redis 缓存

```python
import redis
import pickle
from datetime import timedelta

class RedisCachedDatabase(BaseDatabase):
    """使用 Redis 缓存的数据库实现"""
    
    def __init__(self, database: BaseDatabase, redis_host="localhost", redis_port=6379):
        self.database = database
        self.redis = redis.Redis(
            host=redis_host,
            port=redis_port,
            decode_responses=False
        )
    
    def _get_cache_key(self, symbol: str, exchange: Exchange, 
                       interval: Interval, start: datetime, end: datetime) -> str:
        return f"bar:{symbol}:{exchange}:{interval}:{start}:{end}"
    
    def load_bar_data(
        self,
        symbol: str,
        exchange: Exchange,
        interval: Interval,
        start: datetime,
        end: datetime
    ) -> list[BarData]:
        """从 Redis 缓存或数据库加载"""
        cache_key = self._get_cache_key(symbol, exchange, interval, start, end)
        
        # 尝试从缓存获取
        cached_data = self.redis.get(cache_key)
        if cached_data:
            return pickle.loads(cached_data)
        
        # 从数据库加载
        bars = self.database.load_bar_data(
            symbol, exchange, interval, start, end
        )
        
        # 写入缓存（1小时过期）
        self.redis.setex(
            cache_key,
            timedelta(hours=1),
            pickle.dumps(bars)
        )
        
        return bars
    
    def save_bar_data(self, bars: list[BarData], stream: bool = False) -> bool:
        """保存数据时清除缓存"""
        result = self.database.save_bar_data(bars, stream)
        
        if result and bars:
            bar = bars[0]
            pattern = f"bar:{bar.symbol}:{bar.exchange}:{bar.interval}:*"
            
            # 删除匹配的所有缓存键
            for key in self.redis.scan_iter(pattern):
                self.redis.delete(key)
        
        return result
```

### 4.4 批量操作优化

#### 4.4.1 批量插入

```python
def save_bar_data_batch(
    self,
    bars: list[BarData],
    batch_size: int = 1000
) -> bool:
    """批量插入 K 线数据"""
    if not bars:
        return False
    
    bar = bars[0]
    
    # 分批处理
    for i in range(0, len(bars), batch_size):
        batch = bars[i:i + batch_size]
        
        data_dicts = []
        for bar in batch:
            bar.datetime = convert_tz(bar.datetime)
            d = bar.__dict__
            d["exchange"] = d["exchange"].value
            d["interval"] = d["interval"].value
            d.pop("gateway_name")
            d.pop("vt_symbol")
            d.pop("extra", None)
            data_dicts.append(d)
        
        # 使用事务批量插入
        with self.db.atomic():
            for c in chunked(data_dicts, 50):
                DbBarData.insert_many(c).on_conflict_replace().execute()
    
    return True
```

#### 4.4.2 批量删除

```python
def delete_bar_data_batch(
    self,
    symbols: list[str],
    exchanges: list[Exchange],
    intervals: list[Interval]
) -> int:
    """批量删除 K 线数据"""
    total_deleted = 0
    
    with self.db.atomic():
        for symbol in symbols:
            for exchange in exchanges:
                for interval in intervals:
                    count = DbBarData.delete().where(
                        (DbBarData.symbol == symbol) &
                        (DbBarData.exchange == exchange.value) &
                        (DbBarData.interval == interval.value)
                    ).execute()
                    
                    # 删除汇总数据
                    DbBarOverview.delete().where(
                        (DbBarOverview.symbol == symbol) &
                        (DbBarOverview.exchange == exchange.value) &
                        (DbBarOverview.interval == interval.value)
                    ).execute()
                    
                    total_deleted += count
    
    return total_deleted
```

---

## 5. 数据导入导出完整方案

### 5.1 CSV 格式

#### 5.1.1 导出为 CSV

```python
import csv
from datetime import datetime
from pathlib import Path

def export_bars_to_csv(
    database: BaseDatabase,
    symbol: str,
    exchange: Exchange,
    interval: Interval,
    start: datetime,
    end: datetime,
    output_path: str
) -> int:
    """
    导出 K 线数据到 CSV 文件。
    
    参数:
        database: 数据库实例
        symbol: 交易品种代码
        exchange: 交易所
        interval: K线周期
        start: 开始时间
        end: 结束时间
        output_path: 输出文件路径
    
    返回:
        int: 导出的数据条数
    """
    # 加载数据
    bars = database.load_bar_data(
        symbol, exchange, interval, start, end
    )
    
    if not bars:
        print("没有数据可导出")
        return 0
    
    # 确保输出目录存在
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 写入 CSV
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # 写入表头
        headers = [
            'datetime', 'symbol', 'exchange', 'interval',
            'open_price', 'high_price', 'low_price', 'close_price',
            'volume', 'turnover', 'open_interest'
        ]
        writer.writerow(headers)
        
        # 写入数据
        for bar in bars:
            row = [
                bar.datetime.strftime('%Y-%m-%d %H:%M:%S'),
                bar.symbol,
                bar.exchange.value,
                bar.interval.value,
                bar.open_price,
                bar.high_price,
                bar.low_price,
                bar.close_price,
                bar.volume,
                bar.turnover,
                bar.open_interest
            ]
            writer.writerow(row)
    
    print(f"成功导出 {len(bars)} 条数据到 {output_path}")
    return len(bars)


# 使用示例
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.database import get_database

database = get_database()
export_bars_to_csv(
    database=database,
    symbol="IF2602",
    exchange=Exchange.CFFEX,
    interval=Interval.MINUTE,
    start=datetime(2024, 1, 1),
    end=datetime(2024, 12, 31),
    output_path="data/IF2602_1m_2024.csv"
)
```

#### 5.1.2 从 CSV 导入

```python
def import_bars_from_csv(
    database: BaseDatabase,
    csv_path: str,
    symbol: str,
    exchange: Exchange,
    interval: Interval
) -> int:
    """
    从 CSV 文件导入 K 线数据。
    
    参数:
        database: 数据库实例
        csv_path: CSV 文件路径
        symbol: 交易品种代码
        exchange: 交易所
        interval: K线周期
    
    返回:
        int: 导入的数据条数
    """
    csv_path = Path(csv_path)
    if not csv_path.exists():
        print(f"文件不存在: {csv_path}")
        return 0
    
    bars = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            try:
                bar = BarData(
                    symbol=symbol,
                    exchange=exchange,
                    interval=interval,
                    datetime=datetime.strptime(row['datetime'], '%Y-%m-%d %H:%M:%S'),
                    open_price=float(row['open_price']),
                    high_price=float(row['high_price']),
                    low_price=float(row['low_price']),
                    close_price=float(row['close_price']),
                    volume=float(row['volume']),
                    turnover=float(row['turnover']),
                    open_interest=float(row['open_interest']),
                    gateway_name="CSV"
                )
                bars.append(bar)
            except (ValueError, KeyError) as e:
                print(f"解析失败: {row}, 错误: {e}")
                continue
    
    if not bars:
        print("没有有效数据可导入")
        return 0
    
    # 保存到数据库（分批）
    batch_size = 1000
    total_imported = 0
    
    for i in range(0, len(bars), batch_size):
        batch = bars[i:i + batch_size]
        result = database.save_bar_data(batch)
        if result:
            total_imported += len(batch)
            print(f"已导入 {total_imported}/{len(bars)} 条数据")
    
    print(f"成功导入 {total_imported} 条数据")
    return total_imported


# 使用示例
import_bars_from_csv(
    database=database,
    csv_path="data/IF2602_1m_2024.csv",
    symbol="IF2602",
    exchange=Exchange.CFFEX,
    interval=Interval.MINUTE
)
```

### 5.2 Excel 格式

```python
import pandas as pd
from vnpy.trader.object import BarData

def export_bars_to_excel(
    database: BaseDatabase,
    symbol: str,
    exchange: Exchange,
    interval: Interval,
    start: datetime,
    end: datetime,
    output_path: str
) -> int:
    """导出 K 线数据到 Excel 文件"""
    # 加载数据
    bars = database.load_bar_data(
        symbol, exchange, interval, start, end
    )
    
    if not bars:
        print("没有数据可导出")
        return 0
    
    # 转换为 DataFrame
    data = {
        'datetime': [bar.datetime for bar in bars],
        'symbol': [bar.symbol for bar in bars],
        'exchange': [bar.exchange.value for bar in bars],
        'interval': [bar.interval.value for bar in bars],
        'open_price': [bar.open_price for bar in bars],
        'high_price': [bar.high_price for bar in bars],
        'low_price': [bar.low_price for bar in bars],
        'close_price': [bar.close_price for bar in bars],
        'volume': [bar.volume for bar in bars],
        'turnover': [bar.turnover for bar in bars],
        'open_interest': [bar.open_interest for bar in bars],
    }
    df = pd.DataFrame(data)
    
    # 写入 Excel
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='K线数据')
        
        # 添加统计信息
        stats = {
            '统计项': ['数据条数', '开始时间', '结束时间', 
                      '最高价', '最低价', '平均成交价', '总成交量'],
            '值': [
                len(bars),
                bars[0].datetime,
                bars[-1].datetime,
                max(bar.high_price for bar in bars),
                min(bar.low_price for bar in bars),
                sum(bar.close_price for bar in bars) / len(bars),
                sum(bar.volume for bar in bars)
            ]
        }
        stats_df = pd.DataFrame(stats)
        stats_df.to_excel(writer, index=False, sheet_name='统计信息')
    
    print(f"成功导出 {len(bars)} 条数据到 {output_path}")
    return len(bars)


def import_bars_from_excel(
    database: BaseDatabase,
    excel_path: str,
    symbol: str,
    exchange: Exchange,
    interval: Interval,
    sheet_name: str = 'K线数据'
) -> int:
    """从 Excel 文件导入 K 线数据"""
    excel_path = Path(excel_path)
    if not excel_path.exists():
        print(f"文件不存在: {excel_path}")
        return 0
    
    # 读取 Excel
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    
    bars = []
    for _, row in df.iterrows():
        try:
            bar = BarData(
                symbol=symbol,
                exchange=exchange,
                interval=interval,
                datetime=pd.to_datetime(row['datetime']).to_pydatetime(),
                open_price=float(row['open_price']),
                high_price=float(row['high_price']),
                low_price=float(row['low_price']),
                close_price=float(row['close_price']),
                volume=float(row['volume']),
                turnover=float(row['turnover']),
                open_interest=float(row['open_interest']),
                gateway_name="Excel"
            )
            bars.append(bar)
        except (ValueError, KeyError) as e:
            print(f"解析失败: {row}, 错误: {e}")
            continue
    
    # 保存到数据库
    batch_size = 1000
    total_imported = 0
    
    for i in range(0, len(bars), batch_size):
        batch = bars[i:i + batch_size]
        result = database.save_bar_data(batch)
        if result:
            total_imported += len(batch)
            print(f"已导入 {total_imported}/{len(bars)} 条数据")
    
    print(f"成功导入 {total_imported} 条数据")
    return total_imported
```

### 5.3 JSON 格式

```python
import json
from datetime import datetime, date

def export_bars_to_json(
    database: BaseDatabase,
    symbol: str,
    exchange: Exchange,
    interval: Interval,
    start: datetime,
    end: datetime,
    output_path: str
) -> int:
    """导出 K 线数据到 JSON 文件"""
    bars = database.load_bar_data(
        symbol, exchange, interval, start, end
    )
    
    if not bars:
        print("没有数据可导出")
        return 0
    
    # 自定义 JSON 编码器
    class BarDataEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, datetime):
                return obj.strftime('%Y-%m-%d %H:%M:%S')
            if isinstance(obj, date):
                return obj.strftime('%Y-%m-%d')
            return super().default(obj)
    
    # 转换为字典列表
    data = [{
        'datetime': bar.datetime,
        'symbol': bar.symbol,
        'exchange': bar.exchange.value,
        'interval': bar.interval.value,
        'open_price': bar.open_price,
        'high_price': bar.high_price,
        'low_price': bar.low_price,
        'close_price': bar.close_price,
        'volume': bar.volume,
        'turnover': bar.turnover,
        'open_interest': bar.open_interest,
    } for bar in bars]
    
    # 写入 JSON
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, cls=BarDataEncoder)
    
    print(f"成功导出 {len(bars)} 条数据到 {output_path}")
    return len(bars)


def import_bars_from_json(
    database: BaseDatabase,
    json_path: str,
    symbol: str,
    exchange: Exchange,
    interval: Interval
) -> int:
    """从 JSON 文件导入 K 线数据"""
    json_path = Path(json_path)
    if not json_path.exists():
        print(f"文件不存在: {json_path}")
        return 0
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    bars = []
    for item in data:
        try:
            bar = BarData(
                symbol=symbol,
                exchange=exchange,
                interval=interval,
                datetime=datetime.strptime(item['datetime'], '%Y-%m-%d %H:%M:%S'),
                open_price=float(item['open_price']),
                high_price=float(item['high_price']),
                low_price=float(item['low_price']),
                close_price=float(item['close_price']),
                volume=float(item['volume']),
                turnover=float(item['turnover']),
                open_interest=float(item['open_interest']),
                gateway_name="JSON"
            )
            bars.append(bar)
        except (ValueError, KeyError) as e:
            print(f"解析失败: {item}, 错误: {e}")
            continue
    
    # 保存到数据库
    batch_size = 1000
    total_imported = 0
    
    for i in range(0, len(bars), batch_size):
        batch = bars[i:i + batch_size]
        result = database.save_bar_data(batch)
        if result:
            total_imported += len(batch)
            print(f"已导入 {total_imported}/{len(bars)} 条数据")
    
    print(f"成功导入 {total_imported} 条数据")
    return total_imported
```

### 5.4 Parquet 格式（推荐）

Parquet 是列式存储格式，压缩率高，查询速度快，特别适合大数据场景。

```python
import pyarrow as pa
import pyarrow.parquet as pq

def export_bars_to_parquet(
    database: BaseDatabase,
    symbol: str,
    exchange: Exchange,
    interval: Interval,
    start: datetime,
    end: datetime,
    output_path: str,
    compression: str = "snappy"
) -> int:
    """导出 K 线数据到 Parquet 文件"""
    bars = database.load_bar_data(
        symbol, exchange, interval, start, end
    )
    
    if not bars:
        print("没有数据可导出")
        return 0
    
    # 转换为 PyArrow Table
    data = {
        'datetime': [bar.datetime for bar in bars],
        'symbol': [bar.symbol for bar in bars],
        'exchange': [bar.exchange.value for bar in bars],
        'interval': [bar.interval.value for bar in bars],
        'open_price': [bar.open_price for bar in bars],
        'high_price': [bar.high_price for bar in bars],
        'low_price': [bar.low_price for bar in bars],
        'close_price': [bar.close_price for bar in bars],
        'volume': [bar.volume for bar in bars],
        'turnover': [bar.turnover for bar in bars],
        'open_interest': [bar.open_interest for bar in bars],
    }
    
    table = pa.table(data)
    
    # 写入 Parquet
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    pq.write_table(
        table,
        output_path,
        compression=compression,
        row_group_size=10000
    )
    
    print(f"成功导出 {len(bars)} 条数据到 {output_path}")
    return len(bars)


def import_bars_from_parquet(
    database: BaseDatabase,
    parquet_path: str,
    symbol: str,
    exchange: Exchange,
    interval: Interval
) -> int:
    """从 Parquet 文件导入 K 线数据"""
    parquet_path = Path(parquet_path)
    if not parquet_path.exists():
        print(f"文件不存在: {parquet_path}")
        return 0
    
    # 读取 Parquet
    table = pq.read_table(parquet_path)
    df = table.to_pandas()
    
    bars = []
    for _, row in df.iterrows():
        try:
            bar = BarData(
                symbol=symbol,
                exchange=exchange,
                interval=interval,
                datetime=pd.to_datetime(row['datetime']).to_pydatetime(),
                open_price=float(row['open_price']),
                high_price=float(row['high_price']),
                low_price=float(row['low_price']),
                close_price=float(row['close_price']),
                volume=float(row['volume']),
                turnover=float(row['turnover']),
                open_interest=float(row['open_interest']),
                gateway_name="Parquet"
            )
            bars.append(bar)
        except (ValueError, KeyError) as e:
            print(f"解析失败: {row}, 错误: {e}")
            continue
    
    # 保存到数据库
    batch_size = 1000
    total_imported = 0
    
    for i in range(0, len(bars), batch_size):
        batch = bars[i:i + batch_size]
        result = database.save_bar_data(batch)
        if result:
            total_imported += len(batch)
            print(f"已导入 {total_imported}/{len(bars)} 条数据")
    
    print(f"成功导入 {total_imported} 条数据")
    return total_imported
```

---

## 6. 数据备份与恢复策略

### 6.1 SQLite 备份与恢复

#### 6.1.1 文件复制备份

```python
import shutil
from datetime import datetime
from pathlib import Path

def backup_sqlite_database(
    db_path: str,
    backup_dir: str = "backups"
) -> str:
    """备份 SQLite 数据库文件"""
    db_path = Path(db_path)
    backup_dir = Path(backup_dir)
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成备份文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = backup_dir / f"{db_path.stem}_{timestamp}{db_path.suffix}"
    
    # 复制文件
    shutil.copy2(db_path, backup_path)
    print(f"备份成功: {backup_path}")
    return str(backup_path)


def restore_sqlite_database(
    backup_path: str,
    db_path: str
) -> bool:
    """恢复 SQLite 数据库"""
    backup_path = Path(backup_path)
    db_path = Path(db_path)
    
    if not backup_path.exists():
        print(f"备份文件不存在: {backup_path}")
        return False
    
    # 备份当前数据库（避免覆盖）
    if db_path.exists():
        current_backup = backup_path.parent / f"{db_path.stem}_before_restore{db_path.suffix}"
        shutil.copy2(db_path, current_backup)
        print(f"已备份当前数据库: {current_backup}")
    
    # 恢复数据
    shutil.copy2(backup_path, db_path)
    print(f"恢复成功: {db_path}")
    return True
```

#### 6.1.2 SQL 转储备份

```python
import sqlite3

def export_sqlite_to_sql(db_path: str, output_sql: str) -> bool:
    """导出 SQLite 数据库为 SQL 文件"""
    db_path = Path(db_path)
    output_sql = Path(output_sql)
    output_sql.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        conn = sqlite3.connect(db_path)
        
        with open(output_sql, 'w', encoding='utf-8') as f:
            # 导出表结构和数据
            for line in conn.iterdump():
                f.write(f"{line}\n")
        
        conn.close()
        print(f"导出成功: {output_sql}")
        return True
    except Exception as e:
        print(f"导出失败: {e}")
        return False


def import_sqlite_from_sql(sql_file: str, db_path: str) -> bool:
    """从 SQL 文件恢复 SQLite 数据库"""
    sql_file = Path(sql_file)
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        conn = sqlite3.connect(db_path)
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_script = f.read()
            conn.executescript(sql_script)
        
        conn.commit()
        conn.close()
        print(f"恢复成功: {db_path}")
        return True
    except Exception as e:
        print(f"恢复失败: {e}")
        return False
```

### 6.2 MySQL 备份与恢复

#### 6.2.1 使用 mysqldump

```python
import subprocess
from vnpy.trader.setting import SETTINGS

def backup_mysql(output_path: str) -> bool:
    """使用 mysqldump 备份 MySQL 数据库"""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    command = [
        "mysqldump",
        f"--host={SETTINGS['database.host']}",
        f"--port={SETTINGS['database.port']}",
        f"--user={SETTINGS['database.username']}",
        f"--password={SETTINGS['database.password']}",
        SETTINGS['database.database'],
        "--single-transaction",
        "--routines",
        "--triggers"
    ]
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            subprocess.run(
                command,
                stdout=f,
                check=True,
                text=True
            )
        print(f"备份成功: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"备份失败: {e}")
        return False


def restore_mysql(input_path: str) -> bool:
    """从 SQL 文件恢复 MySQL 数据库"""
    input_path = Path(input_path)
    
    if not input_path.exists():
        print(f"备份文件不存在: {input_path}")
        return False
    
    command = [
        "mysql",
        f"--host={SETTINGS['database.host']}",
        f"--port={SETTINGS['database.port']}",
        f"--user={SETTINGS['database.username']}",
        f"--password={SETTINGS['database.password']}",
        SETTINGS['database.database']
    ]
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            subprocess.run(
                command,
                stdin=f,
                check=True,
                text=True
            )
        print(f"恢复成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"恢复失败: {e}")
        return False
```

#### 6.2.2 使用 Python 导出导入

```python
import pandas as pd
from sqlalchemy import create_engine

def backup_mysql_to_csv(output_dir: str) -> bool:
    """将 MySQL 表导出为 CSV 文件"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建数据库连接
    db_url = (
        f"mysql+pymysql://{SETTINGS['database.username']}:"
        f"{SETTINGS['database.password']}@"
        f"{SETTINGS['database.host']}:{SETTINGS['database.port']}/"
        f"{SETTINGS['database.database']}"
    )
    engine = create_engine(db_url)
    
    # 导出每个表
    tables = ["bar_data", "tick_data", "bar_overview", "tick_overview"]
    
    for table in tables:
        try:
            df = pd.read_sql(f"SELECT * FROM {table}", engine)
            output_path = output_dir / f"{table}.csv"
            df.to_csv(output_path, index=False, encoding='utf-8')
            print(f"导出 {table}: {len(df)} 条记录")
        except Exception as e:
            print(f"导出 {table} 失败: {e}")
            return False
    
    print(f"备份完成: {output_dir}")
    return True


def restore_mysql_from_csv(input_dir: str) -> bool:
    """从 CSV 文件恢复 MySQL 表"""
    input_dir = Path(input_dir)
    
    # 创建数据库连接
    db_url = (
        f"mysql+pymysql://{SETTINGS['database.username']}:"
        f"{SETTINGS['database.password']}@"
        f"{SETTINGS['database.host']}:{SETTINGS['database.port']}/"
        f"{SETTINGS['database.database']}"
    )
    engine = create_engine(db_url)
    
    # 导入每个表
    tables = ["bar_data", "tick_data", "bar_overview", "tick_overview"]
    
    for table in tables:
        csv_path = input_dir / f"{table}.csv"
        if not csv_path.exists():
            print(f"文件不存在: {csv_path}")
            continue
        
        try:
            df = pd.read_csv(csv_path)
            df.to_sql(table, engine, if_exists='append', index=False)
            print(f"导入 {table}: {len(df)} 条记录")
        except Exception as e:
            print(f"导入 {table} 失败: {e}")
            return False
    
    print(f"恢复完成")
    return True
```

### 6.3 PostgreSQL 备份与恢复

```python
def backup_postgresql(output_path: str) -> bool:
    """使用 pg_dump 备份 PostgreSQL 数据库"""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    command = [
        "pg_dump",
        f"--host={SETTINGS['database.host']}",
        f"--port={SETTINGS['database.port']}",
        f"--username={SETTINGS['database.username']}",
        "--dbname", SETTINGS['database.database'],
        "--format=custom",
        f"--file={output_path}"
    ]
    
    try:
        subprocess.run(command, check=True)
        print(f"备份成功: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"备份失败: {e}")
        return False


def restore_postgresql(input_path: str) -> bool:
    """从备份文件恢复 PostgreSQL 数据库"""
    input_path = Path(input_path)
    
    if not input_path.exists():
        print(f"备份文件不存在: {input_path}")
        return False
    
    command = [
        "pg_restore",
        f"--host={SETTINGS['database.host']}",
        f"--port={SETTINGS['database.port']}",
        f"--username={SETTINGS['database.username']}",
        "--dbname", SETTINGS['database.database'],
        "--clean",
        "--if-exists",
        str(input_path)
    ]
    
    try:
        subprocess.run(command, check=True)
        print(f"恢复成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"恢复失败: {e}")
        return False
```

### 6.4 自动化备份脚本

```python
import schedule
import time
from datetime import datetime, timedelta

def auto_backup():
    """自动化备份任务"""
    print(f"开始备份: {datetime.now()}")
    
    # 创建备份目录
    backup_dir = Path(f"backups/{datetime.now().strftime('%Y%m%d')}")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # 根据数据库类型选择备份方式
    db_name = SETTINGS.get("database.name", "sqlite")
    
    if db_name == "sqlite":
        db_path = SETTINGS.get("database.database", "database.db")
        backup_sqlite_database(db_path, str(backup_dir))
    
    elif db_name == "mysql":
        backup_path = backup_dir / "mysql_backup.sql"
        backup_mysql(str(backup_path))
    
    elif db_name == "postgresql":
        backup_path = backup_dir / "postgresql_backup.dump"
        backup_postgresql(str(backup_path))
    
    # 清理旧备份（保留最近7天）
    cleanup_old_backups(backup_dir.parent, days=7)
    
    print(f"备份完成: {datetime.now()}")


def cleanup_old_backups(backup_dir: Path, days: int = 7):
    """清理旧的备份文件"""
    cutoff_time = datetime.now() - timedelta(days=days)
    
    for backup_path in backup_dir.iterdir():
        if backup_path.is_dir():
            # 检查目录修改时间
            stat = backup_path.stat()
            mtime = datetime.fromtimestamp(stat.st_mtime)
            
            if mtime < cutoff_time:
                shutil.rmtree(backup_path)
                print(f"删除旧备份: {backup_path}")


def schedule_backup(hour: int = 2, minute: int = 0):
    """定时备份"""
    schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(auto_backup)
    
    print(f"已设置每日 {hour:02d}:{minute:02d} 自动备份")
    
    while True:
        schedule.run_pending()
        time.sleep(60)


# 使用示例
if __name__ == "__main__":
    # 立即执行一次备份
    auto_backup()
    
    # 启动定时备份（每天凌晨2点）
    schedule_backup(hour=2, minute=0)
```

---

## 7. 大数据处理高级技巧

### 7.1 数据分片

#### 7.1.1 按时间分片

```python
from datetime import datetime, timedelta

def load_bars_in_chunks(
    database: BaseDatabase,
    symbol: str,
    exchange: Exchange,
    interval: Interval,
    start: datetime,
    end: datetime,
    chunk_size: int = 30
) -> list[BarData]:
    """分块加载 K 线数据（避免一次性加载过多数据）"""
    all_bars = []
    current_start = start
    
    while current_start <= end:
        current_end = min(
            current_start + timedelta(days=chunk_size),
            end
        )
        
        # 加载一个时间块的数据
        bars = database.load_bar_data(
            symbol, exchange, interval, current_start, current_end
        )
        all_bars.extend(bars)
        
        print(f"已加载 {len(bars)} 条数据 "
              f"({current_start} ~ {current_end})")
        
        current_start = current_end + timedelta(seconds=1)
    
    return all_bars


# 使用示例
bars = load_bars_in_chunks(
    database=database,
    symbol="IF2602",
    exchange=Exchange.CFFEX,
    interval=Interval.MINUTE,
    start=datetime(2020, 1, 1),
    end=datetime(2024, 12, 31),
    chunk_size=90  # 每90天加载一次
)
```

#### 7.1.2 按品种分片

```python
def export_all_symbols_to_parquet(
    database: BaseDatabase,
    output_dir: str,
    interval: Interval,
    start: datetime,
    end: datetime
) -> dict:
    """导出所有品种的 K 线数据（每个品种一个文件）"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 获取所有品种概览
    overviews = database.get_bar_overview()
    
    # 筛选指定周期和时间范围
    target_overviews = [
        o for o in overviews 
        if o.interval == interval and o.start <= end and o.end >= start
    ]
    
    stats = {
        "total_symbols": len(target_overviews),
        "exported": 0,
        "failed": 0,
        "symbols": []
    }
    
    for overview in target_overviews:
        symbol = overview.symbol
        exchange = overview.exchange
        
        # 加载数据
        bars = database.load_bar_data(
            symbol, exchange, interval, start, end
        )
        
        if not bars:
            continue
        
        # 导出为 Parquet
        try:
            output_path = output_dir / f"{symbol}_{exchange.value}.parquet"
            export_bars_to_parquet(
                database, symbol, exchange, interval,
                start, end, str(output_path)
            )
            stats["exported"] += 1
            stats["symbols"].append(symbol)
        except Exception as e:
            print(f"导出 {symbol} 失败: {e}")
            stats["failed"] += 1
    
    print(f"导出完成: 成功 {stats['exported']}, 失败 {stats['failed']}")
    return stats
```

### 7.2 数据压缩

```python
import gzip
import pickle
from pathlib import Path

def save_compressed_bars(
    bars: list[BarData],
    output_path: str,
    compression_level: int = 6
) -> bool:
    """保存压缩的 K 线数据"""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with gzip.open(output_path, 'wb', compresslevel=compression_level) as f:
            pickle.dump(bars, f, protocol=pickle.HIGHEST_PROTOCOL)
        
        original_size = len(pickle.dumps(bars))
        compressed_size = output_path.stat().st_size
        ratio = (1 - compressed_size / original_size) * 100
        
        print(f"保存成功: 原始 {original_size/1024:.2f}KB, "
              f"压缩 {compressed_size/1024:.2f}KB, "
              f"压缩率 {ratio:.1f}%")
        return True
    except Exception as e:
        print(f"保存失败: {e}")
        return False


def load_compressed_bars(input_path: str) -> list[BarData]:
    """加载压缩的 K 线数据"""
    input_path = Path(input_path)
    
    if not input_path.exists():
        print(f"文件不存在: {input_path}")
        return []
    
    try:
        with gzip.open(input_path, 'rb') as f:
            bars = pickle.load(f)
        print(f"加载成功: {len(bars)} 条数据")
        return bars
    except Exception as e:
        print(f"加载失败: {e}")
        return []
```

### 7.3 流式处理

```python
import pandas as pd
from typing import Iterator, Callable

def stream_bars_to_csv(
    database: BaseDatabase,
    symbol: str,
    exchange: Exchange,
    interval: Interval,
    start: datetime,
    end: datetime,
    output_path: str,
    batch_size: int = 1000,
    transform: Callable[[BarData], dict] = None
) -> int:
    """流式写入 K 线数据到 CSV（内存友好）"""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    total_count = 0
    first_batch = True
    
    current_start = start
    while current_start <= end:
        current_end = min(
            current_start + timedelta(days=30),
            end
        )
        
        # 加载一个批次的数据
        bars = database.load_bar_data(
            symbol, exchange, interval, current_start, current_end
        )
        
        if not bars:
            current_start = current_end + timedelta(seconds=1)
            continue
        
        # 转换为 DataFrame
        if transform:
            data = [transform(bar) for bar in bars]
        else:
            data = [{
                'datetime': bar.datetime,
                'open': bar.open_price,
                'high': bar.high_price,
                'low': bar.low_price,
                'close': bar.close_price,
                'volume': bar.volume
            } for bar in bars]
        
        df = pd.DataFrame(data)
        
        # 写入 CSV（追加模式）
        df.to_csv(
            output_path,
            mode='a' if not first_batch else 'w',
            header=first_batch,
            index=False
        )
        
        total_count += len(bars)
        first_batch = False
        current_start = current_end + timedelta(seconds=1)
        
        print(f"已处理 {total_count} 条数据")
    
    print(f"流式写入完成: {total_count} 条数据")
    return total_count


# 使用示例：自定义转换函数
def custom_transform(bar: BarData) -> dict:
    """自定义数据转换"""
    return {
        'time': bar.datetime.strftime('%Y-%m-%d %H:%M:%S'),
        'open': round(bar.open_price, 2),
        'high': round(bar.high_price, 2),
        'low': round(bar.low_price, 2),
        'close': round(bar.close_price, 2),
        'volume': int(bar.volume),
        'amount': bar.turnover
    }

stream_bars_to_csv(
    database=database,
    symbol="IF2602",
    exchange=Exchange.CFFEX,
    interval=Interval.MINUTE,
    start=datetime(2020, 1, 1),
    end=datetime(2024, 12, 31),
    output_path="data/IF2602_stream.csv",
    batch_size=1000,
    transform=custom_transform
)
```

### 7.4 并行处理

```python
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing

def process_symbol_task(args: tuple) -> dict:
    """单个品种的处理任务"""
    database, symbol, exchange, interval, start, end, output_dir = args
    
    try:
        # 加载数据
        bars = database.load_bar_data(
            symbol, exchange, interval, start, end
        )
        
        if not bars:
            return {"symbol": symbol, "status": "no_data"}
        
        # 导出为 Parquet
        output_path = Path(output_dir) / f"{symbol}_{exchange.value}.parquet"
        export_bars_to_parquet(
            database, symbol, exchange, interval,
            start, end, str(output_path)
        )
        
        return {
            "symbol": symbol,
            "status": "success",
            "count": len(bars)
        }
    except Exception as e:
        return {
            "symbol": symbol,
            "status": "failed",
            "error": str(e)
        }


def parallel_export_symbols(
    database: BaseDatabase,
    output_dir: str,
    interval: Interval,
    start: datetime,
    end: datetime,
    max_workers: int = None
) -> dict:
    """并行导出多个品种的数据"""
    if max_workers is None:
        max_workers = multiprocessing.cpu_count()
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 获取所有品种
    overviews = database.get_bar_overview()
    target_overviews = [
        o for o in overviews 
        if o.interval == interval and o.start <= end and o.end >= start
    ]
    
    # 准备任务列表
    tasks = [
        (database, o.symbol, o.exchange, interval, start, end, str(output_dir))
        for o in target_overviews
    ]
    
    stats = {
        "total": len(tasks),
        "success": 0,
        "failed": 0,
        "no_data": 0,
        "details": []
    }
    
    # 并行执行
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_symbol_task, task): task 
                  for task in tasks}
        
        for future in as_completed(futures):
            result = future.result()
            stats["details"].append(result)
            
            if result["status"] == "success":
                stats["success"] += 1
            elif result["status"] == "failed":
                stats["failed"] += 1
            elif result["status"] == "no_data":
                stats["no_data"] += 1
            
            print(f"处理 {result['symbol']}: {result['status']}")
    
    print(f"\n导出完成: 成功 {stats['success']}, "
          f"失败 {stats['failed']}, 无数据 {stats['no_data']}")
    return stats
```

---

## 8. 数据同步机制设计

### 8.1 增量同步

```python
from datetime import datetime, timedelta

class DataSync:
    """数据同步工具"""
    
    def __init__(self, source_db: BaseDatabase, target_db: BaseDatabase):
        self.source_db = source_db
        self.target_db = target_db
        self.sync_log = {}
    
    def sync_bars_incremental(
        self,
        symbol: str,
        exchange: Exchange,
        interval: Interval
    ) -> dict:
        """
        增量同步 K 线数据。
        
        策略：
        1. 查询目标数据库的最新数据时间
        2. 从源数据库加载该时间之后的数据
        3. 写入目标数据库
        """
        # 查询目标数据库的最新数据时间
        target_overviews = self.target_db.get_bar_overview()
        target_overview = next(
            (o for o in target_overviews 
             if o.symbol == symbol and o.exchange == exchange 
             and o.interval == interval),
            None
        )
        
        if target_overview:
            last_datetime = target_overview.end
            # 从第二天开始同步（避免重复）
            start_time = last_datetime + timedelta(seconds=1)
        else:
            # 目标数据库无数据，从很久以前开始
            start_time = datetime(2000, 1, 1)
        
        end_time = datetime.now()
        
        print(f"同步 {symbol} {exchange} {interval}: "
              f"{start_time} ~ {end_time}")
        
        # 从源数据库加载新数据
        new_bars = self.source_db.load_bar_data(
            symbol, exchange, interval, start_time, end_time
        )
        
        if not new_bars:
            print(f"没有新数据需要同步")
            return {
                "symbol": symbol,
                "added": 0,
                "start": start_time,
                "end": end_time
            }
        
        # 写入目标数据库
        result = self.target_db.save_bar_data(new_bars, stream=True)
        
        stats = {
            "symbol": symbol,
            "added": len(new_bars),
            "start": start_time,
            "end": end_time
        }
        
        print(f"同步完成: 新增 {len(new_bars)} 条数据")
        return stats
    
    def sync_all_bars_incremental(
        self,
        interval: Interval
    ) -> list[dict]:
        """增量同步所有品种的 K 线数据"""
        # 获取源数据库的所有品种
        source_overviews = self.source_db.get_bar_overview()
        target_symbols = [o.symbol for o in source_overviews if o.interval == interval]
        
        results = []
        for symbol in set(target_symbols):
            for overview in source_overviews:
                if overview.symbol == symbol and overview.interval == interval:
                    result = self.sync_bars_incremental(
                        symbol, overview.exchange, interval
                    )
                    results.append(result)
        
        total_added = sum(r["added"] for r in results)
        print(f"\n全部同步完成: 共新增 {total_added} 条数据")
        return results
```

### 8.2 全量同步

```python
def sync_bars_full(
    source_db: BaseDatabase,
    target_db: BaseDatabase,
    symbol: str,
    exchange: Exchange,
    interval: Interval
) -> dict:
    """
    全量同步 K 线数据。
    
    策略：
    1. 删除目标数据库中的现有数据
    2. 从源数据库加载全部数据
    3. 写入目标数据库
    """
    # 删除目标数据库的现有数据
    deleted_count = target_db.delete_bar_data(symbol, exchange, interval)
    print(f"已删除目标数据库中的 {deleted_count} 条数据")
    
    # 查询源数据库的数据范围
    source_overviews = source_db.get_bar_overview()
    source_overview = next(
        (o for o in source_overviews 
         if o.symbol == symbol and o.exchange == exchange 
         and o.interval == interval),
        None
    )
    
    if not source_overview:
        print("源数据库中无数据")
        return {"symbol": symbol, "added": 0}
    
    # 加载全部数据（分块加载避免内存溢出）
    all_bars = load_bars_in_chunks(
        source_db, symbol, exchange, interval,
        source_overview.start, source_overview.end,
        chunk_size=90
    )
    
    # 写入目标数据库（分批）
    batch_size = 1000
    total_added = 0
    
    for i in range(0, len(all_bars), batch_size):
        batch = all_bars[i:i + batch_size]
        result = target_db.save_bar_data(batch, stream=True)
        if result:
            total_added += len(batch)
            print(f"已同步 {total_added}/{len(all_bars)} 条数据")
    
    stats = {
        "symbol": symbol,
        "added": total_added,
        "start": source_overview.start,
        "end": source_overview.end
    }
    
    print(f"全量同步完成: 共 {total_added} 条数据")
    return stats
```

### 8.3 数据一致性检查

```python
def verify_data_consistency(
    source_db: BaseDatabase,
    target_db: BaseDatabase,
    symbol: str,
    exchange: Exchange,
    interval: Interval
) -> dict:
    """验证源数据库和目标数据库的数据一致性"""
    # 获取两个数据库的概览
    source_overviews = source_db.get_bar_overview()
    target_overviews = target_db.get_bar_overview()
    
    source_overview = next(
        (o for o in source_overviews 
         if o.symbol == symbol and o.exchange == exchange 
         and o.interval == interval),
        None
    )
    
    target_overview = next(
        (o for o in target_overviews 
         if o.symbol == symbol and o.exchange == exchange 
         and o.interval == interval),
        None
    )
    
    result = {
        "symbol": symbol,
        "exchange": exchange.value,
        "interval": interval.value,
        "source_count": 0,
        "target_count": 0,
        "count_match": False,
        "time_match": False,
        "sample_match": True
    }
    
    # 比较数据条数
    if source_overview:
        result["source_count"] = source_overview.count
        result["source_start"] = source_overview.start
        result["source_end"] = source_overview.end
    
    if target_overview:
        result["target_count"] = target_overview.count
        result["target_start"] = target_overview.start
        result["target_end"] = target_overview.end
    
    result["count_match"] = (result["source_count"] == result["target_count"])
    result["time_match"] = (
        result.get("source_start") == result.get("target_start") and
        result.get("source_end") == result.get("target_end")
    )
    
    # 抽样检查数据内容
    if result["source_count"] > 0 and result["target_count"] > 0:
        # 检查开头、中间、结尾各10条数据
        sample_times = []
        
        if source_overview and target_overview:
            total = min(source_overview.count, target_overview.count)
            sample_times.append(source_overview.start)
            
            if total > 20:
                mid_time = source_overview.start + (
                    source_overview.end - source_overview.start
                ) / 2
                sample_times.append(mid_time)
            
            sample_times.append(source_overview.end)
        
        for sample_time in sample_times:
            window_start = sample_time - timedelta(minutes=5)
            window_end = sample_time + timedelta(minutes=5)
            
            source_bars = source_db.load_bar_data(
                symbol, exchange, interval, window_start, window_end
            )
            target_bars = target_db.load_bar_data(
                symbol, exchange, interval, window_start, window_end
            )
            
            # 比较数据
            for s_bar, t_bar in zip(source_bars, target_bars):
                if (abs(s_bar.open_price - t_bar.open_price) > 0.01 or
                    abs(s_bar.close_price - t_bar.close_price) > 0.01):
                    result["sample_match"] = False
                    result["mismatch_at"] = s_bar.datetime
                    break
    
    return result
```

---

## 9. 完整代码示例集合

### 9.1 数据库操作完整示例

```python
"""
vn.py 数据库操作完整示例
涵盖：初始化、增删改查、数据导出、备份恢复等
"""

from datetime import datetime
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.database import get_database
from vnpy.trader.object import BarData, TickData

def main():
    """主函数"""
    # 1. 获取数据库实例
    database = get_database()
    print(f"使用数据库: {type(database).__name__}")
    
    # 2. 创建测试数据
    print("\n=== 创建测试数据 ===")
    test_bars = create_test_bars("IF2602", Exchange.CFFEX, Interval.MINUTE, 100)
    print(f"已创建 {len(test_bars)} 条测试数据")
    
    # 3. 保存数据到数据库
    print("\n=== 保存数据 ===")
    result = database.save_bar_data(test_bars)
    print(f"保存结果: {result}")
    
    # 4. 查询数据
    print("\n=== 查询数据 ===")
    start = datetime(2024, 1, 1)
    end = datetime(2024, 12, 31)
    bars = database.load_bar_data(
        "IF2602", Exchange.CFFEX, Interval.MINUTE, start, end
    )
    print(f"查询到 {len(bars)} 条数据")
    if bars:
        print(f"第一条: {bars[0].datetime}, 收盘价: {bars[0].close_price}")
        print(f"最后一条: {bars[-1].datetime}, 收盘价: {bars[-1].close_price}")
    
    # 5. 获取数据概览
    print("\n=== 数据概览 ===")
    overviews = database.get_bar_overview()
    print(f"共有 {len(overviews)} 个品种的数据")
    for overview in overviews[:5]:
        print(f"  {overview.symbol} {overview.exchange.value} {overview.interval.value}: "
              f"{overview.count} 条 ({overview.start} ~ {overview.end})")
    
    # 6. 导出数据
    print("\n=== 导出数据 ===")
    export_bars_to_csv(
        database, "IF2602", Exchange.CFFEX, Interval.MINUTE,
        start, end, "exports/IF2602_1m.csv"
    )
    export_bars_to_parquet(
        database, "IF2602", Exchange.CFFEX, Interval.MINUTE,
        start, end, "exports/IF2602_1m.parquet"
    )
    
    # 7. 备份数据库
    print("\n=== 备份数据库 ===")
    from vnpy.trader.setting import SETTINGS
    db_name = SETTINGS.get("database.name", "sqlite")
    
    if db_name == "sqlite":
        db_path = SETTINGS.get("database.database", "database.db")
        backup_sqlite_database(db_path, "backups")
    
    # 8. 数据同步示例
    print("\n=== 数据同步 ===")
    # 假设有另一个数据库实例
    # sync = DataSync(source_db, target_db)
    # sync.sync_bars_incremental("IF2602", Exchange.CFFEX, Interval.MINUTE)
    
    print("\n=== 完成 ===")


def create_test_bars(
    symbol: str,
    exchange: Exchange,
    interval: Interval,
    count: int
) -> list[BarData]:
    """创建测试 K 线数据"""
    import numpy as np
    
    bars = []
    base_price = 3500.0
    current_time = datetime(2024, 1, 1, 9, 30)
    
    for i in range(count):
        # 随机生成价格波动
        change = np.random.randn() * 10
        
        bar = BarData(
            symbol=symbol,
            exchange=exchange,
            interval=interval,
            datetime=current_time,
            open_price=base_price + change,
            high_price=base_price + change + abs(np.random.randn() * 5),
            low_price=base_price + change - abs(np.random.randn() * 5),
            close_price=base_price + change + np.random.randn() * 2,
            volume=np.random.randint(1000, 10000),
            turnover=np.random.randint(1000000, 10000000),
            open_interest=np.random.randint(10000, 50000),
            gateway_name="TEST"
        )
        
        bars.append(bar)
        base_price = bar.close_price
        
        # 更新时间
        if interval == Interval.MINUTE:
            current_time = current_time + timedelta(minutes=1)
        elif interval == Interval.HOUR:
            current_time = current_time + timedelta(hours=1)
        elif interval == Interval.DAILY:
            current_time = current_time + timedelta(days=1)
    
    return bars


if __name__ == "__main__":
    main()
```

### 9.2 数据迁移完整示例

```python
"""
vn.py 数据库迁移工具
支持：SQLite <-> MySQL <-> PostgreSQL 之间的数据迁移
"""

import sys
from datetime import datetime
from typing import Optional
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.database import BaseDatabase, get_database, convert_tz
from vnpy.trader.object import BarData, TickData

class DataMigrator:
    """数据迁移工具"""
    
    def __init__(self, source_db: BaseDatabase, target_db: BaseDatabase):
        self.source_db = source_db
        self.target_db = target_db
    
    def migrate_bar_data(
        self,
        symbol: str,
        exchange: Exchange,
        interval: Interval,
        batch_size: int = 1000
    ) -> dict:
        """迁移单个品种的 K 线数据"""
        print(f"\n开始迁移 {symbol} {exchange.value} {interval.value}")
        
        # 获取源数据库的数据范围
        source_overviews = self.source_db.get_bar_overview()
        source_overview = next(
            (o for o in source_overviews 
             if o.symbol == symbol and o.exchange == exchange 
             and o.interval == interval),
            None
        )
        
        if not source_overview:
            print("源数据库中无数据")
            return {"symbol": symbol, "migrated": 0}
        
        print(f"数据范围: {source_overview.start} ~ {source_overview.end}")
        print(f"数据条数: {source_overview.count}")
        
        # 分块加载数据
        from datetime import timedelta
        all_bars = load_bars_in_chunks(
            self.source_db, symbol, exchange, interval,
            source_overview.start, source_overview.end,
            chunk_size=30
        )
        
        # 分批写入目标数据库
        total_migrated = 0
        for i in range(0, len(all_bars), batch_size):
            batch = all_bars[i:i + batch_size]
            result = self.target_db.save_bar_data(batch)
            if result:
                total_migrated += len(batch)
                print(f"已迁移 {total_migrated}/{len(all_bars)} 条数据")
        
        # 验证数据一致性
        verification = verify_data_consistency(
            self.source_db, self.target_db, symbol, exchange, interval
        )
        
        return {
            "symbol": symbol,
            "migrated": total_migrated,
            "verification": verification
        }
    
    def migrate_all_bar_data(
        self,
        interval: Optional[Interval] = None,
        batch_size: int = 1000
    ) -> dict:
        """迁移所有 K 线数据"""
        source_overviews = self.source_db.get_bar_overview()
        
        if interval:
            # 只迁移指定周期
            target_overviews = [
                o for o in source_overviews if o.interval == interval
            ]
        else:
            # 迁移所有周期
            target_overviews = source_overviews
        
        results = {
            "total_symbols": len(set(o.symbol for o in target_overviews)),
            "migrated": 0,
            "failed": 0,
            "details": []
        }
        
        for overview in target_overviews:
            try:
                result = self.migrate_bar_data(
                    overview.symbol, overview.exchange, 
                    overview.interval, batch_size
                )
                results["details"].append(result)
                
                if result["migrated"] > 0:
                    results["migrated"] += 1
            except Exception as e:
                print(f"迁移失败: {overview.symbol}, 错误: {e}")
                results["failed"] += 1
        
        print(f"\n迁移完成: 成功 {results['migrated']}, "
              f"失败 {results['failed']}")
        return results
    
    def migrate_tick_data(
        self,
        symbol: str,
        exchange: Exchange,
        batch_size: int = 10000
    ) -> dict:
        """迁移 Tick 数据"""
        print(f"\n开始迁移 {symbol} {exchange.value} Tick 数据")
        
        # Tick 数据量通常很大，需要特别处理
        source_overviews = self.source_db.get_tick_overview()
        source_overview = next(
            (o for o in source_overviews 
             if o.symbol == symbol and o.exchange == exchange),
            None
        )
        
        if not source_overview:
            print("源数据库中无数据")
            return {"symbol": symbol, "migrated": 0}
        
        print(f"数据范围: {source_overview.start} ~ {source_overview.end}")
        print(f"数据条数: {source_overview.count}")
        
        # 分块加载
        from datetime import timedelta
        all_ticks = []
        current_start = source_overview.start
        
        while current_start <= source_overview.end:
            current_end = min(
                current_start + timedelta(days=1),
                source_overview.end
            )
            
            ticks = self.source_db.load_tick_data(
                symbol, exchange, current_start, current_end
            )
            all_ticks.extend(ticks)
            
            print(f"已加载 {len(ticks)} 条 Tick 数据 "
                  f"({current_start} ~ {current_end})")
            
            current_start = current_end + timedelta(seconds=1)
        
        # 分批写入
        total_migrated = 0
        for i in range(0, len(all_ticks), batch_size):
            batch = all_ticks[i:i + batch_size]
            result = self.target_db.save_tick_data(batch)
            if result:
                total_migrated += len(batch)
                print(f"已迁移 {total_migrated}/{len(all_ticks)} 条数据")
        
        return {
            "symbol": symbol,
            "migrated": total_migrated
        }


def migrate_database(
    source_db_type: str,
    target_db_type: str
) -> dict:
    """数据库迁移主函数"""
    from vnpy.trader.setting import SETTINGS
    
    # 保存当前数据库配置
    original_db_type = SETTINGS.get("database.name", "sqlite")
    
    # 连接源数据库
    SETTINGS["database.name"] = source_db_type
    source_db = get_database()
    print(f"源数据库: {type(source_db).__name__}")
    
    # 连接目标数据库
    SETTINGS["database.name"] = target_db_type
    target_db = get_database()
    print(f"目标数据库: {type(target_db).__name__}")
    
    # 创建迁移器
    migrator = DataMigrator(source_db, target_db)
    
    # 迁移所有 K 线数据
    print("\n=== 迁移 K 线数据 ===")
    result = migrator.migrate_all_bar_data()
    
    # 恢复原始数据库配置
    SETTINGS["database.name"] = original_db_type
    
    return result


if __name__ == "__main__":
    # 示例：从 SQLite 迁移到 MySQL
    if len(sys.argv) >= 3:
        source_type = sys.argv[1]
        target_type = sys.argv[2]
    else:
        source_type = "sqlite"
        target_type = "mysql"
    
    print(f"开始迁移: {source_type} -> {target_type}")
    result = migrate_database(source_type, target_type)
    print(f"\n迁移结果: {result}")
```

### 9.3 性能测试工具

```python
"""
vn.py 数据库性能测试工具
测试：读写性能、并发性能、大数据处理能力
"""

import time
import statistics
from datetime import datetime, timedelta
from typing import List
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.database import get_database, BaseDatabase
from vnpy.trader.object import BarData

class DatabasePerformanceTester:
    """数据库性能测试器"""
    
    def __init__(self, database: BaseDatabase):
        self.database = database
        self.results = {}
    
    def test_write_performance(
        self,
        test_bars: List[BarData],
        batch_sizes: List[int] = [100, 500, 1000, 5000]
    ) -> dict:
        """测试写入性能"""
        print("\n=== 写入性能测试 ===")
        results = {}
        
        for batch_size in batch_sizes:
            times = []
            
            for i in range(5):  # 每个批次大小测试5次
                start_time = time.time()
                
                self.database.save_bar_data(test_bars[:batch_size])
                
                elapsed = time.time() - start_time
                times.append(elapsed)
                
                # 清理数据
                self.database.delete_bar_data(
                    test_bars[0].symbol,
                    test_bars[0].exchange,
                    test_bars[0].interval
                )
            
            avg_time = statistics.mean(times)
            throughput = batch_size / avg_time
            
            results[batch_size] = {
                "avg_time": avg_time,
                "min_time": min(times),
                "max_time": max(times),
                "throughput": throughput
            }
            
            print(f"批次大小: {batch_size}, "
                  f"平均时间: {avg_time:.3f}s, "
                  f"吞吐量: {throughput:.0f} 条/秒")
        
        return results
    
    def test_read_performance(
        self,
        symbol: str,
        exchange: Exchange,
        interval: Interval,
        data_sizes: List[int] = [1000, 5000, 10000, 50000]
    ) -> dict:
        """测试读取性能"""
        print("\n=== 读取性能测试 ===")
        results = {}
        
        for data_size in data_sizes:
            # 查询数据
            start = datetime(2024, 1, 1)
            end = start + timedelta(minutes=data_size)
            
            times = []
            for i in range(5):
                start_time = time.time()
                
                bars = self.database.load_bar_data(
                    symbol, exchange, interval, start, end
                )
                
                elapsed = time.time() - start_time
                times.append(elapsed)
            
            avg_time = statistics.mean(times)
            actual_size = len(bars) if bars else 0
            throughput = actual_size / avg_time if actual_size > 0 else 0
            
            results[data_size] = {
                "actual_size": actual_size,
                "avg_time": avg_time,
                "min_time": min(times),
                "max_time": max(times),
                "throughput": throughput
            }
            
            print(f"数据量: {actual_size}, "
                  f"平均时间: {avg_time:.3f}s, "
                  f"吞吐量: {throughput:.0f} 条/秒")
        
        return results
    
    def test_concurrent_write(
        self,
        test_bars: List[BarData],
        thread_counts: List[int] = [1, 2, 4, 8]
    ) -> dict:
        """测试并发写入性能"""
        from concurrent.futures import ThreadPoolExecutor
        
        print("\n=== 并发写入测试 ===")
        results = {}
        
        batch_size = 1000
        
        for thread_count in thread_counts:
            times = []
            
            for i in range(3):
                start_time = time.time()
                
                with ThreadPoolExecutor(max_workers=thread_count) as executor:
                    futures = []
                    for j in range(thread_count):
                        batch = test_bars[j * batch_size:(j + 1) * batch_size]
                        future = executor.submit(
                            self.database.save_bar_data, batch
                        )
                        futures.append(future)
                    
                    for future in futures:
                        future.result()
                
                elapsed = time.time() - start_time
                times.append(elapsed)
                
                # 清理
                self.database.delete_bar_data(
                    test_bars[0].symbol,
                    test_bars[0].exchange,
                    test_bars[0].interval
                )
            
            avg_time = statistics.mean(times)
            total_size = batch_size * thread_count
            throughput = total_size / avg_time
            
            results[thread_count] = {
                "avg_time": avg_time,
                "throughput": throughput
            }
            
            print(f"线程数: {thread_count}, "
                  f"平均时间: {avg_time:.3f}s, "
                  f"吞吐量: {throughput:.0f} 条/秒")
        
        return results


def run_performance_tests():
    """运行完整性能测试"""
    database = get_database()
    print(f"测试数据库: {type(database).__name__}")
    
    tester = DatabasePerformanceTester(database)
    
    # 创建测试数据
    print("\n准备测试数据...")
    test_bars = create_test_bars("TEST", Exchange.SSE, Interval.MINUTE, 50000)
    print(f"已创建 {len(test_bars)} 条测试数据")
    
    # 保存测试数据
    database.save_bar_data(test_bars)
    print("测试数据已保存到数据库")
    
    # 运行测试
    write_results = tester.test_write_performance(test_bars)
    read_results = tester.test_read_performance(
        "TEST", Exchange.SSE, Interval.MINUTE
    )
    concurrent_results = tester.test_concurrent_write(test_bars)
    
    # 输出总结
    print("\n=== 性能测试总结 ===")
    print(f"写入性能: {max(r['throughput'] for r in write_results.values()):.0f} 条/秒")
    print(f"读取性能: {max(r['throughput'] for r in read_results.values()):.0f} 条/秒")
    print(f"最佳并发: {max(concurrent_results, key=lambda k: concurrent_results[k]['throughput'])} 线程")
    
    # 清理
    database.delete_bar_data("TEST", Exchange.SSE, Interval.MINUTE)
    print("\n测试数据已清理")


if __name__ == "__main__":
    run_performance_tests()
```

---

## 总结

vn.py 数据管理模块采用抽象工厂模式和策略模式，实现了数据库层的完全解耦，支持 SQLite、MySQL、PostgreSQL 等多种数据库。本文档深度解析了：

1. **抽象层设计**：BaseDatabase 定义了统一的数据访问接口，通过工厂方法动态创建数据库实例
2. **多数据库支持**：各数据库实现继承 BaseDatabase，提供统一的操作体验
3. **数据存储机制**：使用时区转换、upsert 去重、汇总表维护等机制保证数据质量
4. **查询优化**：通过复合索引、分页查询、聚合查询、缓存策略等提升性能
5. **数据导入导出**：支持 CSV、Excel、JSON、Parquet 等多种格式
6. **备份恢复**：针对不同数据库提供了完整的备份恢复方案
7. **大数据处理**：使用数据分片、压缩、流式处理、并行处理等技巧处理海量数据
8. **数据同步**：支持增量同步和全量同步，并提供数据一致性检查

通过合理运用这些技术，可以构建一个高性能、高可靠性的量化交易数据管理系统。
