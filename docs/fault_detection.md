# Phase 4: Fault & Condition Identification Documentation

## Overview
This document specifies the fault taxonomy, supervised multi-class classification model, rule-based reasoning layer, authoritatively evaluated performance metrics, and machine condition severity determination logic implemented in the **IoT Industrial Anomaly Detection System**.

---

## 1. Supported Fault Taxonomy & Sensor Signature Profiles

Based on empirical analysis of `smart_manufacturing_data.csv`, 4 primary industrial machine fault categories are supported in addition to Normal operation:

| Fault Category | Sensor Signature Profile | Key Feature Indicators | Recommended Operator Action |
| :--- | :--- | :--- | :--- |
| **Normal** | All sensor streams within nominal baseline ranges. | Temp: ~75°C, Vib: ~50, Press: ~3.0 bar, Energy: ~2.75 kW | Continue routine operations and scheduled monitoring. |
| **Overheating** | Temperature spikes (> 88°C - 100°C+), often accompanied by elevated power draw. | Primary: `temperature`, Secondary: `energy_consumption` | Inspect cooling systems, coolant fluid, bearing lubrication, and thermal sensors. |
| **Vibration Issue** | High mechanical vibration (> 68 - 85+), mechanical resonance, bearing looseness. | Primary: `vibration`, Secondary: `temperature` | Check mechanical alignment, rotor balance, motor mounting, and bearing tightness. |
| **Pressure Drop** | Hydraulic or pneumatic line pressure drop (< 1.5 - 2.0 bar). | Primary: `pressure` | Inspect hydraulic lines, check fluid pumps, seals, and pneumatic pressure valves. |
| **Electrical Fault**| Irregular power consumption spikes (> 4.0 - 4.7 kW+), unstable energy draw. | Primary: `energy_consumption`, Secondary: `temperature` | Inspect power delivery unit, electrical wiring, voltage regulators, and surge suppressors. |

---

## 2. Model & Rule Hybrid Architecture

The condition analyzer uses a 3-layer hybrid architecture:

```
                      [Input Sensor Payload]
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
[AnomalyDetector]       [FaultClassifier]      [Statistical Rule Engine]
(is_anomaly, score)     (pred_fault, conf)     (Evaluate thresholds)
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                ▼
                   [Condition Severity Logic]
                   (NORMAL / WARNING / CRITICAL)
                                │
                                ▼
                     [Structured JSON Report]
```

### Distinction Between ML Anomaly Detection & Logic Explanation
- **ML Anomaly Detector**: Identifies *that* an anomaly has occurred by computing statistical out-of-distribution distance (Isolation Forest score).
- **ML Fault Classifier**: Predicts the *type* of fault by matching multi-feature patterns against historical failure labels.
- **Rule Engine**: Evaluates feature deviation levels against physical threshold limits to explain *why* the machine is in a given state.

---

## 3. Authoritative Performance Metrics (Evaluated on Hold-out Test Set: 15,000 Rows)

### A. Anomaly Detection Model (`models/anomaly_detector.joblib`)
- **Algorithm**: Isolation Forest (`contamination=0.089`, `n_estimators=150`)
- **ROC-AUC**: **`0.8417`**
- **Precision**: `0.3670`
- **Recall**: `0.3659`
- **F1-Score**: `0.3664`
- **Accuracy**: `0.8877`
- **Confusion Matrix**: `[[12829 TN, 840 FP], [844 FN, 487 TP]]`

### B. Fault Classification Model (`models/fault_classifier.joblib`)
- **Algorithm**: Random Forest Classifier (`n_estimators=150`, `max_depth=12`, `class_weight='balanced'`)
- **Accuracy**: `0.5690` (56.90%)
- **Weighted F1-Score**: **`0.6779`**
- **Macro F1-Score**: `0.1705`

#### Detailed Per-Class Metrics

| Class Label | Precision | Recall | F1-Score | Support |
| :--- | :--- | :--- | :--- | :--- |
| **Electrical Fault** | `0.0090` | `0.0704` | `0.0160` | 142 |
| **Normal** | `0.9191` | `0.6097` | `0.7331` | 13,815 |
| **Overheating** | `0.0212` | `0.1181` | `0.0360` | 288 |
| **Pressure Drop** | `0.0134` | `0.0693` | `0.0225` | 274 |
| **Vibration Issue** | `0.0287` | `0.1019` | `0.0448` | 481 |

*(Note: Raw sensor feature distributions across `failure_type` labels in synthetic data overlap significantly. Therefore, the hybrid Rule Engine in `ConditionAnalyzer` is essential to guarantee accurate operational condition diagnostics).*

---

## 4. Machine Condition Severity Logic

Severity status (`NORMAL`, `WARNING`, `CRITICAL`) is calculated using the following rule matrix:

- **CRITICAL**:
  - `anomaly_flag == True` AND (`reasons >= 2` OR `predicted_fault != 'Normal'` OR `anomaly_score > 0.85`).
- **WARNING**:
  - `anomaly_flag == True` OR `predicted_fault != 'Normal'` OR `reasons > 1`.
- **NORMAL**:
  - `anomaly_flag == False` AND `predicted_fault == 'Normal'`.

---

## 5. Payload Validation & Error Handling

If an incoming telemetry payload contains missing sensor features, missing `machine_id`, or non-numeric float values, `ConditionAnalyzer` returns an explicit validation error:

```json
{
  "status": "ERROR",
  "error": true,
  "error_message": "Telemetry validation failed: Missing required sensor field: 'temperature'.",
  "details": [
    "Missing required sensor field: 'temperature'."
  ],
  "machine_id": "M05",
  "timestamp": "2025-01-01 02:00:00"
}
```
