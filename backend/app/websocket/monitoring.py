import json
from typing import List, Dict, Any
from fastapi import WebSocket, WebSocketDisconnect


class ConnectionManager:
    """
    WebSocket Connection Manager for /ws/monitoring endpoint.
    Manages active client connections and broadcasts live machine status updates & alerts.
    """

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, data: Dict[str, Any], alert: Dict[str, Any] = None):
        """Broadcast machine condition report and optional alert to all active WebSocket clients."""
        payload = {
            "type": "TELEMETRY_UPDATE",
            "data": data,
            "alert": alert
        }
        json_msg = json.dumps(payload)

        disconnected_clients = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json_msg)
            except Exception:
                disconnected_clients.append(connection)

        for client in disconnected_clients:
            self.disconnect(client)


# Singleton manager instance
ws_manager = ConnectionManager()
