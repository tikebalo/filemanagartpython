from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from typing import Dict, Set
import json

from app.database import get_db
from app.utils.security import decode_token
from app.models.user import User

router = APIRouter()

# Active WebSocket connections
active_connections: Dict[int, Set[WebSocket]] = {}


async def get_user_from_token(token: str, db: Session) -> User:
    """Get user from JWT token"""
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    user = db.query(User).filter(User.id == int(user_id)).first()
    return user


@router.websocket("")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()

    user = None
    try:
        # Wait for authentication
        auth_message = await websocket.receive_text()
        auth_data = json.loads(auth_message)

        token = auth_data.get("token")
        if not token:
            await websocket.send_json({"type": "error", "message": "No token provided"})
            await websocket.close()
            return

        user = await get_user_from_token(token, db)
        if not user:
            await websocket.send_json({"type": "error", "message": "Invalid token"})
            await websocket.close()
            return

        # Add connection
        if user.id not in active_connections:
            active_connections[user.id] = set()
        active_connections[user.id].add(websocket)

        # Send connection success
        await websocket.send_json({"type": "connected", "message": "Connected successfully"})

        # Keep connection alive
        while True:
            data = await websocket.receive_text()
            # Echo back or process commands
            await websocket.send_json({"type": "pong", "data": data})

    except WebSocketDisconnect:
        if user and user.id in active_connections:
            active_connections[user.id].discard(websocket)
            if not active_connections[user.id]:
                del active_connections[user.id]

    except Exception as e:
        if user and user.id in active_connections:
            active_connections[user.id].discard(websocket)
            if not active_connections[user.id]:
                del active_connections[user.id]


async def broadcast_to_user(user_id: int, message: dict):
    """Broadcast message to all user's connections"""
    if user_id in active_connections:
        for connection in active_connections[user_id]:
            try:
                await connection.send_json(message)
            except:
                pass


async def broadcast_to_all(message: dict):
    """Broadcast message to all connected users"""
    for connections in active_connections.values():
        for connection in connections:
            try:
                await connection.send_json(message)
            except:
                pass
