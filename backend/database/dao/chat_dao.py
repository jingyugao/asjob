from typing import List, Optional, Dict, Any, Tuple
from pymysql.cursors import DictCursor
from backend.database.model.chat import ConversationModel, MessageModel
import json


class ChatDAO:
    """聊天相关数据访问对象"""

    def __init__(self, cursor: DictCursor):
        self.cursor = cursor

    def ensure_tables(self):
        """确保聊天相关表存在"""
        # 创建conversations表
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
        
        # 创建messages表
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                conversation_id INT NOT NULL,
                role VARCHAR(20) NOT NULL,
                content TEXT NOT NULL,
                name VARCHAR(255) NULL,
                tool_call JSON NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """
        )

    def create_conversation(self, title: Optional[str] = None) -> Dict[str, Any]:
        """创建新的会话"""
        self.cursor.execute("INSERT INTO conversations (title) VALUES (%s)", (title,))
        conversation_id = self.cursor.lastrowid
        
        # 获取创建的会话
        self.cursor.execute("SELECT * FROM conversations WHERE id=%s", (conversation_id,))
        return self.cursor.fetchone()

    def get_conversation(self, conversation_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取会话"""
        self.cursor.execute("SELECT * FROM conversations WHERE id=%s", (conversation_id,))
        return self.cursor.fetchone()

    def list_messages(self, conversation_id: int) -> List[Dict[str, Any]]:
        """获取会话的所有消息"""
        self.cursor.execute(
            "SELECT * FROM messages WHERE conversation_id=%s ORDER BY id",
            (conversation_id,),
        )
        return self.cursor.fetchall()

    def load_history(self, conversation_id: int) -> List[Tuple[str, str, Optional[str]]]:
        """加载会话历史（用于LLM上下文）"""
        self.cursor.execute(
            "SELECT role, content, name FROM messages WHERE conversation_id=%s ORDER BY id",
            (conversation_id,),
        )
        return [(msg["role"], msg["content"], msg.get("name")) for msg in self.cursor.fetchall()]

    def insert_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
        name: Optional[str] = None,
        tool_call: Optional[Dict[str, Any]] = None,
    ) -> int:
        """插入新消息"""
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

    def get_messages_after_id(self, conversation_id: int, after_id: int = 0) -> List[Dict[str, Any]]:
        """获取指定ID之后的所有消息"""
        self.cursor.execute(
            """
            SELECT id, conversation_id, role, content, name, tool_call, created_at 
            FROM messages 
            WHERE conversation_id=%s AND id > %s 
            ORDER BY id
            """,
            (conversation_id, after_id),
        )
        messages = self.cursor.fetchall()
        
        # 解析tool_call JSON字段
        for msg in messages:
            if msg.get("tool_call") and isinstance(msg["tool_call"], str):
                try:
                    msg["tool_call"] = json.loads(msg["tool_call"])
                except json.JSONDecodeError:
                    msg["tool_call"] = None
        
        return messages

    def get_all_conversations(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """获取所有会话列表"""
        self.cursor.execute(
            """
            SELECT c.*, 
                   (SELECT COUNT(*) FROM messages WHERE conversation_id = c.id) as message_count,
                   (SELECT MAX(created_at) FROM messages WHERE conversation_id = c.id) as last_message_at
            FROM conversations c
            ORDER BY c.updated_at DESC
            LIMIT %s OFFSET %s
            """,
            (limit, skip)
        )
        return self.cursor.fetchall()

    def update_conversation_title(self, conversation_id: int, title: str) -> bool:
        """更新会话标题"""
        self.cursor.execute(
            "UPDATE conversations SET title=%s WHERE id=%s",
            (title, conversation_id)
        )
        return self.cursor.rowcount > 0

    def delete_conversation(self, conversation_id: int) -> bool:
        """删除会话（级联删除所有消息）"""
        self.cursor.execute("DELETE FROM conversations WHERE id=%s", (conversation_id,))
        return self.cursor.rowcount > 0