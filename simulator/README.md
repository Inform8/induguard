# Virtual IoT Machine Telemetry Simulator

## Overview
The Virtual IoT Sensor Simulator generates realistic, correlated time-series machine sensor telemetry streams (`temperature`, `vibration`, `humidity`, `pressure`, `energy_consumption`).

It models both standard nominal machine operation and controlled progressive fault injection scenarios based on the feature distributions of `smart_manufacturing_data.csv`.

---

## Supported Failure Scenarios

| Scenario Flag | Description | Failure Behavior |
| :--- | :--- | :--- |
| `normal` | Standard operational telemetry | Stable baseline values with realistic sensor noise |
| `overheating` | Thermal runaway fault | Thermal elevation leading to overheating & power draw rise |
| `vibration_fault` | Mechanical bearing / rotor fault | Progressive vibration amplitude increase |
| `pressure_drop` | Hydraulic / pneumatic leak | Line pressure decay and pressure drop fault |
| `electrical_fault` | Power supply instability | Spike in energy draw and current imbalance |

---

## CLI Usage Instructions

### Basic Telemetry Stream (Normal Machine Operation)
```bash
python simulator/sensor_simulator.py --scenario normal --steps 10 --interval 1.0
```

### Overheating Fault Simulation with Real-Time Condition Analysis
```bash
python simulator/sensor_simulator.py --scenario overheating --steps 15 --interval 0.5 --evaluate
```

### Vibration Fault Simulation
```bash
python simulator/sensor_simulator.py --scenario vibration_fault --steps 20 --evaluate
```

### Continuous Stream (Indefinite Monitoring)
```bash
python simulator/sensor_simulator.py --scenario pressure_drop --steps 0 --interval 2.0 --evaluate
```

---

## Output Data Format

The simulator emits clean, structured JSON stream events suitable for real-time inference integration:

```json
{
  "timestamp": "2026-08-09 15:49:11",
  "machine_id": "M01",
  "scenario": "overheating",
  "step": 12,
  "temperature": 104.2,
  "vibration": 72.1,
  "humidity": 55.0,
  "pressure": 3.01,
  "energy_consumption": 4.82,
  "condition_analysis": {
    "status": "CRITICAL",
    "anomaly": true,
    "anomaly_score": 0.924,
    "predicted_fault": "Overheating",
    "fault_confidence": 0.961,
    "condition": "CRITICAL: Overheating detected with severe sensor deviation.",
    "reasons": [
      "Critical temperature spike detected (104.2°C > 100.0°C)",
      "Excessive electrical power draw (4.82 kW)"
    ],
    "recommended_action": "Inspect cooling systems, lubrication levels, and thermal bearings immediately."
  }
}
```
