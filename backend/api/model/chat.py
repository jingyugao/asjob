from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class ChatReq(BaseModel):
    conversation_id: Optional[int] = Field(
        None, description="会话ID（可选，不传则新建）"
    )
    content: str = Field(..., description="用户输入")


class ChatRsp(BaseModel):
    conversation_id: int
    assistant_message: str
    tool_call: Optional[Dict[str, Any]] = None
    tool_result: Optional[Any] = None
    messages: List[Dict[str, Any]]


class ConversationCreateReq(BaseModel):
    title: Optional[str] = Field(None, description="会话标题")


class ConversationRsp(BaseModel):
    id: int
    title: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class MessageRsp(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    name: Optional[str] = None
    tool_call: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None
