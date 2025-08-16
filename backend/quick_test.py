#!/usr/bin/env python3
"""
快速测试脚本
用于验证MySQL连接日志系统是否正常工作
"""

import sys
import os
from pathlib import Path
from backend.logger import get_logger

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))


def test_imports():
    """测试模块导入"""
    logger = get_logger("quick_test")
    logger.info("测试模块导入...")

    try:
        from database.config import DatabaseConfig

        logger.info("DatabaseConfig 导入成功")

        # 统一使用 backend.logger 提供的 get_logger
        logger.info("日志模块可用")

        from database.session import db_connection

        logger.info("数据库连接模块导入成功")

        return True

    except ImportError as e:
        logger.error(f"模块导入失败: {e}")
        return False


def test_logger():
    """测试日志记录器"""
    logger = get_logger("quick_test")
    logger.info("测试日志记录器...")

    try:
        test_logger = get_logger("quick_test.test")
        test_logger.info("测试日志记录")
        test_logger.debug("测试调试日志")
        test_logger.error("测试错误日志")

        logger.info("日志记录器测试成功")
        return True

    except Exception as e:
        logger.error(f"日志记录器测试失败: {e}")
        return False


def test_config():
    """测试配置加载"""
    logger = get_logger("quick_test")
    logger.info("测试配置加载...")

    try:
        from database.config import DatabaseConfig

        config = DatabaseConfig()
        logger.info("配置加载成功")
        logger.info(
            "连接参数",
            extra={
                "host": config.connection_params.get("host"),
                "port": config.connection_params.get("port"),
                "username": config.connection_params.get("username"),
                "database": config.connection_params.get("database"),
            },
        )

        return True

    except Exception as e:
        logger.error(f"配置加载失败: {e}")
        return False


def test_connection():
    """测试数据库连接"""
    logger = get_logger("quick_test")
    logger.info("测试数据库连接...")

    try:
        from database.session import db_connection

        # 尝试获取连接信息
        connection_info = db_connection.connection_params
        logger.info("连接参数获取成功")
        logger.info(
            "连接参数",
            extra={
                "host": connection_info.get("host"),
                "port": connection_info.get("port"),
                "username": connection_info.get("username"),
                "database": connection_info.get("database"),
            },
        )

        # 注意：这里不实际连接数据库，只测试配置
        logger.warning("跳过实际数据库连接测试（需要MySQL服务运行）")

        return True

    except Exception as e:
        logger.error(f"连接测试失败: {e}")
        return False


def show_log_files():
    """显示日志文件信息"""
    logger = get_logger("quick_test")
    logger.info("日志文件信息:")

    log_dir = Path("logs/database")
    if log_dir.exists():
        logger.info(f"日志目录: {log_dir.absolute()}")

        for log_file in log_dir.glob("*.log"):
            size = log_file.stat().st_size
            logger.info(f"{log_file.name}: {size} bytes")
    else:
        logger.error("日志目录不存在")


def main():
    """主函数"""
    logger = get_logger("quick_test")
    logger.info("MySQL连接日志系统快速测试")

    # 测试模块导入
    if not test_imports():
        logger.error("模块导入测试失败，请检查依赖安装")
        return

    # 测试日志记录器
    if not test_logger():
        logger.error("日志记录器测试失败")
        return

    # 测试配置加载
    if not test_config():
        logger.error("配置加载测试失败")
        return

    # 测试连接配置
    if not test_connection():
        logger.error("连接配置测试失败")
        return

    # 显示日志文件信息
    show_log_files()

    logger.info("所有测试完成！")
    logger.info(
        "下一步操作: 1) 确保MySQL服务运行 2) 运行: python test_mysql_logging.py 3) 查看 logs/ 目录 4) 使用: python switch_logging_mode.py dev"
    )


if __name__ == "__main__":
    main()
