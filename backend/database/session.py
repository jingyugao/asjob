from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from .config import DatabaseConfig

Base = declarative_base()

# 创建数据库引擎
config = DatabaseConfig()


# 构建SQLAlchemy URL
def build_sqlalchemy_url():
    """构建SQLAlchemy连接URL"""
    mysql_dns = config.mysql_dns

    # 将mysql://转换为mysql+pymysql://
    if mysql_dns.startswith("mysql://"):
        sqlalchemy_url = mysql_dns.replace("mysql://", "mysql+pymysql://")
    else:
        sqlalchemy_url = mysql_dns

    return sqlalchemy_url


# 创建数据库引擎
engine = create_engine(
    build_sqlalchemy_url(),
    echo=False,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=10,
    max_overflow=20,
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session() -> Session:
    """获取数据库会话"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def create_tables():
    """创建所有表"""
    Base.metadata.create_all(bind=engine)


def get_connection_info():
    """获取连接信息（用于调试）"""
    return {
        "mysql_dns": config.mysql_dns,
        "sqlalchemy_url": build_sqlalchemy_url(),
        "connection_params": config.connection_params,
    }
