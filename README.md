# Smart IoT-Based Industrial Anomaly Detection System 🛡️⚡

InduGuard is an AI-driven real-time health monitoring and anomaly detection platform for industrial machinery. It combines **Isolation Forest anomaly detection**, **Random Forest fault classification**, and **physical thermodynamic reasoning** to deliver zero-false-alarm predictive maintenance.

---

## 🔐 System Authentication

The application is secured with a centralized operator authentication portal. Upon launching the frontend, you must authenticate to access the dashboard and telemetry commands.

**Default Administrator Login:**
- **Operator ID (Username):** `admin`
- **Access Code (Password):** `admin123`

---

## 📖 Complete Technical Documentation

For in-depth mathematical justifications, model selection rationale (Isolation Forest vs One-Class SVM/Autoencoders, Random Forest vs XGBoost), architecture diagrams, and API specifications, please read:

👉 **[PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md)**

---

## ⚡ Quick Start Guide

### Option 1: One-Click Windows Launchers

1. **Start Backend**: Double-click `run_backend.bat` (or run `.\run_backend.bat` in PowerShell).
2. **Start Frontend**: Double-click `run_frontend.bat` (or run `.\run_frontend.bat` in PowerShell).

---

### Option 2: Manual Terminal Commands

#### 1. Backend Server
```bash
# Install dependencies
pip install -r requirements.txt

# Launch FastAPI Server on Port 8000
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```
- API Documentation: `http://127.0.0.1:8000/docs`

#### 2. Frontend UI
```bash
# Navigate to frontend
cd frontend

# Install dependencies & run Vite dev server
npm install
npm run dev
```
- Open Application: `http://localhost:5173`

---

## ⚙️ Core Features

- **Real-Time 1 Hz Telemetry Streaming**: WebSockets & REST API ingesting Temperature, Vibration, Humidity, Pressure, and Power Draw.
- **Sub-Millisecond Inference**: Dual-model machine learning pipeline scoring outliers and classifying fault modes.
- **Single-Alert Deduplication**: Enforces a 60-second cooldown per machine to eliminate alarm fatigue.
- **Marvel HUD Command Center**: Glassmorphic UI featuring live time-series charts, statistical mean overlays, temperature donut gauges, audio MP3 chime alerts, and interactive single-machine focus mode.

---

## 📂 Project Structure

```
Johnson/
├── backend/                # FastAPI Application & WebSocket Routes
├── frontend/               # React 19 + TypeScript + Vite Dashboard
├── models/                 # Joblib ML Model Artifacts
├── simulator/              # Async Telemetry Simulator & Fault Injectors
├── src/                    # Core Analytics, Preprocessing, & ML Modules
├── run_backend.bat         # Launcher for Backend
├── run_frontend.bat        # Launcher for Frontend
├── README.md               # Quick Start Guide
└── PROJECT_DOCUMENTATION.md # Comprehensive Technical Documentation
```