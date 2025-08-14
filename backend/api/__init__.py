from fastapi import APIRouter
from backend.api.connector_api import router as connector_router

# 创建主路由
api_router = APIRouter(prefix="/api/v1")

# 注册子路由
api_router.include_router(connector_router, prefix="/connectors", tags=["connectors"])

__all__ = ["api_router"]
