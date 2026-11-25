import collections
from typing import Dict, Any, List, Generator

from src.analysis.condition_analyzer import ConditionAnalyzer


class RealtimeInferencePipeline:
    """
    Real-Time Inference Pipeline Orchestration Layer.
    Loads ML models ONCE at startup, validates incoming telemetry,
    maintains bounded machine history state, and runs hybrid condition analysis.
    """

    def __init__(self, history_limit_per_machine: int = 50,
                 anomaly_detector_path: str = "models/anomaly_detector.joblib",
                 fault_classifier_path: str = "models/fault_classifier.joblib"):
        
        self.history_limit = history_limit_per_machine
        # Load ML models ONCE at pipeline initialization
        self.analyzer = ConditionAnalyzer(
            anomaly_detector_path=anomaly_detector_path,
            fault_classifier_path=fault_classifier_path
        )
        # Bounded sliding window history storage per machine_id
        self._machine_history: Dict[str, collections.deque] = {}

    def process_reading(self, reading: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single IoT telemetry reading payload through validation,
        ML inference, condition analysis, and history tracking.
        """
        # Run ConditionAnalyzer (which performs strict validation & ML inference)
        result = self.analyzer.analyze_reading(reading)

        # Store in per-machine history if reading is valid
        if not result.get("error", False):
            machine_id = result["machine_id"]
            if machine_id not in self._machine_history:
                self._machine_history[machine_id] = collections.deque(maxlen=self.history_limit)

            self._machine_history[machine_id].append(result)

        return result

    def get_machine_history(self, machine_id: str) -> List[Dict[str, Any]]:
        """Retrieve recent bounded reading history for a given machine."""
        if machine_id in self._machine_history:
            return list(self._machine_history[machine_id])
        return []

    def get_all_machine_states(self) -> Dict[str, Dict[str, Any]]:
        """Retrieve the latest condition status for all active machines."""
        latest_states = {}
        for m_id, history in self._machine_history.items():
            if history:
                latest_states[m_id] = history[-1]
        return latest_states

    def process_stream(self, stream_generator: Generator[Dict[str, Any], None, None]):
        """
        Consume a continuous telemetry stream generator yielding processed results.
        """
        for item in stream_generator:
            yield self.process_reading(item)


if __name__ == "__main__":
    print("Testing RealtimeInferencePipeline...")
    pipeline = RealtimeInferencePipeline()

    sample_valid = {
        "timestamp": "2026-08-09 16:00:00",
        "machine_id": "M01",
        "temperature": 105.4,
        "vibration": 88.2,
        "humidity": 55.0,
        "pressure": 3.0,
        "energy_consumption": 4.85
    }

    res = pipeline.process_reading(sample_valid)
    print("Processed Result Status:", res["status"])
    print("History Count M01:", len(pipeline.get_machine_history("M01")))
