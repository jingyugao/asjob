#!/usr/bin/env python3
"""
数据库配置验证脚本
用于验证数据库连接配置是否正确
"""

import os
import sys
from pathlib import Path
from backend.logger import get_logger

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.database.config import DatabaseConfig
from backend.database.session import get_connection_info
from backend.database.init_db import test_connection


def check_environment():
    """检查环境变量配置"""
    logger = get_logger("check_config")
    logger.info("环境变量检查")

    # 检查环境变量
    env_vars = {
        "DB_MYSQL_DNS": os.getenv("DB_MYSQL_DNS"),
        "DB_HOST": os.getenv("DB_HOST"),
        "DB_PORT": os.getenv("DB_PORT"),
        "DB_USERNAME": os.getenv("DB_USERNAME"),
        "DB_PASSWORD": os.getenv("DB_PASSWORD"),
        "DB_DATABASE": os.getenv("DB_DATABASE"),
    }

    logger.info("当前环境变量:")
    for key, value in env_vars.items():
        if value:
            # 隐藏密码
            if "PASSWORD" in key:
                display_value = "*" * len(value) if value else "None"
            else:
                display_value = value
            logger.info(f"{key}: {display_value}")
        else:
            logger.info(f"{key}: None")

    return env_vars


def check_config():
    """检查配置对象"""
    logger = get_logger("check_config")
    logger.info("配置对象检查")

    try:
        config = DatabaseConfig()
        logger.info("配置对象创建成功")

        logger.info(f"MySQL DNS: {config.mysql_dns}")
        logger.info(f"URL: {config.url}")

        connection_params = config.connection_params
        logger.info("解析的连接参数:")
        for key, value in connection_params.items():
            if key == "password":
                display_value = "*" * len(str(value)) if value else "None"
            else:
                display_value = value
            logger.info(f"{key}: {display_value}")

        return True
    except Exception as e:
        logger.error(f"配置对象创建失败: {e}")
        return False


def check_database_connection():
    """检查数据库连接"""
    logger = get_logger("check_config")
    logger.info("数据库连接检查")

    try:
        connection_info = get_connection_info()
        logger.info("连接信息:")
        logger.info(f"MySQL DNS: {connection_info['mysql_dns']}")

        # 测试连接
        if test_connection():
            logger.info("数据库连接成功")
            return True
        else:
            logger.error("数据库连接失败")
            return False
    except Exception as e:
        logger.error(f"连接检查失败: {e}")
        return False


def suggest_fixes():
    """提供修复建议"""
    logger = get_logger("check_config")
    logger.info("配置修复建议")

    logger.info(
        "1. 设置环境变量: export DB_MYSQL_DNS='mysql://username:password@host:port/database'"
    )
    logger.info(
        "2. 或者创建 .env 文件: DB_MYSQL_DNS=mysql://root:password@localhost:3306/chatjob"
    )
    logger.info("3. 常见连接字符串格式: 无密码/有密码/特殊字符密码")
    logger.info("4. 检查MySQL服务: systemctl status/start mysql")
    logger.info(
        "5. 检查数据库是否存在: mysql -u root -p -e 'CREATE DATABASE IF NOT EXISTS chatjob;'"
    )


def main():
    """主函数"""
    logger = get_logger("check_config")
    logger.info("数据库配置验证工具")

    # 检查环境变量
    env_vars = check_environment()

    # 检查配置对象
    config_ok = check_config()

    # 检查数据库连接
    connection_ok = False
    if config_ok:
        connection_ok = check_database_connection()

    # 总结
    logger.info("检查结果总结")

    if config_ok and connection_ok:
        logger.info("所有检查通过！配置正确。可以启动应用了: python start_with_db.py")
    else:
        logger.warning("配置存在问题，请参考以下修复建议")
        suggest_fixes()


if __name__ == "__main__":
    main()
