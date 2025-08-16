import sys
from pathlib import Path
from loguru import logger

# 创建日志目录
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# 移除默认的控制台输出
logger.remove()

# 添加控制台输出（INFO级别）
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
    level="INFO",
    colorize=True,
)

# 添加文件输出（DEBUG级别，包含更多详细信息）
logger.add(
    log_dir / "backend.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
    level="DEBUG",
    rotation="10 MB",
    retention="30 days",
    compression="zip",
)


# 获取logger实例
def get_logger(name: str):
    return logger.bind(name=name)
