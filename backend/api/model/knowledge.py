from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class KnowledgeCreateReq(BaseModel):
    target_type: str = Field(..., description="目标类型: database|table|field")
    target_name: str = Field(..., description="目标名称: connector::db::table::field")
    content: str = Field(..., description="知识内容")
    created_by: str = Field(..., description="创建者")


class KnowledgeUpdateReq(BaseModel):
    content: str = Field(..., description="知识内容")


class KnowledgeRsp(BaseModel):
    id: int
    target_type: str
    target_name: str
    content: str
    created_by: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class KnowledgeListRsp(BaseModel):
    items: List[KnowledgeRsp]
