import numpy as np
from typing import Dict, Any
from simulator.config import NORMAL_BASELINES, FAULT_SCENARIOS, CORRELATION_MATRIX


class FaultInjector:
    """
    Simulates realistic machine degradation and progressive fault injection
    preserving multi-sensor correlations.
    """

    def __init__(self, scenario: str = "normal", seed: int = None):
        if scenario not in FAULT_SCENARIOS:
            raise ValueError(f"Unknown scenario '{scenario}'. Supported: {list(FAULT_SCENARIOS.keys())}")

        self.scenario = scenario
        self.scenario_config = FAULT_SCENARIOS[scenario]
        self.step_count = 0

        if seed is not None:
            np.random.seed(seed)

        # Precompute correlated random noise transformation matrix using Cholesky decomposition
        self.sensor_keys = ['temperature', 'vibration', 'humidity', 'pressure', 'energy_consumption']
        self.stds = np.array([NORMAL_BASELINES[k]['std'] for k in self.sensor_keys])
        self.means = np.array([NORMAL_BASELINES[k]['mean'] for k in self.sensor_keys])

        cov = np.outer(self.stds, self.stds) * np.array(CORRELATION_MATRIX)
        self.chol = np.linalg.cholesky(cov)

    def generate_step(self, machine_id: str = "M01") -> Dict[str, float]:
        """
        Generate next sensor reading payload for current scenario step.
        """
        self.step_count += 1
        
        # 1. Base correlated gaussian noise vector
        uncorrelated = np.random.normal(0, 1, size=len(self.sensor_keys))
        correlated_noise = self.chol @ uncorrelated

        # 2. Compute progressive drift offsets based on scenario step
        # Degradation starts gently after step 5 and ramps up linearly
        drift_factor = max(0, self.step_count - 5)

        temp_offset = self.scenario_config['temp_drift'] * drift_factor
        vib_offset = self.scenario_config['vib_drift'] * drift_factor
        press_offset = self.scenario_config['press_drift'] * drift_factor
        energy_offset = self.scenario_config['energy_drift'] * drift_factor

        drift_vector = np.array([temp_offset, vib_offset, 0.0, press_offset, energy_offset])

        # 3. Combine baseline + noise + drift
        values = self.means + correlated_noise * 0.3 + drift_vector

        # 4. Clamp within physical sensor bounds
        reading = {}
        for i, k in enumerate(self.sensor_keys):
            min_val = NORMAL_BASELINES[k]['min']
            max_val = NORMAL_BASELINES[k]['max'] + (50.0 if k in ['temperature', 'vibration'] else 0.0)
            val = float(np.clip(values[i], min_val, max_val))
            reading[k] = round(val, 2)

        return reading

    def reset(self):
        """Reset step count to restart simulation scenario."""
        self.step_count = 0
