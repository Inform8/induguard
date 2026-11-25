# Phase 1: Dataset Profile & Analysis Report

## Overview & Metadata
- **Dataset Filename**: `smart_manufacturing_data.csv`
- **File Format**: Comma-Separated Values (CSV)
- **Total Rows**: 100,000 observations (plus 1 header row)
- **Total Columns**: 13 features
- **Missing Values**: 0 nulls across all columns
- **Duplicate Rows**: 0 duplicates
- **Time Range**: `2025-01-01 00:00:00` to `2025-03-11 10:39:00` (Minute-level timestamps)

---

## Detailed Schema Profile

| Column Name | Data Type | Role / Category | Description & Range | Missing Count |
| :--- | :--- | :--- | :--- | :--- |
| `timestamp` | Datetime (string) | Time Index | Chronological observation timestamp (`2025-01-01` to `2025-03-11`) | 0 |
| `machine_id` | Integer | Entity Identifier | Unique machine index ranging from `1` to `50` (50 industrial assets) | 0 |
| `temperature` | Continuous Float | Sensor Reading | Operating temperature in °C (Min: 35.55, Mean: 75.02, Max: 121.94) | 0 |
| `vibration` | Continuous Float | Sensor Reading | Vibration frequency/amplitude (Min: -17.09, Mean: 50.01, Max: 113.80) | 0 |
| `humidity` | Continuous Float | Sensor Reading | Relative humidity % (Min: 30.00, Mean: 55.00, Max: 80.00) | 0 |
| `pressure` | Continuous Float | Sensor Reading | Fluid/Pneumatic pressure in bar (Min: 1.00, Mean: 3.00, Max: 5.00) | 0 |
| `energy_consumption` | Continuous Float | Sensor Reading | Power draw in kW/kWh (Min: 0.50, Mean: 2.75, Max: 5.00) | 0 |
| `machine_status` | Discrete Integer | Operational Status | Operating state: `0` (Idle/Stopped: 9,852), `1` (Normal: 80,091), `2` (Fault/Warning: 10,057) | 0 |
| `anomaly_flag` | Binary Integer | Ground-Truth Anomaly Label | `0` (Normal: 91,084 / 91.08%), `1` (Anomaly: 8,916 / 8.92%) | 0 |
| `predicted_remaining_life`| Continuous Integer | Asset Lifetime Metric | Remaining Useful Life (RUL) in hours (Min: 0, Max: 500) | 0 |
| `failure_type` | Categorical String | Fault Classification Target | `Normal` (91,899), `Vibration Issue` (3,129), `Overheating` (1,989), `Pressure Drop` (1,969), `Electrical Fault` (1,014) | 0 |
| `downtime_risk` | Continuous Float | Risk Score | Machine failure risk probability index (`0.0` or `1.0`) | 0 |
| `maintenance_required` | Binary Integer | Maintenance Target | `0` (No Maintenance: 80,303), `1` (Maintenance Required: 19,697) | 0 |

---

## 10 Core Analytical Questions

### 1. What is this dataset?
It is a synthetic, high-frequency IoT industrial machine telemetry dataset containing 100,000 observations of machine operational states, physical sensor parameters, and annotated fault labels for smart manufacturing equipment.

### 2. How many machines are represented?
Exactly **50 unique industrial machines** (`machine_id` values 1 through 50). Each machine contributes ~2,000 observations across time.

### 3. What sensor parameters are available?
Five physical sensor telemetry channels:
1. `temperature`: Thermal reading of machine housing/bearings (°C)
2. `vibration`: Mechanical vibration signal
3. `humidity`: Environmental relative humidity percentage (%)
4. `pressure`: Hydraulic or pneumatic line pressure (bar)
5. `energy_consumption`: Real-time electrical power draw (kW)

### 4. Which parameters can be used for anomaly detection?
The unsupervised anomaly detection model MUST strictly use raw sensor readings:
- `temperature`
- `vibration`
- `humidity`
- `pressure`
- `energy_consumption`

*(Optional derived temporal features such as rolling mean/std per machine can also be included).*

### 5. Which columns represent ground-truth labels?
- `anomaly_flag`: Primary binary ground-truth column for evaluating anomaly detection models (0 = Normal, 1 = Anomaly).

### 6. Which columns can be used for fault/condition identification?
- `failure_type`: Multi-class ground-truth fault category (`Normal`, `Vibration Issue`, `Overheating`, `Pressure Drop`, `Electrical Fault`).
- `machine_status`: Operational status indicator (0, 1, 2).
- `maintenance_required` & `downtime_risk`: Additional asset health flags.

### 7. Is this time-series data?
**Yes.** The dataset contains minute-by-minute timestamped observations (`timestamp`) tracked chronologically per `machine_id`. Preprocessing and train/validation/test splits must follow strict chronological ordering to reflect real-world time-series monitoring.

### 8. Are there class imbalances?
**Yes.**
- **Anomaly Detection**: Significant class imbalance. Normal instances comprise **91.08%** (91,084 rows), while Anomalies account for only **8.92%** (8,916 rows).
- **Fault Types**: Severe multi-class imbalance (`Normal`: 91,899, `Vibration Issue`: 3,129 [3.13%], `Overheating`: 1,989 [1.99%], `Pressure Drop`: 1,969 [1.97%], `Electrical Fault`: 1,014 [1.01%]).

### 9. Are there data leakage risks?
**High Risk if target or outcome columns are included during model training.**
Target columns (`anomaly_flag`, `failure_type`, `machine_status`, `predicted_remaining_life`, `downtime_risk`, `maintenance_required`) directly encode downstream diagnostic outcomes. If any of these are passed into the anomaly detector or feature scalar, the ML model will trivially memorize labels rather than learning physical sensor anomalies.

### 10. Which features should NOT be used for anomaly detection and why?
- `anomaly_flag`: Ground truth target; including it is direct label leakage.
- `failure_type`: Ground truth target for fault classification; including it causes target leakage.
- `machine_status`, `predicted_remaining_life`, `downtime_risk`, `maintenance_required`: Diagnostic outcomes created post-facto; including them would leak state information not present in raw sensor streams.
- `timestamp` & `machine_id`: Raw ID strings/datetimes should not be directly passed as numeric features; entity embeddings or rolling time windows should be used instead.
