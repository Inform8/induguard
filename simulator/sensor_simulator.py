import argparse
import datetime
import json
import os
import sys
import time
from typing import Dict, Any

# Ensure project root is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulator.fault_injector import FaultInjector
from simulator.config import FAULT_SCENARIOS
from src.analysis.condition_analyzer import ConditionAnalyzer


class SensorSimulator:
    """
    Virtual IoT Sensor Telemetry Simulator.
    Generates realistic, correlated time-series machine telemetry streams
    with optional fault injection and real-time condition evaluation.
    """

    def __init__(self, scenario: str = "normal", machine_id: str = "M01", evaluate: bool = False):
        self.scenario = scenario
        self.machine_id = machine_id
        self.evaluate = evaluate
        self.injector = FaultInjector(scenario=scenario)
        
        self.analyzer = None
        if evaluate:
            self.analyzer = ConditionAnalyzer()

    def generate_reading(self) -> Dict[str, Any]:
        """Generate single timestamped sensor reading payload."""
        timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sensor_values = self.injector.generate_step(machine_id=self.machine_id)

        payload = {
            "timestamp": timestamp_str,
            "machine_id": self.machine_id,
            "scenario": self.scenario,
            "step": self.injector.step_count,
            **sensor_values
        }

        if self.analyzer:
            analysis = self.analyzer.analyze_reading(payload)
            payload["condition_analysis"] = analysis

        return payload

    def run_stream(self, steps: int = 10, interval: float = 1.0):
        """
        Run continuous telemetry stream for specified steps and sampling interval.
        """
        print(f"==================================================")
        print(f" Starting Virtual IoT Sensor Simulator Stream")
        print(f" Machine ID : {self.machine_id}")
        print(f" Scenario   : {self.scenario} ({FAULT_SCENARIOS[self.scenario]['description']})")
        print(f" Steps      : {steps if steps > 0 else 'Continuous'}")
        print(f" Interval   : {interval}s")
        print(f"==================================================\n")

        count = 0
        try:
            while steps <= 0 or count < steps:
                count += 1
                reading = self.generate_reading()
                print(json.dumps(reading, indent=2))
                sys.stdout.flush()

                if steps <= 0 or count < steps:
                    time.sleep(interval)

        except KeyboardInterrupt:
            print("\nSimulation stream stopped by user.")


def main():
    parser = argparse.ArgumentParser(description="Virtual IoT Sensor Telemetry Simulator")
    parser.add_argument("--scenario", type=str, default="normal",
                        choices=list(FAULT_SCENARIOS.keys()),
                        help="Failure scenario to simulate (default: normal)")
    parser.add_argument("--machine_id", type=str, default="M01",
                        help="Machine Identifier string (default: M01)")
    parser.add_argument("--steps", type=int, default=5,
                        help="Number of telemetry readings to output (0 for continuous, default: 5)")
    parser.add_argument("--interval", type=float, default=1.0,
                        help="Sampling interval in seconds (default: 1.0)")
    parser.add_argument("--evaluate", action="store_true",
                        help="Enable real-time ConditionAnalyzer evaluation in output")

    args = parser.parse_args()

    simulator = SensorSimulator(
        scenario=args.scenario,
        machine_id=args.machine_id,
        evaluate=args.evaluate
    )
    simulator.run_stream(steps=args.steps, interval=args.interval)


if __name__ == "__main__":
    main()
