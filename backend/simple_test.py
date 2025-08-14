#!/usr/bin/env python3
"""
简单的连接字符串测试脚本
演示如何使用不同的连接字符串配置
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database.config import DatabaseConfig


def test_connection_strings():
    """测试不同的连接字符串格式"""
    print("=" * 60)
    print("连接字符串配置测试")
    print("=" * 60)

    # 测试用例
    test_cases = [
        "mysql://root@localhost:3306/asjob",
        "mysql://root:password@localhost:3306/asjob",
        "mysql://root:Str0ngP@ssw0rd!@localhost:3306/asjob",
        "mysql://user:pass@db.example.com:3307/prod_db",
        "mysql://admin@localhost/asjob",
    ]

    for i, test_dns in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {test_dns}")
        print("-" * 40)

        try:
            # 临时设置环境变量
            os.environ["DB_MYSQL_DNS"] = test_dns

            # 创建配置对象
            config = DatabaseConfig()

            # 显示解析结果
            print(f"✅ 解析成功")
            print(f"   URL: {config.url}")

            params = config.connection_params
            print(f"   主机: {params.get('host', 'N/A')}")
            print(f"   端口: {params.get('port', 'N/A')}")
            print(f"   用户: {params.get('username', 'N/A')}")
            print(
                f"   密码: {'*' * len(str(params.get('password', ''))) if params.get('password') else 'None'}"
            )
            print(f"   数据库: {params.get('database', 'N/A')}")

        except Exception as e:
            print(f"❌ 解析失败: {e}")

        finally:
            # 清理环境变量
            if "DB_MYSQL_DNS" in os.environ:
                del os.environ["DB_MYSQL_DNS"]


def test_environment_variables():
    """测试环境变量配置"""
    print("\n" + "=" * 60)
    print("环境变量配置测试")
    print("=" * 60)

    # 设置测试环境变量
    test_env = {"DB_MYSQL_DNS": "mysql://test_user:test_pass@test_host:3306/test_db"}

    # 保存原始环境变量
    original_env = {}
    for key in test_env:
        if key in os.environ:
            original_env[key] = os.environ[key]

    try:
        # 设置测试环境变量
        for key, value in test_env.items():
            os.environ[key] = value

        print("设置环境变量:")
        for key, value in test_env.items():
            print(f"  {key}: {value}")

        # 创建配置对象
        config = DatabaseConfig()
        print(f"\n✅ 配置创建成功")
        print(f"MySQL DNS: {config.mysql_dns}")
        print(f"URL: {config.url}")

        params = config.connection_params
        print(f"\n解析的连接参数:")
        for key, value in params.items():
            if key == "password":
                display_value = "*" * len(str(value)) if value else "None"
            else:
                display_value = value
            print(f"  {key}: {display_value}")

    except Exception as e:
        print(f"❌ 配置创建失败: {e}")

    finally:
        # 恢复原始环境变量
        for key in test_env:
            if key in original_env:
                os.environ[key] = original_env[key]
            else:
                del os.environ[key]


def main():
    """主函数"""
    print("连接字符串配置测试工具")

    # 测试连接字符串解析
    test_connection_strings()

    # 测试环境变量配置
    test_environment_variables()

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    print("\n使用说明:")
    print("1. 设置环境变量: export DB_MYSQL_DNS='mysql://user:pass@host:port/db'")
    print("2. 或创建 .env 文件")
    print("3. 运行 python check_config.py 验证配置")
    print("4. 运行 python start_with_db.py 启动应用")


if __name__ == "__main__":
    main()
