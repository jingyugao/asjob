#!/usr/bin/env python3
"""
数据库配置验证脚本
用于验证数据库连接配置是否正确
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.database.config import DatabaseConfig
from backend.database.session import get_connection_info
from backend.database.init_db import test_connection


def check_environment():
    """检查环境变量配置"""
    print("=" * 60)
    print("环境变量检查")
    print("=" * 60)

    # 检查环境变量
    env_vars = {
        "DB_MYSQL_DNS": os.getenv("DB_MYSQL_DNS"),
        "DB_HOST": os.getenv("DB_HOST"),
        "DB_PORT": os.getenv("DB_PORT"),
        "DB_USERNAME": os.getenv("DB_USERNAME"),
        "DB_PASSWORD": os.getenv("DB_PASSWORD"),
        "DB_DATABASE": os.getenv("DB_DATABASE"),
    }

    print("当前环境变量:")
    for key, value in env_vars.items():
        if value:
            # 隐藏密码
            if "PASSWORD" in key:
                display_value = "*" * len(value) if value else "None"
            else:
                display_value = value
            print(f"  {key}: {display_value}")
        else:
            print(f"  {key}: None")

    return env_vars


def check_config():
    """检查配置对象"""
    print("\n" + "=" * 60)
    print("配置对象检查")
    print("=" * 60)

    try:
        config = DatabaseConfig()
        print("✅ 配置对象创建成功")

        print(f"MySQL DNS: {config.mysql_dns}")
        print(f"URL: {config.url}")

        connection_params = config.connection_params
        print(f"解析的连接参数:")
        for key, value in connection_params.items():
            if key == "password":
                display_value = "*" * len(str(value)) if value else "None"
            else:
                display_value = value
            print(f"  {key}: {display_value}")

        return True
    except Exception as e:
        print(f"❌ 配置对象创建失败: {e}")
        return False


def check_database_connection():
    """检查数据库连接"""
    print("\n" + "=" * 60)
    print("数据库连接检查")
    print("=" * 60)

    try:
        connection_info = get_connection_info()
        print("连接信息:")
        print(f"  MySQL DNS: {connection_info['mysql_dns']}")

        # 测试连接
        if test_connection():
            print("✅ 数据库连接成功")
            return True
        else:
            print("❌ 数据库连接失败")
            return False
    except Exception as e:
        print(f"❌ 连接检查失败: {e}")
        return False


def suggest_fixes():
    """提供修复建议"""
    print("\n" + "=" * 60)
    print("配置修复建议")
    print("=" * 60)

    print("1. 设置环境变量:")
    print("   export DB_MYSQL_DNS='mysql://username:password@host:port/database'")
    print()
    print("2. 或者创建 .env 文件:")
    print("   DB_MYSQL_DNS=mysql://root:password@localhost:3306/chatjob")
    print()
    print("3. 常见连接字符串格式:")
    print("   - 无密码: mysql://root@localhost:3306/chatjob")
    print("   - 有密码: mysql://root:password@localhost:3306/chatjob")
    print("   - 特殊字符密码: mysql://root:Str0ngP@ssw0rd!@localhost:3306/chatjob")
    print()
    print("4. 检查MySQL服务:")
    print("   sudo systemctl status mysql")
    print("   sudo systemctl start mysql")
    print()
    print("5. 检查数据库是否存在:")
    print("   mysql -u root -p -e 'CREATE DATABASE IF NOT EXISTS chatjob;'")


def main():
    """主函数"""
    print("数据库配置验证工具")
    print("=" * 60)

    # 检查环境变量
    env_vars = check_environment()

    # 检查配置对象
    config_ok = check_config()

    # 检查数据库连接
    connection_ok = False
    if config_ok:
        connection_ok = check_database_connection()

    # 总结
    print("\n" + "=" * 60)
    print("检查结果总结")
    print("=" * 60)

    if config_ok and connection_ok:
        print("🎉 所有检查通过！配置正确。")
        print("可以启动应用了:")
        print("  python start_with_db.py")
    else:
        print("⚠️  配置存在问题，请参考以下修复建议:")
        suggest_fixes()

    print("=" * 60)


if __name__ == "__main__":
    main()
