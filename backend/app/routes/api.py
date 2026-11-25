from fastapi import APIRouter, HTTPException, Path
from typing import Dict, Any, List, Optional

from backend.app.schemas import (
    HealthCheckResponse,
    SimulatorStartRequest,
    SimulatorStatusResponse
)
from backend.app.state import system_state
from backend.app.services.simulator_service import simulator_service
from backend.app.websocket.monitoring import ws_manager

router = APIRouter()


@router.get("/health", response_model=HealthCheckResponse)
async def get_health():
    """Health check endpoint returning backend status."""
    return {"status": "ok", "service": "iot-anomaly-backend"}


@router.get("/api/machines", response_model=List[Dict[str, Any]])
async def get_all_machines():
    """Return latest condition state for all tracked machines."""
    return system_state.get_machines()


@router.get("/api/machines/{machine_id}", response_model=Dict[str, Any])
async def get_machine(machine_id: str = Path(..., description="Machine Identifier")):
    """Return current state for a specific machine."""
    machine = system_state.get_machine(machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail=f"Machine '{machine_id}' not found.")
    return machine


@router.get("/api/machines/{machine_id}/history", response_model=List[Dict[str, Any]])
async def get_machine_history(machine_id: str = Path(..., description="Machine Identifier")):
    """Return recent bounded reading history for a specific machine."""
    return system_state.get_machine_history(machine_id)


@router.get("/api/alerts", response_model=List[Dict[str, Any]])
async def get_alerts():
    """Return all generated alerts."""
    return system_state.get_alerts()


@router.post("/api/alerts/{alert_id}/acknowledge", response_model=Dict[str, Any])
async def acknowledge_alert(alert_id: str = Path(..., description="Alert ID")):
    """Acknowledge an alert by ID."""
    success = system_state.acknowledge_alert(alert_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Alert '{alert_id}' not found.")
    return {"status": "ok", "message": f"Alert '{alert_id}' acknowledged.", "alert_id": alert_id}


@router.post("/api/simulator/start", response_model=SimulatorStatusResponse)
async def start_simulator(req: Optional[SimulatorStartRequest] = None):
    """Start virtual IoT stream simulation."""
    if req is None:
        req = SimulatorStartRequest()
    simulator_service.start(
        scenario=req.scenario,
        machine_id=req.machine_id,
        steps=req.steps,
        interval=req.interval
    )
    return simulator_service.get_status()


@router.post("/api/simulator/stop", response_model=SimulatorStatusResponse)
async def stop_simulator():
    """Stop virtual IoT stream simulation."""
    simulator_service.stop()
    return simulator_service.get_status()


@router.get("/api/simulator/status", response_model=SimulatorStatusResponse)
async def get_simulator_status():
    """Return current virtual IoT stream simulator status."""
    return simulator_service.get_status()


@router.post("/api/telemetry", response_model=Dict[str, Any])
async def ingest_telemetry(payload: Dict[str, Any]):
    """Direct HTTP REST endpoint to ingest a single telemetry reading payload."""
    result, alert = system_state.process_telemetry(payload)
    await ws_manager.broadcast(result, alert)
    return result


@router.get("/api/alerts/email-settings", response_model=Dict[str, Any])
async def get_email_settings():
    """Return active alert email configuration."""
    from backend.app.services.email_service import email_service
    return email_service.get_config()


@router.post("/api/alerts/email-settings", response_model=Dict[str, Any])
async def update_email_settings(payload: Dict[str, Any]):
    """Update active alert email recipient."""
    from backend.app.services.email_service import email_service
    recipient = payload.get("recipient_email", "")
    if recipient:
        email_service.update_recipient(recipient)
    return {"status": "ok", "config": email_service.get_config()}


@router.post("/api/alerts/test-email", response_model=Dict[str, Any])
async def send_test_alert_email():
    """Manually dispatch a sample test email alert."""
    from backend.app.services.email_service import email_service
    test_alert = {
        "id": "TEST-DISPATCH",
        "machine_id": "M01",
        "severity": "CRITICAL",
        "type": "Overheating (Test Dispatch)",
        "timestamp": "Now",
        "message": "Manual test alert triggered by system operator.",
        "reasons": ["Test email notification verification from InduGuard UI."],
        "recommended_action": "Verify email receipt in operator inbox."
    }
    email_service.dispatch_alert_email(test_alert)
    return {"status": "ok", "message": f"Test email dispatched to {email_service.recipient_email}"}

@router.post("/api/auth/register", response_model=Dict[str, Any])
async def register_operator(payload: dict):
    """Register a new operator."""
    from backend.app.schemas import RegisterRequest
    try:
        req = RegisterRequest(**payload)
        from backend.app.services.supabase_service import supabase_service
        operator = await supabase_service.register_operator(
            operator_id=req.username,
            access_code=req.password,
            name=req.name
        )
        return {"status": "ok", "operator": {"id": operator.get("id"), "name": operator.get("name"), "operator_id": operator.get("operator_id")}}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/api/auth/login", response_model=Dict[str, Any])
async def login_operator(payload: dict):
    """Authenticate an operator."""
    from backend.app.schemas import LoginRequest
    try:
        req = LoginRequest(**payload)
        from backend.app.services.supabase_service import supabase_service
        operator = await supabase_service.authenticate_operator(
            operator_id=req.username,
            access_code=req.password
        )
        return {"status": "ok", "operator": {"id": operator.get("id"), "name": operator.get("name"), "operator_id": operator.get("operator_id")}}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

