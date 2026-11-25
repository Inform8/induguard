import collections
from typing import Dict, Any, List, Optional
from src.realtime.inference_pipeline import RealtimeInferencePipeline
from backend.app.services.alert_engine import AlertEngine


class SystemStateStore:
    """
    In-Memory State Store for FastAPI Backend.
    Tracks live machine status, bounded reading history, alerts, and inference pipeline.
    """

    def __init__(self, history_limit_per_machine: int = 50):
        self.history_limit = history_limit_per_machine
        self.pipeline = RealtimeInferencePipeline(history_limit_per_machine=history_limit_per_machine)
        self.alert_engine = AlertEngine()

        # Latest condition report per machine_id
        self._machines: Dict[str, Dict[str, Any]] = {}
        # Bounded history per machine_id
        self._history: Dict[str, collections.deque] = {}

    def process_telemetry(self, telemetry_reading: Dict[str, Any]) -> tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
        """
        Process single telemetry reading:
        1. Run RealtimeInferencePipeline (ConditionAnalyzer + ML + Rules)
        2. Update machine latest state & bounded history
        3. Evaluate AlertEngine for deduplicated alert generation
        Returns: (condition_result, alert_or_none)
        """
        result = self.pipeline.process_reading(telemetry_reading)

        if not result.get("error", False):
            machine_id = result["machine_id"]
            self._machines[machine_id] = result

            if machine_id not in self._history:
                self._history[machine_id] = collections.deque(maxlen=self.history_limit)
            self._history[machine_id].append(result)

            # Evaluate alert generation
            alert = self.alert_engine.process_condition_result(result)
            
            # Fire and forget cloud logging
            import asyncio
            from backend.app.services.supabase_service import supabase_service
            asyncio.create_task(supabase_service.log_telemetry(result))
            if alert:
                asyncio.create_task(supabase_service.log_alert(alert))
                
            return result, alert

        return result, None

    def get_machines(self) -> List[Dict[str, Any]]:
        """Return array of latest states for all tracked machines."""
        return list(self._machines.values())

    def get_machine(self, machine_id: str) -> Optional[Dict[str, Any]]:
        """Return latest state for a specific machine."""
        return self._machines.get(machine_id, None)

    def get_machine_history(self, machine_id: str) -> List[Dict[str, Any]]:
        """Return recent bounded reading history for a specific machine."""
        if machine_id in self._history:
            return list(self._history[machine_id])
        return []

    def get_alerts(self) -> List[Dict[str, Any]]:
        """Return all historical alerts."""
        return self.alert_engine.get_all_alerts()

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge alert by ID and update database."""
        success = self.alert_engine.acknowledge_alert(alert_id)
        if success:
            import asyncio
            from backend.app.services.supabase_service import supabase_service
            asyncio.create_task(supabase_service.acknowledge_alert(alert_id))
        return success


# Global singleton instance for app state
system_state = SystemStateStore()
