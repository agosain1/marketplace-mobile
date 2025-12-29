from typing import Dict, Set
from fastapi import WebSocket
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for real-time messaging.
    Supports multiple connections per user (multi-device).
    """

    def __init__(self):
        # {user_id: Set of WebSocket connections}
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        """
        Accept and register a WebSocket connection.

        Args:
            websocket: The WebSocket connection
            user_id: UUID of the user as string
        """
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()

        self.active_connections[user_id].add(websocket)
        logger.info(f"User {user_id} connected. Total connections: {len(self.active_connections[user_id])}")

    def disconnect(self, websocket: WebSocket, user_id: str):
        """
        Remove a WebSocket connection and clean up if user has no more connections.

        Args:
            websocket: The WebSocket connection to remove
            user_id: UUID of the user as string
        """
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)

            # If no more connections, remove user entirely
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                logger.info(f"User {user_id} fully disconnected")
            else:
                logger.info(f"User {user_id} connection closed. Remaining: {len(self.active_connections[user_id])}")

    async def send_personal_message(self, message: dict, user_id: str):
        """
        Send a message to a specific user across all their connections.
        Automatically cleans up dead connections.

        Args:
            message: Dictionary to send as JSON
            user_id: UUID of the user as string
        """
        if user_id not in self.active_connections:
            logger.debug(f"User {user_id} not connected, message not sent")
            return

        disconnected = set()

        for connection in self.active_connections[user_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send message to {user_id}: {e}")
                disconnected.add(connection)

        # Clean up dead connections
        for conn in disconnected:
            self.active_connections[user_id].discard(conn)

        # Remove user if all connections are dead
        if not self.active_connections[user_id]:
            del self.active_connections[user_id]

    async def broadcast_user_status(self, user_id: str, status: str, exclude_user_id: str = None):
        """
        Notify all connected users about a user's status change (online/offline).

        Args:
            user_id: UUID of the user whose status changed
            status: "online" or "offline"
            exclude_user_id: Optional user ID to exclude from broadcast (typically the user themselves)
        """
        message = {
            "type": "user_status",
            "data": {
                "user_id": user_id,
                "status": status
            }
        }

        for uid in list(self.active_connections.keys()):
            if exclude_user_id and uid == exclude_user_id:
                continue
            await self.send_personal_message(message, uid)

    async def broadcast_unread_count_update(self, user_id: str, unread_count: int):
        """
        Notify a user about their updated unread message count.

        Args:
            user_id: UUID of the user
            unread_count: New unread message count
        """
        message = {
            "type": "unread_count_update",
            "data": {
                "unread_count": unread_count
            }
        }
        await self.send_personal_message(message, user_id)

    def is_user_online(self, user_id: str) -> bool:
        """
        Check if a user has any active connections.

        Args:
            user_id: UUID of the user as string

        Returns:
            True if user is connected, False otherwise
        """
        return user_id in self.active_connections and len(self.active_connections[user_id]) > 0

    def get_online_users(self) -> list:
        """
        Get list of all currently connected user IDs.

        Returns:
            List of user IDs (as strings)
        """
        return list(self.active_connections.keys())

    def get_connection_count(self, user_id: str) -> int:
        """
        Get the number of active connections for a user.

        Args:
            user_id: UUID of the user as string

        Returns:
            Number of active connections
        """
        if user_id in self.active_connections:
            return len(self.active_connections[user_id])
        return 0


# Global instance
manager = ConnectionManager()