# Project Scope & Capabilities Specification

## Executive Summary
This document specifies the technical boundary and functional capabilities of the **IoT-Based Industrial Anomaly Detection System** based on empirical verification of `smart_manufacturing_data.csv`.

---

## 1. Supported Capabilities

### Sensor Parameter Monitoring
The system monitors 5 continuous physical telemetry channels across 50 industrial machines:
- **Thermal Monitoring**: Bearings & machine casing temperature (°C)
- **Vibration Telemetry**: Mechanical vibration frequency/amplitude
- **Environmental Humidity**: Ambient relative humidity percentage (%)
- **Pneumatic / Hydraulic Pressure**: Operational fluid line pressure (bar)
- **Power Draw / Energy Consumption**: Electrical power consumption (kW)

### ML Anomaly Detection
- Unsupervised detection of anomalous machine operating states based strictly on sensor deviations.
- Binary anomaly score and anomaly probability estimation without relying on target labels.

### Fault & Condition Identification
The dataset supports multi-class fault classification and condition interpretation for 4 specific industrial fault modes:
1. **Overheating**: Elevated temperature trends accompanied by energy draw shifts.
2. **Vibration Issue**: Mechanical resonance, bearing wear, or imbalance causing high vibration.
3. **Pressure Drop**: Hydraulic/pneumatic pressure collapse or fluid leaks.
4. **Electrical Fault**: Anomalous power draw spikes or irregular energy consumption.

### Realistic IoT Simulator
- Progressive degradation and fault injection for all 4 supported failure scenarios plus normal machine operation.

---

## 2. Explicitly Unsupported Capabilities

To maintain technical integrity during demonstration, the following features are explicitly **NOT supported** by the current dataset and must NOT be claimed:

1. **Gas Sensor Leakage Detection**: No chemical, methane, or gas sensor features exist in `smart_manufacturing_data.csv`. If gas leak detection is requested in future phases, a separate gas telemetry dataset or simulated gas sensor module would be required.
2. **Acoustic Emission Analysis**: No audio/ultrasonic sensor streams exist.
3. **Computer Vision Inspection**: No optical, thermal camera, or surface defect image data is included.
4. **Automated Physical Actuation**: The system generates operator alerts and recommendations but does not directly send SCADA control signals to halt machines physically.

---

## 3. Data Flow Architecture (Phases 1 - 5)

```
[smart_manufacturing_data.csv]
          │
          ▼
[src/data/preprocessing.py] ─── (Chronological Train/Val/Test Split + Feature Scaling)
          │
          ├──────────────────────────────┐
          ▼                              ▼
[src/models/anomaly_detector.py] [src/models/fault_classifier.py]
 (Isolation Forest / Unsupervised) (Supervised Multi-class Fault Model)
          │                              │
          └──────────────┬───────────────┘
                         ▼
        [src/analysis/condition_analyzer.py]
      (Rules + ML -> Severity, Reasons, Action)
                         │
                         ▼
          [simulator/sensor_simulator.py]
    (Realistic IoT Telemetry & Fault Injection Stream)
```
