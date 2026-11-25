import os
import asyncio
import logging
from typing import Dict, Any, Optional

try:
    from supabase import create_client, Client
    _HAS_SUPABASE = True
except ImportError:
    _HAS_SUPABASE = False

logger = logging.getLogger(__name__)

class SupabaseService:
    def __init__(self):
        self.url: str = os.getenv("SUPABASE_URL", "")
        self.key: str = os.getenv("SUPABASE_KEY", "")
        self.client: Optional[Client] = None
        
        if _HAS_SUPABASE and self.url and self.key:
            try:
                self.client = create_client(self.url, self.key)
                logger.info("Supabase client initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
        else:
            logger.warning("Supabase URL or KEY not configured. Cloud logging disabled.")

    async def log_telemetry(self, result: Dict[str, Any]):
        if not self.client:
            return

        sensors = result.get("sensor_readings", {})
        payload = {
            "machine_id": result.get("machine_id"),
            "timestamp": result.get("timestamp"),
            "temperature": sensors.get("temperature", 0.0),
            "vibration": sensors.get("vibration", 0.0),
            "humidity": sensors.get("humidity", 0.0),
            "pressure": sensors.get("pressure", 0.0),
            "energy_consumption": sensors.get("energy_consumption", 0.0),
            "anomaly_score": result.get("anomaly_score", 0.0),
            "is_anomaly": result.get("anomaly", False),
            "predicted_fault": result.get("predicted_fault", "Normal")
        }

        # Run in executor to not block async loop
        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(
                None, 
                lambda: self.client.table("telemetry_readings").insert(payload).execute()
            )
        except Exception as e:
            logger.error(f"Error logging telemetry to Supabase: {e}")

    async def log_alert(self, alert: Dict[str, Any]):
        if not self.client:
            return

        payload = {
            "alert_id": alert.get("id"),
            "machine_id": alert.get("machine_id"),
            "timestamp": alert.get("timestamp"),
            "severity": alert.get("severity"),
            "type": alert.get("type", "Unknown"),
            "message": alert.get("message", ""),
            "recommended_action": alert.get("recommended_action", ""),
            "acknowledged": alert.get("acknowledged", False)
        }

        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(
                None, 
                lambda: self.client.table("alerts").insert(payload).execute()
            )
        except Exception as e:
            logger.error(f"Error logging alert to Supabase: {e}")

    async def acknowledge_alert(self, alert_id: str):
        if not self.client:
            return
            
        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(
                None,
                lambda: self.client.table("alerts").update({"acknowledged": True}).eq("alert_id", alert_id).execute()
            )
        except Exception as e:
            logger.error(f"Error acknowledging alert in Supabase: {e}")

    async def register_operator(self, operator_id: str, access_code: str, name: str) -> Dict[str, Any]:
        if not self.client:
            raise Exception("Supabase is not configured.")
        
        import uuid
        from datetime import datetime
        payload = {
            "id": str(uuid.uuid4()),
            "name": name,
            "operator_id": operator_id,
            "access_code": access_code,
            "created_at": datetime.utcnow().isoformat(),
            "is_verified": True
        }
        
        loop = asyncio.get_event_loop()
        try:
            # Check if operator exists
            existing = await loop.run_in_executor(
                None,
                lambda: self.client.table("operators").select("id").eq("operator_id", operator_id).execute()
            )
            if existing.data:
                raise Exception("Operator ID already registered.")

            res = await loop.run_in_executor(
                None,
                lambda: self.client.table("operators").insert(payload).execute()
            )
            return res.data[0] if res.data else payload
        except Exception as e:
            logger.error(f"Error registering operator: {e}")
            raise e

    async def authenticate_operator(self, operator_id: str, access_code: str) -> Dict[str, Any]:
        if not self.client:
            raise Exception("Supabase is not configured.")
            
        loop = asyncio.get_event_loop()
        try:
            res = await loop.run_in_executor(
                None,
                lambda: self.client.table("operators").select("*").eq("operator_id", operator_id).execute()
            )
            if not res.data:
                raise Exception("Invalid Operator ID or Password.")
            
            operator = res.data[0]
            if operator.get("access_code") != access_code:
                raise Exception("Invalid Operator ID or Password.")
                
            return operator
        except Exception as e:
            logger.error(f"Error authenticating operator: {e}")
            raise e

supabase_service = SupabaseService()
