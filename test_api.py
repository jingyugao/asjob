#!/usr/bin/env python3
"""测试API接口的脚本"""

import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000"


def test_health_check():
    """测试健康检查接口"""
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"健康检查: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"健康检查失败: {e}")
        return False


def test_add_connection():
    """测试添加数据库连接接口"""
    connection_data = {
        "name": "dev",
        "host": "localhost",
        "port": 3306,
        "username": "root",
        "password": "Str0ngP@ssw0rd!",
        "database": "asjob",
        "db_type": "mysql",
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/connections",
            json=connection_data,
            headers={"Content-Type": "application/json"},
        )

        print(f"添加连接: {response.status_code}")
        if response.status_code == 200:
            print(f"成功: {response.json()}")
        else:
            print(f"错误: {response.text}")

        return response.status_code == 200
    except Exception as e:
        print(f"添加连接失败: {e}")
        return False


def test_get_connections():
    """测试获取连接列表接口"""
    try:
        response = requests.get(f"{BASE_URL}/api/connections")
        print(f"获取连接: {response.status_code}")
        if response.status_code == 200:
            connections = response.json()
            print(f"连接数量: {len(connections)}")
            for conn in connections:
                print(f"  - {conn['name']}: {conn['host']}:{conn['port']}")
        else:
            print(f"错误: {response.text}")

        return response.status_code == 200
    except Exception as e:
        print(f"获取连接失败: {e}")
        return False


def test_connector_api():
    """测试connector API接口"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/connectors")
        print(f"Connector API: {response.status_code}")
        if response.status_code == 200:
            connectors = response.json()
            print(f"连接器数量: {len(connectors)}")
        else:
            print(f"错误: {response.text}")

        return response.status_code == 200
    except Exception as e:
        print(f"Connector API失败: {e}")
        return False


def main():
    """主测试函数"""
    print("API接口测试")
    print("=" * 50)

    # 测试健康检查
    if not test_health_check():
        print("❌ 服务不可用，请检查后端是否启动")
        return

    print("\n✅ 服务可用，继续测试...\n")

    # 测试connector API
    test_connector_api()

    print("\n" + "-" * 30 + "\n")

    # 测试connections API
    test_add_connection()
    test_get_connections()


if __name__ == "__main__":
    main()
