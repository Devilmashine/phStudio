from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
import asyncio
import json
import logging
from ...core.database import get_db
from ...core.websocket_manager import ws_manager
from ...deps import get_current_employee
from ...models.employee_enhanced import Employee

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["websocket"])

@router.websocket("/kanban")
async def kanban_websocket(
    websocket: WebSocket,
    db: Session = Depends(get_db),
    employee: Employee = Depends(get_current_employee)
):
    """WebSocket endpoint for kanban board updates"""
    # Accept the WebSocket connection
    await websocket.accept()
    
    # Create a queue for this connection
    queue = asyncio.Queue()
    
    try:
        # Connect to the kanban room
        await ws_manager.connect(queue, "kanban_board")
        
        # Send initial connection message
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "message": f"Connected to kanban board updates as {employee.username}"
        }))
        
        # Handle incoming and outgoing messages
        while True:
            # Wait for either:
            # 1. A message from the client (ping/pong)
            # 2. A message from the queue (broadcast update)
            try:
                # Wait for client message with timeout
                client_msg_task = asyncio.create_task(websocket.receive_text())
                # Wait for broadcast message
                broadcast_msg_task = asyncio.create_task(queue.get())
                
                # Wait for whichever completes first
                done, pending = await asyncio.wait(
                    [client_msg_task, broadcast_msg_task],
                    return_when=asyncio.FIRST_COMPLETED,
                    timeout=30.0  # 30 second timeout
                )
                
                # Cancel pending tasks
                for task in pending:
                    task.cancel()
                
                # Process completed tasks
                for task in done:
                    if task == client_msg_task:
                        # Handle client message
                        try:
                            data = await task
                            message = json.loads(data)
                            
                            # Handle ping messages
                            if message.get("type") == "ping":
                                await websocket.send_text(json.dumps({
                                    "type": "pong",
                                    "timestamp": message.get("timestamp")
                                }))
                        except json.JSONDecodeError:
                            logger.warning("Received invalid JSON from client")
                        except Exception as e:
                            logger.error(f"Error processing client message: {e}")
                    
                    elif task == broadcast_msg_task:
                        # Handle broadcast message
                        try:
                            message = await task
                            await websocket.send_text(json.dumps(message))
                        except Exception as e:
                            logger.error(f"Error sending broadcast message: {e}")
            
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                try:
                    await websocket.send_text(json.dumps({
                        "type": "ping",
                        "timestamp": asyncio.get_event_loop().time()
                    }))
                except Exception:
                    # Connection likely closed
                    break
            except Exception as e:
                logger.error(f"Error in WebSocket loop: {e}")
                break
                
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        # Disconnect from manager
        await ws_manager.disconnect(queue)
        try:
            await websocket.close()
        except Exception:
            pass

@router.websocket("/notifications")
async def notifications_websocket(
    websocket: WebSocket,
    db: Session = Depends(get_db),
    employee: Employee = Depends(get_current_employee)
):
    """WebSocket endpoint for general notifications"""
    # Accept the WebSocket connection
    await websocket.accept()
    
    # Create a queue for this connection
    queue = asyncio.Queue()
    
    try:
        # Connect to the notifications room
        await ws_manager.connect(queue, "notifications")
        
        # Send initial connection message
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "message": f"Connected to notifications as {employee.username}"
        }))
        
        # Handle messages
        while True:
            try:
                # Wait for broadcast message
                message = await queue.get()
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error in notifications WebSocket: {e}")
                break
                
    except WebSocketDisconnect:
        logger.info("Notifications WebSocket disconnected")
    except Exception as e:
        logger.error(f"Notifications WebSocket error: {e}")
    finally:
        # Disconnect from manager
        await ws_manager.disconnect(queue)
        try:
            await websocket.close()
        except Exception:
            pass