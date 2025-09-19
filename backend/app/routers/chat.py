# chat.py
from typing import Dict
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from ..auth import decode_access_token_user_id


router = APIRouter(prefix="/chat", tags=["chat"])


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int) -> None:
        self.active_connections.pop(user_id, None)

    async def send_personal_message(self, user_id: int, message: str) -> None:
        ws = self.active_connections.get(user_id)
        if ws:
            await ws.send_text(message)

    async def broadcast(self, message: str) -> None:
        for ws in self.active_connections.values():
            await ws.send_text(message)


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    try:
        user_id = decode_access_token_user_id(token)
    except ValueError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(user_id, websocket)
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                obj = json.loads(raw)
                to_user_id = int(obj.get("to_user_id")) if obj.get("to_user_id") is not None else None
                text = str(obj.get("text", ""))
                image_url = obj.get("image_url")
            except Exception:
                to_user_id = None
                text = raw
                image_url = None

            payload = json.dumps({"sender_id": user_id, "text": text, "image_url": image_url, "to_user_id": to_user_id})

            if to_user_id and to_user_id in manager.active_connections:
                # Адресная доставка + эхо отправителю
                await manager.send_personal_message(to_user_id, payload)
                if to_user_id != user_id:
                    await manager.send_personal_message(user_id, payload)
            else:
                # Без указания получателя — эхо только отправителю (никакого broadcast)
                await manager.send_personal_message(user_id, payload)
    except WebSocketDisconnect:
        manager.disconnect(user_id)


