# ChatJob Docker 部署指南

## 概述

本项目使用 Docker Compose 进行容器化部署，包含以下服务：

- **MySQL 8.0**: 数据库服务
- **Redis 7**: 缓存服务  
- **Backend**: Python 后端 API 服务
- **Frontend**: Vue.js 前端服务
- **Nginx**: 反向代理和负载均衡

## 系统要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少 4GB 可用内存
- 至少 10GB 可用磁盘空间

## 快速开始

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd chatjob
```

### 2. 配置环境变量

复制并修改环境配置文件：

```bash
cp backend/env.example backend/.env
```

根据需要修改数据库连接信息。

### 3. 部署服务

```bash
cd deploy
chmod +x deploy.sh
./deploy.sh
```

或者手动执行：

```bash
docker-compose up -d --build
```

### 4. 访问服务

- 前端: http://localhost
- 后端 API: http://localhost/api
- 健康检查: http://localhost/health

## 服务配置

### MySQL 配置

- 端口: 3306
- 数据库: chatjob
- 用户名: chatjob
- 密码: chatjob123
- 根密码: root123456

### Redis 配置

- 端口: 6379
- 持久化: 启用 AOF
- 无密码认证

### Nginx 配置

- HTTP 端口: 80
- HTTPS 端口: 443 (需要配置 SSL 证书)
- 前端代理: 3000 端口
- 后端代理: 8000 端口

## 常用命令

### 启动服务

```bash
docker-compose up -d
```

### 停止服务

```bash
docker-compose down
```

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs backend
docker-compose logs frontend
docker-compose logs nginx
```

### 重启服务

```bash
docker-compose restart
```

### 重新构建

```bash
docker-compose up -d --build
```

## 数据持久化

- MySQL 数据存储在 `mysql_data` 卷中
- Redis 数据存储在 `redis_data` 卷中
- 应用代码通过卷挂载实现热更新

## 故障排除

### 1. 服务无法启动

检查端口占用：

```bash
netstat -tulpn | grep :80
netstat -tulpn | grep :3306
netstat -tulpn | grep :6379
```

### 2. 数据库连接失败

检查 MySQL 容器状态：

```bash
docker-compose logs mysql
```

### 3. 前端无法访问

检查前端构建：

```bash
docker-compose logs frontend
```

### 4. Nginx 代理失败

检查 Nginx 配置：

```bash
docker-compose exec nginx nginx -t
```

## 生产环境配置

### 1. 修改默认密码

修改 `docker-compose.yaml` 中的数据库密码。

### 2. 配置 SSL 证书

将 SSL 证书文件放入 `nginx/ssl/` 目录，并取消注释 HTTPS 配置。

### 3. 设置环境变量

创建 `.env` 文件管理敏感信息：

```bash
MYSQL_ROOT_PASSWORD=your_secure_password
MYSQL_PASSWORD=your_secure_password
```

### 4. 配置防火墙

确保只开放必要的端口：

```bash
# 只开放 HTTP/HTTPS 端口
ufw allow 80
ufw allow 443
ufw deny 3306
ufw deny 6379
```

## 监控和维护

### 1. 查看资源使用

```bash
docker stats
```

### 2. 备份数据

```bash
# 备份 MySQL
docker exec chatjob_mysql mysqldump -u root -p chatjob > backup.sql

# 备份 Redis
docker exec chatjob_redis redis-cli BGSAVE
```

### 3. 更新服务

```bash
git pull
docker-compose up -d --build
```

## 支持

如遇到问题，请检查：

1. Docker 和 Docker Compose 版本
2. 系统资源使用情况
3. 服务日志输出
4. 网络连接状态
