# 后端配置说明

## 环境变量配置

### 1. 创建环境变量文件
在项目根目录创建 `.env` 文件：

```bash
# 数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=chatjob

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# 日志配置
LOG_LEVEL=INFO

# LLM配置
LLM_MODEL=gemini-pro
LLM_TEMPERATURE=0.7
LLM_TIMEOUT=120
LLM_GOOGLE_API_KEY=your_google_api_key_here

# 应用配置
APP_HOST=0.0.0.0
APP_PORT=8000
APP_DEBUG=false

# 测试配置
TEST_BATCH_SIZE=100
TEST_TABLE_NAME=test_users
```

### 2. 获取Google API密钥
1. 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 创建新的API密钥
3. 将密钥添加到 `.env` 文件的 `LLM_GOOGLE_API_KEY` 字段

### 3. 配置系统特点
- **类型安全**: 所有配置都有明确的类型注解
- **自动验证**: 配置值在应用启动时自动验证
- **环境变量映射**: 自动从.env文件读取配置
- **前缀映射**: 每个配置类都有对应的环境变量前缀

### 4. 配置访问方式
```python
from backend.config import settings

# 数据库配置
db_host = settings.database.host
db_port = settings.database.port

# LLM配置
llm_model = settings.llm.model
llm_api_key = settings.llm.api_key

# 应用配置
app_host = settings.app.host
app_port = settings.app.port
```

### 5. 重要提醒
- **禁止在代码中使用os.getenv()获取配置**
- **所有配置必须通过settings对象访问**
- **配置值只能通过.env文件设置**
- **.env文件不会被提交到版本控制系统**

### 6. 环境变量前缀映射
- `MYSQL_*` → 数据库配置
- `REDIS_*` → Redis配置
- `LOG_*` → 日志配置
- `LLM_*` → LLM配置
- `APP_*` → 应用配置
- `TEST_*` → 测试配置

### 7. 部署说明
- 生产环境：设置环境变量或使用专门的.env文件
- 开发环境：使用本地的.env文件
- 测试环境：使用测试专用的.env.test文件
