# vn.py 数据管理模块数据库配置说明

vn.py 数据管理模块支持多种数据库后端，包括 SQLite、MySQL 和 PostgreSQL。本文档详细介绍各数据库的配置方法及切换注意事项。

## 一、SQLite 配置方法

SQLite 是 vn.py 的默认数据库，无需额外安装，开箱即用。

**配置步骤：**

1. 在 `setting.json` 中配置数据库路径：
```json
{
  "database.name": "sqlite",
  "database.database": "database.db"
}
```

2. SQLite 数据库文件默认保存在项目根目录下，可指定绝对路径或相对路径。

**优点：** 零配置、轻量级、适合单机使用和开发测试环境。

## 二、MySQL 配置方法

MySQL 适合生产环境和多用户并发场景。

**配置步骤：**

1. 安装 MySQL 服务器和客户端库：
```bash
pip install pymysql
```

2. 在 `setting.json` 中配置连接参数：
```json
{
  "database.name": "mysql",
  "database.host": "localhost",
  "database.port": 3306,
  "database.username": "root",
  "database.password": "password",
  "database.database": "vnpy"
}
```

3. 创建数据库：
```sql
CREATE DATABASE vnpy CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

**注意：** 确保 MySQL 服务已启动，用户权限配置正确。

## 三、PostgreSQL 配置方法

PostgreSQL 提供更强大的功能和更好的并发性能。

**配置步骤：**

1. 安装 PostgreSQL 客户端库：
```bash
pip install psycopg2-binary
```

2. 在 `setting.json` 中配置连接参数：
```json
{
  "database.name": "postgresql",
  "database.host": "localhost",
  "database.port": 5432,
  "database.username": "postgres",
  "database.password": "password",
  "database.database": "vnpy"
}
```

3. 创建数据库：
```sql
CREATE DATABASE vnpy ENCODING 'UTF8';
```

## 四、数据库切换注意事项

1. **数据迁移：** 切换数据库前，需导出原数据库数据并导入新数据库。vn.py 提供数据导出导入工具，建议使用官方脚本进行迁移。

2. **表结构差异：** 不同数据库的数据类型和约束可能存在细微差异，迁移后需验证数据完整性。

3. **性能考虑：** SQLite 适合单机和小规模数据，MySQL 和 PostgreSQL 更适合生产环境和大规模数据。

4. **备份策略：** 生产环境建议配置定期备份，特别是使用 MySQL 或 PostgreSQL 时。

5. **连接池：** 高并发场景下，建议配置数据库连接池以提高性能。

## 五、配置文件示例

以下是完整的 `setting.json` 配置示例：

```json
{
  "database.name": "mysql",
  "database.host": "localhost",
  "database.port": 3306,
  "database.username": "vnpy_user",
  "database.password": "secure_password",
  "database.database": "vnpy_production",
  
  "database.timezone": "Asia/Shanghai",
  "database.encoding": "utf8mb4",
  
  "database.pool_size": 10,
  "database.max_overflow": 20,
  "database.pool_timeout": 30,
  "database.pool_recycle": 3600
}
```

**参数说明：**
- `database.name`: 数据库类型（sqlite/mysql/postgresql）
- `database.host`: 数据库服务器地址
- `database.port`: 数据库端口
- `database.username`: 数据库用户名
- `database.password`: 数据库密码
- `database.database`: 数据库名称
- `database.timezone`: 时区设置
- `database.pool_size`: 连接池大小
- `database.max_overflow`: 最大溢出连接数
- `database.pool_timeout`: 连接超时时间（秒）
- `database.pool_recycle`: 连接回收时间（秒）

通过合理配置数据库，可以确保 vn.py 数据管理模块稳定高效地运行，满足不同场景的需求。