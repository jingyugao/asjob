# Connector DAO层使用说明

## 快速开始

### 1. 环境配置

#### 方式1: 使用连接字符串（推荐）
复制环境配置文件并修改数据库连接信息：

```bash
cp env.example .env
# 编辑 .env 文件，设置正确的数据库连接字符串
```

**连接字符串格式**:
```bash
# 无密码
DB_MYSQL_DNS=mysql://root@localhost:3306/asjob

# 有密码
DB_MYSQL_DNS=mysql://root:password@localhost:3306/asjob

# 特殊字符密码（如你提到的例子）
DB_MYSQL_DNS=mysql://root:Str0ngP@ssw0rd!@localhost:3306/asjob

# 自定义端口
DB_MYSQL_DNS=mysql://root:password@localhost:3307/asjob
```

#### 方式2: 使用环境变量
```bash
export DB_MYSQL_DNS="mysql://root:password@localhost:3306/asjob"
```

### 2. 配置验证

在启动应用前，建议先验证配置：

```bash
python check_config.py
```

这个脚本会检查：
- 环境变量设置
- 配置对象创建
- 数据库连接测试
- 提供修复建议

### 3. 安装依赖

```bash
uv sync
```

### 4. 启动应用

#### 方式1: 使用数据库初始化脚本（推荐）
```bash
python start_with_db.py
```

#### 方式2: 手动初始化数据库
```bash
# 初始化数据库
python -m database.init_db

# 启动应用
uvicorn main:app --reload
```

### 5. 访问API

- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/api/health

## 连接字符串配置详解

### 基本格式
```
mysql://username:password@host:port/database
```

### 各部分说明
- `username`: 数据库用户名
- `password`: 数据库密码（可选）
- `host`: 数据库主机地址
- `port`: 数据库端口（可选，默认3306）
- `database`: 数据库名称

### 特殊字符处理
如果密码包含特殊字符，建议使用环境变量或.env文件：

```bash
# 包含特殊字符的密码
DB_MYSQL_DNS="mysql://root:Str0ngP@ssw0rd!@localhost:3306/asjob"

# 包含@符号的密码（需要URL编码）
DB_MYSQL_DNS="mysql://root:pass%40word@localhost:3306/asjob"
```

### 常见配置示例

```bash
# 本地开发环境
DB_MYSQL_DNS=mysql://root:dev_password@localhost:3306/asjob_dev

# 测试环境
DB_MYSQL_DNS=mysql://test_user:test_pass@test-db.example.com:3306/asjob_test

# 生产环境
DB_MYSQL_DNS=mysql://prod_user:prod_pass@prod-db.example.com:3306/asjob_prod

# 使用Unix socket（本地）
DB_MYSQL_DNS=mysql://root:password@/var/run/mysqld/mysqld.sock/asjob
```

## API使用示例

### 创建连接器

```bash
curl -X POST "http://localhost:8000/api/v1/connectors/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my_mysql",
    "db_type": "mysql",
    "host": "localhost",
    "port": 3306,
    "username": "root",
    "password": "password",
    "database": "test",
    "description": "我的MySQL数据库"
  }'
```

### 查询连接器

```bash
# 获取所有连接器
curl "http://localhost:8000/api/v1/connectors/"

# 获取特定连接器
curl "http://localhost:8000/api/v1/connectors/1"

# 搜索连接器
curl "http://localhost:8000/api/v1/connectors/search/mysql"
```

### 更新连接器

```bash
curl -X PUT "http://localhost:8000/api/v1/connectors/1" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "更新后的描述"
  }'
```

### 测试连接

```bash
curl -X POST "http://localhost:8000/api/v1/connectors/1/test"
```

## 代码使用示例

### 在Python代码中使用DAO层

```python
from database.service.connector_service import ConnectorService
from database.session import get_db_session

# 获取服务实例
session = next(get_db_session())
service = ConnectorService(session)

# 创建连接器
connector = service.create_connector({
    "name": "prod_db",
    "db_type": "mysql",
    "host": "prod.example.com",
    "port": 3306,
    "username": "app_user",
    "password": "secure_pass",
    "database": "app_db"
})

# 查询连接器
all_connectors = service.list_connectors()
mysql_connectors = service.list_connectors_by_type("mysql")

# 测试连接
is_connected = service.test_connector(connector.id)
```

## 测试

运行测试脚本验证DAO层功能：

```bash
python test_dao.py
```

## 项目结构

```
backend/
├── database/
│   ├── __init__.py
│   ├── config.py          # 数据库配置（支持连接字符串）
│   ├── session.py         # 数据库会话管理
│   ├── init_db.py         # 数据库初始化
│   ├── model/
│   │   ├── __init__.py
│   │   └── connector.py   # 连接器数据模型
│   ├── dao/
│   │   ├── __init__.py
│   │   └── connector_dao.py # 连接器DAO
│   ├── service/
│   │   ├── __init__.py
│   │   └── connector_service.py # 连接器服务层
│   └── schema/
│       ├── __init__.py
│       └── connector_schema.py # Pydantic模型
├── api/
│   ├── __init__.py
│   └── connector_api.py   # 连接器API路由
├── connectors/             # 现有连接器实现
├── main.py                # 主应用文件
├── start_with_db.py       # 带数据库初始化的启动脚本
├── check_config.py        # 配置验证脚本
└── test_dao.py            # DAO层测试脚本
```

## 故障排除

### 配置验证
使用配置验证脚本检查问题：

```bash
python check_config.py
```

### 常见问题

#### 1. 连接字符串格式错误
```
错误: Invalid MySQL DNS format
解决: 确保连接字符串格式为 mysql://username:password@host:port/database
```

#### 2. 数据库连接失败
```
错误: Can't connect to MySQL server
解决: 
- 检查MySQL服务是否运行
- 验证连接字符串中的主机、端口、用户名、密码
- 确认数据库是否存在
```

#### 3. 权限不足
```
错误: Access denied for user
解决:
- 检查用户名和密码是否正确
- 确认用户是否有访问指定数据库的权限
- 确认用户是否有CREATE TABLE权限
```

### 调试技巧

1. **查看连接信息**:
   ```python
   from database.session import get_connection_info
   print(get_connection_info())
   ```

2. **启用SQL日志**:
   修改 `database/session.py` 中的 `echo=True`

3. **检查环境变量**:
   ```bash
   echo $DB_MYSQL_DNS
   ```

## 注意事项

1. **密码安全**: 密码以明文存储，生产环境建议加密
2. **连接池**: 当前使用SQLAlchemy连接池配置
3. **事务管理**: 所有数据库操作都在事务中执行
4. **错误处理**: 统一的异常处理和错误响应格式
5. **特殊字符**: 密码中的特殊字符需要正确转义

## 扩展性

### 支持新的数据库类型
1. 在`connectors/`目录下添加新的连接器类
2. 在`get_connector_instance()`函数中添加类型映射
3. 更新数据库模型（如需要）

### 添加新的字段
1. 修改`ConnectorModel`类
2. 更新Pydantic schema
3. 运行数据库迁移
