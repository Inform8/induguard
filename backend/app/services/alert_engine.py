import uuid
import time
from typing import Dict, Any, List, Optional
from backend.app.services.email_service import email_service


class AlertEngine:
    """
    Industrial Alert Engine with Rate Limiting & Cooldown.
    Evaluates ConditionAnalyzer output, enforces a 60-second cooldown per machine
    to prevent notification spam, and manages alert lifecycle and acknowledgement.
    """

    def __init__(self, cooldown_seconds: float = 60.0):
        self._alerts: List[Dict[str, Any]] = []
        self.cooldown_seconds = cooldown_seconds
        # Track last active state per machine: {machine_id: {"severity": str, "fault": str, "alert_id": str, "time": float}}
        self._active_machine_faults: Dict[str, Dict[str, Any]] = {}

    def process_condition_result(self, condition_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Evaluate condition result and generate an alert if necessary.
        Applies strict 60-second cooldown rate-limiting per machine.
        """
        if condition_result.get("error", False):
            return None

        status = condition_result.get("status", "NORMAL")
        machine_id = condition_result.get("machine_id", "UNKNOWN")
        fault_type = condition_result.get("predicted_fault", "Normal")
        timestamp = condition_result.get("timestamp", "")
        reasons = condition_result.get("reasons", [])
        action = condition_result.get("recommended_action", "")
        now = time.time()

        # If machine is NORMAL, return None (preserve cooldown memory to avoid oscillation spam)
        if status == "NORMAL":
            return None

        # Check existing active fault state & cooldown for rate-limiting
        last_active = self._active_machine_faults.get(machine_id, None)

        if last_active:
            last_sev = last_active["severity"]
            last_fault = last_active["fault"]
            last_time = last_active.get("time", 0.0)
            elapsed = now - last_time

            # Rate limit: Suppress if generated within cooldown period (60s), UNLESS escalating to CRITICAL
            if elapsed < self.cooldown_seconds and not (status == "CRITICAL" and last_sev == "WARNING"):
                return None

            if status == "CRITICAL" and last_sev == "WARNING":
                msg = f"Escalated CRITICAL condition ({fault_type}) on machine {machine_id}."
            else:
                msg = f"{status} condition ({fault_type}) detected on machine {machine_id}."
        else:
            msg = f"{status} condition ({fault_type}) detected on machine {machine_id}."

        alert_id = f"ALT-{str(uuid.uuid4())[:8].upper()}"

        alert_object = {
            "id": alert_id,
            "timestamp": timestamp,
            "machine_id": machine_id,
            "severity": status,
            "type": fault_type,
            "message": msg,
            "reasons": reasons,
            "recommended_action": action,
            "acknowledged": False,
            "sensor_readings": condition_result.get("sensor_readings", {})
        }

        self._alerts.append(alert_object)
        self._active_machine_faults[machine_id] = {
            "severity": status,
            "fault": fault_type,
            "alert_id": alert_id,
            "time": now
        }

        # Dispatch automated email notification in background thread
        email_service.dispatch_alert_email(alert_object)

        return alert_object

    def get_all_alerts(self) -> List[Dict[str, Any]]:
        """Return all historical alerts."""
        return list(reversed(self._alerts))

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Mark alert as acknowledged without removing it from history."""
        for alert in self._alerts:
            if alert["id"] == alert_id:
                alert["acknowledged"] = True
                return True
        return False
