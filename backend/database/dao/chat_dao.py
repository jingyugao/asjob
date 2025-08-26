import json
import logging
from typing import Any, Dict, List, Optional

from pymysql.cursors import DictCursor

from backend.database.model.chat import Conversation, Message

logger = logging.getLogger("chat_dao")


class ChatDAO:
    def __init__(self, cursor: DictCursor):
        self.cursor = cursor

    def ensure_tables(self):
        """确保聊天相关表存在"""
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                conversation_id INT NOT NULL,
                role VARCHAR(32) NOT NULL,
                content LONGTEXT NOT NULL,
                name VARCHAR(128) NULL,
                tool_call LONGTEXT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """
        )

    def create_conversation(self, title: Optional[str] = None) -> Conversation:
        """创建新会话"""
        self.cursor.execute(
            "INSERT INTO conversations (title) VALUES (%s)", (title,)
        )
        conv_id = self.cursor.lastrowid
        self.cursor.execute("SELECT * FROM conversations WHERE id=%s", (conv_id,))
        row = self.cursor.fetchone()
        return Conversation(**row)

    def get_conversation(self, conversation_id: int) -> Optional[Conversation]:
        """获取会话信息"""
        self.cursor.execute("SELECT * FROM conversations WHERE id=%s", (conversation_id,))
        row = self.cursor.fetchone()
        return Conversation(**row) if row else None

    def list_messages(self, conversation_id: int) -> List[Dict[str, Any]]:
        """获取会话的所有消息"""
        self.cursor.execute(
            "SELECT * FROM messages WHERE conversation_id=%s ORDER BY id",
            (conversation_id,),
        )
        rows = self.cursor.fetchall()
        # 反序列化 tool_call
        for row in rows:
            if row.get("tool_call") and isinstance(row["tool_call"], (str, bytes)):
                try:
                    row["tool_call"] = json.loads(row["tool_call"]) if row["tool_call"] else None
                except Exception:
                    pass
        return rows

    def get_message_history(self, conversation_id: int) -> List[Dict[str, Any]]:
        """获取消息历史，用于LLM调用"""
        self.cursor.execute(
            "SELECT role, content, name FROM messages WHERE conversation_id=%s ORDER BY id",
            (conversation_id,),
        )
        return self.cursor.fetchall()

    def save_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
        name: Optional[str] = None,
        tool_call: Optional[Dict[str, Any]] = None,
    ) -> int:
        """保存消息"""
        self.cursor.execute(
            "INSERT INTO messages (conversation_id, role, content, name, tool_call) VALUES (%s,%s,%s,%s,%s)",
            (
                conversation_id,
                role,
                content,
                name,
                json.dumps(tool_call) if tool_call else None,
            ),
        )
        return self.cursor.lastrowid
