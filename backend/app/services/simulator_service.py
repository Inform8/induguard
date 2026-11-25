import asyncio
from typing import Optional, Callable, Awaitable, Any

from simulator.sensor_simulator import SensorSimulator

# Import backend components for processing
from backend.app.state import system_state


class SimulatorService:
    """
    Asynchronous background service managing the virtual IoT sensor simulator.
    Provides start/stop controls and status queries.
    Integrates generated telemetry with the real-time inference pipeline.
    """

    def __init__(self):
        self._task: Optional[asyncio.Task] = None
        self._simulator: Optional[SensorSimulator] = None
        self._generated: int = 0
        self._is_running: bool = False
        self._broadcast_callback: Optional[Callable[[dict, dict | None], Awaitable[None]]] = None

    def register_broadcast_callback(self, callback: Callable[[dict, dict | None], Awaitable[None]]):
        """Register a coroutine that will be called with (result, alert) after each reading.
        The FastAPI main module registers the WebSocket broadcast function here.
        """
        self._broadcast_callback = callback

    async def _run_simulation(self, scenario: str, machine_id: str, steps: int, interval: float):
        """Generate telemetry and push each reading through the inference pipeline.

        Parameters
        ----------
        scenario: str
            The failure scenario to simulate (e.g., "normal", "overheating").
        machine_id: str
            Identifier for the simulated machine.
        steps: int
            Number of readings to produce; 0 means run indefinitely.
        interval: float
            Seconds to wait between readings.
        """
        self._is_running = True
        self._simulator = SensorSimulator(scenario=scenario, machine_id=machine_id)
        count = 0
        while steps == 0 or count < steps:
            reading = self._simulator.generate_reading()
            # Process the reading through the shared inference pipeline / state manager
            result, alert = system_state.process_telemetry(reading)
            # If a broadcast callback has been registered, call it
            if self._broadcast_callback is not None:
                await self._broadcast_callback(result, alert)
            self._generated += 1
            count += 1
            await asyncio.sleep(interval)
        # Simulation completed
        self._is_running = False
        self._simulator = None

    def start(self, scenario: str = "normal", machine_id: str = "M01", steps: int = 0, interval: float = 1.0):
        """Start the simulator in background. Steps=0 for infinite stream."""
        if self._task and not self._task.done():
            return
        self._is_running = True
        loop = asyncio.get_event_loop()
        self._task = loop.create_task(self._run_simulation(scenario, machine_id, steps, interval))

    def stop(self):
        """Stop the simulator if running."""
        if self._task and not self._task.done():
            self._task.cancel()
            self._is_running = False
        self._task = None
        self._simulator = None

    def get_status(self):
        """Return status dict for API response."""
        return {
            "is_running": self._is_running,
            "scenario": getattr(self._simulator, "scenario", "normal") if self._simulator else "normal",
            "machine_id": getattr(self._simulator, "machine_id", "M01") if self._simulator else "M01",
            "interval": getattr(self._simulator, "interval", 1.0) if self._simulator else 1.0,
            "total_generated": self._generated,
        }

# Export a singleton instance for importers
simulator_service = SimulatorService()
