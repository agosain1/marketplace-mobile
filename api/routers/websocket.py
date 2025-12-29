from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from jose import jwt
import os
import logging
from dotenv import load_dotenv

from db.database import get_db
from services.websocket_manager import manager
from services.messaging_service import send_message, mark_message_as_read, get_unread_messages_count
from models import Users, Messages
import uuid

load_dotenv()

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ws",
    tags=["websocket"]
)

JWT_SECRET = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")


def get_user_from_websocket(websocket: WebSocket):
    """
    Extract and verify JWT token from WebSocket cookie header.
    Returns user_id if valid, None otherwise.
    """
    try:
        # Get cookie header from WebSocket
        cookie_header = websocket.headers.get('cookie', '')

        # Parse cookies to find auth_token
        auth_token = None
        for cookie in cookie_header.split(';'):
            cookie = cookie.strip()
            if cookie.startswith('auth_token='):
                auth_token = cookie.split('auth_token=')[1]
                break

        if not auth_token:
            logger.warning("No auth_token found in WebSocket cookies")
            return None

        # Verify JWT token
        payload = jwt.decode(auth_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get('uuid')

        if not user_id:
            logger.warning("No uuid found in JWT payload")
            return None

        return user_id

    except jwt.ExpiredSignatureError:
        logger.warning("JWT token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {e}")
        return None
    except Exception as e:
        logger.error(f"Error extracting user from WebSocket: {e}")
        return None


@router.websocket("/messages")
async def websocket_endpoint(
    websocket: WebSocket,
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time messaging.

    Authentication:
    - Uses existing auth_token cookie (automatically sent with WebSocket handshake)
    - No separate token needed

    Message format from client:
    {
        "type": "send_message" | "mark_read" | "typing_start" | "typing_stop" | "get_unread_count",
        "data": { ... }
    }

    Message format to client:
    {
        "type": "message_received" | "read_receipt" | "typing_indicator" | "user_status" | "unread_count_update",
        "data": { ... }
    }
    """

    # Authenticate user from cookie
    user_id = get_user_from_websocket(websocket)

    if not user_id:
        await websocket.close(code=4001, reason="Unauthorized")
        return

    logger.info(f"WebSocket connection attempt from user {user_id}")

    # Connect user
    await manager.connect(websocket, user_id)

    # Notify others that user is online
    await manager.broadcast_user_status(user_id, "online", exclude_user_id=user_id)

    # Send initial unread count
    try:
        unread_data = get_unread_messages_count(user_id, db)
        await manager.send_personal_message({
            "type": "unread_count_update",
            "data": unread_data
        }, user_id)
    except Exception as e:
        logger.error(f"Error sending initial unread count: {e}")

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message_type = data.get("type")
            message_data = data.get("data", {})

            logger.debug(f"Received WebSocket message type: {message_type} from user {user_id}")

            if message_type == "send_message":
                """
                Client sends: {
                    "type": "send_message",
                    "data": {
                        "receiver_email": "user@example.com",
                        "content": "Hello!"
                    }
                }
                """
                receiver_email = message_data.get("receiver_email")
                content = message_data.get("content")

                if not receiver_email or not content:
                    await websocket.send_json({
                        "type": "error",
                        "data": {"message": "Missing receiver_email or content"}
                    })
                    continue

                try:
                    # Store message in database
                    result = send_message(user_id, receiver_email, content, db)

                    # Get receiver info
                    receiver = db.query(Users).filter(Users.email == receiver_email).first()

                    if receiver:
                        receiver_id = str(receiver.id)

                        # Add sender info to result
                        sender = db.query(Users).filter(Users.id == uuid.UUID(user_id)).first()
                        result["sender_email"] = sender.email if sender else None
                        result["sender_name"] = f"{sender.fname} {sender.lname}" if sender else None
                        result["receiver_email"] = receiver.email
                        result["receiver_name"] = f"{receiver.fname} {receiver.lname}"

                        # Send to receiver if online
                        await manager.send_personal_message({
                            "type": "message_received",
                            "data": result
                        }, receiver_id)

                        # Update receiver's unread count
                        unread_data = get_unread_messages_count(receiver_id, db)
                        await manager.broadcast_unread_count_update(receiver_id, unread_data["unread_count"])

                        # Confirm to sender
                        await manager.send_personal_message({
                            "type": "message_sent",
                            "data": result
                        }, user_id)
                    else:
                        await websocket.send_json({
                            "type": "error",
                            "data": {"message": "Receiver not found"}
                        })

                except Exception as e:
                    logger.error(f"Error sending message: {e}")
                    await websocket.send_json({
                        "type": "error",
                        "data": {"message": str(e)}
                    })

            elif message_type == "mark_read":
                """
                Client sends: {
                    "type": "mark_read",
                    "data": {
                        "message_id": "uuid"
                    }
                }
                """
                message_id = message_data.get("message_id")

                if not message_id:
                    await websocket.send_json({
                        "type": "error",
                        "data": {"message": "Missing message_id"}
                    })
                    continue

                try:
                    # Mark as read
                    result = mark_message_as_read(message_id, user_id, db)

                    # Get message to find sender
                    msg = db.query(Messages).filter(Messages.id == uuid.UUID(message_id)).first()

                    if msg:
                        # Send read receipt to sender
                        await manager.send_personal_message({
                            "type": "read_receipt",
                            "data": {
                                "message_id": message_id,
                                "read_at": result.get("read_at"),
                                "reader_id": user_id
                            }
                        }, str(msg.sender_id))

                        # Update current user's unread count
                        unread_data = get_unread_messages_count(user_id, db)
                        await manager.broadcast_unread_count_update(user_id, unread_data["unread_count"])

                except Exception as e:
                    logger.error(f"Error marking message as read: {e}")
                    await websocket.send_json({
                        "type": "error",
                        "data": {"message": str(e)}
                    })

            elif message_type == "typing_start":
                """
                Client sends: {
                    "type": "typing_start",
                    "data": {
                        "receiver_id": "uuid"
                    }
                }
                """
                receiver_id = message_data.get("receiver_id")

                if receiver_id:
                    # Get sender info
                    sender = db.query(Users).filter(Users.id == uuid.UUID(user_id)).first()

                    await manager.send_personal_message({
                        "type": "typing_indicator",
                        "data": {
                            "user_id": user_id,
                            "user_email": sender.email if sender else None,
                            "typing": True
                        }
                    }, receiver_id)

            elif message_type == "typing_stop":
                """
                Client sends: {
                    "type": "typing_stop",
                    "data": {
                        "receiver_id": "uuid"
                    }
                }
                """
                receiver_id = message_data.get("receiver_id")

                if receiver_id:
                    # Get sender info
                    sender = db.query(Users).filter(Users.id == uuid.UUID(user_id)).first()

                    await manager.send_personal_message({
                        "type": "typing_indicator",
                        "data": {
                            "user_id": user_id,
                            "user_email": sender.email if sender else None,
                            "typing": False
                        }
                    }, receiver_id)

            elif message_type == "get_unread_count":
                """
                Client sends: {
                    "type": "get_unread_count",
                    "data": {}
                }
                """
                try:
                    unread_data = get_unread_messages_count(user_id, db)
                    await manager.send_personal_message({
                        "type": "unread_count_update",
                        "data": unread_data
                    }, user_id)
                except Exception as e:
                    logger.error(f"Error getting unread count: {e}")
                    await websocket.send_json({
                        "type": "error",
                        "data": {"message": str(e)}
                    })

            else:
                logger.warning(f"Unknown message type: {message_type}")
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": f"Unknown message type: {message_type}"}
                })

    except WebSocketDisconnect:
        logger.info(f"User {user_id} disconnected")
        manager.disconnect(websocket, user_id)

        # Only broadcast offline if user has no more connections
        if not manager.is_user_online(user_id):
            await manager.broadcast_user_status(user_id, "offline")

    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(websocket, user_id)

        if not manager.is_user_online(user_id):
            await manager.broadcast_user_status(user_id, "offline")