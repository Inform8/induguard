import os
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

# Define sensor feature column names
SENSOR_COLUMNS = ['temperature', 'vibration', 'humidity', 'pressure', 'energy_consumption']
TARGET_ANOMALY = 'anomaly_flag'
TARGET_FAULT = 'failure_type'
ID_COLUMNS = ['timestamp', 'machine_id']


class IndustrialDataPreprocessor:
    """
    Reproducible preprocessing and chronological data splitting pipeline
    for industrial machine sensor datasets.
    """

    def __init__(self, raw_data_path: str = "data/raw/smart_manufacturing_data.csv"):
        self.raw_data_path = raw_data_path
        self.scaler = StandardScaler()
        self.sensor_cols = SENSOR_COLUMNS
        self.is_fitted = False

    def load_data(self) -> pd.DataFrame:
        """Load raw CSV dataset and validate basic structure."""
        if not os.path.exists(self.raw_data_path):
            raise FileNotFoundError(f"Raw dataset not found at {self.raw_data_path}")

        df = pd.read_csv(self.raw_data_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Sort chronologically by machine_id and timestamp
        df = df.sort_values(by=['timestamp', 'machine_id']).reset_index(drop=True)
        return df

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean missing values, duplicates, and handle basic sanity checks."""
        df_clean = df.copy()
        
        # Remove duplicate rows if any
        df_clean = df_clean.drop_duplicates().reset_index(drop=True)
        
        # Fill/forward fill any missing sensor readings per machine if needed
        for col in self.sensor_cols:
            if df_clean[col].isnull().sum() > 0:
                df_clean[col] = df_clean.groupby('machine_id')[col].ffill().bfill()
                
        return df_clean

    def chronological_split(self, df: pd.DataFrame, train_ratio: float = 0.70, val_ratio: float = 0.15):
        """
        Perform a strict chronological split across time to prevent temporal data leakage.
        Train: Earlier observations (0% to train_ratio)
        Validation: Middle observations (train_ratio to train_ratio + val_ratio)
        Test: Latest observations (train_ratio + val_ratio to 100%)
        """
        n = len(df)
        train_end = int(n * train_ratio)
        val_end = int(n * (train_ratio + val_ratio))

        train_df = df.iloc[:train_end].copy()
        val_df = df.iloc[train_end:val_end].copy()
        test_df = df.iloc[val_end:].copy()

        return train_df, val_df, test_df

    def fit_scaler(self, train_df: pd.DataFrame):
        """Fit StandardScaler strictly on training set sensor features."""
        self.scaler.fit(train_df[self.sensor_cols])
        self.is_fitted = True

    def transform_features(self, df: pd.DataFrame) -> np.ndarray:
        """Scale sensor features using the fitted scaler."""
        if not self.is_fitted:
            raise ValueError("Scaler has not been fitted yet. Call fit_scaler first.")
        return self.scaler.transform(df[self.sensor_cols])

    def run_pipeline(self, output_dir: str = "data/processed/"):
        """Run complete preprocessing and save split datasets and fitted scaler."""
        print("Loading raw dataset...")
        df = self.load_data()
        
        print("Cleaning dataset...")
        df_clean = self.clean_data(df)
        
        print(f"Splitting dataset chronologically ({len(df_clean)} rows)...")
        train_df, val_df, test_df = self.chronological_split(df_clean)
        
        print("Fitting scaler on training set...")
        self.fit_scaler(train_df)
        
        # Save processed splits and scaler
        os.makedirs(output_dir, exist_ok=True)
        train_df.to_csv(os.path.join(output_dir, "train.csv"), index=False)
        val_df.to_csv(os.path.join(output_dir, "val.csv"), index=False)
        test_df.to_csv(os.path.join(output_dir, "test.csv"), index=False)
        
        scaler_path = os.path.join(output_dir, "scaler.joblib")
        joblib.dump(self.scaler, scaler_path)
        
        print(f"Pipeline complete! Saved processed data to {output_dir}")
        print(f"Train set: {len(train_df)} rows | Val set: {len(val_df)} rows | Test set: {len(test_df)} rows")
        return train_df, val_df, test_df


if __name__ == "__main__":
    pipeline = IndustrialDataPreprocessor()
    pipeline.run_pipeline()
