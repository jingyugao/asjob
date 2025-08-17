from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ConversationModel(BaseModel):
    """会话数据模型（数据库层）"""
    
    id: Optional[int] = Field(None, description="主键ID")
    title: Optional[str] = Field(None, description="会话标题")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    
    def __repr__(self) -> str:
        return f"<ConversationModel(id={self.id}, title='{self.title}')>"
    
    class Config:
        from_attributes = True


class MessageModel(BaseModel):
    """消息数据模型（数据库层）"""
    
    id: Optional[int] = Field(None, description="主键ID")
    conversation_id: int = Field(..., description="会话ID")
    role: str = Field(..., description="角色(user/assistant/system)")
    content: str = Field(..., description="消息内容")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    
    def __repr__(self) -> str:
        return f"<MessageModel(id={self.id}, conversation_id={self.conversation_id}, role='{self.role}')>"
    
    class Config:
        from_attributes = True