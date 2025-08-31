from typing import Dict, Set, Any, Callable
import asyncio
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class WebSocketManager:
    """WebSocket connection manager for real-time updates"""
    
    def __init__(self):
        # Store active connections by room
        self.rooms: Dict[str, Set[asyncio.Queue]] = {}
        # Store connection metadata
        self.connections: Dict[asyncio.Queue, Dict[str, Any]] = {}
    
    async def connect(self, websocket_queue: asyncio.Queue, room: str = "default") -> None:
        """Add a new WebSocket connection to a room"""
        if room not in self.rooms:
            self.rooms[room] = set()
        
        self.rooms[room].add(websocket_queue)
        self.connections[websocket_queue] = {
            "room": room,
            "connected_at": datetime.now(),
            "last_activity": datetime.now()
        }
        
        logger.info(f"WebSocket connected to room '{room}'. Total connections: {len(self.rooms[room])}")
    
    async def disconnect(self, websocket_queue: asyncio.Queue) -> None:
        """Remove a WebSocket connection"""
        if websocket_queue in self.connections:
            room = self.connections[websocket_queue]["room"]
            
            # Remove from room
            if room in self.rooms and websocket_queue in self.rooms[room]:
                self.rooms[room].remove(websocket_queue)
                logger.info(f"WebSocket disconnected from room '{room}'. Remaining connections: {len(self.rooms[room])}")
            
            # Remove connection metadata
            del self.connections[websocket_queue]
    
    async def broadcast_to_room(self, room: str, message: Dict[str, Any]) -> None:
        """Broadcast a message to all connections in a room"""
        if room not in self.rooms:
            logger.debug(f"No connections in room '{room}' to broadcast to")
            return
        
        # Add timestamp to message
        message_with_timestamp = {
            **message,
            "timestamp": datetime.now().isoformat()
        }
        
        # Send to all connections in the room
        disconnected = set()
        for queue in self.rooms[room]:
            try:
                # Non-blocking put with timeout
                await asyncio.wait_for(queue.put(message_with_timestamp), timeout=1.0)
                # Update last activity
                if queue in self.connections:
                    self.connections[queue]["last_activity"] = datetime.now()
            except asyncio.TimeoutError:
                logger.warning(f"Timeout sending message to WebSocket connection")
                disconnected.add(queue)
            except Exception as e:
                logger.error(f"Error sending message to WebSocket connection: {e}")
                disconnected.add(queue)
        
        # Remove disconnected connections
        for queue in disconnected:
            await self.disconnect(queue)
    
    async def send_to_connection(self, websocket_queue: asyncio.Queue, message: Dict[str, Any]) -> None:
        """Send a message to a specific connection"""
        try:
            message_with_timestamp = {
                **message,
                "timestamp": datetime.now().isoformat()
            }
            await asyncio.wait_for(websocket_queue.put(message_with_timestamp), timeout=1.0)
            
            # Update last activity
            if websocket_queue in self.connections:
                self.connections[websocket_queue]["last_activity"] = datetime.now()
        except asyncio.TimeoutError:
            logger.warning("Timeout sending message to WebSocket connection")
            await self.disconnect(websocket_queue)
        except Exception as e:
            logger.error(f"Error sending message to WebSocket connection: {e}")
            await self.disconnect(websocket_queue)
    
    def get_room_connections(self, room: str) -> int:
        """Get the number of connections in a room"""
        return len(self.rooms.get(room, set()))
    
    def get_all_rooms(self) -> Dict[str, int]:
        """Get all rooms and their connection counts"""
        return {room: len(connections) for room, connections in self.rooms.items()}
    
    async def cleanup_inactive_connections(self, max_inactivity_minutes: int = 60) -> None:
        """Remove inactive connections"""
        now = datetime.now()
        inactive_connections = set()
        
        for queue, metadata in self.connections.items():
            inactivity = (now - metadata["last_activity"]).total_seconds() / 60
            if inactivity > max_inactivity_minutes:
                inactive_connections.add(queue)
        
        for queue in inactive_connections:
            await self.disconnect(queue)
            logger.info(f"Removed inactive WebSocket connection")

# Global WebSocket manager instance
ws_manager = WebSocketManager()