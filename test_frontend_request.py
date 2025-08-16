#!/usr/bin/env python3
"""模拟前端发送的请求，测试API接口"""

import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000"


def test_frontend_request():
    """模拟前端发送的请求"""

    # 模拟前端发送的数据（从你提供的curl请求中提取）
    connection_data = {
        "name": "dev",
        "host": "localhost",
        "port": 3306,
        "username": "root",
        "password": "Str0ngP@ssw0rd!",
        "database": "chatjob",
        "db_type": "mysql",
    }

    print("模拟前端请求数据:")
    print(json.dumps(connection_data, indent=2, ensure_ascii=False))
    print()

    try:
        # 发送POST请求到/api/connections
        response = requests.post(
            f"{BASE_URL}/api/connections",
            json=connection_data,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/plain, */*",
                "Origin": "http://localhost:3000",
                "Referer": "http://localhost:3000/database",
            },
        )

        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应内容: {response.text}")

        if response.status_code == 200:
            print("✅ 请求成功!")
        else:
            print("❌ 请求失败!")

        return response.status_code == 200

    except Exception as e:
        print(f"请求异常: {e}")
        return False


def test_validation_error():
    """测试数据验证错误"""

    # 测试缺少必需字段的情况
    invalid_data = {
        "name": "test",
        "host": "localhost",
        # 缺少 port, username, password, database, db_type
    }

    print("\n测试数据验证错误:")
    print("缺少必需字段的数据:")
    print(json.dumps(invalid_data, indent=2, ensure_ascii=False))
    print()

    try:
        response = requests.post(
            f"{BASE_URL}/api/connections",
            json=invalid_data,
            headers={"Content-Type": "application/json"},
        )

        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")

    except Exception as e:
        print(f"请求异常: {e}")


def main():
    """主函数"""
    print("前端请求模拟测试")
    print("=" * 50)

    # 测试正常请求
    test_frontend_request()

    # 测试验证错误
    test_validation_error()


if __name__ == "__main__":
    main()
