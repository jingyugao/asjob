# Data Development Platform Backend

数据开发平台后端服务

## 功能特性

- 数据库连接器管理
- 支持MySQL、Doris等数据库
- RESTful API接口
- 完整的CRUD操作
- 连接测试和状态管理

## 快速开始

### 1. 环境配置

```bash
# 复制环境配置文件
cp env.example .env

# 编辑 .env 文件，设置数据库连接字符串
DB_MYSQL_DNS=mysql://root:password@localhost:3306/asjob
```

### 2. 安装依赖

```bash
uv sync
```

### 3. 启动服务

```bash
python start_with_db.py
```

### 4. 访问API

- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/api/health

## 项目结构

```
backend/
├── database/           # 数据库层
├── api/               # API接口
├── connectors/         # 数据库连接器
├── main.py            # 主应用
└── README_DAO.md      # 详细使用说明
```

## 详细文档

更多详细信息请参考 [README_DAO.md](README_DAO.md)
