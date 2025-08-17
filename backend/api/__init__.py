from fastapi import APIRouter
from backend.api.connector_api import router as connector_router
from backend.api.knowledge_api import router as knowledge_router
from backend.api.chat import router as chat_router
from backend.api.scheduler_api import router as scheduler_router

# 创建主路由
api_router = APIRouter(prefix="/api/v1")

# 注册子路由
api_router.include_router(connector_router, prefix="/connectors", tags=["connectors"])
api_router.include_router(knowledge_router, prefix="/knowledge", tags=["knowledge"])
api_router.include_router(chat_router, prefix="/chat", tags=["chat"])
api_router.include_router(scheduler_router, prefix="/scheduler", tags=["scheduler"])

__all__ = ["api_router"]
