from typing import List, Dict, Any
from fastapi import HTTPException
from api.database import get_db_cursor
import uuid

def send_message(sender_id: str, receiver_email: str, content: str) -> Dict[str, Any]:
    """
    Insert a new message into the messages table.
    """
    with get_db_cursor() as cur:
        # 1. Get receiver_id
        cur.execute("SELECT id FROM users WHERE email = %s", (receiver_email,))
        receiver_row = cur.fetchone()
        if not receiver_row:
            raise HTTPException(status_code=404, detail=f"Receiver with email {receiver_email} not found")
        receiver_id = receiver_row["id"]

        # 2. Insert the message
        cur.execute(
            """
            INSERT INTO messages (sender_id, receiver_id, content)
            VALUES (%s, %s, %s)
            RETURNING id, created_at
            """,
            (uuid.UUID(sender_id), receiver_id, content),
        )
        result = cur.fetchone()

    return {
        "message_id": str(result["id"]),
        "sender_id": str(sender_id),
        "receiver_id": str(receiver_id),
        "content": content,
        "created_at": result["created_at"].isoformat()
    }

def get_user_messages(user_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Get all messages for a user (both sent and received).
    """
    user_uuid = uuid.UUID(user_id)
    with get_db_cursor() as cur:
        cur.execute(
            """
            SELECT 
                m.id,
                m.sender_id,
                m.receiver_id,
                m.content,
                m.created_at,
                m.read_at,
                sender.email as sender_email,
                receiver.email as receiver_email
            FROM messages m
            JOIN users sender ON m.sender_id = sender.id
            JOIN users receiver ON m.receiver_id = receiver.id
            WHERE m.sender_id = %s OR m.receiver_id = %s
            ORDER BY m.created_at DESC
            LIMIT %s OFFSET %s
            """,
            (user_uuid, user_uuid, limit, offset)
        )
        messages = cur.fetchall()
        
    return [{
        "message_id": str(msg["id"]),
        "sender_id": str(msg["sender_id"]),
        "receiver_id": str(msg["receiver_id"]),
        "content": msg["content"],
        "created_at": msg["created_at"].isoformat(),
        "read_at": msg["read_at"].isoformat() if msg["read_at"] else None,
        "sender_email": msg["sender_email"],
        "receiver_email": msg["receiver_email"]
    } for msg in messages]

def get_conversation(user_id: str, other_user_email: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Get conversation between two users.
    """
    user_uuid = uuid.UUID(user_id)
    with get_db_cursor() as cur:
        # First get the other user's ID
        cur.execute("SELECT id FROM users WHERE email = %s", (other_user_email,))
        other_user = cur.fetchone()
        if not other_user:
            raise HTTPException(status_code=404, detail=f"User with email {other_user_email} not found")
        other_user_id = other_user["id"]
        
        # Get messages between the two users
        cur.execute(
            """
            SELECT 
                m.id,
                m.sender_id,
                m.receiver_id,
                m.content,
                m.created_at,
                m.read_at,
                sender.email as sender_email,
                receiver.email as receiver_email
            FROM messages m
            JOIN users sender ON m.sender_id = sender.id
            JOIN users receiver ON m.receiver_id = receiver.id
            WHERE (m.sender_id = %s AND m.receiver_id = %s) 
               OR (m.sender_id = %s AND m.receiver_id = %s)
            ORDER BY m.created_at ASC
            LIMIT %s OFFSET %s
            """,
            (user_uuid, other_user_id, other_user_id, user_uuid, limit, offset)
        )
        messages = cur.fetchall()
        
    return [{
        "message_id": str(msg["id"]),
        "sender_id": str(msg["sender_id"]),
        "receiver_id": str(msg["receiver_id"]),
        "content": msg["content"],
        "created_at": msg["created_at"].isoformat(),
        "read_at": msg["read_at"].isoformat() if msg["read_at"] else None,
        "sender_email": msg["sender_email"],
        "receiver_email": msg["receiver_email"]
    } for msg in messages]

def mark_message_as_read(message_id: str, user_id: str) -> Dict[str, Any]:
    """
    Mark a message as read (only receiver can mark as read).
    """
    msg_uuid = uuid.UUID(message_id)
    user_uuid = uuid.UUID(user_id)
    
    with get_db_cursor() as cur:
        # Verify the message exists and user is the receiver
        cur.execute(
            "SELECT id, receiver_id, read_at FROM messages WHERE id = %s",
            (msg_uuid,)
        )
        message = cur.fetchone()
        
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
            
        if message["receiver_id"] != user_uuid:
            raise HTTPException(status_code=403, detail="Only the receiver can mark message as read")
            
        if message["read_at"]:
            return {"message": "Message already marked as read", "read_at": message["read_at"].isoformat()}
        
        # Mark as read
        cur.execute(
            "UPDATE messages SET read_at = CURRENT_TIMESTAMP WHERE id = %s RETURNING read_at",
            (msg_uuid,)
        )
        result = cur.fetchone()
        
    return {
        "message": "Message marked as read",
        "read_at": result["read_at"].isoformat()
    }

def get_unread_messages_count(user_id: str) -> Dict[str, int]:
    """
    Get count of unread messages for a user.
    """
    user_uuid = uuid.UUID(user_id)
    with get_db_cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) as unread_count FROM messages WHERE receiver_id = %s AND read_at IS NULL",
            (user_uuid,)
        )
        result = cur.fetchone()
        
    return {"unread_count": result["unread_count"]}

def delete_message(message_id: str, user_id: str) -> Dict[str, str]:
    """
    Delete a message (only sender can delete).
    """
    msg_uuid = uuid.UUID(message_id)
    user_uuid = uuid.UUID(user_id)
    
    with get_db_cursor() as cur:
        # Verify the message exists and user is the sender
        cur.execute(
            "SELECT id, sender_id FROM messages WHERE id = %s",
            (msg_uuid,)
        )
        message = cur.fetchone()
        
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
            
        if message["sender_id"] != user_uuid:
            raise HTTPException(status_code=403, detail="Only the sender can delete the message")
        
        # Delete the message
        cur.execute("DELETE FROM messages WHERE id = %s", (msg_uuid,))
        
    return {"message": "Message deleted successfully"}