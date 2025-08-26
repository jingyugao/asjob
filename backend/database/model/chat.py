from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel


class Conversation(BaseModel):
    id: Optional[int] = None
    title: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Message(BaseModel):
    id: Optional[int] = None
    conversation_id: int
    role: str
    content: str
    name: Optional[str] = None
    tool_call: Optional[str] = None
    created_at: Optional[datetime] = None
