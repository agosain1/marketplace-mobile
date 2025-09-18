from typing import List, Dict, Any
from fastapi import HTTPException
from models import Users, Messages
from sqlalchemy.orm import Session
import uuid
import datetime

def get_all_messages(query, db: Session):
    result = []
    for msg in query:
        # Get sender and receiver info
        sender = db.query(Users).filter(Users.id == msg.sender_id).first()
        receiver = db.query(Users).filter(Users.id == msg.receiver_id).first()

        result.append({
            "message_id": str(msg.id),
            "sender_id": str(msg.sender_id),
            "receiver_id": str(msg.receiver_id),
            "content": msg.content,
            "created_at": msg.created_at.isoformat() if msg.created_at else None,
            "read_at": msg.read_at.isoformat() if msg.read_at else None,
            "sender_email": sender.email if sender else None,
            "receiver_email": receiver.email if receiver else None,
            "sender_name": f"{sender.fname} {sender.lname}" if sender else None,
            "receiver_name": f"{receiver.fname} {receiver.lname}" if receiver else None
        })

    return result

def send_message(sender_id: str, receiver_email: str, content: str, db: Session) -> Dict[str, Any]:
    """
    Insert a new message into the messages table.
    """
    # 1. Get receiver by email
    receiver = db.query(Users).filter(Users.email == receiver_email).first()
    if not receiver:
        raise HTTPException(status_code=404, detail=f"Receiver with email {receiver_email} not found")

    # 2. Create and insert the message
    new_message = Messages(
        sender_id=uuid.UUID(sender_id),
        receiver_id=receiver.id,
        content=content
    )
    
    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    return {
        "message_id": str(new_message.id),
        "sender_id": str(sender_id),
        "receiver_id": str(receiver.id),
        "content": content,
        "created_at": new_message.created_at.isoformat() if new_message.created_at else None
    }

def get_user_messages(user_id: str, limit: int = 50, offset: int = 0, db: Session = None) -> List[Dict[str, Any]]:
    """
    Get all messages for a user (both sent and received).
    """
    user_uuid = uuid.UUID(user_id)
    
    # Use separate queries for sender and receiver data for clearer results
    query = db.query(
        Messages.id,
        Messages.sender_id,
        Messages.receiver_id,
        Messages.content,
        Messages.created_at,
        Messages.read_at
    ).filter(
        (Messages.sender_id == user_uuid) | (Messages.receiver_id == user_uuid)
    ).order_by(
        Messages.created_at.desc()
    ).limit(limit).offset(offset).all()
        
    return get_all_messages(query, db)

def get_conversation(user_id: str, other_user_email: str, limit: int = 50, offset: int = 0, db: Session = None) -> List[Dict[str, Any]]:
    """
    Get conversation between two users.
    """
    user_uuid = uuid.UUID(user_id)
    
    # First get the other user's ID
    other_user = db.query(Users).filter(Users.email == other_user_email).first()
    if not other_user:
        raise HTTPException(status_code=404, detail=f"User with email {other_user_email} not found")
    
    # Get messages between the two users
    messages = db.query(Messages).filter(
        ((Messages.sender_id == user_uuid) & (Messages.receiver_id == other_user.id)) |
        ((Messages.sender_id == other_user.id) & (Messages.receiver_id == user_uuid))
    ).order_by(
        Messages.created_at.asc()
    ).limit(limit).offset(offset).all()

    return get_all_messages(messages, db)

def mark_message_as_read(message_id: str, user_id: str, db: Session) -> Dict[str, Any]:
    """
    Mark a message as read (only receiver can mark as read).
    """
    msg_uuid = uuid.UUID(message_id)
    user_uuid = uuid.UUID(user_id)
    
    # Find the message
    message = db.query(Messages).filter(Messages.id == msg_uuid).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
        
    if message.receiver_id != user_uuid:
        raise HTTPException(status_code=403, detail="Only the receiver can mark message as read")
        
    if message.read_at:
        return {"message": "Message already marked as read", "read_at": message.read_at.isoformat()}
    
    # Mark as read
    message.read_at = datetime.datetime.now(datetime.timezone.utc)
    db.commit()
    
    return {
        "message": "Message marked as read",
        "read_at": message.read_at.isoformat()
    }

def get_unread_messages_count(user_id: str, db: Session) -> Dict[str, int]:
    """
    Get count of unread messages for a user.
    """
    user_uuid = uuid.UUID(user_id)
    
    unread_count = db.query(Messages).filter(
        Messages.receiver_id == user_uuid,
        Messages.read_at.is_(None)
    ).count()
    
    return {"unread_count": unread_count}

def delete_message(message_id: str, user_id: str, db: Session) -> Dict[str, str]:
    """
    Delete a message (only sender can delete).
    """
    msg_uuid = uuid.UUID(message_id)
    user_uuid = uuid.UUID(user_id)
    
    # Find the message
    message = db.query(Messages).filter(Messages.id == msg_uuid).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
        
    if message.sender_id != user_uuid:
        raise HTTPException(status_code=403, detail="Only the sender can delete the message")
    
    # Delete the message
    db.delete(message)
    db.commit()
    
    return {"message": "Message deleted successfully"}