import logs
import os
from pathlib import Path

# 创建日志目录
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# 配置日志
logs.setup(
    level="INFO",
    format="[{time:YYYY-MM-DD HH:mm:ss}] {level} | {name}:{function}:{line} | {message}",
    file=log_dir / "backend.log",
    rotation="10 MB",
    retention="30 days"
)

# 获取logger实例
def get_logger(name: str):
    return logs.get_logger(name)
