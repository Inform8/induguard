import os
import math
import numpy as np
import pandas as pd
from typing import Dict, Any, List

from src.models.anomaly_detector import AnomalyDetector
from src.models.fault_classifier import FaultClassifier

# Define required sensor feature columns
REQUIRED_SENSOR_FIELDS = ['temperature', 'vibration', 'humidity', 'pressure', 'energy_consumption']

# Define operational baseline thresholds (derived from dataset statistics)
NORMAL_THRESHOLDS = {
    'temperature': {'mean': 75.0, 'std': 10.0, 'high_warn': 88.0, 'high_crit': 100.0},
    'vibration': {'mean': 50.0, 'std': 15.0, 'high_warn': 68.0, 'high_crit': 85.0},
    'humidity': {'low': 32.0, 'high': 78.0},
    'pressure': {'mean': 3.0, 'std': 1.15, 'low_crit': 1.5, 'high_crit': 4.7},
    'energy_consumption': {'mean': 2.75, 'std': 1.3, 'high_warn': 4.0, 'high_crit': 4.7}
}

RECOMMENDED_ACTIONS = {
    'Normal': "Continue routine operation and scheduled monitoring.",
    'Overheating': "Inspect cooling systems, lubrication levels, and thermal bearings immediately.",
    'Vibration Issue': "Check mechanical alignment, balance, and bearing tightness.",
    'Pressure Drop': "Inspect hydraulic line pressure, check for fluid leaks or valve failure.",
    'Electrical Fault': "Inspect power delivery unit, electrical wiring, and surge suppressors."
}


