import sys
from pathlib import Path

# Ensure project root is available on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from backend.app.routes.api import router as api_router
from backend.app.websocket.monitoring import ws_manager
from backend.app.services.simulator_service import simulator_service

app = FastAPI(
    title="IoT Industrial Anomaly Detection System API",
    description="FastAPI Backend for real-time industrial telemetry, ML anomaly detection, fault classification, and alert monitoring.",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount REST API Routes
app.include_router(api_router)


# Register simulator broadcast callback to WebSocket manager
async def broadcast_telemetry(result, alert):
    await ws_manager.broadcast(result, alert)

simulator_service.register_broadcast_callback(broadcast_telemetry)


@app.websocket("/ws/monitoring")
async def websocket_endpoint(websocket: WebSocket):
    """Real-Time Monitoring WebSocket Endpoint."""
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive & receive optional client messages
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)
