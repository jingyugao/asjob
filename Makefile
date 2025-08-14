.PHONY: help start stop test test-api clean install

# 默认目标
help:
	@echo "可用的命令:"
	@echo "  make start      - 启动数据开发平台（后端+前端）"
	@echo "  make stop       - 停止所有服务"
	@echo "  make test       - 运行所有测试"
	@echo "  make test-api   - 运行API测试"
	@echo "  make install    - 安装依赖"
	@echo "  make clean      - 清理临时文件"
	@echo "  make backend    - 只启动后端服务"
	@echo "  make frontend   - 只启动前端服务"

# 启动完整服务
start: backend frontend
	@echo "🚀 数据开发平台启动完成！"
	@echo "前端: http://localhost:3000"
	@echo "后端: http://localhost:8000"
	@echo "按 Ctrl+C 停止服务"

# 启动后端服务
backend:
	@echo "启动后端服务..."
	@export PYTHONPATH=$PYTHONPATH:$(pwd)
	@uv run python backend/main.py &
	@echo "后端服务已启动 (PID: $$!)"

# 启动前端服务
frontend:
	@echo "启动前端服务..."
	@cd frontend && npm run dev &
	@echo "前端服务已启动 (PID: $$!)"

# 停止所有服务
stop:
	@echo "停止所有服务..."
	@pkill -f "python main.py" || true
	@pkill -f "npm run dev" || true
	@echo "所有服务已停止"



# 运行所有测试
test: test-api
	@echo "🧪 所有测试完成"

# 运行API测试
test-api:
	@echo "🧪 运行API测试..."
	@cd tests && python3 test_api.py

# 运行连接器测试
test-connectors:
	@echo "🧪 运行连接器测试..."
	@cd backend && uv run python ../tests/test_connectors.py

# 运行简单测试
test-simple:
	@echo "🧪 运行简单测试..."
	@cd backend && uv run python ../tests/simple_test.py

# 创建测试数据
create-test-data:
	@echo "📊 创建测试数据..."
	@cd backend && uv run python ../tests/create_test_data.py

# 清理临时文件
clean:
	@echo "清理临时文件..."
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.log" -delete
	@echo "清理完成"

# 检查服务状态
status:
	@echo "检查服务状态..."
	@echo "后端服务:"
	@pgrep -f "python main.py" && echo "  ✅ 运行中" || echo "  ❌ 未运行"
	@echo "前端服务:"
	@pgrep -f "npm run dev" && echo "  ✅ 运行中" || echo "  ❌ 未运行"

# 重启服务
restart: stop
	@sleep 2
	@make start

# 查看日志
logs:
	@echo "查看服务日志..."
	@echo "按 Ctrl+C 退出"
	@tail -f /dev/null 2>/dev/null || echo "日志功能不可用"
