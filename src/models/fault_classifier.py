import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, f1_score

SENSOR_COLUMNS = ['temperature', 'vibration', 'humidity', 'pressure', 'energy_consumption']
TARGET_FAULT = 'failure_type'


class FaultClassifier:
    """
    Supervised Multi-Class Fault Classification model for industrial machines.
    Predicts fault type: 'Normal', 'Vibration Issue', 'Overheating', 'Pressure Drop', 'Electrical Fault'.
    """

    def __init__(self, n_estimators: int = 150, max_depth: int = 12, random_state: int = 42):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.random_state = random_state
        self.feature_names = SENSOR_COLUMNS
        self.target_name = TARGET_FAULT
        self.model = RandomForestClassifier(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            random_state=self.random_state,
            class_weight='balanced',
            n_jobs=-1
        )
        self.classes_ = None
        self.is_fitted = False

    def fit(self, X: pd.DataFrame | np.ndarray, y: pd.Series | np.ndarray):
        """Fit Random Forest Fault Classifier."""
        if isinstance(X, pd.DataFrame):
            X_input = X[self.feature_names].values
        else:
            X_input = X

        self.model.fit(X_input, y)
        self.classes_ = self.model.classes_
        self.is_fitted = True
        return self

    def predict(self, X: pd.DataFrame | np.ndarray) -> np.ndarray:
        """Predict multi-class fault string labels."""
        if not self.is_fitted:
            raise ValueError("Model is not fitted yet.")

        if isinstance(X, pd.DataFrame):
            X_input = X[self.feature_names].values
        else:
            X_input = X

        return self.model.predict(X_input)

    def predict_proba(self, X: pd.DataFrame | np.ndarray) -> np.ndarray:
        """Predict class probabilities."""
        if not self.is_fitted:
            raise ValueError("Model is not fitted yet.")

        if isinstance(X, pd.DataFrame):
            X_input = X[self.feature_names].values
        else:
            X_input = X

        return self.model.predict_proba(X_input)

    def predict_single(self, sensor_payload: dict) -> dict:
        """
        Predict fault condition for a single IoT telemetry reading payload.
        """
        missing = [f for f in self.feature_names if f not in sensor_payload]
        if missing:
            raise KeyError(f"Payload missing required sensor features: {missing}")

        features_df = pd.DataFrame([[sensor_payload[f] for f in self.feature_names]], columns=self.feature_names)
        pred_label = str(self.predict(features_df)[0])
        probs = self.predict_proba(features_df)[0]
        prob_dict = {cls_name: round(float(p), 4) for cls_name, p in zip(self.classes_, probs)}

        return {
            "predicted_fault": pred_label,
            "confidence": round(float(max(probs)), 4),
            "probabilities": prob_dict
        }

    def evaluate(self, X: pd.DataFrame | np.ndarray, y_true: pd.Series | np.ndarray) -> dict:
        """Evaluate model precision, recall, F1, and confusion matrix."""
        y_pred = self.predict(X)
        report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
        cm = confusion_matrix(y_true, y_pred, labels=self.classes_).tolist()

        return {
            "weighted_f1": round(float(f1_score(y_true, y_pred, average='weighted', zero_division=0)), 4),
            "classification_report": report,
            "confusion_matrix": cm,
            "classes": self.classes_.tolist() if hasattr(self.classes_, 'tolist') else list(self.classes_)
        }

    def save_model(self, path: str = "models/fault_classifier.joblib"):
        """Serialize model to disk."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self, path)
        print(f"Saved FaultClassifier model to {path}")

    @classmethod
    def load_model(cls, path: str = "models/fault_classifier.joblib") -> "FaultClassifier":
        """Deserialize model from disk."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found at {path}")
        return joblib.load(path)


if __name__ == "__main__":
    print("Testing FaultClassifier module...")
    # Train test script
    train_df = pd.read_csv("data/processed/train.csv")
    test_df = pd.read_csv("data/processed/test.csv")
    clf = FaultClassifier()
    clf.fit(train_df, train_df['failure_type'])
    metrics = clf.evaluate(test_df, test_df['failure_type'])
    print("Fault Classifier Weighted F1:", metrics['weighted_f1'])
    clf.save_model("models/fault_classifier.joblib")
