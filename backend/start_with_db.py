#!/usr/bin/env python3
"""
带数据库初始化的启动脚本
"""

import uvicorn
from database.init_db import init_database, test_connection
from database.session import get_connection_info


def main():
    """主函数"""
    print("=" * 60)
    print("Data Development Platform - 启动脚本")
    print("=" * 60)

    # 显示数据库配置信息
    connection_info = get_connection_info()
    print(f"数据库配置:")
    print(f"  MySQL DNS: {connection_info['mysql_dns']}")
    print(f"  SQLAlchemy URL: {connection_info['sqlalchemy_url']}")
    print(f"  解析参数: {connection_info['connection_params']}")
    print()

    print("正在检查数据库连接...")

    if test_connection():
        print("数据库连接正常，正在初始化...")
        try:
            init_database()
            print("数据库初始化完成")
        except Exception as e:
            print(f"数据库初始化失败: {e}")
            print("继续启动应用...")
    else:
        print("数据库连接失败，请检查配置")
        print("继续启动应用...")

    print("\n启动FastAPI应用...")
    print("API文档: http://localhost:8000/docs")
    print("健康检查: http://localhost:8000/api/health")
    print("=" * 60)

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")


if __name__ == "__main__":
    main()
