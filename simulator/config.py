"""
IoT Sensor Simulator Configuration.
Defines normal baseline distributions, multi-sensor covariance matrix,
and scenario-specific fault degradation patterns derived from smart_manufacturing_data.csv.
"""

# Baseline Normal Operating Parameters
NORMAL_BASELINES = {
    'temperature': {'mean': 75.02, 'std': 4.5, 'min': 50.0, 'max': 85.0},
    'vibration': {'mean': 50.01, 'std': 8.0, 'min': 20.0, 'max': 65.0},
    'humidity': {'mean': 55.00, 'std': 7.0, 'min': 30.0, 'max': 80.0},
    'pressure': {'mean': 3.00, 'std': 0.4, 'min': 1.8, 'max': 4.5},
    'energy_consumption': {'mean': 2.75, 'std': 0.5, 'min': 1.0, 'max': 4.0}
}

# Multi-Sensor Correlation Matrix (T, V, H, P, E)
CORRELATION_MATRIX = [
    [1.00,  0.25, -0.01, -0.02,  0.30],  # Temperature
    [0.25,  1.00, -0.01,  0.01,  0.20],  # Vibration
    [-0.01, -0.01, 1.00,  0.00, -0.01],  # Humidity
    [-0.02,  0.01, 0.00,  1.00, -0.05],  # Pressure
    [0.30,  0.20, -0.01, -0.05,  1.00]   # Energy Consumption
]

# Supported Scenario Failure Profiles
FAULT_SCENARIOS = {
    'normal': {
        'description': 'Normal continuous operational state',
        'temp_drift': 0.0,
        'vib_drift': 0.0,
        'press_drift': 0.0,
        'energy_drift': 0.0
    },
    'overheating': {
        'description': 'Gradual thermal runaway leading to overheating',
        'temp_drift': 1.5,     # °C per step
        'vib_drift': 0.4,
        'press_drift': 0.0,
        'energy_drift': 0.08
    },
    'vibration_fault': {
        'description': 'Mechanical imbalance / bearing wear causing high vibration',
        'temp_drift': 0.3,
        'vib_drift': 2.0,      # vibration amplitude per step
        'press_drift': 0.0,
        'energy_drift': 0.05
    },
    'pressure_drop': {
        'description': 'Hydraulic / pneumatic fluid pressure drop fault',
        'temp_drift': 0.1,
        'vib_drift': 0.2,
        'press_drift': -0.15,  # bar drop per step
        'energy_drift': -0.04
    },
    'electrical_fault': {
        'description': 'Unstable electrical power supply and high energy draw',
        'temp_drift': 0.4,
        'vib_drift': 0.3,
        'press_drift': 0.0,
        'energy_drift': 0.12   # kW increase per step
    }
}
