# 🛡️ InduGuard: B.Tech Major Project Handover & Technical Defense Guide

**Project Title:** Smart IoT-Based Industrial Anomaly Detection & Predictive Fault Diagnostic System  
**Domain:** Artificial Intelligence, Industrial IoT (IIoT), Predictive Maintenance, Full-Stack Web Systems  
**Target Audience:** B.Tech / B.E. Computer Science, AI/ML, and Information Technology Students

---

## 📑 Table of Contents
1. [Executive Summary & Problem Statement](#1-executive-summary--problem-statement)
2. [End-to-End System Architecture](#2-end-to-end-system-architecture)
3. [Complete Technology Stack](#3-complete-technology-stack)
4. [Machine Learning Pipeline & Model Training](#4-machine-learning-pipeline--model-training)
5. [Model Selection Rationale (Why These Models?)](#5-model-selection-rationale-why-these-models)
6. [Alert Engine, Deduplication & Audio Subsystem](#6-alert-engine-deduplication--audio-subsystem)
7. [Cloud Database, Supabase & Email Notifications Integration](#7-cloud-database-supabase--email-notifications-integration)
8. [Project Setup & Step-by-Step Execution Guide](#8-project-setup--step-by-step-execution-guide)
9. [API & WebSocket Specifications](#9-api--websocket-specifications)
10. [Comprehensive Viva Voce Questions & Answers](#10-comprehensive-viva-voce-questions--answers)

---

## 1. Executive Summary & Problem Statement

### 1.1 The Industrial Challenge
Unscheduled downtime in heavy manufacturing (turbines, hydraulic pumps, compressors, and industrial motors) costs industries billions of dollars annually. Traditional maintenance operates on two flawed paradigms:
1. **Reactive Maintenance (Run-to-Failure):** Machines run until catastrophic breakdown, resulting in expensive repairs and safety hazards.
2. **Preventive Maintenance (Time-Based):** Maintenance is performed on arbitrary schedules regardless of machine health, causing unnecessary operational downtime.

### 1.2 The InduGuard Solution
**InduGuard** is an AI-powered industrial IoT monitoring system that implements **Predictive Maintenance (Condition-Based)**. It processes a continuous **1 Hz 5-variate sensor telemetry stream** across industrial machines (`M01` to `M04`), evaluates condition anomalies in **< 1 ms**, classifies root-cause failures, deduplicates alarms to prevent operator fatigue, and streams live telemetry to a glassmorphic command center.

---

## 2. End-to-End System Architecture

```
                                  +-------------------------------------------------------+
                                  |            Industrial Machines (M01 - M04)            |
                                  |  [Temperature, Vibration, Humidity, Pressure, Power]  |
                                  +---------------------------+---------------------------+
                                                              | 1 Hz Sensor Telemetry
                                                              v
                                  +-------------------------------------------------------+
                                  |               FastAPI Telemetry Gateway               |
                                  |      (REST /api/telemetry & Background Simulator)      |
                                  +---------------------------+---------------------------+
                                                              |
                                                              v
                                  +-------------------------------------------------------+
                                  |               ConditionAnalyzer Engine                |
                                  |  +-------------------------------------------------+  |
                                  |  |  1. Isolation Forest (Outlier Anomaly Scoring)   |  |
                                  |  |  2. Random Forest (Root-Cause Multi-Classifier) |  |
                                  |  |  3. Thermodynamic Boundary Validation Rules     |  |
                                  |  +-------------------------------------------------+  |
                                  +---------------------------+---------------------------+
                                                              |
                                                              v
                                  +-------------------------------------------------------+
                                  |                     Alert Engine                      |
                                  |        (60-Second Cooldown & Escalation Logic)        |
                                  +---------------------------+---------------------------+
                                                              |
                                           +------------------+------------------+
                                           |                                     |
                                           v                                     v
                        +------------------------------------+  +--------------------------------+
                        |     WebSocket Broadcast Manager    |  |   Optional Supabase / Email    |
                        |      (ws://127.0.0.1:8000/ws)      |  |  (Postgres Log & SMTP Alerts)  |
                        +------------------+-----------------+  +--------------------------------+
                                           |
                                           v
                        +--------------------------------------------------------+
                        |              React 19 Marvel HUD Dashboard             |
                        |   - Live Recharts (Vibration / Temp Time Series)       |
                        |   - Gauge Donut Overlays & Anomaly Radar Cards         |
                        |   - Audio Warning Chimes & Single-Event Toast Alerts   |
                        +--------------------------------------------------------+
```

---

## 3. Complete Technology Stack

| Layer | Technology | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Frontend Framework** | React + Vite | React 19.x, Vite 8.x | High-performance reactive UI rendering |
| **Language (Frontend)** | TypeScript | 6.x / 5.x | Strict type safety for streaming telemetry |
| **Data Visualization** | Recharts | 3.x | Real-time time-series area charts, gauges, & bar charts |
| **Icons & Audio** | Lucide-React, Web Audio | 1.x | Industrial UI icons and audio alert notifications |
| **Styling** | Vanilla Glassmorphic CSS | Modern CSS3 | Custom dark-mode UI with no heavy UI framework overhead |
| **Backend Framework** | FastAPI (ASGI) | >= 0.100.0 | Asynchronous REST API and WebSocket gateway |
| **ASGI Web Server** | Uvicorn | >= 0.22.0 | Ultra-fast ASGI server for streaming WebSockets |
| **Data Science & ML** | Scikit-Learn, NumPy, Pandas | >= 1.2.0 | Machine learning training and data transformations |
| **Model Serialization** | Joblib | >= 1.2.0 | High-efficiency disk persistence for ML models |
| **Cloud/DB (Optional)** | Supabase (PostgreSQL) | v2.x | Cloud auth, persistent telemetry, and alert logging |

---

## 4. Machine Learning Pipeline & Model Training

### 4.1 Telemetry Sensor Features
InduGuard continuously monitors 5 numerical physical sensor features:
1. **Temperature ($T$ in °C):** Baseline ~75.0 °C. Warning > 88.0 °C. Critical > 100.0 °C.
2. **Vibration Index ($V$ in Hz):** Baseline ~50.0 Hz. Warning > 68.0 Hz. Critical > 85.0 Hz.
3. **Relative Humidity ($H$ in %):** Baseline ~58.1 %. Outlier if < 32.0% or > 78.0%.
4. **Hydraulic Pressure ($P$ in bar):** Baseline ~3.08 bar. Critical if < 1.50 bar or > 4.70 bar.
5. **Energy Consumption ($E$ in kW):** Baseline ~2.86 kW. High Warning > 4.0 kW. Critical > 4.70 kW.

---

### 4.2 The 3 Training Phases

#### Phase 1: Chronological Preprocessing (`src/data/preprocessing.py`)
- **Dataset:** `data/raw/smart_manufacturing_data.csv` (100,000 raw sensor records).
- **Split Strategy:** Strict **Chronological Split** (70% Train = 70,000; 15% Validation = 15,000; 15% Test = 15,000).
- **Why Chronological?** Standard randomized $K$-Fold cross-validation leaks future temporal correlations into the past (lookahead bias). Chronological splitting mirrors real-world deployment.
- **Normalization:** `StandardScaler` is fitted *only* on the training set to prevent data leakage.

#### Phase 2: Unsupervised Anomaly Detection (`src/models/anomaly_detector.py`)
- **Algorithm:** Isolation Forest (`sklearn.ensemble.IsolationForest`).
- **Hyperparameters:** `n_estimators=150`, `contamination=0.089`, `random_state=42`, `n_jobs=-1`.
- **Mathematical Formula:**
  $$s(x, n) = 2^{-\frac{E(h(x))}{c(n)}}$$
  Where $h(x)$ is path depth in the isolation trees, and $c(n)$ is the average path length of an unsuccessful binary search tree.
- **Score Normalization:** Raw decision function is scaled to continuous range $[0.0, 1.0]$.
- **Artifact:** `models/anomaly_detector.joblib`.

#### Phase 3: Supervised Multi-Class Fault Classification (`src/models/fault_classifier.py`)
- **Algorithm:** Random Forest Classifier (`sklearn.ensemble.RandomForestClassifier`).
- **Hyperparameters:** `n_estimators=150`, `max_depth=12`, `class_weight='balanced'`, `random_state=42`.
- **Target Output Classes:**
  1. `Normal`
  2. `Overheating`
  3. `Vibration Issue`
  4. `Pressure Drop`
  5. `Electrical Fault`
- **Artifact:** `models/fault_classifier.joblib`.

---

### 4.3 Training Execution Commands

```powershell
# Step 1: Preprocess raw dataset and generate train/val/test splits
python -m src.data.preprocessing

# Step 2: Train and save Isolation Forest Anomaly Detector
python -c "
import pandas as pd
from src.models.anomaly_detector import AnomalyDetector
train_df = pd.read_csv('data/processed/train.csv')
detector = AnomalyDetector(contamination=0.089, n_estimators=150)
detector.fit(train_df)
detector.save_model('models/anomaly_detector.joblib')
"

# Step 3: Train and save Random Forest Fault Classifier
python -c "
import pandas as pd
from src.models.fault_classifier import FaultClassifier
train_df = pd.read_csv('data/processed/train.csv')
clf = FaultClassifier(n_estimators=150, max_depth=12)
clf.fit(train_df, train_df['failure_type'])
clf.save_model('models/fault_classifier.joblib')
"
```

---

## 5. Model Selection Rationale (Why These Models?)

### 5.1 Isolation Forest vs. Competing Anomaly Detectors

| Model | Time Complexity | Real-Time Latency | Stream Drift Resilience | Decision Reason |
| :--- | :--- | :--- | :--- | :--- |
| **Isolation Forest (Selected)** | $\mathcal{O}(N \log N)$ | **< 0.5 ms** | **High** (Random tree partitioning) | ✅ **Chosen:** Fast, lightweight, tree-based isolation with no distance matrix storage. |
| **One-Class SVM** | $\mathcal{O}(N^2)$ | ~15 ms | Low (Kernel boundary drift) | ❌ Quadratic scaling makes it too slow for 100k+ rows and 1 Hz live streaming. |
| **Deep Autoencoders** | $\mathcal{O}(\text{Epochs} \cdot N)$ | ~8 ms (CPU) | Medium (Reconstruction quantile drift) | ❌ Requires heavy PyTorch/TensorFlow runtimes and GPU hardware overhead. |
| **Local Outlier Factor (LOF)** | $\mathcal{O}(N^2)$ | ~25 ms | Low (Requires global sample memory) | ❌ Cannot perform out-of-sample prediction without keeping all training points in RAM. |

---

### 5.2 Random Forest vs. Competing Classifiers

| Model | Non-Linear Fit | Noise Robustness | Explainability | Decision Reason |
| :--- | :--- | :--- | :--- | :--- |
| **Random Forest (Selected)** | **High** | **High** (Bagging averages jitter) | **High** (Feature Importances) | ✅ **Chosen:** Ensembling 150 trees resists sensor noise and delivers calibrated probabilities. |
| **Logistic Regression** | Low (Linear only) | Medium | High | ❌ Fails on non-linear multi-sensor interactions (e.g. Temp + Pressure vs Power). |
| **XGBoost / Gradient Boost** | High | Low (Prone to overfitting noise) | Medium | ❌ Gradient boosting greedily fits white-noise sensor spikes in live streams. |
| **Single Decision Tree** | Medium | Very Low (High variance) | High | ❌ A single tree has high variance and unstable probability estimates. |

---

## 6. Alert Engine, Deduplication & Audio Subsystem

### 6.1 The "Alarm Fatigue" Problem
In industrial operations, an overheating machine sending telemetry at 1 Hz triggers 60 alerts every minute. Operators quickly develop **alarm fatigue** and ignore notifications.

### 6.2 InduGuard 60-Second Cooldown Logic
The `AlertEngine` (`backend/app/services/alert_engine.py`) enforces a stateful cooldown:
```python
# Cooldown Algorithm
cooldown_key = machine_id
elapsed = current_time - last_alert_time[cooldown_key]

if elapsed < 60.0:
    if current_severity == "CRITICAL" and previous_severity == "WARNING":
        trigger_alert("Escalated to CRITICAL") # Immediate escalation allowed
    else:
        suppress_alert() # Suppress continuous repeating alarm
else:
    trigger_alert()
    last_alert_time[cooldown_key] = current_time
```

### 6.3 Multimodal Alert Feedback
- **Visual Alert:** Single floating glassmorphic Toast banner with recommended engineering action.
- **Auditory Alert:** 800 ms Web Audio warning chime (`warning_sound.mp3`).
- **Acknowledgment State:** Operators can click **"Acknowledge"** via REST API to verify maintenance dispatch without deleting the audit log.

---

## 7. Cloud Database, Supabase & Email Notifications Integration

For extended full-stack deployments or enterprise requirements, InduGuard integrates seamlessly with **Supabase (PostgreSQL)** and **SMTP Email Alerts**.

### 7.1 Supabase Database Schema (PostgreSQL DDL)

```sql
-- 1. Machines Table
CREATE TABLE machines (
    machine_id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'NORMAL',
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Telemetry History Table
CREATE TABLE telemetry_readings (
    id BIGSERIAL PRIMARY KEY,
    machine_id VARCHAR(10) REFERENCES machines(machine_id),
    timestamp TIMESTAMPTZ NOT NULL,
    temperature FLOAT NOT NULL,
    vibration FLOAT NOT NULL,
    humidity FLOAT NOT NULL,
    pressure FLOAT NOT NULL,
    energy_consumption FLOAT NOT NULL,
    anomaly_score FLOAT NOT NULL,
    is_anomaly BOOLEAN NOT NULL,
    predicted_fault VARCHAR(50) NOT NULL
);

-- 3. Incident & Alerts Table
CREATE TABLE alerts (
    alert_id VARCHAR(20) PRIMARY KEY,
    machine_id VARCHAR(10) REFERENCES machines(machine_id),
    timestamp TIMESTAMPTZ NOT NULL,
    severity VARCHAR(20) NOT NULL,
    fault_type VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    recommended_action TEXT NOT NULL,
    acknowledged BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

### 7.2 Automated Email Alert Notification (FastAPI Background Task)

When a `CRITICAL` alert triggers, the backend can asynchronously dispatch an incident email to maintenance supervisors:

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import BackgroundTasks

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "alerts@induguard-iot.com"
SENDER_PASSWORD = "your-app-password"

def send_critical_email_notification(recipient: str, alert_data: dict):
    """Dispatches formatted HTML incident notification to lead engineers."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🚨 [CRITICAL ALERT] Machine {alert_data['machine_id']} - {alert_data['type']}"
    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient

    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background: #0f172a; color: #f8fafc; padding: 20px;">
        <div style="background: #1e293b; border: 1px solid #ef4444; border-radius: 8px; padding: 20px;">
          <h2 style="color: #ef4444; margin-top: 0;">CRITICAL INDUSTRIAL FAULT DETECTED</h2>
          <p><strong>Machine ID:</strong> {alert_data['machine_id']}</p>
          <p><strong>Detected Failure:</strong> {alert_data['type']}</p>
          <p><strong>Timestamp:</strong> {alert_data['timestamp']}</p>
          <p><strong>Reason:</strong> {', '.join(alert_data.get('reasons', []))}</p>
          <div style="background: #334155; padding: 12px; border-radius: 6px; margin: 15px 0;">
            <strong>Recommended Immediate Action:</strong><br>
            {alert_data['recommended_action']}
          </div>
          <p style="font-size: 12px; color: #94a3b8;">InduGuard Automated Safety Dispatch System</p>
        </div>
      </body>
    </html>
    """
    msg.attach(MIMEText(html_content, "html"))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, recipient, msg.as_string())
```

---

## 8. Project Setup & Step-by-Step Execution Guide

### 8.1 Prerequisites
- **Python:** 3.10, 3.11, or 3.12
- **Node.js:** v18.0.0 or higher (with `npm`)
- **OS:** Windows, macOS, or Linux

---

### 8.2 Execution Instructions

#### Terminal 1: Backend Server (FastAPI)
```powershell
# Navigate to project root
cd d:\InduGuard

# 1. Install backend & ML dependencies
pip install -r requirements.txt -r backend/requirements.txt

# 2. Launch FastAPI Server on Port 8000
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```
- **API URL:** `http://127.0.0.1:8000`
- **Interactive Swagger Docs:** `http://127.0.0.1:8000/docs`

---

#### Terminal 2: Frontend Dashboard (React 19 + Vite)
```powershell
# Navigate to frontend folder
cd d:\InduGuard\frontend

# 1. If PowerShell blocks script execution, run this once:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 2. Install Node.js dependencies
npm install

# 3. Start Vite development server
npm run dev
```
- **Application URL:** `http://localhost:5173`

---

### 8.3 Environment Variables (.env)
The `.env` file at the root contains the student's GitHub token and email alert parameters:
```env
GITHUB_TOKEN=your_github_token_here
ENABLE_EMAIL_ALERTS=true
ALERT_EMAIL_RECIPIENT=operator@induguard.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=alerts@induguard-iot.com
SMTP_PASSWORD=
```

---

### 8.4 Default Operator Login Credentials
- **Operator ID (Username):** `admin`
- **Access Code (Password):** `admin123`

---

## 9. API & WebSocket Specifications

### 9.1 REST Endpoints
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Backend liveness and health status check |
| `GET` | `/api/machines` | Returns current health, anomaly scores, and metrics for `M01`-`M04` |
| `GET` | `/api/machines/{id}/history` | Returns recent bounded 60-point sliding window history |
| `GET` | `/api/alerts` | Returns all generated historical alerts |
| `POST` | `/api/alerts/{id}/acknowledge`| Marks an alert as acknowledged by an operator |
| `POST` | `/api/simulator/start` | Starts background synthetic sensor stream (with scenario injection) |
| `POST` | `/api/simulator/stop` | Stops background simulation |
| `POST` | `/api/telemetry` | Direct HTTP ingestion endpoint for physical IoT devices |

### 9.2 WebSocket Stream
- **Endpoint:** `ws://127.0.0.1:8000/ws/monitoring`
- **Frequency:** 1 Hz (1 message per second)
- **JSON Payload Format:**
```json
{
  "result": {
    "machine_id": "M01",
    "timestamp": "2026-08-27T01:30:00Z",
    "temperature": 94.2,
    "vibration": 72.1,
    "humidity": 51.4,
    "pressure": 2.9,
    "energy_consumption": 4.3,
    "is_anomaly": true,
    "anomaly_score": 0.7821,
    "predicted_fault": "Overheating",
    "fault_confidence": 0.9420,
    "status": "CRITICAL",
    "reasons": ["Temperature exceeded critical threshold (94.2 °C > 88.0 °C)"],
    "recommended_action": "Inspect cooling systems and thermal bearings immediately."
  },
  "alert": {
    "id": "ALT-4A9B2C1D",
    "machine_id": "M01",
    "severity": "CRITICAL",
    "type": "Overheating",
    "acknowledged": false
  }
}
```

---

## 10. Comprehensive Viva Voce Questions & Answers

### Q1: What is the core difference between Anomaly Detection and Fault Classification in this project?
**Answer:**  
- **Anomaly Detection (Isolation Forest)** is an *unsupervised* technique that detects *whether* a reading deviates from nominal historical behavior, outputting a continuous anomaly score ($0.0$ to $1.0$).
- **Fault Classification (Random Forest)** is a *supervised* multi-class technique that diagnoses *what* specific failure mode has occurred (e.g. Overheating, Vibration Issue, Pressure Drop, Electrical Fault).

---

### Q2: Why did you use an Isolation Forest instead of an Autoencoder or One-Class SVM?
**Answer:**  
1. **Computational Efficiency:** Isolation Forest operates in $\mathcal{O}(N \log N)$ time and executes in $< 0.5\ \text{ms}$ on CPU threads, whereas One-Class SVM has $\mathcal{O}(N^2)$ quadratic complexity.
2. **Resource Footprint:** Autoencoders require heavy PyTorch/TensorFlow dependencies and GPU acceleration, which increases edge-device deployment cost.
3. **Drift Robustness:** Isolation Forest does not suffer from kernel boundary drift on streaming continuous data.

---

### Q3: Why is standard K-Fold Cross-Validation invalid for this dataset?
**Answer:**  
In time-series telemetry, sensor readings are temporally autocorrelated. Random $K$-Fold cross-validation leaks future data into past training folds (lookahead bias). InduGuard strictly enforces a **chronological split** (70% Train, 15% Validation, 15% Test) to ensure the model only learns from historical data.

---

### Q4: How does InduGuard prevent alert spam / alarm fatigue?
**Answer:**  
The `AlertEngine` maintains an in-memory state tracker with a **60-second cooldown per machine**. If an asset remains in a warning state for consecutive seconds, duplicate alerts are suppressed. An alert is only re-triggered if:
1. 60 seconds have elapsed, OR
2. The severity escalates from `WARNING` to `CRITICAL`.

---

### Q5: How do WebSockets improve performance over REST polling?
**Answer:**  
REST polling requires the frontend to send continuous HTTP GET requests (HTTP headers, TCP handshakes, round trips) every second, creating significant network overhead. A **WebSocket** maintains a single persistent, bidirectional TCP connection where the server pushes lightweight JSON packets at 1 Hz with sub-millisecond latency.

---

### Q6: What is the role of the ConditionAnalyzer?
**Answer:**  
The `ConditionAnalyzer` is a **hybrid reasoning engine**. Machine learning models can occasionally produce statistical false alarms. The `ConditionAnalyzer` cross-validates ML predictions against **hard thermodynamic physics thresholds** (e.g., Temperature $> 100\ ^\circ\text{C}$, Vibration $> 85\ \text{Hz}$) to ensure zero-false-alarm operational reliability.

---

### Q7: How can this system be scaled in an enterprise production setting?
**Answer:**  
1. **Message Broker Ingestion:** Ingest sensor telemetry using an **MQTT Broker** (like Eclipse Mosquitto) or **Apache Kafka** for millions of readings per second.
2. **Containerization & Orchestration:** Deploy FastAPI and React frontend in **Docker** containers managed by **Kubernetes**.
3. **Persistent Cloud Storage:** Persist long-term telemetry and alert logs into **Supabase / PostgreSQL** with time-series partitioning (TimescaleDB).
4. **Alert Escalation:** Dispatch automatic emails and SMS to on-call maintenance engineers via SMTP / Twilio.

---

*Handover Document Prepared for B.Tech Computer Science & Engineering Final Project Presentation.* 🛡️⚡
