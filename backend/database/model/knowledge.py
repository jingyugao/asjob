from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class KnowledgeModel(BaseModel):
    id: Optional[int] = Field(None, description="主键ID")
    target_type: str = Field("", description="目标类型")
    target_name: str = Field("", description="目标名称")
    content: str = Field("", description="知识内容")
    created_by: str = Field("", description="创建者")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
