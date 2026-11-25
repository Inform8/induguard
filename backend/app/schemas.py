from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class HealthCheckResponse(BaseModel):
    status: str = "ok"
    service: str = "iot-anomaly-backend"


class SimulatorStartRequest(BaseModel):
    scenario: str = Field(default="normal", description="Failure scenario (normal, overheating, vibration_fault, pressure_drop, electrical_fault)")
    machine_id: str = Field(default="M01", description="Machine identifier")
    steps: int = Field(default=0, description="Number of readings (0 for continuous stream)")
    interval: float = Field(default=1.0, description="Sampling interval in seconds")


class SimulatorStatusResponse(BaseModel):
    is_running: bool
    scenario: str
    machine_id: str
    interval: float
    total_generated: int


class AlertSchema(BaseModel):
    id: str
    timestamp: str
    machine_id: str
    severity: str
    type: str
    message: str
    reasons: List[str]
    recommended_action: str
    acknowledged: bool = False


class RegisterRequest(BaseModel):
    username: str = Field(..., description="Email/Operator ID")
    password: str = Field(..., description="Access code")
    name: str = Field(..., description="Display name")


class LoginRequest(BaseModel):
    username: str = Field(..., description="Email/Operator ID")
    password: str = Field(..., description="Access code")
