#!/bin/bash

echo "🚀 开始部署 ChatJob 服务..."

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker 未运行，请先启动 Docker"
    exit 1
fi

# 检查 Docker Compose 是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p nginx/ssl
mkdir -p mysql/init

# 构建并启动服务
echo "🔨 构建并启动服务..."
docker-compose up -d --build

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 检查服务状态
echo "📊 检查服务状态..."
docker-compose ps

# 检查服务健康状态
echo "🏥 检查服务健康状态..."
if curl -f http://localhost/health > /dev/null 2>&1; then
    echo "✅ 服务部署成功！"
    echo "🌐 前端访问地址: http://localhost"
    echo "🔌 后端 API 地址: http://localhost/api"
    echo "🗄️  MySQL 端口: 3306"
    echo "🔴  Redis 端口: 6379"
else
    echo "❌ 服务健康检查失败，请检查日志"
    docker-compose logs nginx
fi
