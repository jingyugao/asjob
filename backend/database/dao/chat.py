from typing import Any, Dict, List, Optional
from pymysql.cursors import DictCursor

from backend.database.session import db_connection, create_tables


def ensure_tables() -> None:
    """Ensure chat related tables exist.

    This function also calls the global `create_tables` to ensure
    other base tables are created.
    """
    # Ensure base tables from session
    create_tables()

    create_conversations_sql = """
        CREATE TABLE IF NOT EXISTS conversations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """

    create_messages_sql = """
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

    with db_connection.get_cursor() as cursor:
        cursor.execute(create_conversations_sql)
        cursor.execute(create_messages_sql)


def create_conversation(cursor: DictCursor, title: Optional[str] = None) -> int:
    """Create a conversation and return its id."""
    cursor.execute("INSERT INTO conversations (title) VALUES (%s)", (title,))
    return cursor.lastrowid


def get_conversation(
    cursor: DictCursor, conversation_id: int
) -> Optional[Dict[str, Any]]:
    """Get a conversation row by id."""
    cursor.execute("SELECT * FROM conversations WHERE id=%s", (conversation_id,))
    row = cursor.fetchone()
    return row


def insert_message(
    cursor: DictCursor,
    conversation_id: int,
    role: str,
    content: str,
    name: Optional[str] = None,
    tool_call: Optional[Dict[str, Any]] = None,
) -> int:
    """Insert a message and return its id."""
    cursor.execute(
        "INSERT INTO messages (conversation_id, role, content, name, tool_call) VALUES (%s,%s,%s,%s,%s)",
        (
            conversation_id,
            role,
            content,
            name,
            json_dumps(tool_call) if tool_call else None,
        ),
    )
    return cursor.lastrowid


def list_messages_by_conversation(
    cursor: DictCursor, conversation_id: int
) -> List[Dict[str, Any]]:
    """List messages for a conversation ordered by id."""
    cursor.execute(
        "SELECT * FROM messages WHERE conversation_id=%s ORDER BY id",
        (conversation_id,),
    )
    rows = cursor.fetchall()
    return rows


def list_messages_for_response(
    cursor: DictCursor, conversation_id: int
) -> List[Dict[str, Any]]:
    """List messages with selected columns for API response."""
    cursor.execute(
        """
        SELECT id, conversation_id, role, content, name, tool_call, created_at
        FROM messages
        WHERE conversation_id=%s
        ORDER BY id
        """,
        (conversation_id,),
    )
    return cursor.fetchall()


def json_dumps(obj: Optional[Dict[str, Any]]) -> Optional[str]:
    if obj is None:
        return None
    import json as _json

    return _json.dumps(obj)
