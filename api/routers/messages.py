from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.routers.auth import verify_jwt_token
from api.database import get_db
from api.services.messaging_service import (
    send_message,
    get_user_messages,
    get_conversation,
    mark_message_as_read,
    get_unread_messages_count,
    delete_message
)

router = APIRouter(
    prefix="/messages",
    tags=["messages"]
)

class SendMessageRequest(BaseModel):
    receiver_email: str
    content: str

@router.post("/send")
def send_message_endpoint(
    message_data: SendMessageRequest,
    token_data: dict = Depends(verify_jwt_token),
    db: Session = Depends(get_db)
):
    """
    Send a new message to another user.
    """
    sender_id = token_data['uuid']
    return send_message(sender_id, message_data.receiver_email, message_data.content, db)

@router.get("/user-messages")
def get_user_messages_endpoint(
    limit: int = 50,
    offset: int = 0,
    token_data: dict = Depends(verify_jwt_token),
    db: Session = Depends(get_db)
):
    """
    Get all messages for the current user (both sent and received).
    """
    user_id = token_data['uuid']
    return get_user_messages(user_id, limit, offset, db)

@router.get("/conversation/{other_user_email}")
def get_conversation_endpoint(
    other_user_email: str,
    limit: int = 50,
    offset: int = 0,
    token_data: dict = Depends(verify_jwt_token),
    db: Session = Depends(get_db)
):
    """
    Get conversation between the current user and another user.
    """
    user_id = token_data['uuid']
    return get_conversation(user_id, other_user_email, limit, offset, db)

@router.patch("/{message_id}/read")
def mark_message_read_endpoint(
    message_id: str,
    token_data: dict = Depends(verify_jwt_token),
    db: Session = Depends(get_db)
):
    """
    Mark a message as read.
    """
    user_id = token_data['uuid']
    return mark_message_as_read(message_id, user_id, db)

@router.get("/unread-count")
def get_unread_count_endpoint(
    token_data: dict = Depends(verify_jwt_token),
    db: Session = Depends(get_db)
):
    """
    Get count of unread messages for the current user.
    """
    user_id = token_data['uuid']
    return get_unread_messages_count(user_id, db)

@router.delete("/{message_id}")
def delete_message_endpoint(
    message_id: str,
    token_data: dict = Depends(verify_jwt_token),
    db: Session = Depends(get_db)
):
    """
    Delete a message (only sender can delete).
    """
    user_id = token_data['uuid']
    return delete_message(message_id, user_id, db)