import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

SENSOR_COLUMNS = ['temperature', 'vibration', 'humidity', 'pressure', 'energy_consumption']


class AnomalyDetector:
    """
    Unsupervised Anomaly Detector using Isolation Forest algorithm.
    Trained strictly on numerical sensor telemetry features.
    """

    def __init__(self, contamination: float = 0.09, n_estimators: int = 100, random_state: int = 42):
        self.contamination = contamination
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.feature_names = SENSOR_COLUMNS
        self.model = IsolationForest(
            contamination=self.contamination,
            n_estimators=self.n_estimators,
            random_state=self.random_state,
            n_jobs=-1
        )
        self.is_fitted = False

    def fit(self, X: pd.DataFrame | np.ndarray):
        """Fit Isolation Forest model on sensor features."""
        if isinstance(X, pd.DataFrame):
            X_input = X[self.feature_names].values
        else:
            X_input = X

        self.model.fit(X_input)
        self.is_fitted = True
        return self

    def predict(self, X: pd.DataFrame | np.ndarray) -> np.ndarray:
        """
        Predict binary anomaly flag.
        Returns:
            np.ndarray: 1 for anomaly, 0 for normal.
        """
        if not self.is_fitted:
            raise ValueError("Model is not fitted yet.")

        if isinstance(X, pd.DataFrame):
            X_input = X[self.feature_names].values
        else:
            X_input = X

        # IsolationForest returns -1 for outlier/anomaly, 1 for inlier/normal
        raw_preds = self.model.predict(X_input)
        binary_preds = np.where(raw_preds == -1, 1, 0)
        return binary_preds

    def score_samples(self, X: pd.DataFrame | np.ndarray) -> np.ndarray:
        """
        Calculate anomaly score (normalized between 0.0 and 1.0).
        Higher score represents higher degree of abnormality.
        """
        if not self.is_fitted:
            raise ValueError("Model is not fitted yet.")

        if isinstance(X, pd.DataFrame):
            X_input = X[self.feature_names].values
        else:
            X_input = X

        # decision_function: lower/negative values -> more abnormal, higher/positive -> normal
        scores = self.model.decision_function(X_input)
        # Convert decision function score to normalized anomaly score (0.0 to 1.0)
        anomaly_scores = 0.5 - (scores * 2.0)
        return np.clip(anomaly_scores, 0.0, 1.0)


    def predict_single(self, sensor_payload: dict) -> dict:
        """
        Predict anomaly status for a single IoT telemetry reading payload.
        Example payload:
        {
            "temperature": 92.4,
            "vibration": 65.1,
            "humidity": 45.0,
            "pressure": 3.1,
            "energy_consumption": 4.2
        }
        """
        # Validate required features
        missing = [f for f in self.feature_names if f not in sensor_payload]
        if missing:
            raise KeyError(f"Payload missing required sensor features: {missing}")

        features_df = pd.DataFrame([[sensor_payload[f] for f in self.feature_names]], columns=self.feature_names)
        is_anomaly = bool(self.predict(features_df)[0])
        score = float(self.score_samples(features_df)[0])

        return {
            "is_anomaly": is_anomaly,
            "anomaly_score": round(score, 4),
            "raw_features": {f: sensor_payload[f] for f in self.feature_names}
        }

    def evaluate(self, X: pd.DataFrame | np.ndarray, y_true: np.ndarray | pd.Series) -> dict:
        """Calculate quantitative evaluation metrics against ground truth labels."""
        y_pred = self.predict(X)
        scores = self.score_samples(X)

        p = precision_score(y_true, y_pred, zero_division=0)
        r = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        auc = roc_auc_score(y_true, scores)
        cm = confusion_matrix(y_true, y_pred).tolist()

        return {
            "precision": round(float(p), 4),
            "recall": round(float(r), 4),
            "f1_score": round(float(f1), 4),
            "roc_auc": round(float(auc), 4),
            "confusion_matrix": cm,
            "false_positives": cm[0][1],
            "false_negatives": cm[1][0]
        }

    def save_model(self, path: str = "models/anomaly_detector.joblib"):
        """Serialize model to disk."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self, path)
        print(f"Saved AnomalyDetector model to {path}")

    @classmethod
    def load_model(cls, path: str = "models/anomaly_detector.joblib") -> "AnomalyDetector":
        """Deserialize model from disk."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found at {path}")
        return joblib.load(path)


if __name__ == "__main__":
    print("Testing AnomalyDetector module...")
    # Quick sanity check with synthetic data
    X_dummy = pd.DataFrame(np.random.randn(100, 5), columns=SENSOR_COLUMNS)
    detector = AnomalyDetector()
    detector.fit(X_dummy)
    test_sample = {"temperature": 110.0, "vibration": 95.0, "humidity": 50.0, "pressure": 4.5, "energy_consumption": 4.8}
    res = detector.predict_single(test_sample)
    print("Sample Single Inference:", res)
