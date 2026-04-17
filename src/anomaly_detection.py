"""
anomaly_detection.py
--------------------
Detects climate anomalies using:
1. Z-Score method (statistical outliers)
2. IQR method (robust outlier detection)
3. Rolling mean deviation (temporal anomalies)
4. Labels anomaly type: Heatwave, Cold Snap, Heavy Rainfall, Drought
"""

import pandas as pd
import numpy as np


def zscore_anomalies(df: pd.DataFrame, column: str, threshold: float = 2.5) -> pd.DataFrame:
    """
    Flag rows where |z-score| > threshold as anomalies.
    Returns a copy with added 'zscore' and 'anomaly_zscore' columns.
    """
    df = df.copy()
    mean = df[column].mean()
    std = df[column].std()
    df[f"zscore_{column}"] = ((df[column] - mean) / std).round(3)
    df[f"anomaly_zscore_{column}"] = df[f"zscore_{column}"].abs() > threshold
    count = df[f"anomaly_zscore_{column}"].sum()
    print(f"[Z-Score] '{column}': {count} anomalies detected (threshold={threshold})")
    return df


def iqr_anomalies(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Flag values outside [Q1 - 1.5*IQR, Q3 + 1.5*IQR] as anomalies.
    """
    df = df.copy()
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    df[f"anomaly_iqr_{column}"] = (df[column] < lower) | (df[column] > upper)
    count = df[f"anomaly_iqr_{column}"].sum()
    print(f"[IQR]     '{column}': {count} anomalies detected (IQR range: {lower:.2f} – {upper:.2f})")
    return df


def rolling_anomalies(df: pd.DataFrame, column: str, window: int = 30, threshold: float = 2.0) -> pd.DataFrame:
    """
    Detect anomalies by comparing daily value to its rolling mean ± n*std.
    Better for detecting local/temporal anomalies like heatwaves.
    """
    df = df.copy()
    roll_mean = df[column].rolling(window=window, center=True, min_periods=1).mean()
    roll_std = df[column].rolling(window=window, center=True, min_periods=1).std()
    deviation = (df[column] - roll_mean).abs()
    df[f"roll_anomaly_{column}"] = deviation > (threshold * roll_std)
    count = df[f"roll_anomaly_{column}"].sum()
    print(f"[Rolling] '{column}': {count} anomalies detected (window={window}, threshold={threshold}σ)")
    return df


def label_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Label anomaly type based on which variable is extreme.
    Categories: Heatwave, Cold Snap, Heavy Rainfall, Drought, Normal
    """
    df = df.copy()
    conditions = [
        df["roll_anomaly_temperature_c"] & (df["temperature_c"] > df["temperature_c"].mean()),
        df["roll_anomaly_temperature_c"] & (df["temperature_c"] < df["temperature_c"].mean()),
        df["anomaly_iqr_rainfall_mm"] & (df["rainfall_mm"] > df["rainfall_mm"].quantile(0.75)),
        df["anomaly_iqr_rainfall_mm"] & (df["rainfall_mm"] == 0),
    ]
    labels = ["Heatwave", "Cold Snap", "Heavy Rainfall", "Drought"]
    df["anomaly_type"] = np.select(conditions, labels, default="Normal")
    summary = df["anomaly_type"].value_counts()
    print("\n=== ANOMALY SUMMARY ===")
    print(summary.to_string())
    return df


def get_anomaly_table(df: pd.DataFrame) -> pd.DataFrame:
    """Return a clean table of all detected anomalies (non-Normal)."""
    anomalies = df[df["anomaly_type"] != "Normal"][[
        "date", "year", "month", "temperature_c", "rainfall_mm", "anomaly_type"
    ]].copy()
    anomalies = anomalies.sort_values("date").reset_index(drop=True)
    print(f"\n[TABLE] {len(anomalies)} total anomaly days found.")
    return anomalies


def run_full_anomaly_detection(df: pd.DataFrame) -> tuple:
    """
    Run all anomaly detection methods and return enriched df + anomaly table.
    """
    df = zscore_anomalies(df, "temperature_c")
    df = iqr_anomalies(df, "rainfall_mm")
    df = rolling_anomalies(df, "temperature_c")
    df = label_anomalies(df)
    anomaly_table = get_anomaly_table(df)
    return df, anomaly_table


if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    from src.preprocessor import load_data, clean_data, feature_engineer
    df = load_data("data/climate_data.csv")
    df = clean_data(df)
    df = feature_engineer(df)
    df, anom = run_full_anomaly_detection(df)
    anom.to_csv("outputs/anomaly_table.csv", index=False)
    print("\nAnomaly table saved to outputs/anomaly_table.csv")