class ConditionAnalyzer:
    """
    Industrial Condition Reasoning Engine.
    Synthesizes ML Anomaly Detection + ML Fault Classification + Rule-Based Feature Deviations
    to output comprehensive asset condition reports.
    """

    def __init__(self, anomaly_detector_path: str = "models/anomaly_detector.joblib",
                 fault_classifier_path: str = "models/fault_classifier.joblib"):
        
        self.anomaly_detector = None
        self.fault_classifier = None

        if os.path.exists(anomaly_detector_path):
            self.anomaly_detector = AnomalyDetector.load_model(anomaly_detector_path)

        if os.path.exists(fault_classifier_path):
            self.fault_classifier = FaultClassifier.load_model(fault_classifier_path)

    def validate_payload(self, sensor_payload: Dict[str, Any]) -> tuple[bool, str, List[str]]:
        """
        Strict validation for incoming telemetry payload.
        Ensures machine_id and all required sensor fields are present and valid numeric values.
        """
        if not isinstance(sensor_payload, dict):
            return False, "Payload must be a dictionary.", ["Invalid payload type."]

        # 1. Validate machine_id
        machine_id = sensor_payload.get("machine_id", None)
        if machine_id is None or str(machine_id).strip() == "" or str(machine_id).strip().lower() in ["none", "null", "nan"]:
            return False, "Telemetry validation failed: Missing or invalid 'machine_id'.", ["Missing or invalid 'machine_id'."]

        # 2. Validate required sensor fields presence & float convertibility
        errors = []
        for field in REQUIRED_SENSOR_FIELDS:
            if field not in sensor_payload or sensor_payload[field] is None:
                errors.append(f"Missing required sensor field: '{field}'.")
                continue

            val = sensor_payload[field]
            try:
                float_val = float(val)
                if math.isnan(float_val) or math.isinf(float_val):
                    errors.append(f"Invalid numeric value for '{field}': non-finite number.")
            except (ValueError, TypeError):
                errors.append(f"Invalid numeric value for '{field}': cannot convert '{val}' to float.")

        if errors:
            msg = f"Telemetry validation failed: {errors[0]}"
            return False, msg, errors

        return True, "Valid", []

    def analyze_reading(self, sensor_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a single IoT sensor payload dictionary and generate a structured condition report.
        Strictly validates inputs without unsafe silent fallbacks.
        """
        # Strict Input Validation
        is_valid, err_msg, err_details = self.validate_payload(sensor_payload)
        if not is_valid:
            return {
                "status": "ERROR",
                "error": True,
                "error_message": err_msg,
                "details": err_details,
                "machine_id": sensor_payload.get("machine_id", None) if isinstance(sensor_payload, dict) else None,
                "timestamp": str(sensor_payload.get("timestamp", "N/A")) if isinstance(sensor_payload, dict) else "N/A"
            }

        machine_id = str(sensor_payload["machine_id"])
        timestamp = str(sensor_payload.get("timestamp", "N/A"))

        temp = float(sensor_payload["temperature"])
        vib = float(sensor_payload["vibration"])
        hum = float(sensor_payload["humidity"])
        press = float(sensor_payload["pressure"])
        energy = float(sensor_payload["energy_consumption"])

        validated_payload = {
            "timestamp": timestamp,
            "machine_id": machine_id,
            "temperature": temp,
            "vibration": vib,
            "humidity": hum,
            "pressure": press,
            "energy_consumption": energy
        }

        # 1. Run ML Anomaly Detector
        is_anomaly = False
        anomaly_score = 0.0
        if self.anomaly_detector:
            anomaly_res = self.anomaly_detector.predict_single(validated_payload)
            is_anomaly = anomaly_res["is_anomaly"]
            anomaly_score = anomaly_res["anomaly_score"]

        # 2. Run ML Fault Classifier
        predicted_fault = "Normal"
        fault_confidence = 1.0
        if self.fault_classifier:
            fault_res = self.fault_classifier.predict_single(validated_payload)
            predicted_fault = fault_res["predicted_fault"]
            fault_confidence = fault_res["confidence"]

        # 3. Rule-Based Feature Deviation & Reason Analysis
        reasons: List[str] = []

        if temp > NORMAL_THRESHOLDS['temperature']['high_crit']:
            reasons.append(f"Critical temperature spike detected ({temp:.1f}°C > {NORMAL_THRESHOLDS['temperature']['high_crit']}°C)")
        elif temp > NORMAL_THRESHOLDS['temperature']['high_warn']:
            reasons.append(f"Elevated temperature trend ({temp:.1f}°C > {NORMAL_THRESHOLDS['temperature']['high_warn']}°C)")

        if vib > NORMAL_THRESHOLDS['vibration']['high_crit']:
            reasons.append(f"Severe mechanical vibration ({vib:.1f} > {NORMAL_THRESHOLDS['vibration']['high_crit']})")
        elif vib > NORMAL_THRESHOLDS['vibration']['high_warn']:
            reasons.append(f"Moderate vibration elevation ({vib:.1f} > {NORMAL_THRESHOLDS['vibration']['high_warn']})")

        if press < NORMAL_THRESHOLDS['pressure']['low_crit']:
            reasons.append(f"Critical pressure drop detected ({press:.2f} bar < {NORMAL_THRESHOLDS['pressure']['low_crit']} bar)")
        elif press > NORMAL_THRESHOLDS['pressure']['high_crit']:
            reasons.append(f"Abnormal high pressure line build-up ({press:.2f} bar)")

        if energy > NORMAL_THRESHOLDS['energy_consumption']['high_crit']:
            reasons.append(f"Excessive electrical power draw ({energy:.2f} kW)")

        # Override ML fault prediction if nominal sensors show perfect normal behavior
        if not reasons and anomaly_score < 0.55:
            predicted_fault = "Normal"
            fault_confidence = 0.99
            is_anomaly = False

        # Align predicted fault with primary sensor deviation if physical breach occurs
        if temp > NORMAL_THRESHOLDS['temperature']['high_warn'] and predicted_fault == "Normal":
            predicted_fault = "Overheating"
        elif vib > NORMAL_THRESHOLDS['vibration']['high_warn'] and predicted_fault == "Normal":
            predicted_fault = "Vibration Issue"
        elif press < NORMAL_THRESHOLDS['pressure']['low_crit'] and predicted_fault == "Normal":
            predicted_fault = "Pressure Drop"

        if not reasons:
            reasons.append("All sensor readings within normal operating parameters.")

        # 4. Determine Machine Severity Status (NORMAL, WARNING, CRITICAL)
        if temp > NORMAL_THRESHOLDS['temperature']['high_crit'] or vib > NORMAL_THRESHOLDS['vibration']['high_crit'] or press < 1.0 or anomaly_score > 0.80:
            status = "CRITICAL"
        elif temp > NORMAL_THRESHOLDS['temperature']['high_warn'] or vib > NORMAL_THRESHOLDS['vibration']['high_warn'] or press < NORMAL_THRESHOLDS['pressure']['low_crit'] or anomaly_score > 0.55 or predicted_fault != "Normal":
            status = "WARNING"
        else:
            status = "NORMAL"

        # 5. Formulate Human-Readable Condition Summary
        if status == "CRITICAL":
            condition_summary = f"CRITICAL: {predicted_fault} detected with severe sensor deviation."
        elif status == "WARNING":
            condition_summary = f"WARNING: Abnormal sensor pattern detected ({predicted_fault})."
        else:
            condition_summary = "Normal: Machine operating within standard nominal parameters."


        action = RECOMMENDED_ACTIONS.get(predicted_fault, RECOMMENDED_ACTIONS['Normal'])
        if status == "CRITICAL" and predicted_fault == "Normal":
            action = "Dispatch technician for immediate visual and physical machine inspection."

        return {
            "timestamp": timestamp,
            "machine_id": machine_id,
            "status": status,
            "anomaly": is_anomaly,
            "anomaly_score": round(anomaly_score, 4),
            "predicted_fault": predicted_fault,
            "fault_confidence": round(fault_confidence, 4),
            "condition": condition_summary,
            "reasons": reasons,
            "recommended_action": action,
            "sensor_readings": {
                "temperature": temp,
                "vibration": vib,
                "humidity": hum,
                "pressure": press,
                "energy_consumption": energy
            }
        }


if __name__ == "__main__":
    analyzer = ConditionAnalyzer()
    
    # Test valid reading
    sample = {
        "timestamp": "2025-01-01 01:32:00",
        "machine_id": "M45",
        "temperature": 105.4,
        "vibration": 88.2,
        "humidity": 69.8,
        "pressure": 1.68,
        "energy_consumption": 4.85
    }
    report = analyzer.analyze_reading(sample)
    print("Valid Payload Result Status:", report["status"])

    # Test invalid reading (missing temperature)
    invalid_sample = {
        "machine_id": "M45",
        "vibration": 88.2
    }
    err_report = analyzer.analyze_reading(invalid_sample)
    print("Invalid Payload Error Result:", err_report)
