from backend.database.session import create_tables, get_connection_info, db_connection
from backend.database.model.connector import ConnectorModel
from backend.logger import get_logger


def init_database():
    """初始化数据库"""
    logger = get_logger("database.init_db")
    # 显示连接信息
    connection_info = get_connection_info()
    logger.info("数据库连接信息")
    logger.info(f"MySQL DNS: {connection_info['mysql_dns']}")
    logger.info(f"解析参数: {connection_info['connection_params']}")

    # 创建表
    create_tables()

    try:
        # 检查是否已有数据
        with db_connection.get_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM connectors")
            result = cursor.fetchone()
            existing_count = result["count"] if result else 0

            if existing_count == 0:
                # 创建示例连接器
                sample_connectors = [
                    {
                        "name": "local_mysql",
                        "db_type": "mysql",
                        "host": "localhost",
                        "port": 3306,
                        "username": "root",
                        "password": "password",
                        "database_name": "test",
                        "description": "本地MySQL测试数据库",
                        "is_active": True,
                    },
                    {
                        "name": "local_doris",
                        "db_type": "doris",
                        "host": "localhost",
                        "port": 9030,
                        "username": "root",
                        "password": "",
                        "database_name": "test",
                        "description": "本地Doris测试数据库",
                        "is_active": True,
                    },
                ]

                for connector_data in sample_connectors:
                    sql = """
                    INSERT INTO connectors (name, db_type, host, port, username, password, database_name, description, is_active)
                    VALUES (%(name)s, %(db_type)s, %(host)s, %(port)s, %(username)s, %(password)s, %(database_name)s, %(description)s, %(is_active)s)
                    """
                    cursor.execute(sql, connector_data)

                logger.info("数据库初始化完成，已创建示例连接器")
            else:
                logger.info("数据库已存在数据，跳过初始化")

    except Exception as e:
        logger.exception(f"数据库初始化失败: {e}")


def test_connection():
    """测试数据库连接"""
    logger = get_logger("database.init_db")
    try:
        # 显示连接信息
        connection_info = get_connection_info()
        logger.info("正在测试数据库连接...")
        logger.info(f"连接字符串: {connection_info['mysql_dns']}")

        with db_connection.get_cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result:
                logger.info("数据库连接测试成功")
                return True
            else:
                logger.error("数据库连接测试失败")
                return False
    except Exception as e:
        logger.error(f"数据库连接测试失败: {e}")
        return False


if __name__ == "__main__":
    if test_connection():
        init_database()
    else:
        logger = get_logger("database.init_db")
        logger.error("无法连接到数据库，请检查配置")
        logger.info(
            "请检查以下配置: 1) 环境变量 DB_MYSQL_DNS 是否正确设置 2) MySQL 服务是否运行 3) 用户名和密码是否正确 4) 数据库是否存在"
        )
